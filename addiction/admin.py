from django.contrib import admin

# 别忘了导入AddictionrPost
from .models import AddictionPost, AddictionColumn


# 注册AddictionPost到admin中
admin.site.register(AddictionPost)

# 注册文章栏目
admin.site.register(AddictionColumn)