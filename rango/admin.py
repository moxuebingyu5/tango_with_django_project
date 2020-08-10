from django.contrib import admin
from rango.models import Category, Page, UserProfile

# 添加这个类，定制管理界面
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(Page)
admin.site.register(UserProfile)
