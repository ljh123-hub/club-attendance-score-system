from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from django.conf import settings          # 新增导入

from .models import Member, Department

class MemberRegistrationForm(UserCreationForm):
    full_name = forms.CharField(
        label='姓名',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入真实姓名'})
    )
    student_id = forms.CharField(

        label='学号',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例如：25010022022'})

    )
    phone = forms.CharField(
        label='联系电话',
        required=False,

        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '可选'})

    )
    user_type = forms.ChoiceField(
        choices=Member.USER_TYPE_CHOICES,
        label='身份',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    departments = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        label='所属部门（可多选）',
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '8'})
    )


    # 新增：管理员注册码字段（仅当身份为教师时需验证）
    teacher_secret = forms.CharField(
        label='管理员注册码',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '如需注册为站长，请输入密钥'})
    )

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']   # 移除了 'username'


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 确保预设部门存在
        department_names = [
            '程序部', 'web部', 'app部', '游戏部', 'IOS部', 'UI部',
            '系统维护部门', '精英培优班', '其他（糯唧唧的gyh）'
        ]
        for name in department_names:
            Department.objects.get_or_create(name=name)

        self.fields['departments'].queryset = Department.objects.all()


        # 统一添加 form-control 类

        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.SelectMultiple)):
                field.widget.attrs.setdefault('class', 'form-control')


    def clean_student_id(self):
        """检查学号是否已被使用（包括作为用户名或已存在于 Member）"""
        student_id = self.cleaned_data['student_id']
        if User.objects.filter(username=student_id).exists():
            raise forms.ValidationError('该学号已被注册')
        if Member.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError('该学号已存在成员信息')
        return student_id

    # 新增：整体验证逻辑
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        teacher_secret = cleaned_data.get('teacher_secret')

        # 如果用户选择教师/站长，则必须验证注册码
        if user_type == 'teacher':
            correct_secret = settings.TEACHER_REGISTRATION_SECRET
            if not teacher_secret:
                self.add_error('teacher_secret', '注册站长必须填写管理员注册码')
            elif teacher_secret != correct_secret:
                self.add_error('teacher_secret', '管理员注册码错误')
        # 如果选择学生，忽略 teacher_secret 字段（即使填写了也不验证）
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['student_id']   # 学号作为用户名

        user.first_name = self.cleaned_data['full_name']
        user.last_name = ''
        if commit:
            user.save()
            member = Member.objects.create(
                user=user,
                student_id=self.cleaned_data['student_id'],
                user_type=self.cleaned_data['user_type'],
                phone=self.cleaned_data['phone']
            )
            if self.cleaned_data['departments']:
                member.departments.set(self.cleaned_data['departments'])
        return user