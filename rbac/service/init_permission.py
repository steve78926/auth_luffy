# -*- coding:utf-8 -*-

from django.conf import settings

def init_permission(current_user, request):

    '''
    用户权限信息初始化
    :param current_user: 当前用户对象
    :param request: 请求相关所有数据
    :return:
    '''
    # 2. 权限信息初始化
    #根据当前用户信息获取此用户所拥有的所有权限， 并放入session
    #  permission_list 就是当前用户所有的权限, queryset 不能直接放到session当中

    ######################   一级菜单列   ######################
    # permission_queryset = current_user.roles.filter(permissions__isnull=False).values("permissions__id",
    #                                                                                   "permissions__title",
    #                                                                                   "permissions__is_menu",
    #                                                                                   "permissions__icon",
    #                                                                                   "permissions__url",
    #                                                                                   ).distinct()

    ######################   二级菜单列   ######################
    permission_queryset = current_user.roles.filter(permissions__isnull=False).values("permissions__id",
                                                                                      "permissions__title",
                                                                                      "permissions__url",
                                                                                      "permissions__name",   #权限的别名
                                                                                      "permissions__pid_id",
                                                                                      "permissions__pid__title",   #pid 是自关联ForeignKey
                                                                                      "permissions__pid__url",      #pid 是自关联ForeignKey
                                                                                      "permissions__menu_id",
                                                                                      "permissions__menu__title",
                                                                                      "permissions__menu__icon",
                                                                                      ).distinct()

    #"permissions__pid__title" 表示permissions表中pid外键表，由于是自关联，这个键表还是permission, pid外键对应的记录的title
    #"permissions__pid__url", 表示permissions表中pid外键表，由于是自关联，这个键表还是permission, pid外键对应的记录的url
    #permissions__menu_id, 与 permissions__menu__title, permissions__menu__icon 有什么区别？
    # permissions__menu_id为什么用一个下划线？ permissions__menu__title, permissions__menu__icon 用两个下划线
    #答：permissions__menu_id表示permission表的menu_id列，permissions__menu__title 表示menu表的title列
    #3. 获取权限 + 菜单信息
    # permissions__id， permissions__url 必须用双引号引起来，否则报错
    #获取权限中所有的URL
    # permission_list = []
    # for item in permission_queryset:
    #     permission_list.append(item['permission_url'])

    # menu_list = []   # 一级菜单
    #permission_list = []
    permission_dict = {}
    menu_dict = {}
    for item in permission_queryset:

        #permission_list.append(item['permissions__url'])    #构建权限列表
        # permission_list.append({'id': item['permissions__id'],
        #                         'title': item['permissions__title'],
        #                         'url': item['permissions__url'],
        #                         'pid': item['permissions__pid_id'],     #当前权限URL对应的外键表（自关联表rbac_permission）的id (本例中1，7)
        #                         'p_title': item['permissions__pid__title'],    #当前权限URL对应的外键表（自关联表rbac_permission）的title （(本例中客户列表，账单列表）
        #                         'p_url': item['permissions__pid__url'],
        #                         })

        permission_dict[item['permissions__name']] = {
                                'id': item['permissions__id'],
                                'title': item['permissions__title'],
                                'url': item['permissions__url'],
                                'pid': item['permissions__pid_id'],     #当前权限URL对应的外键表（自关联表rbac_permission）的id (本例中1，7)
                                'p_title': item['permissions__pid__title'],    #当前权限URL对应的外键表（自关联表rbac_permission）的title （(本例中客户列表，账单列表）
                                'p_url': item['permissions__pid__url'],
                                }
        menu_id = item['permissions__menu_id']
        print("menu_id:",menu_id)
        if not menu_id:   #如果menu_id为空，说明这行url不是一个菜单，跳过当前记录，处理下一行记录
            continue

        node = {'id': item['permissions__id'], 'title': item['permissions__title'], 'url': item['permissions__url']}
        if menu_id in menu_dict:        #menu_id的取值如：1，2。。。
            menu_dict[menu_id]['children'].append(node)     #menu_id 是一级菜单ID, append(node) 是再次增加二级菜单项
        else:
            menu_dict[menu_id] = {
                'title': item['permissions__menu__title'],
                'icon': item['permissions__menu__icon'],
                'children': [node,]
            }

    print(menu_dict)  #构建二极菜单数据结构

    #如果权限表中url:客户列表的menu_id=1,同时，账单列表的menu_id=1，即两个menu_id相同
    #则：menu_dict结果：
    '''
        {1:
            {'title': '信息管理',
             'icon': 'fa-camero-retro',
             'children': [
                 {
                    'id': 1, 'title': '客户列表',
                    'url': '/customer/list/'
                 },
                 {
                     'id': 7, 'title': '账单列表',
                    'url': '/payment/list/'
                 }
                ]
             }
         }
    '''
    #如果权限表中url:客户列表的menu_id=1,同时，账单列表的menu_id=2，，即两个menu_id不相同
    #则：menu_dict结果：


    '''
            {
            1:
                {'title': '信息管理', 'icon': 'fa-camero-retro',
                'children': [{'id': 1, 'title': '客户列表', 'url': '/customer/list/'}]},
             2:
                 {'title': '用户管理', 'icon': 'fa-fire', '
                 children': [{'id': 7, 'title': '账单列表', 'url': '/payment/list/'}]}
            }

    '''

    ############################       一级菜单   ############################
        # if item['permissions__is_menu']:
        #     temp = {                                           #构建菜单临时字典，包括，菜单名称，菜单图标，菜单URL
        #         'title': item['permissions__title'],
        #         'icon': item['permissions__icon'],
        #         'url': item['permissions__url']
        #     }
        #     menu_list.append(temp)                              #构建菜单列表

    ### permission_list = [item['permissions__url'] for item in permission_queryset]
    #request.session[settings.PERMISSION_SESSION_KEY] = permission_list
    #request.session[settings.MENU_SESSION_KEY] = menu_list
    ############################       一级菜单代码结束   ############################
    #request.session[settings.PERMISSION_SESSION_KEY] = permission_list
    request.session[settings.PERMISSION_SESSION_KEY] = permission_dict
    request.session[settings.MENU_SESSION_KEY] = menu_dict

    ###############100 test #####################