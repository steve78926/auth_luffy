#-*- coding: utf-8 -*-

from django.shortcuts import render, redirect, HttpResponse
from app01 import models
from app01.forms.host import HostModelForm
from rbac.service.urls import memory_reverse

def host_list(request):
    host_queryset = models.Host.objects.all()
    return render(request, 'host_list.html', {'host_queryset': host_queryset})


def host_add(request):
    if request.method == 'GET':
        form = HostModelForm()
        print('form:', form)
        return render(request, 'rbac/change.html', {'form': form})

    form = HostModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(memory_reverse(request, 'host_list'))      #反向生成    改成 memory_reverse ，去掉rbac:

    return render(request, 'rbac/change.html', {'form': form})   #防止表单没有输入直接点保存报错

def host_edit(request, pk):
    obj = models.Host.objects.filter(id=pk).first()

    if not obj:
        return HttpResponse('主机不存在')

    if request.method == 'GET':
        form = HostModelForm(instance=obj)   #因为有instance=obj ，所以表单中有默认值
        return render(request, 'rbac/change.html', {'form': form})   #访问http://127.0.0.1:8000/rbac/role/edit/1/， 表单中有默认值

    form = HostModelForm(instance=obj, data=request.POST)  #data=request.POST 表示提交过来的数据
    if form.is_valid():
        form.save()
        return redirect(memory_reverse(request, 'host_list'))         #改成 memory_reverse ，去掉rbac:

    return render(request, 'rbac/change.html', {'form': form })    #错误信息的展示 防止表单没有输入直接点保存报错
    ######## 上一行代码不能是redirect(), 必须是render()  ############


def host_del(request, pk):
    origin_url = memory_reverse(request, 'host_list')      # delete.html 中取消按钮跳转 origin_url: /rbac/role/list/    改成 memory_reverse ，去掉rbac:
    print("origin_url:",origin_url)
    if request.method == 'GET':
        return render(request, 'rbac/delete.html',{'cancle':origin_url})   #cancle 作为变量传给前端delete.html页面

    # 当点击delete.html页面的确认按钮时,浏览器向服务器发送了一个post请求，url:http://127.0.0.1:8000/rbac/role/del/7/
    models.Host.objects.filter(id=pk).delete()
    return redirect(origin_url)
