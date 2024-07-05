from .models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm


# 表单文件,创建用户注册表单
class RegistrationForm(UserCreationForm):
    qq_email = forms.EmailField(label='QQ Email', required=True)

    class Meta:
        model = User
        fields = ('username', 'qq_email', 'password1', 'password2')

    def save(self, commit=True):
        # 保存用户时，你可以在这里添加额外的逻辑
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['qq_email']
        if commit:
            user.save()
        return user
