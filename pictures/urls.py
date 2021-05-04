from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('save', views.update_information, name='save'),
    path('acquire', views.all_user_information, name='acquire'),
    path('group', views.page_meme_groups, name='group'),
    path('tags', views.tags_group, name='tags'),
    path('tag-detail', views.tag_meme_groups, name='tag-detail'),
    path('hot', views.hot_meme_page, name='hot'),
    path('sort', views.sort_meme_group, name='sort'),
    path('star', views.star_by_user, name='star'),
    path('exist', views.is_already_star, name='exist'),
    path('cancel', views.cancel_star_by_user, name='cancel'),
    path('star-list', views.star_meme_group, name='star-list'),
    path('upload-list', views.upload_meme_group, name='upload-list'),
    path('upload', views.upload_group_by_user, name='upload'),
    path('search', views.search_meme_groups, name='search')
]
