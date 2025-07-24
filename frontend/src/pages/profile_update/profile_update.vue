<template>
  <div class="flex-col justify-start page">
    <div class="section">
      <div class="auth-container">
        <div class="auth-header">
          <h1 class="title">新增医疗病例</h1>
          <p class="subtitle">请填写以下信息以添加新的医疗病例</p>
        </div>

        <form class="auth-form" @submit.prevent="handleSubmit">
          <!-- 患者基本信息 -->
          <div class="form-section">
            <div class="form-section-header">患者基本信息</div>
            <div class="form-group">
              <label for="patient-age" class="form-label">年龄</label>
              <input
                type="number"
                id="patient-age"
                class="form-input"
                placeholder="请输入年龄"
                v-model.number="formData.age"
                required
              />
            </div>
            <div class="form-group">
              <label for="patient-gender" class="form-label">性别</label>
              <select
                id="patient-gender"
                class="form-input"
                v-model="formData.gender"
                required
              >
                <option value="">请选择性别</option>
                <option value="male">男</option>
                <option value="female">女</option>
                <option value="other">其他</option>
              </select>
            </div>
          </div>

          <!-- 地域信息 -->
          <div class="form-section">
            <div class="form-section-header">地域信息</div>
            <div class="form-group">
              <label for="origin-province" class="form-label">原籍省份</label>
              <input
                type="text"
                id="origin-province"
                class="form-input"
                placeholder="请输入原籍省份（如：江苏省）"
                v-model="formData.originProvince"
                required
              />
            </div>
            <div class="form-group">
              <label for="shanghai-division" class="form-label">上海行政区域</label>
              <input
                type="text"
                id="shanghai-division"
                class="form-input"
                placeholder="请输入上海行政区域（如：浦东新区）"
                v-model="formData.shanghaiDivision"
                required
              />
            </div>
          </div>

          <!-- 病例详情 -->
          <div class="form-section">
            <div class="form-section-header">病例详情</div>
            <div class="form-group">
              <label for="case-date" class="form-label">确诊日期</label>
              <input
                type="date"
                id="case-date"
                class="form-input"
                v-model="formData.caseDate"
                required
              />
            </div>
          </div>

          <!-- 诊断结果 -->
          <div class="form-section">
            <div class="form-section-header">诊断结果</div>
            <div class="form-group">
              <label for="diagnosis" class="form-label">癌症类型</label>
              <input
                type="text"
                id="diagnosis"
                class="form-input"
                placeholder="例如：肺癌、乳腺癌等"
                v-model="formData.diagnosis"
                required
              />
            </div>
            <div class="form-group">
              <label for="smoking-status" class="form-label">吸烟状态</label>
              <select
                id="smoking-status"
                class="form-input"
                v-model="formData.smokingStatus"
                required
              >
                <option value="">请选择吸烟状态</option>
                <option value="是">吸烟</option>
                <option value="否">不吸烟</option>
              </select>
            </div>
          </div>

          <!-- 提交按钮 -->
          <div class="form-actions">
            <button 
              type="submit" 
              class="auth-button"
              :disabled="isSubmitting"
            >
              <span v-if="isSubmitting">提交中...</span>
              <span v-else>提交病例</span>
            </button>
          </div>
          
          <!-- 错误信息显示 -->
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
          
          <!-- 端点验证提示 -->
          <div v-if="apiError" class="api-error">
            <i class="fas fa-exclamation-circle"></i> {{ apiError }}
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      formData: {
        age: null,
        gender: '',
        caseDate: '',
        diagnosis: '',
        smokingStatus: '',
        originProvince: '',
        shanghaiDivision: ''
      },
      isSubmitting: false,
      errorMessage: null,
      apiError: null
    };
  },
  
  computed: {
    formattedDiagnosisDate() {
      if (!this.formData.caseDate) return null;
      
      const date = new Date(this.formData.caseDate);
      return {
        diagnosis_year: date.getFullYear().toString(),
        diagnosis_month: (date.getMonth() + 1).toString().padStart(2, '0')
      };
    }
  },

  methods: {
    generatePatientSN() {
      return 'SN' + Math.random().toString(36).substr(2, 9).toUpperCase();
    },

    async handleSubmit() {
      if (this.apiError) {
        this.errorMessage = "API服务不可用，无法提交数据";
        return;
      }

      this.errorMessage = null;
      
      // 验证必填字段
      if (
        !this.formData.age ||
        !this.formData.gender ||
        !this.formData.caseDate ||
        !this.formData.diagnosis ||
        !this.formData.smokingStatus
      ) {
        this.errorMessage = '请填写所有带红色*号的字段';
        return;
      }

      this.isSubmitting = true;
      
      try {
        const patient_SN = this.generatePatientSN();
        const sequence_number = Math.floor(Math.random() * 1000000000);
        
        const postData = {
          sequence_number,
          patient_SN,
          gender: this.formData.gender === 'male' ? '男' : 
                 this.formData.gender === 'female' ? '女' : '其他',
          age: this.formData.age,
          origin_province: this.formData.originProvince,
          shanghai_administrative_division: this.formData.shanghaiDivision,
          diagnosis_year: this.formattedDiagnosisDate.diagnosis_year,
          diagnosis_month: this.formattedDiagnosisDate.diagnosis_month,
          diagnosis: this.formData.diagnosis,
          smoking_status: this.formData.smokingStatus
        };

        const response = await fetch('http://localhost:3000/api/cases', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(postData)
        });

        if (!response.ok) {
          let errorMsg = `API错误: ${response.status}`;
          
          try {
            const errorData = await response.json();
            if (errorData?.message) errorMsg = errorData.message;
          } catch (e) {
            console.warn("无法解析错误响应:", e);
          }
          
          throw new Error(errorMsg);
        }

        const result = await response.json();
        console.log('提交的数据:', postData);
        
        console.log('提交成功:', result);

        alert(`病例已成功保存！分配编号：${sequence_number}，SN：${patient_SN}`);
        this.resetForm();
        
        // 触发全局事件通知历史页面刷新
        this.$root.$emit('new-case-added');
        this.$router.push({ name: 'history', query: { t: Date.now() } });
        
      } catch (error) {
        console.error('提交失败:', error);
        this.errorMessage = error.message || `提交失败: ${error}`;
      } finally {
        this.isSubmitting = false;
      }
    },

    resetForm() {
      this.formData = {
        age: null,
        gender: '',
        caseDate: '',
        diagnosis: '',
        smokingStatus: '',
        originProvince: '',
        shanghaiDivision: ''
      };
      this.errorMessage = null;
    }
  }
};
</script>


<style scoped lang="css">
.page {
  padding: 32px 0;
  background-color: #f5f7fa;
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
  max-width: 800px;
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

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-section-header {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
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
  background-color: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 16px;
  transition: all 0.3s;
  outline: none;
}

.form-input:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
  background-color: #ffffff;
}

.form-textarea {
  padding: 12px;
  background-color: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 16px;
  transition: all 0.3s;
  outline: none;
  min-height: 100px;
  resize: vertical;
}

.form-textarea:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
  background-color: #ffffff;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.auth-button {
  padding: 14px 32px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.auth-button:hover:not(:disabled) {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.auth-button:disabled {
  background-color: #a0c4e3;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.error-message {
  margin-top: 15px;
  padding: 10px;
  background-color: #ffebee;
  border: 1px solid #ffcdd2;
  border-radius: 6px;
  color: #c62828;
  text-align: center;
  font-size: 14px;
}

.api-error {
  margin-top: 15px;
  padding: 15px;
  background-color: #fff8e1;
  border: 1px solid #ffd54f;
  border-radius: 6px;
  color: #e65100;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>