from django.db import transaction
from rest_framework.serializers import ModelSerializer

from .mixins import EagerLoadingMixin, NestedCreateMixin, NestedUpdateMixin


class EagerModelSerializer(EagerLoadingMixin, ModelSerializer):
    """Serializer that includes the select and prefetch related"""


class ManyToManySerializer(EagerModelSerializer, NestedCreateMixin, NestedUpdateMixin):
    """Serializer that includes the select, prefetch related and nestable writing"""

    @transaction.atomic
    def create(self, validated_data):
        return super().create(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
