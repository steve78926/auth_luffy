"""auth_luffy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, re_path, include
from app01.views import user, host
from app01.views import account

urlpatterns = [
    path('admin/', admin.site.urls),

    re_path(r'^login/$', account.login, name='login'),
    re_path(r'^logout/$', account.logout, name='logout'),

    re_path(r'^index/$', account.index, name='index'),


    re_path(r'^user/list/$', user.user_list, name='user_list'),
    re_path(r'^user/add/$', user.user_add, name='hostuser_add'),
    re_path(r'^user/edit/(?P<pk>\d+)/$', user.user_edit, name='user_edit'),
    re_path(r'^user/del/(?P<pk>\d+)/$', user.user_del, name='user_del'),
    re_path(r'^user/reset/password/(?P<pk>\d+)/$', user.user_reset_pwd, name='user_reset_pwd'),

    re_path(r'^host/list/$', host.host_list, name='host_list'),
    re_path(r'^host/add/$', host.host_add, name='host_add'),
    re_path(r'^host/edit/(?P<pk>\d+)/$', host.host_edit, name='host_edit'),
    re_path(r'^host/del/(?P<pk>\d+)/$', host.host_del, name='host_del'),

    re_path(r'^rbac/', include('rbac.urls', namespace='rbac')),


]
