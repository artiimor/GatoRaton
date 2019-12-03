from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from datamodel import constants


class GameStatus(models.Model):
    CREATED = 0
    ACTIVE = 1
    FINISHED = 2


class Game(models.Model):
    # cat and mouse are foreign keys of a user
    cat_user = models.ForeignKey(User, related_name="games_as_cat",
                                 null=False, on_delete=models.CASCADE)
    mouse_user = models.ForeignKey(User, related_name="games_as_mouse",
                                   null=True, blank=True,
                                   on_delete=models.CASCADE)
    MIN_CELL = 0
    MAX_CELL = 63

    # The cats and mouse are ints with the position
    # range is [0, 63]
    # default values are the initial position
    val = [MaxValueValidator(MAX_CELL), MinValueValidator(MIN_CELL)]
    cat1 = models.IntegerField(null=False, default=0, validators=val)
    cat2 = models.IntegerField(null=False, default=2, validators=val)
    cat3 = models.IntegerField(null=False, default=4, validators=val)
    cat4 = models.IntegerField(null=False, default=6, validators=val)
    mouse = models.IntegerField(null=False, default=59, validators=val)

    # if True it is cat turn. if False it is mouse turn. Default the cat starts
    cat_turn = models.BooleanField(null=False, default=True)
    status = models.IntegerField(null=False, default=GameStatus.CREATED)

    def cell_is_valid(self, cell):
        if cell < self.MIN_CELL or cell > self.MAX_CELL:
            return False
        row = int(cell) / 8
        col = int(cell) % 8
        if int(row) % 2 != col % 2:
            return False
        return True

    def validate(self):
        # Status validation
        if self.mouse_user is None and self.status != GameStatus.CREATED:
            raise ValidationError(constants.MSG_ERROR_GAMESTATUS)
        if self.mouse_user is None:
            self.status = GameStatus.CREATED
        elif self.status != GameStatus.FINISHED:
            self.status = GameStatus.ACTIVE
        # Position validation
        for cell in self.get_array_positions():
            if not self.cell_is_valid(cell=cell):
                raise ValidationError(constants.MSG_ERROR_INVALID_CELL)
        return True

    def save(self, *args, **kwargs):
        if self.validate() is True:
            super(Game, self).save(*args, **kwargs)

    def get_array_positions(self):
        return [self.cat1, self.cat2, self.cat3, self.cat4, self.mouse]

    def get_cat_positions(self):
        return [self.cat1, self.cat2, self.cat3, self.cat4]

    def get_game_cells(self):
        game_cells = []
        for i in range(0, 64):
            if i == self.mouse:
                game_cells.append(-1)
            elif i in self.get_cat_positions():
                game_cells.append(1)
            else:
                game_cells.append(0)
        return game_cells

    def mouse_alternatives(self):
        alternatives = []
        m = self.mouse
        # alternatives in the four directions, if they are valid
        if self.cell_is_valid(m-9):
            alternatives.append(m-9)
        if self.cell_is_valid(m-7):
            alternatives.append(m-7)
        if self.cell_is_valid(m+7):
            alternatives.append(m+7)
        if self.cell_is_valid(m+7):
            alternatives.append(m+9)
        return alternatives

    def mouse_is_trapped(self):
        if self.cat_turn is False:
            return False
        for target in self.mouse_alternatives():
            if target not in self.get_cat_positions():
                return False
        self.status = GameStatus.FINISHED
        return True

    def mouse_at_top(self):
        if int(self.mouse/8) <= int(min(self.get_cat_positions())/8):
            self.status = GameStatus.FINISHED
            return True
        return False

    def get_status_str(self):
        if self.status == GameStatus.ACTIVE:
            return "Active"
        elif self.status == GameStatus.FINISHED:
            return "Finished"
        else:
            return "Created"

    def __str__(self):
        status = "(" + str(self.id) + ", " + self.get_status_str() + ")"
        cat_positions = str(self.cat1) + ", " + str(self.cat2) + ", "
        cat_positions += str(self.cat3) + ", " + str(self.cat4)
        cat = "\tCat [X] " if self.cat_turn else "\tCat [ ] "
        cat += str(self.cat_user) + "(" + cat_positions + ")"
        mouse = ""
        if self.mouse_user:
            mouse = " --- Mouse [ ] " if self.cat_turn else " --- Mouse [X] "
            mouse += str(self.mouse_user) + "(" + str(self.mouse) + ")"
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
    game = models.ForeignKey(Game, on_delete=models.CASCADE,
                             related_name="moves")
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)

    def cat_moving_well(self):
        origin = int(self.origin)
        target = int(self.target)

        # The target is empty validation
        if target in self.game.get_array_positions():
            raise ValidationError(constants.MSG_ERROR_MOVE)

        # The target is a valid position validation
        if not self.game.cell_is_valid(target):
            raise ValidationError(constants.MSG_ERROR_MOVE)

        # If its a cat, the target is origin + 7 or origin + 9
        if origin + 7 != target and origin + 9 != target:
            raise ValidationError(constants.MSG_ERROR_MOVE)

        return True

    def mouse_moving_well(self):
        # The target is empty validation
        if self.target in self.game.get_array_positions():
            raise ValidationError(constants.MSG_ERROR_MOVE)

        # The target is a valid position validation
        if self.target not in self.game.mouse_alternatives():
            raise ValidationError(constants.MSG_ERROR_MOVE)

        return True

    def validate(self):
        # We check if the game is active
        if self.game.status != GameStatus.ACTIVE:
            raise ValidationError(constants.MSG_ERROR_MOVE)

        # If is cat_turn, then the player must be the cat
        if self.player == self.game.cat_user and self.game.cat_turn:

            origin = int(self.origin)

            if self.cat_moving_well():
                if origin is self.game.cat1:
                    self.game.cat1 = self.target
                elif origin is self.game.cat2:
                    self.game.cat2 = self.target
                elif origin is self.game.cat3:
                    self.game.cat3 = self.target
                elif origin is self.game.cat4:
                    self.game.cat4 = self.target
                else:
                    # Moving from an empty cell
                    raise ValidationError(constants.MSG_ERROR_MOVE)

                self.game.cat_turn = False
                self.game.save()
                return True

        # If is mouse turn
        elif self.player == self.game.mouse_user and not self.game.cat_turn \
                and self.mouse_moving_well():
            self.game.mouse = self.target
            self.game.cat_turn = True
            self.game.save()
            return True

        raise ValidationError(constants.MSG_ERROR_MOVE)

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
            raise ValidationError(constants.MSG_ERROR_NEW_COUNTER)

    def __str__(self):
        return "The counter id is:: " + str(self.id) + \
               "\nAnd the value is: " + str(self.value)
