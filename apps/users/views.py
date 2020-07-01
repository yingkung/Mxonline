from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from apps.users.forms import LoginForm, DynamicLoginForm, DynamicLoginPostForm, RegisterGetForm, RegisterPostForm
from apps.users.models import UserProfile
from config.settings import yp_apikey, REDIS_HOST, REDIS_PORT
from apps.utils.random_str import generate_random
from apps.utils.YunPian import send_singal_sms
import json, redis


class RegisterView(View):
    def get(self, request, *args, **kwargs):
        register_get_form = RegisterGetForm()
        return render(request, 'register.html', {'register_get_form': register_get_form})

    def post(self, request, *args, **kwargs):  # 注册接口
        register_post_form = RegisterPostForm()
        if register_post_form.is_valid():
            mobile = register_post_form.cleaned_data['mobile']
            passoword = register_post_form.cleaned_data['password']

            # 新建一个用户
            user = UserProfile(username=mobile)
            user.set_password(passoword)
            user.mobile = mobile
            user.save()
            login(request,user)
            return HttpResponseRedirect(reverse('index'))
        else:  # 如果这个手机号码已经存在，则返回注册页面
            register_get_form = RegisterGetForm()
            return render(request, 'register.html', {'register_get_form': register_get_form}, {'register_post_form': register_post_form})


class DynamicLoginView(View):
    def post(self, request, *args, **kwargs):
        login_form = DynamicLoginPostForm(request.POST)
        dynamic_login = True
        if login_form.is_valid():  # 存在mobile 和 code
            # 没有注册账号依然可以登录
            mobile = login_form.cleaned_data['mobile']
            existed_users = UserProfile.objects.filter(mobile=mobile)
            if existed_users:
                user = existed_users[0]
            else:
                # 将用户添加到数据库
                user = UserProfile(username=mobile)
                password = generate_random(10, 2)
                user.set_password(password)
                user.mobile = mobile
                user.save()
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
            # code是否和redis存储的code一致
        else:  # 如果code不正确，返回login页面
            d_form = DynamicLoginForm()
            return render(request, 'login.html', {'login_form': login_form,
                          'd_form': d_form, 'dynamic_login': dynamic_login})


class SendSmsView(View):
    def post(self, request, *args, **kwargs):
        send_sms_form = DynamicLoginForm(request.POST)
        res_dic = {}
        if send_sms_form.is_valid():
            mobile = send_sms_form.cleaned_data['mobile']
            # code， 随机生成4位数字验证码
            code = generate_random(4, 0)
            res_json = send_singal_sms(yp_apikey, code, mobile)
            if res_json['code'] == 0:
                res_dic['status'] = 'success'
                r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset='utf-8', decode_responses=True)
                r.set(str(mobile), code)
                r.expire(str(mobile), 60*5)  # 设置5分钟过期
            else:
                res_dic['msg'] = res_json['msg']
        else:
            for key, value in send_sms_form.errors.items():
                res_dic[key] = value[0]
        return JsonResponse(res_dic)


#退出登录的处理
class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('index'))


# 定义用户登录功能的类
class LoginView(View):
    # 需要定义get 和post方法
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('index'))
        login_form = DynamicLoginForm()  # 手机动态登录
        return render(request, 'login.html', {'login_form': login_form})

    def post(self, request, *args, **kwargs):
        # 处理用户输入的用户名和密码进行登录
        user_name = request.POST.get('username', '')  # get中的名字是对应元素的name，可以在网页中查看, 也就是html中字段的名字
        password = request.POST.get('password', '')

        # if not user_name:
        #     return render(request, 'login.html', {'msg': '请输入用户名'})
        # if not password:
        #     return render(request, 'login.html', {'msg': '请输入密码'})
        # if len(password) < 3:
        #     return render(request, 'login.html', {'msg': '密码格式不正确'})

        # 代替上面代码的简化写法： 表单验证 django 中提供form验证功能
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # 通过用户和密码查询用户是否存在
            user_name = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']

            user = authenticate(username=user_name, password=password)  # 验证了用户名和密码， 返回User的一个obj

            # ====== 通过数据库进行查询 ====== #
            # from apps.users.models import UserProfile
            # user = UserProfile.objects.get(username = user_name)
            # 上面的这种方式，只查到了用户是否存在，没有比较密码是否正确
            # 但是在数据库中密码都是加密的，如果比较密码，我们需要把获取的密码进行加密，再和数据库中的密码进行比较
            # 这种方式既繁琐，又不利于代码的扩展
            # ================================ #

            if user is not None:
                # 查询到用户
                login(request, user)  # 涉及cookie和session的内容
                # 登录成功之后应该怎么返回页面, 一般跳转到首页
                # return render(request, 'index.html')
                return HttpResponseRedirect(reverse('index'))

            else:
                # 未查到用户
                return render(request, 'login.html', {'msg': '用户名/密码错', 'login_form': login_form})
                # 需要传递是用户名/密码错
        else:
            # return render(request, 'login.html', {'msg': '用户名/密码错'})
            return render(request, 'login.html', {'login_form': login_form})

    # def post(self, request, *args, **kwargs):
    #     login_form = LoginForm(request.POST)
    #     if login_form.is_valid():
    #         user_name = login_form.cleaned_data.get('username')  # 此处的username 和html页面中的元素name一致
    #         password = login_form.cleaned_data.get('password')
    #         user = authenticate(username=user_name, password=password)
    #         if user is not None:  # 用户验证成功
    #             login(request, user_name)
    #             return HttpResponseRedirect(reverse('index'))
    #         else:  # 没有查到此用户， 仍然返回login页面
    #             # return render(request, 'login.html', {'msg': "用户名/密码错", 'login_form': login_form})
    #             return render(request, 'login.html')
    #     else:
    #         # return render(request, 'login.html', {'login_form': login_form})
    #         return render(request, 'login.html')