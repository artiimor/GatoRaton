from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import password_validation, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from datamodel.models import Move


class SignupForm(UserCreationForm):

    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    password1 = forms.CharField(widget=forms.HiddenInput(), required=False)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput(), required=True)

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False

    def clean_password(self):
        password = self.cleaned_data.get('password')
        password_validation.validate_password(password)
        return password

    def clean_password2(self):
        password2 = self.cleaned_data.get('password2')
        password = self.cleaned_data.get('password')
        if password != password2 and password and password2:
            raise ValidationError("Password and Repeat password are not the same", code='signup_error1')

        return password2

    def save(self):
        user = super(SignupForm, self).save()
        user.set_password(self.cleaned_data.get('password'))
        user.save()
        return user

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password')


class LogInForm(AuthenticationForm):

    def is_valid(self):
        if not User.objects.filter(username=self.data['username']).exists():
            self.add_error(None, "Username/password is not valid")
            return False
        if not authenticate(username=self.data['username'], password=self.data['password']):
            self.add_error(None, "Username/password is not valid")
            return False
        return super(LogInForm, self).is_valid()

    class Meta:
        model = User
        fields = ('username', 'password')


class MoveForm(forms.ModelForm):
    origin = forms.IntegerField(initial=0, required=True)
    target = forms.IntegerField(initial=0, required=True)

    def __init__(self, *args, **kwargs):
        super(MoveForm, self).__init__(*args, **kwargs)

    def is_valid(self):
        if int(self.data['origin']) not in range(0, 64) or int(self.data['target']) not in range(0, 64):
            self.add_error(None, "Move not allowed")
            return False
        return super(MoveForm, self).is_valid()

    class Meta:
        # Provide an association between the ModelForm and a model
        model = Move
        fields = ('origin', 'target')
