from django.http import HttpResponseForbidden
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from datamodel import constants
from datamodel.models import Game, Move, Counter, User
from logic.forms import SignupForm, LogInForm


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
