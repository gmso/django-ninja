# Returning Django QuerySets and model instances

## Goal

Oftentimes, we just need to output a database object or a `QuerySet` of objects. And to do that a lot of manual work is needed for every model (create schema, list fields, pass it as `response` argument).

To address this problem, you can simplify your views by skipping the creation of usage of `Schema`. It is possible to directly return a Django `QuerySet` or a Django model instance. In this case, django-ninja will return a serialized representation of the object(s) in your `QuerySet` or the object instance.

## Example

Given the following example `Model`:

```Python
class Todo(models.Model):
    title = models.CharField(max_length=50)
    completed_at = models.DateTimeField(null=True, blank=True)
    goal = models.ForeignKey(Goal, null=True, blank=True, on_delete=models.CASCADE)
```

## Returning a QuerySet

If your view returns a `QuerySet` with all `Todo` objects in the database:

```Python hl_lines="3"
@router.get("/todos")
def get_all_todos(request):
    return Todo.objects.all()
```

The serialized HTTP response will correspond to a list of all fields found in the `QuerySet`, including the model's `Foreign Keys` (`goal` in this example) and reverse `OneToOne` relationships (`ranking` in this example):
```json
[
  {
    "ranking": {
        "id": 2,
        "position": 2
    },  
    "id": 1,
    "title": "Study italian",
    "completed_at": "2022-01-03T19:57:46Z",
    "goal": {
        "id": 1,
      "name": "Learn foreign languages"
    },
  },
  {
    "ranking": null,  
    "id": 2,
    ...
  }
  ...
]
```

## Returning a model instance

If your view returns a single model instance, it will be serialized as a JSON object. Considering the following view:

```Python hl_lines="3 4"
@router.get("/todos/{id}")
def get_todo_from_id(request, id: int):
    todo = get_object_or_404(Todo, pk=id)
    return todo
```

If called with `id=1`, the response will be:
```json
{
  "ranking": {
    "id": 2,
    "position": 2
  },
  "id": 1,
  "title": "Study italian",
  "completed_at": "2022-01-03T19:57:46Z",
  "goal": {
    "id": 1,
    "name": "Learn foreign languages"
  }
}
```

## Including related fields

If you need to return also related `ManyToMany` relationships (both direct and reverse), you can use Django's `prefetch_related` to fetch these fields before serialization ocurrs.

Considering that the `Todo` model has a reverse `ManyToMany` relationship with the `Tag` model:

```Python hl_lines="3"
class Tag(models.Model):
    name = models.CharField(max_length=30)
    todos = models.ManyToManyField(Todo)
```

If we add `prefetch_related` to the view in the first example:

```Python hl_lines="3"
@router.get("/todos/prefetched")
def get_all_todos_with_prefetch(request):
    return Todo.objects.all().prefetch_related("tag_set")
```

We should now have the `tag_set` included in the objects of the returned `QuerySet`

```json hl_lines="3 17 18 19 20 21 22"
[
  {
    "tag_set": [],
    "ranking": {
      "id": 2,
      "position": 2
    },
    "id": 1,
    "title": "Study italian",
    "completed_at": "2022-01-03T19:57:46Z",
    "goal": {
      "id": 1,
      "name": "Learn foreign languages"
    }
  },
  {
    "tag_set": [
      {
        "id": 2,
        "name": "Work"
      }
    ],
    "ranking": {
      "id": 1,
      "position": 1
    },
    "id": 2,
    "title": "Work on project A",
    "completed_at": "2022-01-04T09:16:07.230Z",
    "goal": null
  },
  ...
]
```

!!! Warning
    If you need to add further nested relationships that are not directly related to the `Model`, it might be better to define a `ModelSchema` to be more specific with the returned data.