from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import StudentRegistrationForm, TeacherRegistrationForm


def home(request):
    return render(request, 'home.html')


def register_choice(request):
    return render(request, 'register_choice.html')


def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = StudentRegistrationForm()
    return render(request, 'register_student.html', {'form': form})


def register_teacher(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'register_teacher.html', {'form': form})


@login_required
def profile(request):
    user = request.user
    context = {'user': user}
    if hasattr(user, 'student_profile'):
        context['profile'] = user.student_profile
        context['role'] = 'student'
    elif hasattr(user, 'teacher_profile'):
        context['profile'] = user.teacher_profile
        context['role'] = 'teacher'
    else:
        context['role'] = 'admin'
    return render(request, 'profile.html', context)


from django.shortcuts import render

# Create your views here.
from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    logout(request)           # 退出登录
    return redirect('home')   # 跳转到首页（确保 'home' 是首页的 URL name）