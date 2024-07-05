from django.urls import path
from . import views
from django.contrib import admin
# Django 应用的名称, 用于html中 action 等操作的跳转进行明确指明
app_name = 'sign'


urlpatterns = [
    # 主页url
    path("", views.home, name="home"),
    # 登录url
    path("login/", views.login_view, name="login"),
    # 注册url
    path("register/", views.register, name="register"),
    # 打卡url
    path("punching/", views.punching, name="punching"),
    # 人脸注册url
    path("face/", views.face_registration, name="face"),
    # 退出登录url
    path('logout/', views.logout_view, name='logout'),
    # 管理员url
    path('admin/', admin.site.urls),
]
