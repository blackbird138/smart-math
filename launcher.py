import subprocess
import pathlib

# 启动 Mineru（如果已经在运行，可跳过）
subprocess.Popen(["docker", "compose", "up", "-d"], cwd=pathlib.Path(__file__).parent)

# 启动 API Server
api_proc = subprocess.Popen(["uvicorn", "api_server:app", "--port", "8001"])

# 启动前端
frontend_dir = pathlib.Path(__file__).parent / "frontend"
npm_proc = subprocess.Popen(["npm", "run", "dev"], cwd=frontend_dir)

api_proc.wait()
npm_proc.wait()