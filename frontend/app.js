// app.js
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const app = express();
console.log('DASHSCOPE_API_KEY:', process.env.DASHSCOPE_API_KEY);

const environmentRouter = require('./routes/environment');
const casesRouter = require('./routes/cases');
const riskPredictionRoutes = require('./routes/riskPrediction');
const ForecastRoutes = require('./routes/forecast.js');

app.use(cors({ origin: 'http://localhost:8080', credentials: true }));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

/* ---- 路由 ---- */
app.use('/api/environment', environmentRouter);
app.use('/api/cases', casesRouter);
app.use('/api/riskPrediction', riskPredictionRoutes);
app.use('/api/forecast', ForecastRoutes);

/* ---- 404 & 全局错误 ---- */
app.use((req, res) => res.status(404).json({ error: 'Route not found' }));
app.use((err, req, res, next) => {
  console.error('全局错误处理:', err);
  res.status(err.statusCode || 500).json({ error: 'Internal Server Error', details: err.message });
});

/* ---- 启动 ---- */
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`✅ Backend ready → http://localhost:${PORT}`));