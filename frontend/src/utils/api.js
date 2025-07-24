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
      const errorData = await response.json().catch(() => ({ message: response.statusText }));
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

// 封装获取病例数据的 API
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
    if (key !== 'page' && key !== 'limit' && params[key] !== '' && params[key] !== null && params[key] !== undefined) {
      queryParams.append(key, params[key]);
    }
  }
  const url = `http://localhost:3000/api/cases${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  return request(url);
}


// 封装删除病例数据的 API
export async function deleteCaseById(caseId) {
  const url = `http://localhost:3000/api/cases/${caseId}`;
  return request(url, { method: 'DELETE' });
}

// 封装获取风险预测数据的 API
export async function fetchForecastByIds(ids) {
  const url = `http://localhost:3000/api/forecast?ids=${ids}`;
  return request(url);
}
