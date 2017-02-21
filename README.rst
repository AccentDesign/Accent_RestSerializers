*****************
Accent_SoftDelete
*****************

|Build_Status| |Coverage_Status|

.. |Build_Status| image:: https://circleci.com/gh/AccentDesign/Accent_RestSerializers.svg?style=svg
   :target: https://circleci.com/gh/AccentDesign/Accent_RestSerializers
.. |Coverage_Status| image:: http://img.shields.io/coveralls/AccentDesign/Accent_RestSerializers/master.svg
   :target: https://coveralls.io/r/AccentDesign/Accent_RestSerializers?branch=master

Description
***********

Library of useful Rest Framework serializers for django

Includes:

# Many-to-many serializer that will loop through an infinite depth and create, update and delete related entities.


Getting Started
***************

Installation::

   pip install git+https://github.com/AccentDesign/Accent_RestSerializers.git@master#egg=rest_serializers

settings.py::

   INSTALLED_APPS = [
       ...
       'rest_serializers',
       ...
   ]


Usage
*****

ManyToManySerializer:

This class is required in the parent serializer.

The pk field is required implicitly on the child serializer to make sure it exists in the
validated data in the create and update methods. The name of this must match that of the
actual field on the model.

Example::

    from rest_serializers.serializers import ManyToManySerializer


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

Here the ChildSerializer can also inherit from ManyToManySerializer to include a further depth and so on.
