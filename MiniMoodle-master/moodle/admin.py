from django.contrib import admin
from .models import Course,Message,EnrollTime

# Register your models here.

admin.site.register(Course)
admin.site.register(Message)
admin.site.register(EnrollTime)
