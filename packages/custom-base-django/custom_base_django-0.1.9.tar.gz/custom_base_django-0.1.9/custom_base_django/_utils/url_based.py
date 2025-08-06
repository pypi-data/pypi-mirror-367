import re
import unicodedata

def slugify(value):
    value = str(value)
    value = unicodedata.normalize('NFKD', value)
    value = value.encode('ascii', 'ignore').decode('ascii')  # حذف نویسه‌های غیر ASCII
    value = re.sub(r'[^\w\s-]', '', value)  # حذف کاراکترهای خاص
    value = re.sub(r'[-\s]+', '-', value).strip('-_')  # فاصله یا خط تیره تبدیل به یک خط تیره
    return value.lower()