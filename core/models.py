from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField('学号', max_length=20, unique=True)
    class_name = models.CharField('班级', max_length=50)
    phone = models.CharField('电话', max_length=11, blank=True)

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name() or self.user.username}"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    teacher_id = models.CharField('工号', max_length=20, unique=True)
    department = models.CharField('院系', max_length=50)
    title = models.CharField('职称', max_length=20, blank=True)

    def __str__(self):
        return f"{self.teacher_id} - {self.user.get_full_name() or self.user.username}"

class AttendanceRecord(models.Model):
    STATUS_CHOICES = (
        ('present', '正常'),
        ('late', '迟到'),
        ('absent', '旷课'),
        ('leave', '请假'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='学生')
    date = models.DateField('考勤日期', auto_now_add=True)
    status = models.CharField('考勤状态', max_length=10, choices=STATUS_CHOICES, default='present')
    remark = models.CharField('备注', max_length=200, blank=True)

    class Meta:
        unique_together = ('student', 'date')  # 一个学生一天只能有一条记录

    def __str__(self):
        return f"{self.student.student_id} - {self.date} - {self.get_status_display()}"