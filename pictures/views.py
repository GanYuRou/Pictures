import json
import datetime

# from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import MemeInfo, MemeGroupRelation, MemeGroupTagRelation, \
    MemeGroupInfo, UserInfo, TagInfo, UserStarRelation
from .utils.response_util import ResponseUtil
from .utils.password_util import PasswordUtil
from .utils.code_util import CodeUtil

# backup: http://aston.zapto.org:28500/resource/


def register(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    req = json.loads(request.body)
    user_email = req['email']
    user = UserInfo.objects.filter(email=user_email)
    if user:
        return ResponseUtil.response_format('failure', {'message': '此邮箱已存在！'})
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
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    req = json.loads(request.body)
    req_user_email = req['email']
    user = UserInfo.objects.filter(email=req_user_email)
    if user:
        #  将密码通过md5加密，再与其数据库中存储的密码进行匹配
        user_password = req['password']
        hash_pwd = PasswordUtil.password_hash(user[0].code, user_password, user[0].created_at)
        if user[0].password == hash_pwd:
            return ResponseUtil.response_format('success', {'code': user[0].code, 'message': '登录成功！'})
        else:
            return ResponseUtil.response_format('failure', {'message': '密码不正确！'})
    else:
        return ResponseUtil.response_format('failure', {'message': '用户不存在！'})


# 完善自我信息
def update_information(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    req = json.loads(request.body)
    code, name, sex, email, birthday = req['code'], req['username'], req['sex'], req['email'], req['birthday']
    UserInfo.objects.filter(code=code) \
        .update(nick=name, gender=sex, email=email, birthday=birthday)
    return ResponseUtil.response_format('success', {'message': '修改成功！'})


# 获取完整的用户信息
def all_user_information(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    req = json.loads(request.body)
    code = req['code']
    user = UserInfo.objects.filter(code=code).values('nick', 'email', 'gender', 'birthday')
    return JsonResponse(user, json_dumps_params={"ensure_ascii": False})


def page_meme_groups(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    records, req = [], json.loads(request.body)
    page_number, page_size = req['pageNo'], req['pageSize']

    # 分页
    meme_groups_page = Paginator(MemeGroupInfo.objects.all(), page_size)
    meme_groups = meme_groups_page.page(page_number).object_list
    total_page_number = meme_groups_page.num_pages

    # 获取图片的 url 和 tag
    meme_group_codes = [meme_group.code for meme_group in meme_groups]
    meme_group_image_dict = get_meme_info_by_group_codes(meme_group_codes)
    meme_group_tag_dict = get_meme_tag_by_group_codes(meme_group_codes)

    for meme_group in meme_groups:
        records.append({
            'code': meme_group.code,
            'title': meme_group.name,
            'images': meme_group_image_dict[meme_group.code],
            'tags': meme_group_tag_dict[meme_group.code]
        })

    return ResponseUtil.response_format('success', {'records': records, 'total': total_page_number})


def get_meme_info_by_group_codes(meme_group_codes):
    relations = MemeGroupRelation.objects \
        .filter(meme_group_code__in=meme_group_codes).all()
    meme_group_images = MemeInfo.objects \
        .filter(code__in=[relation.meme_code for relation in relations]).all()
    meme_image_dict = {image.code: image for image in meme_group_images}

    meme_group_image_dict = {}
    for relation in relations:
        if relation.meme_group_code not in meme_group_image_dict.keys():
            meme_group_image_dict[relation.meme_group_code] = []

        meme_image = meme_image_dict[relation.meme_code]
        meme_group_image_dict[relation.meme_group_code] \
            .append({
                'code': meme_image.code,
                'name': meme_image.name,
                'url': 'http://aston.zapto.org:28500/resource/' + meme_image.resource_key})
    return meme_group_image_dict


def get_meme_tag_by_group_codes(meme_group_codes):
    relations = MemeGroupTagRelation.objects \
        .filter(meme_group_code__in=meme_group_codes).all()
    meme_group_tags = TagInfo.objects \
        .filter(code__in=[relation.tag_code for relation in relations]).all()
    meme_tag_dict = {tag.code: tag for tag in meme_group_tags}

    meme_group_tag_dict = {}
    for relation in relations:
        if relation.meme_group_code not in meme_group_tag_dict.keys():
            meme_group_tag_dict[relation.meme_group_code] = []

        tag_info = meme_tag_dict[relation.tag_code]
        meme_group_tag_dict[relation.meme_group_code] \
            .append({
                'code': tag_info.code,
                'name': tag_info.name})
    return meme_group_tag_dict


def hot_meme_page(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    records, req = [], json.loads(request.body)
    page_number, page_size = req['pageNo'], req['pageSize']

    # 分页
    meme_hot_groups_page = Paginator(MemeGroupInfo.objects.filter(hot=1), page_size)
    meme_hot_groups = meme_hot_groups_page.page(page_number).object_list
    total_page_number = meme_hot_groups_page.num_pages

    # 获取图片的 url 和 tag
    meme_group_hot_codes = [meme_hot_group.code for meme_hot_group in meme_hot_groups]

    meme_group_image_dict = get_meme_info_by_group_codes(meme_group_hot_codes)
    meme_group_tag_dict = get_meme_tag_by_group_codes(meme_group_hot_codes)

    for meme_hot_group in meme_hot_groups:
        records.append({
            'code': meme_hot_group.code,
            'title': meme_hot_group.name,
            'images': meme_group_image_dict[meme_hot_group.code],
            'tags': meme_group_tag_dict[meme_hot_group.code]
        })

    return ResponseUtil.response_format('success', {'records': records, 'total': total_page_number})


# 分类
def sort_tag_groups(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    records, req = [], json.loads(request.body)
    page_number, page_size = req['pageNo'], req['pageSize']

    meme_sort_page = Paginator(TagInfo.objects.all(), page_size)
    meme_sort_groups = meme_sort_page.page(page_size).object_list


# 标签：先拿取前24个，之后在随机
def tags_group(request):
    if request.method != 'GET':
        return ResponseUtil.response_format('failure', None)

    tags = TagInfo.objects.all()[:28]
    records = [{'code': tag.code, 'name': tag.name} for tag in tags]
    return ResponseUtil.response_format('success', {'records': records})


# 收藏
def star_by_user(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    records, req = [], json.loads(request.body)
    user_code, meme_group_code = req['userCode'], req['groupCode']
    time_now = datetime.datetime.now()
    UserStarRelation.objects.create(user_code=user_code, meme_group_code=meme_group_code, created_at=time_now)
    return ResponseUtil.response_format('success', {'message': '已收藏！'})


# 是否已收藏
def is_already_star(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    req = json.loads(request.body)
    user_code, meme_group_code = req['userCode'], req['groupCode']
    exist = UserStarRelation.objects.filter(user_code=user_code, meme_group_code=meme_group_code)
    if exist:
        return ResponseUtil.response_format('success', {'exist': True})

    return ResponseUtil.response_format('success', {'exist': False})


# 取消收藏
def cancel_star_by_user(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    req = json.loads(request.body)
    user_code, meme_group_code = req['userCode'], req['groupCode']
    UserStarRelation.objects \
        .filter(user_code=user_code, meme_group_code=meme_group_code).delete()
    return ResponseUtil.response_format('success', {'message': '已取消！'})


def upload_group(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    req = json.loads(request.body)

