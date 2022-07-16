from django.urls import path
# 引入views.py
from . import views

app_name = 'addiction'

urlpatterns = [
    # 文章列表
    path('addiction-list/', views.addiction_list, name='addiction_list'),
    # 文章详情
    path('addiction-detail/<int:id>/', views.addiction_detail, name='addiction_detail'),
    # 写文章
    path('addiction-create/', views.addiction_create, name='addiction_create'),
    # 删除文章
    path('addiction-delete/<int:id>/', views.addiction_delete, name='addiction_delete'),
    # 安全删除文章
    path('addiction-safe-delete/<int:id>/', views.addiction_safe_delete, name='addiction_safe_delete'),
    # 更新文章
    path('addiction-update/<int:id>/', views.addiction_update, name='addiction_update'),
    # 点赞 +1
    path('increase-likes/<int:id>/', views.IncreaseLikesView.as_view(), name='increase_likes'),

    # 列表类视图
    path('list-view/', views.AddictionListView.as_view(), name='list_view'),
    # 详情类视图
    path('detail-view/<int:pk>/', views.AddictionDetailView.as_view(), name='detail_view'),
    # 创建类视图
    path('create-view/', views.AddictionCreateView.as_view(), name='create_view'),
]