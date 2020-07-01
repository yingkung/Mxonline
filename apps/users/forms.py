from django import forms
from captcha.fields import CaptchaField
import redis
from config.settings import REDIS_PORT, REDIS_HOST
from apps.users.models import UserProfile


class RegisterGetForm(forms.Form):
    # 展示register页面
    captcha = CaptchaField()


class RegisterPostForm(forms.Form):
    mobile = forms.CharField(required=True, max_length=11, min_length=11)
    code = forms.CharField(required=True, max_length=4, min_length=4)
    password = forms.CharField(required=True)

    def clean_mobile(self):
        # 验证手机号码是否已经注册
        mobile = self.data.get('mobile')
        users = UserProfile.objects.filter(mobile=mobile)
        if users:
            raise forms.ValidationError('手机号码已注册')
        return mobile

    def clean_code(self):
        # 判断填写的验证码是否正确
        mobile = self.data.get('mobile')
        code = self.data.get('code')
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset='utf-8', decode_responses=True)
        redis_code = r.get(str(mobile))
        if redis_code != code:  # 如果输入的验证码和保存在redis中的验证码不符
            raise forms.ValidationError('验证码不正确')
        return code


class LoginForm(forms.Form):
    # 定义这个表单类中有哪些字段需要验证， 和model中的定义相似
    username = forms.CharField(required=True, min_length=2)
    password = forms.CharField(required=True, min_length=3)
    # 字段的名称必须和html中字段的name一致


class DynamicLoginForm(forms.Form):
    captcha = CaptchaField()
    mobile = forms.CharField(required=True, max_length=11, min_length=11)


class DynamicLoginPostForm(forms.Form):
    mobile = forms.CharField(required=True, max_length=11, min_length=11)
    code = forms.CharField(required=True, max_length=4, min_length=4)

    def clean_code(self):
        # 判断填写的验证码是否正确
        mobile = self.data.get('mobile')
        code = self.data.get('code')
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset='utf-8', decode_responses=True)
        redis_code = r.get(str(mobile))
        if redis_code != code:  # 如果输入的验证码和保存在redis中的验证码不符
            raise forms.ValidationError('验证码不正确')
        return self.cleaned_data

    # def clean(self):
    #     # 判断填写的验证码是否正确
    #     mobile = self.data.get('mobile')
    #     code = self.data.get('code')
    #     r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset='utf-8', decode_responses=True)
    #     redis_code = r.get(str(mobile))
    #     if redis_code != code:  # 如果输入的验证码和保存在redis中的验证码不符
    #         raise forms.ValidationError('验证码不正确')
    #     return self.cleaned_data
