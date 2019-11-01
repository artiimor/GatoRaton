from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
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
    cat_user = models.ForeignKey(User, on_delete=models.CASCADE)
    mouse_user = models.ForeignKey(User, on_delete=models.CASCADE)

    # The cats and mouse are ints with the position
    # range is [1, 59]
    # default values are the initial position
    cat1 = models.IntegerField(null=False, default=0, validators=[MaxValueValidator(59), MinValueValidator(0)])
    cat2 = models.IntegerField(null=False, default=2, validators=[MaxValueValidator(59), MinValueValidator(0)])
    cat3 = models.IntegerField(null=False, default=4, validators=[MaxValueValidator(59), MinValueValidator(0)])
    cat4 = models.IntegerField(null=False, default=6, validators=[MaxValueValidator(59), MinValueValidator(0)])
    mouse = models.IntegerField(null=False, default=59, validators=[MaxValueValidator(59), MinValueValidator(0)])

    # if is cat turn. if False is mouse turn.
    # Default the cat starts
    cat_turn = models.BooleanField(null=False, default=True)
    status = models.IntegerField(null=False, choices=GameStatus)

    def save(self, *args, **kwargs):
        # La URL es nombre del raton + _ + nombre del gato
        self.slug = slugify(self.mouse_user+'_'+self.cat_user)
        super(Game, self).save(*args, **kwargs)

    def getArrayPositions(self):
        return [self.cat1, self.cat2, self.cat3, self.cat4, self.mouse]


class Move(models.Model):
    origin = models.IntegerField(null=False)
    target = models.IntegerField(null=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(null=False)
