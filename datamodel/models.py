from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from enum import Enum


class GameStatus(Enum):
    CREATED = 0
    ACTIVE = 1
    FINISHED = -1


class User(models.Model):
    # link UserProfile to a User model instance
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Game(models.Model):
    # cat and mouse are foreign keys of a user
    cat_user = models.ForeignKey(User)
    mouse_user = models.ForeignKey(User)
    # The cats and mouse are ints with the position
    cat1 = models.IntegerField(null=False)
    cat2 = models.IntegerField(null=False)
    cat3 = models.IntegerField(null=False)
    cat4 = models.IntegerField(null=False)
    mouse = models.IntegerField(null=False)
    # if is cat turn. if False is mouse turn
    cat_turn = models.BooleanField(null=False)
    status = models.IntegerField(null=False, choices=GameStatus)

    def save(self, *args, **kwargs):

        # La URL es nombre del raton + _ + nombre del gato
        self.slug = slugify(self.mouse_user+'_'+self.cat_user)
        super(Game, self).save(*args, **kwargs)


class Move(models.Model):
    origin = models.IntegerField(null=False)
    target = models.IntegerField(null=False)
    game = models.ForeignKey(Game)
    player = models.ForeignKey(User)
    date = models.DateField(null=False)
