from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import PunchRecord

def index(request):
    return HttpResponse("Hello, world.")


@login_required
def checkin_view(request):
    if request.method == 'POST':
        punch_type = request.POST.get('punch_type')  # 'in' 或 'out'
        # 创建打卡记录
        PunchRecord.objects.create(
            user=request.user,
            punch_type=punch_type
        )
        return render(request, 'checkin/checkin_success.html', {'type': punch_type})
    # GET 请求显示打卡页面
    return render(request, 'checkin/checkin.html')