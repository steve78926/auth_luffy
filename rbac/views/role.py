#-*- coding:utf-8 -*-

'''
角色管理
'''

from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from rbac import models
from rbac.forms.role import RoleModelForm

def role_list(request):
    '''
    角色列表
    :param request:
    :return:
    '''
    role_queryset = models.Role.objects.all()
    return render(request, 'rbac/role_list.html', {'roles': role_queryset})  #role_list.html 在luffy_permission\rbac\templates\rbac 下

def role_add(request):
    '''
    添加角色
    :param request:
    :return:
    '''
    if request.method == 'GET':
        form = RoleModelForm()
        print('form:', form)
        return render(request, 'rbac/change.html', {'form': form})

    form = RoleModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(reverse('rbac:role_list'))      #反向生成

    return render(request, 'rbac/change.html', {'form': form})   #防止表单没有输入直接点保存报错

def role_edit(request, pk):
    '''
    编辑角色
    此处重点：role_add, 与role_edit 显示的表单是一样的，唯一不同的是，role_add 页面表单不显示默认值，role_edit页面表单
    显示默认值，因此，两个视频函数，添加role_add, 编辑role_edit 渲染时使用同一个页面文件role_add.html
    :param request:
    :param pk: 要修改的角色id
    :return:
    '''
    obj = models.Role.objects.filter(id=pk).first()
    if not obj:
        return HttpResponse('角色不存在')

    if request.method == 'GET':
        form = RoleModelForm(instance=obj)   #因为有instance=obj ，所以表单中有默认值
        return render(request, 'rbac/change.html', {'form': form})   #访问http://127.0.0.1:8000/rbac/role/edit/1/， 表单中有默认值

    form = RoleModelForm(instance=obj, data=request.POST)  #data=request.POST 表示提交过来的数据
    if form.is_valid():
        form.save()
        return redirect(reverse('rbac:role_list'))

    return render(request, 'rbac/change.html', {'form': form })    #错误信息的展示 防止表单没有输入直接点保存报错
    ######## 上一行代码不能是redirect(), 必须是render()  ############

def role_del(request, pk):
    '''
    删除角色
    :param request:
    :param pk:
    :return:
    '''

    origin_url = reverse('rbac:role_list')      # delete.html 中取消按钮跳转 origin_url: /rbac/role/list/
    print("origin_url:",origin_url)
    if request.method == 'GET':
        return render(request, 'rbac/delete.html',{'cancle':origin_url})   #cancle 作为变量传给前端delete.html页面

    # 当点击delete.html页面的确认按钮时,浏览器向服务器发送了一个post请求，url:http://127.0.0.1:8000/rbac/role/del/7/
    models.Role.objects.filter(id=pk).delete()
    return redirect(origin_url)
