"""
@author: rlatorre
"""

import re, json
from decimal import Decimal

from datamodel import constants
from datamodel.models import Counter, Game, GameStatus, Move
from datamodel.tests import BaseModelTest
from django.contrib.auth.models import User
from django.db.models import Max, Q
from django.test import Client, TestCase
from django.urls import reverse

from . import forms
from . import tests_services

GET_MOVE_SERVICE = "get_move"


class GetMoveServiceTests(tests_services.PlayGameBaseServiceTests):
    def setUp(self):
        super().setUp()

        self.game = Game.objects.create(
            cat_user=self.user1, mouse_user=self.user2, status=GameStatus.ACTIVE)
        self.moves = [
            {"player": self.user1, "origin": 0, "target": 9},
            {"player": self.user2, "origin": 59, "target": 50},
            {"player": self.user1, "origin": 2, "target": 11},
        ]

        for move in self.moves:
            Move.objects.create(
                game=self.game, player=move["player"], origin=move["origin"], target=move["target"])
        self.game.status = GameStatus.FINISHED
        self.game.save()

    def tearDown(self):
        super().tearDown()

    def test1(self):
        """ GET no permitido """
        self.set_game_in_session(self.client1, self.user1, self.game.id)
        response = self.client.get(reverse(GET_MOVE_SERVICE), {"shift": 1}, follow=True)
        self.assertEqual(response.status_code, 404)

    def test2(self):
        """ Secuencia de movimientos válidos """
        self.set_game_in_session(self.client1, self.user1, self.game.id)
        n_move = 0
        for move in self.moves:
            response = self.client1.post(
                reverse(GET_MOVE_SERVICE), {"shift": 1}, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code, 200)
            data = json.loads(self.decode(response.content))
            self.assertEqual(data["origin"], move["origin"])
            self.assertEqual(data["target"], move["target"])
            self.assertTrue(data["previous"])
            self.assertEqual(data["next"], n_move != len(self.moves)-1)
            n_move += 1

        self.moves.reverse()
        n_move = 0
        for move in self.moves:
            response = self.client1.post(
                reverse(GET_MOVE_SERVICE), {"shift": -1}, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code, 200)
            data = json.loads(self.decode(response.content))
            self.assertEqual(data["origin"], move["target"])
            self.assertEqual(data["target"], move["origin"])
            self.assertTrue(data["next"])
            self.assertEqual(data["previous"], n_move != len(self.moves)-1)
            n_move += 1
