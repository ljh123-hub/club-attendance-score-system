from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Member, Department

class MemberRegistrationForm(UserCreationForm):
    student_id = forms.CharField(label='学号/工号')
    phone = forms.CharField(label='联系电话', required=False)
    user_type = forms.ChoiceField(choices=Member.USER_TYPE_CHOICES, label='身份', required=True)
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label='所属部门（没有可不选）',
        required=False
    )

    class Meta:
        model = User
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
        return user