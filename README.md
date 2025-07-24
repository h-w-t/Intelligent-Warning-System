# 智能预警系统使用文档

## 项目简介
本项目是一个智能预警系统，采用前后端分离架构，后端使用 Python Flask 提供 API 接口，前端使用 Vue3 进行数据展示和交互。系统旨在实现对数据的批量访问、历史记录管理、风险预测等功能。

## 技术栈

### 后端
- **语言**: Python
- **框架**: Flask
- **数据库**: MySQL (关系型数据库), Neo4j (图数据库，如果使用)

### 前端
- **语言**: JavaScript
- **框架**: Vue3
- **包管理工具**: npm

## 环境配置与运行

### 1. Python 后端环境配置

1.  **Python 版本**: 3.12.6
2.  **虚拟环境管理**: 本项目使用 `uv` 进行 Python 虚拟环境搭建。如果您尚未安装 `uv`，请在系统 Python 环境下执行以下命令安装：
    ```bash
    pip install uv
    ```
3.  **创建并激活虚拟环境**:
    *   进入 `backend` 目录：
        ```bash
        cd ./backend
        ```
    *   在 `backend` 目录下执行 `uv venv` 创建虚拟环境：
        ```bash
        uv venv
        ```
    *   激活虚拟环境：
        ```bash
        .\.venv\Scripts\activate
        ```
        (在 Linux/macOS 上可能是 `source ./.venv/bin/activate`)
    *   **注意**：如果您使用 Conda，并且遇到环境冲突，可以使用 `conda deactivate` 关闭 Conda 的 `base` 环境。建议配置 Conda 禁止自动激活 `base` 环境：
        ```bash
        conda config --set auto_activate_base false
        ```
4.  **安装后端依赖**: 成功激活虚拟环境后，使用 `uv sync --dev` 同步项目依赖包：
    ```bash
    uv pip install -r requirements.txt
    ```
    **开发过程中请使用 `uv pip install <package_name>` 下载新的项目依赖包！**

### 2. 数据库配置

1.  **MySQL 数据库**: 确保您的系统已安装并运行 MySQL 数据库服务。
2.  **数据库连接**: 数据库连接信息在 `backend/config/db.py` 中配置。请根据您的实际数据库信息修改该文件。**数据库名称以及密码在后端`.env`文件中进行修改。**
3.  **构建数据库**:
    *   核对 `backend/database/environmentalsql.py` 中的数据库配置，确保与本地数据库配置正确。
    *   在 `backend` 目录下运行以下命令构建大气污染数据库和病例数据库（请确保虚拟环境已激活）：
        ```bash
        python ./database/environmentalsql.py
        python ./database/patientsql.py
        ```
        **注意**：请勿重复运行这两个文件，否则可能会导致数据库中的数据丢失。

### 3. Node.js 前端环境配置

1.  **Node.js 版本**: 建议使用 `nvm` 管理 Node.js 版本，并确保使用 Node.js 16.14.2。
    -   一定要先安装 `nvm`才能正确使用nvm进行环境管理
    -   安装nvm：
        ```bash
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
        ```
        **注意**：nvm安装成功后，请重启终端。
    -  安装Node.js：
        ```bash
        nvm install 16.14.2
        ```
    -   验证Node.js版本：
        ```bash
        node -v
        ```
        输出结果为16.14.2，则说明安装成功。

2.  **安装前端依赖**:
    *   进入 `frontend` 目录：
        ```bash
        cd ./frontend
        ```
    *   安装前端依赖包：
        ```bash
        npm install
        ```
        或
        ```bash
        yarn install
        ```

### 4. 运行项目

1.  **启动后端服务**:
    *   确保您已激活 Python 虚拟环境（参考 **1. Python 后端环境配置**）。
    *   在项目根目录（`Intelligent-Warning-System`）下执行：
    *   进入 `backend` 目录
        ```bash
        cd backend
        ```
    *   启动后端服务：
        ```bash
        uv run app.py
        ```
        后端服务将运行在 `http://localhost:3000`。
2.  **启动前端服务**:
    *   进入 `frontend` 目录：
        ```bash
        cd frontend
        ```
    *   启动前端开发服务器：
        ```bash
        npm run serve
        ```
        前端应用通常会在 `http://localhost:8080` 运行。

## API 接口概述
后端 API 接口定义在 `backend/routes/` 目录下。主要包括：
- `/api/cases`: 病例数据相关的 CRUD 操作及查询。
- `/api/environment`: 环境数据相关接口。
- `/api/QA`: 问答系统相关接口。
- `/api/riskPrediction`: 风险预测相关接口。（已注释）
- `/api/forecast`: 预测数据相关接口。（已注释）

前端通过这些 API 调用数据。
