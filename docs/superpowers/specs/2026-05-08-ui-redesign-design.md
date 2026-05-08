# UI Redesign: Social Auto Upload

**Date:** 2026-05-08
**Branch:** feat/ui-redesign
**Status:** Approved

## Overview

Complete UI redesign of the Social Auto Upload content distribution platform. Redesign all 4 existing pages, implement 3 placeholder pages with full functionality, and establish a new unified design language.

**Design Direction:** Gradient Vibrant Dark — purple-blue gradient accents on deep dark backgrounds, modern and professional feel suitable for a content distribution platform.

**Implementation Strategy:** Bottom-up — design system tokens first, then layout shell, then shared components, then individual pages.

## 1. Design System Tokens

### Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| `$bg-base` | `#0a0a1a` | Page background (deepest) |
| `$bg-elevated` | `#12122a` | Card/panel background |
| `$bg-surface` | `rgba(255,255,255,0.04)` | Semi-transparent overlay |
| `$brand-start` | `#8b5cf6` | Purple — gradient start |
| `$brand-end` | `#3b82f6` | Blue — gradient end |
| `$accent-cyan` | `#06b6d4` | Cyan accent |
| `$accent-green` | `#22c55e` | Green accent |
| `$accent-rose` | `#f43f5e` | Rose/red accent (Douyin) |
| `$accent-amber` | `#f59e0b` | Amber accent (Kuaishou) |
| `$text-primary` | `#f1f5f9` | Headings, body text |
| `$text-secondary` | `#94a3b8` | Descriptions, labels |
| `$text-muted` | `#64748b` | Placeholders, disabled |
| `$border` | `rgba(255,255,255,0.08)` | General borders |
| `$border-active` | `rgba(139,92,246,0.25)` | Active/focus borders |

### Gradient Presets

| Name | Value |
|------|-------|
| Brand | `linear-gradient(135deg, $brand-start, $brand-end)` |
| Brand subtle bg | `linear-gradient(135deg, rgba($brand-start, 0.12), rgba($brand-end, 0.08))` |
| Success | `linear-gradient(135deg, rgba(34,197,94,0.15), rgba(6,182,212,0.1))` |
| Danger | `linear-gradient(135deg, rgba(239,68,68,0.15), rgba(244,63,94,0.1))` |
| Info | `linear-gradient(135deg, rgba(59,130,246,0.15), rgba(139,92,246,0.1))` |
| Cyan | `linear-gradient(135deg, rgba(6,182,212,0.15), rgba(34,197,94,0.1))` |

### Platform Colors

| Platform | Primary | Background |
|----------|---------|------------|
| Douyin | `#f43f5e` (rose) | `rgba(244,63,94,0.15)` |
| Kuaishou | `#f59e0b` (amber) | `rgba(245,158,11,0.15)` |
| WeChat Channels | `#3b82f6` (blue) | `rgba(59,130,246,0.15)` |
| Xiaohongshu | `#8b5cf6` (violet) | `rgba(139,92,246,0.15)` |

### Spacing, Radius, Effects

- **Border radius:** 12px (cards), 10px (buttons/inputs), 14px (large cards), 8px (tags)
- **Shadows:** No traditional box-shadow. Use border-glow: `0 0 20px rgba($brand-start, 0.08)` for elevation
- **Transitions:** `200ms cubic-bezier(0.4, 0, 0.2, 1)` unified
- **Typography:** System font stack only, no external fonts

## 2. Layout Shell (App.vue)

### Icon Rail Navigation (64px fixed)

```
┌──────┬─────────────────────────────────────┐
│      │  Header (48px)                       │
│ Icon │  Breadcrumb left + User area right   │
│ Rail ├─────────────────────────────────────┤
│(64px)│                                      │
│      │  Main Content (padding: 24px)        │
│ Logo │  Full width                          │
│ ──── │                                      │
│ Nav  │                                      │
│ icons│                                      │
│ ...  │                                      │
│      │                                      │
│ ──── │                                      │
│ Cog  │                                      │
└──────┴─────────────────────────────────────┘
```

**Icon Rail details:**
- Top: Brand logo (gradient circle, tooltip on hover)
- Middle: Navigation icons (SVG), active state uses gradient background highlight
- Separator line
- Bottom: Settings icon
- Hover: floating tooltip panel to the right showing page name

**Header:**
- Left: Breadcrumb navigation
- Right: User info area (reserved for avatar, notification bell)
- Background: `rgba(255,255,255,0.03)` + bottom border
- Height: 48px

**Page transitions:** router-view with `fade-slide` transition (150ms)

## 3. Component Library

### Card
- Background: `rgba(255,255,255,0.04)` + border `rgba(255,255,255,0.08)`
- Border-radius: 12px, no traditional shadow
- Hover: border → `rgba(139,92,246,0.25)` + glow `box-shadow: 0 0 20px rgba(139,92,246,0.06)`
- Stat cards: individual theme gradients (purple/blue/cyan/green) with gradient icon container top-left

### Table (Element Plus override)
- Header bg: `rgba(255,255,255,0.03)`
- Row hover: `rgba(139,92,246,0.06)`
- Borders: `rgba(255,255,255,0.04)`
- Wrapped in 12px border-radius container, no hard Element Plus borders

### Dialog
- Background: `#12122a`
- Border: `rgba(139,92,246,0.15)`
- Border-radius: 16px
- Overlay: `backdrop-filter: blur(4px)`

### Buttons
- Primary: brand gradient `linear-gradient(135deg, #8b5cf6, #3b82f6)`
- Secondary: `rgba(255,255,255,0.06)` bg + brand border
- Danger: red gradient
- All: border-radius 10px, hover brightness increase

### Input
- Background: `rgba(255,255,255,0.04)`
- Border: `rgba(255,255,255,0.1)`
- Focus: brand border + subtle glow
- Border-radius: 10px

### Tags
- Platform tags: each platform color with low-opacity gradient bg, border-radius 8px
- Status tags: color-coded (success green, danger red, info blue)

### Empty State
- Custom SVG illustration (not Element Plus default)
- Brand gradient icon + description + action button

### Numbers/Badges
- Large numbers use gradient text via `background-clip: text`

## 4. Page Designs

### 4.1 Dashboard

**Structure (top to bottom):**

1. **Page title:** "仪表盘" + subtitle "数据概览与快捷操作"
2. **4 stat cards row** (equal-width grid):
   - Account count (purple gradient) — shows normal/abnormal
   - Connected platforms (blue gradient) — shows platform tags
   - Material count (cyan gradient) — shows video/image/other
   - Today's publishes (green gradient) — shows success rate
3. **Quick actions row** (4 columns):
   - Quick publish, Upload material, View tasks, Account management
   - Each: gradient icon + title + description, hover float-up
4. **Recent materials table:**
   - Title row "最近素材" + "查看全部" link
   - Columns: filename, size, type tag, upload time
   - Max 5 rows

### 4.2 Account Management

1. **Title:** "账号管理" + "管理所有平台账号"
2. **Toolbar:**
   - Left: Platform filter tags (All/Douyin/Kuaishou/Channels/XHS) with custom gradient tag style
   - Right: Search input + Refresh button + "Add Account" primary button
3. **Account table:**
   - Columns: Avatar (gradient circle), Name, Platform tag, Status tag, Actions
   - Status: Normal (green), Abnormal (red, clickable to re-login), Verifying (blue + loading)
   - Actions: Edit, Download Cookie, Upload Cookie, Delete
4. **Add/Edit dialog:**
   - Platform selector: card-style picker (not dropdown)
   - Name input
   - QR code area: dark bg + white QR code with gradient border
   - Status animation: loading → QR code → success/failure

### 4.3 Material Management

1. **Title:** "素材管理" + "上传和管理视频素材"
2. **Toolbar:** Search + Upload button + Refresh
3. **Material table:**
   - Columns: Thumbnail (gradient placeholder for video/image), Filename, Size, Upload time, Actions
   - Actions: Preview, Delete
4. **Upload dialog:**
   - Drag zone with dashed gradient border
   - Upload list with gradient progress bars
5. **Preview dialog:**
   - Centered video playback / image display on dark background
   - Gradient border decoration

### 4.4 Publish Center

**Major restructure — two-column layout:**

1. **Tab bar (top):**
   - Custom tab component, active tab uses gradient background
   - Right side: Add Tab + Batch Publish buttons
2. **Two-column form layout:**
   - **Left column (60%):**
     - Video upload area: drag upload + select from material library
     - Uploaded file list (thumbnail + name + size + delete)
     - Title input (textarea)
     - Topic tags area (selected tags + add button)
   - **Right column (40%):**
     - Platform selection (card-style radio, each platform a card with brand color)
     - Account selection (click to open selector)
     - Original declaration toggle
     - Scheduled publish toggle (expand to show config)
     - Action buttons (Cancel + Publish)
3. **Material library dialog:** Grid layout with multi-select
4. **Batch publish progress dialog:** Gradient progress bar + result list

### 4.5 Task Center (NEW)

**API:** `GET /api/v2/tasks`, `POST /api/v2/tasks/:id/cancel`, `POST /api/v2/tasks/:id/retry`, `GET /api/v2/tasks/stream` (SSE)

1. **Title:** "任务中心" + "查看和管理发布任务"
2. **Toolbar:**
   - Left: Status filter tags (All/Queued/Publishing/Success/Failed)
   - Right: Search + Refresh
3. **Task table:**
   - Columns: Task ID, Platform tag, Account, Title, Status tag, Created time, Actions
   - Real-time status updates via SSE
   - Status colors: Queued (blue), Publishing (purple + pulse animation), Success (green), Failed (red)
   - Actions: Retry/Cancel for failed, Cancel for in-progress
4. **Queue status bar:**
   - Shows: Active workers / Waiting tasks
   - Small tag style display

### 4.6 Publish History (NEW)

**API:** `GET /api/v2/history`, `GET /api/v2/stats`

1. **Title:** "发布历史" + "回顾所有发布记录"
2. **Stats row (3 cards):** Total publishes, Success rate, This month (each with gradient theme)
3. **Filter toolbar:**
   - Left: Time range selector (Today/7d/30d/Custom), Platform filter, Status filter
   - Right: Export button (placeholder), Refresh
4. **History table:**
   - Columns: Platform tag, Account, Title, Status, Publish time, Duration
   - Pagination support
   - Success rows: left green border; Failed rows: left red border
5. **Row expand detail:**
   - Video title, description, tags
   - Error message (for failed)
   - Publish URL (clickable for success)

### 4.7 Settings (NEW)

**API:** `GET /api/v2/settings`, `PUT /api/v2/settings`

1. **Title:** "系统设置" + "配置应用偏好"
2. **Settings sections (card groups):**

   **General settings card:**
   - Backend address (API Base URL)
   - Max concurrent tasks
   - Default retry count

   **Publish settings card:**
   - Default platform
   - Default original declaration toggle
   - WeChat Channels default draft toggle

   **Account settings card:**
   - Cookie expiration warning days
   - Auto-verify account status toggle

   **About card:**
   - Version number
   - Tech stack info
   - Supported platforms list

3. Each setting item: label left + control right (input/switch/select)
4. Save button at bottom (brand gradient)

## 5. Implementation Order

1. **Phase 1 — Foundation:** SCSS variables, global component overrides, Element Plus theme customization
2. **Phase 2 — Shell:** App.vue layout with icon rail navigation + header
3. **Phase 3 — Redesign existing:** Dashboard → Account Management → Material Management → Publish Center
4. **Phase 4 — New pages:** Task Center → Publish History → Settings
5. **Phase 5 — Polish:** Animations, transitions, empty states, responsive checks

## 6. Constraints

- **Framework:** Vue 3 + Element Plus + Vite (no change)
- **Dark only:** No light/dark toggle, dark theme only
- **Desktop-first:** Minimum 1024px width, no mobile responsive required
- **No external fonts:** Use system font stack for performance
- **No emoji icons:** All icons from Element Plus Icons or inline SVG
- **API compatibility:** All pages connect to existing backend APIs, no backend changes
