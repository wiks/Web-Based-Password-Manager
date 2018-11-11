from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from mysite.core import views as core_views


urlpatterns = [
    url(r'^$', core_views.home, name='home'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(template_name='auth/logged_out.html'), name='logout'),
    url(r'^signup/$', core_views.signup, name='signup'),
    url(r'^account_activation_sent/$', core_views.account_activation_sent, name='account_activation_sent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        core_views.activate, name='activate'),
    url(r'^one/new/$', core_views.create_new, name='create_new'),
    url(r'^one/(?P<pk>\d+)/edit/$', core_views.one_edit, name='one_edit'),
    url(r'^one/(?P<pk>\d+)/delete/$', core_views.one_delete, name='one_delete'),
    url(r'^one/(?P<pk>\d+)/$', core_views.one_show, name='one_show'),
    url(r'^shared/(?P<shared_key>[0-9a-f-]+)/$', core_views.shared, name='shared'),
]
