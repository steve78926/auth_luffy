
#-*- coding:utf-8 -*-

'''
角色表单
'''

from rbac import models
from django import forms

class RoleModelForm(forms.ModelForm):
    class Meta:
        model = models.Role
        fields = ['title',]   #只对角色表操作，角色表只有一个列, title
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'})       #修改表单的样式
        }
