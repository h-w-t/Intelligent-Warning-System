from flask import Flask, jsonify, request
from config.db import init_app
from flask_cors import CORS
from dotenv import load_dotenv
from routes.QA import qa_bp  # 确保导入正确的蓝图
from routes.cases import cases_bp
from routes.environment import environment_bp
from routes.riskPrediction import risk_bp
from routes.forecast import forecast_bp
import os

# 载入环境变量
load_dotenv()

# 初始化Flask应用
app = Flask(__name__)
init_app(app)  

# 配置CORS，允许前端跨域请求
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "http://localhost:8080"}})

# 注册蓝图
app.register_blueprint(environment_bp, url_prefix='/api/environment', strict_slashes=False)
app.register_blueprint(cases_bp, url_prefix='/api/cases', strict_slashes=False)
app.register_blueprint(qa_bp, url_prefix='/api/QA', strict_slashes=False)
# app.register_blueprint(risk_bp, url_prefix='/api/riskPrediction', strict_slashes=False)
# app.register_blueprint(forecast_bp, url_prefix='/api/forecast', strict_slashes=False)

# 处理 OPTIONS 请求，确保预检请求成功
@app.before_request
def handle_options_request():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        headers = response.headers
        headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
        headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        headers['Access-Control-Max-Age'] = '3600' # 缓存预检请求结果1小时
        return response

# 404页面
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Route not found'}), 404

# 全局错误处理
@app.errorhandler(Exception)
def handle_error(e):
    print('全局错误处理:', e)
    return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500

# 启动服务器
if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    app.run(debug=True, host='0.0.0.0', port=port)
