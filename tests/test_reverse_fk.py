from django.test import TestCase

from rest_framework import serializers
from rest_serializers.serializers import ManyToManySerializer
from tests.models import Child, Parent


class ChildSerializer(serializers.ModelSerializer):
    id = serializers.ModelField(model_field=Child()._meta.get_field('id'), required=False, allow_null=True)

    class Meta:
        model = Child
        fields = ('id', 'name')


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
        self.child_1 = Child.objects.create(parent=self.parent, name='Dave Smith')
        self.child_2 = Child.objects.create(parent=self.parent, name='Tim Smith')

    def test_serialized_data(self):
        self._create_test_data()
        serializer = ParentSerializer(instance=self.parent)
        self.assertEqual(
            serializer.data,
            {
                'id': self.parent.pk,
                'name': self.parent.name,
                'children': [
                    {'id': self.child_1.id, 'name': self.child_1.name},
                    {'id': self.child_2.id, 'name': self.child_2.name}
                ]
            }
        )

    def test_add__with_related_entities_will_accept_null_pk(self):
        data = {
            'name': 'Fred Smith',
            'children': [
                {'id': None, 'name': 'Bobby'}
            ]
        }
        serializer = ParentSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.assertEqual(Parent.objects.count(), 1)
        self.assertEqual(Child.objects.count(), 1)

        parent = Parent.objects.get(name='Fred Smith')
        Child.objects.get(parent=parent, name='Bobby')

    def test_add__with_related_entities(self):
        data = {
            'name': 'Fred Smith',
            'children': [
                {'name': 'Bobby'},
                {'name': 'Steve'}
            ]
        }
        serializer = ParentSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.assertEqual(Parent.objects.count(), 1)
        self.assertEqual(Child.objects.count(), 2)

        parent = Parent.objects.get(name='Fred Smith')
        Child.objects.get(parent=parent, name='Bobby')
        Child.objects.get(parent=parent, name='Steve')

    def test_update__related_entities(self):
        self._create_test_data()
        data = {
            'id': self.parent.pk,
            'name': 'Freddy Star',
            'children': [
                {'id': self.child_1.id, 'name': 'Bob'},
                {'id': self.child_2.id, 'name': 'Sally'}
            ]
        }
        serializer = ParentSerializer(self.parent, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.assertEqual(Parent.objects.count(), 1)
        self.assertEqual(Child.objects.count(), 2)

        Parent.objects.get(id=self.parent.id, name='Freddy Star')
        Child.objects.get(id=self.child_1.id, name='Bob')
        Child.objects.get(id=self.child_2.id, name='Sally')

    def test_update__removal_of_related_entities(self):
        self._create_test_data()
        data = {
            'id': self.parent.pk,
            'name': 'Freddy Star',
            'children': [
                {'id': self.child_1.id, 'name': 'Bob'}
            ]
        }
        serializer = ParentSerializer(self.parent, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.assertEqual(Parent.objects.count(), 1)
        self.assertEqual(Child.objects.count(), 1)

        Child.objects.get(id=self.child_1.id, name='Bob')

    def test_update__adding_another_related_entity(self):
        self._create_test_data()
        data = {
            'id': self.parent.pk,
            'name': 'Freddy Star',
            'children': [
                {'id': self.child_1.id, 'name': 'Bob'},
                {'id': self.child_2.id, 'name': 'Sally'},
                {'name': 'Fred'}
            ]
        }
        serializer = ParentSerializer(self.parent, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.assertEqual(Parent.objects.count(), 1)
        self.assertEqual(Child.objects.count(), 3)

        Child.objects.get(id=self.child_1.id, name='Bob')
        Child.objects.get(id=self.child_2.id, name='Sally')
        Child.objects.get(name='Fred')
