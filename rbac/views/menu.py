#-*- coding:utf-8 -*-

'''
菜单管理
'''

from collections import OrderedDict
from django.shortcuts import render, redirect,reverse, HttpResponse
#from django.urls import reverse
from django.forms import formset_factory
from django.conf import settings
from django.utils.module_loading import import_string
from rbac import models
from rbac.forms.menu import MenuModelForm, SecondMenuModelForm,PermissionModelForm,MultiAddPermissionForm,MultiEditPermissionForm
from rbac.service.urls import memory_reverse



def menu_list(request):
    '''
    菜单和权限列表
    :param request:
    :return:
    '''
    menus = models.Menu.objects.all()
    menu_id = request.GET.get('mid')        #用户选择的一级菜单
    second_menu_id = request.GET.get('sid')        #用户选择的二级菜单

    #如果request.GET.get 中的menu_id 没有在数据库中,不显示”新建“按钮
    menu_exists = models.Menu.objects.filter(id=menu_id).exists()
    if not menu_exists:
         menu_id = None

    if menu_id:
         second_menus = models.Permission.objects.filter(menu_id=menu_id)
    else:
         second_menus = []

    ################################### 权限分配 ########################################
    second_menu_exists = models.Permission.objects.filter(id=second_menu_id).exists()

    if not second_menu_exists:
        second_menu_id = None

    if second_menu_id:     #如果二级菜单的id存在，获取当前二级菜单下的所有权限
        permissions = models.Permission.objects.filter(pid_id=second_menu_id)   #根据permission表中的pid_id=second_menu_id ，获取当前菜单下的所有权限
    else:
        permissions = []

    return render(request, 'rbac/menu_list.html',
                  {
                      'menus': menus,
                      'second_menus': second_menus,
                      'permissions': permissions,
                      'menu_id': menu_id,
                      'second_menu_id': second_menu_id,
                  }
            )


def menu_add(request):
    '''
    添加一级菜单
    :param request:
    :return:
    '''

    if request.method == 'GET':
        form = MenuModelForm()
        print('form:', form)
        return render(request, 'rbac/change.html', {'form': form})

    form = MenuModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(memory_reverse(request, 'rbac:menu_list'))   #重定向到带原始参数的URL(通过URL参数反向解析得到带参的URL)

    return render(request, 'rbac/change.html', {'form': form})   #防止表单没有输入直接点保存报错


def menu_edit(request, pk):
    '''
    编辑一级菜单
    :param request:
    :return:
    '''

    obj = models.Menu.objects.filter(id=pk).first()
    if not obj:
        return HttpResponse('菜单不存在')

    if request.method == 'GET':
        form = MenuModelForm(instance=obj)   #因为有instance=obj ，所以表单中有默认值
        return render(request, 'rbac/change.html', {'form': form})   #访问http://127.0.0.1:8000/rbac/role/edit/1/， 表单中有默认值

    form = MenuModelForm(instance=obj, data=request.POST)  #data=request.POST 表示提交过来的数据
    if form.is_valid():
        form.save()
        return redirect(memory_reverse(request, 'rbac:menu_list'))  #重定向到带原始参数的URL(通过URL参数反向解析得到带参的URL)

    return render(request, 'rbac/change.html', {'form': form })    #错误信息的展示 防止表单没有输入直接点保存报错
    ######## 上一行代码不能是redirect(), 必须是render()  ############


def menu_del(request, pk):
    '''
    删除一级菜单
    :param request:
    :return:
    '''

    url = memory_reverse(request, 'rbac:menu_list') #重定向到带原始参数的URL(通过URL参数反向解析得到带参的URL)
    if request.method == 'GET':
        return render(request, 'rbac/delete.html',{'cancle':url})   #cancle 作为变量传给前端delete.html页面

    # 当点击delete.html页面的确认按钮时,浏览器向服务器发送了一个post请求，url:http://127.0.0.1:8000/rbac/role/del/7/
    models.Menu.objects.filter(id=pk).delete()
    return redirect(url)

def second_menu_add(request, menu_id):
    '''
    添加二级菜单
    :param request:
    :param menu_id: 已选择的一级菜单ID(用于设置默认值)
    :return:
    '''

    menu_object = models.Menu.objects.filter(id=menu_id).first()    #menu_object 直接打印是 menu。title 如 信息管理
    if request.method == 'GET':
        form = SecondMenuModelForm(initial={'menu': menu_object})    #initial= {} 初始化赋值, menu_object, 如 信息管理
        print("form:",form)
        return render(request, 'rbac/change.html', {'form': form})

    form = SecondMenuModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(memory_reverse(request, 'rbac:menu_list'))   #重定向到带原始参数的URL(通过URL参数反向解析得到带参的URL)

    return render(request, 'rbac/change.html', {'form': form})   #防止表单没有输入直接点保存报错


def second_menu_edit(request, pk):
    '''
    编辑二级菜单
    :param request:
    :param pk: 当前要编辑的二级菜单
    :return:
    '''

    permission_object = models.Permission.objects.filter(id=pk).first()
    if request.method == 'GET':
        form = SecondMenuModelForm(instance=permission_object)    # 初始化赋值
        return render(request, 'rbac/change.html', {'form': form})

    form = SecondMenuModelForm(data=request.POST, instance=permission_object)
    if form.is_valid():
        form.save()
        return redirect(memory_reverse(request, 'rbac:menu_list'))   #重定向到带原始参数的URL(通过URL参数反向解析得到带参的URL)

    return render(request, 'rbac/change.html', {'form': form})   #防止表单没有输入直接点保存报错


def second_menu_del(request, pk):
    '''
    删除二级菜单
    :param request:
    :return:
    '''

    url = memory_reverse(request, 'rbac:menu_list') #重定向到带原始参数的URL(通过URL参数反向解析得到带参的URL)
    if request.method == 'GET':
        return render(request, 'rbac/delete.html',{'cancle':url})   #cancle 作为变量传给前端delete.html页面

    # 当点击delete.html页面的确认按钮时,浏览器向服务器发送了一个post请求，http://127.0.0.1:8000/rbac/second/menu/del/14/?_filter=mid%3D13
    models.Permission.objects.filter(id=pk).delete()
    return redirect(url)

def permission_add(request, second_menu_id):
    '''
    添加权限
    :param request:
    :param second_menu_id:
    :return:
    '''

    if request.method == 'GET':
        form = PermissionModelForm()    #initial= {} 初始化赋值, menu_object, 如 信息管理
        return render(request, 'rbac/change.html', {'form': form})

    form = PermissionModelForm(data=request.POST)
    if form.is_valid():
        second_menu_object = models.Permission.objects.filter(id=second_menu_id).first()
        if not second_menu_object:
            return HttpResponse('二级菜单不存在，请重新选择:')

        #form.instance中包含用户提交的所有值, instance
        # instance = models.Permission(title='', name='', url='', pid=second_menu_object)
        # instance.pid = second_menu_object 相当于给instance 增加 pid=second_menu_object
        # instance.save()

        form.instance.pid = second_menu_object
        form.save()
        return redirect(memory_reverse(request, 'rbac:menu_list'))   #重定向到带原始参数的URL(通过URL参数反向解析得到带参的URL)

    return render(request, 'rbac/change.html', {'form': form})   #防止表单没有输入直接点保存报错

def permission_edit(request, pk):
    '''
    编辑二级菜单
    :param request:
    :param pk: 当前要编辑的二级菜单
    :return:
    '''

    permission_object = models.Permission.objects.filter(id=pk).first()
    if request.method == 'GET':
        form = PermissionModelForm(instance=permission_object)    # 初始化赋值
        return render(request, 'rbac/change.html', {'form': form})

    form = PermissionModelForm(data=request.POST, instance=permission_object)
    if form.is_valid():
        form.save()
        return redirect(memory_reverse(request, 'rbac:menu_list'))   #重定向到带原始参数的URL(通过URL参数反向解析得到带参的URL)

    return render(request, 'rbac/change.html', {'form': form})   #防止表单没有输入直接点保存报错


def permission_del(request, pk):
    '''
    删除二级菜单
    :param request:
    :return:
    '''

    url = memory_reverse(request, 'rbac:menu_list') #重定向到带原始参数的URL(通过URL参数反向解析得到带参的URL)
    if request.method == 'GET':
        return render(request, 'rbac/delete.html',{'cancle':url})   #cancle 作为变量传给前端delete.html页面

    # 当点击delete.html页面的确认按钮时,浏览器向服务器发送了一个post请求，http://127.0.0.1:8000/rbac/second/menu/del/14/?_filter=mid%3D13
    models.Permission.objects.filter(id=pk).delete()
    return redirect(url)


import re

from django.conf import settings
from django.utils.module_loading import import_string    #根据字符串形式导入模块，这句话不太明白
#from django.urls import RegexURLResolver, RegexURLPattern     #此处与视频中一样
from django.urls.resolvers import URLPattern, URLResolver       #此处与视频中不一样


def check_url_exclude(url):
    '''
    排除特定的URL
    :param url:
    :return:
    '''
    # exclude_url = [
    #     '/admin/.*',
    #     '/login/.*',
    # ]
    #exclude_url 这个列表放在settings.py中了
    for regex in settings.AUTO_DISCOVER_EXCLUDE:
        if re.match(regex, url):
            return True

def recursion_urls(pre_namespace, pre_url, urlpatterns, url_ordered_dict):
    '''
    递归的去获取URL(前提是url必须有name别名)
    :param pre_namespace: namespace的前缀， 以后用于拼接name
    :param pre_url: url前缀，以后用于拼接URL
    :param urlpatterns: 路由关系列表
    :param url_ordered_dict: 用于保存递归中获取的所有的路由
    :return:
    '''
    for item in urlpatterns:
        if isinstance(item, URLPattern):   #非路由分发，将路由添加到url_ordered_dict
            if not item.name:  #如果当前URL没有别名name,则跳过当前URL，向后处理
                continue

            if pre_namespace:
                name = "%s:%s" % (pre_namespace, item.name)
            else:
                name = item.name
            #url = pre_url + item._regex  注意：item._regex 表示当前URL,可能不存在
            url = pre_url + str(item.pattern)    # /^rbac/^user/edit/(?P<pk>\d+)/$， str(item.pattern)表示当前URL的字符串形式, 本案例中 /^rbac/  是pre_url

            #运行报错：'URLResolver' object has no attribute 'regex'
            url = url.replace('^', '').replace('$', '')   #得到 /rbac/user/edit/(?P<pk>\d+)/
            if check_url_exclude(url):
                continue

            url_ordered_dict[name] = {'name': name, 'url': url}

        elif isinstance(item, URLResolver):   #路由分发，递归操作
            if pre_namespace:
                if item.namespace:      #namespace 也可能有多级
                    namespace = "%s:%s" % (pre_namespace, item.namespace)   #包括父级namespace, 和当前级namespace
                else:
                    namespace = pre_namespace   #视频中这句好像打错了，namespace = item.namespace, 应该namespace = pre_namespace
            else:
                if item.namespace:
                    namespace = item.namespace
                else:
                    namespace = None
            #recursion_urls(namespace, pre_url + item.regex.pattern, item.url_patterns, url_ordered_dict)  #这行是原始视频代码：item.regex.pattern 表示URL前缀 + 当前URL
            recursion_urls(namespace, pre_url + str(item.pattern), item.url_patterns, url_ordered_dict)  #pre_url + item.regex.pattern 表示URL前缀 + 当前URL

def get_all_url_dict():
    '''
    获取项目中所有的URL
    :return:
    '''
    url_ordered_dict = OrderedDict()
    '''
    {
       'rbac: menu_list': { name: 'rbac:menu_list', url: 'xxx/xxx/menu_list'}
    }
    '''
    #在settings.py中 ROOT_URLCONF = 'luffy_permission.urls'
    md = import_string(settings.ROOT_URLCONF)   #from luff... import urls  根据字符串形式导入一个模块
    #print("md:", md)   #md: <module 'luffy_permission.urls' from 'D:\\lufei_xue_cheng\\module7\\crm\\luffy_permission\\luffy_permission\\urls.py'>
    #print("md.urlpatterns:", md.urlpatterns)  #返回如下 4行内容 ,注意：URLResolver 与 URLPattern
    # md.urlpatterns: [
    # <URLResolver <URLPattern list> (admin:admin) 'admin/'>,
    # <URLResolver <module 'rbac.urls' from 'D:\\lufei_xue_cheng\\module7\\crm\\luffy_permission\\rbac\\urls.py'> ([rbac]:rbac) '^rbac/'>,
    # <URLResolver <module 'web.urls' from 'D:\\lufei_xue_cheng\\module7\\crm\\luffy_permission\\web\\urls.py'> (None:None) '^'>]

    #None 表示根路由没有分发，namespace没有前缀。 '/', 表示在根路由前面 加/
    recursion_urls(None,'/', md.urlpatterns, url_ordered_dict)   #递归去获取所有的路由
    return url_ordered_dict


def multi_permissions(request):
    '''
    批量操作权限
    :param request:
    :return:
    '''

    post_type = request.GET.get('type')
    generate_formset_class = formset_factory(MultiAddPermissionForm, extra=0)
    update_formset_class = formset_factory(MultiEditPermissionForm, extra=0)

    generate_formset = None

    if request.method == 'POST' and post_type == 'generate':
        # pass    #批量添加
        formset = generate_formset_class(data=request.POST)
        if formset.is_valid():
            object_list = []
            post_row_list = formset.cleaned_data
            has_error = False
            for i in range(0, formset.total_form_count()):
                row_dict = post_row_list[i]  # row_dict 表示每一行的数据
                try:
                    # 判断新记录对象在数据库中是否符合索引唯一的约束条件
                    new_object = models.Permission(**row_dict)  # 用行数据实例化一个对象
                    new_object.validate_unique()
                    object_list.append(new_object)
                except Exception as e:
                    formset.errors[i].update(e)  # 校验索引唯一失败，更新错误信息
                    generate_formset = formset  # 这行目的是在页面上显示错误信息
                    has_error = True
            if not has_error:  # 没有错误才可以批量增加
                models.Permission.objects.bulk_create(object_list, batch_size=100)  # 没有错误信息时，批量增加100条数据
        else:  # 如果formset校验失败，含校验错误数据的formset 赋值给generate_formset， 不再初始化生成formset数据
            generate_formset = formset  # 包含校验错误数据的formset 赋值给generate_formset

    update_formset = None
    if request.method == 'POST' and post_type == 'update':
        # pass    #批量更新
        formset = update_formset_class(data=request.POST)
        if formset.is_valid():
            post_row_list = formset.cleaned_data
            for i in range(0, formset.total_form_count()):
                row_dict = post_row_list[i]
                permission_id = row_dict.pop('id')
                try:
                    row_object = models.Permission.objects.filter(id=permission_id).first()
                    for k, v in row_dict.items():  # 利用反射将row_dict的数据(校验后的页面数据)设置到row_object， k,v
                        setattr(row_object, k, v)
                    row_object.validate_unique()
                    row_object.save()  # 由于是更新，不能批量插入数据库
                except Exception as e:
                    formset.errors[i].update(e)
                    update_formset = formset
        else:
            update_formset = formset

    # 1. 获取项目中所有的URL
    all_url_dict = get_all_url_dict()
    '''
    {
        rbac:role_list {'name': 'rbac:role_list', 'url': '/rbac/role/list/'}
        rbac:role_add {'name': 'rbac:role_add', 'url': '/rbac/role/add/'}
        rbac:role_edit {'name': 'rbac:role_edit', 'url': '/rbac/role/edit/(?P<pk>\\d+)/'}
    }
    '''
    router_name_set = set(all_url_dict.keys())  # 项目中所有URL的name 集合

    # 2. 获取数据库中所有的URL
    permissions = models.Permission.objects.all().values('id', 'title', 'name', 'url', 'menu_id',
                                                         'pid_id')  # 返回一个Queryset类型
    permission_dict = OrderedDict()
    permission_name_set = set()
    for row in permissions:
        permission_dict[row['name']] = row
        permission_name_set.add(row['name'])  # 将数据库中的URL添加到集合中

    '''
    {
        'rbac:role_list': {'id':1, 'title': '角色列表', 'name': 'rbac:role_list', url....},
        'rbac:role_add': {'id':2, 'title': '添加角色', 'name': 'rbac:role_add', url....},
        ....

    }
    '''

    for name, value in permission_dict.items():
        router_row_dict = all_url_dict.get(name)  # {'name': 'rbac:role_list', 'url': '/rbac/role/list/'}
        if not router_row_dict:  # 当数据库中有name, 但自动发现中没有name, ，在更新操作中处理，先跳过当前循环
            continue
        if value['url'] != router_row_dict['url']:  # 如果数据库中name对应的URL， 与自动发现name对应的url不相等
            value['url'] = '自动发现URL和数据库URL中不一致'

            # print("permission_dict:",permission_dict)
            # 3. 应该添加，删除，修改的权限有哪些
            # 3.1 计算出应该增加的name

    # 如果generate_formset不为None， 说明提交的请求是POST,不再初始化生成generate_formset数据，使用提交的generate_formset数据
    # 如果generate_formset为None， 说明提交的请求是GET , generate_formset 初始化生成数据
    if not generate_formset:
        print("generate_formset:", generate_formset)
        generate_name_list = router_name_set - permission_name_set  # 自动发现name数量 大于 数据库中name数量， 求差集
        # generate_formset_class = formset_factory(MultiAddPermissionForm, extra=0)   #该行移动到本函数的顶部
        # generate_formset_class(initial=[{'name': 'rbac:role_list', 'url': '/rbac/role/list/'},{'name': 'rbac:role_add', 'url': '/rbac/role/add/'}])  #initial示例
        generate_formset = generate_formset_class(
                initial=[row_dict for name, row_dict in all_url_dict.items() if name in generate_name_list])  # 列表生成式



    # 3.2 计算出应该删除的name
    delete_name_list = permission_name_set - router_name_set  # 数据库中name数量 大于 自动发现name数量 求差集
    delete_row_list = [row_dict for name, row_dict in permission_dict.items() if name in delete_name_list]
    # print("delete_row_list:", delete_row_list)

    # 3.3 计算出应该更新的name
    if not update_formset:
        update_name_list = permission_name_set & router_name_set  # 取两个集合的交集, 即集合1与集合2 都有的数据
        # update_formset_class = formset_factory(MultiEditPermissionForm, extra=0)   #这行代码移动到上面了
        update_formset = update_formset_class(
                initial=[row_dict for name, row_dict in permission_dict.items() if name in update_name_list])  # ??

    # print("update_formset",update_formset)
    # print("all_url_dict:",all_url_dict)
    # for k,v in all_url_dict.items():
    #     print(k,v)

    '''
    输出结果：
rbac:role_list {'name': 'rbac:role_list', 'url': '/rbac/role/list/'}
rbac:role_add {'name': 'rbac:role_add', 'url': '/rbac/role/add/'}
rbac:role_edit {'name': 'rbac:role_edit', 'url': '/rbac/role/edit/(?P<pk>\\d+)/'}
rbac:role_del {'name': 'rbac:role_del', 'url': '/rbac/role/del/(?P<pk>\\d+)/'}
rbac:user_list {'name': 'rbac:user_list', 'url': '/rbac/user/list/'}
rbac:user_add {'name': 'rbac:user_add', 'url': '/rbac/user/add/'}
rbac:user_edit {'name': 'rbac:user_edit', 'url': '/rbac/user/edit/(?P<pk>\\d+)/'}
rbac:user_del {'name': 'rbac:user_del', 'url': '/rbac/user/del/(?P<pk>\\d+)/'}
rbac:user_reset_pwd {'name': 'rbac:user_reset_pwd', 'url': '/rbac/user/reset/password/(?P<pk>\\d+)/'}
rbac:menu_list {'name': 'rbac:menu_list', 'url': '/rbac/menu/list/'}
rbac:menu_add {'name': 'rbac:menu_add', 'url': '/rbac/menu/add/'}
rbac:menu_edit {'name': 'rbac:menu_edit', 'url': '/rbac/menu/edit/(?P<pk>\\d+)/'}
rbac:menu_del {'name': 'rbac:menu_del', 'url': '/rbac/menu/del/(?P<pk>\\d+)/'}
rbac:second_menu_add {'name': 'rbac:second_menu_add', 'url': '/rbac/second/menu/add/(?P<menu_id>\\d+)/'}
rbac:second_menu_edit {'name': 'rbac:second_menu_edit', 'url': '/rbac/second/menu/edit/(?P<pk>\\d+)/'}
rbac:second_menu_del {'name': 'rbac:second_menu_del', 'url': '/rbac/second/menu/del/(?P<pk>\\d+)/'}
rbac:permission_add {'name': 'rbac:permission_add', 'url': '/rbac/permission/add/(?P<second_menu_id>\\d+)/'}
rbac:permission_edit {'name': 'rbac:permission_edit', 'url': '/rbac/permission/edit/(?P<pk>\\d+)/'}
rbac:permission_del {'name': 'rbac:permission_del', 'url': '/rbac/permission/del/(?P<pk>\\d+)/'}
rbac:multi_permissions {'name': 'rbac:multi_permissions', 'url': '/rbac/multi/permissions/'}
customer_layout {'name': 'customer_layout', 'url': '/layout'}
    '''
    return render(
            request,
            'rbac/multi_permissions.html',
            {
                'generate_formset': generate_formset,
                'delete_row_list': delete_row_list,
                'update_formset': update_formset,

            }
    )


def multi_permissions_del(request, pk):
    '''
    批量页面的权限删除
    :param request:
    :param pk:
    :return:
    '''
    url = memory_reverse(request, 'rbac:multi_permissions')  # 重定向到带原始参数的URL(通过URL参数反向解析得到带参的URL)
    if request.method == 'GET':
        return render(request, 'rbac/delete.html', {'cancle': url})  # cancle 作为变量传给前端delete.html页面

    # 当点击delete.html页面的确认按钮时,浏览器向服务器发送了一个post请求，http://127.0.0.1:8000/rbac/second/menu/del/14/?_filter=mid%3D13
    models.Permission.objects.filter(id=pk).delete()
    return redirect(url)


def distribute_permissions(request):
    '''
    权限分配
    :param request:
    :return:
    '''
    user_id = request.GET.get('uid')
    #业务中的用户表settings.RBAC_USER_MODLE_CLASS == "app01.models.UserInfo" 是一个字符串
    user_model_class = import_string(settings.RBAC_USER_MODLE_CLASS) #这个函数的功能就是从字符串来导入相应的函数的

    #user_object = models.UserInfo.objects.filter(id=user_id).first()
    user_object = user_model_class.objects.filter(id=user_id).first()
    if not user_object:
        user_id = None

    role_id = request.GET.get('rid')
    role_object = models.Role.objects.filter(id=role_id).first()
    if not role_object:
        role_id = None

    print(request.POST)
    if request.method == 'POST' and request.POST.get('type') == 'role':
        role_id_list = request.POST.getlist('roles')   #roles 是所有复选框， 前端页面 <input class="" type="checkbox" name="roles"
        # 用户和角色关系添加到第三张表(关系表)
        if not user_object:
            return HttpResponse('请选择用户，然后再分配角色')
        user_object.roles.set(role_id_list) #通过user对象的roles属性的set()向第三张关系表添加记录

    if request.method == 'POST' and request.POST.get('type') == 'permission':
        permission_id_list = request.POST.getlist('permissions')  #permissions 是所有复选框，<input  name="permissions"  type="checkbox"
        # 用户和角色关系添加到第三张表(关系表)
        if not role_object:
            return HttpResponse('请选择角色，然后再分配权限')
        role_object.permissions.set(permission_id_list) #通过role对象的permissions属性的set()向第三张关系表添加记录

    #获取当前用户所拥有的角色id
    if user_id:
        user_has_roles = user_object.roles.all()
    else:
        user_has_roles = []

    user_has_roles_dict = { item.id:None for item in user_has_roles }  #将角色id构造成字典，因为字典查找速度快，实际上只需要角色id
    '''
    {
        1:None,
        2:None,
        3:None,

    }

    '''

    #获取当前用户所拥有的权限

    #如果只选中的角色，优先显示选中角色中所拥有的权限
    #如果没有选择角色，才显示用户所拥有的权限

    if role_object:         #只选择了角色，显示当前角色所拥有的所有权限
        user_has_permissions = role_object.permissions.all()
        user_has_permissions_dict = {item.id:None for item in user_has_permissions }    # item.id 表示rbac_role_permissions权限id，即permission_id
        #print("user_has_permissions1",user_has_permissions) #<QuerySet [<Permission: Permission object (1)>, <Permission: Permission object (2)>, 返回多条rbac_permission表的记录对象

    elif user_object:       #未选择角色 ，但选择了用户，显示该用户所拥有的角色以及对应的角色的权限
     #为什么要有permissions__id__isnull=False？ 一个角色如果没有权限，他可能出现None, 另外，还要去重复记录
        user_has_permissions = user_object.roles.filter(permissions__id__isnull=False).values('id', 'permissions').distinct()   #通过role-permissions关系表，根据角色id, 查找permission_id
        user_has_permissions_dict = { item['permissions']:None  for item in user_has_permissions }    # item['permission'] 表示权限id
        print("user_has_permissions",user_has_permissions) #<QuerySet [{'id': 3, 'permissions': 1}, {'id': 3, 'permissions': 2}]>

    else:
        user_has_permissions = []
        user_has_permissions_dict = { }

    all_user_list = user_model_class.objects.all()
    all_role_list = models.Role.objects.all()

    menu_permission_list = []

    #通过3个for循环将一级菜单，二级菜单和所有权限组合起来，所有权限挂靠二级菜单，二级菜单挂靠一级菜单
    #所有的菜单(一级菜单)
    all_menu_list = models.Menu.objects.values('id', 'title')

    '''
    [
        { id:'1', title: 菜单1， children: [{ id:'1', title:x1, menu_id: 1，children ：[{id:11, title: x2, pid: 1},},{ id:'2', title:x1, menu_id: 1},]},
        { id:'2', title: 菜单2}, children: [{ id:'1', title:x1, menu_id: 2},{ id:'2', title:x1, menu_id: 2}
        { id:'3', title: 菜单3},
    ]
    '''
    all_menu_dict = { }
    '''
    {
        1:{ id:'1', 'title': '菜单1', children:[{ id:'1', title:x1, menu_id: 1, children = [] },{ id:'2', title:x1, menu_id: 1, children = [] },]},
        2:{ id:'2', 'title': '菜单2'}, children: [{ id:'3', title:x1, menu_id: 2, children = [] },{ id:'4', title:x1, menu_id: 2, children = [] },]},
        3:{ id:'3', 'title': '菜单3', children:[]},
        4:{ id:'4', 'title': '菜单4'},
    }
    '''
    #将列表转化成字典的目的：需要频繁的将二级菜单的menu_id，在一级菜单中查找，转换成字典后查找会快， 第二，在字典中加条目，等同于在列表中加条目
    for item in all_menu_list:
        item['children'] = []
        all_menu_dict[item['id']] = item   #all_menu_list 与all_menu_dict 是同一块内存地址，即如果修改了与all_menu_dict, 修改后的数据也会体现在all_menu_list

    #所有的二级菜单
    all_second_menu_list = models.Permission.objects.filter(menu__isnull=False).values('id', 'title', 'menu_id')            #menu__isnull=False 表示 menu_id 不为空

    '''
    为什么要获取menu_id ? 答：之后要将二级菜单归属到一级菜单
    [
        { id:'1', title:x1, menu_id: 1, children = [] },   #当menu_id: 1， 将该二级菜单归属到一级菜单id=1
        { id:'2', title:x1, menu_id: 1, children = []},
        { id:'3', title:x1, menu_id: 2, children = []},   #当menu_id: 2， 将该二级菜单归属到一级菜单id=2
        { id:'4', title:x1, menu_id: 2, children = []},
        { id:'5', title:x1, menu_id: 3, children = []},   #当menu_id: 3， 将该二级菜单归属到一级菜单id=3
    ]

    '''
    all_second_menu_dict = { }
    '''
     {
        1: { id:'1', title:x1, menu_id: 1, children = [{id:11, title: x2, pid: 1},]},   #当menu_id: 1， 将该二级菜单归属到一级菜单id=1
        2: { id:'2', title:x1, menu_id: 1, children = []},
        3: { id:'3', title:x1, menu_id: 2, children = []},   #当menu_id: 2， 将该二级菜单归属到一级菜单id=2
        4: { id:'4', title:x1, menu_id: 2, children = []},
        5: { id:'5', title:x1, menu_id: 3, children = []},   #当menu_id: 3， 将该二级菜单归属到一级菜单id=3
    }
    '''

    for row in all_second_menu_list:
        row['children'] = []    #放三级菜单
        all_second_menu_dict[row['id']] = row
        menu_id = row['menu_id']
        all_menu_dict[menu_id]['children'].append(row)   #将二级菜单挂靠到一级菜单， all_menu_dict[menu_id]是一个字典，如：all_menu_dict[1]，它的children.append(row)

    #所有的三级菜单(不能做菜单的权限)
    all_permission_list = models.Permission.objects.filter(menu__isnull=True).values('id', 'title', 'pid_id')            #menu__isnull=False 表示 menu_id 不为空

    #一级菜单，二级菜单与所有权限都是同一块内存
    '''
    [
        {id:11, title: x2, pid: 1},    #根据pid找到二级菜单
        {id:12, title: x2, pid: 1},
        {id:13, title: x2, pid: 2},
        {id:14, title: x2, pid: 3},
        {id:15, title: x2, pid: 4},
        {id:15, title: x2, pid: 5},
    ]
    '''
    #三级菜单挂到二级菜单， 一级菜单引用二级菜单，二级菜单引用所有权限， 即一级菜单包括所有的数据
    for row in all_permission_list:
        pid = row['pid_id']        #pid_id 可能为None 为什么？因为在批量操作权限页面，有可能即没选择菜单和也没选择父权限
        if not pid:
            continue
        all_second_menu_dict[pid]['children'].append(row)    #所有权限挂靠到二级菜单，all_second_menu_dict[pid]是一个字典, 如all_second_menu_dict[7]，它的children.append(row)

    '''
    构造最终的数据结构如下
    [
        {
            id:1,
            title: '业务管理',
            children: [
                {
                    'id': 11,
                    title: '账单列表'，
                    children: [
                        {'id': 12, title: '客户列表'},
                    },
                {'id': 12, title: '客户列表'},
            ]
        },
    ]
    '''
    #print("all_menu_list:",all_menu_list)
    return render(
        request,
            'rbac/distribute_permissions.html',
        {
            'user_list': all_user_list,
            'role_list': all_role_list,
            'all_menu_list':all_menu_list,
            'user_id': user_id,
            'user_has_roles_dict': user_has_roles_dict,
            'user_has_permissions_dict': user_has_permissions_dict,
            'role_id': role_id,

        }
    )