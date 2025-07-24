// routes/cases.js
const express = require('express');
const router = express.Router();
const pool = require('../config/db');

/* GET /api/cases?search=&patient=&year=&month=&age=&gender=&cancerType=&isSmoker= */
router.get('/', async (req, res) => {
  try {
    const {
      search, patient, year, month, age, gender,
      cancerType, isSmoker
    } = req.query;

    let sql = `
      SELECT
        patient_SN,
        sequence_number AS caseId,
        gender,
        age,
        smoking_status,
        lung_cancer_classification AS diagnosis,
        diagnosis_year,
        diagnosis_month
      FROM lung_cancer_patients
      WHERE 1=1
    `;
    const params = [];

    if (search) {
      sql += ` AND (patient_SN LIKE ? OR sequence_number LIKE ? OR lung_cancer_classification LIKE ?)`;
      const like = `%${search}%`;
      params.push(like, like, like);
    }
    if (patient) { sql += ' AND patient_SN = ?'; params.push(patient); }
    if (year) { sql += ' AND diagnosis_year = ?'; params.push(parseInt(year, 10)); }
    if (month) { sql += ' AND diagnosis_month = ?'; params.push(parseInt(month, 10)); }
    if (age) { sql += ' AND age = ?'; params.push(parseInt(age, 10)); }
    if (gender) { sql += ' AND gender = ?'; params.push(gender); }
    if (cancerType) { sql += ' AND lung_cancer_classification = ?'; params.push(cancerType); }
    if (isSmoker !== undefined) { sql += ' AND smoking_status = ?'; params.push(isSmoker === 'true' ? '是' : '否'); }

    sql += ' ORDER BY diagnosis_year DESC, diagnosis_month DESC';
    const [rows] = await pool.query(sql, params);

    const formatted = rows.map(r => ({
      ...r,
      diagnosis_month: r.diagnosis_month ? String(r.diagnosis_month).padStart(2, '0') : ''
    }));
    res.json(formatted);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/* POST /api/cases */
router.post('/', async (req, res) => {
  try {
    const {
      sequence_number, patient_SN, gender, age,
      origin_province, shanghai_administrative_division,
      diagnosis, smoking_status,
      diagnosis_year, diagnosis_month 
    } = req.body;

    const sql = `
      INSERT INTO lung_cancer_patients (
        sequence_number, patient_SN, gender, age,
        origin_province, shanghai_administrative_division,
        lung_cancer_classification, smoking_status,
        diagnosis_year, diagnosis_month
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;
    const values = [
      sequence_number, patient_SN, gender, parseInt(age, 10),
      origin_province || null, shanghai_administrative_division || null,
      diagnosis, smoking_status,
      parseInt(diagnosis_year, 10), parseInt(diagnosis_month, 10)
    ];

    await pool.query(sql, values);
    console.log('接收到的请求体:', req.body);
    res.status(201).json({ message: '病例已创建', caseId: sequence_number });
  } catch (err) {
    const code = err.code === 'ER_DUP_ENTRY' ? 409 : 500;
    res.status(code).json({ error: err.message });
  }
});
/* DELETE /api/cases/:id */
router.delete('/:id', async (req, res) => {
  try {
    let id = req.params.id;
    if (id.startsWith('#')) id = id.slice(1);

    const [result] = await pool.query(
      'DELETE FROM lung_cancer_patients WHERE sequence_number = ?', [id]
    );
    if (result.affectedRows === 0) return res.status(404).json({ error: '病例未找到' });
    res.json({ success: true, message: '已删除' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/* GET /api/cases/lung-cancer-types */
router.get('/lung-cancer-types', async (req, res) => {
  try {
    const [rows] = await pool.query(`
      SELECT lung_cancer_classification AS cancer_type, COUNT(*) AS total_cases
      FROM lung_cancer_patients
      GROUP BY lung_cancer_classification
    `);
    const total = rows.reduce((s, r) => s + r.total_cases, 0);
    res.json(rows.map(r => ({
      cancer_type: r.cancer_type,
      percentage: Math.round((r.total_cases / total) * 100)
    })));
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/* GET /api/cases/stats */
router.get('/stats', async (req, res) => {
  try {
    const [rows] = await pool.query(`
      SELECT
        COUNT(*) AS total_cases,
        GROUP_CONCAT(DISTINCT diagnosis_year ORDER BY diagnosis_year) AS years,
        ROUND(AVG(age), 1) AS avg_age,
        ROUND(SUM(gender = '男') * 100 / COUNT(*), 0) AS male_percentage
      FROM lung_cancer_patients
    `);
    const ys = rows[0].years ? rows[0].years.split(',') : [];
    const yearRange = ys.length ? `${ys[0]}-${ys[ys.length - 1]}` : '';
    res.json({
      total_cases: rows[0].total_cases,
      diagnosis_year_range: yearRange,
      avg_age: rows[0].avg_age,
      male_percentage: rows[0].male_percentage
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/* GET /api/cases/:id */
router.get('/:id', async (req, res) => {
  try {
    const id = req.params.id;
    console.log('🔍 实际执行的 id:', id); // 加这行
    const sql = `
      SELECT
        patient_SN,
        sequence_number AS caseId,
        gender,
        age,
        smoking_status,
        origin_province,
        shanghai_administrative_division,
        lung_cancer_classification AS diagnosis,
        diagnosis_year,
        diagnosis_month
      FROM lung_cancer_patients
      WHERE sequence_number = ?
    `;
    const [rows] = await pool.query(sql, [id]);
    console.log('🔍 查询结果:', rows[0]); // 加这行
    if (rows.length === 0) {
      return res.status(404).json({ error: '未找到该病例' });
    }

    const caseDetail = {
      ...rows[0],
      diagnosis_month: rows[0].diagnosis_month ? String(rows[0].diagnosis_month).padStart(2, '0') : ''
    };

    res.json(caseDetail);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

//////////////////////预留影像学数据接口
router.get('/:caseId', async (req, res) => {   
  try {
    const { caseId } = req.params;

    // 示例：从数据库拿数据
    const basic   = await db.collection('cases').findOne({ caseId });
    const imaging = await db.collection('imaging').findOne({ caseId });

    if (!basic) {
      return res.status(404).json({ message: '病例不存在' });
    }

    res.json({
      ...basic,
      imaging: imaging || null
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: '服务器错误' });
  }
});


module.exports = router;