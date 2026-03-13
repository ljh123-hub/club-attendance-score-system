from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Department, Member, AttendanceRecord

class MemberInline(admin.StackedInline):
    model = Member
    can_delete = False
    verbose_name = '成员信息'

class CustomUserAdmin(UserAdmin):
    inlines = [MemberInline]
<<<<<<< HEAD
    list_display = ('username', 'full_name', 'user_type', 'department', 'is_admin')
=======
    list_display = ('username', 'full_name', 'user_type', 'department_list', 'is_admin')
>>>>>>> 03f2d59 (feat: 优化界面风格，实现多部门选择及Tom Select交互)

    def full_name(self, obj):
        return obj.get_full_name() or obj.username
    full_name.short_description = '姓名'

    def user_type(self, obj):
        return obj.member_profile.get_user_type_display() if hasattr(obj, 'member_profile') else '-'
    user_type.short_description = '身份'

<<<<<<< HEAD
    def department(self, obj):
        return obj.member_profile.department.name if hasattr(obj, 'member_profile') and obj.member_profile.department else '-'
    department.short_description = '部门'
=======
    def department_list(self, obj):
        if hasattr(obj, 'member_profile') and obj.member_profile.departments.exists():
            return ', '.join([dept.name for dept in obj.member_profile.departments.all()])
        return '-'
    department_list.short_description = '部门'
>>>>>>> 03f2d59 (feat: 优化界面风格，实现多部门选择及Tom Select交互)

    def is_admin(self, obj):
        return obj.member_profile.is_admin if hasattr(obj, 'member_profile') else False
    is_admin.boolean = True
    is_admin.short_description = '管理员'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
<<<<<<< HEAD
    list_display = ('student_id', 'user', 'user_type', 'department', 'is_admin')
    search_fields = ('student_id', 'user__username')
    list_filter = ('user_type', 'department', 'is_admin')
=======
    list_display = ('student_id', 'user', 'user_type', 'department_list', 'is_admin')
    search_fields = ('student_id', 'user__username')
    list_filter = ('user_type', 'departments', 'is_admin')
    filter_horizontal = ('departments',)  # 方便管理多对多

    def department_list(self, obj):
        return ', '.join([dept.name for dept in obj.departments.all()]) if obj.departments.exists() else '-'
    department_list.short_description = '部门'
>>>>>>> 03f2d59 (feat: 优化界面风格，实现多部门选择及Tom Select交互)

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status')
<<<<<<< HEAD
    list_filter = ('date', 'status', 'student__department')
=======
    list_filter = ('date', 'status', 'student__departments')
>>>>>>> 03f2d59 (feat: 优化界面风格，实现多部门选择及Tom Select交互)
