
#-*- coding:utf-8 -*-

'''
RBAC组件使用文档
最好使用markdown 写文档

RBAC组件的使用文档

1. 将rbac组件拷贝到项目中。


2. 将rbac/migrations目录中的数据库迁移记录删除，不要删除__init__.py
    数据库迁移记录是数据表结构有变化 迁移时留下的记录
    没有讲为什么要删除这些记录

3。 业务系统中用户表结构的设计

    业务表结构中的用户表需要和rbac中的用户表有继承关系，如：

     rbac/models.py
    class UserInfo(models.Model):
        """
        用户表
        """
        name = models.CharField(verbose_name='用户名',max_length=32)
        password = models.CharField(verbose_name='密码', max_length=32)
        email = models.EmailField(verbose_name='邮箱', max_length=32)
        roles = models.ManyToManyField(verbose_name='关联的角色', to=Role, blank=True)  严重提醒：to=Role 不能加引号

        def __str__(self):
            return self.name

        #class Meta:
            #abstract = True 表示 django以后再做数据库迁移时，不再为UserInfo类创建相关的表以及表结构了。
            # 同时，也不会生成用户表与角色表的关系表
            # 而此类可以当做"父类"，被其他Model类继承。目的：让业务应用的用户表继承rbac的用户表
            abstract = True

    业务app01/models.py

    class UserInfo(RbacUserInfo):       #从父类rbac/UserInfo 类中继承所有字段，原rbac中的字段转移动业务用户表中
        """
        用户表, RBAC组件里也有用户表
        用户管理功能写在业务功能中，不要用RBAC组件里用户管理
        """
        phone = models.CharField(verbose_name='联系方式', max_length=32)
        level_choices = (
            (1, 'T1'),
            (2, 'T2'),
            (3, 'T3'),
        )
        level = models.IntegerField(verbose_name='级别', choices=level_choices)

        department = models.ForeignKey(verbose_name='部门', to='Department')

4。 将业务系统中的用户表的路径写到配置文件

    #业务中的用户表
    RBAC_USER_MODLE_CLASS = "app01.models.UserInfo"

    用于在rbac分配权限时，读取业务表中的用户信息。

5. 业务逻辑开发

    5.1 将所有的路由都设置一个name, 用于反向生成url, 以及粒度控制 到按钮级别的权限控制。 如：

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

6。 权限信息的录入

    6.1  在URL中添加rbac的路由分发，注意：必须设置namespace
urlpatterns = [
    。。。。
    re_path(r'^rbac/', include('rbac.urls', namespace='rbac')),
]

    6.2 rbac提供的地址进行操作

        http://127.0.0.1:8000/rbac/menu/list/
        http://127.0.0.1:8000/rbac/role/list/
        http://127.0.0.1:8000/rbac/distribute/permissions/

    相关配置：自动发现URL时，排除的URL:

    #自动发现路由中URL时， 排除的URL
AUTO_DISCOVER_EXCLUDE = [
        '/admin/.*',
        '/login/',
        '/logout/',
        '/index/',
    ]





7. 编写用户登录逻辑【进行权限 的初始化】

from django.shortcuts import render, redirect
from app01 import models
from rbac.service.init_permission import init_permission

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    user = request.POST.get('username')
    pwd = request.POST.get('password')

    user_object = models.UserInfo.objects.filter(name=user, password=pwd).first()
    if not user_object:
        return render(request, 'login.html', {'error': '用户名和密码错误'})

    #用户权限信息初始化
    init_permission(user_object, request)

    return redirect('/index/')

    相关的配置：权限和菜单的session_key

 在settings.py中增加
#权限在Session中存储的key
PERMISSION_SESSION_KEY="luffy_permission_url_list_key"
#菜单在Session中存储的key
MENU_SESSION_KEY = "luffy_permission_menu_key"

8. 编写首页的逻辑

def index(request):
    return render(request, 'index.html')

    相关的配置：

    #需要登录能才访问，但无需权限校验
    NO_PERMISSION_LIST = [
        '/index/',
        '/logout/',
    ]

9. 通过中间件进行权限校验

    #中间件权限校验
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'rbac.middlewares.rbac.RbacMiddleware',
    ]

    #白名单， 无需登录就可以访问
    VALID_URL_LIST = [          #VALID_URL_LIST 是不受限权控制的白名单
        '/admin/.*',
        '/login/',
    ]

10。 粒度到按钮级别的控制

{% extends 'layout.html' %}
{% load rbac %}

{% block content %}
    <h1>角色列表</h1>
    <div class="luffy-container">
        <div class="btn-group">

            {% if request |has_permission: 'host_add' %}
            <a href="{% memory_url request 'host_add' %}" class="btn btn-default">
                <i class="fa fa-plus-square"></i> 添加主机
            </a>
            {% endif  %}
        </div>
        <table class="table table-bordered table-responsive">
            <thead>
            <tr>
                <td>主机名</td>
                <td>IP</td>
                <td>部门</td>
                {% if request |has_permission: 'host_eidt' or request |has_permission: 'host_del' %}
                    <td>操作</td>
                {% endif %}
            </tr>
            </thead>
            <tbody>
            {% for row in host_queryset %}
                <tr>
                    <td>{{ row.hostname }}</td>
                    <td>{{ row.ip }}</td>
                    <td>{{ row.depart.title }}</td>   <!-- row.department.title  是跨表操作 -->
                    {% if request |has_permission: 'host_eidt' or request |has_permission: 'host_del' %}
                        <td>
                            {% if request |has_permission: 'host_eidt' %}
                                <a style="color:#333" href="{% memory_url request 'host_edit' pk=row.id  %}">
                                    <i class="fa fa-edit" aria-hidden="true"></i>
                                </a>
                            {% endif %}
                            |
                            {% if request |has_permission: 'host_eidt' %}
                                <a style="color:#d9534f" href="{% memory_url request 'host_del' pk=row.id  %}">
                                    <i class="fa fa-trash-o" aria-hidden="true"></i>
                                </a>
                            {% endif %}
                    {% endif %}
                    </td>
                </tr>
            {% endfor %}
            </tbody>
        </table>
    </div>
{% endblock content %}





    time: 13:30

总结 ： 目的是希望在任意系统中应用权限系统。

    -  用户登录 + 用户首页 ＋ 用户注销， 业务逻辑
    － 项目业务逻辑开发
        注意：开发时将灵活的去设置layout.html 中两个inclusion_tag

        <div class="pg-body">
            <div class="left-menu">
                <div class="menu-body">         {# 为什么要加这层盒子 #}
                    {% multi_menu request %}     #开发时去掉，上线时取回。{# request 作为参数传给static_menu模板函数 #}
                </div>

            </div>
            <div class="right-body">
                {%  breadcrumb request %}      #开发时去掉，上线时取回。    {# 面包屑导航条#}
                {% block content %} {% endblock content %}
            </div>
        </div>

    - 权限信息的录入

    - 配置文件

        #注册app:
        INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app01',
    'rbac',
]

#定义中间件
MIDDLEWARE = [
  .......
    'rbac.middlewares.rbac.RbacMiddleware',
]


######################  权限相关配置  ######################
#业务中的用户表
RBAC_USER_MODLE_CLASS = "app01.models.UserInfo"

#权限在Session中存储的key
PERMISSION_SESSION_KEY="luffy_permission_url_list_key"
#菜单在Session中存储的key
MENU_SESSION_KEY = "luffy_permission_menu_key"

#白名单
VALID_URL_LIST = [          #VALID_URL_LIST 是不受限权控制的白名单
    '/admin/.*',
    '/login/',
]

#需要登录能才访问，但无需权限校验
NO_PERMISSION_LIST = [
    '/index/',
    '/logout/',
]


#自动发现路由中URL时， 排除的URL
AUTO_DISCOVER_EXCLUDE = [
        '/admin/.*',
        '/login/',
        '/logout/',
        '/index/',
    ]

    - 粒度到按钮级别的控制



auth_luffy\app01\templates\host_list.html


auth_luffy\app01\templates\user_list.html





3. 业务开发
    3.1 (方式一) 用户表的处理使用 One to One 将用户表拆分到两张表中，

    class UserInfo(models.Model):
        """
        用户表
        """
        name = models.CharField(verbose_name='用户名',max_length=32)
        password = models.CharField(verbose_name='密码', max_length=32)
        email = models.EmailField(verbose_name='邮箱', max_length=32)
        roles = models.ManyToManyField(verbose_name='关联的角色', to='Role', blank=True)

        def __str__(self):
            return self.name


    class UserInfo(models.Model):
        """
        用户表, RBAC组件里也有用户表
        用户管理功能写在业务功能中，不要用RBAC组件里用户管理
        """
        user = models.OneToOneField(verbose_name='用户', to=RbacUserInfo)     #业务系统的用户表与RBAC的用户表创建一对一的关系
        phone = models.CharField(verbose_name='联系方式', max_length=32)
        level_choices = (
            (1, 'T1'),
            (2, 'T2'),
            (3, 'T3'),
        )
        level = models.IntegerField(verbose_name='级别', choices=level_choices)

        department = models.ForeignKey(verbose_name='部门', to='Department')

        def __str__(self):
            return self.user.name               # self.user.name ??

    缺点：用户数据分散在两张表中
    优点：利用上rbac中的用户管理功能，但这个功能不全。在rbac中对用户的增删改查已经写好了，但无法对业务应用中的用户表进行操作

    3.2  用户表整合在一张表中 （被佩奇老师推荐的方法）

    rbac/models.py
    class UserInfo(models.Model):
        """
        用户表
        """
        name = models.CharField(verbose_name='用户名',max_length=32)
        password = models.CharField(verbose_name='密码', max_length=32)
        email = models.EmailField(verbose_name='邮箱', max_length=32)
        roles = models.ManyToManyField(verbose_name='关联的角色', to=Role, blank=True)  严重提醒：to=Role 不能加引号

        def __str__(self):
            return self.name

        #class Meta:
            #abstract = True 表示 django以后再做数据库迁移时，不再为UserInfo类创建相关的表以及表结构了。
            # 同时，也不会生成用户表与角色表的关系表
            # 而此类可以当做"父类"，被其他Model类继承。目的：让业务应用的用户表继承rbac的用户表
            abstract = True

    业务app01/models.py

    class UserInfo(RbacUserInfo):       #从父类rbac/UserInfo 类中继承所有字段，原rbac中的字段转移动业务用户表中
        """
        用户表, RBAC组件里也有用户表
        用户管理功能写在业务功能中，不要用RBAC组件里用户管理
        """
        phone = models.CharField(verbose_name='联系方式', max_length=32)
        level_choices = (
            (1, 'T1'),
            (2, 'T2'),
            (3, 'T3'),
        )
        level = models.IntegerField(verbose_name='级别', choices=level_choices)

        department = models.ForeignKey(verbose_name='部门', to='Department')

        def __str__(self):
            return self.user.name               # self.user.name ??

    优点：将所有用户信息放入到一张表中(业务的用户表)
    缺点：在rbac中所有关于用户表的操作，不能在使用了。

    注意：rbac中 两处使用了用户表
        - 用户管理： 用户密码重置，用户增，删，改，查  【该部分代码删除】
        - 权限分配时用户列表 【读取业务中的用户表即可】

    删除rbac/admin.py中的代码，这部分代码已经用不上了

    迁移数据库时报错：

    D:\lufei_xue_cheng\module7\auth_luffy>python manage.py makemigrations
SystemCheckError: System check identified some issues:

ERRORS:
app01.UserInfo.roles: (fields.E300) Field defines a relation with model 'Role', which is either not installed, or is abstract.
app01.UserInfo.roles: (fields.E307) The field app01.UserInfo.roles was declared with a lazy reference to 'app01.role', but app 'app01' doesn't provide model 'role'.
app01.UserInfo_roles.role: (fields.E307) The field app01.UserInfo_roles.role was declared with a lazy reference to 'app01.role', but app 'app01' doesn't provide model 'role'.

    Field defines a relation with model 'Role', which is either not installed, or is abstract.
    字段定义了与模型“Role”的关系，该关系要么没有安装，要么是抽象的。

    因为：业务app01/models.py/UserInfo类从rbac/RbacUserInfo类中继承，相当于 业务app01/models.py/UserInfo类中包含如下一行代码：
    roles = models.ManyToManyField(verbose_name='关联的角色', to='Role', blank=True)
    而app01/models.py没有定义Role类，所以上一行代码 to='Role' 对Role模型的引用导致报错

    解决方法： rbac/models.py/UserInfo类中， to='Role'  去掉单引号变成 to=Role 表示 子类在继承父类时，子类继承了父类的内存地址

    即， to='Role' 表示在当前models.py中查找 Role类，
         to=Role   表示在父类或基类中查找Role类

    重新迁移数据库：命令操作正常

    但是请注意：在rbac/models.py中，Role类的定义一定要放在UserInfo类的前面

    D:\lufei_xue_cheng\module7\auth_luffy>python manage.py makemigrations
    Migrations for 'app01':
    app01\migrations\0001_initial.py
        - Create model Department
        - Create model Host
        - Create model UserInfo

   D:\lufei_xue_cheng\module7\auth_luffy>python manage.py migrate
    Operations to perform:
    Apply all migrations: admin, app01, auth, contenttypes, rbac, sessions
    Running migrations:
    Applying contenttypes.0001_initial... OK
    Applying auth.0001_initial... OK
    Applying admin.0001_initial... OK
    Applying admin.0002_logentry_remove_auto_add... OK
    Applying rbac.0001_initial... OK
    Applying app01.0001_initial... OK

    数据库迁移在数据库中生成了app01_userinfo表，app01_userinfo_roles表(app01_userinfo与 rbac_role表的关系表 )

    对于rbac中的代码修改：

    1.  在URL中讲用户表的增，删，改，查和修改密码的功能删除，即将rbac/urls.py 中用户管理的URL注释掉，如下
       在业务应用中实现用户管理功能

    # re_path(r'^user/list/$', user.user_list, name='user_list'),
    # re_path(r'^user/add/$', user.user_add, name='user_add'),
    # re_path(r'^user/edit/(?P<pk>\d+)/$', user.user_edit, name='user_edit'),
    # re_path(r'^user/del/(?P<pk>\d+)/$', user.user_del, name='user_del'),
    # re_path(r'^user/reset/password/(?P<pk>\d+)/$', user.user_reset_pwd, name='user_reset_pwd'),


    2. 权限分配时，读取用户表变成通过配置文件来进行指定并导入
    rbac/menu.py
    from django.conf import settings
    from django.utils.module_loading import import_string

    def distribute_permissions(request):
         #业务中的用户表settings.RBAC_USER_MODLE_CLASS == "app01.models.UserInfo" 是一个字符串
        user_model_class = import_string(settings.RBAC_USER_MODLE_CLASS) #这个函数的功能就是通过字符串来导入相应的函数

    3.3 业务开发
        - 用户表的增，删，改， 查
        - 主机表的增，删，改， 查

        感受： 编写业务功能时，出现了大量的拷贝 (通过stark组件可以避免大量拷贝)

        rbac中的页面模板也引入到新项目中

        如果要使用rbac模板，则需要将模板中的导航条 + 菜单 去掉，当业务开发完成之后，上线之前再把他拿回来。
         {% multi_menu request %}
         {%  breadcrumb request %}

    4. 权限的应用

        4.1 将菜单权限和面包屑导航条加到layout.html

        <div class="pg-body">
            <div class="left-menu">
                <div class="menu-body">         {# 为什么要加这层盒子 #}
                    {% multi_menu request %}     {# request 作为参数传给static_menu模板函数 #}
                </div>
            </div>
            <div class="right-body">
                {%  breadcrumb request %}       {# 面包屑导航条#}
                {% block content %} {% endblock content %}
            </div>
        </div>

        4.2  中间件的应用

        IDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'rbac.middlewares.rbac.RbacMiddleware',         #增加rbac中间件
]


        4.3 白名单的处理 settings.py 中添加以下配置

               VALID_URL_LIST = [          #VALID_URL_LIST 是不受限权控制的白名单
            '/login/',
            '/admin/.*',
        ]

        4.4 权限初始化 settings.py 中添加以下配置
        PERMISSION_SESSION_KEY="luffy_permission_url_list_key"
        MENU_SESSION_KEY = "luffy_permission_menu_key"

        4.5 批量操作权限时，自动发现路由中所有的URL时，应该排除的URL

        AUTO_DISCOVER_EXCLUDE = [
                '/admin/.*',
                '/login/.*',
        ]

        4.6  用户登录的逻辑

            写完用户登录逻辑，对于index/，login/，logout/ 三个URL权限是否用分配

            2019-11-23  56-rbac组件应用以及补充（三）

        方案一:

            将


        在app01/templates/ 里新建user_list.thml (从rbac中复制同名文件)

        auth_luffy应用：

        auth_luffy\auth_luffy\settings.py

        auth_luffy\auth_luffy\urls.py

        auth_luffy\app01\views\user.py

        auth_luffy\app01\views\account.py

        auth_luffy\app01\views\host.py

        auth_luffy\app01\templates\user_list.html

        auth_luffy\app01\templates\host_list.html

        auth_luffy\app01\templates\index.html

        auth_luffy\app01\templates\login.html

        auth_luffy\app01\forms\user.py

        auth_luffy\app01\forms\host.py

        rbac组件改变的文件：

        auth_luffy\rbac\models.py

        auth_luffy\rbac\urls.py

        auth_luffy\rbac\menu.py

        auth_luffy\rbac\templates\layout.html


        time: 55:38 用户的增，删，改，查 结束

        time: 56: 05 主机表的增，删，改，查 开始

        time: 1:05:04  加回权限和面包屑导航菜单

        time: 1:24:21  权限分配功能的编写 2019-11-16

        time: 1:33:18  权限分配功能的编写 2019-11-16


    4.6  用户登录的逻辑

            写完用户登录逻辑，对于index/，login/，logout/ 三个URL权限是否用分配

            2019-11-23  56-rbac组件应用以及补充（三）

        方案一:

            将 /index/，logout/ 录入数据库，以后给每个用户都分配该权限

        方案二: (推荐)

            默认用户登录后，都能访问 /index/, 和 /login/

            在settings.py 里自动发现 应该排除 /index/, 和 /login/
             AUTO_DISCOVER_EXCLUDE = [
                '/admin/.*',
                '/login/.*',
                '/logout/',
                '/index/',
        ]

          time: 07:19
        auth_luffy\auth_luffy\settings.py

        auth_luffy\rbac\middlewares\rbac.py

        auth_luffy\rbac\templates\layout.html


        注意： WSGIRequest object 其实就是request对象






'''