# coding=utf8
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.template import RequestContext
from django.http import HttpResponseRedirect
from usernet.models import People,Tags,ActiveUsr
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from cmstodo.settings import WECHAT_TOKEN,APPID,APPSECRET
from django.utils.encoding import smart_str,smart_unicode
from django.http import HttpResponse

import xml.etree.ElementTree as ET
import time,json
import hashlib
import urllib2
import uuid

#internal
def getUserInfo(code):
    CODE = code

    url_open_accesstoken = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid='+APPID+'&secret='+APPSECRET+'&code='+CODE+'&grant_type=authorization_code'

    data = urllib2.urlopen(url_open_accesstoken)
    msg = json.load(data)
    ACCESS_TOKEN = msg['access_token']
    OPENID = msg['openid']

    url_open_userinfo = 'https://api.weixin.qq.com/sns/userinfo?access_token='+ACCESS_TOKEN+'&openid='+OPENID

    data1 = urllib2.urlopen(url_open_userinfo)
    msg1 =json.load(data1)
    return msg1

def search(request):
    if request.method == 'GET':
        CODE = request.GET.get('code')
        msg = getUserInfo(CODE)
        pid=msg['openid']
        try:
            a = ActiveUsr.objects.get(OpenId = pid)
        except ActiveUsr.DoesNotExist:
            messages.add_message(request,messages.WARNING,"请绑定账号")
            return render_to_response('wechat/message.html',{},
                              context_instance=RequestContext(request))
    p=[]
    p_l=[]
    pre_l=[]
    status=1
    if request.method == 'POST':
        q = request.POST.get("q")
        if q !='':
            p = People.objects.filter(Usr_Name__contains=q,isdel=0)
            tag = Tags.objects.filter(tag__contains = q)
            p_l = []
            for t in tag:
                x =  People.objects.filter(tags = t,isdel=0)
                p_l.append(x)
            pre_man = People.objects.filter(Usr_Name__contains=q,isdel=0)
            pre_l=[]
            for pre in pre_man:
                pre_x = People.objects.filter(Prev_Usr = pre,isdel=0)
                pre_l.append(pre_x)
        if p.count()<1 and p_l==[] and pre_l==[]:
            status=0

    return render_to_response('wechat/search.html',{'p':p ,'p_l':p_l,'pre_l':pre_l,'status':status},
                              context_instance=RequestContext(request))

def show(request):
    p_id = request.GET.get('id')
    t = People.objects.get(id=p_id)
    tags = t.tags.all()
    tag=[]
    for i in tags:
        tag.append(i.tag)
    return render_to_response('wechat/show.html',{'person':t ,'tags':tag},
                              context_instance=RequestContext(request))

def insert(request):
    if request.method == 'POST':
       # save new post
       Usr_Name = request.POST.get('name','')
       Usr_Mobile = request.POST.get('mobile','')
       Usr_Remark = request.POST.get('remark','')
       tags = request.POST.get('tags','')
       pre_id = request.POST.get('pre_id','')

       p_uuid = uuid.uuid1()
       p = People(Usr_Name = Usr_Name,Usr_Mobile = Usr_Mobile,Usr_Remark=Usr_Remark,active = 0,isdel = 0,uuid = p_uuid,)
       p.save()

       for tag in tags.replace(u'，',',').split(','):
           try:
               t = Tags.objects.get(tag = tag)
           except Tags.DoesNotExist:
               newtag = Tags(tag=tag)
               newtag.save()
               p.tags.add(newtag)
               p.save()
           else:
               p.tags.add(t)
               p.save()

       if pre_id != '':
           act = ActiveUsr.objects.get(OpenId = pre_id)
           try:
               pre = People.objects.filter(Usr_Name = act.Usr_Name,active = 1)
           except People.DoesNotExist:
               print "error"
           else:
               p.Prev_Usr=pre[0]
               p.Cluster_id = pre[0].Cluster_id
               p.save()

       messages.add_message(request,messages.SUCCESS,"添加成功")

       return render_to_response('wechat/message.html',{},
                              context_instance=RequestContext(request))
    CODE = request.GET.get('code')
    msg = getUserInfo(CODE)
    pid=msg['openid']
    try:
        a = ActiveUsr.objects.get(OpenId = pid)
    except ActiveUsr.DoesNotExist:
        messages.add_message(request,messages.WARNING,"请绑定账号")
        return render_to_response('wechat/message.html',{},
                              context_instance=RequestContext(request))
    return render_to_response('wechat/insert.html', {'pid':pid},
                              context_instance=RequestContext(request))

#*********wechat**************
def bind(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        openid = request.POST.get('openid')
        user = authenticate(username=username, password=password)
        if user is not None:
            try:
                a = ActiveUsr.objects.get(Usr_Name = username)
            except ActiveUsr.DoesNotExist:
                pass
            else:
                a.OpenId = openid
                a.save()
                messages.add_message(request,messages.SUCCESS,"绑定成功")
        else:
            messages.add_message(request,messages.WARNING,"绑定失败")
        return render_to_response('wechat/message.html',{},
                              context_instance=RequestContext(request))


def oauth2(request):
    CODE = request.GET.get('code')
    status_code = 1

    msg1 = getUserInfo(CODE)

    openid=msg1['openid']
    headimgurl=msg1['headimgurl']
    nickname=msg1['nickname']
    return render_to_response('wechat/bind.html',{'openid':openid,'headimgurl':headimgurl,'nickname':nickname,},
                              context_instance=RequestContext(request))





def checkSignature(request):
    signature=request.GET.get('signature',None)
    timestamp=request.GET.get('timestamp',None)
    nonce=request.GET.get('nonce',None)
    echostr=request.GET.get('echostr',None)
    token=WECHAT_TOKEN

    tmplist=[token,timestamp,nonce]
    tmplist.sort()
    tmpstr="%s%s%s"%tuple(tmplist)
    tmpstr=hashlib.sha1(tmpstr).hexdigest()
    if tmpstr==signature:
        return echostr
    else:
        return "check error"

#internal
def paraseMsgXml(rootElem):
    msg = {}
    if rootElem.tag == 'xml':
        for child in rootElem:
            msg[child.tag] = smart_str(child.text)
    return msg



def getReplyXml(msg,contant):
    extTpl = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content></xml>"
    extTpl=extTpl % (msg['FromUserName'],msg['ToUserName'],str(int(time.time())),'text',smart_str(contant))

    return extTpl

def getReplyXmlArc(msg):
    tplHeader = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[%s]]></MsgType><ArticleCount>%s</ArticleCount><Articles>"
    tplBody = "<item><Title><![CDATA[%s]]></Title><Description><![CDATA[%s]]></Description><PicUrl><![CDATA[%s]]></PicUrl><Url><![CDATA[%s]]></Url></item>"
    tplFooter ="</Articles></xml>"

    openid = msg['FromUserName']

    try:
        p = ActiveUsr.objects.get(OpenId = openid)
    except ActiveUsr.DoesNotExist:
        url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid='+APPID+'&redirect_uri=http://www.linsuo.com/wechat/oauth2&response_type=code&scope=snsapi_userinfo&state=1#wechat_redirect'
        tplHeader =tplHeader % (msg['FromUserName'],msg['ToUserName'],str(int(time.time())),'news', smart_str(1))
        body = ""
        task_url = url
        image_url = ""
        body += tplBody % (smart_str("绑定账号"),"",image_url,task_url)
        tpl = tplHeader+body+tplFooter
        return tpl
    else:
        data = msg['Content']
        if data == "input":
            tplHeader =tplHeader % (msg['FromUserName'],msg['ToUserName'],str(int(time.time())),'news', smart_str(1))
            body = ""
            url = "http://www.linsuo.com/wechat/insert/?pid="+msg['FromUserName']
            image_url = ""
            body += tplBody % (smart_str("点击添加用户信息"),"",image_url,url)
            tpl = tplHeader+body+tplFooter
            return tpl
        else:
            data = msg['Content']
            return getReplyXml(msg,data)
        if data =='bind':
            url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid='+APPID+'&redirect_uri=http://www.linsuo.com/wechat/oauth2&response_type=code&scope=snsapi_userinfo&state=1#wechat_redirect'
            tplHeader =tplHeader % (msg['FromUserName'],msg['ToUserName'],str(int(time.time())),'news', smart_str(1))
            body = ""
            task_url = url
            image_url = ""
            body += tplBody % (smart_str("绑定账号"),"",image_url,task_url)
            tpl = tplHeader+body+tplFooter
            return tpl



def responseMsg(request):
    rawStr = request.body
    msg = paraseMsgXml(ET.fromstring(rawStr))

    #TODO get Contant

    return getReplyXmlArc(msg)


@csrf_exempt
def index(request):
    if request.method == 'GET':
        response = HttpResponse(checkSignature(request),content_type="text/plain")
        return  response
    elif request.method == 'POST':
        response=HttpResponse(responseMsg(request),content_type="application/xml")
        return response
    else:
        return None
