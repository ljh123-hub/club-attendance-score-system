
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.http import JsonResponse
from collections import defaultdict

from .models import Meeting, Attendance
from .forms import MeetingForm
from core.models import Student, Teacher  # 导入 core 中的用户资料模型

def is_teacher(user):
    return hasattr(user, 'teacher_profile')

# 考勤主页（学生/管理员共用）
@login_required
def attendance_home(request):
    now = timezone.now()
    # 根据用户身份决定会议列表
    if is_teacher(request.user):
        meetings = Meeting.objects.all()  # 教师看到所有会议
    else:
        meetings = request.user.meetings.all()  # 学生只看到自己参与的会议

    meeting_list = []
    for meeting in meetings:
        try:
            attendance = Attendance.objects.get(user=request.user, meeting=meeting)
        except Attendance.DoesNotExist:
            attendance = None

        status = {}
        if not meeting.enable_checkin:
            status['display'] = '此会议无需签到'
            status['can_checkin'] = False
        elif attendance and attendance.checkin_time:
            status['display'] = f'已签到 ({attendance.checkin_time.strftime("%Y-%m-%d %H:%M")})'
            status['can_checkin'] = False
        elif now > meeting.end_time:
            status['display'] = '缺勤'
            status['can_checkin'] = False
        elif now < meeting.start_time:
            status['display'] = '会议未开始'
            status['can_checkin'] = False
        else:
            status['display'] = '待签到'
            status['can_checkin'] = True

        meeting_list.append({
            'meeting': meeting,
            'status': status,
        })

    context = {
        'meeting_list': meeting_list,
        'is_teacher': is_teacher(request.user),  # 传递给模板
    }
    return render(request, 'checkin/attendance_home.html', context)

# 签到处理（AJAX）
@login_required
def do_checkin(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    # 权限检查
    if request.user not in meeting.participants.all():
        return JsonResponse({'error': '您不是该会议的与会成员'}, status=403)

    if not meeting.enable_checkin:
        return JsonResponse({'error': '此会议未开启签到'}, status=400)

    now = timezone.now()
    if now > meeting.end_time:
        return JsonResponse({'error': '签到时间已过'}, status=400)

    attendance, created = Attendance.objects.get_or_create(
        user=request.user,
        meeting=meeting
    )
    if attendance.checkin_time:
        return JsonResponse({'error': '您已经签过到了'}, status=400)

    attendance.checkin_time = now
    attendance.save()

    return JsonResponse({
        'success': True,
        'checkin_time': now.strftime('%Y-%m-%d %H:%M:%S')
    })

# 管理员：发布会议
from django.core.exceptions import PermissionDenied

@login_required
def meeting_create(request):
    if not is_teacher(request.user):
        raise PermissionDenied
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.created_by = request.user
            meeting.save()
            form.save_m2m()
            return redirect('attendance_home')
    else:
        form = MeetingForm()
    return render(request, 'checkin/meeting_form.html', {'form': form})

# 管理员：考勤详情页（按部门/班级分组）
@login_required
def meeting_detail(request, meeting_id):
    if not is_teacher(request.user):
        raise PermissionDenied
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    participants = meeting.participants.all()
    grouped = defaultdict(list)

    for user in participants:
        group_name = '未分组'
        try:
            if hasattr(user, 'student_profile'):
                group_name = user.student_profile.class_name
            elif hasattr(user, 'teacher_profile'):
                group_name = user.teacher_profile.department
        except:
            pass

        try:
            attendance = Attendance.objects.get(user=user, meeting=meeting)
            checkin_time = attendance.checkin_time
        except Attendance.DoesNotExist:
            checkin_time = None

        grouped[group_name].append({
            'user': user,
            'checkin_time': checkin_time,
        })

    grouped_list = [{'department': dept, 'users': users} for dept, users in grouped.items()]

    context = {
        'meeting': meeting,
        'grouped_list': grouped_list,
    }
    return render(request, 'checkin/meeting_detail.html', context)