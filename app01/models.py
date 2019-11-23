from django.db import models
from rbac.models import UserInfo as RbacUserInfo


class Department(models.Model):
    """
    部门表
    """
    title = models.CharField(verbose_name='部门', max_length=32)

    def __str__(self):
        return self.title


class UserInfo(RbacUserInfo):       #从父类rbac/UserInfo 类中继承所有字段，原rbac中的字段转移动业务用户表中
    """
    用户表, RBAC组件里也有用户表
    用户管理功能写在业务功能中，不要用RBAC组件里用户管理
    """
    #user = models.OneToOneField(verbose_name='用户', to=RbacUserInfo)     #业务系统的用户表与RBAC的用户表创建一对一的关系
    phone = models.CharField(verbose_name='联系方式', max_length=32)
    level_choices = (
        (1, 'T1'),
        (2, 'T2'),
        (3, 'T3'),
    )
    level = models.IntegerField(verbose_name='级别', choices=level_choices)

    depart = models.ForeignKey(verbose_name='部门', to='Department', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.name               # self.user.name ??

class Host(models.Model):
    '''
    主机表
    '''
    hostname = models.CharField(verbose_name='主机名', max_length=32)
    ip = models.GenericIPAddressField(verbose_name='IP', protocol='both')   # protocol='both' 表示支持IPV4, IPV6
    depart = models.ForeignKey(verbose_name='归属部门', to=Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.hostname
