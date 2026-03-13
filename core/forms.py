from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Member, Department

class MemberRegistrationForm(UserCreationForm):
<<<<<<< HEAD
    student_id = forms.CharField(label='学号/工号')
    phone = forms.CharField(label='联系电话', required=False)
    user_type = forms.ChoiceField(choices=Member.USER_TYPE_CHOICES, label='身份', required=True)
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label='所属部门（没有可不选）',
        required=False
=======
    full_name = forms.CharField(
        label='姓名',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入真实姓名'})
    )
    student_id = forms.CharField(
        label='学号/工号',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例如：2024001'})
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
>>>>>>> 03f2d59 (feat: 优化界面风格，实现多部门选择及Tom Select交互)
    )

    class Meta:
        model = User
<<<<<<< HEAD
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Member.objects.create(
                user=user,
                student_id=self.cleaned_data['student_id'],
                user_type=self.cleaned_data['user_type'],
                department=self.cleaned_data.get('department'),
                phone=self.cleaned_data['phone']
            )
=======
        fields = ['username', 'email', 'password1', 'password2']

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

        # 统一添加 form-control 类（已在各字段单独添加，但确保一致性）
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.SelectMultiple)):
                field.widget.attrs.setdefault('class', 'form-control')

    def save(self, commit=True):
        user = super().save(commit=False)
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
>>>>>>> 03f2d59 (feat: 优化界面风格，实现多部门选择及Tom Select交互)
        return user