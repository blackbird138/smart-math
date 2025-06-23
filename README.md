# Smart Math

Smart Math 是一个面向数学文档解析和问答的实验项目。项目通过 Mineru 服务解析 PDF 内容，使用 RAG（Retrieval Augmented Generation）方式将检索到的文档与 LLM 结合来生成答案。

## 项目结构
- `mineru_service/`：FastAPI 服务，提供 `/parse` 接口解析 PDF，通过 Dockerfile 构建镜像
- `src/`：数据清洗、文本切片和向量检索的核心代码
- `frontend/`：基于 Vue 3 + TypeScript 的前端项目
- `config/`：RAG 及模型依赖的 YAML 配置文件
- `tests/`：单元测试

## 环境准备
1. 安装 Python 3.11 以及依赖
   ```bash
   pip install -r requirements.txt
   ```
2. 可选安装用于清洗的附加包
   ```bash
   pip install unstructured==0.14.0 transformers
   ```
3. 启动 Mineru 服务
   ```bash
   docker compose up -d
   ```
4. 运行前端
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 快速使用
可以以 `test.py` 为例，向本地 Mineru 服务上传 PDF 并获取解析结果。`src/pipeline.py` 中的 `SmartMathPipeline` 执行数据加载、清洗和向量化流程。

## 运行测试
```bash
cd tests
PYTHONPATH=.. pytest
```

## 版权声明
项目目前没有 LICENSE 文件，如需使用请在使用前补充相应的协议。
