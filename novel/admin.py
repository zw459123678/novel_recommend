from django.contrib import admin

from .models import NovelChannel, NovelInfo, NovelContent, WordForbid, NovelCollect, NovelRead

class NovelChannelDisplay(admin.ModelAdmin):

    list_display = ['channelid', 'channelstr', 'crawled']

class NovelInfoDisplay(admin.ModelAdmin):

    list_display = ['name', 'author', 'keywords', 'crawled', 'read_counts']


class NovelContentDisplay(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['novelId', 'chapterNo', 'url', 'read_counts']
    
    def get_novelId(self, obj):
        return obj.novelId.name

class WordForbidDisplay(admin.ModelAdmin):

    list_display = ['keyword']

class NovelCollectDisplay(admin.ModelAdmin):

    list_display = ['user', 'novel']
    
    def get_user(self, obj):
        return obj.user.username
    
    def get_novel(self, obj):
        return obj.novel.name

class NovelReadDisplay(admin.ModelAdmin):

    list_display = ['user', 'keyword', 'read_time']
    
    def get_user(self, obj):
        return obj.user.username

# 自定义管理站点的名称和URL标题
admin.site.site_header = '小说推荐系统后台管理'
admin.site.site_title = '小说推荐系统'

# Register your models here.

admin.site.register(NovelChannel, NovelChannelDisplay)
admin.site.register(NovelInfo, NovelInfoDisplay)
admin.site.register(NovelContent, NovelContentDisplay)
admin.site.register(WordForbid, WordForbidDisplay)
admin.site.register(NovelCollect, NovelCollectDisplay)
admin.site.register(NovelRead, NovelReadDisplay)