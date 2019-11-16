from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from datamodel import constants
from datamodel.models import Game, Move, Counter, User
from logic.forms import SignupForm, LogInForm, MoveForm


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
    user_form = LogInForm()
    if request.method == 'POST':
        user_form = LogInForm(data=request.POST)
        if user_form.is_valid():
            user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
            login(request, user)
            request.session['counter'] = 0
            request.session.modified = True
            return redirect(reverse('index'))

    return render(request, 'mouse_cat/login.html', {'user_form': user_form})


@login_required
def logout_service(request):
    # Also the same in tango with django
    logout(request)

    return redirect(reverse('logic:index'))


@anonymous_required
def signup_service(request):
    user_form = SignupForm()
    if request.method == 'POST':
        user_form = SignupForm(data=request.POST)
        if user_form.is_valid():
            # Save the user onto the database
            user = user_form.save()
            # Signup also logs the user in
            authenticate(username=user_form.cleaned_data.get('username'),
                        password=user_form.cleaned_data.get('password'))
            login(request, user)
            request.session['counter'] = 0
            return render(request, 'mouse_cat/signup.html')
    # Render template. Two cases: GET or user_form not valid
    return render(request, 'mouse_cat/signup.html', {'user_form': user_form})


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

    return render(request, 'mouse_cat/counter.html', context_dict)


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
