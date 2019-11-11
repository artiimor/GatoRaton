from django import forms
from django.contrib.auth.models import User


# Same that in tango with django
class SignupForm(forms.ModelForm):

    username = forms.CharField(max_length=128, help_text="Please enter the username name.", required=True)
    password = forms.CharField(max_length=128, help_text="Please enter the password.", required=True)
    password_confirm = forms.CharField(max_length=128, help_text="Please enter the password.", required=True)

    def validate(self):
        if len(self.username) < 3 or len(self.password) < 3:
            return False
        if self.password != self.password_confirm:
            return False
        return True

    class Meta:
        model = User
        fields = ('username', 'password')