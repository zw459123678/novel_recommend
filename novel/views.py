# coding:utf-8
import jieba
import time
from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.core import serializers
from crawler import novel
from .models import *
from django.db.models import *
import time, json
import datetime
import math

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import io, os, sys

from django.contrib.auth.hashers import make_password,check_password
from django.utils import timezone

from pyecharts.charts import WordCloud



# 首页
def home(request):
    if request.session.get('username'):
        login=request.session.get('username')
    else:
        login=None

    novels = get_novels(request, 1, 20)
    for novel in novels:
        # print(novel.keywords)
        novel.keywords = ', '.join(eval(novel.keywords))
    # print(novels)

    # 携带数据传输
    context={
        'novels': novels,
        'username': login # 登录名
    }
    return render(request, 'index.html',context=context)


# 搜索
def search(request):
    if request.session.get('username'):
        login=request.session.get('username')
    else:
        login=None
    if request.POST:
        get_type = request.POST['type']
        keyword = request.POST['key']
        page = request.POST['page']
        page_size = request.POST['page_size']

        if get_type == 'author':
            novels = get_novels_by_author(request, keyword, page, page_size)
            for novel in novels:
                # print(novel.keywords)
                novel.keywords = ', '.join(eval(novel.keywords))
            # print(novels)

            # 携带数据传输
            context={
                'novels': novels,
                'username': login # 登录名
            }
            return render(request, 'novel-search.html', context=context)
        else:
            novels = get_novels_by_name(request, keyword, page, page_size)
            for novel in novels:
                # print(novel.keywords)
                novel.keywords = ', '.join(eval(novel.keywords))
            # print(novels)

            # 携带数据传输
            context={
                'novels': novels,
                'username': login # 登录名
            }
            return render(request, 'novel-search.html',context=context)


# 按作者搜索
def search_author(request, author, page, page_size):
    if request.session.get('username'):
        login=request.session.get('username')
    else:
        login=None

    novels = get_novels_by_author(request, author, page, page_size)
    for novel in novels:
        # print(novel.keywords)
        novel.keywords = ', '.join(eval(novel.keywords))
    # print(novels)

    # 携带数据传输
    context={
        'novels': novels,
        'username': login # 登录名
    }
    return render(request, 'novel-search.html',context=context)

# 按小说名搜索
def search_name(request, name, page, page_size):
    if request.session.get('username'):
        login=request.session.get('username')
    else:
        login=None

    novels = get_novels_by_name(request, name, page, page_size)
    for novel in novels:
        # print(novel.keywords)
        novel.keywords = ', '.join(eval(novel.keywords))
    # print(novels)

    # 携带数据传输
    context={
        'novels': novels,
        'username': login # 登录名
    }
    return render(request, 'novel-search.html',context=context)
    
# 登录
def login(request):
    print('login')
    return render(request, 'login-page.html')


def login_inspect(request):
    global password, username
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

    user=AuthUser.objects.get(username=username)
    encode=user.password
    if check_password(password,encode):
        request.session['username']=username
        refresh=AuthUser.objects.get(username=username)
        refresh.last_login=timezone.now()
        refresh.save()
        request.session['username']=username
        return redirect(reverse('home:home'))
    else:
        context={
            'error': '用户名或密码错误',
        }
        return render(request,'login-page.html',context=context)

        
# 注册
def regist(request):
    return render(request, 'regist-page.html')


def regist_inspect(request):
    global email, phone, username, password
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
    
    again_password=request.POST['password_inspect']


    if password != again_password:
        context={
            "error": '两次密码输入不一致'
        }

        return render(request, 'regist-page.html', context=context)
        
    phone = 0
    password=make_password(password)
    for user in AuthUser.objects.all():
        if user.username == username:
            context = {
                'username': 0,
            }
            return render(request, 'regist-page.html', context=context)
    user_information=UserInformation(phone=phone,email=email)
    user_information.save()
    auth_user=AuthUser(username=username,password=password,user_id=user_information.id,is_superuser=0,is_staff=0,is_active=1,last_login=timezone.now(),date_joined=timezone.now())
    auth_user.save()
    return redirect(reverse('home:login'))

#登出
def sign_out(request):
    request.session.flush()
    return redirect(reverse('home:home'))


def change_information(request):
    if not request.session.get('username'):
        return redirect(reverse("home:login"))

    if request.POST:
        sex=request.POST['sex']

        print(sex)

        user=request.session.get('username')
        users=AuthUser.objects.get(username=user)
        users.save()
        information=UserInformation.objects.get(id=users.user_id)
        information.sex=sex
        information.save()

        return redirect(reverse("home:home"))

        

# 个人中心
def my_space(request):
    if request.session.get('username'):
        user=request.session.get('username')
        user_id=AuthUser.objects.get(username=user).user_id
        information=UserInformation.objects.get(id=user_id)
        context={
            "username":user,
            "information":information,
        }
        return render(request, 'templates/my_backstage/about_me.html', context=context)
    else:
        return redirect(reverse("home:login"))

# 个人中心
def tag(request):
    if request.session.get('username'):
        user=request.session.get('username')
        user=AuthUser.objects.get(username=user)
        tags=NovelRead.objects.filter(user=user)
        tags = list(set(tags))
        context={
            "username":user,
            "tags":tags,
        }
        return render(request, 'templates/my_backstage/tag.html', context=context)
    else:
        return redirect(reverse("home:login"))

def change(request):
    if not request.session.get('username'):
        return redirect(reverse("home:login"))
    if request.POST:
        password=request.POST['password']
        new_password=request.POST['new_password']
        again_password=request.POST['again_password']


        if new_password != again_password:
            context={
                "error": '两次密码输入不一致'
            }

            return render(request, 'templates/my_backstage/change_password.html',context=context)
            
        user=request.session.get('username')
        encode=AuthUser.objects.get(username=user).password
        if check_password(password=password,encoded=encode):
            password=make_password(password=new_password)
            users=AuthUser.objects.get(username=user)
            users.password=password
            users.save()
            return redirect(reverse("home:sign_out"))
        else:
            return redirect(reverse("home:change_password"))


def change_password(request):
    if request.session.get('username'):
        user=AuthUser.objects.get(username=request.session.get('username'))
        passowrd=user.password
        context={
            "password":passowrd,
        }
        return render(request, 'templates/my_backstage/change_password.html',context=context)
    else:
        return redirect(reverse("home:login"))

def last_month(now_time):
    last_month = now_time.month - 1
    last_year = now_time.year
    if last_month == 0:
        last_month = 12
        last_year -= 1
    month_time = datetime.datetime(month=last_month, year=last_year, day=now_time.day)
    return month_time

def get_novels(request, page, page_size):
    """
    获取小说列表
    """
    print('start get novel')
    if request.session.get('username'):
        login=request.session.get('username')
        user = AuthUser.objects.get(username=login)
        novel_reads = NovelRead.objects.filter(user=user)
        # 计算权重
        # 总关键词数量
        item_total = len(novel_reads)
        if item_total == 0:
            # 返回默认列表
            novel_list = []
            novels = NovelInfo.objects.values('id', 'name', 'author', 'keywords', 'read_counts').all()
            for novel in novels:
                novel_list.append(NovelInfo(id=novel['id'], name=novel['name'], author=novel['author'], keywords=novel['keywords'], read_counts=novel['read_counts']))
            #创建分页对象
            ptr=Paginator(novel_list, page_size)
            res = {}
            res['total']=ptr.count
            
            novels = ptr.page(page)
            res['list'] = novels
            # res['list'] = json.loads(serializers.serialize("json", novels))
            return novels
        # 关键词列表
        # 权重计算公式: 
        #       一个月前,统一0.01
        #       一个月内,1-(curr_time-read_time)/30天
        cnt = {}
        for novel_read in novel_reads:
            read_time = novel_read.read_time.timestamp()
            curr_time = time.time()
            diff_time = curr_time - read_time
            # print(f'{curr_time} - {read_time} = {diff_time}')
            
            # 30天对应2592000秒
            if diff_time > 2592000:
                cnt[novel_read.keyword]=cnt.get(novel_read.keyword,0) + 0.01
            else:
                cnt[novel_read.keyword]=cnt.get(novel_read.keyword,0) + (1 - diff_time / 2592000)
        
        items=list(cnt.items())   #将其返回为列表类型
        items.sort(key=lambda x:x[1],reverse=True)  #排序

        print(items)

        keys = []
        vals = []
        for item in items:
            keys.append(item[0])
            vals.append(item[1])
        print(keys)
        print(vals)

        # 权重处理
        max_val = max(vals)
        min_val = min(vals)
        ave = sum(vals) / len(vals)
        processed_val = []
        for val in vals:
            processed_val.append(((val - ave) / (max_val - min_val)) + 1)
        print('processed')
        print(processed_val)

        novel_list = []
        for key in keys:
            novels = NovelInfo.objects.values('id', 'name', 'author', 'keywords', 'read_counts').filter(keywords__icontains=key)[0:page_size]
            for novel in novels:
                novel_list.append(NovelInfo(id=novel['id'], name=novel['name'], author=novel['author'], keywords=novel['keywords'], read_counts=novel['read_counts']))
        # 去重
        print(novel_list)
        novel_list = list(set(novel_list))
        print(novel_list)

        # 计算相似度
        for novel in novel_list:
            keywords = eval(novel.keywords)
            # 特征向量,如果当前关键字列中有对应特征关键字,则赋值为1,否则赋值为0
            v = []
            for key in keys:
                if key in keywords:
                    v.append(1)
                else:
                    v.append(0)
            # 计算余弦相似度
            novel.cosine = cosine_similarity(v, vals) * 100

        # 按余弦相似度排序
        novel_list.sort(key=lambda x:x.cosine, reverse=True)
        return novel_list[0:page_size]

    else:
        # 未登录,返回随机列表
        novels = NovelInfo.objects.all().order_by('?')[:page_size]
        return novels

def norm(vector):
    return math.sqrt(sum(x * x for x in vector))    
 
def cosine_similarity(vec_a, vec_b):
    """
    余弦相似度函数
    """
    norm_a = norm(vec_a)
    norm_b = norm(vec_b)
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    return dot / (norm_a * norm_b)

def page_by_tag(request, tag, page, page_size):
    
    if request.session.get('username'):
        login=request.session.get('username')
    else:
        login=None

    res = get_novels_by_tag(request, tag, page, page_size)
    for novel in res['list']:
        # print(novel.keywords)
        novel.keywords = ', '.join(eval(novel.keywords))
    # 携带数据传输
    context={
        'novels': res['list'],
        'tag': tag,
        'username': login # 登录名
    }
    return render(request, 'novel-tag.html',context=context)

def get_novels_by_tag(request, tag, page, page_size):
    """
    获取小说列表，通过标签
    """
    print('start get novel')
    # 未登录,返回默认列表
    novel_list = NovelInfo.objects.filter(keywords__icontains=tag).order_by('-read_counts')
    ptr=Paginator(novel_list, page_size)
    res = {}
    res['total']=ptr.count
    
    novels = ptr.page(page)
    res['list'] = novels
    return res

def page_by_read_counts(request, page, page_size):
    
    if request.session.get('username'):
        login=request.session.get('username')
    else:
        login=None

    res = get_novels_by_read_counts(request, page, page_size)
    # 携带数据传输
    context={
        'novels': res['list'],
        'username': login # 登录名
    }
    return render(request, 'novel-hot.html',context=context)

def list_novels_by_read_counts(request, page, page_size):
    res = get_novels_by_read_counts(request, page, page_size)
    
    res['list'] = json.loads(serializers.serialize("json", res['list']))
    return JsonResponse(res)

def get_novels_by_read_counts(request, page, page_size):
    """
    获取小说列表，通过章阅读量
    """
    print('start get novel')
    # 未登录,返回默认列表
    novel_list = NovelInfo.objects.order_by('-read_counts')
    ptr=Paginator(novel_list, page_size)
    res = {}
    res['total']=ptr.count
    
    novels = ptr.page(page)
    res['list'] = novels
    return res

def page_by_author_read_counts(request, page, page_size):
    
    if request.session.get('username'):
        login=request.session.get('username')
    else:
        login=None

    res = get_novels_by_author_read_counts(request, page, page_size)
    # 携带数据传输
    context={
        'novels': res['list'],
        'username': login # 登录名
    }
    return render(request, 'novel-author-hot.html',context=context)

def page_by_collect(request, page, page_size):
    
    if request.session.get('username'):
        login=request.session.get('username')
    else:
        login=None

    res = get_novels_by_collect(request, login, page, page_size)
    novels = res['list']
    for novel in novels:
        # print(novel.keywords)
        novel.keywords = ', '.join(eval(novel.keywords))
    # 携带数据传输
    context={
        'novels': novels,
        'username': login # 登录名
    }
    return render(request, 'novel-collect.html',context=context)

def list_novels_by_author_read_counts(request, page, page_size):
    res = get_novels_by_author_read_counts(request, page, page_size)
    
    res['list'] = json.loads(serializers.serialize("json", res['list']))
    return JsonResponse(res)

def get_novels_by_collect(request, username, page, page_size):
    """
    获取小说列表，通过收藏
    """
    print('start get novel')
    user = AuthUser.objects.get(username=username)
    novel_collects = NovelCollect.objects.filter(user=user)
    ptr=Paginator(novel_collects, page_size)
    res = {}
    res['total']=ptr.count
    
    novels = ptr.page(page)
    novel_list = []
    for nc in novels:
        novel_list.append(nc.novel)
    res['list'] = novel_list
    return res


def get_novels_by_author_read_counts(request, page, page_size):
    """
    获取小说列表，通过作者总章阅读量
    """
    print('start get novel')
    # 未登录,返回默认列表
    novel_list = NovelInfo.objects.values('author').annotate(readSum=Sum('read_counts')).order_by('-readSum')
    ptr=Paginator(novel_list, page_size)
    res = {}
    res['total']=ptr.count
    
    novels = ptr.page(page)
    res['list'] = novels
    return res


def get_novels_by_author(request, author, page, page_size):
    """
    获取小说列表，通过作者名检索
    """
    print('start get novel')
    # 未登录,返回默认列表
    novel_list = NovelInfo.objects.filter(author__icontains=author)
    ptr=Paginator(novel_list, page_size)
    res = {}
    res['total']=ptr.count
    
    novels = ptr.page(page)
    res['list'] = novels
    return novels

def get_novels_by_name(request, name, page, page_size):
    """
    获取小说列表，通过小说名检索
    """
    print('start get novel')
    novel_list = NovelInfo.objects.filter(name__icontains=name)
    #创建分页对象
    ptr=Paginator(novel_list, page_size)
    res = {}
    res['total']=ptr.count
    
    novels = ptr.page(page)
    res['list'] = novels
    return novels



# 小说章节信息页
def novel_info(request, novel_id):
    if request.session.get('username'):
        login=request.session.get('username')
    else:
        login=None

    novel_info = NovelInfo.objects.get(id=novel_id)
    sections = eval(novel_info.chapterInfo)

    chapter_info = []
    for section in sections:
        item = json.loads(section)
        chapter_info.append(item)

    
    chapters = NovelContent.objects.filter(novelId_id=novel_id)

    contents = []
    for chapter in chapters:
        contents.append(chapter.content)
    content_str = ''.join(contents)

    datas = []
    # data = [('python', 23),('word',10),('cloud',5)]

    # 获取词语屏蔽列表
    word_forbids = WordForbid.objects.all()
    forbids = []
    for word in word_forbids:
        forbids.append(word.keyword)

    # 检查数据库中是否有该小说的词频
    novel_info = NovelInfo.objects.get(id=novel_id)
    try:
        novel_word_cloud = NovelWordCloud.objects.get(novelId=novel_id)
        datas_ori = json.loads(novel_word_cloud.words)
        for word in datas_ori:
            if word[0] not in forbids:
                datas.append(word)
    except Exception:
        start = time.perf_counter()
        words=jieba.cut(content_str, cut_all=True)
        cnt={}  #用来计数

        for word in words:
            if word not in forbids:
                cnt[word]=cnt.get(word,0)+1
        items=list(cnt.items())   #将其返回为列表类型
        items.sort(key=lambda x:x[1],reverse=True)  #排序

        for i in range(1000):   #输出我亲爱的二维列表
            name,ans=items[i]
            print("{0} 出现次数为：{1}".format(name,ans))
            datas.append((name, ans))
        end = time.perf_counter()      #结束时间
        print('程序运行时间：%.4f'%(end - start))
        obj = NovelWordCloud(novelId=novel_info, words = json.dumps(datas))
        obj.save()

    
    
    mywordcloud = WordCloud()
    mywordcloud.add('',datas[:100], shape='circle')
    
    
    hot_novels = get_novels_by_read_counts(request, 1, 10)
    
    hot_author = get_novels_by_author_read_counts(request, 1, 10)

    
    novel_info.keywords = ', '.join(eval(novel_info.keywords))

    img_title = novel_info.name.replace('!', '').replace('?', '').replace(',', '').replace('.', '')

    context={
        'hot_novels': hot_novels['list'],
        'hot_author': hot_author['list'],
        # 小说基本信息
        'novel': novel_info,
        'img_title': img_title,
        # 小说章节信息
        'chapters': chapter_info,
        # 登录名
        'username': login,
        # 'myechart':l3d.render_embed(),
        'myechart':mywordcloud.render_embed()
    }
    return render(request,'templates/novel-info.html',context=context)


# 查询当前用户是否收藏了本小说
def novel_is_collect(request, novel_id):
    if request.session.get('username'):
        login=request.session.get('username')
        

        novel_info = NovelInfo.objects.get(id=novel_id)
        user = AuthUser.objects.get(username=login)
        try:
            NovelCollect.objects.get(user=user, novel=novel_info)
            return JsonResponse({
                "code": 1
            })
        except NovelCollect.DoesNotExist:
            return JsonResponse({
                "code": 0
            })
    return JsonResponse({
        "code": 0
    })

# 收藏/取消收藏小说
def novel_change_collect(request, novel_id):
    if request.session.get('username'):
        login=request.session.get('username')
        

        novel_info = NovelInfo.objects.get(id=novel_id)
        user = AuthUser.objects.get(username=login)

        try:
            collect = NovelCollect.objects.get(user=user, novel=novel_info)
            collect.delete()
            return JsonResponse({
                "code": 0
            })
        except NovelCollect.DoesNotExist:
            collect = NovelCollect(user=user, novel=novel_info)
            collect.save()
            return JsonResponse({
                "code": 1
            })
    return JsonResponse({
        "code": 0
    })


# 小说详情页
def novel_detail(request, novel_id, chapter_no):
    if request.session.get('username'):
        login=request.session.get('username')
    else:
        login=None

    try:
        chapter = NovelContent.objects.get(novelId_id=novel_id, chapterNo=chapter_no)
    except NovelContent.DoesNotExist:
        chapter = NovelContent(novelId_id=novel_id, chapterNo=chapter_no)
    novel_info = NovelInfo.objects.get(id=novel_id)

    # 如果用户登录了,则记录观看的关键词
    if request.session.get('username'):
        login=request.session.get('username')
        user = AuthUser.objects.get(username=login)
        keywords = eval(novel_info.keywords)
        for keyword in keywords:
            obj = NovelRead(user=user, keyword=keyword)
            obj.save()
            
    # 记录本章阅读数
    chapter.read_counts += 1
    chapter.save()

    # 记录本小说阅读数
    novel_info.read_counts += 1
    novel_info.save()

    sections = eval(novel_info.chapterInfo)

    chapter_no = int(chapter_no)

    cur_section = json.loads(sections[chapter_no - 1])

    prev_chapter = chapter_no - 1
    next_chapter = chapter_no + 1
    if next_chapter == len(sections) + 1:
        next_chapter = 0

    chapter.content = chapter.content.replace('\n', '\n</p><p>\n')
    context={
        'novel_id': novel_id,
        'chapter': chapter,
        'title': cur_section['title'],
        'is_prev': prev_chapter > 0,
        'is_next': next_chapter > 0,
        'prev': prev_chapter,
        'next': next_chapter,
        'username': login
    }
    return render(request,'templates/novel-detail.html',context=context)


# 获取随机颜色
def get_random_color():
    R = random.randrange(255)
    G = random.randrange(255)
    B = random.randrange(255)
    return (R, G, B)
 
# 获取黑色
def get_random_color():
    R = random.randrange(0)
    G = random.randrange(255)
    B = random.randrange(255)
    return (R, G, B)
 
def get_novel_img(req, title):
    """
    生成封面图
    """

    img = Image.open(r'static/novel.jpg').convert('RGB')
    # # 定义画布背景颜色
    # bg_color = get_random_color()
    # # 画布大小
    # img_size = (130, 70)
    # # 定义画布
    # image = Image.new("RGB", img_size, bg_color)
    # 定义画笔
    draw = ImageDraw.Draw(img, "RGB")
    text_color = (255, 255, 255)
    # 将字符画到画布上
    title_len = len(title)
    font_size = round(400 / title_len)
    text_font = ImageFont.truetype(r"static/SourceHanSerifSC-Bold.otf", font_size)
    
    draw.text((50, 200 - font_size / 2), title, text_color, text_font)
    # 获得一个缓存区
    buf = io.BytesIO()
    # 将图片保存到缓存区
    img.save(buf, 'png')
    # 将缓存区的内容返回给前端 .getvalue 是把缓存区的所有数据读取
    return HttpResponse(buf.getvalue(), 'image/png')


    

# 删除喜好标签
def delete_tag(request, tag):
    if request.session.get('username'):
        login=request.session.get('username')
        user = AuthUser.objects.get(username=login)

        try:
            collect = NovelRead.objects.filter(user=user, keyword=tag)
            collect.delete()
            return JsonResponse({
                "code": 1
            })
        except NovelRead.DoesNotExist:
            return JsonResponse({
                "code": 0
            })
    return JsonResponse({
        "code": 0
    })
