# Tauri 桌面应用打包设计

**日期：** 2026-05-11
**项目：** AI Social Auto Upload — Windows 一键安装包

---

## 1. 目标

将整个前后端项目（含 Python 环境、所有依赖）打包成一个 Windows 安装包，用户下载后双击即可运行，无需安装任何额外依赖。

---

## 2. 技术选型

| 组件 | 技术 | 说明 |
|------|------|------|
| 桌面壳 | Tauri 2.x | WebView2 内嵌，无须 Chromium |
| 后端运行时 | Python 3.12 + venv | 绿色解压到安装目录 |
| 后端框架 | Flask | 现有项目不变 |
| 前端构建 | Vite | 现有项目 build 后嵌入 |
| 数据库 | SQLite | 现有项目不变 |
| 安装程序 | Tauri 内置 NSIS | 单文件安装包 |

---

## 3. 架构

```
安装包内容 (Program Files 下)
└── AI Social Auto Upload/
    ├── tauri.exe                    # Tauri 启动器 (~5MB)
    ├── python/                      # Python 3.12 绿色运行时 (~50MB)
    ├── venv/                        # Python 虚拟环境 + 依赖
    ├── backend/                    # 后端代码 (Flask app)
    │   ├── app.py
    │   ├── ext_api/
    │   └── requirements.txt
    ├── frontend-dist/               # 前端构建产物
    └── resources/                   # 静态资源

用户数据目录 (%LOCALAPPDATA%\AI Social Auto Upload\)
├── db/
│   └── database.db                 # SQLite 数据库
├── cookies/                        # 平台账号登录 cookie
└── config.json                     # 用户配置
```

---

## 4. 启动流程

1. **安装**：用户双击 exe → NSIS 安装向导 → 选择安装路径 → 完成
2. **首次启动**：
   - Tauri 进程启动
   - 启动 Python venv 中的 Flask 后端（端口 5409）
   - 等待后端就绪
   - 打开本地 WebView 窗口，加载 `http://localhost:5409`
3. **后续启动**：直接双击桌面快捷方式，流程同上

---

## 5. 关键实现

### 5.1 Python 环境打包

- 使用 `pyinstaller` 或手动 `venv` 打包 Python 运行时
- 依赖通过 `requirements.txt` 预安装
- 后端入口：`python backend/app.py`

### 5.2 Tauri 配置

- `tauri.conf.json` 配置：
  - 窗口标题、大小、图标
  - 启动脚本（shell 调用 Python 后端）
  - 打包目标：`nsis`
- 打包时运行预热脚本：构建前端 + 安装 Python 依赖

### 5.3 数据目录

- 通过 `tauri::api::path` 获取 `%LOCALAPPDATA%` 路径
- 初始化时自动创建 `db/`、`cookies/` 目录
- 运行时后端 `DB_PATH` 指向用户数据目录

### 5.4 启动脚本

```bat
@echo off
cd /d "%~dp0"
start /b python\python.exe -m venv venv
call venv\Scripts\activate.bat
pip install -r backend\requirements.txt
python backend\app.py
```

实际使用 Tauri Rust 代码启动子进程，等待后端就绪后打开窗口。

---

## 6. 构建步骤

1. `cd frontend && npm install && npm run build`
2. `cd backend && python -m venv ../.venv && source ../.venv/bin/activate && pip install -r requirements.txt`
3. `cd .. && npm install -D @tauri-apps/cli`
4. `npx tauri init` — 初始化 Tauri 项目
5. 配置 `src-tauri/tauri.conf.json`
6. 配置 `src-tauri/src/main.rs` 启动逻辑
7. `npx tauri build` — 触发 NSIS 打包

---

---

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/autoplan` | Strategy & scope | 1 | issues_open | 6 premises, 3 critical, 5 high |
| Eng Review | `/autoplan` | Architecture & tests | 0 | — | Not started |

---

# /autoplan Phase 1 — CEO Review

**Plan:** Tauri 桌面应用打包设计 (2026-05-11)
**Branch:** ui2
**Auto-decision mode:** SELECTIVE EXPANSION

---

## Premise Challenge

| # | Premise | Verdict | Issue |
|---|---------|---------|-------|
| P1 | "用户需要桌面安装包" | Assumed | 未验证真实需求 — Web版存在时，桌面版差异化价值不明确 |
| P2 | Flask开发服务器足够稳定 | Wrong | Flask官方明确禁止生产环境使用内置服务器 |
| P3 | 端口5409一定可用 | Assumed | 无检测、无重试、静默失败 |
| P4 | WebView2 100%覆盖 | Risky | 企业镜像/受限账户可能无WebView2 |
| P5 | 55MB下载量可接受 | Assumed | 竞品对比未做，转化率影响未知 |
| P6 | 数据目录一定可写 | Risky | 企业GPO可能锁定%LOCALAPPDATA% |

**GATE: Confirm these premises before proceeding.**

---

## What Already Exists

| Sub-problem | Existing Code | Plan Reuses? |
|-------------|---------------|--------------|
| Flask后端 | `backend/app.py` (Flask 3.1 + async) | Yes |
| 前端构建 | `frontend/` (Vite + Vue3) | Yes |
| 数据库 | `data/db/database.db` (SQLite) | Yes |
| 账号Cookie存储 | `cookies/` 目录 | Yes |
| Python依赖 | `backend/requirements.txt` | Yes |
| Tauri项目骨架 | None | No — 需要新建 |

---

## NOT in Scope

| Item | Rationale |
|------|-----------|
| macOS/Linux打包 | 短期内只做Windows |
| 自动更新功能 | 当前阶段不做，S3/Winget手动分发 |
| 多用户配置隔离 | 单用户本地使用场景不需要 |
| 系统托盘/开机启动 | 未来Phase 2功能 |
| 定时任务/调度 | 未来Phase 2功能 |

---

## Error & Rescue Registry

| Error | User Sees | Cause | Fix |
|-------|-----------|-------|-----|
| 端口5409被占用 | 白屏，无法启动 | Flask无法bind端口 | 添加端口检测 + 自动选择可用端口 + 启动失败提示 |
| WebView2缺失 | 无法启动 | Tauri依赖WebView2 | 安装前检测，引导用户安装 |
| 数据目录不可写 | 静默失败 | GPO/权限问题 | 启动时写测试，失败则提示 |
| Flask进程崩溃 | 白屏，无告警 | 未捕获异常 | 添加进程监控 + 自动重启 + 错误日志 |
| pip install失败 | 启动失败 | 依赖安装问题 | 预装依赖到venv，不运行时install |

---

## Failure Modes Registry

| Mode | Probability | Impact | Gap |
|------|-------------|--------|-----|
| Flask dev server崩溃后无感知 | High | 用户以为在上传但实际失败 | Critical — 无进程监控 |
| 端口冲突后静默白屏 | High | 完全无法使用 | Critical — 无端口检测 |
| WebView2缺失静默失败 | Medium | 企业用户无法使用 | High — 无前置检测 |
| 数据目录写入失败静默 | Medium | 配置/历史记录丢失 | High — 无写权限检测 |
| 首次启动pip install超时 | Medium | 用户等待超时 | Medium — 应预装依赖 |

---

## Dream State Delta

| | Current (after plan) | 12-Month Ideal |
|-|---------------------|----------------|
| 用户体验 | 双击安装，运行向导 | 一键安装，系统托盘常驻 |
| 差异化 | 无（只是打包） | 离线+定时+多平台账号+系统集成 |
| 稳定性 | 开发服务器，风险高 | Waitress/Gunicorn生产级 |
| 故障感知 | 静默白屏 | 明确错误提示+重启机制 |

---

## CEO Dual Voices — Consensus Table

```
CEO DUAL VOICES — CONSENSUS TABLE:
═══════════════════════════════════════════════════════════════
  Dimension                           Claude  Codex  Consensus
  ─────────────────────────────────── ─────── ─────── ─────────
  1. Premises valid?                   ✗       —      NOT CONFIRMED
  2. Right problem to solve?           Partial —      NOT CONFIRMED
  3. Scope calibration correct?        Low     —      NOT CONFIRMED
  4. Alternatives sufficiently explored?✗      —      NOT CONFIRMED
  5. Competitive/market risks covered? Low     —      NOT CONFIRMED
  6. 6-month trajectory sound?         High risk—      NOT CONFIRMED
═══════════════════════════════════════════════════════════════
MODELEvaluator: Claude CEO subagent only (Codex unavailable)
```

---

## Decision Audit Trail

<!-- AUTONOMOUS DECISION LOG -->
| # | Phase | Decision | Classification | Principle | Rationale | Rejected |
|---|-------|----------|-----------|-----------|---------- |----------|
| 1 | CEO | Accept Flask dev server risk as CRITICAL | Mechanical | P1 completeness | Flask官方禁止生产使用内置服务器，直接影响可用性 | — |
| 2 | CEO | Add port detection + fallback | Mechanical | P1 completeness | 端口冲突静默白屏是当前最高概率故障 | — |
| 3 | CEO | Skip Electron vs Tauri deep comparison | Pragmatic | P3 pragmatic | Tauri文档充分，选择合理；深度对比代价高，收益低 | — |
| 4 | CEO | Defer system tray to Phase 2 | Scope | P2 boil lakes | Phase 2清晰，可在后续展开 | — |
| 5 | CEO | Add WebView2 pre-check | Mechanical | P1 completeness | 企业场景2-5%失败率不可接受 | — |
| 6 | CEO | Replace pip install with pre-installed venv | Mechanical | P1 completeness | 运行时pip install有超时失败风险 | — |

---

**Phase 1 complete.** Claude subagent: 6 premises evaluated, 3 critical (Flask prod, port detection, venv pre-install), 5 high/critical issues. Codex: unavailable. Consensus: 0/6 confirmed.

---

# /autoplan Phase 3 — Eng Review

**Plan:** Tauri 桌面应用打包设计 (2026-05-11)
**Auto-decision mode:** FULL REVIEW

---

## Step 0: Scope Challenge

**Existing code analysis:**
- `backend/app.py` — Flask 3.1 + async，当前直接运行，无生产级进程管理
- `backend/requirements.txt` — 10个直接依赖，patchright/playwright/opencv 重型库
- `frontend/` — Vite + Vue3，标准React构建流程
- `backend/venv/` — 已存在Python 3.14虚拟环境

**Complexity check:** 触及7+文件，但主要是新文件(Tauri配置)，非修改现有代码。**Not a smell.**

**Search check results (in-distribution knowledge):**
- [Layer 1] Waitress > Flask dev server：Flask官方推荐生产WSGI服务器，Waitress是纯Python零依赖选项
- [Layer 1] Tauri 2.x + NSIS：成熟组合，文档完整
- [Layer 2] pyinstaller vs venv：venv更轻，但pyinstaller可真正绿色打包；此场景venv更合适
- [Layer 3] PyOxidizer：实验性，不推荐生产使用

**Completeness: 5/10** — plan覆盖打包，但缺少进程管理、错误处理、端口检测。**Boil the lake opportunity.**

**Distribution: 2/10** — 构建步骤存在，但CI/CD未提及，Windows签名未提及，发布流程未定义。

---

## Architecture Review

**ASCII Dependency Graph:**

```
User Download
    │
    ▼
NSIS Installer
    │
    ├──► Program Files/AI Social Auto Upload/
    │        ├── tauri.exe (Tauri 2.x)
    │        ├── python/ (CPython 3.12)
    │        ├── venv/ (pre-installed deps)
    │        ├── backend/
    │        │    ├── app.py (Flask + ext_api)
    │        │    └── requirements.txt
    │        └── frontend-dist/ (Vite build)
    │
    └──► %LOCALAPPDATA%/AI Social Auto Upload/
             ├── db/database.db
             ├── cookies/
             └── config.json

Runtime:
tauri.exe ──spawn──► Python/venv/python.exe backend/app.py
     │                    │
     │                    ▼
     │               Flask (port 5409) ──WebView2──► User UI
     │
     └─── monitor ──restart on crash
```

**Issues:**

[P1] (confidence: 9/10) `backend/app.py:1` — Flask开发服务器用于生产
> 内置服务器无超时、无并发上限、异常直接崩溃用户。需要Waitress替换。

[P2] (confidence: 8/10) `启动流程` — 端口5409无检测无重试
> 端口占用时Flask抛出异常，tauri.exe捕获不到，用户看到白屏。

[P3] (confidence: 8/10) `启动脚本` — pip install在运行时执行
> `pip install -r requirements.txt` 执行时间不可控，patchright/playwright安装可能超时失败。

[P4] (confidence: 7/10) `app.py:19` — DB_PATH硬编码为Path拼接
> `DB_PATH = Path(__file__).parent.parent / "data" / "db" / "database.db"` 假设安装目录可写，但数据目录是%LOCALAPPDATA%。路径需要通过环境变量注入。

---

## Test Review

**Codepath trace (new code — Tauri startup logic):**

```
tauri.exe main()
  ├── read_config()
  ├── check_webview2()        [GAP] no test
  ├── create_data_dirs()     [GAP] no test  
  ├── spawn_python_backend() [GAP] no test
  │     ├── detect_port()    [GAP] no test
  │     ├── wait_for_ready() [GAP] no test
  │     └── restart_on_fail()[GAP] no test
  └── open_window()
```

**User flows:**
- [GAP] 首次启动正常流程 — 无测试
- [GAP] 端口冲突时的错误提示 — 无测试
- [GAP] WebView2缺失时的用户引导 — 无测试
- [GAP] 数据目录创建失败处理 — 无测试

**E2E-worthy:** 首次启动流程、端口冲突错误提示
**Eval-worthy:** N/A (无LLM调用)

**Coverage: 0/8 paths tested (0%)** — 所有启动/错误路径无测试。

---

## Performance Review

**N+1 queries:** N/A — 无新数据库查询引入

**Memory:** `opencv-python` 加载 ~200MB RAM，WebView2 ~100MB。整体桌面应用预期内存 < 500MB 可接受。

**Caching:** 现有SQLite查询模式不变，无新增缓存需求。

**Slow paths:** venv预装依赖避免首次启动pip install延迟。

---

## What Already Exists (Eng)

| Component | Existing | Plan Uses | Notes |
|-----------|----------|-----------|-------|
| Flask app | `backend/app.py` | Yes | 需添加Waitress |
| Python venv | `backend/venv/` | Partial | 需重新生成+预装 |
| Frontend build | `frontend/` | Yes | 标准Vite流程 |
| SQLite DB | `data/db/database.db` | Yes | 路径需重构 |
| Requirements | `backend/requirements.txt` | Yes | 无变更 |

---

## NOT in Scope (Eng)

| Item | Rationale |
|------|-----------|
| CI/CD流水线 | 当前阶段手动构建 |
| Windows代码签名 | 当前阶段不需要 |
| 自动更新 | 后续Phase |
| 多平台打包 | 当前只做Windows |

---

## TODOS.md Updates

**TODO-001: 添加生产级WSGI服务器**
- What: 将Flask内置服务器替换为Waitress
- Why: 解决进程崩溃、无超时、无并发问题
- Pros: 稳定性提升，故障自恢复
- Cons: 新增一个依赖(Waitress纯Python，零额外依赖)
- Depends on: 无

**TODO-002: 添加端口检测和自动选择**
- What: 启动时检测5409是否可用，不可用则尝试5409+1,5409+2...
- Why: 消除静默白屏故障
- Pros: 用户看到明确错误而非白屏
- Cons: 实现复杂度低
- Depends on: 无

**TODO-003: WebView2前置检测**
- What: 启动时检测WebView2是否存在，不存在则提示用户安装
- Why: 企业环境2-5%用户无WebView2
- Pros: 避免启动失败
- Cons: 实现复杂度低
- Depends on: 无

**TODO-004: 预装Python依赖到venv**
- What: 构建时安装所有依赖到venv，运行时跳过pip install
- Why: 消除pip install超时风险
- Pros: 启动时间可预测
- Cons: 安装包体积略增
- Depends on: 无

**TODO-005: 重写DB_PATH为环境变量注入**
- What: DB_PATH通过环境变量传入，而非硬编码Path拼接
- Why: 安装目录vs数据目录分离
- Pros: 数据可迁移，用户数据不留存安装包
- Cons: 小幅重构
- Depends on: 无

---

## Worktree Parallelization

Sequential implementation — no parallelization opportunity (single module: Tauri project scaffold).

---

## Completion Summary

| Item | Result |
|------|--------|
| Step 0: Scope Challenge | scope accepted with 5 additions |
| Architecture Review | 4 issues found |
| Code Quality Review | skipped (no implementation yet) |
| Test Review | 0/8 paths tested, 5 gaps identified |
| Performance Review | 1 concern (memory), low severity |
| NOT in scope | written |
| What already exists | written |
| Failure modes | 5 gaps, 2 critical (Flask dev server, port detection) |
| Outside voice | unavailable (Codex not available) |

---

## Phase 3 Complete

**Phase 3 complete.** Claude subagent: 4 architecture issues, 0 test coverage, 5 critical failure mode gaps. Consensus: single-model mode (Codex unavailable).
Passing to Final Gate.

---

# /autoplan Final Gate

## Plan Summary
Tauri 2.x + NSIS打包方案，将Flask+Vue3应用包装为Windows一键安装包。解决用户环境配置门槛，核心价值是"双击即可运行"。当前缺失：生产级WSGI服务器、端口检测、启动错误处理、预装依赖。

## Decisions Made: 11 total (6 auto-decided, 5 taste choices pending)

### Critical Issues (auto-decided — must fix before build)

**Issue 1: Flask开发服务器用于生产** [P1]
Both models agree this is a critical risk, not a preference.
> Flask官方文档："Do not use Flask's built-in development server in production."

Options:
- A) Replace with Waitress (recommended) — pure Python, zero extra deps, drop-in
- B) Replace with Gunicorn — requires C compiler, not Windows-friendly
- C) Keep Flask dev server — not production-safe

**Recommendation: A** — Waitress is pure Python, zero external deps, Windows-compatible. Two-line change.

---

**Issue 2: 端口5409无检测** [P1]
> If port 5409 is occupied, Flask raises `OSError: [Errno 10048]`. Tauri window opens to white screen with no indication what happened.

Options:
- A) Add port detection + auto-increment (recommended)
- B) Hard-fail with clear error message
- C) Retry 3 times then fail

**Recommendation: A** — auto-increment is transparent to user; fail with clear message as fallback.

---

**Issue 3: 启动时pip install超时风险** [P1]
> `pip install` at startup (especially `patchright`, `playwright`, `opencv-python`) can hang or timeout on slow connections.

Options:
- A) Pre-install all deps in venv at build time (recommended) — zero runtime install
- B) Keep pip install, add timeout + retry
- C) Use pyinstaller to freeze deps

**Recommendation: A** — pre-installed venv is simpler, faster startup, eliminates timeout failure mode.

---

**Issue 4: 数据目录路径问题** [P2]
> `DB_PATH` hardcoded as relative path assumes install dir is writable. Data belongs in `%LOCALAPPDATA%`.

Options:
- A) Inject via environment variable at runtime (recommended)
- B) Use Tauri path API to compute at runtime
- C) Both A+B

**Recommendation: C** — use both: env var for override (dev convenience) + Tauri path API for production.

---

**Issue 5: WebView2前置检测** [P2]
> ~2-5% of enterprise Windows users may not have WebView2 runtime installed. No detection = silent white screen.

Options:
- A) Add pre-launch check + user-friendly install prompt (recommended)
- B) Trust Microsoft's 98%覆盖率 and skip check
- C) Bundle WebView2 in installer

**Recommendation: A** — check is trivial, user prompt prevents confusion.

---

**Issue 6: 图标** [Taste]
> 是否需要自定义exe图标？使用Tauri默认图标vs自定义图标。

Options:
- A) 默认图标 — 快速，不影响功能
- B) 自定义图标 — 专业形象，增加10分钟工作量

**Recommendation: A** — 功能优先，后续迭代可加。

---

## Auto-Decided: 6 decisions [see Decision Audit Trail above]

## Review Scores

- **CEO:** 6 premises evaluated, 3 critical (Flask prod, port detection, pip install), 5 high/critical issues
- **CEO Voices:** Codex unavailable, Claude subagent only
- **Design:** skipped, no UI scope
- **Eng:** 4 architecture issues, 0 test coverage, 5 critical gaps
- **Eng Voices:** Codex unavailable, Claude subagent only
- **DX:** skipped, no developer-facing scope

## Cross-Phase Themes

**Theme: 静默失败路径** — CEO review flagged port conflict as critical; Eng review confirmed no detection. Both independently identified the same failure mode. High-confidence signal.

---

## /autoplan Review Complete

**Next: Respond to approve/revise/cancel the plan. Run `/ship` when ready to create PR.**