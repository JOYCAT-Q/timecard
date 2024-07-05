const video = document.getElementById('videoElement');
const canvas = document.getElementById('canvasElement');
const captureButton = document.getElementById('captureButton');
const photo = document.getElementById('photo');
const openCameraButton = document.getElementById('openCameraButton');
const closeCameraButton = document.getElementById('closeCameraButton');
let stream;

const constraints = {
    video: true
};

// 检测摄像头是否存在
function checkCameraAvailability() {
    return navigator.mediaDevices.enumerateDevices().then(devices => {
        return devices.some(device => device.kind === 'videoinput');
    }).catch(() => false);
}

// 初始化摄像头
async function initCamera() {
    if (!await checkCameraAvailability()) {
        alert('摄像头不存在！');
        return;
    }
    try {
        stream = await navigator.mediaDevices.getUserMedia(constraints);
        handleSuccess(stream);
        openCameraButton.disabled = true;
        closeCameraButton.disabled = false;
        captureButton.disabled = false;
    } catch (e) {
        console.error('访问摄像头出错: ', e);
    }
}

// 显示摄像头视频流
function handleSuccess(stream) {
    video.srcObject = stream;
}

// 停止摄像头
function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
        openCameraButton.disabled = false;
        closeCameraButton.disabled = true;
        captureButton.disabled = true;
    }
}

// 捕获视频流中的图像
function captureImage() {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataURL = canvas.toDataURL('image/png');
        // 显示拍摄的照片
        photo.src = dataURL;
        // photo.style.display = 'block';
}

// 页面加载时检测摄像头
window.onload = () => {
    checkCameraAvailability().then(hasCamera => {
        if (hasCamera) {
            initCamera();
        }
    });
};

// 打开摄像头按钮点击事件
openCameraButton.addEventListener('click', initCamera);

// 关闭摄像头按钮点击事件
closeCameraButton.addEventListener('click', stopCamera);

// 拍照按钮点击事件
captureButton.addEventListener('click', captureImage);


document.getElementById('submitBtn').addEventListener('click', sendFaceData);

function sendFaceData() {
    const imageData = canvas.toDataURL('image/png').split(',')[1]; // 移除Data URL的头部信息
    // console.log(imageData);
    fetch('/punching/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'), // 确保你处理了CSRF
        },
        body: JSON.stringify({
            location: document.getElementById('punching_location').value,
            face_data: imageData,
        }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // 处理响应数据
    if (data.status === 'success') {
        // 或者更新页面上的某个元素来显示消息
        document.getElementById('success-message').textContent = '打卡成功: ' + data.message;
        // 显示成功消息
        alert('打卡成功: ' + data.message);
    } else {
        // 处理错误情况
        alert('打卡失败: ' + data.message);
    }
    })
    .catch((error) => {
        console.error('There was a problem with your fetch operation:', error);
        alert('请检查网络设置');
        console.error('Error:', error);
    });
}

// 假设你有一个函数来获取CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 定义获取地理位置的函数
function getLocationAndSetToForm() {
    navigator.geolocation.getCurrentPosition(function(position) {
        // 构造位置字符串
        var locationStr = position.coords.latitude + ',' + position.coords.longitude;

        // 将位置字符串设置到表单的隐藏字段中
        document.getElementById('punching_location').value = locationStr;
        document.getElementById('lng_lat').innerHTML = locationStr;
        console.log(locationStr);

    }, function(error) {
        console.error('定位失败:', error);
    }, {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0
    });
}
window.onload = function() {
    getLocationAndSetToForm();
};
