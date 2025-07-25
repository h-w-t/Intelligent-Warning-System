from flask import Flask, jsonify, request
from config.db import init_app
from flask_cors import CORS
from dotenv import load_dotenv
from routes.QA import qa_bp  # 确保导入正确的蓝图
from routes.cases import cases_bp
from routes.environment import environment_bp
# from routes.riskPrediction import risk_bp # 暂时注释掉未使用的蓝图
# from routes.forecast import forecast_bp # 暂时注释掉未使用的蓝图
import os

# 载入环境变量，用于配置数据库连接等
load_dotenv()

# 初始化Flask应用实例
app = Flask(__name__)
# 初始化数据库连接池并绑定到Flask应用
init_app(app)  

# 配置CORS，允许来自 http://localhost:8080 的前端跨域请求
# 允许所有 /api/* 路径的请求
CORS(app, resources={r"/api/*": {"origins": "http://localhost:8080"}})

# 注册API蓝图
# 注册环境相关路由
app.register_blueprint(environment_bp, url_prefix='/api/environment', strict_slashes=False)
# 注册病例相关路由
app.register_blueprint(cases_bp, url_prefix='/api/cases', strict_slashes=False)
# 注册QA相关路由
app.register_blueprint(qa_bp, url_prefix='/api/QA', strict_slashes=False)
# app.register_blueprint(risk_bp, url_prefix='/api/riskPrediction', strict_slashes=False) # 暂时注释掉未使用的蓝图
# app.register_blueprint(forecast_bp, url_prefix='/api/forecast', strict_slashes=False) # 暂时注释掉未使用的蓝图

# 处理OPTIONS请求，用于CORS预检
# 在处理任何请求之前，先检查是否为OPTIONS请求
@app.before_request
def handle_options_request():
    """处理OPTIONS请求，确保CORS预检成功"""
    if request.method == 'OPTIONS':
        # 创建一个默认的OPTIONS响应
        response = app.make_default_options_response()
        headers = response.headers
        # 设置允许的源、方法和头部信息
        headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
        headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        # 设置预检请求的缓存时间（秒），例如1小时
        headers['Access-Control-Max-Age'] = '3600' 
        return response

# 定义404错误处理器
@app.errorhandler(404)
def not_found(e):
    """处理404 Not Found错误，返回JSON格式的错误信息"""
    return jsonify({'error': 'Route not found'}), 404

# 定义全局异常处理器
@app.errorhandler(Exception)
def handle_error(e):
    """处理所有未捕获的异常，返回通用的服务器内部错误信息"""
    print('全局错误处理:', e) # 在服务器控制台打印详细错误信息
    return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500

# 启动服务器的入口点
if __name__ == '__main__':
    # 从环境变量获取端口号，默认为3000
    port = int(os.getenv('PORT', 3000))
    # 运行Flask开发服务器
    # debug=True 启用调试模式，host='0.0.0.0' 使服务器可从网络访问
    app.run(debug=True, host='0.0.0.0', port=port)
