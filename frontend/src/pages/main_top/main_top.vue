<template>
  <div class="dashboard-container">
    <!-- 侧边栏 -->
    <div class="sidebar">
      <div class="logo">
        <h1>健康数据平台</h1>
      </div>
      
      <router-link 
        class="menu-item nav-link" 
        :to="{ name: 'main_top' }" 
        active-class="active"
        exact
      >
        <div class="menu-icon">📊</div>
        <div class="menu-text">数据概览</div>
      </router-link>
      
      <router-link 
        class="menu-item nav-link" 
        :to="{ name: 'history' }" 
        active-class="active"
      >
        <div class="menu-icon">🔍</div>
        <div class="menu-text">历史记录</div>
      </router-link>
      
      <router-link 
        class="menu-item nav-link" 
        :to="{ name: 'FAQ' }" 
        active-class="active"
      >
        <div class="menu-icon">❓</div>
        <div class="menu-text">常见问题</div>
      </router-link>
      
      <router-link 
        class="menu-item nav-link" 
        :to="{ name: 'profile_update' }" 
        active-class="active"
      >
        <div class="menu-icon">📈</div>
        <div class="menu-text">新增数据</div>
      </router-link>


      <router-link 
        class="menu-item nav-link" 
        :to="{ name: 'Datahub' }" 
        active-class="active"
      >
        <div class="menu-icon">🖥️</div>
        <div class="menu-text">数据中台</div>
      </router-link>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <div class="content-header">
        <h2>健康数据与分析中心</h2>
        <div class="date-display">{{ currentDate }}</div>
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
      
      <div class="chart-hint" v-if="showDataZoomHint">
        <div class="hint-content">
          <span class="hint-icon">🔍</span>
          <p>您可在此区域左右拖动，查看不同时间段的数据</p>
        </div>
      </div>
      
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
          <div v-else-if="airQualityData.dates.length > 0" ref="airQualityChart" class="chart"></div>
          <div v-else class="no-data-hint">
            <p>📊 没有可用的空气质量数据</p>
            <p>请选择不同的时间范围或添加更多数据</p>
          </div>
        </div>
        
        <!-- 肺癌病例分类分布 -->
        <div class="disease-rate-chart">
  <h3>肺癌病例分类分布</h3>
  <div v-show="diseaseRateLoading" class="loading-indicator">
    <div class="spinner"></div>
    <p>加载肺癌数据...</p>
  </div>
  <div v-show="!diseaseRateLoading" class="chart-legend-separate">
    <div class="legend-left">
      <div class="legend-scroll-container">
        <div v-for="(name, index) in diseaseRateData.names" :key="index" class="legend-item" @click="toggleData(index)">
          <div class="legend-color" :style="{ backgroundColor: getColorByIndex(index) }"></div>
          <span>{{ name }}</span>
        </div>
      </div>
    </div>
    <div ref="diseaseRateChart" class="chart-right"></div>
  </div>
</div>
      </div>
      
      <div class="data-summary">
        <div class="summary-card">
          <div class="summary-header">
            <div class="summary-icon" style="background-color: rgba(84, 112, 198, 0.2);">
              🌬️
            </div>
            <h4>空气质量概览</h4>
          </div>
          <div class="summary-body">
            <div v-if="latestAirData">
              <p>最近月份: {{ latestAirData.month }}</p>
              <p>AQI指数: <span :class="getAqiClass(latestAirData.aqi)">{{ (latestAirData.aqi ?? 0).toFixed(2) }}</span></p>
              <p>PM2.5: {{ latestAirData.pm25 }} μg/m³</p>
              <p>PM10: {{ latestAirData.pm10 }} μg/m³</p>
            </div>
            <div v-else>
              <p>无可用数据</p>
            </div>
          </div>
        </div>
        
        <div class="summary-card">
          <div class="summary-header">
            <div class="summary-icon" style="background-color: rgba(238, 102, 102, 0.2);">
              🩺
            </div>
            <h4>肺癌统计</h4>
          </div>
          <div class="summary-body" v-if="lungCancerStats">
            <p>病例总数: {{ lungCancerStats.total_cases }}</p>
            <p>诊断年份: {{ lungCancerStats.diagnosis_year_range }}</p>
            <p>男性病例: {{ lungCancerStats.male_percentage }}%</p>
            <p>平均年龄: {{ lungCancerStats.avg_age }}岁</p>
          </div>
          <div v-else>
            <p>加载统计数据中...</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  data() {
    return {
      currentDate: '',
      airQualityChart: null,
      diseaseRateChart: null,
      selectedTimeRange: '3_month',
      loading: false,
      diseaseRateLoading: false,
      error: null,
      pollutionTypes: [
        { value: 'aqi', label: 'AQI', color: '#5470c6', visible: true },
        { value: 'pm25', label: 'PM2.5', color: '#91cc75', visible: true },
        { value: 'pm10', label: 'PM10', color: '#fac858', visible: true },
        { value: 'o3', label: 'O₃', color: '#ee6666', visible: true },
        { value: 'co', label: 'CO', color: '#73c0de', visible: false },
        { value: 'no2', label: 'NO₂', color: '#3ba272', visible: false },
        { value: 'so2', label: 'SO₂', color: '#fc8452', visible: false }
      ],
      selectedPollutionTypes: ['aqi', 'pm25', 'pm10', 'o3'],
      airQualityData: {
        dates: [],
        aqi: [],
        pm25: [],
        pm10: [],
        o3: [],
        co: [],
        no2: [],
        so2: []
      },
      latestAirData: null,
      diseaseRateData: {
        names: [],
        values: []
      },
      lungCancerStats: null,
      showDataZoomHint: false,
      intervalMonths: {
        '3_month': 3,
        '6_month': 6,
        '12_month': 12,
        '24_month': 24,
        '36_month': 36
      },
      selectedDataIndex: null // 用于存储当前选中数据的索引
    };
  },
  watch: {
    selectedPollutionTypes() {
      this.initAirQualityChart();
    }
  },
  created() {
    this.setCurrentDate();
    setInterval(this.setCurrentDate, 60000);
  },
  mounted() {
    this.fetchAirPollutionData();
    this.fetchLungCancerData();
    window.addEventListener('resize', this.resizeCharts);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.resizeCharts);
    if (this.airQualityChart) {
      this.airQualityChart.dispose();
    }
    if (this.diseaseRateChart) {
      this.diseaseRateChart.dispose();
    }
  },
  methods: {
////////////////////////////////////////////////////////////////////此处应有个人风险预测模块
    async fetchRiskPrediction({ age, gender, smoker, province, division }) {
  try {
    const res = await fetch('http://localhost:3000/api/risk/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ age, gender, smoker, province, division })
    });
    const data = await res.json();
    
    return data;
  } catch (error) {
    console.error('预测失败:', error);
    return null;
  }
},
async predictRisk() {
  const result = await this.fetchRiskPrediction({
    age: 65,
    gender: '男',
    smoker: true,
    province: '江苏',
    division: '浦东新区'
  });
  alert(`预测风险：${result?.risk || '未知'}`);
},
///////////////////////此处应有大气污染物预测模块
async fetchPollutionForecast({ daysAhead = 7, location = 'shanghai' } = {}) {
  try {
    const res = await fetch('http://localhost:3000/api/pollution-forecast/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ daysAhead, location })
    });
    const data = await res.json();
    return data;
  } catch (error) {
    console.error('污染物预测失败:', error);
    return null;
  }
},



    async fetchAirPollutionData() {
      this.loading = true;
      this.error = null;

      try {
        const months = this.intervalMonths[this.selectedTimeRange];
        const response = await fetch(`http://localhost:3000/api/environment?months=${months}`);

        if (!response.ok) {
          const errorData = await response.text();
          throw new Error(`API错误: ${response.status} - ${errorData}`);
        }

        const responseData = await response.json();

        if (!responseData || responseData.length === 0) {
          this.airQualityData = {
            dates: [],
            aqi: [],
            pm25: [],
            pm10: [],
            o3: [],
            co: [],
            no2: [],
            so2: []
          };
          this.latestAirData = null;
        } else {
          const sorted = responseData.sort((a, b) => a.measure_period.localeCompare(b.measure_period));

          this.airQualityData = {
            dates: sorted.map(item => item.measure_period),
            aqi: sorted.map(item => item.aqi),
            pm25: sorted.map(item => item.pm25),
            pm10: sorted.map(item => item.pm10),
            o3: sorted.map(item => item.o3),
            co: sorted.map(item => item.co),
            no2: sorted.map(item => item.no2),
            so2: sorted.map(item => item.so2)
          };

          if (this.airQualityData.dates.length > 0) {
            const lastIndex = this.airQualityData.dates.length - 1;
            this.latestAirData = {
              month: this.airQualityData.dates[lastIndex],
              aqi: this.airQualityData.aqi[lastIndex],
              pm25: this.airQualityData.pm25[lastIndex],
              pm10: this.airQualityData.pm10[lastIndex],
              o3: this.airQualityData.o3[lastIndex]
            };
          }
        }
        this.$nextTick(() => {
        this.initAirQualityChart();
        });
      } catch (error) {
        console.error('获取环境数据失败:', error);
        this.error = error.message || '获取环境数据失败';
      } finally {
        this.loading = false;
      }
    },
    
    async fetchLungCancerData() {
      this.diseaseRateLoading = true;
      
      try {
        const [rateResponse, statsResponse] = await Promise.all([
          fetch('http://localhost:3000/api/cases/lung-cancer-types'),
          fetch('http://localhost:3000/api/cases/stats')
        ]);
        
        if (!rateResponse.ok || !statsResponse.ok) {
          throw new Error('获取肺癌数据失败');
        }
        
        const rateData = await rateResponse.json();
        const statsData = await statsResponse.json();
        
        this.diseaseRateData = {
          names: rateData.map(item => item.cancer_type),
          values: rateData.map(item => item.percentage)
        };
        
        this.lungCancerStats = statsData;
        
        this.$nextTick(() => {
  this.initDiseaseRateChart();
});
      } catch (error) {
        console.error('获取肺癌数据失败:', error);
      } finally {
        this.diseaseRateLoading = false;
      }
    },
    
    setCurrentDate() {
      const now = new Date();
      this.currentDate = `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    },
    
    initAirQualityChart() {
      if (!this.$refs.airQualityChart || this.airQualityData.dates.length === 0) return;
      
      if (this.airQualityChart) {
        this.airQualityChart.dispose();
      }
      
      this.airQualityChart = echarts.init(this.$refs.airQualityChart);
      
      const visibleSeries = [];
      const total = this.airQualityData.dates.length;
      const defaultShow = 10;
      const startPercent = total > defaultShow ? 100 - (defaultShow / total * 100) : 0;
      
      const pollutionConfig = {
        aqi: { name: 'AQI', color: '#5470c6' },
        pm25: { name: 'PM2.5', color: '#91cc75' },
        pm10: { name: 'PM10', color: '#fac858' },
        o3: { name: 'O₃', color: '#ee6666' },
        co: { name: 'CO', color: '#73c0de' },
        no2: { name: 'NO₂', color: '#3ba272' },
        so2: { name: 'SO₂', color: '#fc8452' }
      };
      
      this.selectedPollutionTypes.forEach(type => {
        const config = pollutionConfig[type];
        if (config) {
          visibleSeries.push({
            name: config.name,
            type: 'line',
            data: this.airQualityData[type],
            smooth: true,
            lineStyle: {
              width: 3,
              color: config.color
            },
            symbol: 'circle',
            symbolSize: 6,
            itemStyle: {
              color: config.color
            }
          });
        }
      });
      
      const option = {
        title: {
          text: '空气质量历史数据',
          subtext: `${this.intervalMonths[this.selectedTimeRange]}个月平均数据`,
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          formatter: function (params) {
            let result = `<div style="margin-bottom:5px;font-weight:bold">${params[0].name}</div>`;
            params.forEach(item => {
              result += `<div style="display:flex;align-items:center;margin-bottom:3px;">
                          <div style="width:10px;height:10px;background-color:${item.color};margin-right:5px;border-radius:50%;"></div>
                          <div>${item.seriesName}: ${item.value}</div>
                        </div>`;
            });
            return result;
          }
        },
        legend: {
          data: visibleSeries.map(s => s.name),
          bottom: 10,
          itemHeight: 12,
          itemWidth: 12
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: this.airQualityData.dates,
          axisLabel: {
            interval: 0,
            rotate: this.airQualityData.dates.length > 6 ? 45 : 0
          }
        },
        yAxis: {
          type: 'value',
          name: '污染物浓度',
          axisLabel: {
            formatter: '{value}'
          }
        },
        dataZoom: [{
          type: 'slider',
          show: true,
          start: startPercent,
          end: 100,
          bottom: 25
        }, {
          type: 'inside',
          start: startPercent,
          end: 100
        }],
        series: visibleSeries
      };
      
      this.airQualityChart.setOption(option);
      
      setTimeout(() => {
        this.showDataZoomHint = false;
      }, 5000);
    },
    
    initDiseaseRateChart() {
      if (!this.$refs.diseaseRateChart || this.diseaseRateData.names.length === 0) return;

      if (this.diseaseRateChart) {
        this.diseaseRateChart.dispose();
      }
      this.diseaseRateChart = echarts.init(this.$refs.diseaseRateChart);

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: function (params) {
            return `${params.name}: ${params.value} (${(params.percent ?? 0).toFixed(2)}%)`;

          }
        },
        series: [
          {
            name: '肺癌类型',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['50%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 0,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '14',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: this.diseaseRateData.names.map((name, index) => ({
              value: this.diseaseRateData.values[index],
              name: name,
              itemStyle: {
                color: new echarts.graphic.RadialGradient(0.5, 0.5, 0.7, [
                  { offset: 0, color: this.getColorByIndex(index) },
                  { offset: 1, color: this.getLighterColor(this.getColorByIndex(index)) }
                ])
              }
            }))
          }
        ]
      };

      this.diseaseRateChart.setOption(option);
    },

    getColorByIndex(index) {
      const colors = [
        '#5470c6', '#91cc75', '#fac858', '#ee6666', 
        '#73c0de', '#3ba272', '#fc8452', '#9a60b4'
      ];
      return colors[index % colors.length];
    },

    getLighterColor(color) {
      return echarts.color.modifyHSL(color, null, null, 0.5);
    },

    resizeCharts() {
      if (this.airQualityChart) this.airQualityChart.resize();
      if (this.diseaseRateChart) this.diseaseRateChart.resize();
    },

    getAqiClass(aqiValue) {
      if (aqiValue <= 50) return 'aqi-good';
      if (aqiValue <= 100) return 'aqi-moderate';
      if (aqiValue <= 150) return 'aqi-unhealthy-sensitive';
      if (aqiValue <= 200) return 'aqi-unhealthy';
      if (aqiValue <= 300) return 'aqi-very-unhealthy';
      return 'aqi-hazardous';
    },

    toggleData(index) {
      const option = this.diseaseRateChart.getOption();
      const data = option.series[0].data;

      // 重置所有数据的 selected 状态
      data.forEach(item => {
        item.selected = false;
      });

      // 设置当前点击数据的 selected 状态
      data[index].selected = true;

      // 更新图表
      this.diseaseRateChart.setOption({
        series: [{
          data: data
        }]
      });
    }
  }
};
</script>

<style scoped>
.dashboard-container {
  display: flex;
  height: 100vh;
  background-color: #f5f7fa;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.sidebar {
  width: 220px;
  background-color: #ffffff;
  border-right: 1px solid #e8e8e8;
  padding: 24px 0;
  height: 100vh;
  position: fixed;
  overflow-y: auto;
  z-index: 10;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.03);
}

.logo {
  padding: 0 24px 24px;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 24px;
}

.logo h1 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.menu-item {
  padding: 12px 24px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-bottom: 6px;
  text-decoration: none;
}

.menu-item:hover {
  background-color: #f5f7fa;
}

.menu-item.active {
  background-color: #e6f7ff;
  border-left: 3px solid #1890ff;
}

.menu-icon {
  margin-right: 12px;
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.menu-text {
  font-size: 15px;
  color: #666;
}

.menu-item.active .menu-text {
  color: #1890ff;
}

.main-content {
  flex: 1;
  margin-left: 220px;
  padding: 24px;
  overflow-y: auto;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e8e8e8;
}

.content-header h2 {
  font-size: 22px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
}

.date-display {
  font-size: 14px;
  color: #7f8c8d;
  background: #ecf0f1;
  padding: 5px 10px;
  border-radius: 4px;
}

.filter-container {
  background-color: #ffffff;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.time-range-selector {
  flex: 1;
  min-width: 200px;
}

.time-range-selector label,
.pollution-type-selector label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #2c3e50;
}

.time-range-selector select {
  width: 100%;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  background-color: #f8f9fa;
  cursor: pointer;
  transition: border-color 0.3s;
}

.time-range-selector select:focus {
  border-color: #5470c6;
  outline: none;
  box-shadow: 0 0 0 3px rgba(84, 112, 198, 0.2);
}

.pollution-type-selector {
  flex: 2;
  min-width: 300px;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 8px;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  background-color: #f0f2f5;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  margin-right: 8px;
  margin-bottom: 8px;
  font-size: 14px;
  border: 1px solid #e0e0e0;
}

.checkbox-group label:hover {
  background-color: #e4e6eb;
}

.checkbox-group input {
  display: none;
}

.custom-checkbox {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 3px;
  margin-right: 8px;
  position: relative;
}

.checkbox-group input:checked + .custom-checkbox::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 10px;
  height: 10px;
  background-color: white;
  border-radius: 2px;
}

.chart-hint {
  position: fixed;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(84, 112, 198, 0.9);
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
  animation: fadeIn 0.5s, fadeOut 0.5s 4.5s;
}

.hint-content {
  display: flex;
  align-items: center;
}

.hint-icon {
  font-size: 18px;
  margin-right: 10px;
}

.chart-hint p {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
}

.data-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.data-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  min-height: 380px;
}

.data-card h3 {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 16px;
  color: #2c3e50;
  padding-bottom: 12px;
  border-bottom: 1px solid #edf2f7;
}

.chart-actions {
  position: absolute;
  top: 15px;
  right: 20px;
  z-index: 10;
  display: flex;
  gap: 10px;
}

.chart-hint-btn {
  background: rgba(84, 112, 198, 0.1);
  border: 1px solid rgba(84, 112, 198, 0.3);
  color: #5470c6;
  border-radius: 5px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.2s;
}

.refresh-btn {
  background: rgba(91, 204, 145, 0.1);
  border: 1px solid rgba(91, 204, 145, 0.3);
  color: #3ba272;
  border-radius: 5px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.2s;
}

.chart-hint-btn:hover, .refresh-btn:hover {
  opacity: 0.8;
}

.chart {
  width: 100%;
  height: 300px;
}

.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(84, 112, 198, 0.2);
  border-radius: 50%;
  border-top-color: #5470c6;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  text-align: center;
  color: #e74c3c;
}

.error-message button {
  margin-top: 15px;
  padding: 10px 20px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s;
  font-size: 14px;
  font-weight: 500;
}

.error-message button:hover {
  background-color: #c0392b;
}

.data-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-top: 24px;
}

.summary-card {
  background-color: #ffffff;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.summary-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.summary-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 18px;
}

.summary-card h4 {
  margin: 0;
  font-size: 16px;
  color: #2c3e50;
}

.summary-body {
  font-size: 14px;
  color: #555;
}

.summary-body p {
  margin: 8px 0;
}

/* AQI级别颜色指示 */
.aqi-good {
  color: #009966;
  font-weight: bold;
}

.aqi-moderate {
  color: #ffde33;
  font-weight: bold;
}

.aqi-unhealthy-sensitive {
  color: #ff9933;
  font-weight: bold;
}

.aqi-unhealthy {
  color: #cc0033;
  font-weight: bold;
}

.aqi-very-unhealthy {
  color: #660099;
  font-weight: bold;
}

.aqi-hazardous {
  color: #7e0023;
  font-weight: bold;
}

/* 肺癌病例分类分布 */
.disease-rate-chart {
  display: flex;
  flex-direction: column;
}

.chart-legend-separate {
  display: flex;
  height: 300px;
}

.legend-left {
  width: 150px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.legend-scroll-container {
  overflow-y: auto;
  height: 100%;
  padding: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  cursor: pointer;
}

.legend-color {
  width: 15px;
  height: 15px;
  margin-right: 8px;
  border-radius: 2px;
}

.chart-right {
  flex: 1;
  padding: 10px;
  box-sizing: border-box;
}

@media (max-width: 1024px) {
  .data-container {
    grid-template-columns: 1fr;
  }
  
  .sidebar {
    width: 200px;
  }
  
  .main-content {
    margin-left: 200px;
  }
  
  .filter-container {
    flex-direction: column;
    gap: 15px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 0;
    padding: 0;
    overflow: hidden;
    transition: width 0.3s;
  }
  
  .sidebar.open {
    width: 200px;
    padding: 24px 0;
  }
  
  .main-content {
    margin-left: 0;
    padding: 15px;
  }
  
  .filter-container {
    padding: 15px;
  }
  
  .content-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .date-display {
    margin-top: 10px;
  }
  
  .data-card {
    min-height: 320px;
  }
  
  .chart {
    height: 250px;
  }
}

@keyframes fadeIn {
  from { opacity: 0; bottom: 60px; }
  to { opacity: 1; bottom: 80px; }
}

@keyframes fadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}
</style>