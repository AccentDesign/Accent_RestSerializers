from django.db import models


# Models for the reverse foreign key relations
class Parent(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        app_label = 'tests'
        ordering = ('name', )


class Child(models.Model):
    name = models.CharField(max_length=20)
    parent = models.ForeignKey(Parent, related_name='children', on_delete=models.CASCADE)

    class Meta:
        app_label = 'tests'
        ordering = ('name', )


class Toy(models.Model):
    name = models.CharField(max_length=20)
    child = models.ForeignKey(Child, related_name='toys', on_delete=models.CASCADE)

    class Meta:
        app_label = 'tests'
        ordering = ('name', )


# Models for a standard m2m to ensure they still work
class House(models.Model):
    name = models.CharField(max_length=20)
    parents = models.ManyToManyField(Parent, blank=True)

    class Meta:
        app_label = 'tests'
        ordering = ('name', )
