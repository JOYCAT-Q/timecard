from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import User, AttendanceRecord, Photo, WorkTimeSettings
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.core.files.base import ContentFile
import json
from django.utils import timezone
from datetime import timedelta
from insightface.app import FaceAnalysis
from .formatConversion import base64_to_cv2, base64_to_content, reverse_geocoding
from .formatConversion import base64_to_np, np_to_base64, compare_face
# ！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
# 设置全局时区[同时确保Mysql数据库中时区也设置为统一时区,否则Django中的关于时间的ORM查询会失效]
# ！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
timezone.activate('Asia/Shanghai')
# Create your views here.


def home(request):
    """
    主页视图函数
    :param request:
    :return:
    """
    response = render(request, 'sign/home.html')
    print('session: ', request.session)
    print('cookie: ', request.COOKIES)
    return response


def login_view(request):
    """
    登录视图函数
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'sign/sign.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not (username and password):
            return render(request, "sign/sign.html", {'output_messages': "Please input all messages."})
        # 尝试认证用户[使用Django自带的认证系统]
        user = authenticate(request, username=username, password=password)

        # 如果用户存在且密码正确
        if user is not None:
            # 登录用户[使用Django自带的登录视图]
            login(request, user)
            response = render(request, 'sign/home.html')
            # 设置cookie表示登录状态，对当前功能无作用,因为使用了Django的认证系统,后续进行前后端分离时可使用
            response.set_cookie('is_logged_in', 'true', max_age=3600)  # 有效期为1小时
            return response
        else:
            # 如果认证失败，显示错误信息
            return render(request, 'sign/sign.html', {'output_messages': "username or password is wrong, please check "
                                                                         "it."})


def logout_view(request):
    """
    退出登录视图
    :param request:
    :return:
    """
    # 登出用户
    logout(request)
    # 重定向到登录页面或其他页面
    response = render(request, 'sign/home.html')
    response.set_cookie('is_logged_in', 'false')
    return response


def send_qq_email(username, password, receiver, subject=None, message=None):
    """
    对自带的邮箱发送进一步封装
    :param username: 用户名
    :param password: 未加密密码
    :param receiver: 接收者邮箱
    :param subject: 邮箱标题
    :param message: 邮箱正文
    :return:
    """
    if not subject:
        subject = "Welcome to use django facial attendance"
    if not message:
        message = (f'Thank you for registering: \n\nYour username is: {username},\nYour password is: {password},\n\n'
                   f'\nPlease remember your account.\n\nPlease be careful not to disclose the contents of this email, '
                   f'which may cause account loss.\n\n\nWishing you a pleasant use.')
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = receiver
    try:
        # 发送邮件
        send_mail(subject, message, from_email, [to_email])
        return True
    except Exception:
        return False


def register(request):
    """
    注册视图函数
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'sign/sign.html')
    else:
        username = request.POST.get("username")
        password = request.POST.get("password1")
        password2 = request.POST.get("password2")
        qq_email = request.POST.get("qq_email")
        # 对两次密码输入进行验证
        if password != password2:
            return render(request, "sign/sign.html",
                          {'output_messages': "Twice passwords do not match!"})
        # 确保所有数据都存在requests中
        if not (username and password and qq_email):
            return render(request, "sign/sign.html",
                          {'output_messages': "Please input all messages."})
        # 在数据库中对当前注册用户名称进行过滤
        is_existed = User.objects.filter(username=username)
        # 若已经存在相同名称,则不允许继续注册
        if is_existed:
            return render(request, "sign/sign.html", {'output_messages': username + " has been registered, please use "
                                                                                    "another name or login it."})
        # 对密码进行hash加密
        password_hash = make_password(password)
        # 对用户发送注册邮箱
        if not send_qq_email(username, password, qq_email):
            return render(request, "sign/sign.html",
                          {'output_messages': "Could not send email to " + qq_email + " please "
                                                                                      "check it."})
        # 对用户发送用户id邮箱
        user_id = User.objects.create(username=username, password=password_hash, email=qq_email).id
        if not send_qq_email(username, password, qq_email, subject='check your id', message=f'Your ID is {user_id}'):
            return render(request, "sign/sign.html",
                          {'output_messages': "Could not send email to " + qq_email + " please "
                                                                                      "check it."})
        response = render(request, 'sign/sign.html')
        return response


def detect_faces(img_base64):
    """
    检测base64编码图片中的人脸特征以及人脸框数据
    :param img_base64: base64编码图片[单张]
    :return: dict{}
    """
    # 检测图像中的人脸
    face_analysis = FaceAnalysis(providers=['CPUExecutionProvider'], name='buffalo_sc')
    face_analysis.prepare(ctx_id=0, det_size=(640, 640))
    img_cv2 = base64_to_cv2(img_base64)
    faces = face_analysis.get(img_cv2)
    # 将每个人脸的嵌入向量和边界框转换为 Base64 编码的字符串
    embeddings = [np_to_base64(face['embedding']) for face in faces]
    bboxs = [np_to_base64(face['bbox']) for face in faces]
    return {"embeddings": embeddings, "bboxs": bboxs}


def images_detected(imgs_base64: list):
    """
    判断传入的图片的人脸信息相似度
    :param imgs_base64: base64编码图片[仅支持传入两张]
    :return:
    """
    results_json = []
    for img_base64 in imgs_base64:
        results_json.append(detect_faces(img_base64))
    embeddings = [result_json['embeddings'] for result_json in results_json]
    embeddings = [[base64_to_np(emb) for emb in embs] for embs in embeddings]
    # 比较两张图片中，各自第一张人脸的特征向量
    embs = [embeddings[i][0] for i in range(len(embeddings))]
    is_like, how_like = compare_face(embs[0], embs[1], threshold=0.5)

    return is_like, how_like


def check_early_or_late(now, punch_type):
    """
    判断当前打卡时间的对应状态
    :param now: 服务器端本地时间
    :param punch_type: 打卡类型['in': '上班', 'out': '下班']
    :return: str['None', 'late', 'on_time', 'early']
    """
    # 设定上下班时间
    # 获取时间段设置
    work_time_settings = WorkTimeSettings.objects.order_by('-updated_at').first()
    if not work_time_settings:
        # 如果没有设置，使用默认时间
        start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
        middle_time = now.replace(hour=12, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=18, minute=0, second=0, microsecond=0)
    else:
        start_time = now.replace(hour=work_time_settings.start_time.hour, minute=work_time_settings.start_time.minute,
                                 second=work_time_settings.start_time.second, microsecond=0)
        middle_time = now.replace(hour=work_time_settings.middle_time.hour,
                                  minute=work_time_settings.middle_time.minute,
                                  second=work_time_settings.middle_time.second, microsecond=0)
        end_time = now.replace(hour=work_time_settings.end_time.hour, minute=work_time_settings.end_time.minute,
                               second=work_time_settings.end_time.second, microsecond=0)

    if punch_type == 'in':
        # 如果现在时间早于开始时间30分钟，那么无法打卡
        if start_time > (timedelta(minutes=30) + now):
            return "None"

        # 如果现在是上班时间前30分钟内,则进行上班打卡
        elif (start_time <= (timedelta(minutes=30) + now)) and (start_time >= now):
            return 'on_time'
        # 超过8:00且在中午之前打卡为迟到
        elif (now > start_time) and (now <= middle_time):
            return 'late'
        else:
            return "None"
    elif punch_type == 'out':
        # 如果现在时间晚于结束时间30分钟，那么无法打卡
        if now > (end_time + timedelta(minutes=30)):
            return 'None'
        # 如果现在是上班时间前30分钟内,则进行上班打卡
        elif (now >= end_time) and (now <= (end_time + timedelta(minutes=30))):
            return 'on_time'
        # 超过12:00且在下班之前打卡为早退
        elif (now < end_time) and (now > middle_time):
            return 'early'
        else:
            return "None"
    else:
        return "None"


def has_attendance_today(user, now):
    """
    在数据库中查找当前用户是否存在当天的打卡记录
    :param user: 用户实例
    :param now: 服务器本地时间
    :return: bool
    """
    today = now.date()
    return AttendanceRecord.objects.filter(user=user, check_in_time__date=today).exists()


def has_reached_attendance_limit(user, now):
    """
    每个用户每天仅能打卡两次[上班,下班]
    :param user: 用户实例
    :param now: 服务器本地时间
    :return: bool
    """
    today = now.date()
    return AttendanceRecord.objects.filter(user=user, check_in_time__date=today).count() >= 2


def create_attendance_record(user, punch_type, punch_time, late_or_early, location, photo):
    """
    为当前用户创建打卡记录
    :param user: 用户实例
    :param punch_type: 打卡类型['in': '上班', 'out': '下班']
    :param punch_time: 打卡时间
    :param late_or_early: 打卡状态['late': "迟到", 'on_time': '正常打卡', 'early': '早退']
    :param location: 打卡位置
    :param photo: photo模型实例
    :return:
    """
    today = punch_time.date()
    record = AttendanceRecord(
        user=user,
        check_in_time=punch_time if punch_type == 'in' else None,  # 上班打卡时设置check_in_time
        check_out_time=punch_time if punch_type == 'out' else None,  # 下班打卡时设置check_out_time
        late_or_early=late_or_early,
        punching_location=location,
    )
    record.save_with_photo(photo)
    # 如果已经打卡过（上班），则这是下班打卡
    if has_attendance_today(user, punch_time):
        if record.check_in_time:
            raise ValueError("You have already punched in for today.")
            # 否则，更新check_out_time
        existing_record = AttendanceRecord.objects.get(user=user, check_in_time__date=today)
        existing_record.check_out_time = punch_time
        if existing_record.check_in_time and existing_record.check_out_time:
            # 计算工作时长
            existing_record.working_hours = existing_record.check_out_time - existing_record.check_in_time
        existing_record.save()
    else:
        # 否则，创建新的上班打卡记录
        record.check_in_time = punch_time
        record.save()
    return record


# 登录检测修饰器,判断当前是否登录,未登录则跳转登录
@login_required(login_url='/login/')
def punching(request):
    """
    打卡视图函数
    :param request:
    :return:
    """
    if request.method == 'POST':
        # 判断当前用户是否通过登录验证
        if request.user.is_authenticated:
            # 获取前端传入的数据
            data = json.loads(request.body)
            face_data_base64 = data.get('face_data')
            # 经纬度坐标
            location = data.get('location')
            lng = location.split(',')[1]
            lat = location.split(',')[0]
            # 百度逆地理编码API
            address = reverse_geocoding(str(lng), str(lat), settings.BAIDU_AK)

            username_request = request.user.username
            password_request = request.user.password
            user = User.objects.get(username=username_request)
            if not user.face_emb:
                # 当前用户未注册人脸信息
                return JsonResponse({'status': 'error', 'message': "The current user's facial information has not "
                                                                   "been entered into the database yet"}, status=200)
            if user.password == password_request and face_data_base64 and user.face_emb:
                imgs_base64 = [face_data_base64, user.face_emb]
                try:
                    is_like, how_like = images_detected(imgs_base64)
                # 当传入的图片中不存在人脸信息时会导致范围错误
                except IndexError:
                    # 当前传入图片无人脸信息
                    return JsonResponse({'status': 'error', 'message': "Please ensure that there is facial "
                                                                       "information in the screen"}, status=200)
                if not is_like:
                    # 当前传入的人脸特征与数据库中人脸信息不匹配
                    return JsonResponse({'status': 'error', 'message': "The current user's facial information does "
                                                                       "not match the database. Please check in "
                                                                       "yourself"}, status=200)
                now_utc = timezone.now()
                now = timezone.localtime(now_utc)
                if has_reached_attendance_limit(user, now):
                    # 当前用户已经完成两次打卡
                    return JsonResponse({'status': 'error', 'message': "You have completed two clock ins"},
                                        status=200)
                # 判断当前用户是否存在当天的打卡记录
                if has_attendance_today(user, now):
                    punch_type = 'out'
                else:
                    punch_type = 'in'
                # 判断当前打卡时间对应的状态
                early_or_late = check_early_or_late(now, punch_type)
                # 当前时间不在打卡时间范围内
                if early_or_late == 'None':
                    return JsonResponse({'status': 'error', 'message': "Unable to clock in before the clock in "
                                                                       "time.\nCheck in time is within 30 minutes "
                                                                       "before and after commuting."}, status=200)
                img_content = base64_to_content(face_data_base64)
                content_file = ContentFile(img_content, name=f"{user.username}.jpg")
                photo = Photo(user=user, title=f'Uploaded Photo by {user.username}', image=content_file)
                record = create_attendance_record(user, punch_type, timezone.localtime(now), early_or_late, address,
                                                  photo)
                # 打卡记录创建成功
                if record.id:
                    return JsonResponse({'status': 'success', 'message': 'Attendance clock in successfully'})
                else:
                    # 数据保存发生了错误
                    return JsonResponse({'status': 'error', 'message': "An error occurred during the process of "
                                                                       "saving data."}, status=200)

            else:
                return JsonResponse({'status': 'error', 'message': 'Please check your account information or uploaded '
                                                                   'photos'},
                                    status=200)

        else:
            # 当前用户未登录
            return render(request, "sign/sign.html", {'output_messages': "Current account not logged in"})

    else:
        # GET 请求
        return render(request, 'sign/punching.html')


@login_required(login_url='/login/')
def face_registration(request):
    """
    人脸注册视图函数
    :param request:
    :return:
    """
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            face_data_base64 = data.get('face_data')
            username_request = request.user.username
            password_request = request.user.password
            # print(request.user.username)
            # print(request.user.password)
            user = User.objects.get(username=username_request)
            # 将当前用户人脸信息存入数据库中
            if user.password == password_request and face_data_base64:
                user.face_emb = str(face_data_base64)
                user.save()
            else:
                return JsonResponse({'status': 'error', 'message': 'An error occurred while saving facial '
                                                                   'information. Please check the facial photo'},
                                    status=200)

        else:
            return render(request, "sign/sign.html", {'output_messages': "Current account not logged in"})

        return JsonResponse({'status': 'success', 'message': 'Face registered successfully'})
    else:
        return render(request, 'sign/faceRegister.html')
