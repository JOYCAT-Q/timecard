# Django Web 人脸考勤

`基于`python3.10`和`Django4.2`的人脸考勤系统，当前教程默认在Windows下进行 `

## 主要功能：
- 注册：使用用户名、密码、邮箱进行注册，注册成功发送注册成功邮箱通知
- 登录：已注册的用户可使用用户名与密码进行登录
- 面部信息录入：用户可在登录后将面部信息录入数据库`MySql`中
- 考勤打卡：对于已录入面部信息的用户支持进行打卡，每人每天仅有2次打卡机会
- 管理员后台：使用`python manage.py createsuperuser`来创建自己的超级管理员
  1. 允许为用户创建、修改、删除分组，进行权限管理
  2. 允许查看、新增、删除注册用户，以及通过关键词搜索、有效状态和是否为工作人员进行检索用户
  3. 允许查看、新增、修改、删除当前所有用户的打卡信息，以及通过打卡状态、打卡日期、用户名等对打卡记录进行检索
  4. 允许选中所需的打卡记录，通过邮箱发送到管理员邮箱中，格式为`xlsx`
  5. 允许更新设置上下班打卡时间点


## 安装：

1. 安装`MySQL8.0`社区版

   下载地址：`https://dev.mysql.com/downloads/mysql/ `

2. 在`Pycharm`中新建解释器环境

3. 安装`pysql`或者`mysqlclient`,自行手动使用`pip`安装

4. 使用pip安装： `pip install -Ur requirements.txt`来补全环境

## 注意事项：

1. 代码中`Django`使用的时区为北京东八区时间，而数据库`MySQL`使用`UTC`时间，从而影响`Django`的`ORM`关于时间字段的查询

​	所以需要在`MySQL`中导入时区表

​	在`timecard\MySQLTimeZone`下存在`timezone_posix.sql`数据库文件，

​	或者自行在官网下载最新：`https://dev.mysql.com/downloads/timezones.html`

​	将其拷贝至数据库安装路径：`C:\Program Files\MySQL\MySQL Server 8.0\bin`[默认路径如此]

​	在当前位置打开终端输入：`mysql -u root -p mysql < timezone_posix.sql`将其导入数据库

​	重新打开终端输入：`mysql -u root -p`进入数据库

​	在数据库中输入：`SELECT * FROM mysql.time_zone_name WHERE Name = 'Asia/Shanghai';`查询是否导入成功，输出	不为`empty`即为导入成功

​	然后输入：`SET GLOBAL time_zone = 'Asia/Shanghai';`即可将数据库时区设置为东八区

2. 需要通过`Visual Studio Installer`下载`Visual Studio 生成工具`，我使用的版本为2022

​	安装组件选择：`MSVC v143 - VS 2022 C++ `和对应`Windows`版本的`SDK`





## `settings.py`中配置修改：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        "USER": "root",  # 你自己的数据库用户名
        "PASSWORD": "12345678",  # 你自己的数据库密码
        "HOST": "127.0.0.1",
        "PORT": 3306,
        'NAME': "timecard",  # 必须为已存在的数据库名称, 需要自己手动创建
    }
}
```

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'  # 取决于你自己的邮箱类型, 当前示例为QQ邮箱类型
EMAIL_PORT = 465  # 取决于你自己的邮箱类型的转发端口, 当前示例为QQ邮箱转发端口
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False  # 确保这个为False，因为使用了SSL
EMAIL_HOST_USER = 'yourself_email@qq.com'  # 代发邮箱地址, 当前示例为QQ邮箱
EMAIL_HOST_PASSWORD = 'vertified_code'  # 代发邮箱SMTP服务授权码, 当前示例为QQ邮箱
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

AUTH_USER_MODEL = 'sign.User'
# 百度地理逆编码ak授权码
BAIDU_AK = "vertified_code"  # 登录百度开发者中心的控制台创建自己的应用来获取
```


### 创建数据库
`mysql`数据库中执行:

```sql
CREATE DATABASE `timecard` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;
```

然后终端下执行以下命令进行迁移:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 创建超级用户

 终端下执行:
```bash
python manage.py createsuperuser
```


### 开始运行：
执行： `python manage.py runserver`


浏览器打开: http://127.0.0.1:8000/  就可以看到效果了

以下为运行界面：

1. 首页

![home.png](https://s2.loli.net/2024/07/05/DRG3j4IMZBLozWU.png)

登录后

![home_logined.png](https://s2.loli.net/2024/07/05/JlquMQnvNByYhbI.png)

2. 注册页

![register.png](https://s2.loli.net/2024/07/05/jMvxdunhwGSofAJ.png)

3. 登录页

![login.png](https://s2.loli.net/2024/07/05/xg3s8ftdBlM9SYL.png)

4. 面部信息注册页

![faceRegister.jpg](https://s2.loli.net/2024/07/05/nGMRzr9ySO61fLQ.jpg)

5. 考勤打卡页

![punch.jpg](https://s2.loli.net/2024/07/05/yrhUDMTHkVLzZWI.jpg)

6. 管理员页

![admin_login.png](https://s2.loli.net/2024/07/05/UZ1eADzqu4mTNfE.png)

![admin_interface1.png](https://s2.loli.net/2024/07/05/zpw3IT85nOQWryG.png)

- 普通用户管理页

![admin_interface_user1.png](https://s2.loli.net/2024/07/05/qzOL97nBUrF84iG.png)

![admin_interface_user2.png](https://s2.loli.net/2024/07/05/byfCtLeD3rHpJOA.png)

- 考勤信息管理页

![admin_interface_attendance1.png](https://s2.loli.net/2024/07/05/uSaYFMisQKjbIch.png)

考勤信息邮箱发送至管理员邮箱
![admin_interface_attendance4.png](https://s2.loli.net/2024/07/05/57Jl6qrmZMKyNEc.png)

上下班时间点管理页

![admin_interface_worktime1.png](https://s2.loli.net/2024/07/05/VYi4ZoO3lMjLsyX.png)

![admin_interface_worktime2.png](https://s2.loli.net/2024/07/05/TC9td6IyJs8Mpav.png)

用户组管理页

![admin_interface_group.png](https://s2.loli.net/2024/07/05/rBMWGnDlycv3qYs.png)

- 注册者邮箱接收内容

![email_content2.jpg](https://s2.loli.net/2024/07/05/ovJFOEjeuyzA2Z1.jpg)

![email_content1.jpg](https://s2.loli.net/2024/07/05/xHbw6aOipEzmhPe.jpg)

- 管理员邮箱接收内容

![email_content3.jpg](https://s2.loli.net/2024/07/05/RMaiTYJA2Gwp7Wk.jpg)

`attendance_records.xlsx` 即为考勤记录导出结果

