from django.conf.urls import patterns, include, url
from views import insert, manage, active, search, show,update,delete,myloop

urlpatterns=patterns('',
    #url(r'^$','authserver.views.index'),
    url(r'^insert/', insert,),
    url(r'^manage/', manage,),
    url(r'^active/',active,),
    url(r'^search/',search,),
    url(r'^show/',show,),
    url(r'^update/',update,),
    url(r'^delete/',delete,),
    url(r'^my/',myloop,),
    url(r'^$',search,),
)
