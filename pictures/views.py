import json
import datetime

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
            data = {'code': user[0].code, 'nick': user[0].nick, 'message': '登录成功！'}
            return ResponseUtil.response_format('success', data)
        else:
            return ResponseUtil.response_format('failure', {'message': '密码不正确！'})
    else:
        return ResponseUtil.response_format('failure', {'message': '用户不存在！'})


# 完善个人信息
def update_information(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    req = json.loads(request.body)
    code, nick, gender, email, birthday = req['code'], req['nick'], req['gender'], req['email'], req['birthday']
    UserInfo.objects.filter(code=code) \
        .update(nick=nick, gender=gender, email=email, birthday=birthday)
    return ResponseUtil.response_format('success', {'message': '修改成功！'})


# 获取完整的用户信息
def all_user_information(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    req = json.loads(request.body)
    code = req['code']
    user = UserInfo.objects.filter(code=code).values('nick', 'email', 'gender', 'birthday')

    return ResponseUtil.response_orm('success', user)


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


def get_meme_title_by_group_codes(star_group_codes):
    meme_groups = MemeGroupInfo.objects \
        .filter(code__in=star_group_codes).all()

    meme_group_title_dict = {}
    for group in meme_groups:
        meme_group_title_dict[group.code] = group.name
    print(meme_group_title_dict)
    return meme_group_title_dict


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


def sort_meme_group(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    records, req = [], json.loads(request.body)
    page_number, page_size = req['pageNo'], req['pageSize']

    meme_sort_page = Paginator(TagInfo.objects.all(), page_size)
    sort_groups = meme_sort_page.page(page_number).object_list
    total_sort_number = meme_sort_page.num_pages

    sort_codes = [sort_group.code for sort_group in sort_groups]
    sort_group_dict = get_meme_group_by_sort_tag(sort_codes)

    for sort_group in sort_groups:
        records.append({
            'name': sort_group.name,
            'groups': sort_group_dict[sort_group.code]
        })

    return ResponseUtil.response_format('success', {'records': records, 'total': total_sort_number})


def get_meme_group_by_sort_tag(meme_sort_codes):
    relations = MemeGroupTagRelation.objects \
        .filter(tag_code__in=meme_sort_codes).all()
    meme_groups = MemeGroupInfo.objects \
        .filter(code__in=[relation.meme_group_code for relation in relations])
    meme_groups_code_dict = {meme_group.code: meme_group for meme_group in meme_groups}

    meme_groups_dict = {}
    for relation in relations:
        if relation.tag_code not in meme_groups_dict.keys():
            meme_groups_dict[relation.tag_code] = []

        group = meme_groups_code_dict[relation.meme_group_code]
        image_dict = get_meme_info_by_group_codes([group.code])
        tag_dict = get_meme_tag_by_group_codes([group.code])

        meme_groups_dict[relation.tag_code].append({
            'code': group.code,
            'title': group.name,
            'images': image_dict[group.code],
            'tags': tag_dict[group.code],
        })
    return meme_groups_dict


# 标签：先拿取前24个，之后在随机
def tags_group(request):
    if request.method != 'GET':
        return ResponseUtil.response_format('failure', None)

    tags = TagInfo.objects.all()[:28]
    records = [{'code': tag.code, 'name': tag.name} for tag in tags]

    return ResponseUtil.response_format('success', {'records': records})


def tag_meme_groups(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    records, req = [], json.loads(request.body)
    code = req['code']

    relations = MemeGroupTagRelation.objects.filter(tag_code=code).all()
    hot_tag_group_codes = [relation.meme_group_code for relation in relations]

    hot_tag_group_title_dict = get_meme_title_by_group_codes(hot_tag_group_codes)
    hot_tag_group_image_dict = get_meme_info_by_group_codes(hot_tag_group_codes)
    hot_tag_group_tag_dict = get_meme_tag_by_group_codes(hot_tag_group_codes)

    for relation in relations:
        records.append({
            'code': relation.meme_group_code,
            'title': hot_tag_group_title_dict[relation.meme_group_code],
            'images': hot_tag_group_image_dict[relation.meme_group_code],
            'tags': hot_tag_group_tag_dict[relation.meme_group_code],
        })

    return ResponseUtil.response_format('success', {'records': records})


# 收藏
def star_by_user(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    records, req = [], json.loads(request.body)
    user_code, meme_group_code = req['userCode'], req['groupCode']
    time_now = datetime.datetime.now()
    UserStarRelation.objects \
        .create(user_code=user_code, meme_group_code=meme_group_code, created_at=time_now)

    return ResponseUtil.response_format('success', {'message': '已收藏！'})


# 是否已收藏
def is_already_star(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    req = json.loads(request.body)
    user_code, meme_group_code = req['userCode'], req['groupCode']
    exist = UserStarRelation.objects \
        .filter(user_code=user_code, meme_group_code=meme_group_code)
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


# 获取收藏列表
def star_meme_group(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    records, req = [], json.loads(request.body)
    user_code = req['code']
    star_groups = UserStarRelation.objects.filter(user_code=user_code)

    star_group_codes = [star_group.meme_group_code for star_group in star_groups]
    meme_group_title_dict = get_meme_title_by_group_codes(star_group_codes)
    meme_group_image_dict = get_meme_info_by_group_codes(star_group_codes)
    meme_group_tag_dict = get_meme_tag_by_group_codes(star_group_codes)

    for star_group in star_groups:
        records.append({
            'code': star_group.meme_group_code,
            'title': meme_group_title_dict[star_group.meme_group_code],
            'images': meme_group_image_dict[star_group.meme_group_code],
            'tags': meme_group_tag_dict[star_group.meme_group_code]
        })

    return ResponseUtil.response_format('success',  {'records': records})


# 发布列表
def upload_meme_group(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    records, req = [], json.loads(request.body)
    user_nick = req['nick']

    upload_groups = MemeGroupInfo.objects.filter(created_by=user_nick).all()
    upload_group_codes = [upload_group.code for upload_group in upload_groups]
    upload_group_img_dict = get_meme_info_by_group_codes(upload_group_codes)
    upload_group_tag_dict = get_meme_tag_by_group_codes(upload_group_codes)

    for upload_group in upload_groups:
        records.append({
            'code': upload_group.code,
            'title': upload_group.name,
            'images': upload_group_img_dict[upload_group.code],
            'tags': upload_group_tag_dict[upload_group.code],
        })

    return ResponseUtil.response_format('success', {'records': records})


# 发布表情包
def upload_group_by_user(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    req = json.loads(request.body)
    name, nick, tag_list, remark, upload = req['title'], req['person'], req['tag'], req['description'], req['upload']
    # 生成唯一code
    group_code = CodeUtil.gen_code('MG')
    # 当前时间
    time_now = datetime.datetime.now()
    MemeGroupInfo.objects \
        .create(code=group_code, name=name, created_at=time_now, created_by=nick, remark=remark, status='VISIBLE')

    for tag in tag_list:
        tag_code = CodeUtil.gen_code('TA')
        TagInfo.objects.create(code=tag_code, name=tag)

        MemeGroupTagRelation.objects.create(meme_group_code=group_code, tag_code=tag_code, created_at=time_now)

    for meme in upload:
        meme_code = CodeUtil.gen_code('MI')
        MemeInfo.objects \
            .create(code=meme_code, img_type=meme['type'], img_md5=meme['md5'], status='VISIBLE', resource_url=meme['url'], resource_key=meme['key'], created_at=time_now, created_by=nick)

        MemeGroupRelation.objects.create(meme_group_code=group_code, meme_code=meme_code, created_at=time_now)

    return ResponseUtil.response_format('success', {'message': '发布成功！'})


def search_meme_groups(request):
    if request.method != 'POST':
        return ResponseUtil.response_format('failure', None)

    req = json.loads(request.body)
    records, keyword = [], req['keyword']

    meme_groups = MemeGroupInfo.objects \
        .filter(name__icontains=keyword).all()

    if meme_groups:
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

        return ResponseUtil.response_format('success', {'records': records})

    return ResponseUtil.response_format('failure', {'message': '无相关表情包'})

