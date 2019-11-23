
#-*- coding: utf8-*-

from django.urls import reverse
from django.http import QueryDict

def memory_url(request, name, *args, **kwargs):
    '''
    生成带有原搜索条件的URL（替代了模板中的URL）
    :param request: 例如： <WSGIRequest: GET '/rbac/menu/list/?mid=3'>
    :param name:  例如："rbac:menu_add"
    :return:    /menu/add/?_filter="mid=2&age=99", 在 luffy_permission\rbac\templates\rbac\menu_list.html 中调用memory_url
    '''
    print('request.GET:',request.GET)       #<QueryDict: {'mid': ['3']}>
    basic_url = reverse(name, args=args, kwargs=kwargs)
    if not request.GET:            #如果request.GET 返回None 表示当前URL中无参数
        return basic_url

    #old_params = request.GET.urlencode()         # 例如：mid=3&age=100&name=steve
    #tpl = "%s?_filter=%s" % (basic_url, old_params)   # 这是拼接好的效果 /menu/add/?_filter=mid=2&age=99  参数没有打包

    query_dict = QueryDict(mutable=True)    #实例化QueryDict() 目的是打包URL参数
    query_dict['_filter'] = request.GET.urlencode()     # 将request.GET参数如：mid=2&age=99 进行urlencode()编码后，存储到query_dict['_filter']
    print("query_dict:",query_dict.urlencode())

    return "%s?%s" % (basic_url, query_dict.urlencode())    #这是拼接好的效果 /menu/add/?_filter="mid=2&age=99", 把参数打包

    #浏览器地址栏的效果：/rbac/menu/add/?_filter=mid%3D3

def memory_reverse(request, name, *args, **kwargs):
    '''
    反向生成URL: 把原来的搜索条件
        http://127.0.0.1:8000/rbac/menu/add/?_filter=mid%3D5
        1。 在url中将原来的搜索条件或

        2. reverse 生成原来的URL， 如/menu/list
        3. /menu/add/?_filter=mid%3D5
    :param request:
    :param name:  如：'rbac:menu_list'
    :param args:
    :param kwargs:
    :return:    #/rbac/menu/list/?mid=3
    '''

    url = reverse(name, args=args, kwargs=kwargs)       #反向生成
    origin_params = request.GET.get('_filter')          #带上原搜索条件参数
    if origin_params:
        url = "%s?%s" % (url, origin_params)            #/rbac/menu/list/?mid=3
    print("memory_reserver_url:",url)
    return url