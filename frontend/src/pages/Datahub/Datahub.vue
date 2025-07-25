<template>
  <div class="data-hub-container">
    <h2>数据中台 - 空气污染趋势</h2>

    <!-- ➕ 新增按钮 -->
    <button class="add-data-btn" @click="showAddModal = true">
      ➕ 添加数据
    </button>

    <!-- 新增数据弹窗 -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal-content">
        <h3>新增环境数据</h3>
        <form @submit.prevent="submitNewData">
          <label>
            年：
            <input type="number" v-model.number="newData.diag_year" required />
          </label>
          <label>
            月：
            <input type="number" min="1" max="12" v-model.number="newData.diag_month" required />
          </label>
          <label>
            时间窗口：
            <select v-model.number="newData.window_months" required>
              <option :value="3">3 个月</option>
              <option :value="6">6 个月</option>
              <option :value="12">12 个月</option>
              <option :value="24">24 个月</option>
              <option :value="36">36 个月</option>
            </select>
          </label>

          <label v-for="key in pollutionKeys" :key="key">
            {{ key.toUpperCase() }}：
            <input type="number" step="0.1" v-model.number="newData[key]" />
          </label>

          <div class="modal-actions">
            <button type="submit" class="submit-btn">提交</button>
            <button type="button" @click="showAddModal = false">取消</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 原有内容 -->
    <div class="data-container">
      <div class="data-card air-quality-chart">
        <h3>空气质量指数 (AQI)</h3>
        <div class="chart-actions">
          <button @click="showDataZoomHint = true" class="chart-hint-btn">
            <span class="hint-icon">💡</span> 拖动帮助
          </button>
          <button @click="fetchAirPollutionData" class="refresh-btn">
            <span class="refresh-icon">🔄</span> 刷新数据
          </button>
        </div>

        <div v-if="loading" class="loading-indicator">
          <div class="spinner"></div>
          <p>正在从数据库加载数据...</p>
        </div>
        <div v-else-if="error" class="error-message">
          <p>⚠️ 数据加载失败: {{ error }}</p>
          <button @click="fetchAirPollutionData">重试</button>
        </div>
        <div v-show="airQualityData.dates.length > 0" ref="airQualityChart" class="chart"></div>
        <div v-if="!loading && !error && airQualityData.dates.length === 0" class="no-data-hint">
          <p>📊 没有可用的空气质量数据</p>
          <p>请选择不同的时间范围或添加更多数据</p>
        </div>
      </div>
    </div>

    <div class="filter-container">
      <div class="time-range-selector">
        <label for="timeRange">数据时间范围：</label>
        <select id="timeRange" v-model="selectedTimeRange" @change="fetchAirPollutionData">
          <option value="3_month">3个月</option>
          <option value="6_month">6个月</option>
          <option value="12_month">12个月</option>
          <option value="24_month">24个月</option>
          <option value="36_month">36个月</option>
        </select>
      </div>

      <div class="pollution-type-selector">
        <label>污染物指标：</label>
        <div class="checkbox-group">
          <label v-for="type in pollutionTypes" :key="type.value">
            <input type="checkbox" v-model="selectedPollutionTypes" :value="type.value">
            <span class="custom-checkbox" :style="{ backgroundColor: type.color }"></span>
            {{ type.label }}
          </label>
        </div>
      </div>
    </div>

    <!-- ▼ 筛选控制条 -->
    <div class="filter-bar">
      <label>年月筛选：<input type="month" v-model="filterMonth" /></label>
      <label>PM₂.₅ ≥ <input type="number" step="0.1" v-model.number="filterPM25Min" /></label>
      <label>AQI ≥ <input type="number" step="0.1" v-model.number="filterAQIMin" /></label>
      <button @click="applyFilter">🔍 应用筛选</button>
    </div>

    <!-- 列表区域 -->
    <div class="data-list-container">
      <div class="list-header">
        <h3>逐月空气质量明细</h3>
        <div>
          <button
            v-if="selectedRows.length"
            @click="deleteSelected"
            class="delete-batch-btn"
          >
            🗑️ 删除选中 ({{ selectedRows.length }})
          </button>
          <button @click="fetchAirPollutionData" class="refresh-btn">
            <span class="refresh-icon">🔄</span> 刷新列表
          </button>
        </div>
      </div>

      <div v-if="loadingList" class="loading-indicator">
        <div class="spinner"></div>
        <p>正在加载列表...</p>
      </div>
      <div v-else-if="airQualityList.length === 0" class="no-data-hint">
        <p>暂无数据</p>
      </div>

      <div v-else class="list-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>
                <input
                  type="checkbox"
                  :checked="selectedRows.length === filteredList.length && filteredList.length"
                  @change="toggleSelectAll"
                />
              </th>
              <th>年月</th>
              <th>AQI</th>
              <th>PM₂.₅</th>
              <th>PM₁₀</th>
              <th>O₃</th>
              <th>CO</th>
              <th>NO₂</th>
              <th>SO₂</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in pagedList" :key="idx">
              <td>
                <input
                  type="checkbox"
                  :value="row.measure_period"
                  v-model="selectedRows"
                />
              </td>
              <td>{{ row.measure_period }}</td>
              <td>{{ row.aqi?.toFixed(1) ?? '-' }}</td>
              <td>{{ row.pm25?.toFixed(1) ?? '-' }}</td>
              <td>{{ row.pm10?.toFixed(1) ?? '-' }}</td>
              <td>{{ row.o3?.toFixed(1) ?? '-' }}</td>
              <td>{{ row.co?.toFixed(1) ?? '-' }}</td>
              <td>{{ row.no2?.toFixed(1) ?? '-' }}</td>
              <td>{{ row.so2?.toFixed(1) ?? '-' }}</td>
              <td>
                <button
                  @click="deleteSingle(row.measure_period)"
                  class="delete-single-btn"
                  title="删除此条"
                >
                  ❌
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="pagination" v-if="airQualityList.length > pageSize">
          <button @click="prevPage" :disabled="currentPage === 1">上一页</button>
          <span>{{ currentPage }} / {{ totalPages }}</span>
          <button @click="nextPage" :disabled="currentPage === totalPages">下一页</button>
        </div>
      </div>
    </div>

    <!-- 拖动提示 -->
    <div class="chart-hint" v-if="showDataZoomHint">
      <div class="hint-content">
        <span class="hint-icon">🔍</span>
        <p>您可在此区域左右拖动，查看不同时间段的数据</p>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'DataHub',
  data() {
    return {
      /* ➕ 新增状态 */
      showAddModal: false,
      newData: {
        patient_sn: '',
        diag_year: new Date().getFullYear(),
        diag_month: new Date().getMonth() + 1,
        window_months: 12,
        aqi: null,
        pm2_5: null,
        pm10: null,
        o3: null,
        co: null,
        no2: null,
        so2: null,
      },
      pollutionKeys: ['aqi', 'pm2_5', 'pm10', 'o3', 'co', 'no2', 'so2'],

      /* ✅ 新增缺失的筛选字段 */
      filterMonth: '',
      filterPM25Min: null,
      filterAQIMin: null,

      /* ✅ 新增删除相关 */
      selectedRows: [],

      /* === 原有状态 === */
      selectedTimeRange: '3_month',
      selectedPollutionTypes: ['aqi', 'pm25', 'pm10', 'o3'],
      pollutionTypes: [
        { value: 'aqi', label: 'AQI', color: '#5470c6' },
        { value: 'pm25', label: 'PM2.5', color: '#91cc75' },
        { value: 'pm10', label: 'PM10', color: '#fac858' },
        { value: 'o3', label: 'O₃', color: '#ee6666' },
        { value: 'co', label: 'CO', color: '#73c0de' },
        { value: 'no2', label: 'NO₂', color: '#3ba272' },
        { value: 'so2', label: 'SO₂', color: '#fc8452' }
      ],
      airQualityData: { dates: [], aqi: [], pm25: [], pm10: [], o3: [], co: [], no2: [], so2: [] },
      loading: false,
      error: null,
      airQualityChart: null,
      intervalMonths: { '3_month': 3, '6_month': 6, '12_month': 12, '24_month': 24, '36_month': 36 },
      showDataZoomHint: false,
      airQualityList: [],
      currentPage: 1,
      pageSize: 20,
      loadingList: false
    };
  },
  watch: {
    selectedPollutionTypes() {
      this.initAirQualityChart();
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.filteredList.length / this.pageSize);
    },
    pagedList() {
      const start = (this.currentPage - 1) * this.pageSize;
      return this.filteredList.slice(start, start + this.pageSize);
    },
    filteredList() {
      let list = this.airQualityList;
      if (this.filterMonth) {
        list = list.filter(r => r.measure_period === this.filterMonth);
      }
      if (this.filterPM25Min != null) {
        list = list.filter(r => (r.pm25 ?? 0) >= this.filterPM25Min);
      }
      if (this.filterAQIMin != null) {
        list = list.filter(r => (r.aqi ?? 0) >= this.filterAQIMin);
      }
      return list;
    }
  },
  mounted() {
    this.fetchAirPollutionData();
    window.addEventListener('resize', this.resizeChart);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.resizeChart);
    if (this.airQualityChart) {
      this.airQualityChart.dispose();
    }
  },
  methods: {
    /* ➕ 新增：提交数据 */
    async submitNewData() {
      const suffix = `${this.newData.window_months}_month_avg`;
      const payload = {
        patient_sn: null,
        diag_year: this.newData.diag_year,
        diag_month: this.newData.diag_month,
        [`aqi_${suffix}`]: this.newData.aqi,
        [`pm2_5_${suffix}`]: this.newData.pm2_5,
        [`pm10_${suffix}`]: this.newData.pm10,
        [`o3_${suffix}`]: this.newData.o3,
        [`co_${suffix}`]: this.newData.co,
        [`no2_${suffix}`]: this.newData.no2,
        [`so2_${suffix}`]: this.newData.so2
      };

      try {
        const res = await fetch('http://localhost:3000/api/environment/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error(await res.text());
        this.showAddModal = false;
        this.resetNewData();
        await this.fetchAirPollutionData();
      } catch (e) {
        alert('提交失败：' + e.message);
      }
    },
    resetNewData() {
      Object.assign(this.newData, {
        diag_year: new Date().getFullYear(),
        diag_month: new Date().getMonth() + 1,
        window_months: 12,
        aqi: null,
        pm2_5: null,
        pm10: null,
        o3: null,
        co: null,
        no2: null,
        so2: null
      });
    },

    /* ✅ 单条删除 */
    async deleteSingle(measurePeriod) {
      if (!confirm('确定删除该条记录？')) return;
      const [y, m] = measurePeriod.split('-').map(Number);
      await fetch(`http://localhost:3000/api/environment/${y}/${m}`, { method: 'DELETE' });
      await this.fetchAirPollutionData();
    },

    /* ✅ 批量删除 */
    async deleteSelected() {
      if (!confirm(`确定删除选中的 ${this.selectedRows.length} 条记录？`)) return;
      for (const period of this.selectedRows) {
        const [y, m] = period.split('-').map(Number);
        await fetch(`http://localhost:3000/api/environment/${y}/${m}`, { method: 'DELETE' });
      }
      this.selectedRows = [];
      await this.fetchAirPollutionData();
    },

    /* ✅ 全选/取消全选 */
    toggleSelectAll(e) {
      if (e.target.checked) {
        this.selectedRows = this.filteredList.map(r => r.measure_period);
      } else {
        this.selectedRows = [];
      }
    },

    applyFilter() {
      /* 触发 computed 更新即可 */
    },

    /* === 原有方法 === */
    async fetchAirPollutionData() {
      this.loadingList = this.loading = true;
      this.error = null;
      try {
        const months = this.intervalMonths[this.selectedTimeRange];
        const res = await fetch(`http://localhost:3000/api/environment?months=${months}`);
        if (!res.ok) throw new Error('API错误');
        const data = await res.json();
        this.airQualityList = data.sort((a, b) => a.measure_period.localeCompare(b.measure_period));
        this.airQualityData = {
          dates: this.airQualityList.map(d => d.measure_period),
          aqi: this.airQualityList.map(d => d.aqi),
          pm25: this.airQualityList.map(d => d.pm25),
          pm10: this.airQualityList.map(d => d.pm10),
          o3: this.airQualityList.map(d => d.o3),
          co: this.airQualityList.map(d => d.co),
          no2: this.airQualityList.map(d => d.no2),
          so2: this.airQualityList.map(d => d.so2)
        };
        this.currentPage = 1;
        this.$nextTick(() => this.initAirQualityChart());
      } catch (e) {
        this.error = e.message || '获取环境数据失败';
      } finally {
        this.loading = this.loadingList = false;
      }
    },
    initAirQualityChart() {
      const chartEl = this.$refs.airQualityChart;
      if (!chartEl) return;
      if (!this.airQualityData.dates.length) return;
      if (this.airQualityChart) this.airQualityChart.dispose();
      this.airQualityChart = echarts.init(chartEl);

      const cfg = {
        aqi: { name: 'AQI', color: '#5470c6' },
        pm25: { name: 'PM2.5', color: '#91cc75' },
        pm10: { name: 'PM10', color: '#fac858' },
        o3: { name: 'O₃', color: '#ee6666' },
        co: { name: 'CO', color: '#73c0de' },
        no2: { name: 'NO₂', color: '#3ba272' },
        so2: { name: 'SO₂', color: '#fc8452' }
      };

      const series = this.selectedPollutionTypes
        .filter(t => cfg[t])
        .map(t => ({
          name: cfg[t].name,
          type: 'line',
          data: this.airQualityData[t],
          smooth: true,
          lineStyle: { width: 3, color: cfg[t].color },
          symbol: 'circle',
          symbolSize: 6,
          itemStyle: { color: cfg[t].color }
        }));

      const total = this.airQualityData.dates.length;
      const showCount = 100;
      const startPercent = total > showCount
        ? Math.max(0, 100 - (showCount / total) * 100)
        : 0;

      const option = {
        title: { text: '空气质量趋势图', left: 'center' },
        tooltip: { trigger: 'axis' },
        legend: { data: series.map(s => s.name), bottom: 10 },
        grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
        xAxis: {
          type: 'category',
          data: this.airQualityData.dates,
          axisLabel: { interval: 0, rotate: total > 6 ? 45 : 0 }
        },
        yAxis: { type: 'value', name: '浓度' },
        dataZoom: [
          { type: 'slider', start: startPercent, end: 100, bottom: 25 },
          { type: 'inside', start: startPercent, end: 100 }
        ],
        series
      };
      this.airQualityChart.setOption(option);
      window.addEventListener('resize', () => this.airQualityChart.resize());
    },
    resizeChart() {
      if (this.airQualityChart) this.airQualityChart.resize();
    },
    prevPage() {
      if (this.currentPage > 1) this.currentPage--;
    },
    nextPage() {
      if (this.currentPage < this.totalPages) this.currentPage++;
    }
  }
};
</script>

<style scoped>
/* 基础变量 */
:root {
  --bg: #f7fafc;
  --bg-card: #ffffff;
  --border: #e2e8f0;
  --primary: #0ea5e9;
  --primary-light: #e0f2fe;
  --text-primary: #1e293b;
  --text-secondary: #475569;
  --success: #10b981;
  --danger: #ef4444;
}

/* 全局 */
.data-hub-container {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  padding: 32px 24px;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

/* 卡片通用 */
.data-card,
.filter-container,
.data-list-container {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.2s;
}
.data-card:hover,
.filter-container:hover,
.data-list-container:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* 标题 */
h2 { font-size: 26px; font-weight: 700; color: var(--primary); margin: 0 0 8px; }
h3 { font-size: 18px; font-weight: 600; color: var(--text-primary); margin: 0 0 16px; }

/* 按钮 */
.chart-hint-btn,
.refresh-btn,
.add-data-btn,
.submit-btn,
.delete-batch-btn,
.delete-single-btn {
  background: var(--primary-light);
  border: 1px solid var(--primary);
  color: var(--primary);
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.chart-hint-btn:hover,
.refresh-btn:hover,
.add-data-btn:hover,
.submit-btn:hover,
.delete-batch-btn:hover {
  background: var(--primary);
  color: #fff;
}
.delete-single-btn {
  padding: 2px 6px;
  font-size: 12px;
  background: var(--danger);
  color: #fff;
  border-color: var(--danger);
}
.delete-single-btn:hover {
  background: #dc2626;
}

/* 图表 */
.chart { width: 100%; height: 400px; }

/* 过滤器 */
.filter-container { display: flex; flex-wrap: wrap; gap: 20px; }
select,
.checkbox-group label {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 12px;
  color: var(--text-primary);
  font-size: 14px;
  transition: border-color 0.2s;
}
select:focus,
.checkbox-group label:focus-within {
  border-color: var(--primary);
  outline: none;
}
.custom-checkbox {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 3px;
  margin-right: 6px;
}

/* 列表 */
.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.list-header h3 { margin: 0; }
.data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.data-table th,
.data-table td { padding: 10px; border-bottom: 1px solid var(--border); text-align: center; }
.data-table th { background: var(--primary-light); color: var(--primary); font-weight: 600; }
.data-table tr:hover { background: #f1f5f9; }

/* 分页 */
.pagination { display: flex; justify-content: center; align-items: center; gap: 12px; margin-top: 16px; }
.pagination button { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 4px 10px; color: var(--primary); cursor: pointer; transition: background 0.2s, color 0.2s; }
.pagination button:hover:not(:disabled) { background: var(--primary); color: #fff; }
.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }

/* 加载 / 空态 */
.loading-indicator,
.error-message,
.no-data-hint { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 160px; color: var(--text-secondary); }
.spinner { width: 36px; height: 36px; border: 4px solid var(--primary-light); border-top-color: var(--primary); border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 8px; }
@keyframes spin { to { transform: rotate(360deg); } }

/* 弹窗样式 */
.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.4); display: flex; align-items: center; justify-content: center; z-index: 999; }
.modal-content { background: #fff; border-radius: 12px; padding: 24px; width: 360px; max-height: 90vh; overflow-y: auto; }
.modal-content label { display: block; margin-bottom: 12px; font-size: 14px; }
.modal-content input,
.modal-content select { width: 100%; padding: 6px 8px; margin-top: 4px; border: 1px solid var(--border); border-radius: 6px; }
.modal-actions { margin-top: 16px; display: flex; justify-content: flex-end; gap: 8px; }

.filter-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.filter-bar label {
  font-size: 14px;
}
.filter-bar input {
  width: 120px;
  padding: 4px 6px;
  border: 1px solid var(--border);
  border-radius: 6px;
}
</style>
