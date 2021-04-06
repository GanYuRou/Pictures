from django.db import models


class UserInfo(models.Model):
    id = models.AutoField(primary_key=True)  # 自增主键
    code = models.CharField(max_length=32, null=True)  # 用户唯一标识
    password = models.CharField(max_length=256, null=True)  # 密码
    email = models.CharField(max_length=128, null=True)  # 邮箱
    nick = models.CharField(max_length=32, null=True)  # 昵称
    meme_code = models.CharField(max_length=32, null=True)  # 头像 ID
    remark = models.TextField(null=True)  # 简介
    active = models.BooleanField(null=True)  # 账号正常/注销
    gender = models.CharField(max_length=2, null=True)  # 性别
    birthday = models.DateTimeField(null=True)  # 生日
    created_at = models.DateTimeField(null=True)  # 创建时间
    updated_at = models.DateTimeField(null=True)  # 修改时间

    class Meta:
        db_table = 'user_info'


class MemeInfo(models.Model):
    id = models.AutoField(primary_key=True)  # 自增主键
    code = models.CharField(max_length=32, null=True)  # 表情唯一标识
    name = models.CharField(max_length=64, null=True)  # 表情名称
    remark = models.TextField(null=True)  # 表情描述
    img_type = models.CharField(max_length=16, null=True)  # 图片类型
    img_md5 = models.CharField(max_length=32, null=True)  # 图片 md5
    status = models.CharField(max_length=16, null=True)  # 状态 DELETE, VISIBLE, HIDDEN
    resource_url = models.TextField(null=True)  # 图片地址前缀
    resource_key = models.TextField(null=True)  # 图片远程 ID
    created_at = models.DateTimeField(null=True)  # 创建时间
    created_by = models.CharField(max_length=32, null=True)  # 创建人
    update_at = models.DateTimeField(null=True)  # 修改时间
    updated_by = models.CharField(max_length=32, null=True)  # 修改人

    class Meta:
        db_table = 'meme_info'


class MemeGroupInfo(models.Model):
    id = models.AutoField(primary_key=True)  # 自增主键
    code = models.CharField(max_length=32, null=True)  # 表情组唯一标识
    name = models.CharField(max_length=256, null=True)  # 表情组名称
    remark = models.TextField(null=True)  # 表情组描述
    hot = models.BooleanField(null=True)  # 是否热门
    status = models.CharField(max_length=16, null=True)  # 状态 DELETE, VISIBLE, HIDDEN
    created_at = models.DateTimeField(null=True)  # 创建时间
    created_by = models.CharField(max_length=32, null=True)  # 创建人
    update_at = models.DateTimeField(null=True)  # 修改时间
    updated_by = models.CharField(max_length=32, null=True)  # 修改人

    class Meta:
        db_table = 'meme_group_info'


class TagInfo(models.Model):
    id = models.AutoField(primary_key=True)  # 自增主键
    code = models.CharField(max_length=32, null=True)  # 标签唯一标识
    name = models.CharField(max_length=64, null=True)  # 标签名称
    remark = models.TextField(null=True)  # 标签描述

    class Meta:
        db_table = 'tag_info'


class MemeGroupRelation(models.Model):
    id = models.AutoField(primary_key=True)  # 自增主键
    meme_group_code = models.CharField(max_length=32, null=True)
    meme_code = models.CharField(max_length=32, null=True)
    created_at = models.DateTimeField(null=True)  # 创建时间

    class Meta:
        db_table = 'meme_group_relation'


class MemeGroupTagRelation(models.Model):
    id = models.AutoField(primary_key=True)  # 自增主键
    meme_group_code = models.CharField(max_length=32, null=True)
    tag_code = models.CharField(max_length=32, null=True)
    created_at = models.DateTimeField(null=True)  # 创建时间

    class Meta:
        db_table = 'meme_group_tag_relation'


class UserStarRelation(models.Model):
    id = models.AutoField(primary_key=True)
    user_code = models.CharField(max_length=32, null=True)
    meme_group_code = models.CharField(max_length=32, null=True)
    created_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'user_star_relation'
