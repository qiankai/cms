# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import smart_str,smart_unicode
from cmstodo.settings import APPID,APPSECRET,WECHAT_TOKEN
from django.core.cache import cache

from models import APDevice, People, LoginTmp, LoginHistory, Device

import xml.etree.ElementTree as ET
import time
import hashlib
import random
import urllib,urllib2
import json
import uuid

def createMenu(request):
    menu = '''{"button":[{"type":"click","name": "绑定账户","key": "bind"},{"type":"view","name": "新增人脉","url": "https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxa1dffce607b94e53&redirect_uri=http://www.linsuo.com/wechat/insert&response_type=code&scope=snsapi_userinfo&state=1#wechat_redirect"},{"type":"view","name": "查询人脉","url": "https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxa1dffce607b94e53&redirect_uri=http://www.linsuo.com/wechat/search&response_type=code&scope=snsapi_userinfo&state=1#wechat_redirect"}]}'''


    access_token = getAccessToken(APPID,APPSECRET)
    QR_Create_Urls="https://api.weixin.qq.com/cgi-bin/menu/create?access_token="+ access_token
    print menu
    #req = urllib2.Request(QR_Create_Urls,menu.encode("utf-8"))


    response = urllib.urlopen(QR_Create_Urls,menu)
    return HttpResponse(response.read())



def ping(request):
    gw_id = request.GET.get('gw_id',"")
    sys_uptime = request.GET.get('sys_uptime',"")
    sys_memfree = request.GET.get('sys_memfree',"")
    sys_load= request.GET.get('sys_load',"")
    wifidog_uptime= request.GET.get('wifidog_uptime',"")
    gw_address = request.GET.get('gw_address',"")
    gw_port = request.GET.get('gw_port',"")

    try:
        device = Device.objects.get(Gw_Id = gw_id)
    except Device.DoesNotExist:
        device = Device(Gw_Id = gw_id,Gw_Address = gw_address, Gw_Port = gw_port)
        device.save()
    else:
        pass
    apd = APDevice(device = device, Sys_Uptime=sys_uptime,Sys_Memfree=sys_memfree, Sys_Load=sys_load, Wifidog_Uptime=wifidog_uptime)
    apd.save()
    return HttpResponse("Pong")

def auth(request):
    stage = request.GET.get('stage',"")
    ip = request.GET.get('ip',"")
    mac = request.GET.get('mac',"")
    token = request.GET.get('token',"")
    incoming = request.GET.get('incoming',"")
    outgoing = request.GET.get('outgoing',"")

    if stage == "login":
        try:
            p = People.objects.get(Token =token)
            code = "1"
            p.id = p.id
            p.Mac = mac
            p.IsLogin = 3
            p.save()
            p = People.objects.get(Token =token)
            l = LoginHistory()
            l.people = p
            l.Gw_Id = p.Gw_Id
            l.save()
        except People.DoesNotExist:
            code = "0"
    elif stage == "counters":
        try:
            p = People.objects.get(Token =token)
            code = "5"
        except People.DoesNotExist:
            code = "6"
    return HttpResponse("Auth: "+code)

def login(request):
    if request.method =="GET":
        gw_address = request.GET.get("gw_address","")
        gw_port = request.GET.get("gw_port","")
        gw_id = request.GET.get("gw_id","")

        template_name = "login.html"
        t = get_template(template_name)
        #html = t.render(RequestContext(request,{"imgsrc":src}))
        html = t.render(RequestContext(request, {}))
        return HttpResponse(html)


def portal(request):
    uui = uuid.uuid1()
    template_name = "portal.html"
    t = get_template(template_name)
    html = t.render(RequestContext(request,{"uui":uui}))
    return  HttpResponse(html)

#internal    
def getAccessToken(appid,secret):
    pre_url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid="
    url = pre_url + appid + "&secret=" + secret
    access_token = cache.get('access_token1')
    if access_token == None:
        data = urllib2.urlopen(url)
        msg = json.load(data)
        access_token = msg['access_token']
        cache.set('access_token1',access_token,7200)
    return access_token

#internal 
def getQRTicket(QR_Create_Urls, param):
    req = urllib2.Request(QR_Create_Urls)
    data = param
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    response = opener.open(req, data)
    msg = json.load(response)
    return msg['ticket']

def device_list(request):
    p = Device.objects.all()
    template_name = "list.html"
    t = get_template(template_name)
    html = t.render(RequestContext(request,{"device":p}))
    return HttpResponse(html)

def getqr(request):
    access_token = getAccessToken(APPID,SECRET)
    QR_Create_Urls = "https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=" + access_token
    scene_id = request.GET.get('id',"")
    #param = "{\"expire_seconds\": 1800,\"action_name\": \"QR_SCENE\",\"action_info\": {\"scene\": {\"scene_id\":" + scene_id + " }}}"
    param = "{\"action_name\": \"QR_LIMIT_SCENE\",\"action_info\": {\"scene\": {\"scene_id\":" + scene_id + " }}}"
    src = "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket="+getQRTicket(QR_Create_Urls,param)
    template_name = "qr.html"
    t = get_template(template_name)
    html = t.render(RequestContext(request,{"imgsrc":src}))
    return HttpResponse(html)

#internal
def getGwUrl(gw_Id):
    try:
        p = Device.objects.get(id = gw_Id)
    except Device.DoesNotExist:
        return None
    else:
        url = "http://"+p.Gw_Address+":"+p.Gw_Port+"/wifidog/auth?token="
        return url

def getNickName(msg):
    access_token = getAccessToken(APPID, SECRET)
    url_open = "https://api.weixin.qq.com/cgi-bin/user/info?access_token="+access_token+"&openid="+msg['FromUserName']+"&lang=zh_CN"
    data = urllib2.urlopen(url_open)
    msgs = json.load(data)
    return None
#*********wechat**************


#wechat check
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

    if msg['Event'] == 'subscribe':
        gw_id = msg['EventKey'][8:]
    elif msg['Event'] == 'SCAN':
        gw_id = msg['EventKey']
    elif msg['Event'] == 'CLICK':
        if msg['EventKey'] == 'world':
            try:
                act = People.objects.get(OpenId = msg['FromUserName'])
            except People.DoesNotExist:
                data = "online error"
                return getReplyXml(msg,data)
            else:
                d = Device.objects.get(Gw_Id = act.Gw_Id)
                url ="http://"+d.Gw_Address+":"+d.Gw_Port+"/wifidog/auth?token=" + act.Token
                data = '<a href="'+url+'">logon</a>'
                return getReplyXml(msg,data)
        else:
            data = msg['EventKey']
            return getReplyXml(msg,data)
    else:
        gw_id = None
        return getReplyXml(msg, "none")
    if gw_id is not None:
        try:
            p = People.objects.get(OpenId = msg['FromUserName'])
        except People.DoesNotExist:
            tok = uuid.uuid1()
            p = People(Token=tok, OpenId=msg['FromUserName'], IsLogin=2, Gw_Id=gw_id,)
            p.save()
        else:
            tok = p.Token
        url =getGwUrl(gw_id) + smart_str(tok)
        tplHeader =tplHeader % (msg['FromUserName'],msg['ToUserName'],str(int(time.time())),'news', smart_str(1))
        body = ""
        task_url = url
        image_url = ""
        body += tplBody % (smart_str(tok),"",image_url,task_url)
        tpl = tplHeader+body+tplFooter
        return tpl
    return getReplyXml(msg,"nerver present")

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








