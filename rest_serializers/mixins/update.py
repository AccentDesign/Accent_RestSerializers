from collections import OrderedDict

from django.contrib.contenttypes.fields import GenericRelation
from django.db.models.fields.related import ForeignObjectRel

from .base import BaseNestedModelSerializer


class NestedUpdateMixin(BaseNestedModelSerializer):
    """
    Mixin adds update nested feature
    """

    def update(self, instance, validated_data):
        relations, reverse_relations = self._extract_relations(validated_data)

        # Create or update direct relations (foreign key, one-to-one)
        self.update_or_create_direct_relations(validated_data, relations)

        # Update instance
        instance = super().update(instance, validated_data)

        self.update_or_create_reverse_relations(instance, reverse_relations)
        self.delete_reverse_relations_if_need(instance, reverse_relations)
        return instance

    def delete_reverse_relations_if_need(self, instance, reverse_relations):
        # Reverse `reverse_relations` for correct delete priority
        reverse_relations = OrderedDict(reversed(list(reverse_relations.items())))

        # Delete instances which is missed in data
        for field_name, (
            related_field,
            field,
            field_source,
        ) in reverse_relations.items():
            model_class = field.Meta.model

            related_data = self.initial_data[field_name]
            # Expand to array of one item for one-to-one for uniformity
            if related_field.one_to_one:
                related_data = [related_data]

            # M2M relation can be as direct or as reverse. For direct relation we
            # should use reverse relation name
            if related_field.many_to_many and not isinstance(
                related_field, ForeignObjectRel
            ):
                related_field_lookup = {related_field.remote_field.name: instance}
            elif isinstance(related_field, GenericRelation):
                related_field_lookup = self._get_generic_lookup(instance, related_field)
            else:
                related_field_lookup = {related_field.name: instance}

            current_ids = [d.get("pk") for d in related_data if d is not None]
            pks_to_delete = list(
                model_class.objects.filter(**related_field_lookup)
                .exclude(pk__in=current_ids)
                .values_list("pk", flat=True)
            )

            if related_field.many_to_many:
                # Remove relations from m2m table
                m2m_manager = getattr(instance, field_source)
                m2m_manager.remove(*pks_to_delete)
            else:
                model_class.objects.filter(pk__in=pks_to_delete).delete()
