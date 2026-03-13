
# Create your views here.
# checkin/views.py - 片段替换
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.http import JsonResponse
from collections import defaultdict
from datetime import timedelta

from .models import Meeting, Attendance
from .forms import MeetingForm
from core.models import Member
from django.views.decorators.http import require_POST

def is_teacher(user):
    if hasattr(user, 'member_profile'):
        return user.member_profile.user_type == 'teacher'
    return False


@login_required
def attendance_home(request):
    """
    列表分为三组：
      - this_week_meetings: 本周（周一~周日）内的会议（不分页）
      - future_meetings: 本周之后的未来会议（不分页）
      - past_meetings: 历史会议（分页，超过10条时翻页）
    另外为每条会议计算签到状态（支持提前10分钟签到）
    """
    now = timezone.now()
    user_is_teacher = is_teacher(request.user)

    # 基本 queryset：教师看所有会议，学生看其参与的会议
    if user_is_teacher:
        base_qs = Meeting.objects.all()
    else:
        base_qs = request.user.meetings.all()

    # 为后续减少查询：一次性拉取 Attendance（针对当前 user 或针对会议）
    user_attendances = {
        att.meeting_id: att
        for att in Attendance.objects.filter(user=request.user, meeting__in=base_qs)
    }

    # 计算本周范围（以周一为起点）
    # 注意 timezone-aware
    weekday = now.weekday()  # Monday=0
    start_of_week = (now - timedelta(days=weekday)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = (start_of_week + timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=999999)

    # 按时间将会议分组（注意查询仅在需要时 eval）
    # 我们会遍历 base_qs; 如果你担心性能，可按时间预过滤并加索引
    this_week = []
    future_after_week = []
    past = []

    for meeting in base_qs.order_by('-start_time'):
        # 取出该用户在该会议的考勤记录（如果存在）
        attendance = user_attendances.get(meeting.id)
        # 判断是否可签到的时间窗口：start_time - 10min <= now <= end_time
        can_checkin_window_start = meeting.start_time - timedelta(minutes=10)
        can_checkin_window_end = meeting.end_time

        status = {}
        # 教师不需要签到
        if user_is_teacher:
            status['display'] = '-'
            status['can_checkin'] = False
        elif not meeting.enable_checkin:
            status['display'] = '此会议无需签到'
            status['can_checkin'] = False
        elif attendance and attendance.checkin_time:
            status['display'] = f'已签到 ({attendance.checkin_time.strftime("%Y-%m-%d %H:%M")})'
            status['can_checkin'] = False
        elif now > can_checkin_window_end:
            status['display'] = '缺勤'
            status['can_checkin'] = False
        elif now < can_checkin_window_start:
            # 会议尚未到可以签到的时间（注意可能是“会议未开始”或“待签到（提前10分钟内）”）
            if now < meeting.start_time:
                status['display'] = '会议未开始'
            else:
                status['display'] = '等待签到'
            status['can_checkin'] = False
        else:
            # now 在 [start_time - 10min, end_time] 且尚未签到
            status['display'] = '待签到'
            status['can_checkin'] = True

        # 把需要在模板展示的信息附上
        entry = {
            'meeting': meeting,
            'status': status,
            'description': meeting.description,
            'start_time': meeting.start_time,
            'end_time': meeting.end_time,
        }

        # 分类到本周/未来/历史
        # 以会议的 start_time 或 end_time 作判断：
        if meeting.end_time < now:
            past.append(entry)
        elif meeting.start_time >= start_of_week and meeting.start_time <= end_of_week:
            this_week.append(entry)
        else:
            # 非本周且在未来
            future_after_week.append(entry)

    # 对历史会议启用分页（每页10条）
    page = request.GET.get('page', 1)
    paginator = Paginator(past, 10)
    try:
        past_page = paginator.page(page)
    except PageNotAnInteger:
        past_page = paginator.page(1)
    except EmptyPage:
        past_page = paginator.page(paginator.num_pages)

    context = {
        'this_week': this_week,
        'future_after_week': future_after_week,
        'past_page': past_page,  # 这是一个 Page 对象
        'is_teacher': user_is_teacher,
    }
    return render(request, 'checkin/attendance_home.html', context)


@login_required
@require_POST
def do_checkin(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)

    # 权限检查：是否为与会人员
    if not meeting.participants.filter(id=request.user.id).exists() and not is_teacher(request.user):
        return JsonResponse({'error': '您不是该会议的与会成员'}, status=403)

    if not meeting.enable_checkin:
        return JsonResponse({'error': '此会议未开启签到'}, status=400)

    now = timezone.now()
    # 签到窗口：允许在会议开始前10分钟签到，直到会议结束
    earliest = meeting.start_time - timedelta(minutes=10)
    latest = meeting.end_time

    if now < earliest:
        return JsonResponse({'error': '签到尚未开启（请在会议开始前10分钟内签到）'}, status=400)
    if now > latest:
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
    
    # 注意：participants 可能仍然是 User 的多对多，但我们需要通过 User 获取 Member
    participants = meeting.participants.all()
    
    # 一次性获取所有相关 Member 信息，避免 N+1 查询
    members = Member.objects.filter(user__in=participants).select_related('user').prefetch_related('departments')
    member_dict = {member.user_id: member for member in members}
    
    # 签到记录
    attendance_dict = {
        att.user_id: att.checkin_time 
        for att in Attendance.objects.filter(meeting=meeting)
    }

    grouped = defaultdict(list)

    for user in participants:
        member = member_dict.get(user.id)
        if not member:
            # 如果用户没有关联的 Member（理论上不应该），跳过或作为未分组
            group_name = '未关联成员'
        else:
            # 取第一个部门名称作为分组（如果无部门则显示“未分组”）
            first_dept = member.departments.first()
            group_name = first_dept.name if first_dept else '未分组'

        checkin_time = attendance_dict.get(user.id)
        grouped[group_name].append({
            'user': user,
            'checkin_time': checkin_time,
            'member': member,  # 如果需要显示更多信息
        })

    grouped_list = [{'department': dept, 'users': users} for dept, users in grouped.items()]

    context = {
        'meeting': meeting,
        'grouped_list': grouped_list,
    }
    return render(request, 'checkin/meeting_detail.html', context)