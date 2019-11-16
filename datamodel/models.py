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
            row = int(cell) / 8
            col = int(cell) % 8

            if int(row) % 2 != col % 2:
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


"""
    The cells are:
    |00|xx|02|xx|04|xx|06|xx|
    |xx|09|xx|11|xx|13|xx|15|
    |16|xx|18|xx|20|xx|22|xx|
    |xx|25|xx|27|xx|29|xx|31|
    |32|xx|34|xx|36|xx|38|xx|
    |xx|41|xx|43|xx|45|xx|47|
    |48|xx|50|xx|52|xx|54|xx|
    |xx|57|xx|59|xx|61|xx|63|

"""


class Move(models.Model):
    origin = models.IntegerField(null=False)
    target = models.IntegerField(null=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="moves")
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)

    def cat_moving_well(self):
        """Let's check if the cat is moving correctly """

        origin = int(self.origin)
        target = int(self.target)
        # The target must be different than origin
        if self.target == self.origin:
            raise ValidationError(MSG_ERROR_MOVE)

        # The target is empty validation
        if self.target in self.game.get_array_positions():
            raise ValidationError(MSG_ERROR_MOVE)

        # The target is a valid position:
        row = target / 8
        col = target % 8
        if int(row) % 2 != col % 2:
            raise ValidationError(MSG_ERROR_MOVE)
        # If its a cat, the target is origin + 7 or origin + 9
        if origin + 7 != target and origin + 9 != target:
            raise ValidationError(MSG_ERROR_MOVE)

        # Now check the extremes with only one possible movement
        # Top extreme
        if self.origin in [57, 59, 61, 63]:
            raise ValidationError(MSG_ERROR_MOVE)
        # Right extremes
        if self.origin == 0 and self.target != 9:
            raise ValidationError(MSG_ERROR_MOVE)
        elif self.origin == 16 and self.target != 25:
            raise ValidationError(MSG_ERROR_MOVE)
        elif self.origin == 32 and self.target != 41:
            raise ValidationError(MSG_ERROR_MOVE)
        elif self.origin == 48 and self.target != 57:
            raise ValidationError(MSG_ERROR_MOVE)
        # Left extremes
        elif self.origin == 15 and self.target != 22:
            raise ValidationError(MSG_ERROR_MOVE)
        elif self.origin == 31 and self.target != 38:
            raise ValidationError(MSG_ERROR_MOVE)
        elif self.origin == 47 and self.target != 54:
            raise ValidationError(MSG_ERROR_MOVE)
        return True

    def mouse_moving_well(self):
        """Let's check if the mouse is moving correctly """
        # The target must be different than origin
        if self.target == self.origin:
            raise ValidationError(MSG_ERROR_MOVE)

        # The target is a valid position:
        row = int(self.target) / 8
        col = int(self.target) % 8
        if int(row) % 2 != col % 2:
            raise ValidationError(MSG_ERROR_MOVE)

        origin = int(self.origin)
        target = int(self.target)

        if origin + 7 != target and origin + 9 != target and origin - 7 != target and origin-9 != target:
            raise ValidationError(MSG_ERROR_MOVE)
            # Now check the extremes with only one possible movement
            # Top extreme
        if self.origin == 57 and self.target != 48 and self.target != 50:
            raise ValidationError(MSG_ERROR_MOVE)
        elif self.origin == 59 and self.target != 50 and self.target != 52:
            raise ValidationError(MSG_ERROR_MOVE)
        elif self.origin == 61 and self.target != 52 and self.target != 54:
            raise ValidationError(MSG_ERROR_MOVE)
        elif self.origin == 63 and self.target != 54:
            raise ValidationError(MSG_ERROR_MOVE)
        # Left extremes
        elif self.origin == 0 and self.target != 9:
            raise ValidationError(MSG_ERROR_MOVE)
        elif self.origin == 16 and self.target != 25 and self.target != 9:
            raise ValidationError(MSG_ERROR_MOVE)
        elif self.origin == 32 and self.target != 41 and self.target != 25:
            raise ValidationError(MSG_ERROR_MOVE)
        elif self.origin == 48 and self.target != 57 and self.target != 41:
            raise ValidationError(MSG_ERROR_MOVE)
        # Right extremes
        elif self.origin == 15 and self.target != 22 and self.target != 6:
            raise ValidationError(MSG_ERROR_MOVE)
        elif self.origin == 31 and self.target != 38 and self.target != 22:
            raise ValidationError(MSG_ERROR_MOVE)
        elif self.origin == 47 and self.target != 54 and self.targer != 38:
            raise ValidationError(MSG_ERROR_MOVE)

        return True

    def validate(self):
        # We check if the game is active
        if self.game.status != GameStatus.ACTIVE:
            raise ValidationError(MSG_ERROR_MOVE)

        """ Check if the one who moves is the cat or mouse and it coincides with the player that moves """
        # If is cat_turn, then the player must be the cat
        if self.player == self.game.cat_user and self.game.cat_turn:
            # Check what is the cate moving
            # print("ORIGEN: ")
            # print(self.origin)
            # print("GATOS: ")
            # print(self.game.cat1)
            # print(self.game.cat2)
            # print(self.game.cat3)
            # print(self.game.cat4)

            origin = int(self.origin)

            if origin == self.game.cat1 and self.cat_moving_well():
                self.game.cat1 = self.target
                self.game.cat_turn = False
                self.game.save()
                return True
            elif origin == self.game.cat2 and self.cat_moving_well():
                self.game.cat2 = self.target
                self.game.cat_turn = False
                self.game.save()
                return True
            elif origin == self.game.cat3 and self.cat_moving_well():
                self.game.cat3 = self.target
                self.game.cat_turn = False
                self.game.save()
                return True
            elif origin == self.game.cat4 and self.cat_moving_well():
                self.game.cat4 = self.target
                self.game.cat_turn = False
                self.game.save()
                return True
            raise ValidationError(MSG_ERROR_MOVE)
        # If is cat turn
        elif self.player == self.game.mouse_user and not self.game.cat_turn and self.mouse_moving_well():
            self.game.mouse = self.target
            self.game.cat_turn = True
            self.game.save()
            return True

        raise ValidationError(MSG_ERROR_MOVE)

    def save(self, *args, **kwargs):
        if self.validate() is True:
            super(Move, self).save(*args, **kwargs)

    def create(self, game, player, origin, target):
        self.validate()


# This class work for Counter.objects. Making it a singleton class
class SingletonCounter(models.Manager):

    def inc(self):
        try:
            counter = Counter.objects.get(pk=1)
            counter.value += 1
            Counter.objects.all().filter(pk=1).update(value=counter.value)
            return counter.value
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
