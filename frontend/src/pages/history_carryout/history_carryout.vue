<template>
  <div class="flex-col justify-start items-start page">
    <div v-if="isLoading">加载中...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else class="section">
      <h2>病例 #{{ caseDetail.caseId }}</h2>

      <div class="case-detail">
        <p><strong>患者 SN:</strong> {{ caseDetail.patient_SN }}</p>
        <p><strong>性别:</strong> {{ caseDetail.gender }}</p>
        <p><strong>年龄:</strong> {{ caseDetail.age }}</p>
        <p><strong>吸烟状态:</strong> {{ caseDetail.smoking_status === "是" ? "吸烟" : "不吸烟" }}</p>
        <p><strong>来源省份:</strong> {{ caseDetail.origin_province || '无' }}</p>
        <p><strong>上海行政区划:</strong> {{ caseDetail.shanghai_administrative_division || '无' }}</p>
        <p><strong>诊断结果:</strong> {{ caseDetail.diagnosis }}</p>
        <p><strong>确诊时间:</strong> {{ caseDetail.diagnosis_year }}年{{ caseDetail.diagnosis_month | formatMonth }}月</p>
      </div>
    </div>

    <!-- AI 预测报告 -->
    <div v-if="aiReport">
      <h3>AI 预测报告</h3>
      <p><strong>5 年发病风险：</strong>{{ aiReport.risk }}%</p>
      <p><strong>原因：</strong>{{ aiReport.reason }}</p>
      <p><strong>建议：</strong>{{ aiReport.risk >= 50 ? '强烈建议戒烟并定期低剂量 CT ' : '保持年度体检即可' }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      caseDetail: null,
      aiReport: null,
      isLoading: false,
      error: null
    };
  },
  filters: {
    formatMonth(month) {
      return month ? String(month).padStart(2, '0') : '无';
    }
  },
  created() {
    const caseId = this.$route.params.caseId;
    this.fetchCaseDetail(caseId);
  },
  methods: {
    async fetchCaseDetail(caseId) {
      this.isLoading = true;
      try {
        const response = await fetch(`http://localhost:3000/api/cases/${caseId}`);
        if (!response.ok) {
          throw new Error('获取详情失败');
        }
        const data = await response.json();
        this.caseDetail = data;

        const payload = {
          age: this.caseDetail.age,
          gender: this.caseDetail.gender,
          smoking_status: this.caseDetail.smoking_status,
          diagnosis: this.caseDetail.diagnosis,
          origin_province: this.caseDetail.origin_province
        };
        const predictionResponse = await fetch('http://localhost:3000/api/riskPrediction', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!predictionResponse.ok) {
          throw new Error('获取预测结果失败');
        }

        this.aiReport = await predictionResponse.json();
      } catch (err) {
        this.error = err.message;
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped lang="css">
.page {
  padding: 97px 0 141px;
  background-color: #c1e3e8;
  width: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  height: 100%;
}

.section {
  margin-left: 12px;
  background-color: #ffffff;
  width: 1385px;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.case-detail {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  font-size: 16px;
  line-height: 1.5;
}

.case-detail p strong {
  color: #333;
  min-width: 120px;
  display: inline-block;
}

.risk-high {
  background-color: #ffe5ec !important;
  border-left: 4px solid #ff4d6d;
}
</style>