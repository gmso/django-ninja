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
    tag_work.todos.set([todo_project])
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


def assert_plain_returned_todo_list(db, res):
    assert res[0]["ranking"]["id"] == db["rankings"]["ranking_2"].id
    assert res[0]["ranking"]["position"] == db["rankings"]["ranking_2"].position
    assert res[0]["id"] == db["todos"]["todo_italian"].id
    assert res[0]["title"] == db["todos"]["todo_italian"].title
    assert res[0]["completed_at"] == datetime_to_str(db["todos"]["todo_italian"].completed_at)
    assert res[0]["goal"]["id"] == db["goal"].id
    assert res[0]["goal"]["name"] == db["goal"].name

    assert res[1]["ranking"]["id"] == db["rankings"]["ranking_1"].id
    assert res[1]["ranking"]["position"] == db["rankings"]["ranking_1"].position
    assert res[1]["id"] == db["todos"]["todo_project"].id
    assert res[1]["title"] == db["todos"]["todo_project"].title
    assert res[1]["completed_at"] == datetime_to_str(db["todos"]["todo_project"].completed_at)
    assert res[1]["goal"] == None

    assert res[2]["ranking"] == None
    assert res[2]["id"] == db["todos"]["todo_dishes"].id
    assert res[2]["title"] == db["todos"]["todo_dishes"].title
    assert res[2]["completed_at"] == None
    assert res[2]["goal"] == None

    assert res[3]["ranking"]["id"] == db["rankings"]["ranking_3"].id
    assert res[3]["ranking"]["position"] == db["rankings"]["ranking_3"].position
    assert res[3]["id"] == db["todos"]["todo_french"].id
    assert res[3]["title"] == db["todos"]["todo_french"].title
    assert res[3]["completed_at"] == None
    assert res[3]["goal"]["id"] == db["goal"].id
    assert res[3]["goal"]["name"] == db["goal"].name


def assert_prefetched_returned_todo_list(db, res):
    assert_plain_returned_todo_list(db, res)
    assert res[0]["tag_set"] == []
    assert res[1]["tag_set"][0]["id"] == db["tags"]["tag_work"].id
    assert res[1]["tag_set"][0]["name"] == db["tags"]["tag_work"].name
    assert res[2]["tag_set"][0]["id"] == db["tags"]["tag_home"].id
    assert res[2]["tag_set"][0]["name"] == db["tags"]["tag_home"].name
    assert res[3]["tag_set"][0]["id"] == db["tags"]["tag_home"].id
    assert res[3]["tag_set"][0]["name"] == db["tags"]["tag_home"].name


def assert_plain_returned_tags_list(db, res):
    assert res[0]["id"] == db["tags"]["tag_home"].id
    assert res[1]["id"] == db["tags"]["tag_work"].id


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
    assert_plain_returned_todo_list(db, res)


@pytest.mark.django_db
def test_serialize_model_FK_reversem2m_reverseone2one_queryset_prefetch(client):
    """
    Test serialization of model with Foreign Key, reverse ManyToMany and reverse
    OneToOne relationships.
    Test serialization of Queryset
    Prefetch IS USED for reverse ManyToMany
    """
    db = db_factory()
    http_response = client.get("/api/events/todos/prefetched")
    res = json.loads(http_response.content.decode('utf-8'))
    assert_prefetched_returned_todo_list(db, res)


@pytest.mark.django_db
def test_serialize_model_m2m_queryset_no_prefetch(client):
    """
    Test serialization of model with ManyToMany relationship.
    Test serialization of Queryset
    NO prefetch used for direct ManyToMany
    """
    db = db_factory()
    http_response = client.get("/api/events/tags/no_prefetch")
    res = json.loads(http_response.content.decode('utf-8'))
    assert_plain_returned_tags_list(db, res)