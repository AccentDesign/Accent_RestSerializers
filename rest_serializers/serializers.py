from django.db import transaction
from rest_framework.serializers import ModelSerializer
from rest_framework.utils import model_meta

from .utils import set_many


class ManyToManySerializer(ModelSerializer):

    def create(self, validated_data):
        model_class = self.Meta.model
        info = model_meta.get_field_info(model_class)

        # enable atomic so can rollback
        with transaction.atomic():

            # remove many-to-many relationships from validated_data as they
            # need to be created once the instance is saved
            many_to_many = {}
            for field_name, relation_info in info.relations.items():
                if relation_info.to_many and (field_name in validated_data):
                    many_to_many[field_name] = validated_data.pop(field_name)

            instance = model_class.objects.create(**validated_data)

            # save or delete many-to-many relationships after the instance is
            # created.
            if many_to_many:
                for field_name, value in many_to_many.items():
                    set_many(instance, field_name, value)

        return instance

    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        # enable atomic so can rollback
        with transaction.atomic():

            for attr, value in validated_data.items():
                if attr in info.relations and info.relations[attr].to_many:
                    set_many(instance, attr, value)
                else:
                    setattr(instance, attr, value)

            instance.save()

        return instance
