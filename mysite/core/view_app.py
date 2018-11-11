import uuid
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.utils.timezone import datetime, timedelta
from django.conf import settings
from mysite.core.forms import LoginPassForm
from mysite.core.models import LoginPass
from mysite.core.mypass import *
import logging
logger = logging.getLogger(__name__)


@login_required
def home(request):

    current_user = request.user
    logger.debug('home USER-ID: %s', current_user.id)
    if request.method == 'POST':
        if 'create' in request.POST.keys():
            return redirect('create_new')
        else:
            val = None
            key = None
            kkeys = ['edit', 'delete', 'show']  # , 'share'
            for k in kkeys:
                if k in request.POST.keys() and request.POST[k]:
                    val = request.POST[k]
                    key = k
            if key == 'edit':
                return redirect('one_edit', pk=val)
            elif key == 'delete':
                return redirect('one_delete', pk=val)
            elif key == 'show':
                return redirect('one_show', pk=val)
            else:
                return render(request, 'app/home.html', locals())
    fields = ('Your Page (Nick-)Name', 'page url', 'Your login')
    objs = LoginPass.objects.values_list('pk', 'pagename', 'url', 'login_name').filter(ownerid=current_user.id)
    data = []
    for obj in objs:
        di = obj
        data.append( di )
    owner_data = {
        'fields': fields,
        'data': data,
    }
    return render(request, 'app/home.html', locals())


@login_required
def create_new(request):

    current_user = request.user
    logger.debug('create-new USER-ID: %s', current_user.id)
    if request.method == 'POST':
        form = LoginPassForm(request.POST)
        if form.is_valid():
            cleaned_info = form.cleaned_data
            if not cleaned_info['url']:  #  not cleaned_info['url']
                return redirect('home')
            exist_id = LoginPass.objects.values_list('pk').filter(url=cleaned_info['url'],
                                                                  ownerid=current_user.id)
            if not exist_id:
                login_pass = form.save(commit=False)
                login_pass.ownerid = request.user
                login_pass.login_pass = encode(settings.MY_PASSWORD_CODEC, login_pass.login_pass)
                login_pass.save()
                return redirect('home')
            else:
                return redirect('one_show', exist_id[0][0])
        return redirect('home')
    form = LoginPassForm()
    return render(request, 'app/create_new.html', locals(), {'form': form})


@login_required
def one_edit(request, pk):

    logger.debug('one edit ')
    login_pass = get_object_or_404(LoginPass, pk=pk)
    if request.method == "POST":
        if 'create' in request.POST.keys():
            form = LoginPassForm(request.POST, instance=login_pass)
            if form.is_valid():
                login_pass = form.save(commit=False)
                login_pass.login_pass = encode(settings.MY_PASSWORD_CODEC, login_pass.login_pass)
                login_pass.ownerid = request.user
                login_pass.save()
                return redirect('home')
        else:
            return redirect('home')
    else:
        login_pass.login_pass = decode(settings.MY_PASSWORD_CODEC, login_pass.login_pass)
        form = LoginPassForm(instance=login_pass)
    return render(request, 'app/one_edit.html', {'form': form})


@login_required
def one_show(request, pk):

    logger.debug('one show ')
    shared_key = None
    valid_to = None
    login_pass = get_object_or_404(LoginPass, pk=pk)
    mcach = cache.get(pk)
    if mcach:
        shared_key = mcach[0]
        valid_to = mcach[1]
        logger.debug('CACHE EXIST valid to: %s', valid_to)
    else:
        logger.debug('CACHE ABSENT ')
    if request.method == "POST":
        if 'share' in request.POST.keys():
            timeout_sec = settings.SHARED_LINK_VALID_FOR_MINUTES * 60
            mcach = cache.get(pk)
            if not mcach:
                # shared_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(40))
                shared_key = uuid.uuid4()
                valid_to = (datetime.now() + timedelta(seconds=timeout_sec)).strftime("%Y-%m-%d %H:%M:%S")
                logger.debug('CACHE CREATED valid to: %s', valid_to)
                cache.set(pk, [shared_key, valid_to], timeout_sec)
                cache.set(shared_key, pk, timeout_sec)
            else:
                shared_key = mcach[0]
                valid_to = mcach[1]
        elif 'cancel' in request.POST.keys():
            return redirect('home')
    login_pass.login_pass = decode(settings.MY_PASSWORD_CODEC, login_pass.login_pass)
    form = LoginPassForm(instance=login_pass)
    return render(request, 'app/one_show.html', {'form': form,
                                                 'loginpassid': pk,
                                                 'key': shared_key,
                                                 'valid_to': valid_to,
                                                 'valid_mins': settings.SHARED_LINK_VALID_FOR_MINUTES,
                                                 })


@login_required
def one_delete(request, pk):

    logger.debug('one delete ')
    login_pass = get_object_or_404(LoginPass, pk=pk)
    if 'delete' in request.POST.keys():
        login_pass.delete()
        return redirect('home')
    elif 'cancel' in request.POST.keys():
        return redirect('home')
    login_pass.login_pass = decode(settings.MY_PASSWORD_CODEC, login_pass.login_pass)  # settings.MY_PASSWORD_CODEC = 'mypassword'
    form = LoginPassForm(instance=login_pass)
    return render(request, 'app/one_delete.html', {'form': form})


def shared(request, shared_key):

    pk = cache.get(shared_key)
    if pk:
        logger.info('CACHE used: ID: %s link-key: %s', pk, shared_key)
        login_pass = get_object_or_404(LoginPass, pk=pk)
        login_pass.login_pass = decode(settings.MY_PASSWORD_CODEC, login_pass.login_pass)
        form = LoginPassForm(instance=login_pass)
        return render(request, 'app/one_show.html', {'form': form,
                                                     'loginpassid': pk,
                                                     'hide_share_button': True,
                                                     })
    else:
        logger.warning('check non exicting CACHE: %s', shared_key)
    return render(request, 'app/shared_unkn.html')
