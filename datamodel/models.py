from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

MSG_ERROR_INVALID_CELL = "Invalid cell for a cat or the mouse|Gato o ratón en posición no válida"
MSG_ERROR_GAMESTATUS = "Game status not valid|Estado no válido"
MSG_ERROR_MOVE = "Move not allowed|Movimiento no permitido"
MSG_ERROR_NEW_COUNTER = "Insert not allowed|Inseción no permitida"


class GameStatus(models.Model):
    CREATED = 0
    ACTIVE = 1
    FINISHED = 2


class Game(models.Model):
    # cat and mouse are foreign keys of a user
    cat_user = models.ForeignKey(User, related_name="games_as_cat", null=False, on_delete=models.CASCADE)
    mouse_user = models.ForeignKey(User, related_name="games_as_mouse", null=True, blank=True, on_delete=models.CASCADE)
    MIN_CELL = 0
    MAX_CELL = 63

    # The cats and mouse are ints with the position
    # range is [0, 63]
    # default values are the initial position
    cat1 = models.IntegerField(null=False, default=0,
                               validators=[MaxValueValidator(MAX_CELL), MinValueValidator(MIN_CELL)])
    cat2 = models.IntegerField(null=False, default=2,
                               validators=[MaxValueValidator(MAX_CELL), MinValueValidator(MIN_CELL)])
    cat3 = models.IntegerField(null=False, default=4,
                               validators=[MaxValueValidator(MAX_CELL), MinValueValidator(MIN_CELL)])
    cat4 = models.IntegerField(null=False, default=6,
                               validators=[MaxValueValidator(MAX_CELL), MinValueValidator(MIN_CELL)])
    mouse = models.IntegerField(null=False, default=59,
                                validators=[MaxValueValidator(MAX_CELL), MinValueValidator(MIN_CELL)])

    # if True it is cat turn. if False it is mouse turn. Default the cat starts
    cat_turn = models.BooleanField(null=False, default=True)
    status = models.IntegerField(null=False, default=GameStatus.CREATED)

    def validate(self):
        # Status validation
        if self.mouse_user is None and self.status != GameStatus.CREATED:
            raise ValidationError(MSG_ERROR_GAMESTATUS)
        if self.mouse_user is None:
            self.status = GameStatus.CREATED
        elif self.status != GameStatus.FINISHED:
            self.status = GameStatus.ACTIVE
        # Position validation
        for cell in self.get_array_positions():
            row = int(cell/8)
            col = int(cell % 8)
            if row % 2 != col % 2:
                raise ValidationError(MSG_ERROR_INVALID_CELL)
        return True

    def save(self, *args, **kwargs):
        if self.validate() is True:
            super(Game, self).save(*args, **kwargs)

    def get_array_positions(self):
        return [self.cat1, self.cat2, self.cat3, self.cat4, self.mouse]

    def get_status_str(self):
        if self.status == GameStatus.ACTIVE: return "Active"
        elif self.status == GameStatus.FINISHED: return "Finished"
        else: return "Created"

    def __str__(self):
        status = "(" + str(self.id) + ", " + self.get_status_str() + ")"
        cat_positions = str(self.cat1) + ", " + str(self.cat2)  + ", " + str(self.cat3)  + ", " + str(self.cat4)
        cat = "\tCat " + ("[X] " if self.cat_turn else "[ ] ") + str(self.cat_user) + "(" + cat_positions + ")"
        if self.mouse_user:
            mouse = " --- Mouse " + ("[ ] " if self.cat_turn else "[X] ") + str(self.mouse_user) + "(" + str(self.mouse) + ")"
        else:
            mouse = ""
        return status + cat + mouse


class Move(models.Model):
    origin = models.IntegerField(null=False)
    target = models.IntegerField(null=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="moves")
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)

    def validate(self):
        if self.game.status != GameStatus.ACTIVE:
            raise ValidationError(MSG_ERROR_MOVE)
        return True

    def save(self, *args, **kwargs):
        if self.validate() is True:
            super(Move, self).save(*args, **kwargs)


# This class work for Counter.objects. Making it a singleton class
class SingletonCounter(models.Manager):

    # You can't create it
    def create(self, *args, **kwargs):
        raise ValidationError(MSG_ERROR_NEW_COUNTER)

    def inc(self):
        try:
            counter = Counter.objects.get(pk=1)
            counter.value += 1
            Counter.objects.all().filter(pk=1).update(value=counter.value)
            return counter.value
        # If the singleton doesn't exist we create it
        except ObjectDoesNotExist:
            # Initial value is 1 because we are increasing the counter
            counter = Counter(value=1, pk=1)
            counter.save(priv=True)
            return counter.value

    def get_current_value(self):
        counter = Counter.objects.all().filter(pk=1)
        if counter:
            return counter[0].value
        else:
            counter = Counter()
            counter.id = 1
            counter.save(priv=True)
            return counter.value


class Counter(models.Model):
    value = models.IntegerField(null=False, default=0)

    objects = SingletonCounter()

    def save(self, *args, priv=False, **kwargs):
        if priv:
            super(Counter, self).save(*args, **kwargs)
        else:
            raise ValidationError(MSG_ERROR_NEW_COUNTER)

    def __str__(self):
        return "The counter id is:: "+str(self.id)+"\nAnd the value is: "+str(self.value)

