from django.urls import path
# 引入views.py
from . import views

app_name = 'mental'

urlpatterns = [
    # 文章列表
    path('mental-list/', views.mental_list, name='mental_list'),
    # 文章详情
    path('mental-detail/<int:id>/', views.mental_detail, name='mental_detail'),
    # 写文章
    path('mental-create/', views.mental_create, name='mental_create'),
    # 删除文章
    path('mental-delete/<int:id>/', views.mental_delete, name='mental_delete'),
    # 安全删除文章
    path('mental-safe-delete/<int:id>/', views.mental_safe_delete, name='mental_safe_delete'),
    # 更新文章
    path('mental-update/<int:id>/', views.mental_update, name='mental_update'),
    # 点赞 +1
    path('increase-likes/<int:id>/', views.IncreaseLikesView.as_view(), name='increase_likes'),

    # 列表类视图
    path('list-view/', views.MentalListView.as_view(), name='list_view'),
    # 详情类视图
    path('detail-view/<int:pk>/', views.MentalDetailView.as_view(), name='detail_view'),
    # 创建类视图
    path('create-view/', views.MentalCreateView.as_view(), name='create_view'),
]