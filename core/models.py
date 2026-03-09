from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField('部门名称', max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = '部门'

class Member(models.Model):
    USER_TYPE_CHOICES = (
        ('student', '学生/成员'),
        ('teacher', '老师/导员'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member_profile')
    user_type = models.CharField('身份类型', max_length=20, choices=USER_TYPE_CHOICES, default='student')
    student_id = models.CharField('学号/工号', max_length=20, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='所属部门（可选）'
    )
    phone = models.CharField('电话', max_length=11, blank=True)
    is_admin = models.BooleanField('是否管理员', default=False)

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name() or self.user.username}"

class AttendanceRecord(models.Model):
    STATUS_CHOICES = (
        ('present', '正常出勤'),
        ('late', '迟到'),
        ('absent', '缺席'),
        ('leave', '请假'),
    )
    student = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name='成员')
    date = models.DateField('考勤日期', auto_now_add=True)
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='present')
    remark = models.CharField('备注', max_length=200, blank=True)

    class Meta:
        unique_together = ('student', 'date')
        verbose_name = '考勤记录'

    def __str__(self):
        return f"{self.student.student_id} | {self.date} | {self.get_status_display()}"