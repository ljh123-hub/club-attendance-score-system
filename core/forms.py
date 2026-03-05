from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Student, Teacher

class StudentRegistrationForm(UserCreationForm):
    student_id = forms.CharField(max_length=20, label='学号')
    class_name = forms.CharField(max_length=50, label='班级')
    phone = forms.CharField(max_length=11, required=False, label='电话')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                student_id=self.cleaned_data['student_id'],
                class_name=self.cleaned_data['class_name'],
                phone=self.cleaned_data.get('phone', '')
            )
        return user

class TeacherRegistrationForm(UserCreationForm):
    teacher_id = forms.CharField(max_length=20, label='工号')
    department = forms.CharField(max_length=50, label='院系')
    title = forms.CharField(max_length=20, required=False, label='职称')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Teacher.objects.create(
                user=user,
                teacher_id=self.cleaned_data['teacher_id'],
                department=self.cleaned_data['department'],
                title=self.cleaned_data.get('title', '')
            )
        return user