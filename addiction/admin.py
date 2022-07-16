from django.contrib import admin

# 别忘了导入AddictionrPost
from .models import AddictionPost


# 注册AddictionPost到admin中
admin.site.register(AddictionPost)