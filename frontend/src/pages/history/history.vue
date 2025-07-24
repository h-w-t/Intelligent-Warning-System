<template>
  <div class="history-container">
    <div class="history-header">
      <h1 class="history-title">历史记录</h1>
      <p class="history-subtitle">查看和管理您的病例记录</p>
    </div>

    <div class="search-container">
      <input
        type="text"
        class="search-input"
        placeholder="搜索病例..."
        v-model="searchQuery"
        @input="filterCases"
      />
    </div>

    <div class="history-filters">
      <!-- 第一行：患者 + 性别 -->
      <div class="filter-item short">
        <label for="filter-patient" class="filter-label">患者：</label>
        <select
          id="filter-patient"
          class="filter-select"
          v-model="patientFilter"
          @change="filterCases"
        >
          <option value="">全部患者</option>
          <option v-for="patient in uniquePatients" :key="patient" :value="patient">
            {{ patient }}
          </option>
        </select>
      </div>

      <div class="filter-item short">
        <label for="filter-gender" class="filter-label">性别：</label>
        <select
          id="filter-gender"
          class="filter-select"
          v-model="genderFilter"
          @change="filterCases"
        >
          <option value="">全部性别</option>
          <option value="男">男</option>
          <option value="女">女</option>
          <option value="其他">其他</option>
        </select>
      </div>

      <!-- 第二行：年/月 + 癌症类型 -->
      <div class="filter-group">
        <div class="filter-item complex">
          <label for="filter-year" class="filter-label">年/月筛选：</label>
          <div style="display: flex; gap: 8px;">
            <select
              id="filter-year"
              class="filter-select"
              v-model="yearFilter"
              @change="filterCases"
            >
              <option value="">全部年份</option>
              <option v-for="year in availableYears" :key="year" :value="year">
                {{ year }}
              </option>
            </select>
            <select
              id="filter-month"
              class="filter-select"
              v-model="monthFilter"
              @change="filterCases"
            >
              <option value="">全部月份</option>
              <option v-for="month in monthOptions" :key="month.value" :value="month.value">
                {{ month.text }}
              </option>
            </select>
          </div>
        </div>

        <div class="filter-item">
          <label for="filter-cancer-type" class="filter-label">癌症类型：</label>
          <select
            id="filter-cancer-type"
            class="filter-select"
            v-model="cancerTypeFilter"
            @change="filterCases"
          >
            <option value="">全部类型</option>
            <option v-for="type in uniqueCancerTypes" :key="type" :value="type">
              {{ type }}
            </option>
          </select>
        </div>
      </div>

      <div class="filter-item">
        <label for="filter-age" class="filter-label">年龄：</label>
        <input
          type="number"
          id="filter-age"
          class="filter-input"
          v-model="ageFilter"
          @change="filterCases"
        />
      </div>

      <div class="filter-item">
        <label for="filter-smoker" class="filter-label">吸烟状态：</label>
        <select
          id="filter-smoker"
          class="filter-select"
          v-model="smokerFilter"
          @change="filterCases"
        >
          <option value="">全部</option>
          <option value="true">吸烟</option>
          <option value="false">不吸烟</option>
        </select>
      </div>
    </div>

    <!-- 加载状态显示 -->
    <div v-if="isLoading" class="loading">
      <p>加载中...</p>
    </div>

    <!-- 错误信息显示 -->
    <div v-if="error" class="error">
      <p>{{ error }}</p>
    </div>

    <div v-else class="history-list">
      <div v-if="filteredCases.length > 0">
        <div
          v-for="(caseItem, index) in paginatedCases"
          :key="caseItem.caseId"
          class="history-item"
          :class="{ 'risk-high': riskMap[caseItem.caseId]?.risk >= 50 }"
        >
          <div class="history-item-header" @click="toggleCase(index)">
            <div class="history-item-title">
              <span class="case-id">病例 #{{ caseItem.caseId }}</span>
              
              <span class="case-date">
                {{ formatDateForDisplay(caseItem.diagnosis_year, caseItem.diagnosis_month) }}
              </span>
            </div>
            <span class="case-icon">{{ isExpanded[index] ? "-" : "+" }}</span>
          </div>
          <div class="history-item-content" :class="{ expanded: isExpanded[index] }">
            <div class="case-patient">
              <strong>患者SN:</strong>{{ caseItem.patient_SN }}
            </div>
            <div class="case-diagnosis">
              <strong>诊断结果：</strong>{{ caseItem.diagnosis }}
            </div>

            <div class="case-details">
              <strong>年龄：</strong>{{ caseItem.age }}
            </div>
            <div class="case-details">
              <strong>性别：</strong>{{ caseItem.gender }}
            </div>
            <div class="case-details">
              <strong>吸烟状态：</strong>{{ caseItem.smoking_status === "是" ? "吸烟" : "不吸烟" }}
            </div>
            <div class="case-details">
              <strong>癌症类型：</strong>{{ caseItem.diagnosis }}
            </div>
            <div class="case-details">
              <strong>确诊时间：</strong>{{ formatDateForDisplay(caseItem.diagnosis_year, caseItem.diagnosis_month) }}
            </div>
            <div class="case-actions">
              <button class="detail-button" @click.stop="viewDetails(caseItem)">查看详情</button>
              <!--<button class="export-button" @click.stop="exportCase(caseItem)">导出</button>-->
              <button class="delete-button" @click.stop="deleteCase(caseItem)">删除</button>
            </div>
          </div>
        </div>

        <!-- 分页控制 -->
        <div class="pagination-controls">
          <button
            class="pagination-button"
            @click="prevPage"
            :disabled="currentPage === 1"
          >
            上一页
          </button>
          <span class="pagination-info">
            第 {{ currentPage }} 页，共 {{ totalPages }} 页
          </span>
          <button
            class="pagination-button"
            @click="nextPage"
            :disabled="currentPage === totalPages"
          >
            下一页
          </button>
        </div>
      </div>
      <div v-else class="no-results">
        <p>没有找到匹配的病例记录。</p>
      </div>
    </div>
  </div>
</template>

<script>
import History_carryout from '../history_carryout/history_carryout.vue';
import { formatDateForDisplay } from '../../utils/dateUtils'; // 导入日期格式化工具
import { fetchCases, deleteCaseById, fetchForecastByIds } from '../../utils/api'; // 导入 API 工具函数

export default {
data() {
  return {
    searchQuery: '',
    patientFilter: '',
    dateFilter: '',
    yearFilter: '',
    monthFilter: '',
    ageFilter: '',
    genderFilter: '',
    cancerTypeFilter: '',
    smokerFilter: '',
    isExpanded: [],
    cases: [],
    isLoading: false,
    error: null,
    currentPage: 1,
    itemsPerPage: 10,
    riskMap: {},
    totalCount: 0 // 新增 totalCount
  };
},

computed: {
    monthOptions() {
      return [
        { value: '1', text: '一月' },
        { value: '2', text: '二月' },
        { value: '3', text: '三月' },
        { value: '4', text: '四月' },
        { value: '5', text: '五月' },
        { value: '6', text: '六月' },
        { value: '7', text: '七月' },
        { value: '8', text: '八月' },
        { value: '9', text: '九月' },
        { value: '10', text: '十月' },
        { value: '11', text: '十一月' },
        { value: '12', text: '十二月' }
      ];
    },
    availableYears() {
      const years = this.cases
        .map(c => c.diagnosis_year)
        .filter(year => year && year.toString().length === 4);
      
      return ['', ...new Set(years)].sort((a, b) => b - a);
    },
    uniquePatients() {
      const patients = this.cases.map(caseItem => caseItem.patient_SN);
      const uniquePatients = [...new Set(patients)];
      return [''].concat(
        uniquePatients.sort((a, b) => {
          const numA = a.match(/\d+/)?.[0] || '';
          const numB = b.match(/\d+/)?.[0] || '';
          const prefixA = a.replace(/\d+/g, '');
          const prefixB = b.replace(/\d+/g, '');
          if (prefixA === prefixB) {
            return parseInt(numA, 10) - parseInt(numB, 10);
          }
          return a.localeCompare(b);
        })
      );
    },
    uniqueCancerTypes() {
      const types = this.cases.map(caseItem => caseItem.diagnosis);
      return [...new Set(types)];
    },
    filteredCases() {
      // filteredCases 现在直接返回 this.cases，因为过滤和分页都在后端完成
      return this.cases;
    },
    paginatedCases() {
      // paginatedCases 不再需要切片，因为后端已经返回了当前页的数据
      return this.cases;
    },
    totalPages() {
      // totalPages 现在基于后端返回的总记录数
      return Math.ceil(this.totalCount / this.itemsPerPage);
    }
  },
  
  methods: {
    viewDetails(caseItem) {
      this.$router.push({
        name: 'history_carryout', 
        params: { caseId: caseItem.caseId }
      });
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
        this.fetchFilteredCases(); // 重新获取数据
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
        this.fetchFilteredCases(); // 重新获取数据
      }
    },
    filterCases() {
      this.currentPage = 1; // 筛选条件改变时重置到第一页
      this.fetchFilteredCases(); // 重新从后端获取数据
    },
    /**
     * 异步获取过滤后的病例数据并更新组件状态
     * @param {Object} context - Vue组件上下文对象
     * @returns {Promise<void>} 无直接返回值，通过响应式属性更新组件状态
     */
    async fetchFilteredCases() {
      this.isLoading = true;
      this.error = null;
      try {
        const params = {
          page: this.currentPage,
          limit: this.itemsPerPage,
          search: this.searchQuery,
          patient: this.patientFilter,
          year: this.yearFilter,
          month: this.monthFilter,
          age: this.ageFilter,
          gender: this.genderFilter,
          cancerType: this.cancerTypeFilter,
          isSmoker: this.smokerFilter
        };
        const response = await fetchCases(params);
        
        // 处理病例响应数据
        this.cases = Array.isArray(response.cases) ? response.cases : [];
        this.totalCount = response.total_count || 0;
        
        // 初始化病例展开状态数组
        // 为每个病例创建对应的展开状态控制项，默认全部折叠
        this.isExpanded = new Array(this.cases.length).fill(false);
        
        // 只有当有病例时才去获取风险数据
        if (this.cases.length > 0) {
          // 并行获取病例风险数据
          // 通过caseId数组批量查询风险信息
          await this.fetchRiskData(this.cases.map(c => c.caseId));
        } else {
          this.riskMap = {}; // 如果没有病例，清空风险数据
        }
      } catch (err) {
        // 全局错误处理
        // 设置用户提示信息并输出详细错误到控制台
        this.error = '无法加载病例数据。请稍后再试。';
        console.error('Error fetching cases:', err);
      } finally {
        // 最终状态清理
        // 无论成功与否都重置加载状态
        this.isLoading = false;
      }
    },
    async fetchRiskData(caseIds) {
      try {
        const response = await fetchForecastByIds(caseIds);
        this.riskMap = response.reduce((acc, item) => {
          acc[item.caseId] = item;
          return acc;
        }, {});
      } catch (err) {
        console.error('Error fetching risk data:', err);
        // 可以选择不设置错误信息，因为病例数据已经加载
      }
    },
    formatDateForDisplay(year, month) {
      if (!year || !month) return '未知日期';
      return `${year}年${month}月`;
    },
    async deleteCase(caseItem) {
      if (confirm(`确定要删除病例 #${caseItem.caseId} 吗？`)) {
        try {
          await deleteCaseById(caseItem.caseId);
          alert('病例删除成功！');
          this.fetchFilteredCases(); // 重新加载数据
        } catch (error) {
          alert('删除病例失败。');
          console.error('Error deleting case:', error);
        }
      }
    },
    toggleCase(index) {
      this.$set(this.isExpanded, index, !this.isExpanded[index]);
    }
  },
  created() {
    this.fetchFilteredCases();
    // this.$root.$on('new-case-added', this.fetchFilteredCases); // 暂时注释，因为 $root.$on 在 Vue 3 中已移除
  },
  watch: {
    '$route.query.t'() {
      this.fetchFilteredCases();
    }
  },
  beforeUnmount() { // Vue 3 中使用 beforeUnmount 替代 beforeDestroy
    // this.$root.$off('new-case-added', this.fetchFilteredCases); // 暂时注释
  }
};
</script>

<style scoped lang="css">
.history-container {
  padding: 32px;
  background-color: #f5f7fa;
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.history-header {
  text-align: center;
  margin-bottom: 32px;
}

.history-title {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 8px;
}

.history-subtitle {
  font-size: 16px;
  color: #7f8c8d;
}

.search-container {
  margin-bottom: 20px;
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

.history-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 24px;
  padding: 16px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.filter-group {
  display: flex;
  gap: 20px;
  align-items: center;
  width: 100%;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 200px;
  flex: 1 1 200px;
}

.filter-item.short .filter-select {
  max-width: 100px;
}

.filter-label {
  font-size: 14px;
  color: #555;
  white-space: nowrap;
  margin-right: 8px;
}

.filter-select,
.filter-input,
.filter-date {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  max-width: 120px;
}

.filter-select:focus,
.filter-date:focus {
  border-color: #3498db;
}

@media (max-width: 768px) {
  .filter-group {
    flex-direction: column;
    align-items: flex-start;
  }

  .filter-item.complex,
  .filter-item:not(.short) {
    min-width: 100%;
  }
}
.history-item {
  border-bottom: 1px solid #f0f0f0;
  overflow: hidden;
  transition: background-color 0.2s;
}

.history-item-header {
  padding: 16px 24px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
  color: #2c3e50;
  background-color: #ffffff;
  transition: background-color 0.2s;
}

.history-item-header:hover {
  background-color: #f8f9fa;
}

.history-item-title {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.case-id {
  font-weight: 600;
}

.case-date {
  font-size: 14px;
  color: #7f8c8d;
}

.case-icon {
  font-size: 20px;
  color: #3498db;
  transition: transform 0.3s ease;
}

/* 展开动画 */
.history-item-content {
  max-height: 0;
  overflow: hidden;
  padding: 0;
  background-color: #fbfcfd;
  transition: all 0.3s ease-out;
  border-top: 1px dashed #e0e0e0;
}

.history-item-content.expanded {
  max-height: 500px;
  padding: 16px 24px;
  border-top: 1px solid #e0e0e0;
}

/* 内容项样式 */
.case-details {
  margin-bottom: 8px;
  font-size: 14px;
  color: #555;
}

/* 按钮样式 */
.case-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.detail-button,
.export-button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.detail-button {
  background-color: #3498db;
  color: white;
}

.detail-button:hover {
  background-color: #2980b9;
}

.export-button {
  background-color: #f8f9fa;
  color: #555;
  border: 1px solid #e0e0e0;
}

.export-button:hover {
  background-color: #f0f0f0;
}
.delete-button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  background-color: #e74c3c;
  color: white;
  transition: all 0.2s;
}

.delete-button:hover {
  background-color: #c0392b;
}

/* 加载样式 */
.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  font-size: 18px;
  color: #3498db;
}

/* 错误信息样式 */
.error {
  padding: 20px;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 4px;
  text-align: center;
}

/* 分页样式 */
.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 24px;
  gap: 16px;
}

.pagination-button {
  padding: 8px 16px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.pagination-button:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 14px;
  color: #7f8c8d;
}

/* 无结果样式 */
.no-results {
  padding: 30px;
  text-align: center;
  color: #7f8c8d;
  font-size: 16px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.risk-high {
  background-color: #ffe5ec !important;
  border-left: 4px solid #ff4d6d;
}
</style>
