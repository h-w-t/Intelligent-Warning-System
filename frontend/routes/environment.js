const express = require('express');
const router = express.Router();
const pool = require('../config/db');//已在app.js中注册

router.get('/', async (req, res) => {
  console.log('收到请求，months =', req.query.months);
  const months = parseInt(req.query.months) || 36;

  // 白名单校验
  const allowed = [3, 6, 12, 24, 36];
  if (!allowed.includes(months)) {
    return res.status(400).json({ error: 'Invalid months parameter' });
  }

  const suffix = `${months}_month_avg`;

  const sql = `
  SELECT
    CONCAT(diag_year,'-',LPAD(diag_month,2,'0')) AS measure_period,
    aqi_${suffix}   AS aqi,
    pm2_5_${suffix} AS pm25,
    pm10_${suffix}  AS pm10,
    o3_${suffix}    AS o3,
    co_${suffix}    AS co,
    no2_${suffix}   AS no2,
    so2_${suffix}   AS so2
  FROM environmental_data
  ORDER BY diag_year ASC, diag_month ASC
`;

  try {
    const [rows] = await pool.query(sql);
    res.json(rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Database query failed' });
  }
});

module.exports = router;