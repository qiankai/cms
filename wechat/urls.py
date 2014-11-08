from django.conf.urls import patterns, include, url
from views import oauth2,bind,insert,index,search,show

urlpatterns=patterns('',
    #url(r'^$','authserver.views.index'),
    url(r'^$',index,),
    url(r'^oauth2/',oauth2,),
    url(r'^bind/',bind,),
    url(r'^insert/',insert,),
    url(r'^search/',search,),
    url(r'^show/',show,),
)
