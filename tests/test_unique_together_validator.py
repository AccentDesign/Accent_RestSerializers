from django.test import TestCase
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from rest_serializers.serializers import ManyToManySerializer
from rest_serializers.validators import LazyUniqueTogetherValidator
from tests.models import Child, Parent


class ChildSerializer(serializers.ModelSerializer):
    """
    a child serializer that we do not want to pass parent id in the data
    we have to use the lazy validator here which will skip validation
    till attempting to save
    """

    class Meta:
        model = Child
        fields = ("id", "name")
        validators = [
            LazyUniqueTogetherValidator(
                queryset=model.objects.all(), fields=("name", "parent")
            )
        ]


class ParentSerializer(ManyToManySerializer):
    children = ChildSerializer(many=True)

    class Meta:
        model = Parent
        fields = ("id", "name", "children")


class UniqueTogetherTests(TestCase):
    def test_can_validate_and_save(self):
        data = {"name": "Freddy Star", "children": [{"name": "Bob"}, {"name": "Sally"}]}
        serializer = ParentSerializer(data=data)

        self.assertTrue(serializer.is_valid())

        serializer.save()

        # correct rows exist
        self.assertEqual(Parent.objects.count(), 1)
        self.assertEqual(Child.objects.count(), 2)

    def test_invalidates_correctly(self):
        data = {
            "name": "Freddy Star",
            "children": [{"name": "Sally"}, {"name": "Sally"}],
        }
        serializer = ParentSerializer(data=data)

        # initially valid as parent on child is missing
        self.assertTrue(serializer.is_valid())

        # however saving it will raise the correct validation error
        with self.assertRaises(ValidationError) as cm:
            serializer.save()

        self.assertEqual(
            cm.exception.detail,
            {"non_field_errors": ["The fields name, parent must make a unique set."]},
        )

        # nothing should save
        self.assertEqual(Parent.objects.count(), 0)
        self.assertEqual(Child.objects.count(), 0)

    def test_adding_to_existing_validates_and_saves(self):
        parent = Parent.objects.create(name="Freddy Star")
        child = Child.objects.create(name="Bob", parent=parent)

        data = {
            "id": parent.pk,
            "name": parent.name,
            "children": [{"id": child.pk, "name": child.name}, {"name": "Sally"}],
        }

        serializer = ParentSerializer(instance=parent, data=data)

        self.assertTrue(serializer.is_valid())

        serializer.save()

        # correct rows exist
        self.assertEqual(Parent.objects.count(), 1)
        self.assertEqual(Child.objects.count(), 2)

    def test_adding_invalid_to_existing_raises_correct_validation_error(self):
        parent = Parent.objects.create(name="Freddy Star")
        child = Child.objects.create(name="Bob", parent=parent)

        data = {
            "id": parent.pk,
            "name": parent.name,
            "children": [{"id": child.pk, "name": child.name}, {"name": child.name}],
        }

        serializer = ParentSerializer(instance=parent, data=data)

        # initially valid as parent on child is missing
        self.assertTrue(serializer.is_valid())

        # however saving it will raise the correct validation error
        with self.assertRaises(ValidationError) as cm:
            serializer.save()

        self.assertEqual(
            cm.exception.detail,
            {"non_field_errors": ["The fields name, parent must make a unique set."]},
        )

        # correct rows exist
        self.assertEqual(Parent.objects.count(), 1)
        self.assertEqual(Child.objects.count(), 1)
