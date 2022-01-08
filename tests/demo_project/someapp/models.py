from django.core import validators
from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=100)


class Event(models.Model):
    title = models.CharField(max_length=100)
    category = models.OneToOneField(
        Category, null=True, blank=True, on_delete=models.SET_NULL
    )
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.title


class Client(models.Model):
    key = models.CharField(max_length=20, unique=True)


class Goal(models.Model):
    name = models.CharField(max_length=50)


class Todo(models.Model):
    title = models.CharField(max_length=50)
    completed_at = models.DateTimeField(null=True, blank=True)
    goal = models.ForeignKey(Goal, null=True, blank=True, on_delete=models.CASCADE)


class Tag(models.Model):
    name = models.CharField(max_length=30)
    todos = models.ManyToManyField(Todo)


class Ranking(models.Model):
    position = models.PositiveIntegerField(validators=[validators.MinValueValidator(1)])
    todo = models.OneToOneField(Todo, on_delete=models.CASCADE, null=True, blank=True)
