from .base import BaseNestedModelSerializer


class NestedCreateMixin(BaseNestedModelSerializer):
    """
    Mixin adds nested create feature
    """

    def create(self, validated_data):
        relations, reverse_relations = self._extract_relations(validated_data)

        # Create or update direct relations (foreign key, one-to-one)
        self.update_or_create_direct_relations(validated_data, relations)

        # Create instance
        instance = super().create(validated_data)

        self.update_or_create_reverse_relations(instance, reverse_relations)

        return instance
