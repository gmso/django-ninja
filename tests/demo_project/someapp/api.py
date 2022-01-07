from datetime import date
from typing import List

from django.shortcuts import get_object_or_404
from pydantic import BaseModel

from ninja import Router

from .models import Event, Todo, Tag, Goal, Ranking

router = Router()


class EventSchema(BaseModel):
    title: str
    start_date: date
    end_date: date

    class Config:
        orm_mode = True


@router.post("/create", url_name="event-create-url-name")
def create_event(request, event: EventSchema):
    Event.objects.create(**event.dict())
    return event


@router.get("", response=List[EventSchema])
def list_events(request):
    return list(Event.objects.all())


@router.get("/{id}", response=EventSchema)
def get_event(request, id: int):
    event = get_object_or_404(Event, id=id)
    return event


@router.get("/todos/no_prefetch")
def get_all_todos_without_prefetch(request):
    return Todo.objects.all()


@router.get("/todos/prefetched")
def get_all_todos_with_prefetch(request):
    return Todo.objects.all().prefetch_related('tag_set')


@router.get("/tags/no_prefetch")
def get_all_tags_without_prefetch(request):
    return Tag.objects.all()


@router.get("/tags/prefetched")
def get_all_tags_with_prefetch(request):
    return Tag.objects.all().prefetch_related('todos')


@router.get("/goals/no_prefetch")
def get_all_goals_without_prefetch(request):
    return Goal.objects.all()


@router.get("/goals/prefetched")
def get_all_goals_with_prefetch(request):
    return Goal.objects.all().prefetch_related('todo_set')


@router.get("/rankings/no_prefetch")
def get_all_rankings_without_prefetch(request):
    return Ranking.objects.all()


@router.get("/todos/paginated")
def get_paginated_todos(request, page: int = 0):
    paginate_by = 2
    first = paginate_by * page
    last = first + paginate_by
    return Todo.objects.all()[first:last]


@router.get("/todos/first")
def get_first_todo(request):
    return Todo.objects.get(pk=1)