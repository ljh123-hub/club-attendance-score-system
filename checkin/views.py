
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.http import JsonResponse
from collections import defaultdict

from .models import Meeting, Attendance
from .forms import MeetingForm
from core.models import Student, Teacher
from django.views.decorators.http import require_POST

def is_teacher(user):
    return hasattr(user, 'teacher_profile')

# 考勤主页（学生/管理员共用）
@login_required
def attendance_home(request):
    now = timezone.now()
    user_is_teacher = is_teacher(request.user)
    # 根据用户身份决定会议列表
    if user_is_teacher:
        meetings = Meeting.objects.all()  # 教师看到所有会议
    else:
        meetings = request.user.meetings.all()  # 学生只看到自己参与的会议

    # 优化：N+1查询优化。一次性查出该用户在这些会议中的所有考勤记录，转为字典
    # 格式：{ meeting_id: attendance_object }
    user_attendances = {
        att.meeting_id: att 
        for att in Attendance.objects.filter(user=request.user, meeting__in=meetings)
    }

    meeting_list = []
    for meeting in meetings:
        # 优化：直接从内存字典中取，不再频繁查数据库
        attendance = user_attendances.get(meeting.id)

        status = {}
        if user_is_teacher:
            status['display'] = '-'
            status['can_checkin'] = False
        elif not meeting.enable_checkin:
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
@require_POST
def do_checkin(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    # 权限检查
    # 优化：将 meeting.participants.all() 的全量查询改为 exists() 判断，提升性能
    if not meeting.participants.filter(id=request.user.id).exists():
        return JsonResponse({'error': '您不是该会议的与会成员'}, status=403)
    if not meeting.enable_checkin:
        return JsonResponse({'error': '此会议未开启签到'}, status=400)
    now = timezone.now()
    if now > meeting.end_time:
        return JsonResponse({'error': '签到时间已过'}, status=400)
    if now < meeting.start_time: # 优化：补充会议未开始拦截
        return JsonResponse({'error': '会议尚未开始'}, status=400)
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
    
    # 优化：使用 select_related 一次性连表查出用户资料，避免在循环中产生 N+1 查询
    participants = meeting.participants.select_related('student_profile', 'teacher_profile').all()
    
    # 优化：一次性查出该会议的所有签到记录
    attendance_dict = {
        att.user_id: att.checkin_time 
        for att in Attendance.objects.filter(meeting=meeting)
    }

    grouped = defaultdict(list)

    for user in participants:
        group_name = '未分组'
        if hasattr(user, 'student_profile'):
            group_name = user.student_profile.class_name
        elif hasattr(user, 'teacher_profile'):
            group_name = user.teacher_profile.department

        # 优化：直接从内存中读取签到时间
        checkin_time = attendance_dict.get(user.id)

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