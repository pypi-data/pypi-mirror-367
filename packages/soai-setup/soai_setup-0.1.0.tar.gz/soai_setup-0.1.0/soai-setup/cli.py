import subprocess
import platform
import sys
import os

def run(cmd, sudo=False):
    if sudo and platform.system() != "Windows":
        cmd = f"sudo {cmd}"
    print(f"\n➡️  Running: {cmd}")
    subprocess.run(cmd, shell=True, check=False)

def install_vscode_extensions():
    print("\n🔌 Installing VS Code Extensions...")
    extensions = [
        "ms-python.python",
        "ms-toolsai.jupyter",
        "charliermarsh.ruff",
        "cline.dev-coder"
    ]
    for ext in extensions:
        run(f"code --install-extension {ext}")

def install_uv_and_packages():
    print("\n📦 Installing uv and Python packages...")
    run("pip install uv")
    packages = ["numpy", "pandas", "streamlit"]
    for pkg in packages:
        run(f"uv pip install {pkg}")

def main():
    os_name = platform.system()
    print("🚀 SoAI 2025 Dev Setup Starting...")
    print(f"🔍 Detected OS: {os_name}")

    # Install Git
    run("git --version || sudo apt install git -y", sudo=True)

    # Install Python
    run("python3.11 --version || sudo apt install python3.11 python3.11-venv -y", sudo=True)

    # Install VS Code
    if os_name == "Linux":
        run("code --version || sudo snap install code --classic", sudo=True)
    elif os_name == "Darwin":
        print("🛠️  Please install VS Code from: https://code.visualstudio.com/")
    elif os_name == "Windows":
        print("🛠️  Please install VS Code manually or via Winget.")

    # VS Code Extensions
    install_vscode_extensions()

    # UV and Python Packages
    install_uv_and_packages()

    print("\n✅ All tools installed for SoAI 2025!")

if __name__ == "__main__":
    main()
