from django.conf.urls import patterns, include, url
from views import ping,auth,login,index,portal,createMenu,getqr,device_list

urlpatterns=patterns('',
    #url(r'^$','authserver.views.index'),
    url(r'^ping/',ping,),
    url(r'^auth/',auth,),
    url(r'^login/',login),
    url(r'^portal/',portal),
    url(r'^$',index),
    url(r'^createmenu/',createMenu),
    url(r'^getqr/',getqr),
    url(r'^list/',device_list)
)
