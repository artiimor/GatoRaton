"""
@author: rlatorre
"""

from django.contrib.auth.models import User
from django.test import TestCase

MSG_ERROR_INVALID_CELL = "Invalid cell for a cat or the mouse|Gato o ratón en posición no válida"
MSG_ERROR_GAMESTATUS = "Game status not valid|Estado no válido"
MSG_ERROR_MOVE = "Move not allowed|Movimiento no permitido"
MSG_ERROR_NEW_COUNTER = "Insert not allowed|Inseción no permitida"


class BaseModelTest(TestCase):
    def setUp(self):
        self.users = []
        for name in ['cat_user_test', 'mouse_user_test']:
            self.users.append(self.get_or_create_user(name))

    @classmethod
    def get_or_create_user(cls, name):
        try:
            user = User.objects.get(username=name)
        except User.DoesNotExist:
            user = User.objects.create_user(username=name, password=name)

        return user

    @classmethod
    def get_array_positions(cls, game):
        return [game.cat1, game.cat2, game.cat3, game.cat4, game.mouse]
