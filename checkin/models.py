from django.db import models

# Create your models here.

from django.contrib.auth.models import User

class Meeting(models.Model):
    """会议模型"""
    name = models.CharField('会议名称', max_length=100)
    location = models.CharField('开会地点', max_length=100, blank=True)
    start_time = models.DateTimeField('预计开始时间')
    end_time = models.DateTimeField('预计结束时间')
    enable_checkin = models.BooleanField('开启签到', default=True)
    description = models.TextField('简介', blank=True)
    participants = models.ManyToManyField(
        User, 
        verbose_name='与会成员',
        related_name='meetings',
        blank=True
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_meetings',
        verbose_name='创建者'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return self.name

    def checkin_count(self):
        """返回已签到人数"""
        return self.attendance_set.filter(checkin_time__isnull=False).count()

    def absent_count(self):
        """返回缺勤人数（与会人员中，会议开启签到且未签到的人数）"""
        if not self.enable_checkin:
            return 0
        total = self.participants.count()
        checked = self.checkin_count()
        return total - checked

class Attendance(models.Model):
    """考勤记录（每个用户每个会议一条）"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, verbose_name='会议')
    checkin_time = models.DateTimeField('签到时间', null=True, blank=True)

    class Meta:
        unique_together = ('user', 'meeting')

    def __str__(self):
        status = '已签到' if self.checkin_time else '未签到'
        return f"{self.user.username} - {self.meeting.name} - {status}"