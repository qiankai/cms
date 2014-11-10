# coding=utf8
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.template import RequestContext
from django.http import HttpResponseRedirect
from models import People,Tags,ActiveUsr
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from cmstodo.settings import WECHAT_TOKEN
from django.utils.encoding import smart_str,smart_unicode
from django.http import HttpResponse

import xml.etree.ElementTree as ET
import time,json
import hashlib
import urllib2
import uuid

@login_required
def myloop(request):
    if request.method == 'GET':
        pname = request.user
        pre = People.objects.filter(Usr_Mobile = pname)
        p = People.objects.filter(Prev_Usr = pre[0],isdel=0)
        status =0
        if p.count()<1:
            status=1
        return render_to_response('usernet/my.html', {'status':status,'p':p,},
                              context_instance=RequestContext(request))

@login_required
def insert(request):
    status=None
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
       if request.user.is_superuser:
           status="ok"
           p.Cluster_id = 0
           p.save()
           return render_to_response('usernet/index.html', {'status':status,},
                              context_instance=RequestContext(request))
       if pre_id =='':
           pre_id = request.user
       if pre_id != '':
           try:
               pre = People.objects.filter(Usr_Mobile = pre_id,active = 1)
           except People.DoesNotExist:
               print "error"
           else:
               p.Prev_Usr=pre[0]
               p.Cluster_id = pre[0].Cluster_id
               p.save()
       status="ok"
    # Get all posts from DB
    return render_to_response('usernet/index.html', {'status':status,},
                              context_instance=RequestContext(request))
@login_required
def manage(request):
    if request.user.is_superuser:
        p=[]
        if request.method == "GET":
            return render_to_response('usernet/manage.html', {'p': p},
                              context_instance=RequestContext(request))
        if request.method == "POST":
            q = request.POST.get("q")
            if q !='':
                p = People.objects.filter(Usr_Name__contains=q)
                return render_to_response('usernet/manage.html', {'p':p},
                              context_instance=RequestContext(request))



    status = "你没有权限！"
    status_code = 0
    return render_to_response('usernet/message.html', {'status': status,'status_code':status_code,},
                              context_instance=RequestContext(request))

@login_required
def umang(request):
    pname = request.user
    print pname
    px = People.objects.get(Usr_Mobile = pname)
    a = ActiveUsr.objects.get(uuid = px.uuid)
    if a.is_manager == 1:
        p=[]
        if request.method == "GET":
            return render_to_response('usernet/umang.html', {'p': p,},
                              context_instance=RequestContext(request))
        if request.method == "POST":
            q = request.POST.get("q")
            if q !='':
                '''
                if a.Cluster_id =='0':
                    p = People.objects.filter(Usr_Name__contains=q,isdel = 0)
                else:
                    p = People.objects.filter(Usr_Name__contains=q,Cluster_id = a.Cluster_id,isdel = 0)
                return render_to_response('usernet/umang.html', {'p':p},
                              context_instance=RequestContext(request))
                              '''
                p = People.objects.filter(Usr_Name__contains=q,Cluster_id = a.Cluster_id,isdel = 0)
                return render_to_response('usernet/umang.html', {'p':p},
                              context_instance=RequestContext(request))

    status = "你没有权限！"
    status_code = 0
    return render_to_response('usernet/message.html', {'status': status,'status_code':status_code,},
                              context_instance=RequestContext(request))


@login_required
def active(request):
    if request.method == 'GET':
        p_id = request.GET.get('id','')
        p = People.objects.get(id = p_id)


        a = None
        try:
            a = ActiveUsr.objects.get(uuid = p.uuid)
        except ActiveUsr.DoesNotExist:
            messages.add_message(request,messages.WARNING,"HELLO WORLD INFO")
        else:
            messages.add_message(request,messages.SUCCESS,"HELLO WORLD")

        return render_to_response('usernet/active.html',{'post':p,'active':a,},
                              context_instance=RequestContext(request))


    if request.method == 'POST':
        p_name = request.POST.get('name')
        p_password = request.POST.get('password')
        p_id = request.POST.get('id')
        p_user_id = request.POST.get('userid')
        clustid = request.POST.get('clustid')

        is_manager = request.POST.get('is_manager')

        ism = 0
        if is_manager == '1':
            ism = 1


        p = People.objects.get(id = p_id)

        cid = p.Cluster_id

        if clustid == '1':
            cid = p.uuid
            print cid
        p.Cluster_id = cid
        p.save()


        if p_password !=None:
            user = User.objects.create_user(username=p_user_id,password=p_password,)
            user.save
            a = ActiveUsr(Usr_Name = p_name,uuid = p.uuid,Cluster_id = cid,is_manager = ism )
            a.save()
            p.active = 1
            p.save()
        else:
            a = ActiveUsr.objects.get(uuid = p.uuid)
            a.Cluster_id  = cid
            a.is_manager = ism
            a.save()


    status = "ok"
    status_code = 1

    return render_to_response('usernet/message.html',{'status':status,'status_code':status_code,},
                              context_instance=RequestContext(request))

@login_required
def uactive(request):
    if request.method == 'GET':
        p_id = request.GET.get('id','')
        p = People.objects.get(id = p_id)

        a = None
        try:
            a = ActiveUsr.objects.get(uuid = p.uuid)
        except ActiveUsr.DoesNotExist:
            messages.add_message(request,messages.WARNING,'no a')
        else:
            messages.add_message(request,messages.SUCCESS,a.is_manager)

        return render_to_response('usernet/uactive.html',{'post':p,'a':a,},
                              context_instance=RequestContext(request))


    if request.method == 'POST':
        p_name = request.POST.get('name')
        p_password = request.POST.get('password')
        p_id = request.POST.get('id')
        p_user_id = request.POST.get('userid')

        is_manager = request.POST.get('is_manager')

        ism = 0
        if is_manager == '1':
            ism = 1
        p = People.objects.get(id = p_id)

        if p_password !=None:
            user = User.objects.create_user(username=p_user_id,password=p_password,)
            user.save
            a = ActiveUsr(Usr_Name = p_name,uuid = p.uuid,Cluster_id=p.Cluster_id,is_manager = ism )
            a.save()
            p.active = 1
            p.save()
        else:
            a = ActiveUsr.objects.get(uuid = p.uuid)
            a.is_manager = ism
            a.save()


    status = "ok"
    status_code = 1

    return render_to_response('usernet/message.html',{'status':status,'status_code':status_code,},
                              context_instance=RequestContext(request))

@login_required
def search(request):
    p=[]
    p_l=[]
    pre_l=[]
    status=1
    if request.method == 'POST':
        q = request.POST.get("q")
        pname = request.user
        dd  = People.objects.get(Usr_Mobile = pname)
        print dd.Cluster_id
        if dd.Cluster_id != '0':
            if q !='':
                p = People.objects.filter(Usr_Name__contains=q,isdel=0,Cluster_id = dd.Cluster_id)
                tag = Tags.objects.filter(tag__contains = q)
                p_l = []
                for t in tag:
                    x =  People.objects.filter(tags = t,isdel=0,Cluster_id = dd.Cluster_id)
                    p_l.append(x)
                pre_man = People.objects.filter(Usr_Name__contains=q,isdel=0,Cluster_id = dd.Cluster_id)
                pre_l=[]
                for pre in pre_man:
                    pre_x = People.objects.filter(Prev_Usr = pre,isdel=0,Cluster_id = dd.Cluster_id)
                    pre_l.append(pre_x)
            if p.count()<1 and p_l==[] and pre_l==[]:
                status=0
            return render_to_response('usernet/search.html',{'p':p ,'p_l':p_l,'pre_l':pre_l,'status':status},
                              context_instance=RequestContext(request))
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

@login_required
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

        status = "Update " + p.Usr_Name  + " successfully!"
        status_code = 1
        return render_to_response('usernet/message.html',{'status':status,'status_code':status_code,},
                              context_instance=RequestContext(request))

@login_required
def delete(request):
    if request.method == 'GET':
        pid = request.GET.get('id')
        p = People.objects.get(id = pid)
        p.isdel = 1
        p.save()
        status = "Delete "+ p.Usr_Name  + " successfully!"
        status_code = 1
        return render_to_response('usernet/message.html',{'status':status,'status_code':status_code,},
                              context_instance=RequestContext(request))



def login_view(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            print request.user
            if request.user.is_superuser:
                return HttpResponseRedirect('../../usernet/manage/')
            return HttpResponseRedirect('../../usernet/my/')
        messages.add_message(request,messages.WARNING,'用户名或密码错误!')
    return render_to_response('usernet/login.html',{},
                              context_instance=RequestContext(request))

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('../../usernet/my/')
    #return render_to_response('usernet/login.html',{},
    #                          context_instance=RequestContext(request))

@login_required
def passwd_view(request):
    if request.method =='POST':
        username = request.POST.get('username',request.user)
        old_passwd = request.POST.get('oldpasswd')
        new_passwd = request.POST.get('newpasswd')

        user = User.objects.get(username = username)
        if user.check_password(old_passwd):
            user.set_password(new_passwd)
            user.save()
            status = "修改密码成功!"
            status_code = 1
        else:
            status = "密码修改失败，请重试！【旧密码错误】"
            status_code = 0
        return render_to_response('usernet/message.html',{'status':status,'status_code':status_code,},context_instance=RequestContext(request))
    return render_to_response('usernet/passwd.html',{},
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
                login(request, user)
                return HttpResponseRedirect('../../usernet/my/')

        else:
            status = "Bind " +  " failed!"
            status_code = 0
        return render_to_response('usernet/message.html',{'status':status,'status_code':status_code,},
                              context_instance=RequestContext(request))


def oauth2(request):
    CODE = request.GET.get('code')
    status_code = 1
    APPID = 'wx6ea75ebf77f14498'
    APPSECRET = 'b9649f59a540a25971a27d630493cfdc'

    url_open_accesstoken = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid='+APPID+'&secret='+APPSECRET+'&code='+CODE+'&grant_type=authorization_code'

    data = urllib2.urlopen(url_open_accesstoken)
    msg = json.load(data)
    ACCESS_TOKEN = msg['access_token']
    OPENID = msg['openid']

    url_open_userinfo = 'https://api.weixin.qq.com/sns/userinfo?access_token='+ACCESS_TOKEN+'&openid='+OPENID

    data1 = urllib2.urlopen(url_open_userinfo)
    msg1 =json.load(data1)

    openid=msg1['openid']
    headimgurl=msg1['headimgurl']
    nickname=msg1['nickname']
    return render_to_response('usernet/bind.html',{'openid':openid,'headimgurl':headimgurl,'nickname':nickname,},
                              context_instance=RequestContext(request))



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

    url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx6ea75ebf77f14498&redirect_uri=http://www.linsuo.com/usernet/oauth2&response_type=code&scope=snsapi_userinfo&state=1#wechat_redirect'

    tplHeader =tplHeader % (msg['FromUserName'],msg['ToUserName'],str(int(time.time())),'news', smart_str(1))
    body = ""
    task_url = url
    image_url = ""
    body += tplBody % (smart_str("OK OK OK"),"",image_url,task_url)
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
