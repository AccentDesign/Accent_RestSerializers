from collections import OrderedDict, defaultdict

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models import FieldDoesNotExist, ForeignKey
from django.db.models.fields.related import ForeignObjectRel
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from rest_serializers.validators import LazyUniqueTogetherValidator


class BaseNestedModelSerializer(serializers.ModelSerializer):
    def _extract_relations(self, validated_data):
        reverse_relations = OrderedDict()
        relations = OrderedDict()

        # Remove related fields from validated data for future manipulations
        for field_name, field in self.fields.items():
            if field.read_only:
                continue
            try:
                related_field, direct = self._get_related_field(field)
            except FieldDoesNotExist:
                continue

            if isinstance(field, serializers.ListSerializer) and isinstance(field.child, serializers.ModelSerializer):
                if field.source not in validated_data:
                    # Skip field if field is not required
                    continue

                validated_data.pop(field.source)

                reverse_relations[field_name] = (related_field, field.child, field.source)

            if isinstance(field, serializers.ModelSerializer):
                if field.source not in validated_data:
                    # Skip field if field is not required
                    continue

                if validated_data.get(field.source) is None:
                    if direct:
                        # Don't process null value for direct relations
                        # Native create/update processes these values
                        continue

                validated_data.pop(field.source)
                # Reversed one-to-one looks like direct foreign keys but they are reverse relations
                if direct:
                    relations[field_name] = (field, field.source)
                else:
                    reverse_relations[field_name] = (related_field, field, field.source)

        return relations, reverse_relations

    def _get_generic_lookup(self, instance, related_field):
        return {
            related_field.content_type_field_name: ContentType.objects.get_for_model(instance),
            related_field.object_id_field_name: instance.pk,
        }

    def _get_related_field(self, field):
        model_class = self.Meta.model

        try:
            related_field = model_class._meta.get_field(field.source)
        except FieldDoesNotExist:
            # If `related_name` is not set, field name does not include `_set` -> remove it and check again
            default_postfix = '_set'
            if field.source.endswith(default_postfix):
                related_field = model_class._meta.get_field(field.source[:-len(default_postfix)])
            else:
                raise

        if isinstance(related_field, ForeignObjectRel):
            return related_field.field, False
        return related_field, True

    def _get_related_pk(self, data, model_class):
        pk = data.get('pk') or data.get(model_class._meta.pk.attname)

        if pk:
            return str(pk)

        return None

    def _get_serializer_field(self, field, instance):
        if isinstance(field, ForeignKey):
            new_field = serializers.PrimaryKeyRelatedField(
                queryset=field.related_model._default_manager.get_queryset(),
                default=instance.pk
            )
            return new_field

    def _get_serializer_for_field(self, field, **kwargs):
        kwargs.update({
            'context': self.context,
            'partial': self.partial
        })
        return field.__class__(**kwargs)

    def prefetch_related_instances(self, field, related_data):
        model_class = field.Meta.model
        pk_list = []
        for d in filter(None, related_data):
            pk = self._get_related_pk(d, model_class)
            if pk:
                pk_list.append(pk)

        instances = {
            str(related_instance.pk): related_instance
            for related_instance in model_class.objects.filter(pk__in=pk_list)
        }

        return instances

    def update_or_create_reverse_relations(self, instance, reverse_relations):
        # Update or create reverse relations:
        # many-to-one, many-to-many, reversed one-to-one
        for field_name, (related_field, field, field_source) in reverse_relations.items():

            # Skip processing for empty data or not-specified field.
            # The field can be defined in validated_data but isn't defined
            # in initial_data (for example, if multipart form data used)
            related_data = self.initial_data.get(field_name, None)
            if related_data is None:
                continue

            # Expand to array of one item for one-to-one for uniformity
            if related_field.one_to_one:
                related_data = [related_data]

            instances = self.prefetch_related_instances(field, related_data)

            save_kwargs = self.get_save_kwargs(field_name)
            if isinstance(related_field, GenericRelation):
                save_kwargs.update(
                    self._get_generic_lookup(instance, related_field),
                )
            elif not related_field.many_to_many:
                save_kwargs[related_field.name] = instance

            new_related_instances = []
            for data in related_data:
                obj = instances.get(self._get_related_pk(data, field.Meta.model))
                serializer = self._get_serializer_for_field(field, instance=obj, data=data)

                # If the LazyUniqueTogetherValidator is being used it means there is a unique together,
                # and one field of the related instances is missing and is the current instance.
                # This can only be validated post save so its done here.
                # We need to dynamically add the field to the serializer so it can validated
                if LazyUniqueTogetherValidator in [v.__class__ for v in serializer.validators]:
                    missing_field = self._get_serializer_field(related_field, instance)
                    if missing_field:
                        serializer.fields[related_field.name] = missing_field

                serializer.is_valid(raise_exception=True)
                related_instance = serializer.save(**save_kwargs)
                data['pk'] = related_instance.pk
                new_related_instances.append(related_instance)

            if related_field.many_to_many:
                # Add m2m instances to through model via add
                m2m_manager = getattr(instance, field_source)
                m2m_manager.add(*new_related_instances)

    def update_or_create_direct_relations(self, attrs, relations):
        for field_name, (field, field_source) in relations.items():
            obj = None
            data = self.initial_data[field_name]
            model_class = field.Meta.model
            pk = self._get_related_pk(data, model_class)
            if pk:
                obj = model_class.objects.filter(pk=pk).first()
            serializer = self._get_serializer_for_field(field, instance=obj, data=data)
            serializer.is_valid(raise_exception=True)
            attrs[field_source] = serializer.save(**self.get_save_kwargs(field_name))

    def get_save_kwargs(self, field_name):
        save_kwargs = self.save_kwargs[field_name]
        if not isinstance(save_kwargs, dict):
            raise TypeError(_("Arguments to nested serializer's `save` must be dict's"))

        return save_kwargs

    def save(self, **kwargs):
        self.save_kwargs = defaultdict(dict, kwargs)

        return super().save(**kwargs)
