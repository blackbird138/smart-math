import pathlib
import subprocess
import sys
import time
from typing import List

ROOT_DIR = pathlib.Path(__file__).parent


def run_docker() -> None:
    """启动 docker compose，并在失败时直接退出。"""
    try:
        subprocess.run(
            ["docker", "compose", "up", "-d"],
            cwd=ROOT_DIR,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        print("Docker 服务启动失败：")
        print(exc.stdout)
        sys.exit(exc.returncode)


def stop_processes(processes: List[subprocess.Popen]) -> None:
    """终止已启动的子进程，并关闭 docker 服务。"""
    for proc in processes:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
    subprocess.run(["docker", "compose", "down"], cwd=ROOT_DIR)


def main() -> None:
    run_docker()
    print("Mineru 服务：启动")

    processes: List[subprocess.Popen] = []
    try:
        api_proc = subprocess.Popen(
            ["uvicorn", "api_server:app", "--port", "8001"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        processes.append(api_proc)
    except FileNotFoundError as exc:
        print("启动 API 服务失败：", exc)
        stop_processes(processes)
        sys.exit(1)
    print("API 服务：启动")

    try:
        npm_proc = subprocess.Popen(
            ["npm.cmd", "run", "dev"],
            cwd=ROOT_DIR / "frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        processes.append(npm_proc)
    except FileNotFoundError as exc:
        print("启动前端失败：", exc)
        stop_processes(processes)
        sys.exit(1)
    print("前端：启动")
    print("http://localhost:5173/")

    try:
        while True:
            for proc in processes:
                ret = proc.poll()
                if ret is not None:
                    output = proc.stdout.read() if proc.stdout else ""
                    print(f"进程 {proc.args} 退出，返回码 {ret}：\n{output}")
                    if ret != 0:
                        stop_processes(processes)
                        sys.exit(ret)
                    processes.remove(proc)
                    if not processes:
                        stop_processes(processes)
                        return
            time.sleep(1)
    except KeyboardInterrupt:
        stop_processes(processes)


if __name__ == "__main__":
    main()