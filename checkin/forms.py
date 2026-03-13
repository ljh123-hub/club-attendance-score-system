from django import forms
from .models import Meeting

class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['name', 'location', 'start_time', 'end_time', 'enable_checkin', 'description', 'participants']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),

        }

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 为大多数字段添加 form-control 类
        for field_name in ['name', 'location', 'start_time', 'end_time', 'description']:
            self.fields[field_name].widget.attrs.setdefault('class', 'form-control')
        # 为 participants 字段添加 tom-select 类，同时保留可能的多选属性
        self.fields['participants'].widget.attrs.setdefault('class', 'tom-select')
        # 复选框字段不需要 form-control，但可以添加 form-check-input 类（可选）
        self.fields['enable_checkin'].widget.attrs.setdefault('class', 'form-check-input')

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if start_time and end_time and start_time > end_time:
            raise forms.ValidationError('开始时间不能晚于结束时间')
        return cleaned_data

