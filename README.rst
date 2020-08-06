**********************
Accent_RestSerializers
**********************

|Build_Status|

.. |Build_Status| image:: https://github.com/AccentDesign/Accent_RestSerializers/workflows/Testing%20workflow/badge.svg
   :target: https://github.com/AccentDesign/Accent_RestSerializers/workflows/Testing%20workflow

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

Example::

    from rest_serializers.serializers import ManyToManySerializer


    class ChildSerializer(serializers.ModelSerializer):
         class Meta:
            model = Child
            fields = ('id', 'name')


    class ParentSerializer(ManyToManySerializer):
         children = ChildSerializer(many=True)

         class Meta:
            model = Parent
            fields = ('id', 'name', 'children')

Here the ChildSerializer can also inherit from ManyToManySerializer to include a further depth and so on.
