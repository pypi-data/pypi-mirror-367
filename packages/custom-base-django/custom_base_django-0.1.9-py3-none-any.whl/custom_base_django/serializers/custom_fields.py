from rest_framework import serializers
import requests, os, mimetypes
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from ..models.custom_fields import RelatedIdList
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
import hashlib
from urllib.parse import urlparse
import glob

class empty:
    pass

class CustomFieldSerializer:
    def __init__(self, *args, **kwargs):
        model_field = kwargs.pop('model_field', None)
        setattr(self, 'model_field', model_field)
        if model_field:
            for key in getattr(model_field, "_extra_field_kwargs",[]):
                setattr(self, key, kwargs.pop(key, None))
        super().__init__(*args, **kwargs)

    def _post_process(self, instance, **kwargs):
        ...


class SmartFileListSerializerField(CustomFieldSerializer, serializers.ListField):
    child = serializers.JSONField()  # حالا می‌تونه str یا dict باشه

    def __init__(self, *args, **kwargs):
        kwargs.pop("encoder", None)
        kwargs.pop("decoder", None)
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        if not isinstance(data, list):
            raise serializers.ValidationError("Expected a list of file inputs")

        validated = []
        upload_tasks = []

        for item in data:
            # فایل آپلودی
            if hasattr(item, 'read'):
                validated.append(None)
                upload_tasks.append({'type': 'upload', 'source': item, 'meta': None})

            elif isinstance(item, (str, dict)):
                if isinstance(item, str):
                    item = {"url": item}

                item["url"] = item.get("url", "").strip()
                url = item["url"]
                if not url:
                    raise serializers.ValidationError("Missing 'url' in file object.")

                # آدرس لوکال
                if url.startswith(settings.MEDIA_URL):
                    rel_path = url.replace(settings.MEDIA_URL, "")
                    full_path = os.path.join(settings.MEDIA_ROOT, rel_path)

                    if not os.path.isfile(full_path):
                        raise serializers.ValidationError(f"Local file does not exist: {url}")

                    validated.append(item)
                    upload_tasks.append({'type': 'local', 'source': url, 'meta': item})

                # آدرس اینترنتی
                elif url.startswith("http"):
                    if not self.url_file_exists(url):
                        raise serializers.ValidationError(f"Remote file not accessible and no cached copy: {url}")

                    validated.append(None)
                    upload_tasks.append({'type': 'url', 'source': url, 'meta': item})

                else:
                    raise serializers.ValidationError(f"Unsupported file input: {item}")
            else:
                raise serializers.ValidationError("Invalid input type")

        if not hasattr(self.parent, "_post_actions"):
            self.parent._post_actions = []

        self.parent._post_actions.append({
            "field_name": self.field_name,
            "action": lambda instance: self._post_process(instance, upload_tasks)
        })

        return validated

    def _post_process(self, instance, upload_tasks):
        file_entries = []
        self.prefix_file_name = getattr(instance, self.prefix_file_name, self.prefix_file_name)
        self.upload_subfolder = getattr(instance, self.upload_subfolder, self.upload_subfolder)

        for task in upload_tasks:
            meta = task.get("meta") or {}
            prefix_file_name =  meta.get('prefix_file_name', self.prefix_file_name)
            if task['type'] == 'upload':
                file_obj = task['source']
                url = self.save_file(file_obj.read(), file_obj.name)
            elif task['type'] == 'url':
                url = self.download_from_url(task['source'])
            elif task['type'] == 'local':
                url = task['source']
            else:
                continue

            entry = meta.copy()
            entry["url"] = url
            entry['prefix_file_name'] = prefix_file_name
            file_entries.append(entry)

        setattr(instance, self.field_name, file_entries)

    def save_file(self, content, filename):
        filename = os.path.basename(filename).replace(" ", "_")
        filename = f"{self.prefix_file_name}__{filename}" if self.prefix_file_name else filename
        path = os.path.join(self.upload_subfolder, filename)
        base, ext = os.path.splitext(filename)
        counter = 1
        while default_storage.exists(path):
            filename = f"{base}_{counter}{ext}"
            path = os.path.join(self.upload_subfolder, filename)
            counter += 1
        full_path = default_storage.save(path, ContentFile(content))
        return default_storage.url(full_path)

    def download_from_url(self, url):
        try:
            # استخراج نام فایل از URL
            parsed_url = urlparse(url)
            base_name = os.path.basename(parsed_url.path)  # فایل‌نیم اصلی از URL
            file_name, ext_from_url = os.path.splitext(base_name)

            # محاسبه hash برای URL
            hash_name = hashlib.md5(url.encode('utf-8')).hexdigest()
            ext = ext_from_url or ''

            # جستجوی فایل قبلی با همین hash
            hash_pattern = f"__{hash_name}*"
            media_root = settings.MEDIA_ROOT
            search_pattern = os.path.join(media_root, '**', f'*{hash_pattern}')
            existing_files = glob.glob(search_pattern, recursive=True)

            if existing_files:
                existing_file_path = existing_files[0]
                rel_path = os.path.relpath(existing_file_path, media_root)
                return default_storage.url(rel_path)

            # دانلود فایل چون قبلاً ذخیره نشده
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "").split(";")[0].strip()
            ext = mimetypes.guess_extension(content_type) or ext

            # ساخت نام نهایی فایل با فرمت دلخواه
            final_filename = f"{self.prefix_file_name}_{file_name}__{hash_name}{ext}"
            path = os.path.join(self.upload_subfolder, final_filename)

            full_path = default_storage.save(path, ContentFile(response.content))
            return default_storage.url(full_path)

        except requests.RequestException:
            raise serializers.ValidationError(f"Failed to fetch file from URL: {url}")
        except Exception as e:
            raise serializers.ValidationError(f"Error downloading file: {e}")

    def url_file_exists(self, url):
        try:
            hash_name = hashlib.md5(url.encode('utf-8')).hexdigest()
            media_root = settings.MEDIA_ROOT
            search_pattern = os.path.join(media_root, '**', f'*__{hash_name}*')
            existing_files = glob.glob(search_pattern, recursive=True)
            if existing_files:
                return True

            # بررسی اینکه واقعا URL در دسترس هست یا نه (HEAD سریع‌تر از GET)
            response = requests.head(url, timeout=5)
            return response.status_code == 200

        except requests.RequestException:
            return False


class CustomDecimalField(serializers.DecimalField):
    def to_representation(self, value):
        return float(value)

    def run_validation(self, data=empty):
        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data
        value = self.to_internal_value(data)
        self.run_validators(value)
        return value


class RelatedListSerializerField(CustomFieldSerializer, serializers.ListField,):
    def __init__(self, *args, **kwargs):
        # حذف پارامترهای اضافی که ممکن است باعث خطا شوند
        kwargs.pop("encoder", None)
        kwargs.pop("decoder", None)
        super().__init__(**kwargs)

    @staticmethod
    def get_list(data):
        if data and not isinstance(data, (list, RelatedIdList)):
            data = data.get('list', [])
        return data

    def to_representation(self, value):
        # value = self.get_list(value)
        py_value = self.model_field.to_python(value)
        return py_value.to_serializable()

    def to_internal_value(self, data):
        data = self.get_list(data)
        try:
            return self.model_field.to_python(data)
        except Exception as e:
            raise DRFValidationError(f"Invalid format: {e}")

    def run_validation(self, data=serializers.empty):
        data = self.get_list(data)
        value = super().run_validation(data)
        try:
            self.model_field.validate(value, None)  # model_instance=None؛ یا از context بگیر
        except DjangoValidationError as e:
            raise DRFValidationError(e.messages)
        return value
