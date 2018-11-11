from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# from django import forms


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class LoginPass(models.Model):
    ownerid = models.ForeignKey(User, on_delete=models.CASCADE)
    pagename = models.CharField(max_length=255)
    url = models.URLField()
    login_name = models.CharField(max_length=100)
    login_pass = models.CharField(max_length=100)


# class LoginPassForm(forms.Form):
#
#     def clean(self):
#
#         cleaned_data = super().clean()
#
#         print(cleaned_data)

