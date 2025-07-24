<template>
  <div class="flex-col justify-start page">
    <div class="section">
      <div class="auth-container">
        <div class="auth-header">
          <h1 class="title">欢迎使用</h1>
          <p class="subtitle">创建账号并开始您的旅程</p>
        </div>
        
        <div class="auth-tabs">
          <button 
            class="tab-button" 
            :class="{ active: currentTab === 'login' }" 
            @click="currentTab = 'login'"
          >
            登录
          </button>
          <button 
            class="tab-button" 
            :class="{ active: currentTab === 'register' }" 
            @click="currentTab = 'register'"
          >
            注册
          </button>
        </div>

        <div v-if="currentTab === 'login'">
          <form class="auth-form" @submit.prevent="handleLogin">
            <div class="form-group">
              <label for="login-username" class="form-label">用户名</label>
              <input 
                type="text" 
                id="login-username" 
                class="form-input"
                placeholder="请输入用户名"
                v-model="loginForm.username"
                required
              >
            </div>
            <div class="form-group">
              <label for="login-password" class="form-label">密码</label>
              <input 
                type="password" 
                id="login-password" 
                class="form-input"
                placeholder="请输入密码"
                v-model="loginForm.password"
                required
              >
            </div>
            <div class="form-actions">
              <button type="submit" class="auth-button">登录</button>
              <p class="forgot-password">忘记密码？</p>
            </div>
          </form>
        </div>

        <div v-if="currentTab === 'register'">
          <form class="auth-form" @submit.prevent="handleRegister">
            <div class="form-group">
              <label for="register-username" class="form-label">用户名</label>
              <input 
                type="text" 
                id="register-username" 
                class="form-input"
                placeholder="请输入用户名"
                v-model="registerForm.username"
                required
              >
            </div>
            <div class="form-group">
              <label for="register-email" class="form-label">电子邮箱</label>
              <input 
                type="email" 
                id="register-email" 
                class="form-input"
                placeholder="请输入电子邮箱"
                v-model="registerForm.email"
                required
              >
            </div>
            <div class="form-group">
              <label for="register-password" class="form-label">密码</label>
              <input 
                type="password" 
                id="register-password" 
                class="form-input"
                placeholder="请输入密码"
                v-model="registerForm.password"
                required
              >
            </div>
            <div class="form-group">
              <label for="register-confirm-password" class="form-label">确认密码</label>
              <input 
                type="password" 
                id="register-confirm-password" 
                class="form-input"
                placeholder="请再次输入密码"
                v-model="registerForm.confirmPassword"
                required
              >
            </div>
            <div class="form-actions">
              <button type="submit" class="auth-button">注册</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      currentTab: 'login', // 默认显示登录tab
      loginForm: {
        username: '',
        password: ''
      },
      registerForm: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      }
    };
  },
  
  methods: {
    handleLogin() {
      // 这里应该有验证用户名和密码的逻辑
      // 假设验证成功
      this.$router.push('/main_top'); // 登录成功后跳转到主页
    },
    
    handleRegister() {
      // 这里应该有注册逻辑
      // 比如验证两次密码是否一致，发送注册请求到服务器等
      // 假设注册成功后跳转到登录tab
      this.currentTab = 'login';
    }
  }
};
</script>

<style scoped lang="css">
  .page {
    padding: 32px 0;
    background-color: #d0e9f2;
    width: 100%;
    overflow-y: auto;
    overflow-x: hidden;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .section {
    margin: 0 18px;
    background-color: #ffffff;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    padding: 32px;
    width: 100%;
    max-width: 480px;
  }
  
  .auth-container {
    margin-top: 20px;
  }
  
  .auth-header {
    text-align: center;
    margin-bottom: 32px;
  }
  
  .title {
    font-size: 28px;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 8px;
  }
  
  .subtitle {
    font-size: 16px;
    color: #7f8c8d;
  }
  
  .auth-tabs {
    display: flex;
    justify-content: center;
    margin-bottom: 24px;
    border-bottom: 1px solid #e0e0e0;
  }
  
  .tab-button {
    background: transparent;
    border: none;
    padding: 10px 20px;
    font-size: 16px;
    font-weight: 500;
    color: #7f8c8d;
    cursor: pointer;
    position: relative;
  }
  
  .tab-button.active {
    color: #3498db;
  }
  
  .tab-button.active::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 0;
    width: 100%;
    height: 2px;
    background-color: #3498db;
  }
  
  .auth-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .form-label {
    font-size: 14px;
    color: #7f8c8d;
    font-weight: 500;
  }
  
  .form-input {
    padding: 12px;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    font-size: 16px;
    transition: border-color 0.3s;
    outline: none;
  }
  
  .form-input:focus {
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
  }
  
  .form-actions {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .auth-button {
    padding: 12px;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .auth-button:hover {
    background-color: #2980b9;
  }
  
  .forgot-password {
    text-align: right;
    font-size: 14px;
    color: #3498db;
    cursor: pointer;
  }
  
  .forgot-password:hover {
    text-decoration: underline;
  }
</style>