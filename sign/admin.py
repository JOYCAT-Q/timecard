from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, AttendanceRecord, WorkTimeSettings
from django.core.mail import EmailMessage
from io import BytesIO
from openpyxl import Workbook
from django.conf import settings
# Register your models here.


# 定义管理员中用户模型
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active',)
    list_filter = ('is_staff', 'is_active',)


# 定义管理员中考勤表模型
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'check_in_time', 'check_out_time', 'late_or_early', 'punching_location', 'working_hours')
    list_filter = ('late_or_early', 'check_in_time', 'user__username')
    search_fields = ('user__username', 'check_in_time', 'check_out_time', 'late_or_early')
    actions = ['export_as_xlsx_and_email']

    # actions操作定义[将选中的考勤记录发送至管理员邮箱, 格式 xlsx]
    def export_as_xlsx_and_email(self, request, queryset):
        # 创建一个Workbook并写入数据
        wb = Workbook()
        ws = wb.active
        ws.append(['Username', 'Check-in Time', 'Check-out Time', 'Late/Early', 'Location', 'Working Hours'])
        for record in queryset:
            # 移除时区信息
            check_in_time = record.check_in_time.replace(tzinfo=None) if record.check_in_time else ''
            check_out_time = record.check_out_time.replace(tzinfo=None) if record.check_out_time else ''
            ws.append([
                record.user.username,
                check_in_time,
                check_out_time,
                record.late_or_early,
                record.punching_location,
                record.working_hours
            ])
        # 保存Workbook到字节流
        output = BytesIO()
        wb.save(output)
        output.seek(0)  # 确保指针在文件的开头

        # 创建EmailMessage并发送
        subject = 'Attendance Records Export'
        message = 'Here are the attendance records you requested.'
        email = EmailMessage(subject, message, from_email=settings.DEFAULT_FROM_EMAIL, to=[request.user.email])
        email.attach('attendance_records.xlsx', output.getvalue(),
                     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        try:
            email.send()
        except Exception:
            self.message_user(request, 'Email sending failed, please check your email settings.', level='error')
            return

        # 显示成功消息
        self.message_user(request, 'Email with attendance records has been sent successfully.')

    export_as_xlsx_and_email.short_description = "发送至管理员邮箱"


# 注册模型
admin.site.register(AttendanceRecord, AttendanceRecordAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(WorkTimeSettings)
