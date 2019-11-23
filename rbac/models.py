from django.db import models

# Create your models here.

class Menu(models.Model):
    '''
    菜单表
    '''
    title = models.CharField(verbose_name='一级菜单名称', max_length=32)
    icon = models.CharField(verbose_name='图标', max_length=32)       # 去掉null=True，blank=True 表示图标不允许为空

    def __str__(self):
        return self.title


class Permission(models.Model):
    '''
    权限表
    '''

    title = models.CharField(verbose_name='权限名称', max_length=64)
    url = models.CharField(verbose_name='含正则的URL', max_length=128)

    ######################   一级菜单列   ######################
    # is_menu = models.BooleanField(verbose_name='是否可以做菜单', default=False)
    # #null=True 表示数据库中该字段可为空，blank=True 表示django admin中可以为空
    # icon = models.CharField(verbose_name='图标', max_length=32, null=True, blank=True)

    ######################   二级菜单列   ######################

    name = models.CharField(verbose_name='URL别名', max_length=32,unique=True)
    menu = models.ForeignKey(verbose_name='所属菜单',
                             to='Menu',
                             null=True,
                             blank=True,
                             help_text='null表示不是菜单; 非null表示是二级菜单',
                             on_delete=models.CASCADE)

    pid = models.ForeignKey(verbose_name='关联的权限',
                            to='Permission',
                            null=True,
                            blank=True,
                            related_name='parents',  #反向自关联时可能出点问题，因此要加上related_name(不明白)
                            help_text='对于非菜单权限需要选择一个可以成为菜单的权限，用户做默认展开和选中菜单',
                            on_delete=models.CASCADE)


class Role(models.Model):
    '''
    角色表
    '''
    title = models.CharField(verbose_name='角色名称', max_length=32)
    permissions = models.ManyToManyField(verbose_name='关联的权限',to='Permission',blank=True)

    def __str__(self):
        return self.title

    def __str__(self):
        return self.title


class UserInfo(models.Model):
    '''
    用户表
    '''
    name = models.CharField(verbose_name='用户名',max_length=32)
    password = models.CharField(verbose_name='密码', max_length=32)
    email = models.EmailField(verbose_name='邮箱', max_length=32)
    roles = models.ManyToManyField(verbose_name='关联的角色', to=Role, blank=True)   #严重提醒：to=Role 不能加引号

    def __str__(self):
        return self.name

    class Meta:
        #abstract = True 表示 django以后再做数据库迁移时，不再为UserInfo类创建相关的表以及表结构了。
        # 同时，也不会生成用户表与角色表的关系表
        # 而此类可以当做"父类"，被其他Model类继承。目的：让业务应用的用户表继承rbac的用户表
        abstract = True

    '''
    current_user = models.UserInfo.objects.filter(name=user, password=pwd).first()
    #下面一句代码获取当前用户所拥有的所有权限 , 他使用了跨表查询：UserInfo_role--->Role_permissins----->Permission_id, Permission_url
    permission_list = current_user.roles.filter(permissions__isnull=False).values(permissions__id, permissions__url).distinct()

    #所有下面的描述注释都是为了说明如何获取权限列表，即上面的一行代码

    #问题一：
        1. 一个用户是否可以拥有多个角色？ 是
        2. 一个角色 是否可以拥有多个权限？ 是

        #当一个用户拥有3个角色时，必然有URL重复，distinct() 用于去重复URL

        CEO:
            /index
            /order

        总监：
            /index/
            /customer

        销售：
            /user/
            /add_user

        金牌讲师：


    #问题二：
        CEO:
        总监：
        销售：
        金牌讲师：

        角色和权限关系表：
            CEO: /index
            总监：/order

        用户和角色关系表；
           1 1
           1 1
           1 1

        用户表：
            wupeiqi

        总监：/index/
        总监：/customer
        销售：/user
        销售： /add_user
        金牌讲师：null

    '''

