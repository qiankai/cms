from django.conf.urls import patterns, include, url
from cmstodo import settings
from django.conf.urls.static import static
from usernet.views import login_view, logout_view, passwd_view

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cmstodo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^autherserver/',include('authserver.urls')),
    url(r'^usernet/',include('usernet.urls')),
    url(r'^wechat/',include('wechat.urls')),
    url(r'^accounts/login/$',  login_view),
    url(r'^accounts/logout/$', logout_view),
    url(r'^accounts/passwd/$', passwd_view),
)
