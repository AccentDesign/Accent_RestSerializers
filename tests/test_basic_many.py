from django.test import TestCase
from rest_framework import serializers

from rest_serializers.serializers import ManyToManySerializer
from tests.models import House, Parent


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = ("id", "name")


class HouseSerializer(ManyToManySerializer):
    class Meta:
        model = House
        fields = ("id", "name", "parents")


class SerializersTests(TestCase):
    def test_models_create_ok(self):
        self.assertTrue(House.objects.create(name="foo"))
        self.assertTrue(Parent.objects.create(name="foo"))

    def _create_test_data(self):
        self.house = House.objects.create(name="94b")
        self.parent_1 = Parent.objects.create(name="Dave Smith")
        self.parent_2 = Parent.objects.create(name="Tim Smith")
        self.house.parents.add(self.parent_1, self.parent_2)

    def test_serialized_data(self):
        self._create_test_data()
        serializer = HouseSerializer(instance=self.house)
        self.assertEqual(
            serializer.data,
            {
                "id": self.house.pk,
                "name": self.house.name,
                "parents": [self.parent_1.id, self.parent_2.id],
            },
        )

    def test_can_create__with_related(self):
        parent_1 = Parent.objects.create(name="Dave Smith")
        parent_2 = Parent.objects.create(name="Tim Smith")
        data = {"name": "94b", "parents": [parent_1.pk, parent_2.pk]}
        serializer = HouseSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.assertEqual(House.objects.count(), 1)
        self.assertEqual(Parent.objects.count(), 2)

        house = House.objects.get(name="94b")
        self.assertEqual(house.parents.count(), 2)

    def test_can_update__with_adding_related(self):
        self._create_test_data()
        parent_3 = Parent.objects.create(name="Zebra")
        data = {
            "id": self.house.pk,
            "name": "94b",
            "parents": [self.parent_1.id, self.parent_2.id, parent_3.pk],
        }
        serializer = HouseSerializer(self.house, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.assertEqual(House.objects.count(), 1)
        self.assertEqual(Parent.objects.count(), 3)

        house = House.objects.get(name="94b")
        self.assertEqual(house.parents.count(), 3)

    def test_can_update__with_removing_related(self):
        self._create_test_data()
        data = {"id": self.house.pk, "name": "94b", "parents": [self.parent_1.id]}
        serializer = HouseSerializer(self.house, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.assertEqual(House.objects.count(), 1)
        self.assertEqual(Parent.objects.count(), 2)

        house = House.objects.get(name="94b")
        self.assertEqual(house.parents.count(), 1)

    def test_can_update__with_removing_all_related(self):
        self._create_test_data()
        data = {"id": self.house.pk, "name": "94b", "parents": []}
        serializer = HouseSerializer(self.house, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.assertEqual(House.objects.count(), 1)
        self.assertEqual(Parent.objects.count(), 2)

        house = House.objects.get(name="94b")
        self.assertEqual(house.parents.count(), 0)
