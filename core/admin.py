from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Student, Teacher, AttendanceRecord


class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = '学生信息'


class TeacherInline(admin.StackedInline):
    model = Teacher
    can_delete = False
    verbose_name_plural = '教师信息'


class CustomUserAdmin(UserAdmin):
    inlines = [StudentInline, TeacherInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')

    def get_role(self, obj):
        if hasattr(obj, 'student_profile'):
            return '学生'
        elif hasattr(obj, 'teacher_profile'):
            return '教师'
        else:
            return '管理员'

    get_role.short_description = '角色'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'user', 'class_name', 'phone')
    search_fields = ('student_id', 'user__username', 'user__first_name')
    list_filter = ('class_name',)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher_id', 'user', 'department', 'title')
    search_fields = ('teacher_id', 'user__username')


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status')
    list_filter = ('date', 'status')
    date_hierarchy = 'date'