
#-*- coding:utf-8 -*-

'''
用户表单
'''

from rbac import models
from django import forms
from django.core.exceptions import ValidationError

class UserModelForm(forms.ModelForm):
    confirm_password = forms.CharField(label='确认密码')   #新增确认密码字段

    class Meta:             #从数据库中取字段
        model = models.UserInfo
        fields = ['name', 'email', 'password','confirm_password']   #新增确认密码字段

    #注意：__init__() 是UserModelForm类的初始化方法，注意缩进
    def __init__(self, *args, **kwargs):    #这里的__init__() 是为了给上面4个字段(name, email,....)加上class='form-control'
        super(UserModelForm, self).__init__(*args, **kwargs)

        #统一给ModelForm添加样式
        for name,field in self.fields.items():          #循环遍历上面4个字段，添加class='form-control'
            field.widget.attrs['class'] = 'form-control'


        #手动定义中文错误信息
        # error_messages = {
        #     'name': {'required': '用户名不能为空'},
        #     'email': {'required': '邮箱不能为空'},
        #     'password': {'required': '密码不能为空'},
        #     'confirm_password': {'required': '确认密码不能为空'},
        # }

        #自动中文错误信息：在settings.py 找到LANGUAGE_CODE = 'en-us'  改为 LANGUAGE_CODE = 'zh-hans'

    def clean_confirm_password(self):
        '''
        检测密码是否一致
        :return:
        '''
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']

        if password != confirm_password:
            raise ValidationError('两次密码输入不一致啊')      #密码不一致抛异常
        return confirm_password                 #密码一致返回确认密码

class UpdateUserModelForm(forms.ModelForm):

    class Meta:             #从数据库中取字段
        model = models.UserInfo
        fields = ['name', 'email',]

    #注意：__init__() 是UserModelForm类的初始化方法，注意缩进
    def __init__(self, *args, **kwargs):    #这里的__init__() 是为了给上面4个字段(name, email,....)加上class='form-control'
        super(UpdateUserModelForm, self).__init__(*args, **kwargs)

        #统一给ModelForm添加样式
        for name,field in self.fields.items():          #循环遍历上面4个字段，添加class='form-control'
            field.widget.attrs['class'] = 'form-control'


class ResetPasswordUserModelForm(forms.ModelForm):
    confirm_password = forms.CharField(label='确认密码')   #新增确认密码字段

    class Meta:             #从数据库中取字段
        model = models.UserInfo
        fields = ['password','confirm_password']

    #注意：__init__() 是UserModelForm类的初始化方法，注意缩进
    def __init__(self, *args, **kwargs):    #这里的__init__() 是为了给上面4个字段(name, email,....)加上class='form-control'
        super(ResetPasswordUserModelForm, self).__init__(*args, **kwargs)

        #统一给ModelForm添加样式
        for name,field in self.fields.items():          #循环遍历上面4个字段，添加class='form-control'
            field.widget.attrs['class'] = 'form-control'

    def clean_confirm_password(self):
        '''
        检测密码是否一致
        :return:
        '''
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']

        if password != confirm_password:
            raise ValidationError('两次密码输入不一致啊')      #密码不一致抛异常
        return confirm_password                 #密码一致返回确认密码