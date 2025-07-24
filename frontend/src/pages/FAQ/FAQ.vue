<template>
  <div class="faq-container">
    <div class="faq-header">
      <h1 class="faq-title">常见问题</h1>
      <p class="faq-subtitle">查找您在使用过程中可能遇到的问题</p>
    </div>
    
    <div class="search-container">
      <input
        type="text"
        class="search-input"
        placeholder="搜索问题..."
        v-model="searchQuery"
        @input="filterQuestions"
      >
    </div>
    
    <div class="faq-list">
      <div
        v-for="(question, index) in filteredQuestions"
        :key="index"
        class="faq-item"
      >
        <div class="faq-question" @click="toggleAnswer(index)">
          <span class="question-text">{{ question.text }}</span>
          <span class="question-icon">{{ isExpanded[index] ? '-' : '+' }}</span>
        </div>
        <div 
          class="faq-answer" 
          :class="{ expanded: isExpanded[index] }"
        >
          {{ question.answer }}
        </div>
      </div>
      
      <div v-if="filteredQuestions.length === 0" class="no-results">
        没有找到匹配的问题，请尝试其他关键词。
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      searchQuery: '',
      isExpanded: [],
      questions: [
        {
          text: '如何添加新的医疗病例？',
          answer: '要添加新的医疗病例，请点击侧边栏中的“新增数据”菜单项，填写病例表单，包括患者信息、症状描述、诊断结果和治疗方案，然后点击提交按钮。'
        },
        {
          text: '如何更新我的个人资料？',
          answer: '要更新您的个人资料，请点击侧边栏中的“个人资料”菜单项，填写更新表单，包括用户名、电子邮箱和手机号码，然后点击更新资料按钮。'
        },
        {
          text: '如何查看历史记录？',
          answer: '要查看历史记录，请点击侧边栏中的“历史记录”菜单项。您将看到所有历史记录的列表，可以点击查看详细信息。'
        },
        {
          text: '如何导出数据？',
          answer: '要导出数据，请点击侧边栏中的“历史记录”菜单项，然后点击页面右上角的导出按钮。您可以选择导出为CSV或Excel格式。'
        },
        {
          text: '忘记密码怎么办？',
          answer: '如果您忘记了密码，请点击登录页面中的“忘记密码”链接。我们将向您的注册邮箱发送一个重置密码的链接。'
        },
        {
          text: '如何联系技术支持？',
          answer: '您可以通过点击页面底部的“联系我们”链接与我们的技术支持团队联系。我们通常在24小时内回复。'
        }
      ]
    };
  },
  
  computed: {
    filteredQuestions() {
      if (!this.searchQuery) {
        return this.questions;
      }
      return this.questions.filter(question => 
        question.text.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    }
  },
  
  methods: {
    toggleAnswer(index) {
      this.$set(this.isExpanded, index, !this.isExpanded[index]);
    },
    
    filterQuestions() {
      // 输入框内容变化时重新过滤问题
    }
  },
  
  created() {
    // 初始化展开状态数组
    this.isExpanded = new Array(this.questions.length).fill(false);
  }
};
</script>

<style scoped lang="css">
.faq-container {
  padding: 32px;
  background-color: #f5f7fa;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.faq-header {
  text-align: center;
  margin-bottom: 32px;
}

.faq-title {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 8px;
}

.faq-subtitle {
  font-size: 16px;
  color: #7f8c8d;
}

.search-container {
  margin-bottom: 24px;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 16px;
  transition: all 0.3s;
  outline: none;
}

.search-input:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.faq-list {
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.faq-item {
  border-bottom: 1px solid #f0f0f0;
}

.faq-question {
  padding: 16px 24px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
  color: #2c3e50;
  transition: background-color 0.2s;
}

.faq-question:hover {
  background-color: #f8f9fa;
}

.question-icon {
  font-size: 20px;
  color: #3498db;
}

.faq-answer {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease-out;
  padding: 0 24px;
  color: #555;
  font-size: 15px;
  line-height: 1.6;
}

.faq-answer.expanded {
  max-height: 500px;
  padding: 0 24px 16px;
}

.no-results {
  padding: 24px;
  text-align: center;
  color: #7f8c8d;
  font-size: 16px;
}
</style>