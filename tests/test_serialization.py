import datetime
import json

from django.urls import reverse
import pytest

from someapp import models


def db_factory():
    goal = models.Goal.objects.create(name="Learn foreign languages")
    todo_italian = models.Todo.objects.create(
        title="Study italian",
        completed_at = datetime.datetime(2022,10,1,1,10,20,tzinfo=datetime.timezone.utc),
        goal = goal
    )
    todo_project = models.Todo.objects.create(
        title="Work on project A",
        completed_at = datetime.datetime(2022,10,1,1,10,20,tzinfo=datetime.timezone.utc),
    )
    todo_dishes = models.Todo.objects.create(title="Wash the dishes")
    todo_french = models.Todo.objects.create(
        title="Study french",
        goal = goal
    )
    tag_home = models.Tag.objects.create(name = "Home")
    tag_home.todos.set([todo_dishes, todo_french])
    tag_work = models.Tag.objects.create(name = "Work")
    tag_home.todos.set([todo_project])
    ranking_1 = models.Ranking.objects.create(position = 1, todo = todo_project)
    ranking_2 = models.Ranking.objects.create(position = 2, todo = todo_italian)
    ranking_3 = models.Ranking.objects.create(position = 3, todo = todo_french)

    return {
        "goal": goal,
        "todos": {
            "todo_italian": todo_italian,
            "todo_project": todo_project,
            "todo_dishes": todo_dishes,
            "todo_french": todo_french,
        },
        "tags": {
            "tag_home": tag_home,
            "tag_work": tag_work,
        },
        "rankings": {
            "ranking_1": ranking_1,
            "ranking_2": ranking_2,
            "ranking_3": ranking_3,
        }
    }


def datetime_to_str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

@pytest.mark.django_db
def test_serialize_model_FK_reversem2m_reverseone2one_queryset_no_prefetch(client):
    """
    Test serialization of model with Foreign Key, reverse ManyToMany and reverse
    OneToOne relationships.
    Test serialization of Queryset
    NO prefetch used for reverse ManyToMany
    """
    db = db_factory()
    http_response = client.get("/api/events/todos/no_prefetch")
    res = json.loads(http_response.content.decode('utf-8'))
    assert res[0]["ranking"]["id"] == db["rankings"]["ranking_2"].id
    assert res[0]["ranking"]["position"] == db["rankings"]["ranking_2"].position
    assert res[0]["id"] == db["todos"]["todo_italian"].id
    assert res[0]["title"] == db["todos"]["todo_italian"].title
    assert res[0]["completed_at"] == datetime_to_str(db["todos"]["todo_italian"].completed_at)
    assert res[0]["goal"]["id"] == db["goal"].id
    assert res[0]["goal"]["name"] == db["goal"].name
