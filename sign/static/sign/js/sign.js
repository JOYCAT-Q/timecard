const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');
const signUpButton_mobile = document.getElementById('signUp_mobile');
const signInButton_mobile = document.getElementById('signIn_mobile');


signUpButton.addEventListener('click', () => {
	container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
	container.classList.remove("right-panel-active");
});

signUpButton_mobile.addEventListener('click', () => {
	container.classList.add("right-panel-active");
});

signInButton_mobile.addEventListener('click', () => {
	container.classList.remove("right-panel-active");
});

function validatePasswords() {
    var password1 = document.getElementById("pwd1").value;
    var password2 = document.getElementById("pwd2").value;
    if (password1 !== password2) {
        alert("Twice passwords do not match!");
        return false; // 阻止表单提交
    }
    return true; // 允许表单提交
}