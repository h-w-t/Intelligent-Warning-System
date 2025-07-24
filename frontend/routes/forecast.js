// routes/forecast.js
const express = require('express');
const router = express.Router();
const pool = require('../config/db');
const axios = require('axios');

router.get('/', async (req, res) => {
  try {
    const ids = (req.query.ids || '').split(',').map(Number);
    if (!ids.length) return res.status(400).json({ error: '缺少 ids' });

    const [rows] = await pool.query(`
      SELECT sequence_number AS caseId, age, gender, smoking_status,
             lung_cancer_classification AS diagnosis, origin_province
      FROM lung_cancer_patients
      WHERE sequence_number IN (?)
    `, [ids]);

    const results = await Promise.all(
      rows.map(async (caseItem) => {
        const payload = {
          age: caseItem.age,
          gender: caseItem.gender,
          smoking_status: caseItem.smoking_status,
          diagnosis: caseItem.diagnosis,
          origin_province: caseItem.origin_province
        };
        const { data } = await axios.post('http://localhost:3000/api/riskPrediction', payload);
        return { caseId: caseItem.caseId, ...data };
      })
    );
    res.json(results);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: '批量预测失败' });
  }
});

module.exports = router;