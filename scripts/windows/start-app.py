"""IndieTracks 一键启动前后端脚本。"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

# 设置控制台编码为 UTF-8
import os
os.system("chcp 65001 >nul 2>&1")
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"

BACKEND_URL = "http://localhost:8080"
FRONTEND_URL = "http://localhost:5173"


def banner(title: str):
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print()


def check_java() -> bool:
    """检查 Java 是否可用。"""
    try:
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_node() -> bool:
    """检查 Node.js 是否可用。"""
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_maven() -> bool:
    """检查 Maven 是否可用。"""
    mvnw = BACKEND_DIR / "mvnw.cmd"
    if mvnw.exists():
        return True
    try:
        result = subprocess.run(
            ["mvn", "--version"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_backend_deps() -> bool:
    """检查后端依赖是否已下载。"""
    m2_repo = Path.home() / ".m2" / "repository"
    if not m2_repo.exists():
        return False
    # 检查关键依赖是否存在
    spring_boot = m2_repo / "org" / "springframework" / "boot"
    return spring_boot.exists()


def install_backend_deps() -> bool:
    """安装后端依赖。"""
    print("  正在下载后端依赖（首次运行可能需要几分钟）...")
    mvnw = BACKEND_DIR / "mvnw.cmd"
    if mvnw.exists():
        result = subprocess.run(
            [str(mvnw), "dependency:resolve"],
            cwd=str(BACKEND_DIR),
            capture_output=True, text=True
        )
        return result.returncode == 0
    else:
        result = subprocess.run(
            ["mvn", "dependency:resolve"],
            cwd=str(BACKEND_DIR),
            capture_output=True, text=True
        )
        return result.returncode == 0


def check_frontend_deps() -> bool:
    """检查前端依赖是否已安装。"""
    node_modules = FRONTEND_DIR / "node_modules"
    package_json = FRONTEND_DIR / "package.json"
    if not node_modules.exists():
        return False
    # 检查关键依赖是否存在
    vue_dir = node_modules / "vue"
    vite_dir = node_modules / "vite"
    return vue_dir.exists() and vite_dir.exists()


def install_frontend_deps() -> bool:
    """安装前端依赖。"""
    print("  正在安装前端依赖...")
    result = subprocess.run(
        ["npm", "install"],
        cwd=str(FRONTEND_DIR),
        capture_output=True, text=True
    )
    return result.returncode == 0


def check_port(port: int) -> bool:
    """检查端口是否被占用。"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def wait_for_port(port: int, timeout: int = 60) -> bool:
    """等待端口可用。"""
    start = time.time()
    while time.time() - start < timeout:
        if check_port(port):
            return True
        time.sleep(1)
    return False


def main():
    banner("IndieTracks 一键启动")

    # ── 环境检查 ────────────────────────────────────
    print("[1/4] 检查运行环境...")

    if not check_java():
        print("  [ERROR] Java 未安装或不在 PATH 中")
        print("  请安装 Amazon Corretto 25 LTS")
        input("按 Enter 退出...")
        sys.exit(1)
    print("  [OK] Java 已就绪")

    if not check_maven():
        print("  [ERROR] Maven 未安装或不在 PATH 中")
        print("  请安装 Maven 或确保 backend/mvnw.cmd 存在")
        input("按 Enter 退出...")
        sys.exit(1)
    print("  [OK] Maven 已就绪")

    if not check_node():
        print("  [ERROR] Node.js 未安装或不在 PATH 中")
        print("  请安装 Node.js 18+")
        input("按 Enter 退出...")
        sys.exit(1)
    print("  [OK] Node.js 已就绪")

    print()

    # ── 依赖检查 ────────────────────────────────────
    print("[2/5] 检查依赖...")

    # 后端依赖
    print("  后端依赖:")
    if check_backend_deps():
        print("    [OK] Maven 依赖已就绪")
    else:
        print("    [WARN] Maven 依赖未安装")
        if not install_backend_deps():
            print("    [ERROR] Maven 依赖安装失败")
            input("按 Enter 退出...")
            sys.exit(1)
        print("    [OK] Maven 依赖安装完成")

    # 前端依赖
    print("  前端依赖:")
    if check_frontend_deps():
        print("    [OK] npm 依赖已就绪")
    else:
        print("    [WARN] npm 依赖未安装")
        if not install_frontend_deps():
            print("    [ERROR] npm 依赖安装失败")
            input("按 Enter 退出...")
            sys.exit(1)
        print("    [OK] npm 依赖安装完成")

    print()

    # ── 端口检查 ────────────────────────────────────
    print("[3/5] 检查端口...")

    backend_port = 8080
    frontend_port = 5173

    # 检查后端端口
    if check_port(backend_port):
        print(f"  [WARN] 端口 {backend_port} 已被占用（后端）")
        print("  提示：Spring Boot 会自动尝试下一个可用端口")
        print("  如果启动失败，请手动停止占用端口的程序")
    else:
        print(f"  [OK] 端口 {backend_port} 可用")

    # 检查前端端口
    if check_port(frontend_port):
        print(f"  [WARN] 端口 {frontend_port} 已被占用（前端）")
        print("  提示：Vite 会自动尝试下一个可用端口（5174, 5175...）")
    else:
        print(f"  [OK] 端口 {frontend_port} 可用")

    print()

    # ── 启动后端 ────────────────────────────────────
    print("[4/5] 启动后端 (Spring Boot)...")
    print(f"  后端地址: http://localhost:{backend_port}")
    print()

    backend_proc = subprocess.Popen(
        ["cmd", "/c", "mvnw.cmd", "spring-boot:run"],
        cwd=str(BACKEND_DIR),
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

    print("  等待后端启动...")
    if wait_for_port(backend_port, timeout=120):
        print(f"  [OK] 后端已启动 (端口 {backend_port})")
    else:
        # 尝试检测是否使用了其他端口
        for port in range(8081, 8090):
            if check_port(port):
                print(f"  [OK] 后端已启动 (端口 {port})")
                backend_port = port
                break
        else:
            print("  [WARN] 后端启动超时，请检查后端窗口")

    print()

    # ── 启动前端 ────────────────────────────────────
    print("[5/5] 启动前端 (Vue 3 + Vite)...")
    print(f"  前端地址: http://localhost:{frontend_port}")
    print()

    frontend_proc = subprocess.Popen(
        ["cmd", "/c", "npm", "run", "dev"],
        cwd=str(FRONTEND_DIR),
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

    print("  等待前端启动...")
    if wait_for_port(frontend_port, timeout=60):
        print(f"  [OK] 前端已启动 (端口 {frontend_port})")
    else:
        # 尝试检测是否使用了其他端口
        for port in range(5174, 5180):
            if check_port(port):
                print(f"  [OK] 前端已启动 (端口 {port})")
                frontend_port = port
                break
        else:
            print("  [WARN] 前端启动超时，请检查前端窗口")

    print()

    # ── 完成 ────────────────────────────────────────
    banner("启动完成!")
    print(f"  前端: http://localhost:{frontend_port}")
    print(f"  后端: http://localhost:{backend_port}")
    print()
    print("  提示：")
    print("  - 前后端在独立的命令行窗口中运行")
    print("  - 关闭对应窗口即可停止服务")
    print("  - 或按 Ctrl+C 停止当前窗口的服务")
    print()

    # 自动打开浏览器
    open_browser = input("  是否打开浏览器？(Y/n): ").strip().lower()
    if open_browser != "n":
        webbrowser.open(f"http://localhost:{frontend_port}")

    print()
    input("按 Enter 退出启动脚本（前后端将继续运行）...")


if __name__ == "__main__":
    main()
