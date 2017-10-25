from rest_framework.utils import model_meta


def set_many(instance, field, value):
    # get basic info about the instance
    info = model_meta.get_field_info(instance)
    is_many = info.relations[field].to_many
    is_reverse = info.relations[field].reverse
    has_through_model = info.relations[field].has_through_model

    if is_many and is_reverse and not has_through_model:
        # we have a reverse foreign key so we need to give it the full beans
        delete_obsolete_many(instance, field, value)
        update_or_create_many(instance, field, value)
    else:
        # if not we need to just treat it as a normal m2m
        field = getattr(instance, field)
        field.set(value)


def delete_obsolete_many(instance, attr, value):
    related_manager = getattr(instance, attr)

    # find the primary key for the joining table
    primary_key = related_manager.model._meta.pk

    # get a list of primary keys in validated data that we want to keep
    pks = [item.get(primary_key.name)
           for item in value if item.get(primary_key.name)]

    # delete any existing many-to-many that are not wanted
    related_manager.exclude(pk__in=pks).delete()


def update_or_create_many(instance, attr, value):
    related_manager = getattr(instance, attr)
    info = model_meta.get_field_info(related_manager.model)

    # find the primary key for the joining table
    primary_key = related_manager.model._meta.pk

    # loop data and either update if we have been passed a primary key or
    # create one if we have not
    for item in value:

        # remove many-to-many relationships from validated_data as they
        # need to be created once the instance is saved
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in item):
                many_to_many[field_name] = item.pop(field_name)

        # id of the item if there is one
        item_pk = item.pop(primary_key.name) if item.get(
            primary_key.name) else None

        # if we have an id we need to update it otherwise create it
        if item_pk:
            related_object = related_manager.get(pk=item_pk)
            for m_attr, m_value in item.items():
                setattr(related_object, m_attr, m_value)
            related_object.save()
        else:
            related_object = related_manager.create(**item)

        # save or delete many-to-many relationships after the instance is
        # created.
        if many_to_many:
            for field_name, value in many_to_many.items():
                set_many(related_object, field_name, value)
