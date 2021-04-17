
"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'index/$', views.home, name='home'),  # 首页路由

    url(r'^login/$', views.login, name='login'),  # 登录路由
    url(r'^user_regist/$', views.regist, name='regist'),  # 用户注册路由

    # 退出登录
    url(r'^sign_out/$', views.sign_out, name='sign_out'),

    # 个人中心路由
    url(r'^my_home/$', views.my_space, name='my_home'),  # 个人中心首页
    url(r'^change_password/$', views.change_password, name='change_password'),  # 修改密码
    url(r'^change_information/$',views.change_information,name='change_information'), #修改信息
    url(r'^change/$',views.change,name='change'),  #修改密码请求
    url(r'^tag/$',views.tag,name='tag'),  # 标签页

    # 删除标签
    url(r'^novel/tag/(\w+)/$', views.delete_tag, name='delete_tag'),

    # 登录验证路由
    url(r'^login_inspect/$', views.login_inspect, name='login_inspect'),
    # 注册验证路由
    url(r'^regist_inspect/', views.regist_inspect, name='regist_inspect'),

    
    # 小说搜索路由
    url(r'^novel/search/$', views.search, name='search'),
    
    # 小说按作者搜索路由
    url(r'^novel/author/(\w+)/(\d+)/(\d+)/$', views.search_author, name='search_author'),
    
    # 小说按小说名搜索路由
    url(r'^novel/name/(\w+)/(\d+)/(\d+)/$', views.search_name, name='search_name'),
    # 小说信息路由
    url(r'^novel/(\d+)/$', views.novel_info, name='novel_info'),
    # 小说章节详情路由
    url(r'^novel/(\d+)/(\d+)/$', views.novel_detail, name='novel_detail'),

    # 小说按章阅读量排序路由（json）
    url(r'^novel/read_counts/(\d+)/(\d+)/$', views.list_novels_by_read_counts, name='list_novels_by_read_counts'),

    # 小说按章阅读量排序路由（page）
    url(r'^novel/read_count/(\d+)/(\d+)/$', views.page_by_read_counts, name='page_by_read_counts'),

    # 小说按作者总章阅读量排序路由（page）
    url(r'^novel/author_read_count/(\d+)/(\d+)/$', views.page_by_author_read_counts, name='page_by_author_read_counts'),

    # 小说按收藏检索路由（page）
    url(r'^novel/collect/(\d+)/(\d+)/$', views.page_by_collect, name='page_by_collect'),

    # 小说按标签分类路由（page）
    url(r'^novel/tag/(\w+)/(\d+)/(\d+)/$', views.page_by_tag, name='page_by_tag'),

    # 小说检查是否收藏路由（json）
    url(r'^novel/novel_is_collect/(\d+)/$', views.novel_is_collect, name='novel_is_collect'),

    # 小说切换收藏路由（json）
    url(r'^novel/novel_change_collect/(\d+)/$', views.novel_change_collect, name='novel_change_collect'),

    # 小说封面图路由（json）
    url(r'^novel/get_novel_img/(\w+)/$', views.get_novel_img, name='get_novel_img'),
]

