#-*- coding: utf-8 -*-

from app01 import models
from django import forms

class HostModelForm(forms.ModelForm):
    class Meta:
        model = models.Host
        fields = "__all__"

    def __init__(self, *args, **kwargs):    #这里的__init__() 是为了给上面4个字段(name, email,....)加上class='form-control'
        super(HostModelForm, self).__init__(*args, **kwargs)

        #统一给ModelForm添加样式
        for name,field in self.fields.items():          #循环遍历上面4个字段，添加class='form-control'
            field.widget.attrs['class'] = 'form-control'