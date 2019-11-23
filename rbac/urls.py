#-*- coding:utf-8 -*-

from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls import url
from rbac.views import role
from rbac.views import user
from rbac.views import menu

app_name = '[rbac]'         # 启动遇到报错 'Specifying a namespace in include() without providing an app_name '，添加此行
urlpatterns = [
    re_path(r'^role/list/$', role.role_list, name='role_list'),  #在html中引用时格式：名称空间：url别名，如rbac:role_list
    re_path(r'^role/add/$', role.role_add, name='role_add'),  #在html中引用时格式：名称空间：url别名，如rbac:role_add
    re_path(r'^role/edit/(?P<pk>\d+)/$', role.role_edit, name='role_edit'),   #在html中引用时格式：名称空间：url别名，如rbac:role_edit
    re_path(r'^role/del/(?P<pk>\d+)/$', role.role_del, name='role_del'),  #如rbac:role_del

    # re_path(r'^user/list/$', user.user_list, name='user_list'),
    # re_path(r'^user/add/$', user.user_add, name='user_add'),
    # re_path(r'^user/edit/(?P<pk>\d+)/$', user.user_edit, name='user_edit'),
    # re_path(r'^user/del/(?P<pk>\d+)/$', user.user_del, name='user_del'),
    # re_path(r'^user/reset/password/(?P<pk>\d+)/$', user.user_reset_pwd, name='user_reset_pwd'),

    re_path(r'^menu/list/$', menu.menu_list, name='menu_list'),
    re_path(r'^menu/add/$', menu.menu_add, name='menu_add'),
    re_path(r'^menu/edit/(?P<pk>\d+)/$', menu.menu_edit, name='menu_edit'),
    re_path(r'^menu/del/(?P<pk>\d+)/$', menu.menu_del, name='menu_del'),

    re_path(r'^second/menu/add/(?P<menu_id>\d+)/$', menu.second_menu_add, name='second_menu_add'),
    re_path(r'^second/menu/edit/(?P<pk>\d+)/$', menu.second_menu_edit, name='second_menu_edit'),
    re_path(r'^second/menu/del/(?P<pk>\d+)/$', menu.second_menu_del, name='second_menu_del'),

    re_path(r'^permission/add/(?P<second_menu_id>\d+)/$', menu.permission_add, name='permission_add'),
    re_path(r'^permission/edit/(?P<pk>\d+)/$', menu.permission_edit, name='permission_edit'),
    re_path(r'^permission/del/(?P<pk>\d+)/$', menu.permission_del, name='permission_del'),

    re_path(r'^multi/permissions/$', menu.multi_permissions, name='multi_permissions'),
    re_path(r'^multi/permissions/del/(?P<pk>\d+)/$', menu.multi_permissions_del, name='multi_permissions_del'),

    re_path(r'^distribute/permissions/$', menu.distribute_permissions, name='distribute_permissions'),


]

#访问 http://127.0.0.1:8000/rbac/role/list/# 报错如下：
#  Reverse for 'role_edit' with keyword arguments '{'pk': 1}' not found. 1 pattern(s) tried: ['rbac/role/edit/(?P<pk>\\+d)/$']
#原因：正则表达式写错： 错误写法：\+d   正确写法： \d+
 #re_path(r'^role/edit/(?P<pk>\+d)/$', role.role_edit, name='role_edit'),
