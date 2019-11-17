import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ratonGato.settings')

import django

django.setup()

from datamodel.models import User, Game

# First we need an user with id as 10
user_aux = User.objects.filter(id=10)

if user_aux:
    user10 = user_aux[0]
    print("user with id=10 existed")
else:
    user10 = User(id=10, username='user10', password='password123')
    user10.save()
    print("User with id=10 don't exist. I had to create it.")


# Now, the same proccess with an user with id 11
user_aux = User.objects.filter(id=11)

if user_aux:
    user11 = user_aux[0]
    print("user with id=11 existed")
else:
    user11 = User(id=11, username='user11', password='password456')
    user11.save()
    print("User with id=11 didn't exist. I had to create it.")

# Create a game for the user with id 10
game = Game(cat_user=user10)
game.save()

# Look for every games with only one user
game_aux = Game.objects.filter(mouse_user=None)
for g in game_aux:
    if g.id < game.id:
        game = g
    print(g)

# User11 is the mouse in the game with smaller id
game.mouse_user = user11
game.save()

# Move cat2 from position 2 to 11
game.cat2 = 11
game.save()
# Announce it
print("We moved cat2 to 11 position")
print(game)

# Move mouse from position 59 to 52
game.mouse = 52
game.save()
# Announce it
print("We moved mouse from position 59 to 52")
print(game)

print("That's all folks :)")
