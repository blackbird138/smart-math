# Smart Math

Smart Math 是一个面向数学文档解析和问答的实验项目。项目通过 Mineru 服务解析 PDF 内容，使用 RAG（Retrieval Augmented Generation）方式将检索到的文档与 LLM 结合来生成答案。

更多详情请参见 [架构文档](docs/architecture.md)。

## 项目结构
- `mineru_service/`：FastAPI 服务，提供 `/parse` 接口解析 PDF，通过 Dockerfile 构建镜像
- `src/`：数据清洗、文本切片和向量检索的核心代码
- `frontend/`：基于 Vue 3 + TypeScript 的前端项目
- `api_server.py`：提供 `/ingest` 和 `/search` 接口的简易 FastAPI 应用
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
   npm install  # 安装包含 Vuetify 在内的依赖
   npm run dev
   ```

## 快速使用
可以以 `test.py` 为例，向本地 Mineru 服务上传 PDF 并获取解析结果。`src/pipeline.py` 中的 `SmartMathPipeline` 执行数据加载、清洗和向量化流程。

如需通过 HTTP 调用，可启动 `api_server.py`：
```bash
uvicorn api_server:app --reload --port 8001
```

## 日志
所有运行日志会写入项目根目录的 `logs/app.log`，便于排查问题。

## 运行测试
```bash
cd tests
PYTHONPATH=.. pytest
```

## 版权声明
本项目基于 MIT 许可证发布，详见 LICENSE 文件。
