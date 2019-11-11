"""
@author: rlatorre
"""

from django.core.exceptions import ValidationError

from datamodel import tests
from datamodel.models import Game, GameStatus, Move


class GameMoveTests(tests.BaseModelTest):
    def setUp(self):
        super().setUp()
        self.game = Game.objects.create(
            cat_user=self.users[0], mouse_user=self.users[1], status=GameStatus.ACTIVE)

    def test1(self):
        """ Solo los jugadores pueden mover """
        no_player = self.get_or_create_user("no_player")
        moves = [
            {"origin": 0, "target": 9},
            {"origin": 59, "target": 50},
        ]

        for move in moves:
            with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
                Move.objects.create(
                    game=self.game, player=no_player, origin=move["origin"], target=move["target"])
            self.assertEqual(self.game.moves.count(), 0)

    def test2(self):
        """ Secuencia de movimientos correcta y actualización del estado del juego al mover """
        moves = [
            {"origin": 0, "target": 9, "positions": [9, 2, 4, 6, 59]},
            {"origin": 2, "target": 11, "positions": [9, 11, 4, 6, 59]},
            {"origin": 4, "target": 13, "positions": [9, 11, 13, 6, 59]},
            {"origin": 6, "target": 15, "positions": [9, 11, 13, 15, 59]},
        ]

        n_moves = 0
        for move in moves:
            Move.objects.create(
                game=self.game, player=self.users[0], origin=move["origin"], target=move["target"])
            n_moves += 1
            self.assertEqual(move["positions"], self.get_array_positions(self.game))
            self.assertFalse(self.game.cat_turn)
            self.assertEqual(self.game.moves.count(), n_moves)

            self.game.cat_turn = not self.game.cat_turn
            self.game.save()

    def test3(self):
        """ Movimientos válidos y no válidos de gatos por destino """
        confs = [
            {"cats": [2, 0, 4, 6], "origin": 0, "valid_moves": [9]},
            {"cats": [0, 20, 4, 6], "origin": 20, "valid_moves": [27, 29]},
            {"cats": [0, 20, 27, 29], "origin": 20, "valid_moves": []},
            {"cats": [0, 57, 27, 29], "origin": 57, "valid_moves": []},
            {"cats": [0, 52, 27, 29], "origin": 52, "valid_moves": [61]},
        ]

        n_moves = 0
        for conf in confs:
            for target in range(Game.MIN_CELL-1, Game.MAX_CELL+2):
                self.game.cat1 = conf["cats"][0]
                self.game.cat2 = conf["cats"][1]
                self.game.cat3 = conf["cats"][2]
                self.game.cat4 = conf["cats"][3]
                self.game.cat_turn = True
                self.game.save()

                if target in conf["valid_moves"]:
                    Move.objects.create(
                        game=self.game, player=self.users[0], origin=conf["origin"], target=target)
                    n_moves += 1
                    self.assertEqual(self.game.cat2, target)
                    self.assertFalse(self.game.cat_turn)
                    self.assertEqual(self.game.moves.count(), n_moves)
                else:
                    with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
                        Move.objects.create(
                            game=self.game, player=self.users[0], origin=conf["origin"], target=target)

    def test4(self):
        """ Movimientos válidos y no válidos de ratón por destino """
        confs = [
            {"origin": 43, "valid_moves": [34, 36, 50, 52]},
            {"origin": 63, "valid_moves": [54]},
        ]

        n_moves = 0
        for conf in confs:
            for target in range(Game.MIN_CELL-1, Game.MAX_CELL+2):
                self.game.mouse = conf["origin"]
                self.game.cat_turn = False
                self.game.save()

                if target in conf["valid_moves"]:
                    Move.objects.create(
                        game=self.game, player=self.users[1], origin=conf["origin"], target=target)
                    n_moves += 1
                    self.assertEqual(self.game.mouse, target)
                    self.assertTrue(self.game.cat_turn)
                    self.assertEqual(self.game.moves.count(), n_moves)
                else:
                    with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
                        Move.objects.create(
                            game=self.game, player=self.users[1], origin=conf["origin"], target=target)

    def test5(self):
        """ Movimientos válidos y no válidos por turno """
        confs = [
            {"player": self.users[1], "origin": 59, "target": 50, "positions": [0, 2, 4, 6, 50]},
            {"player": self.users[0], "origin": 0, "target": 9, "positions": [9, 2, 4, 6, 50]},
        ]

        fail = True
        n_moves = 0
        for conf in confs:
            for _ in range(1, 3):
                if fail:
                    with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
                        Move.objects.create(
                            game=self.game, player=conf["player"], origin=conf["origin"], target=conf["target"])
                else:
                    Move.objects.create(
                        game=self.game, player=conf["player"], origin=conf["origin"], target=conf["target"])
                    n_moves += 1
                    self.assertEqual(self.get_array_positions(self.game), conf["positions"])
                    self.assertEqual(self.game.cat_turn, conf["player"] == self.users[1])
                self.assertEqual(self.game.moves.count(), n_moves)

                fail = not fail
                self.game.cat_turn = not self.game.cat_turn
                self.game.save()

    def test6(self):
        """ Movimientos válidos y no válidos por estado del juego """
        Move.objects.create(game=self.game, player=self.users[0], origin=0, target=9)
        self.assertEqual(self.game.moves.count(), 1)
        Move.objects.create(game=self.game, player=self.users[1], origin=59, target=52)
        self.assertEqual(self.game.moves.count(), 2)

        self.game.status = GameStatus.FINISHED
        self.game.save()
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
            Move.objects.create(game=self.game, player=self.users[0], origin=9, target=16)
        self.assertEqual(self.game.moves.count(), 2)
        self.game.cat_turn = False
        self.game.save()
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
            Move.objects.create(game=self.game, player=self.users[1], origin=52, target=59)
        self.assertEqual(self.game.moves.count(), 2)
