require('dotenv').config();
const express = require('express');
const router  = express.Router();
const { OpenAI } = require('openai');

const openai = new OpenAI({
  apiKey: process.env.DASHSCOPE_API_KEY,
  baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1'
});

/* POST /api/risk-predict
   body: { age, gender, smoking_status, diagnosis, origin_province }
*/
router.post('/', async (req, res) => {
  try {
    const { age, gender, smoking_status, diagnosis, origin_province } = req.body;

    const prompt = `
你是一名肺癌专科医生，请根据以下信息给出 **5 年发病风险（0-100 的整数）**，并给出 **30 字以内的中文原因**。
患者信息：
年龄=${age} 岁；性别=${gender}；吸烟=${smoking_status}；癌症类型=${diagnosis}；省份=${origin_province}

按 JSON 返回：
{"risk": <整数>, "reason": "<30 字中文>"}
`;

    const completion = await openai.chat.completions.create({
      model: 'qwen-plus',
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 150,
      temperature: 0.2
    });

    let content = completion.choices[0].message.content.trim();
    content = content.replace(/```json|```/g, '').trim();
    const result = JSON.parse(content);

    res.json(result);   // { risk: 73, reason: "长期重度吸烟伴鳞癌病史" }
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: '预测服务异常' });
  }
});

module.exports = router;