import subprocess
import pathlib

subprocess.Popen(["docker", "compose", "up", "-d"], cwd=pathlib.Path(__file__).parent)

api_proc = subprocess.Popen(["uvicorn", "api_server:app", "--port", "8001"])

frontend_dir = pathlib.Path(__file__).parent / "frontend"
npm_proc = subprocess.Popen(["npm.cmd","run","dev"],cwd=frontend_dir)

api_proc.wait()
npm_proc.wait()