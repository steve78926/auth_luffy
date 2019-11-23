#-*- coding:utf-8-*-

import re
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse
from django.conf import settings


class RbacMiddleware(MiddlewareMixin):
    '''
    用户权限信息校验
    #中间件不应该写在web应用中
    '''

    def process_request(self, request):
        '''
        当用户请求进入时触发执行
        :param request:
        :return:
        '''
        """
        1. 获取当前用户请求的URL
        2. 获取当前用户在session中保存的权限列表 ['/customer/list', '/customer/list/(?P<cid>\\d+)/']
        3. 权限信息匹配
       """
        # http://127.0.0.1:8000/customer/list/         path_info:  /customer/list/
        # http://127.0.0.1:8000/customer/list/?age=10  path_info同样是:  /customer/list/

        current_url = request.path_info
        for valid_url in settings.VALID_URL_LIST:       # settings.VALID_URL_LIST 是不受限权控制的白名单
            if re.match(valid_url, current_url):        #白名单中的URL无需权限验证即可访问
                return None     # 返回None 中间件不拦截，继续执行后面的视图


        #这里用get()，而不是[]获取字典的key对应的vlaue, 因为用户没有登录时，session为空，get()不会报错
        #permission_list = request.session.get(settings.PERMISSION_SESSION_KEY)
        permission_dict = request.session.get(settings.PERMISSION_SESSION_KEY)

        # if not permission_list:
        if not permission_dict:
            return HttpResponse('未获取到用户权限信息，请重新登录！')

        flag = False        #flat = False 表示未匹配成功
        url_record = [
            {'title': '首页', 'url': '#'}
        ]
        #for item in permission_list:
        for item in permission_dict.values():
            reg = "^%s$" % item['url']                # 给url 加起始符，终止符，精确匹配
            if re.match(reg, current_url):    #不能用current_url == url 因为reg变量中有正则表达式
                flag = True
                #将item['pid'] 或者 item['id']值赋给 request.current_selected_permission, 方便inclusision_tag 获取该值
                request.current_selected_permission = item['pid'] or item['id']        #如果item['pid'] 为真，返回item['pid']的值，否则返回item['id'] 的值
                #如果item['pid']为空，说明这个权限是菜单，否则这个权限只是个普通权限不能做菜单， item['id']是表的主键，肯定不为空，请参照 rbac_permission表
                #request.current_selected_permission在本例中只有两个值，1，或者7
                if not item['pid']:
                    url_record.extend([{'title': item['title'], 'url': item['url'], 'class':'active'}])
                else:
                    url_record.extend([
                        {'title': item['p_title'], 'url': item['p_url']},
                        {'title': item['title'], 'url': item['url'],'class':'active'},
                    ])
                request.breadcrumb = url_record
                print(request.breadcrumb)
                break


        print("flag:", flag)

        #中间件process_request() 如果有返回值，则不会走到视图，而是直接返回
        if not flag:      #如果flag=False, 则not flag = True, 无权访问， 如果flag=True, 则not flag = False, 继续向后执行
            return HttpResponse("无权访问")    #test