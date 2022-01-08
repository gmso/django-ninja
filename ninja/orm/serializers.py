from typing import Any, Dict, Tuple

from django.db import models


def is_model_instance(data: Any) -> bool:
    return isinstance(data, models.Model)


def is_queryset(data: Any) -> bool:
    return isinstance(data, models.query.QuerySet)


def is_one_relationship(data: Any) -> bool:
    return isinstance(data, models.ForeignKey) or isinstance(data, models.OneToOneRel)


def is_many_relationship(data: Any) -> bool:
    return (
        isinstance(data, models.ManyToManyRel)
        or isinstance(data, models.ManyToManyField)
        or isinstance(data, models.ManyToOneRel)
    )


def serialize_model_instance(
    obj: models.Model, referrers: Tuple[Any] = tuple()
) -> Dict[Any, Any]:
    """Serializes Django model instance to dictionary"""
    out = {}
    for field in obj._meta.get_fields():
        if is_one_relationship(field):  # TODO: Add OneToOne relationship??
            out.update(serialize_foreign_key(obj, field, referrers + (obj,)))
        elif is_many_relationship(field):
            out.update(serialize_many_relationship(obj, referrers + (obj,)))
        else:
            out.update(serialize_value_field(obj, field))
    return out


def serialize_queryset(
    data: models.query.QuerySet, referrers: Tuple[Any] = tuple()
) -> Dict[Any, Any]:
    """Serializes Django Queryset to dictionary"""
    return [serialize_model_instance(obj, referrers) for obj in data]


def serialize_foreign_key(
    obj: models.Model, field: Any, referrers: Tuple[Any] = tuple()
) -> Dict[Any, Any]:
    """Serializes foreign key field of Django model instance"""
    if not hasattr(obj, field.name):
        return {field.name: None}
    related_instance = getattr(obj, field.name)
    if related_instance is None:
        return {field.name: None}
    if related_instance in referrers:
        return {}
    return {field.name: serialize_model_instance(related_instance, referrers)}


def serialize_many_relationship(
    obj: models.Model, referrers: Tuple[Any] = tuple()
) -> Dict[Any, Any]:
    """
    Serializes many relationship (ManyToMany, ManyToOne)
    of Django model instance
    """
    if not hasattr(obj, "_prefetched_objects_cache"):
        return {}
    out = {}
    for k, v in obj._prefetched_objects_cache.items():
        field_name = k if hasattr(obj, k) else k + "_set"
        if v:
            out[field_name] = serialize_queryset(v, referrers + (obj,))
        else:
            out[field_name] = []
    return out


def serialize_value_field(obj: models.Model, field: Any) -> Dict[Any, Any]:
    """Serializes regular 'jsonable' field (Char, Int, etc.) of Django model instance"""
    return {field.name: getattr(obj, field.name)}
