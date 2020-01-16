from rest_framework import serializers


class LazyUniqueTogetherValidator(serializers.UniqueTogetherValidator):
    """
    A unique together validator that will only check if all fields exist.

    This allows a missing field being added programmatically after the
    initial validate.
    """

    def has_missing_fields(self, attrs):
        for field_name in self.fields:
            if field_name not in attrs:
                return True

    def __call__(self, attrs, serializer):
        # only allow it to continue if all fields are present
        if self.has_missing_fields(attrs):
            return
        super().__call__(attrs, serializer)
