from django.db import models
from django.utils.timezone import now
import os
from django.contrib.auth.models import AbstractUser
# Create your models here.


# 用户模型,继承自抽象用户模型 AbstractUser
class User(AbstractUser):
    face_emb = models.TextField(verbose_name='facial_feature', blank=True)


# 考勤表模型
class AttendanceRecord(models.Model):
    # 用户外键
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    # 上班打卡时间
    check_in_time = models.DateTimeField(verbose_name="working_time", blank=True, null=True)
    # 下班打卡时间
    check_out_time = models.DateTimeField(verbose_name="closing_time", blank=True, null=True)
    # 打卡状态: 迟到,早退,正常打卡
    late_or_early = models.CharField(max_length=10, default='on_time',
                                     choices=(('late', 'late'), ('early', 'early'), ('on_time', 'on_time')))
    # 打卡位置,由百度逆地理编码api将经纬度坐标转换获得
    punching_location = models.TextField(verbose_name='punching_location')
    # 工作时间[仅当存在上班打卡后,进行下班打卡时才会进行计算]
    working_hours = models.DurationField(verbose_name="working_hours", blank=True, null=True)
    # 用户打卡图片的保存路径
    photo_path = models.CharField(max_length=255, verbose_name="photo_path")

    # 传入photo模型实例进行保,从而获取照片保存路径
    def save_with_photo(self, photo):
        # 确保 photo 是一个 Photo 实例
        if not isinstance(photo, Photo):
            raise ValueError("photo must be an instance of Photo")

            # 保存 Photo 实例到数据库
        if not photo.id:
            photo.save()

        # 设置 AttendanceRecord 的 photo_path
        self.photo_path = photo.image.url  # 确保配置 MEDIA_URL 和文件存储配置

    # 用于调用查询模型实例时的返回值,如[Your_Name on 2024-07-05]
    def __str__(self):
        return f"{self.user.username} on {self.check_in_time.date()}"

    # 在管理后台的显示名称
    class Meta:
        verbose_name = "考勤记录"
        verbose_name_plural = "考勤记录"


# 获取photo实例,以及传入的图片文件名称
# 构建图片存储路径以及新的文件名称
def upload_to_path(instance, filename):
    # instance是Photo模型的一个实例，且有一个名为'user'的ForeignKey字段指向User模型
    # 使用user_id作为文件名的一部分
    user_id = instance.user.id if hasattr(instance, 'user') else 'anonymous'

    # 获取当前日期和时间
    now_time = now()
    timestamp = now_time.strftime('%Y-%m-%d-%H-%M-%S')

    # 生成新的文件名：用户ID_时间戳_原始文件名
    new_filename = f'{user_id}_{timestamp}_{filename}'

    # 文件夹名使用日期
    folder_name = now_time.strftime('%Y/%m/%d')

    # 返回完整的文件路径
    folder_name = os.path.join(folder_name, str(user_id))
    return os.path.join(folder_name, new_filename)


# 保存用户上传图片的模型
class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 假设有一个指向User的ForeignKey
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to=upload_to_path)

    # 同理,用于实例查询时的默认返回结果
    def __str__(self):
        return self.title


# 用于管理员设置上下班时间
class WorkTimeSettings(models.Model):
    start_time = models.TimeField(verbose_name="Start Time", default="08:00:00")
    middle_time = models.TimeField(verbose_name="Middle Time", default="12:00:00")
    end_time = models.TimeField(verbose_name="End Time", default="18:00:00")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    class Meta:
        verbose_name = "上下班时间点设置"
        verbose_name_plural = "上下班时间点设置"

    def __str__(self):
        return f"Work Time Settings"
