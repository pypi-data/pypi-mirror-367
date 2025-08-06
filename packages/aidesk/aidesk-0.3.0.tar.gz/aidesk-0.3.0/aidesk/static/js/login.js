document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');
    
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(loginForm);
        const data = new URLSearchParams(formData);
        
        fetch('/api/login', {
            method: 'POST',
            body: data
        })
        .then(response => {
            if (response.ok) {
                // 登录成功，重定向到实例管理页面
                window.location.href = '/manage-instances';
            } else {
                return response.json().then(data => {
                    throw new Error(data.message || 'Login failed');
                });
            }
        })
        .catch(error => {
            // 显示错误消息
            errorMessage.textContent = error.message;
            errorMessage.style.display = 'block';
            
            // 3秒后隐藏错误消息
            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 3000);
        });
    });
});
