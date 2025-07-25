/**
 * 发起一个带有默认JSON头的异步API请求
 * @param {string} url - 请求的目标URL地址
 * @param {Object} [options={}] - 请求配置选项
 * @param {Object} [options.headers] - 自定义请求头对象
 * @param {string} [options.method='GET'] - 请求方法（GET/POST等）
 * @param {any} [options.body] - 请求体数据（POST请求时需要）
 * @returns {Promise<any>} 返回解析后的JSON响应数据
 * @throws {Error} 当HTTP响应状态码非2xx或网络异常时抛出错误
 */
export async function request(url, options = {}) {
  try {
    /**
     * 创建带有默认JSON头的fetch请求
     * 合并用户提供的headers和基础headers
     * 保留用户自定义的其他选项（如method、body等）
     */
    const response = await fetch(url, {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    /**
     * 处理非2xx状态码的响应
     * 尝试解析错误响应体中的JSON数据
     * 解析失败时使用状态文本作为错误信息
     */
    if (!response.ok) {
      // 尝试解析JSON错误信息，如果失败则使用状态文本
      const errorData = await response.json().catch(() => ({ message: response.statusText }));
      // 抛出带有详细信息的错误
      throw new Error(`API 请求失败: ${response.status} - ${errorData.message || '未知错误'}`);
    }

    // 返回解析后的JSON响应数据
    return await response.json();
  } catch (error) {
    /**
     * 捕获并记录网络错误或未处理的异常
     * 重新抛出错误以便调用方处理
     */
    console.error('API 请求错误:', error);
    throw error;
  }
}

/**
 * 获取病例数据列表
 * @param {Object} [params={}] - 查询参数对象
 * @param {number} [params.page=1] - 页码
 * @param {number} [params.limit=10] - 每页数量
 * @param {string} [params.search] - 搜索关键词
 * @param {string} [params.patient] - 患者序列号过滤
 * @param {number} [params.year] - 诊断年份过滤
 * @param {number} [params.month] - 诊断月份过滤
 * @param {number} [params.age] - 年龄过滤
 * @param {string} [params.gender] - 性别过滤
/**
 * 获取病例数据列表
 * @param {Object} [params={}] - 查询参数对象
 * @param {number} [params.page=1] - 页码
 * @param {number} [params.limit=10] - 每页数量
 * @param {string} [params.search] - 搜索关键词
 * @param {string} [params.patient] - 患者序列号过滤
 * @param {number} [params.year] - 诊断年份过滤
 * @param {number} [params.month] - 诊断月份过滤
 * @param {number} [params.age] - 年龄过滤
 * @param {string} [params.gender] - 性别过滤
 * @param {string} [params.cancerType] - 癌症类型过滤
 * @param {string} [params.isSmoker] - 吸烟状态过滤 ('true'/'false')
 * @returns {Promise<Object>} 返回包含病例列表和分页信息的对象
 */
export async function fetchCases(params = {}) {
  const queryParams = new URLSearchParams();
  // 添加分页参数
  if (params.page) {
    queryParams.append('page', params.page);
  }
  if (params.limit) {
    queryParams.append('limit', params.limit);
  }

  // 添加其他过滤参数
  for (const key in params) {
    // 排除 page 和 limit，并确保值不为空
    if (key !== 'page' && key !== 'limit' && params[key] !== '' && params[key] !== null && params[key] !== undefined) {
      queryParams.append(key, params[key]);
    }
  }
  // 构建完整的API URL
  const url = `http://localhost:3000/api/cases${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  // 发起API请求
  return request(url);
}


/**
 * 根据病例ID删除病例数据
 * @param {string} caseId - 要删除的病例ID (sequence_number)
 * @returns {Promise<Object>} 返回操作结果
 */
export async function deleteCaseById(caseId) {
  const url = `http://localhost:3000/api/cases/${caseId}`;
  // 发起DELETE请求
  return request(url, { method: 'DELETE' });
}

/**
 * 获取风险预测数据
 * @param {string} ids - 患者序列号字符串，用逗号分隔
 * @returns {Promise<Object>} 返回风险预测数据
 */
export async function fetchForecastByIds(ids) {
  const url = `http://localhost:3000/api/forecast?ids=${ids}`;
  return request(url);
}

/**
 * 获取患者风险评级
 * @param {string} patient_sn - 患者序列号
 * @returns {Promise<Object>} 返回包含风险评分和评级的对象
 */
export async function getPatientRiskRating(patient_sn) {
  const url = `http://localhost:3000/api/cases/${patient_sn}/risk_rating`;
  return request(url);
}

/**
 * 更新患者风险评分
 * @param {string} caseId - 病例ID (sequence_number)
 * @returns {Promise<Object>} 返回操作结果
 */
export async function updatePatientRiskScore(caseId) {
  // 后端在获取病例详情时会自动更新风险评分，所以这里调用获取病例详情接口即可
  const url = `http://localhost:3000/api/cases/${caseId}`;
  return request(url);
}
