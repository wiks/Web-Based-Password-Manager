from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from mysite.core.models import LoginPass
from django.forms import ModelForm

from django.utils.translation import gettext_lazy as _

# from django.core import validators
# from django.forms import CharField


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )


class LoginPassForm(ModelForm):

    class Meta:
         model = LoginPass
         # ownerid = models.ForeignKey(User, on_delete=models.CASCADE)
         # pagename = models.CharField(max_length=255)
         # url = models.URLField()
         # login_name = models.CharField(max_length=100)
         # login_pass = models.CharField(max_length=100)
         fields = '__all__'
         exclude = ['ownerid']
         labels = {
             'pagename': _('page name'),
             'url': _('url address'),
             'login_name': ('login name'),
         }
         help_texts = {
             'pagename': _('Your nick-name of page.'),
             'login_name': ('your login'),
             'login_pass': ('your password'),

         }
         # widgets = {
         #     'login_pass': forms.PasswordInput(),
         # }

    def clean(self):

        cleaned_data = super().clean()

        # print('CLEANED DATA:')
        # print( cleaned_data )



    # class owneridFiels(CharField):
    #
    #     default_validators = [validators.validate_ownerid]
