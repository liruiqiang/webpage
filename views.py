
from django.shortcuts import render
from block.models import Block
from django.contrib.auth.models import User
from forms import UserForm
from django.core.mail import send_mail
import uuid
from activate.models import Activate
import datetime
from django.utils import timezone
from django.contrib.auth import authenticate,login,logout
from comment.models import Comment
from article.models import Article
import json
from django.http import HttpResponse
from message.models import Message
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import loader, RequestContext



def index(request):
    block_infos =Block.objects.filter(status=0).order_by('id')
    username = request.user
    if not request.user.is_authenticated():
        msg_cnt = 0
    else:
        msg_cnt = Message.objects.filter(owner=username, status=0).count()
    return render(request,"index.html",{"blocks":block_infos,"msg_cnt":msg_cnt})

def register(request):
    if request.method=="POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        all_user = User.objects.all()
        password_c = request.POST['password_c']
        a=False
        for user in all_user:
            if user.email == email:
                a=True
            else:
                a=False
        if a == True:
            return render(request,"register.html",{"a":a})
        else:
            user = User.objects.create_user(username=username,email=email,password=password)
            user.is_active = False
            user.save()
            new_code = str(uuid.uuid4()).replace("-","")
            activate_link = "http://%s/activate/%s" % (request.get_host(),new_code)
            activate_email = '''点击<a href="%s">这里</a>激活'''%activate_link
            send_mail(subject='激活邮件',
                    message='点击链接激活：%s'% activate_link,
                    from_email='19309649@qq.com',
                    recipient_list=[email],
                    fail_silently=False,
                    html_message=activate_email)
            expiretime = datetime.datetime.now() + datetime.timedelta(days=1)
            activate = Activate(username=username,code=new_code,expiretime=expiretime)
            activate.save()
            return render(request,"regsend.html")
    else:
        return render(request,"register.html")

def activate(request):
    full_path = request.get_full_path()
    activate_code = full_path[-32:]
    now_time = timezone.now()
    activate = Activate.objects.get(code=activate_code)
    if activate.expiretime < now_time:
        return render(request,'fail.html')
    else:
        user = User.objects.get(username=activate.username)
        user.is_active = True
        user.save()
        return render(request,'sucess.html')

def json_response(obj):
    txt = json.dumps(obj)
    return HttpResponse(txt)

def create_comment(request):
    to_comment_id = int(request.POST.get("to_comment_id",0))
    content = request.POST['content']
    article_id = request.POST['article_id']
    owner_name = request.POST['owner']
    user = User.objects.get(username=owner_name)
    article = Article.objects.get(id=article_id)
    page__num = request.POST.get("page_cnt")
    link = article_id+"?page_no="+page__num
    if to_comment_id !=0:
        to_comment = Comment.objects.get(id=to_comment_id)
        msg_content = "有人评论了您的评论'" + to_comment.content+"'"
    else:
        to_comment = None
        msg_content = "有人评论了您的文章'" + article.title+"'"
    if content == "":
        return json_response({"status":"err","msg":"评论不能为空"})
    elif not request.user.is_authenticated:
        return json_response({"status":"err1","msg":"匿名用户请登录"})
    else:
        comment = Comment.objects.create(owner=request.user,article=article,content=content,status="0",to_comment=to_comment)
        comment.save()
        message = Message.objects.create(owner = user,content=msg_content,link=link,status="0")
        message.save()
        return json_response({"status":"ok","msg":""})

@login_required
def message_list(request):
    username = request.user
    message = Message.objects.filter(owner = username,status=0).order_by("-id")
    msg_cnt = Message.objects.filter(owner = username,status=0).count()
    return render(request,"message.html",{"message":message,"msg_cnt":msg_cnt})


def message_open(request):
    id = int(request.GET.get('msg.id',0))
    message = Message.objects.get(id=id)
    message.status = -1
    redirect_to = "/article/detail/" + str(message.link)
    message.save()
    return HttpResponseRedirect(redirect_to)
