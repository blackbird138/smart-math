# Smart Math

Smart Math 致力于自动解析数学 PDF 文档并提供问答能力，结合
RAG（Retrieval Augmented Generation）技术与大语言模型生成解答。项目内含后端
FastAPI 服务、前端界面及一套数据处理流程。

更多细节请查看 [架构文档](docs/architecture.md)。

## 项目结构
- `mineru_service/`：PDF 解析服务，提供 `/parse` 接口，可通过 Dockerfile 构建
- `src/`：清洗、切片、向量化及解题相关核心代码
- `frontend/`：基于 Vue3 + TypeScript 的前端工程
- `api_server.py`：对外的 API 服务，实现文件索引、检索和解题等接口
- `config/`：模型与 RAG 配置
- `tests/`：Pytest 单元测试

## 环境配置
1. 安装 Python 3.11，并安装依赖
   ```bash
   pip install -r requirements.txt
   ```
2. 构建 Mineru 解析服务
   ```bash
   docker-compose build
   ```
3. 构建前端
   ```bash
   cd frontend
   npm install
   ```

## 快速开始
在根目录下运行即可启动项目
   ```bash
   python launcher.py
   ```

## 技术文档
### API 文档
| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `POST` | `/update_env` | 更新 API Key 等环境变量 |
| `POST` | `/ingest` | 上传并索引单个 PDF |
| `GET` | `/search` | 在指定文件索引中检索 |
| `GET` | `/list_files` | 列出已上传的文件 |
| `POST` | `/image_ocr` | 图片公式识别为 LaTeX |
| `POST` | `/build_graph` | 构建指定文件的关系图 |
| `GET` | `/list_chunks` | 获取文件中所有切片信息 |
| `GET` | `/list_related` | 查看与某个切片相关的条目 |
| `GET` | `/get_chunk` | 按 ID 获取切片内容 |
| `POST` | `/solve` | 根据问题返回答案 |
| `POST` | `/solve_stream` | 以流式方式返回答案 |

### 用户手册
1. 通过 `/ingest` 上传 PDF，得到 `file_id`
2. 使用 `/search` 查询相关片段或 `/list_chunks` 查看所有切片
3. 如需构建关系图，调用 `/build_graph`
4. 使用 `/solve` 或 `/solve_stream` 提出数学问题，`file_id` 对应上传的文档
5. 前端页面可直接上传文件并提问，后端 API 统一由 `api_server.py` 提供

## 版权声明
本项目基于 MIT 许可证发布，详见 LICENSE。