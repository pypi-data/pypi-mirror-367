from django.dispatch import Signal

serializer_pre_get = Signal()
serializer_past_get = Signal()
serializer_pre_validation = Signal()
serializer_past_validation = Signal()
serializer_pre_save = Signal()
serializer_past_save = Signal()

