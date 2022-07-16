from django.contrib import admin

# Register your models here.
from django.contrib import admin

# MentalPost
from .models import MentalPost


# 注册MentalPost到admin中
admin.site.register(MentalPost)