from django.db import models
from django.utils.translation import ugettext as _
# from ckeditor.fields import RichTextField
import os
import datetime
import random
import string

from django.utils import timezone
# Create your models here.


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    is_staff = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    date_joined = models.DateTimeField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auth_user'
    
    def __str__(self):
        return self.username


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)



class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class UserInformation(models.Model):
    
    sex_choices = (
        ('男', '男'),
        ('女', '女'),
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.BigIntegerField(blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    qq = models.CharField(max_length=255, blank=True, null=True)
    datail = models.TextField(blank=True, null=True)
    img = models.CharField(max_length=255, blank=True, null=True)
    sex = models.CharField(choices=sex_choices, max_length=20, blank=False, null=False, default=0, verbose_name=_("性别"))

    class Meta:
        verbose_name_plural = '用户信息表'



# 小说频道表
class NovelChannel(models.Model):
    channel_choices = (
        ('17', '完本半价'),
    )
    channelid = models.CharField(choices=channel_choices, max_length=20, blank=False, null=False, default=0, verbose_name=_("频道类型"))
    channelstr = models.CharField(max_length=255, blank=False, null=False, default=0, verbose_name=_("频道代码"))
    crawled = models.BooleanField(default=False, verbose_name=_("是否已经爬取"))
    
    class Meta:
        verbose_name_plural = '小说频道表'

# 小说信息表
class NovelInfo(models.Model):
    name = models.CharField(max_length=200, blank=False, null=False, verbose_name=_("小说名"))
    author = models.CharField(max_length=200, blank=False, null=False, verbose_name=_("作者"))
    keywords = models.CharField(max_length=1000, blank=False, null=False, default='', verbose_name=_("关键词"))
    chapterInfo = models.TextField(blank=False, null=False, verbose_name=_("章节信息"))
    crawled = models.BooleanField(default=False, verbose_name=_("是否已经爬取"))
    read_counts = models.IntegerField(blank=False, null=False, default=0, verbose_name=_("阅读次数"))
    # 相似度,非数据库字段
    cosine = 0
    class Meta:
        verbose_name_plural = '小说信息表'
        
    def __str__(self):
        return self.name

    def __eq__(self, other):
        if other and self.name == other.name:
            return True
        return False

    def __hash__(self):
        return hash(self.name)

# 小说内容表
class NovelContent(models.Model):
    novelId = models.ForeignKey(NovelInfo, on_delete=models.CASCADE, verbose_name=_("小说"))
    chapterNo = models.IntegerField(blank=False, null=False, verbose_name=_("小说章节序号"))
    title = models.TextField(blank=False, null=False, verbose_name=_("章节名"))
    url = models.CharField(max_length=255, blank=False, null=False, verbose_name=_("本章链接"))
    content = models.TextField(blank=False, null=False, verbose_name=_("小说内容"))
    read_counts = models.IntegerField(blank=False, null=False, default=0, verbose_name=_("阅读次数"))
    
    class Meta:
        verbose_name_plural = '小说内容表'

    def __str__(self):
        return f'{self.novelId.name} - {self.chapterNo} - {self.title}'

# 小说词频表
class NovelWordCloud(models.Model):
    novelId = models.ForeignKey(NovelInfo, on_delete=models.CASCADE, verbose_name=_("小说"))
    words = models.TextField(blank=False, null=False, verbose_name=_("小说词频"))
    
    class Meta:
        verbose_name_plural = '小说词频表'

# 小说阅读表
class NovelRead(models.Model):
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE, verbose_name=_("用户id"))
    keyword = models.CharField(max_length=1000, blank=False, null=False, default='', verbose_name=_("关键词"))
    read_time = models.DateTimeField(auto_now_add = True, verbose_name=_("阅读时间"))
    
    class Meta:
        verbose_name_plural = '小说阅读表'

    def __eq__(self,other):
        if self.keyword == other.keyword:
            return True
        return False

    def __hash__(self):
        return hash(self.keyword)


# 小说收藏表
class NovelCollect(models.Model):
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE, verbose_name=_("用户"))
    novel = models.ForeignKey(NovelInfo, on_delete=models.CASCADE, verbose_name=_("小说"))
    collect_time = models.DateTimeField(auto_now_add = True, verbose_name=_("收藏时间"))
    
    class Meta:
        verbose_name_plural = '小说收藏表'

    def __str__(self):
        return f'{self.user.username} - {self.novel.name}'

# 词语屏蔽表
class WordForbid(models.Model):
    keyword = models.CharField(max_length=1000, blank=False, null=False, default='', verbose_name=_("关键词"))
    
    class Meta:
        verbose_name_plural = '词语屏蔽表'

    def __str__(self):
        return self.keyword