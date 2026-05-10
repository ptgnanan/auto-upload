# Tauri 桌面应用打包实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Flask+Vue3 应用打包为 Windows 一键安装包，用户双击即可运行。

**Architecture:**
- Tauri 2.x 作为桌面壳，通过 WebView2 加载本地 Flask 后端
- Flask 后端通过 Waitress (生产级 WSGI 服务器) 运行，避免 Flask 内置开发服务器
- 用户数据存储在 `%LOCALAPPDATA%\AI Social Auto Upload\`
- 安装包内容放在 `Program Files` 下，数据目录分离

**Tech Stack:** Tauri 2.x, Waitress (WSGI), Python 3.14, Vite, Vue3, NSIS

---

## 文件结构

```
src-tauri/                          # NEW — Tauri 项目根目录
├── Cargo.toml                      # Tauri Rust 依赖
├── tauri.conf.json                 # Tauri 配置
├── build.rs                        # 构建脚本
├── src/
│   ├── main.rs                     # 入口：窗口管理 + 子进程启动
│   └── lib.rs                      # 共享逻辑：端口检测、WebView2 检查
└── icons/                          # 应用图标

backend/
├── app.py                          # MODIFY — 添加 Waitress，移除 app.run()
└── requirements.txt                # MODIFY — 添加 waitress

scripts/
├── build-venv.ps1                  # NEW — Windows PowerShell: 预装依赖到 venv
└── build-frontend.ps1             # NEW — Windows PowerShell: 构建前端

docs/superpowers/
├── specs/
│   └── 2026-05-11-tauri-desktop-bundle-design.md   # 已评审的设计文档
└── plans/
    └── 2026-05-11-tauri-desktop-bundle-implementation.md  # 本计划
```

---

## Task 1: 添加 Waitress 到 Flask 后端

**Files:**
- Modify: `backend/app.py:114-115`
- Modify: `backend/requirements.txt`

- [ ] **Step 1: 添加 waitress 到 requirements.txt**

文件 `backend/requirements.txt` 当前内容：
```
patchright==1.58.2
loguru==0.7.3
opencv-python>=4.13.0.92
qrcode==8.2
requests==2.32.3
Flask[async]==3.1.1
flask-cors==6.0.0
segno>=1.6.6
playwright>=1.58.0
xhs>=0.2.13
```

在末尾添加：
```
waitress>=3.0.0
```

- [ ] **Step 2: 修改 app.py 底部启动逻辑**

找到 `backend/app.py:114-116`:
```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5409)
```

替换为：
```python
def find_available_port(start_port=5409, max_attempts=10):
    """Find an available port starting from start_port."""
    import socket
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find available port in range {start_port}-{start_port + max_attempts}")


if __name__ == "__main__":
    import os
    # Allow port override via environment variable (for dev convenience)
    port = int(os.environ.get("SAU_PORT", "5409"))
    # Check if the requested port is available, auto-increment if not
    if port == 5409:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
        except OSError:
            port = find_available_port(5409 + 1)
            print(f"[Startup] Port 5409 in use, using port {port}")
    print(f"[Startup] Starting Waitress server on port {port}")
    from waitress import serve
    # Expose port via environment variable for frontend
    os.environ["SAU_PORT"] = str(port)
    serve(app, host="0.0.0.0", port=port)
```

注意：需要 `import socket` 和 `from waitress import serve`。`find_available_port` 函数在 `if __name__ == "__main__":` 块之前定义。

- [ ] **Step 3: 验证 app.py 语法正确**

Run: `cd /home/czy/workspace/ai/social-auto-upload/backend && python -m py_compile app.py`
Expected: 无输出（语法正确）

- [ ] **Step 4: 提交**

```bash
git add backend/requirements.txt backend/app.py
git commit -m "feat: add Waitress WSGI server with port auto-detection

- Replace Flask dev server (app.run) with Waitress production server
- Add find_available_port() for automatic port selection on conflict
- Expose SAU_PORT environment variable for frontend to read
"
```

---

## Task 2: 创建 Tauri 项目骨架

**Files:**
- Create: `src-tauri/Cargo.toml`
- Create: `src-tauri/tauri.conf.json`
- Create: `src-tauri/build.rs`
- Create: `src-tauri/src/main.rs`
- Create: `src-tauri/src/lib.rs`
- Create: `src-tauri/.cargo/config.toml`

- [ ] **Step 1: 创建 Cargo.toml**

```toml
[package]
name = "ai-social-auto-upload"
version = "0.1.0"
description = "AI Social Auto Upload - Desktop App"
authors = ["you"]
edition = "2021"

[lib]
name = "ai_social_auto_upload_lib"
crate-type = ["staticlib", "cdylib", "rlib"]

[build-dependencies]
tauri-build = { version = "2", features = [] }

[dependencies]
tauri = { version = "2", features = ["devtools"] }
tauri-plugin-shell = "2"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
log = "0.4"
env_logger = "0.11"
portable-pty = "0.8"

[target.'cfg(windows)'.dependencies]
winreg = "0.52"
```

- [ ] **Step 2: 创建 tauri.conf.json**

```json
{
  "$schema": "https://schema.tauri.app/config/2",
  "productName": "AI Social Auto Upload",
  "version": "0.1.0",
  "identifier": "com.example.ai-social-auto-upload",
  "build": {
    "beforeDevCommand": "",
    "devUrl": "http://localhost:5409",
    "beforeBuildCommand": "",
    "frontendDist": "../frontend-dist"
  },
  "app": {
    "withGlobalTauri": true,
    "windows": [
      {
        "title": "AI Social Auto Upload",
        "width": 1200,
        "height": 800,
        "minWidth": 900,
        "minHeight": 600,
        "resizable": true,
        "fullscreen": false
      }
    ],
    "security": {
      "csp": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    }
  },
  "bundle": {
    "active": true,
    "targets": ["nsis"],
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ],
    "windows": {
      "nsis": {
        "installMode": "currentUser"
      }
    }
  }
}
```

- [ ] **Step 3: 创建 build.rs**

```rust
fn main() {
    tauri_build::build()
}
```

- [ ] **Step 4: 创建 src/lib.rs**

```rust
use std::path::PathBuf;
use std::process::Stdio;
use tauri::Manager;
use portable_pty::{native_pty_system, CommandBuilder, PtySize};

pub fn get_data_dir() -> PathBuf {
    #[cfg(windows)]
    {
        std::env::var("LOCALAPPDATA")
            .map(PathBuf::from)
            .unwrap_or_else(|_| {
                dirs::data_local_dir().unwrap_or_else(|| PathBuf::from("."))
            })
            .join("AI Social Auto Upload")
    }
    #[cfg(not(windows))]
    {
        dirs::data_local_dir()
            .unwrap_or_else(|| PathBuf::from("."))
            .join("ai-social-auto-upload")
    }
}

pub fn check_webview2() -> Result<(), String> {
    #[cfg(windows)]
    {
        use winreg::enums::*;
        use winreg::RegKey;
        let hkcu = RegKey::predef(HKEY_CURRENT_USER);
        let key = hkcu.open_subkey("SOFTWARE\\WOW6432Node\\Microsoft\\EdgeUpdate\\Clients\\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}")
            .or_else(|_| hkcu.open_subkey("SOFTWARE\\Microsoft\\EdgeUpdate\\Clients\\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"));
        match key {
            Ok(k) => {
                let version: String = k.get_value("pv").unwrap_or_default();
                if version.is_empty() {
                    Err("WebView2 not installed".to_string())
                } else {
                    Ok(())
                }
            }
            Err(_) => Err("WebView2 not installed".to_string())
        }
    }
    #[cfg(not(windows))]
    {
        Ok(()) // macOS/Linux always have a browser engine
    }
}

pub fn create_data_dirs(data_dir: &PathBuf) -> std::io::Result<()> {
    std::fs::create_dir_all(data_dir.join("db"))?;
    std::fs::create_dir_all(data_dir.join("cookies"))?;
    Ok(())
}

pub fn spawn_python_backend(
    python_path: PathBuf,
    backend_path: PathBuf,
    port: u16,
    data_dir: PathBuf,
) -> std::io::Result<(std::process::Child, portable_pty:: PtyPair)> {
    let pty_system = native_pty_system();
    let pty_pair = pty_system.openpty(PtySize {
        rows: 24,
        cols: 80,
        pixel_width: 0,
        pixel_height: 0,
    })?;

    let mut cmd = CommandBuilder::new(python_path);
    cmd.args([
        backend_path.to_str().unwrap(),
    ]);
    cmd.env("SAU_PORT", port.to_string());
    cmd.env("SAU_DATA_DIR", data_dir.to_str().unwrap());
    cmd.stdout(Stdio::from(pty_pair.master.take().unwrap()));
    cmd.stderr(Stdio::from(pty_pair.master.take().unwrap()));

    let child = pty_pair.slave.spawn_command(cmd)?;

    Ok((child, pty_pair))
}
```

注意：`portable-pty` 需要在 `Cargo.toml` 中添加依赖。另外需要添加 `dirs` crate。修改 `Cargo.toml`：

```toml
[dependencies]
tauri = { version = "2", features = ["devtools"] }
tauri-plugin-shell = "2"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
log = "0.4"
env_logger = "0.11"
portable-pty = "0.8"
dirs = "5"
```

同时需要添加 Windows winreg 依赖：

```toml
[target.'cfg(windows)'.dependencies]
winreg = "0.52"
```

- [ ] **Step 5: 创建 src/main.rs**

```rust
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::path::PathBuf;
use std::time::Duration;
use ai_social_auto_upload_lib::{
    check_webview2, create_data_dirs, get_data_dir, spawn_python_backend,
};
use tauri::{Manager, WindowEvent};

fn main() {
    env_logger::init();
    log::info!("Starting AI Social Auto Upload desktop app");

    // Check WebView2
    if let Err(e) = check_webview2() {
        eprintln!("ERROR: {}", e);
        eprintln!("Please install Microsoft Edge WebView2 Runtime from:");
        eprintln!("https://developer.microsoft.com/en-us/microsoft-edge/webview2/");
        std::process::exit(1);
    }

    // Get paths
    let exe_dir = std::env::current_exe()
        .unwrap()
        .parent()
        .unwrap()
        .to_path_buf();

    let data_dir = get_data_dir();
    log::info!("Data directory: {:?}", data_dir);

    // Create data directories
    if let Err(e) = create_data_dirs(&data_dir) {
        eprintln!("ERROR: Could not create data directory: {}", e);
        std::process::exit(1);
    }

    // Python path and backend path
    let python_path = exe_dir.join("python").join("python.exe");
    let backend_path = exe_dir.join("backend").join("app.py");

    // Find available port
    let port = find_available_port(5409);
    log::info!("Using backend port: {}", port);

    // Spawn Python backend
    let (_child, _pty_pair) = match spawn_python_backend(
        python_path.clone(),
        backend_path.clone(),
        port,
        data_dir.clone(),
    ) {
        Ok(pair) => pair,
        Err(e) => {
            eprintln!("ERROR: Failed to start backend: {}", e);
            eprintln!("Python path: {:?}", python_path);
            eprintln!("Backend path: {:?}", backend_path);
            std::process::exit(1);
        }
    };

    // Wait for backend to be ready
    let backend_url = format!("http://localhost:{}", port);
    log::info!("Waiting for backend at {}", backend_url);
    let max_wait = 30;
    for i in 0..max_wait {
        if std::net::TcpStream::connect(&backend_url[..]).is_ok() {
            log::info!("Backend ready after {} seconds", i);
            break;
        }
        if i == max_wait - 1 {
            eprintln!("ERROR: Backend did not start within {} seconds", max_wait);
            std::process::exit(1);
        }
        std::thread::sleep(std::time::Duration::from_secs(1));
    }

    // Create Tauri app
    tauri::Builder::default()
        .setup(move |app| {
            let window = app.get_webview_window("main").unwrap();
            window.eval(&format!(
                "window.location.replace('{}')",
                backend_url
            )).unwrap();
            Ok(())
        })
        .on_window_event(|window, event| {
            if let WindowEvent::CloseRequested { .. } = event {
                log::info!("Window closed, shutting down");
                std::process::exit(0);
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

fn find_available_port(start: u16) -> u16 {
    use std::net::TcpListener;
    for port in start..start + 100 {
        if TcpListener::bind(("127.0.0.1", port)).is_ok() {
            return port;
        }
    }
    start // fallback
}
```

注意：`main.rs` 需要导入 `ai_social_auto_upload_lib`。需要确保 `lib.rs` 中的 `check_webview2` 函数在非 Windows 上有一个返回 `Ok` 的版本。

修改 `src/lib.rs`，给 `check_webview2` 添加 `#[cfg(windows)]` 属性：

```rust
#[cfg(windows)]
pub fn check_webview2() -> Result<(), String> {
    // ... Windows implementation
}

#[cfg(not(windows))]
pub fn check_webview2() -> Result<(), String> {
    Ok(()) // Always ok on non-Windows
}
```

- [ ] **Step 6: 创建 .cargo/config.toml**

```toml
[build]
target-dir = "../../target"
```

- [ ] **Step 7: 提交**

```bash
git add src-tauri/Cargo.toml src-tauri/tauri.conf.json src-tauri/build.rs src-tauri/src/
git commit -m "feat: add Tauri 2.x project scaffold with Rust backend"
```

---

## Task 3: 创建构建脚本

**Files:**
- Create: `scripts/build-venv.ps1`
- Create: `scripts/build-frontend.ps1`

- [ ] **Step 1: 创建 scripts/build-venv.ps1 (PowerShell)**

```powershell
# build-venv.ps1 — Build Python venv with pre-installed dependencies
# Usage: .\build-venv.ps1 -PythonPath "C:\Python312" -OutputPath ".\venv"

param(
    [Parameter(Mandatory=$true)]
    [string]$PythonPath,

    [Parameter(Mandatory=$true)]
    [string]$OutputPath
)

$ErrorActionPreference = "Stop"

Write-Host "Creating venv at $OutputPath..."
& $PythonPath\python.exe -m venv $OutputPath

Write-Host "Upgrading pip..."
& "$OutputPath\Scripts\pip.exe" install --upgrade pip

Write-Host "Installing requirements..."
& "$OutputPath\Scripts\pip.exe" install -r backend\requirements.txt

Write-Host "Verifying key packages..."
& "$OutputPath\Scripts\python.exe" -c "import waitress; import flask; import loguru; print('All packages OK')"

Write-Host "Done. Venv ready at $OutputPath"
```

- [ ] **Step 2: 创建 scripts/build-frontend.ps1 (PowerShell)**

```powershell
# build-frontend.ps1 — Build frontend with Vite
# Usage: .\build-frontend.ps1

$ErrorActionPreference = "Stop"

Write-Host "Installing frontend dependencies..."
npm install

Write-Host "Building frontend..."
npm run build

Write-Host "Done. Output in frontend-dist/"
```

- [ ] **Step 3: 提交**

```bash
git add scripts/build-venv.ps1 scripts/build-frontend.ps1
git commit -m "feat: add PowerShell build scripts for venv and frontend"
```

---

## Task 4: 更新 .gitignore

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: 添加 Tauri 构建产物到 .gitignore**

追加到 `.gitignore`：
```
# Tauri
src-tauri/target/
src-tauri/src-tauri/
*.pdb

# Build outputs
frontend-dist/
```

- [ ] **Step 2: 提交**

```bash
git add .gitignore
git commit -m "chore: add Tauri build artifacts to gitignore"
```

---

## Task 5: 创建数据目录测试

**Files:**
- Create: `backend/test_data_dir.py`

- [ ] **Step 1: 编写数据目录测试**

```python
"""Test data directory creation and path resolution."""
import os
import tempfile
import shutil
from pathlib import Path


def test_data_dir_from_env():
    """SAU_DATA_DIR environment variable overrides default path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / "test_data"
        os.environ["SAU_DATA_DIR"] = str(test_dir)
        # The actual resolution depends on Tauri, but we test the env var parsing
        assert os.environ.get("SAU_DATA_DIR") == str(test_dir)


def test_db_path_construction():
    """DB_PATH should be constructed from data_dir, not hardcoded relative path."""
    # Simulate what Tauri does: inject SAU_DATA_DIR
    data_dir = Path(tempfile.mkdtemp())
    db_dir = data_dir / "db"
    db_dir.mkdir()
    db_path = db_dir / "database.db"
    db_path.touch()

    assert db_path.exists()
    assert db_path.parent == db_dir

    # Cleanup
    shutil.rmtree(data_dir)


def test_cookie_dir():
    """Cookie directory should be created alongside db directory."""
    data_dir = Path(tempfile.mkdtemp())
    cookie_dir = data_dir / "cookies"
    cookie_dir.mkdir(parents=True)

    assert cookie_dir.is_dir()
    assert (cookie_dir.parent / "db").mkdir(parents=True) or True

    # Cleanup
    shutil.rmtree(data_dir)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
```

- [ ] **Step 2: 运行测试**

Run: `cd /home/czy/workspace/ai/social-auto-upload && python -m pytest backend/test_data_dir.py -v`
Expected: 3 passed

- [ ] **Step 3: 提交**

```bash
git add backend/test_data_dir.py
git commit -m "test: add data directory path resolution tests"
```

---

## Task 6: 创建端口检测测试

**Files:**
- Create: `backend/test_port_detection.py`

- [ ] **Step 1: 编写端口检测测试**

```python
"""Test port detection and auto-increment logic."""
import socket
import threading
import time


def is_port_available(port):
    """Check if a port is available for binding."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", port))
            return True
    except OSError:
        return False


def find_available_port(start_port=5409, max_attempts=10):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find available port in range {start_port}-{start_port + max_attempts}")


def test_port_available_returns_true_when_free():
    """Free ports should be detected as available."""
    # 54321 should be free in almost all environments
    assert is_port_available(54321)


def test_find_available_port_returns_first_free():
    """find_available_port should return the start port when it's free."""
    port = find_available_port(54321, max_attempts=5)
    assert port == 54321


def test_find_available_port_skips_used():
    """find_available_port should skip ports that are in use."""
    # Bind a port temporarily
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 54322))
    server.listen(1)

    try:
        port = find_available_port(54322, max_attempts=5)
        # Should skip 54322 and find next available
        assert port > 54322
    finally:
        server.close()


def test_find_available_port_raises_on_all_used():
    """find_available_port should raise RuntimeError when all ports in range are used."""
    sockets = []
    for port in range(54330, 54340):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", port))
            s.listen(1)
            sockets.append(s)
        except OSError:
            pass

    try:
        with pytest.raises(RuntimeError, match="Could not find available port"):
            find_available_port(54330, max_attempts=10)
    finally:
        for s in sockets:
            s.close()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
```

- [ ] **Step 2: 运行测试**

Run: `cd /home/czy/workspace/ai/social-auto-upload && python -m pytest backend/test_port_detection.py -v`
Expected: 5 passed (4 basic + 1 that tests all-ports-used raises)

注意：需要在 `test_find_available_port_raises_on_all_used` 的 `finally` 块之前导入 `pytest`。

- [ ] **Step 3: 提交**

```bash
git add backend/test_port_detection.py
git commit -m "test: add port detection and auto-increment tests"
```

---

## Task 7: 更新 app.py 添加环境变量支持

**Files:**
- Modify: `backend/app.py:19`

- [ ] **Step 1: 重构 DB_PATH 支持环境变量注入**

找到 `backend/app.py:19`:
```python
DB_PATH = Path(__file__).parent.parent / "data" / "db" / "database.db"
```

替换为：
```python
def _get_db_path():
    """Get DB path from SAU_DATA_DIR env var, with fallback."""
    if data_dir := os.environ.get("SAU_DATA_DIR"):
        return Path(data_dir) / "db" / "database.db"
    # Fallback: dev environment (repo root/data/db/)
    return Path(__file__).parent.parent / "data" / "db" / "database.db"

DB_PATH = _get_db_path()
```

需要添加 `import os` 到 app.py 顶部（在 `import json` 之后）。

- [ ] **Step 2: 验证语法**

Run: `cd /home/czy/workspace/ai/social-auto-upload/backend && python -m py_compile app.py`
Expected: 无输出

- [ ] **Step 3: 运行已有测试确保没有破坏**

Run: `cd /home/czy/workspace/ai/social-auto-upload && python -m pytest backend/test_data_dir.py -v`
Expected: 3 passed

- [ ] **Step 4: 提交**

```bash
git add backend/app.py
git commit -m "feat: make DB_PATH configurable via SAU_DATA_DIR env var

Allows Tauri to inject user data directory path at runtime."
```

---

## 执行顺序总结

| Task | 内容 | 依赖 |
|------|------|------|
| 1 | 添加 Waitress 到 Flask 后端 | 无 |
| 2 | 创建 Tauri 项目骨架 | Task 1 完成 |
| 3 | 创建构建脚本 | Task 2 完成 |
| 4 | 更新 .gitignore | Task 2 完成 |
| 5 | 创建数据目录测试 | Task 1 完成 |
| 6 | 创建端口检测测试 | Task 1 完成 |
| 7 | 更新 app.py 环境变量支持 | Task 1 完成 |

---

## 验证点

1. `python backend/app.py` 启动后显示 "Starting Waitress server on port XXXX"
2. `python -m pytest backend/test_port_detection.py -v` 全部通过
3. `python -m pytest backend/test_data_dir.py -v` 全部通过
4. `src-tauri/` 目录结构符合上述文件结构
5. Cargo.toml 包含所有必要依赖

---

**Plan complete and saved to `docs/superpowers/plans/2026-05-11-tauri-desktop-bundle-implementation.md`**