from django.shortcuts import render, redirect
<<<<<<< HEAD
from django.contrib.auth import login, logout   # 确保导入 logout
=======
from django.contrib.auth import login, logout
>>>>>>> 03f2d59 (feat: 优化界面风格，实现多部门选择及Tom Select交互)
from django.contrib.auth.decorators import login_required
from .forms import MemberRegistrationForm

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = MemberRegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    profile = user.member_profile if hasattr(user, 'member_profile') else None
<<<<<<< HEAD
    return render(request, 'profile.html', {
        'user': user,
        'profile': profile
    })

# 新增自定义退出视图
=======
    return render(request, 'profile.html', {'user': user, 'profile': profile})

>>>>>>> 03f2d59 (feat: 优化界面风格，实现多部门选择及Tom Select交互)
def custom_logout(request):
    logout(request)
    return redirect('home')