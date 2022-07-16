from django.contrib import admin
# 记得引入include
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

import notifications.urls

from addiction.views import addiction_list
from . import views


# 存放了映射关系的列表
urlpatterns = [
    path('admin/', admin.site.urls),
    # home
    path('', views.get_homepage, name='home'),
    # 重置密码app
    path('password-reset/', include('password_reset.urls')),
    # 新增代码，配置app的url
    path('addiction/', include('addiction.urls', namespace='addiction')),
    # 新增代码，配置app的url
    path('mental/', include('mental.urls', namespace='mental')),
    # 用户管理
    path('userprofile/', include('userprofile.urls', namespace='userprofile')),
    # comment_addiction
    path('comment_addiction/', include('comment_addiction.urls', namespace='comment_addiction')),
    # comment_mental
    path('comment_mental/', include('comment_mental.urls', namespace='comment_mental')),
    # djang-notifications
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
    # notice
    path('notice/', include('notice.urls', namespace='notice')),
    # django-allauth
    path('accounts/', include('allauth.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
