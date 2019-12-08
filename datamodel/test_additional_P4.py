from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from . import tests
from .models import Counter, Game, GameStatus, Move


class GameVictoryTests(tests.BaseModelTest):
    def setUp(self):
        super().setUp()

    def test1(self):
        """ Check cats win when the cats trapped the mouse """
        """
            Initial state:
            
            |00|xx|02|xx|04|xx|06|xx|
            |xx|09|xx|11|xx|13|xx|15|
            |16|xx|18|xx|20|xx|22|xx|
            |xx|C1|xx|27|xx|29|xx|31|
            |32|xx|34|xx|C2|xx|38|xx|
            |xx|41|xx|M |xx|45|xx|47|
            |48|xx|C3|xx|C4|xx|54|xx|
            |xx|57|xx|59|xx|61|xx|63|
            
            Final state after moving the cat 1
                
            |00|xx|02|xx|04|xx|06|xx|
            |xx|09|xx|11|xx|13|xx|15|
            |16|xx|18|xx|20|xx|22|xx|
            |xx|25|xx|27|xx|29|xx|31|
            |32|xx|C1|xx|C2|xx|38|xx|
            |xx|41|xx|M |xx|45|xx|47|
            |48|xx|C3|xx|C4|xx|54|xx|
            |xx|57|xx|59|xx|61|xx|63|
        """
        game = Game(cat_user=self.users[0], mouse_user=self.users[1])
        game.full_clean()
        game.cat1 = 25
        game.cat2 = 36
        game.cat3 = 50
        game.cat4 = 52
        game.mouse = 43
        game.save()
        self.assertEqual(game.mouse_is_trapped(), False)  # The cat is not trapped
        self.assertEqual(game.status, GameStatus.ACTIVE)  # The game is active
        self.assertEqual(game.cat_turn, True)  # It's cat turn
        Move.objects.create(game=game, player=game.cat_user,
                            origin=25,
                            target=34)
        self.assertEqual(game.mouse_is_trapped(), True)
        self.assertEqual(game.status, GameStatus.FINISHED)
        self.assertEqual(game.cat_wins, True)

    def test2(self):
        """ Check mouse win when he arrives to the top """
        """
            Initial state:

            |00|xx|02|xx|04|xx|C4|xx|
            |xx|09|xx|M |xx|13|xx|15|
            |16|xx|18|xx|20|xx|22|xx|
            |xx|C1|xx|C2|xx|C3|xx|31|
            |32|xx|34|xx|36|xx|38|xx|
            |xx|41|xx|M |xx|45|xx|47|
            |48|xx|50|xx|52|xx|54|xx|
            |xx|57|xx|59|xx|61|xx|63|

            Final state after moving the cat 1

            |00|xx|M |xx|04|xx|C4|xx|
            |xx|09|xx|11|xx|13|xx|15|
            |16|xx|18|xx|20|xx|22|xx|
            |xx|25|xx|27|xx|29|xx|31|
            |32|xx|C1|xx|C2|xx|38|xx|
            |xx|41|xx|43|xx|45|xx|47|
            |48|xx|50|xx|52|xx|54|xx|
            |xx|57|xx|59|xx|61|xx|63|
        """
        game = Game(cat_user=self.users[0], mouse_user=self.users[1])
        game.full_clean()
        game.cat1 = 25
        game.cat2 = 27
        game.cat3 = 29
        game.mouse = 11
        game.cat_turn = False
        game.save()
        self.assertEqual(game.mouse_is_trapped(), False)  # The cat is not trapped
        self.assertEqual(game.status, GameStatus.ACTIVE)  # The game is active
        self.assertEqual(game.cat_turn, False)  # It's mouse turn
        Move.objects.create(game=game, player=game.mouse_user,
                            origin=11,
                            target=2)
        self.assertEqual(game.mouse_is_trapped(), False)
        self.assertEqual(game.mouse_at_top(), True)  # It turns the game to finished
        self.assertEqual(game.status, GameStatus.FINISHED)
        self.assertEqual(game.cat_wins, False)

    def test3(self):
        """ Check mouse win when he overcome the higher cat/s """
        """
            Initial state:

            |00|xx|02|xx|04|xx|06|xx|
            |xx|09|xx|C1|xx|C2|xx|15|
            |16|xx|M |xx|20|xx|22|xx|
            |xx|C3|xx|C4|xx|29|xx|31|
            |32|xx|34|xx|36|xx|38|xx|
            |xx|41|xx|43|xx|45|xx|47|
            |48|xx|50|xx|52|xx|54|xx|
            |xx|57|xx|59|xx|61|xx|63|

            Final state after moving the mouse

            |00|xx|02|xx|04|xx|06|xx|
            |xx|M |xx|C1|xx|C2|xx|15|
            |16|xx|18|xx|20|xx|22|xx|
            |xx|C3|xx|C4|xx|29|xx|31|
            |32|xx|34|xx|36|xx|38|xx|
            |xx|41|xx|43|xx|45|xx|47|
            |48|xx|50|xx|52|xx|54|xx|
            |xx|57|xx|59|xx|61|xx|63|
        """
        game = Game(cat_user=self.users[0], mouse_user=self.users[1])
        game.full_clean()
        game.cat1 = 11
        game.cat2 = 13
        game.cat3 = 25
        game.cat4 = 27
        game.mouse = 18
        game.cat_turn = False
        game.save()
        self.assertEqual(game.mouse_is_trapped(), False)  # The cat is not trapped
        self.assertEqual(game.status, GameStatus.ACTIVE)  # The game is active
        self.assertEqual(game.cat_turn, False)  # It's mouse turn
        Move.objects.create(game=game, player=game.mouse_user,
                            origin=18,
                            target=9)
        self.assertEqual(game.mouse_is_trapped(), False)
        self.assertEqual(game.mouse_at_top(), True)  # It turns the game to finished
        self.assertEqual(game.status, GameStatus.FINISHED)
        self.assertEqual(game.cat_wins, False)
