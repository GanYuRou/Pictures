import json
import datetime

from django.db.models import Q
from django.http import HttpResponse
from .models import UserInfo
from .models import MemeGroupInfo
from .models import MemeGroupRelation
from .models import MemeInfo
from .utils.response_util import ResponseUtil
from .utils.password_util import PasswordUtil
from .utils.code_util import CodeUtil

from django.forms.models import model_to_dict


def index(request):
    return HttpResponse("Hello, world. You're at the pictures index")


def register(request):
    if request.method == 'POST':
        req = json.loads(request.body)
        user_email = req['email']
        user = UserInfo.objects.filter(email=user_email)
        if user:
            return ResponseUtil.response_format('fail', {'message': '此邮箱已存在！'})
        else:
            # 生成唯一的用户id
            user_code = CodeUtil.gen_code('UC')
            # 注册账号时的时间
            time_now = datetime.datetime.now()
            # 将明文密码转为密文
            user_password = req['password']
            hash_pwd = PasswordUtil.password_hash(user_code, user_password, time_now)
            UserInfo.objects.create(code=user_code, password=hash_pwd, email=user_email, created_at=time_now)
            return ResponseUtil.response_format('success', {'message': '注册成功！'})


def login(request):
    if request.method == 'POST':
        req = json.loads(request.body)
        user_email = req['email']
        user = UserInfo.objects.filter(email=user_email)
        if user:
            #  将密码通过md5加密，再与其数据库中存储的密码进行匹配
            user_password = req['password']
            hash_pwd = PasswordUtil.password_hash(user[0].code, user_password, user[0].created_at)
            if user[0].password == hash_pwd:
                return ResponseUtil.response_format('success', {'message': '登录成功！'})
            else:
                return ResponseUtil.response_format('error', {'message': '密码不正确！'})
        else:
            return ResponseUtil.response_format('error', {'message': '用户不存在！'})


def pagination(request):
    if request.method == 'POST':
        req = json.load(request)
        page_number = req['pageNo']
        page_size = req['pageSize']
        left_value = (page_number - 1) * page_size + 1
        right_value = page_number * page_size
        group_lists = MemeGroupInfo.objects.filter(Q(id__gte=left_value) & Q(id__lte=right_value))
        data = []
        for g in group_lists:
            group = MemeGroupRelation.objects.filter(meme_group_code=g.code)
            urls = []
            for m in group:
                meme = MemeInfo.objects.filter(code=m.meme_code)
                for x in meme:
                    urls.append(x.resource_url + x.resource_key)
            data.append({'title': g.name, 'code': g.code, 'urls': urls})
        return ResponseUtil.response_format('success', {'data': data})
