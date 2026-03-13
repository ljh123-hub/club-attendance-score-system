from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Department, Member, AttendanceRecord
import csv
import io

class MemberInline(admin.StackedInline):
    model = Member
    can_delete = False
    verbose_name = '成员信息'

class CustomUserAdmin(UserAdmin):
    inlines = [MemberInline]
    list_display = ('username', 'full_name', 'user_type', 'department_list', 'is_admin')

    def full_name(self, obj):
        return obj.get_full_name() or obj.username
    full_name.short_description = '姓名'

    def user_type(self, obj):
        return obj.member_profile.get_user_type_display() if hasattr(obj, 'member_profile') else '-'
    user_type.short_description = '身份'

    def department_list(self, obj):
        if hasattr(obj, 'member_profile') and obj.member_profile.departments.exists():
            return ', '.join([dept.name for dept in obj.member_profile.departments.all()])
        return '-'
    department_list.short_description = '部门'

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
    list_display = ('student_id', 'user', 'user_type', 'department_list', 'is_admin')
    search_fields = ('student_id', 'user__username')
    list_filter = ('user_type', 'departments', 'is_admin')
    filter_horizontal = ('departments',)

    def department_list(self, obj):
        return ', '.join([dept.name for dept in obj.departments.all()]) if obj.departments.exists() else '-'
    department_list.short_description = '部门'

    # ----- 自定义批量导入功能 -----
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import/', self.import_members, name='core_member_import'),
        ]
        return custom_urls + urls

    def import_members(self, request):
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            if not csv_file:
                self.message_user(request, '请选择一个CSV文件', level='ERROR')
                return redirect('..')

            # 解码文件内容
            decoded_file = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            # 必填字段检查
            required_fields = ['学号', '姓名']
            if not all(field in reader.fieldnames for field in required_fields):
                self.message_user(request, 'CSV必须包含“学号”和“姓名”列', level='ERROR')
                return redirect('..')

            success_count = 0
            error_lines = []

            for row_num, row in enumerate(reader, start=2):  # 从第2行开始计数（第1行是标题）
                student_id = row.get('学号', '').strip()
                full_name = row.get('姓名', '').strip()
                email = row.get('邮箱', '').strip() or None
                user_type = row.get('身份', 'student').strip()
                phone = row.get('电话', '').strip()
                dept_names = row.get('部门', '').strip()

                if not student_id or not full_name:
                    error_lines.append(f"第{row_num}行：学号或姓名为空")
                    continue

                # 检查学号是否已存在（作为username或Member.student_id）
                if User.objects.filter(username=student_id).exists() or Member.objects.filter(student_id=student_id).exists():
                    error_lines.append(f"第{row_num}行：学号 {student_id} 已存在")
                    continue

                # 创建User
                user = User.objects.create_user(
                    username=student_id,
                    password=student_id,  # 默认密码=学号，可提醒用户修改
                    email=email,
                    first_name=full_name
                )

                # 创建Member
                member = Member.objects.create(
                    user=user,
                    student_id=student_id,
                    user_type=user_type,
                    phone=phone
                )

                # 处理部门（多个部门用英文逗号分隔）
                if dept_names:
                    dept_list = [name.strip() for name in dept_names.split(',') if name.strip()]
                    for dept_name in dept_list:
                        dept, _ = Department.objects.get_or_create(name=dept_name)
                        member.departments.add(dept)

                success_count += 1

            # 显示结果消息
            if success_count:
                self.message_user(request, f'成功导入 {success_count} 个成员')
            if error_lines:
                self.message_user(request, '以下行导入失败：<br>' + '<br>'.join(error_lines), level='WARNING')

            return redirect('..')

        # GET请求显示导入页面
        context = {
            'opts': self.model._meta,
            'title': '批量导入成员',
        }
        return render(request, 'admin/core/import_members.html', context)

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status')
    list_filter = ('date', 'status', 'student__departments')
