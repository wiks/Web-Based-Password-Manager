from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from mysite.core.forms import SignUpForm
from mysite.core.tokens import account_activation_token
from mysite.core.view_app import *
import logging
logger = logging.getLogger(__name__)

def signup(request):

    logger.debug('SIGNUP')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your MySite Account'
            message = render_to_string('auth/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode('utf-8'),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('account_activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', {'form': form})


def account_activation_sent(request):

    logger.debug('ACCOUNT ACTIVATION SENT')
    return render(request, 'auth/account_activation_sent.html')


def activate(request, uidb64, token):

    logger.debug('try ACTIVATE')
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        logger.debug('try ACTIVATE USER: %s', user)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        logger.debug('%s ACTIVATED', user)
        login(request, user)
        return redirect('home')
    else:
        logger.debug('ACTIVATION INVALID')
        return render(request, 'auth/account_activation_invalid.html')
