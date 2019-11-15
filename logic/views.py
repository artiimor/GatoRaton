from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from datamodel import constants
from datamodel.models import Game, Move, Counter, User
from logic.forms import MoveForm


def anonymous_required(f):
    def wrapped(request):
        if request.user.is_authenticated:
            return HttpResponseForbidden(
                errorHTTP(request, exception="Action restricted to anonymous users"))
        else:
            return f(request)
    return wrapped


def errorHTTP(request, exception=None):
    context_dict = {}
    context_dict[constants.ERROR_MESSAGE_ID] = exception
    return render(request, "mouse_cat/error.html", context_dict)


def index(request):
    return render(request, "mouse_cat/index.html")


@anonymous_required
def login_service(request):
    # It is exactly the same we used in tango with django :)

    # If its a post we pull out the relevant information
    if request.method == 'POST':
        # Get the username and password
        username = request.POST.get('username')
        password = request.POST.get('password')

        # and autenticate it. Djando has his own method
        user = authenticate(username=username, password=password)

        # if everything went well
        if user:
            # If the acount is active
            if user.is_active:
                # We send the user to the main page
                login(request, user)
                return redirect(reverse('logic:index'))
            else:
                # The account is inactive
                return HttpResponse("Your Cat account is disabled")

        else:
            # Bad login information
            print("invalid login detains: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied")

    # If the request is not a post then we render the login template
    else:
        return render(request, 'mouse_cat/login.html')


@login_required
def logout_service(request):
    # Also the same in tango with django
    logout(request)

    return redirect(reverse('rango:index'))


@anonymous_required
def signup_service(request):

    # This is even easies that the tango with django's one
    if request.method == 'POST':

        user_form = User(data=request.POST)

        # If the two forms are valid
        if user_form.is_valid():
            # Save the user onto the database
            user = user_form.save()

            # Set the password and stores it
            user.set_password(user.password)
            user.save()

        else:
            # there has been some kind of error
            print(user_form.errors)

    else:
        # Not a post, so render the forms for allowing the registration
        user_form = User()

    # Of course we have to render the template
    return render(request, 'mouse_cat/singup.html', {'user_form': user_form})


def counter_service(request):
    context_dict = {}

    # If there is no counter we create it
    if 'counter' not in request.session:
        request.session['counter'] = 0

    counter_session = request.session['counter']
    context_dict['counter_session'] = counter_session

    # Now the global counter
    counter_global = Counter.value
    context_dict['counter_global'] = counter_global

    return render(request, 'mouse_cat/counter', context_dict)


@login_required
def create_game_service(request):
    context_dict = {}

    # create the game
    game = Game(cat_user=request.user)
    game.save()

    context_dict['game'] = game

    return render(request, "mouse_cat/new_game.html", context_dict)


@login_required
def join_game_service(request):
    context_dict = {}

    # Same that in test_query
    game_aux = Game.objects.filter(mouse_user=None)
    game = game_aux[0]

    for g in game_aux:
        if g.id < game.id:
            game = g

    # game is the game with less id
    game.mouse_user = request.user
    game.save()

    context_dict['game'] = game

    return render(request, "mouse_cat/join_game.html", context_dict)


@login_required
def select_game_service(request):
    context_dict = {}
    # Select one game to play
    if request.method == 'POST':
        game_id = request.POST.get('game_id')
        request.session['game'] = Game.object.filter(id=game_id)

        return redirect(reverse('mouse_cat:show_game'))

    # if method is get we show all the games
    user = request.user
    cat_games = Game.objects.filter(cat_user=user)
    mouse_games = Game.objects.filter(mouse_user=user)

    context_dict['as_cat'] = cat_games
    context_dict['as_mouse'] = mouse_games

    return render(request, "mouse_cat/select_game.html", context_dict)


def show_game_service(request):
    context_dict = {}

    # If we don't know the user render login
    if 'user' not in request.session:
        return render(request, 'mouse_cat/login.html')

    game = request.session['game']
    user = request.session['user']

    game_cells = []
    ocupped_cells = game.get_array_positions()
    mouse_cell = ocupped_cells[-1]

    for i in range(0,64):
        if i == mouse_cell:
            game_cells[i] = -1
        elif i in ocupped_cells:
            game_cells[i] = 1
        else:
            game_cells[i] = 0

    context_dict['game'] = game
    context_dict['board'] = game_cells

    return render(request, "mouse_cat/game.html", context_dict)


@login_required
def move_service(request):
    context_dict = {}

    # Check if there's a user
    if not request.user:
        redirect(reverse('mouse_cat:login'))

    player = request.user

    if 'game_id' in request.session.keys():
        game_id = request.session['game_id']

        if request.method == 'POST':
            movement = MoveForm(request.POST)
            game = Game.objects.get(id=game_id)

            Move.objects.create(game=game, player=player,
                                origin=movement.data['origin'], target=movement.data['target'])

            return redirect(reverse('show_game'))

    return HttpResponseNotFound('<h1>There was a problem</h1>')
