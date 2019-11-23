
#-*- coding:utf-8-*-
# 这个文件名可以是任意名称

import re
from django.template import Library
from django.conf import settings
from collections import OrderedDict
from django.http import QueryDict
from django.urls import reverse
from rbac.service import urls

register = Library()    # 这个对象名必须叫register

#inclusion_tag('模板路径')
@register.inclusion_tag('rbac/static_menu.html')    #'rbac/static_menu.html' 是以luffy_permission\rbac\templates 作为根目录
def static_menu(request):
    '''
    创建一级菜单
    :return:
    '''
    menu_list = request.session[settings.MENU_SESSION_KEY]
    return {'menu_list': menu_list }


#inclusion_tag('模板路径')
@register.inclusion_tag('rbac/multi_menu.html')    #'rbac/multi_menu.html' 是以luffy_permission\rbac\templates 作为根目录
def multi_menu(request):
    '''
    创建二级菜单
    :return:
    '''
    menu_dict = request.session[settings.MENU_SESSION_KEY]

    """
    menu_dict形如：
{
    1:
     {
        'title': '信息管理',
        'icon': 'fa-camero-retro',
         'children': [
             {'title': '客户列表', 'url': '/customer/list/'}
         ]
     },
    2: {
        'title': '用户管理',
        'icon': 'fa-fire',
        'children': [
            {'title': '账单列表', 'url': '/payment/list/'}
        ]
    }
}
    """

    #sorted() 对字典的key进行排序, 1, 2, ...
    key_list = sorted(menu_dict)

    #创建一个空的有序字典
    ordered_dict = OrderedDict()
    for key in key_list:        #key值如1,2...
        val = menu_dict[key]    #val值如 上面示例1：{}， 2：{}
        val['class'] = 'hide'   #添加默认的样式类: class: 'hide'
        for per in val['children']:
            # regex = "^%s$" % (per['url'],)
            # if re.match(regex, request.path_info):
            if per['id'] == request.current_selected_permission:  #request.current_selected_permission是当前url对应的权限表id或者pid,本例中1，7
                per['class'] = 'active'     #如果当前访问的URL是per['url']， 则将per['url']设置为active
                val['class'] = ''            #同时父新的class：去掉hide样式
        ordered_dict[key] = val

    """
在字典中添加了key, 'class': 'hide' 隐藏标签， key: 'class': 'active' 使用当前标签处于活动状态
{
    1:
     {
        'title': '信息管理',
        'icon': 'fa-camero-retro',
        'class': '',
         'children': [
             {'title': '客户列表', 'url': '/customer/list/', 'class': 'active'}
         ]
     },
    2: {
        'title': '用户管理',
        'icon': 'fa-fire',
         'class': 'hide',
        'children': [
            {'title': '账单列表', 'url': '/payment/list/'}
        ]
    }
}
    """

    return {'menu_dict': ordered_dict}


@register.inclusion_tag('rbac/breadcrumb.html')
def breadcrumb(request):
    return {'record_list': request.breadcrumb}

@register.filter
def has_permission(request, name):
    '''
    判断是否有权限 , 这个filter函数最多有两个参数
    :param request:
    :param name:
    :return:   默认返回None
    '''
    if name in request.session[settings.PERMISSION_SESSION_KEY]:   #request.session[settings.PERMISSION_SESSION_KEY] 是权限字典
        return True

@register.simple_tag            #生成反向url
def memory_url(request, name, *args, **kwargs):
    '''
    生成带有原搜索条件的URL（替代了模板中的URL）
    :param request: 例如： <WSGIRequest: GET '/rbac/menu/list/?mid=3'>
    :param name:  例如："rbac:menu_add"
    :return:
    '''
    return urls.memory_url(request, name, *args, **kwargs)  #调用luffy_permission\rbac\service\urls.py中的memory_url()







