"""
@author: rlatorre
"""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from . import tests
from .models import Counter, Game, GameStatus, Move


class GameModelTests(tests.BaseModelTest):
    def setUp(self):
        super().setUp()

    def test1(self):
        """ Crear juego válido con un único jugador """
        game = Game(cat_user=self.users[0])
        game.full_clean()
        game.save()
        self.assertIsNone(game.mouse_user)
        self.assertEqual(self.get_array_positions(game), [0, 2, 4, 6, 59])
        self.assertTrue(game.cat_turn)
        self.assertEqual(game.status, GameStatus.CREATED)

    def test2(self):
        """ Optional """
        """ Crear juego válido con dos jugadores """
        game = Game(cat_user=self.users[0], mouse_user=self.users[1])
        game.save()
        self.assertEqual(self.get_array_positions(game), [0, 2, 4, 6, 59])
        self.assertTrue(game.cat_turn)
        self.assertEqual(game.status, GameStatus.ACTIVE)

    def test3(self):
        """ Optional """
        """ Transición de creado a activo al añadir el segundo jugador """
        game = Game(cat_user=self.users[0])
        game.save()
        self.assertEqual(game.status, GameStatus.CREATED)
        game.mouse_user = self.users[1]
        game.save()
        self.assertEqual(game.status, GameStatus.ACTIVE)

    def test4(self):
        """ Estados válidos de juegos con dos jugadores """
        states = [
            {"status": GameStatus.ACTIVE, "valid": True},
            {"status": GameStatus.FINISHED, "valid": True}
        ]

        for state in states:
            game = Game(cat_user=self.users[0], mouse_user=self.users[1], status=state["status"])
            game.full_clean()
            game.save()
            self.assertEqual(game.status, state["status"])

    def test5(self):
        """ Estados válidos con un jugador """
        states = [
            {"status": GameStatus.CREATED, "valid": True},
            {"status": GameStatus.ACTIVE, "valid": False},
            {"status": GameStatus.FINISHED, "valid": False}
        ]

        for state in states:
            try:
                game = Game(cat_user=self.users[0], status=state["status"])
                game.full_clean()
                game.save()
                self.assertEqual(game.status, state["status"])
            except ValidationError as err:
                with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_GAMESTATUS):
                    if not state["valid"]:
                        raise err

    def test6(self):
        """ Juegos sin jugador 1 """
        for status in [GameStatus.CREATED, GameStatus.ACTIVE, GameStatus.FINISHED]:
            with self.assertRaises(ValidationError):
                game = Game(mouse_user=self.users[1], status=status)
                game.full_clean()

    def test7(self):
        """ Model test """
        """ Validación de celdas válidas """
        # MIN_CELL = 0, MAX_CELL = 63
        for id_cell in [Game.MIN_CELL, Game.MAX_CELL]:
            game = Game(
                cat_user=self.users[0], cat1=id_cell, cat2=id_cell,
                cat3=id_cell, cat4=id_cell, mouse=id_cell)
            game.full_clean()
            game.save()

    def test8(self):
        """ Piezas fuera del tablero """
        for id_cell in [Game.MIN_CELL - 1, Game.MAX_CELL + 1]:
            with self.assertRaises(ValidationError):
                game = Game(cat_user=self.users[0], mouse_user=self.users[1], cat1=id_cell)
                game.full_clean()
            with self.assertRaises(ValidationError):
                game = Game(cat_user=self.users[0], mouse_user=self.users[1], cat2=id_cell)
                game.full_clean()
            with self.assertRaises(ValidationError):
                game = Game(cat_user=self.users[0], mouse_user=self.users[1], cat3=id_cell)
                game.full_clean()
            with self.assertRaises(ValidationError):
                game = Game(cat_user=self.users[0], mouse_user=self.users[1], cat4=id_cell)
                game.full_clean()
            with self.assertRaises(ValidationError):
                game = Game(cat_user=self.users[0], mouse_user=self.users[1], mouse=id_cell)
                game.full_clean()

    def test9(self):
        """ Relaciones inversas entre User y Game"""
        self.assertEqual(self.users[0].games_as_cat.count(), 0)
        self.assertEqual(self.users[1].games_as_mouse.count(), 0)
        self.assertEqual(User.objects.filter(games_as_cat__cat_user__username=self.users[0].username).count(), 0)
        self.assertEqual(User.objects.filter(games_as_mouse__mouse_user__username=self.users[1].username).count(), 0)

        game = Game(cat_user=self.users[0], mouse_user=self.users[1])
        game.save()
        self.assertEqual(self.users[0].games_as_cat.count(), 1)
        self.assertEqual(self.users[1].games_as_mouse.count(), 1)
        self.assertEqual(User.objects.filter(games_as_cat__cat_user__username=self.users[0].username).count(), 1)
        self.assertEqual(User.objects.filter(games_as_mouse__mouse_user__username=self.users[1].username).count(), 1)

        game = Game(cat_user=self.users[0])
        game.save()
        self.assertEqual(self.users[0].games_as_cat.count(), 2)
        self.assertEqual(self.users[1].games_as_mouse.count(), 1)
        self.assertEqual(User.objects.filter(games_as_cat__cat_user__username=self.users[0].username).count(), 2)
        self.assertEqual(User.objects.filter(games_as_mouse__mouse_user__username=self.users[1].username).count(), 1)

    def test10(self):
        """ Optional """
        """ Posiciones no válidas dentro del tablero """
        # 26, 44, 62, 7, 56 = black cells
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_INVALID_CELL):
            game = Game(cat_user=self.users[0], cat1=26)
            game.save()
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_INVALID_CELL):
            game = Game(cat_user=self.users[0], cat2=44)
            game.save()
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_INVALID_CELL):
            game = Game(cat_user=self.users[0], cat3=62)
            game.save()
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_INVALID_CELL):
            game = Game(cat_user=self.users[0], cat4=7)
            game.save()
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_INVALID_CELL):
            game = Game(cat_user=self.users[0], mouse=56)
            game.save()

    def test11(self):
        """ Conversiones a string """
        game = Game(id=0, cat_user=self.users[0])
        self.assertEqual(str(game), "(0, Created)\tCat [X] cat_user_test(0, 2, 4, 6)")

        game.mouse_user = self.users[1]
        game.status = GameStatus.ACTIVE
        game.save()
        self.assertEqual(
            str(game),
            "(0, Active)\tCat [X] cat_user_test(0, 2, 4, 6) --- Mouse [ ] mouse_user_test(59)")

        game.cat_turn = False
        self.assertEqual(
            str(game),
            "(0, Active)\tCat [ ] cat_user_test(0, 2, 4, 6) --- Mouse [X] mouse_user_test(59)")

        game.status = GameStatus.FINISHED
        game.save()
        self.assertEqual(
            str(game),
            "(0, Finished)\tCat [ ] cat_user_test(0, 2, 4, 6) --- Mouse [X] mouse_user_test(59)")


class MoveModelTests(tests.BaseModelTest):
    def setUp(self):
        super().setUp()

    def test1(self):
        """ Movimientos válidos """
        game = Game.objects.create(
            cat_user=self.users[0], mouse_user=self.users[1], status=GameStatus.ACTIVE)
        moves = [
            {"player": self.users[0], "origin": 0, "target": 9},
            {"player": self.users[1], "origin": 59, "target": 50},
            {"player": self.users[0], "origin": 2, "target": 11},
        ]

        n_moves = 0
        for move in moves:
            Move.objects.create(
                game=game, player=move["player"], origin=move["origin"], target=move["target"])
            n_moves += 1
            self.assertEqual(game.moves.count(), n_moves)

    def test2(self):
        """ Movimientos en un juego no activo """
        game = Game(cat_user=self.users[0])
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_MOVE):
            Move.objects.create(game=game, player=self.users[0], origin=0, target=9)


class CounterModelTests(TestCase):
    def setUp(self):
        Counter.objects.all().delete()

    def test1(self):
        """ No es posible crear un nuevo contador """
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_NEW_COUNTER):
            Counter.objects.create()

        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_NEW_COUNTER):
            Counter.objects.create(value=0)

    def test2(self):
        """ No es posible crear un nuevo contador """
        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_NEW_COUNTER):
            n = Counter()
            n.save()

        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_NEW_COUNTER):
            n = Counter(0)
            n.save()

        with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_NEW_COUNTER):
            n = Counter(11)
            n.save()

    def test3(self):
        """ Incremento a través del singleton """
        self.assertEqual(Counter.objects.inc(), 1)
        self.assertEqual(Counter.objects.inc(), 2)

    def test4(self):
        """ No es posible crear contadores """
        Counter.objects.inc()
        Counter.objects.inc()

        for i in [3, 4]:
            Counter.objects.inc()
            n = Counter.objects.get(value=i)
            self.assertEqual(n.value, i)
            with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_NEW_COUNTER):
                n.save()

    def test5(self):
        """ Devolución correcta del valor del contador """
        self.assertEqual(Counter.objects.get_current_value(), 0)
        Counter.objects.inc()
        self.assertEqual(Counter.objects.get_current_value(), 1)
