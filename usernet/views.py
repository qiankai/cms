# coding=utf8
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.template import RequestContext
from django.http import HttpResponseRedirect
from models import People,Tags,ActiveUsr
from django.views.decorators.csrf import csrf_exempt

import xml.etree.ElementTree as ET
import time
import hashlib


@login_required
def insert(request,wx_flag=None):
    status=None
    if request.method == 'POST':
       # save new post
       Usr_Name = request.POST.get('name','')
       Usr_Mobile = request.POST.get('mobile','')
       Usr_Remark = request.POST.get('remark','')
       tags = request.POST.get('tags','')
       pre_id = request.POST.get('pre_id','')
       p = People(Usr_Name = Usr_Name,Usr_Mobile = Usr_Mobile,Usr_Remark=Usr_Remark,active = 0)
       p.save()
       if pre_id =='':
           pre_id = request.user
       if pre_id != '':
           try:
               pre = People.objects.filter(Usr_Name = pre_id,active = 1)
           except People.DoesNotExist:
               print "error"
           else:
               p.Prev_Usr=pre[0]
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
       status="ok"
    # Get all posts from DB
    return render_to_response('usernet/index.html', {'status':status,'wx_flag':wx_flag},
                              context_instance=RequestContext(request))
@login_required
def manage(request):
    if request.user.is_superuser:
        p = People.objects.all()
        return render_to_response('usernet/active.html', {'Posts': p},
                              context_instance=RequestContext(request))
    status = "你没有权限！"
    return render_to_response('usernet/message.html', {'status': status},
                              context_instance=RequestContext(request))
@login_required
def active(request):
    p_id = request.GET.get('id','')
    p_name = request.GET.get('name','')
    p_openid = request.GET.get('openid','')
    p_password = request.GET.get('password','')

    a = ActiveUsr(Usr_Name = p_name, OpenId = p_openid)
    a.save()

    p = People.objects.get(id = p_id)
    p.active = 1
    p.save()

    user = User.objects.create_user(username=p_name,password=p_password,)
    user.save

    status = "ok"

    return render_to_response('usernet/message.html',{'status':status},
                              context_instance=RequestContext(request))

@login_required
def search(request):
    p=[]
    p_l=[]
    pre_l=[]
    status=1
    if request.method == 'POST':
        q = request.POST.get("q")
        if q !='':
            p = People.objects.filter(Usr_Name__contains=q)
            tag = Tags.objects.filter(tag__contains = q)
            p_l = []
            for t in tag:
                x =  People.objects.filter(tags = t)
                p_l.append(x)
            pre_man = People.objects.filter(Usr_Name__contains=q)
            pre_l=[]
            for pre in pre_man:
                pre_x = People.objects.filter(Prev_Usr = pre)
                pre_l.append(pre_x)
        if p.count()<1 and p_l==[] and pre_l==[]:
            status=0

    return render_to_response('usernet/search.html',{'p':p ,'p_l':p_l,'pre_l':pre_l,'status':status},
                              context_instance=RequestContext(request))
@login_required
def show(request):
    if request.user.is_authenticated():
        print request.user
    p_id = request.GET.get('id')
    t = People.objects.get(id=p_id)
    tags = t.tags.all()
    tag=[]
    for i in tags:
        tag.append(i.tag)

    return render_to_response('usernet/show.html',{'person':t ,'tags':tag},
                              context_instance=RequestContext(request))

def update(request):
    if request.method == 'GET':
        pid = request.GET.get('id')
        p = People.objects.get(id = pid)
        tags = p.tags.all()
        tag=[]
        ta = ''
        for i in tags:
            tag.append(i.tag)
            ta = ta+ i.tag+','
        return render_to_response('usernet/update.html',{'person':p ,'tags':tag,'ta':ta,},
                              context_instance=RequestContext(request))
    if request.method == 'POST':
        pid = request.POST.get('id')
        Usr_Name = request.POST.get('name','')
        Usr_Mobile = request.POST.get('mobile','')
        Usr_Remark = request.POST.get('remark','')
        tags = request.POST.get('tags','')
        pre_id = request.POST.get('pre_id','')


        p = People.objects.get(id = pid)
        p.Usr_Name =Usr_Name
        p.Usr_Mobile = Usr_Mobile
        p.Usr_Remark = Usr_Remark
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

        status = "update ok"
        return render_to_response('usernet/message.html',{'status':status},
                              context_instance=RequestContext(request))


def login_view(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            print request.user
            return HttpResponseRedirect('../../usernet/search/')
    return render_to_response('usernet/login.html',{},
                              context_instance=RequestContext(request))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('../../usernet/search/')
    #return render_to_response('usernet/login.html',{},
    #                          context_instance=RequestContext(request))

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

    openid = msg['FromUserName']

    try:
        t = ActiveUsr.objects.get(OpenId = openid)
    except ActiveUsr.DoesNotExist:
        return getReplyXml(msg,openid)
    else:
        if msg['Content'] == '输入':
            url = '<a href="http://www.linsuo.com/usernet/wx_insert/">输入链接</a>'
            return getReplyXml(msg,url)



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
