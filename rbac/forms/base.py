#-*- coding:utf8-*-

from django import forms

class BootStrapModelForm(forms.ModelForm):
    '''
    优化表单样式代码
    '''

    def __init__(self, *args, **kwargs):    #这里的__init__() 是为了给上面4个字段(name, email,....)加上class='form-control'
        super(BootStrapModelForm, self).__init__(*args, **kwargs)
        #统一给ModelForm添加样式
        for name,field in self.fields.items():          #循环遍历上面4个字段，添加class='form-control'
            field.widget.attrs['class'] = 'form-control'