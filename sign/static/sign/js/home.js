//此JS文件未使用,不影响整体运行,只在控制台打印cookie中登录状态信息
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

function checkLoginStatus() {
    isLoggedIn = getCookie('is_logged_in');
    if (isLoggedIn==='false') {
        // document.getElementById('login-status').innerHTML = '未登录';
        console.log('isLoggedIn: '+isLoggedIn);
    }
    else {
        // document.getElementById('login-status').innerHTML = '已登录';
        // isLoggedIn = 'false';
        console.log('isLoggedIn: '+isLoggedIn);

    }
}

document.addEventListener('DOMContentLoaded', function () {
    checkLoginStatus();
});

