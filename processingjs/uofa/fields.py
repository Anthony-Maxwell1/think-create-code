from django.db import models

# http://bitofpixels.com/blog/unique-on-charfield-when-blanktrue/
class NullableCharField(models.CharField):
    description = "CharField that stores NULL but returns ''"
    __metaclass__ = models.SubfieldBase
    def to_python(self, value):
        return value or ''
    def get_prep_value(self, value):
        return value or None
