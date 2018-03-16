from django.test import TestCase

from rest_framework import serializers

from rest_serializers.serializers import ManyToManySerializer
from tests.models import Child, Parent, Toy


class ToySerializer(serializers.ModelSerializer):
    class Meta:
        model = Toy
        fields = ('id', 'name')


class ChildSerializer(ManyToManySerializer):
    toys = ToySerializer(many=True)

    class Meta:
        model = Child
        fields = ('id', 'name', 'toys')


class ParentSerializer(ManyToManySerializer):
    children = ChildSerializer(many=True)

    class Meta:
        model = Parent
        fields = ('id', 'name', 'children')


class SerializersTests(TestCase):

    def test_models_create_ok(self):
        self.assertTrue(Parent.objects.create(name='foo'))

    def _create_test_data(self):
        self.parent = Parent.objects.create(name='Mr Smith')
        self.child = Child.objects.create(parent=self.parent, name='Dave Smith')
        self.toy_1 = Toy.objects.create(child=self.child, name='Ball')
        self.toy_2 = Toy.objects.create(child=self.child, name='Bike')

    def test_serialized_data(self):
        self._create_test_data()
        serializer = ParentSerializer(instance=self.parent)
        self.assertEqual(
            serializer.data,
            {
                'id': self.parent.pk,
                'name': self.parent.name,
                'children': [
                    {
                        'id': self.child.id,
                        'name': self.child.name,
                        'toys': [
                            {'id': self.toy_1.id, 'name': self.toy_1.name},
                            {'id': self.toy_2.id, 'name': self.toy_2.name}
                        ]
                    }
                ]
            }
        )

    def test_add__with_related_entities(self):
        data = {
            'name': 'Fred Smith',
            'children': [
                {
                    'name': 'Bobby',
                    'toys': [
                        {'name': 'Ball'},
                        {'name': 'Bike'}
                    ]
                }
            ]
        }
        serializer = ParentSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.assertEqual(Parent.objects.count(), 1)
        self.assertEqual(Child.objects.count(), 1)
        self.assertEqual(Toy.objects.count(), 2)

        parent = Parent.objects.get(name='Fred Smith')
        child = Child.objects.get(parent=parent, name='Bobby')
        Toy.objects.get(child=child, name='Ball')
        Toy.objects.get(child=child, name='Bike')

    def test_update__related_entities(self):
        self._create_test_data()
        data = {
            'id': self.parent.pk,
            'name': 'Fred Smith',
            'children': [
                {
                    'id': self.child.id,
                    'name': 'Bob',
                    'toys': [
                        {'id': self.toy_1.id, 'name': 'Drums'},
                        {'id': self.toy_2.id, 'name': 'Guitar'}
                    ]
                }
            ]
        }
        serializer = ParentSerializer(self.parent, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.assertEqual(Parent.objects.count(), 1)
        self.assertEqual(Child.objects.count(), 1)
        self.assertEqual(Toy.objects.count(), 2)

        Parent.objects.get(id=self.parent.id, name='Fred Smith')
        Child.objects.get(id=self.child.id, name='Bob')
        Toy.objects.get(id=self.toy_1.id, name='Drums')
        Toy.objects.get(id=self.toy_2.id, name='Guitar')

    def test_update__removal_of_related_entities(self):
        self._create_test_data()
        data = {
            'id': self.parent.pk,
            'name': 'Fred Smith',
            'children': [
                {
                    'id': self.child.id,
                    'name': 'Bob',
                    'toys': [
                        {'id': self.toy_1.id, 'name': 'Drums'}
                    ]
                }
            ]
        }
        serializer = ParentSerializer(self.parent, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.assertEqual(Parent.objects.count(), 1)
        self.assertEqual(Child.objects.count(), 1)
        self.assertEqual(Toy.objects.count(), 1)

        Parent.objects.get(id=self.parent.id, name='Fred Smith')
        Child.objects.get(id=self.child.id, name='Bob')
        Toy.objects.get(id=self.toy_1.id, name='Drums')

    def test_update__adding_another_related_entity(self):
        self._create_test_data()
        data = {
            'id': self.parent.pk,
            'name': 'Fred Smith',
            'children': [
                {
                    'id': self.child.id,
                    'name': 'Bob',
                    'toys': [
                        {'id': self.toy_1.id, 'name': 'Drums'},
                        {'id': self.toy_2.id, 'name': 'Guitar'},
                        {'name': 'Flute'}
                    ]
                }
            ]
        }
        serializer = ParentSerializer(self.parent, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.assertEqual(Parent.objects.count(), 1)
        self.assertEqual(Child.objects.count(), 1)
        self.assertEqual(Toy.objects.count(), 3)

        Parent.objects.get(id=self.parent.id, name='Fred Smith')
        Child.objects.get(id=self.child.id, name='Bob')
        Toy.objects.get(id=self.toy_1.id, name='Drums')
        Toy.objects.get(id=self.toy_2.id, name='Guitar')
        Toy.objects.get(child=self.child, name='Flute')
