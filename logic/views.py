from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
import json

from datamodel import constants
from datamodel.models import Game, Move, Counter, GameStatus
from logic.forms import SignupForm, LogInForm, MoveForm


def anonymous_required(f):
    def wrapped(request):
        if request.user.is_authenticated:
            return HttpResponseForbidden(
                errorHTTP(request,
                          exception="Action restricted to anonymous users"))
        else:
            return f(request)
    return wrapped


def errorHTTP(request, exception=None):
    context_dict = {}
    context_dict[constants.ERROR_MESSAGE_ID] = exception
    return render(request, "mouse_cat/error.html", context_dict)


def index(request):
    request.session['playhead'] = -1
    if request.user.is_authenticated:
        return redirect(reverse('select_game'))
    return redirect(reverse('login'))


@anonymous_required
def login_service(request):
    request.session['playhead'] = -1
    user_form = LogInForm()
    if request.method == 'POST':
        user_form = LogInForm(data=request.POST)
        if user_form.is_valid():
            user = authenticate(username=request.POST.get('username'),
                                password=request.POST.get('password'))
            login(request, user)
            request.session['counter'] = 0
            request.session.modified = True
            return redirect(reverse('index'))

    return render(request, 'mouse_cat/login.html', {'user_form': user_form})


@login_required
def logout_service(request):
    request.session['playhead'] = -1
    logout(request)
    return redirect(reverse('index'))


@anonymous_required
def signup_service(request):
    request.session['playhead'] = -1
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
    request.session['playhead'] = -1
    # If there is no counter we create it
    if 'counter' not in request.session:
        request.session['counter'] = 1
    else:
        request.session['counter'] += 1

    counter_session = request.session['counter']
    counter_global = Counter.objects.inc()

    return render(request, 'mouse_cat/counter.html',
                  {'counter_session': counter_session,
                   'counter_global': counter_global})


@login_required
def create_game_service(request):
    request.session['playhead'] = -1
    # create the game
    game = Game(cat_user=request.user)
    game.save()
    return render(request, "mouse_cat/new_game.html", {'game': game})


@login_required
def join_game_service(request):
    request.session['playhead'] = -1
    # If there are no games to join, render error message
    if Game.objects.count() == 0:
        return render(request, "mouse_cat/join_game.html",
                      {'msg_error': "No games to join! Let a cat start a game first!"})

    # Get game with greater id
    games = Game.objects.filter(mouse_user=None)
    id_game = max((game.id for game in list(
        filter(lambda g: g.cat_user != request.user, games))), default=None)
    if id_game is None:
        return render(request, "mouse_cat/join_game.html",
                      {'msg_error': "No games to join! Let a cat start a game first!"})

    game = Game.objects.get(id=id_game)

    # User joins the game
    game.mouse_user = request.user
    game.save()
    return redirect(reverse('select_game'))


@login_required
def select_game_service(request, game_id=-1):
    request.session['playhead'] = -1
    context_dict = {}

    user = request.user
    if game_id == -1:
        # if method is get we show all the games
        as_c = Game.objects.filter(cat_user=user, status=GameStatus.ACTIVE)
        as_m = Game.objects.filter(mouse_user=user, status=GameStatus.ACTIVE)
        fg_c = Game.objects.filter(cat_user=user, status=GameStatus.FINISHED)
        fg_m = Game.objects.filter(mouse_user=user, status=GameStatus.FINISHED)
        fg = fg_c | fg_m
        context_dict['as_cat'] = as_c
        context_dict['as_mouse'] = as_m
        context_dict['finished_games'] = fg

        return render(request, "mouse_cat/select_game.html", context_dict)

    # POST in a bad way
    game = Game.objects.filter(id=game_id).first()
    if not game or (game.status != GameStatus.ACTIVE and game.status != GameStatus.FINISHED):
        return HttpResponseNotFound(constants.ERROR_NOT_FOUND)
    else:
        if game.status == GameStatus.FINISHED:
            request.session['game_id'] = game.id
            return redirect(reverse('replay'))
        if game.cat_user == user or game.mouse_user == user:
            request.session['game_id'] = game.id
            return redirect(reverse('show_game'))
        else:
            return HttpResponseNotFound(constants.ERROR_NOT_FOUND)


@login_required
def get_move_service(request):

    if request.method != 'POST' or "shift" not in request.POST or 'game_id' not in request.session:
        return HttpResponseNotFound()

    if 'playhead' not in request.session:
        request.session['playhead'] = -1

    shift = int(request.POST.get("shift"))
    moves = Move.objects.all().filter(game_id=request.session['game_id'])
    origins = []
    targets = []
    prev = True
    next = True
    for move in moves:
        origins.append(move.origin)
        targets.append(move.target)

    if shift >= 0:
        request.session['playhead'] += int(shift)
        if request.session['playhead'] == len(origins)-1:
            next = False
        if request.session['playhead'] >= len(origins):
            request.session['playhead'] -= int(shift)
        dict = {'origin': origins[request.session['playhead']], 'target': targets[request.session['playhead']], 'previous': prev, 'next': next}
    else:
        if request.session['playhead'] <= 0:
            prev = False
        if request.session['playhead'] < 0:
            request.session['playhead'] = 0
        dict = {'origin': targets[request.session['playhead']], 'target': origins[request.session['playhead']], 'previous': prev, 'next': next}
        request.session['playhead'] += int(shift)
    return JsonResponse(dict)


@login_required
def show_game_service(request):
    request.session['playhead'] = -1
    context_dict = {}

    if 'game_id' not in request.session:
        return redirect(reverse('index'))

    game = Game.objects.get(id=request.session['game_id'])
    if game.mouse_is_trapped() or game.mouse_at_top():
        game.status = GameStatus.FINISHED
        game.save()

    context_dict['game'] = game
    context_dict['board'] = game.get_game_cells()
    context_dict['move_form'] = MoveForm()

    return render(request, "mouse_cat/game.html", context_dict)


@login_required
def replay_service(request):
    context_dict = {}

    if 'game_id' not in request.session:
        return redirect(reverse('index'))

    game = Game.objects.get(id=request.session['game_id'])
    context_dict['game'] = game
    context_dict['board'] = game.get_game_initial_cells()
    return render(request, "mouse_cat/replay.html", context_dict)


@login_required
def move_service(request):
    request.session['playhead'] = -1
    # Check if there's a user
    if not request.user:
        return redirect(reverse('login'))

    player = request.user

    if 'game_id' in request.session.keys():
        game_id = request.session['game_id']
        game = Game.objects.get(id=game_id)

        if request.method == 'POST':
            movement = MoveForm(request.POST)
            if movement.is_valid():
                try:
                    Move.objects.create(game=game, player=player,
                                        origin=int(movement.data['origin']),
                                        target=int(movement.data['target']))
                except(ValidationError):
                    print("Error: Invalid move")
            else:
                print("Error: Invalid move")
            return redirect(reverse('show_game'))

    return HttpResponseNotFound(constants.ERROR_NOT_FOUND)
