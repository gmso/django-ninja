import pytest
import datetime

from tests.demo_project.someapp import models


def db_factory():
    goal = models.Goal.create(name="Learn foreign languages")
    todo_italian = models.Todo.create(
        title="Study italian",
        completed_at = datetime.datetime(2022,10,1,1,10,20),
        goal = goal
    )
    todo_project = models.Todo.create(
        title="Work on project A",
        completed_at = datetime.datetime(2022,10,1,1,10,20),
    )
    todo_dishes = models.Todo.create(title="Wash the dishes")
    todo_french = models.Todo.create(
        title="Study french",
        goal = goal
    )
    tag_home = models.Tag.create(
        name = "Home",
        todos = [todo_dishes, todo_french]
    )
    tag_work = models.Tag.create(
        name = "Work",
        todos = [todo_project]
    )
    ranking_1 = models.Ranking.create(position = 1, todo = todo_project)
    ranking_2 = models.Ranking.create(position = 2, todo = todo_italian)
    ranking_3 = models.Ranking.create(position = 3, todo = todo_french)

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
