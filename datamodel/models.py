from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from enum import Enum


class GameStatus(models.Model):
    CREATED = 0
    ACTIVE = 1
    FINISHED = 2


class User(models.Model):
    # link UserProfile to a User model instance
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Game(models.Model):
    # cat and mouse are foreign keys of a user
    cat_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="games")
    mouse_user = models.ForeignKey(User, on_delete=models.CASCADE)

    # The cats and mouse are ints with the position
    # range is [0, 63]
    # default values are the initial position
    cat1 = models.IntegerField(null=False, default=0)
    cat2 = models.IntegerField(null=False, default=2)
    cat3 = models.IntegerField(null=False, default=4)
    cat4 = models.IntegerField(null=False, default=6)
    mouse = models.IntegerField(null=False, default=59)

    # if is cat turn. if False is mouse turn.
    # Default the cat starts
    cat_turn = models.BooleanField(null=False, default=True)
    status = models.IntegerField(null=False, default=GameStatus.CREATED)

    def validate(self):
        if self.cat2 is 8:
            print("HOLA MUNDO")
        return True

    # raise ValidationError("Msg")
    def save(self, *args, **kwargs):
        if not self.validate():
            raise ValidationError("Msg")
        if self.mouse_user is None:
            self.status = GameStatus.CREATED
        else:
            self.status = GameStatus.ACTIVE
        super(Game, self).save(*args, **kwargs)

    def get_array_positions(self):
        return [self.cat1, self.cat2, self.cat3, self.cat4, self.mouse]


class Move(models.Model):
    origin = models.IntegerField(null=False)
    target = models.IntegerField(null=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(null=False)
