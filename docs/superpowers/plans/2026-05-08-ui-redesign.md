# UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete visual redesign of Social Auto Upload platform — new gradient vibrant dark theme, icon rail navigation, and 3 new fully-functional pages.

**Architecture:** Bottom-up approach — replace design system tokens first, rebuild layout shell (App.vue), then update existing pages and create new ones. All pages connect to existing backend APIs (no backend changes). Vue 3 + Element Plus + SCSS + Pinia stack remains unchanged.

**Tech Stack:** Vue 3 (Composition API), Element Plus, Vite, Pinia, SCSS, vue-router 4

**Spec:** `docs/superpowers/specs/2026-05-08-ui-redesign-design.md`

---

## File Structure

```
frontend/src/
├── styles/
│   ├── variables.scss          # MODIFY — new color tokens, gradients, spacing
│   ├── design-system.scss      # MODIFY — new Element Plus CSS var overrides
│   └── index.scss              # MODIFY — new global component overrides
├── App.vue                     # MODIFY — icon rail navigation + header + breadcrumb
├── router/
│   └── index.js                # MODIFY — add meta (icon, title, breadcrumb)
├── views/
│   ├── Dashboard.vue           # MODIFY — new stat cards, quick actions, table
│   ├── AccountManagement.vue   # MODIFY — new toolbar, table, card-style platform picker
│   ├── MaterialManagement.vue  # MODIFY — new table, upload dialog, preview dialog
│   ├── PublishCenter.vue       # MODIFY — two-column layout, card-style platform radio
│   ├── TaskCenter.vue          # REWRITE — full implementation with SSE
│   ├── PublishHistory.vue      # REWRITE — full implementation with stats + filters
│   └── Settings.vue            # REWRITE — full implementation with grouped settings
└── api/
    └── v2.js                   # NO CHANGE — already has all needed APIs
```

---

## Task 1: Replace Design System Tokens

**Files:**
- Modify: `frontend/src/styles/variables.scss`

Replace all existing variables with the new gradient vibrant dark theme tokens.

- [ ] **Step 1: Replace `variables.scss` with new token system**

The entire file content should be replaced with:

```scss
// ========== Color Palette — Gradient Vibrant Dark ==========

// Brand colors
$brand-start: #8b5cf6;
$brand-end: #3b82f6;

// Accent colors
$accent-cyan: #06b6d4;
$accent-green: #22c55e;
$accent-rose: #f43f5e;
$accent-amber: #f59e0b;

// Status colors
$success-color: #22c55e;
$warning-color: #f59e0b;
$danger-color: #ef4444;
$info-color: #3b82f6;

// Background colors
$bg-base: #0a0a1a;
$bg-elevated: #12122a;
$bg-surface: rgba(255, 255, 255, 0.04);
$bg-overlay: rgba(0, 0, 0, 0.5);

// Text colors
$text-primary: #f1f5f9;
$text-secondary: #94a3b8;
$text-muted: #64748b;
$text-placeholder: #64748b;

// Border colors
$border: rgba(255, 255, 255, 0.08);
$border-light: rgba(255, 255, 255, 0.04);
$border-active: rgba(139, 92, 246, 0.25);

// ========== Gradient Presets ==========
$gradient-brand: linear-gradient(135deg, $brand-start, $brand-end);
$gradient-brand-subtle: linear-gradient(135deg, rgba($brand-start, 0.12), rgba($brand-end, 0.08));
$gradient-success: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(6, 182, 212, 0.1));
$gradient-danger: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(244, 63, 94, 0.1));
$gradient-info: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(139, 92, 246, 0.1));
$gradient-cyan: linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(34, 197, 94, 0.1));

// Stat card gradient themes (for 4 stat cards)
$stat-purple-bg: linear-gradient(135deg, rgba($brand-start, 0.15), rgba($brand-end, 0.1));
$stat-purple-border: rgba($brand-start, 0.2);
$stat-blue-bg: linear-gradient(135deg, rgba($brand-end, 0.15), rgba(6, 182, 212, 0.1));
$stat-blue-border: rgba($brand-end, 0.2);
$stat-cyan-bg: linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(34, 197, 94, 0.1));
$stat-cyan-border: rgba(6, 182, 212, 0.2);
$stat-green-bg: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(234, 179, 8, 0.1));
$stat-green-border: rgba(34, 197, 94, 0.2);

// ========== Platform Colors ==========
$platform-douyin: #f43f5e;
$platform-douyin-bg: rgba(244, 63, 94, 0.15);
$platform-kuaishou: #f59e0b;
$platform-kuaishou-bg: rgba(245, 158, 11, 0.15);
$platform-channels: #3b82f6;
$platform-channels-bg: rgba(59, 130, 246, 0.15);
$platform-xiaohongshu: #8b5cf6;
$platform-xiaohongshu-bg: rgba(139, 92, 246, 0.15);

// ========== Spacing ==========
$spacing-xs: 4px;
$spacing-sm: 8px;
$spacing-md: 16px;
$spacing-lg: 24px;
$spacing-xl: 32px;

// ========== Border Radius ==========
$radius-sm: 8px;
$radius-base: 10px;
$radius-card: 12px;
$radius-lg: 14px;
$radius-dialog: 16px;

// ========== Transitions ==========
$transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
$transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
$transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);

// ========== Z-index ==========
$z-normal: 1;
$z-header: 10;
$z-sidebar: 20;
$z-overlay: 1000;
$z-dialog: 2000;

// ========== Legacy compatibility aliases ==========
// These map old variable names to new ones so existing pages don't break
// during the transition. Remove after all pages are updated.
$primary-color: $brand-start;
$bg-color-page: $bg-base;
$bg-color-overlay: $bg-elevated;
$bg-color-surface: $bg-elevated;
$border-base: $border;
$text-regular: $text-secondary;
```

- [ ] **Step 2: Verify dev server starts without SCSS errors**

Run: `cd /home/czy/workspace/ai/social-auto-upload/frontend && npx vite build --mode development 2>&1 | head -30`
Expected: Build succeeds or only shows warnings about unused variables (no errors)

- [ ] **Step 3: Commit**

```bash
git add frontend/src/styles/variables.scss
git commit -m "refactor: replace design system tokens with gradient vibrant dark theme"
```

---

## Task 2: Update Element Plus CSS Variable Overrides

**Files:**
- Modify: `frontend/src/styles/design-system.scss`

Update `:root` CSS custom properties to match the new color scheme.

- [ ] **Step 1: Replace `design-system.scss` with new overrides**

```scss
:root {
  // Background
  --el-bg-color: #12122a;
  --el-bg-color-page: #0a0a1a;
  --el-bg-color-overlay: #12122a;

  // Text
  --el-text-color-primary: #f1f5f9;
  --el-text-color-regular: #94a3b8;
  --el-text-color-secondary: #94a3b8;
  --el-text-color-placeholder: #64748b;
  --el-text-color-disabled: #475569;

  // Border
  --el-border-color: rgba(255, 255, 255, 0.08);
  --el-border-color-light: rgba(255, 255, 255, 0.06);
  --el-border-color-lighter: rgba(255, 255, 255, 0.04);
  --el-border-color-extra-light: rgba(255, 255, 255, 0.04);

  // Fill
  --el-fill-color: #12122a;
  --el-fill-color-light: rgba(255, 255, 255, 0.06);
  --el-fill-color-lighter: rgba(255, 255, 255, 0.04);
  --el-fill-color-extra-light: rgba(255, 255, 255, 0.03);
  --el-fill-color-dark: #0a0a1a;
  --el-fill-color-darker: #0a0a1a;
  --el-fill-color-blank: #12122a;

  // Primary — use brand purple
  --el-color-primary: #8b5cf6;
  --el-color-primary-light-3: #a78bfa;
  --el-color-primary-light-5: #c4b5fd;
  --el-color-primary-light-7: #ddd6fe;
  --el-color-primary-light-8: #ede9fe;
  --el-color-primary-light-9: #f5f3ff;
  --el-color-primary-dark-2: #7c3aed;

  // Shadow
  --el-box-shadow: 0 0 20px rgba(139, 92, 246, 0.08);
  --el-box-shadow-light: 0 0 12px rgba(139, 92, 246, 0.06);
  --el-box-shadow-lighter: 0 0 6px rgba(139, 92, 246, 0.04);
  --el-box-shadow-dark: 0 0 30px rgba(0, 0, 0, 0.4);

  // Mask
  --el-mask-color: rgba(0, 0, 0, 0.6);
  --el-mask-color-extra-light: rgba(0, 0, 0, 0.3);

  // Radius
  --el-border-radius-base: 10px;
  --el-border-radius-small: 8px;
  --el-border-radius-round: 20px;

  // Font
  --el-font-size-base: 14px;
  --el-font-size-small: 13px;
}
```

- [ ] **Step 2: Verify build**

Run: `cd /home/czy/workspace/ai/social-auto-upload/frontend && npx vite build --mode development 2>&1 | tail -5`

- [ ] **Step 3: Commit**

```bash
git add frontend/src/styles/design-system.scss
git commit -m "refactor: update Element Plus CSS overrides for new theme"
```

---

## Task 3: Update Global Component Overrides

**Files:**
- Modify: `frontend/src/styles/index.scss`

Update all Element Plus component overrides to use new variables and gradient accents.

- [ ] **Step 1: Replace the component overrides section in `index.scss`**

Key changes needed:
- Card: replace `$primary-color` with `$brand-start`, use gradient hover borders
- Button: primary uses gradient background
- Table: use `$brand-start` for hover highlights
- Dialog: use `$bg-elevated` background, gradient border
- Input: use `$border-active` for focus state
- All `$border-base` → `$border`, `$bg-color-surface` → `$bg-elevated`, etc.

The file keeps its imports at top, `body` styles, utility classes. Only the Element Plus override section (lines 26-315) needs updating. Replace with overrides that reference the new variable names.

- [ ] **Step 2: Verify build**

Run: `cd /home/czy/workspace/ai/social-auto-upload/frontend && npx vite build --mode development 2>&1 | tail -5`

- [ ] **Step 3: Commit**

```bash
git add frontend/src/styles/index.scss
git commit -m "refactor: update global component overrides for gradient theme"
```

---

## Task 4: Rebuild App.vue Layout — Icon Rail + Header

**Files:**
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/router/index.js`

Replace the collapsible sidebar with a 64px icon rail, add breadcrumb header.

- [ ] **Step 1: Update router to include meta for icons and breadcrumb labels**

Add `meta` to each route in `router/index.js`:

```js
const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard, meta: { icon: 'HomeFilled', title: '仪表盘', breadcrumb: '仪表盘' } },
  { path: '/account-management', name: 'AccountManagement', component: AccountManagement, meta: { icon: 'User', title: '账号管理', breadcrumb: '账号管理' } },
  { path: '/material-management', name: 'MaterialManagement', component: MaterialManagement, meta: { icon: 'Picture', title: '素材管理', breadcrumb: '素材管理' } },
  { path: '/publish-center', name: 'PublishCenter', component: PublishCenter, meta: { icon: 'Upload', title: '发布中心', breadcrumb: '发布中心' } },
  { path: '/task-center', name: 'TaskCenter', component: TaskCenter, meta: { icon: 'List', title: '任务中心', breadcrumb: '任务中心' } },
  { path: '/publish-history', name: 'PublishHistory', component: PublishHistory, meta: { icon: 'Clock', title: '发布历史', breadcrumb: '发布历史' } },
  { path: '/settings', name: 'Settings', component: Settings, meta: { icon: 'Setting', title: '系统设置', breadcrumb: '系统设置', isBottom: true } }
]
```

- [ ] **Step 2: Rewrite `App.vue` template and script**

Replace the entire `<template>` and `<script setup>` sections with:

**Template:** 64px fixed icon rail on left side, 48px header on top, main content fills remaining space. Icon rail contains: logo circle at top, nav icons in middle (using el-tooltip for labels), separator, settings at bottom. Active icon gets gradient background. Header shows breadcrumb on left, empty user area on right.

**Script:** Uses `useRoute()` to compute active menu. Navigation items defined as array with path/icon/label. Breadcrumb computed from route meta.

- [ ] **Step 3: Rewrite `App.vue` styles**

New SCSS:
- Icon rail: `width: 64px`, `background: rgba(255,255,255,0.03)`, `border-right: 1px solid $border`
- Logo: 36px gradient circle with "S" letter
- Nav icons: 40x40px containers, `border-radius: $radius-base`, active gets `$gradient-brand` background
- Header: 48px height, `background: rgba(255,255,255,0.02)`, `border-bottom: 1px solid $border`
- Main: `background: $bg-base`, `padding: $spacing-lg`
- Page transition: `fade-slide` keyframe

- [ ] **Step 4: Verify in browser**

Run: `cd /home/czy/workspace/ai/social-auto-upload/frontend && npx vite`
Expected: Icon rail appears on left with gradient logo, header shows breadcrumb, pages render (may look broken due to old page styles using old variable names — that's OK, pages get updated in later tasks)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/App.vue frontend/src/router/index.js
git commit -m "feat: icon rail navigation with gradient brand header"
```

---

## Task 5: Redesign Dashboard

**Files:**
- Modify: `frontend/src/views/Dashboard.vue`

Rebuild the dashboard with 4 gradient stat cards, quick actions grid, and styled materials table.

- [ ] **Step 1: Update Dashboard template**

Key changes:
- Page title area: `<h1>仪表盘</h1>` + `<p class="page-subtitle">数据概览与快捷操作</p>`
- 4 stat cards in `el-row` with gradient backgrounds (use CSS classes: `.stat-purple`, `.stat-blue`, `.stat-cyan`, `.stat-green`)
- Each stat card: gradient icon container + number (gradient text via `background-clip`) + label + footer stats
- Add 4th card: "今日发布" with success rate
- Quick actions: 4 cards with hover translateY(-4px), gradient icon containers
- Recent materials table: same columns but wrapped in styled card container

- [ ] **Step 2: Update Dashboard styles**

Replace all SCSS. Use new variable names (`$bg-elevated`, `$border`, `$brand-start`, etc.). Key style additions:
- `.stat-card` with 4 color variants using the `$stat-*-bg` and `$stat-*-border` variables
- `.stat-value` with `background: $gradient-brand; -webkit-background-clip: text; -webkit-text-fill-color: transparent`
- `.action-card` hover with `transform: translateY(-4px)` and gradient border glow
- Table section wrapped in card with `$bg-elevated` background

- [ ] **Step 3: Verify in browser**

Run dev server, navigate to Dashboard. Expected: 4 gradient stat cards with purple/blue/cyan/green themes, quick action cards with hover effect, recent materials table in styled card.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/Dashboard.vue
git commit -m "feat: redesign dashboard with gradient stat cards and quick actions"
```

---

## Task 6: Redesign Account Management

**Files:**
- Modify: `frontend/src/views/AccountManagement.vue`

Update toolbar with gradient filter tags, restyle table, update dialog.

- [ ] **Step 1: Update Account Management template**

Key changes:
- Page title area with subtitle
- Toolbar: replace `el-tabs` with custom gradient filter chips (`<div class="platform-filters">` with clickable chips for each platform)
- Table: add platform-specific gradient tag styles, restyle action buttons
- Dialog: replace platform `el-select` with card-style platform picker (4 cards, each with platform icon and color)

- [ ] **Step 2: Update styles**

Key style additions:
- `.platform-filter` chip: `$border` border, hover shows platform color, active gets platform gradient bg
- Platform tags: each uses its `$platform-*-bg` and color
- QR code container: dark bg + gradient border
- Card-style platform picker: 2x2 grid, each card 120px with platform icon and name

- [ ] **Step 3: Verify in browser**

Expected: Platform filter chips with gradient active states, platform-colored tags in table, card-style platform picker in dialog.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/AccountManagement.vue
git commit -m "feat: redesign account management with gradient platform filters"
```

---

## Task 7: Redesign Material Management

**Files:**
- Modify: `frontend/src/views/MaterialManagement.vue`

Update table with thumbnails, restyle upload dialog with gradient border.

- [ ] **Step 1: Update template and styles**

Key changes:
- Add thumbnail column: for video files show play icon in gradient container, for images show preview
- Upload dialog: dragger area with dashed gradient border (`border-image: $gradient-brand 1`)
- Upload progress: gradient progress bar color
- Preview dialog: video/image centered on dark bg with subtle gradient border
- Replace old variable names throughout

- [ ] **Step 2: Verify and commit**

```bash
git add frontend/src/views/MaterialManagement.vue
git commit -m "feat: redesign material management with gradient upload zone"
```

---

## Task 8: Redesign Publish Center — Two-Column Layout

**Files:**
- Modify: `frontend/src/views/PublishCenter.vue`

Major restructure to two-column form layout with card-style platform selection.

- [ ] **Step 1: Restructure template to two-column layout**

Key changes:
- Tab bar at top (unchanged structure, updated styles)
- Content area split: left 60% / right 40% using CSS grid or flex
- Left column: video upload + file list + title textarea + topic tags
- Right column: platform cards (4 cards in 2x2 grid, each with platform icon/color) + account selector + toggles + buttons
- Material library dialog: grid layout for items
- All dialogs use `$bg-elevated` background

- [ ] **Step 2: Update styles**

Key style additions:
- `.publish-layout`: `display: grid; grid-template-columns: 3fr 2fr; gap: 24px`
- `.platform-card`: 2x2 grid, each card gets platform color on active, `border-radius: $radius-card`
- Upload area with gradient dashed border
- Action buttons: primary with `$gradient-brand` background

- [ ] **Step 3: Verify and commit**

```bash
git add frontend/src/views/PublishCenter.vue
git commit -m "feat: redesign publish center with two-column layout"
```

---

## Task 9: Implement Task Center (NEW)

**Files:**
- Rewrite: `frontend/src/views/TaskCenter.vue`

Full implementation with SSE real-time updates, status filters, and queue status bar.

- [ ] **Step 1: Create TaskCenter.vue with full functionality**

Template structure:
1. Page header with title + subtitle
2. Queue status bar: shows active workers / waiting tasks (fetch from `taskApi.getQueueStatus()`)
3. Toolbar: status filter chips (全部/排队中/发布中/成功/失败) + search + refresh
4. Task table: columns — platform tag, account, title, status tag (with pulse animation for "发布中"), created time, actions (cancel/retry)
5. Pagination (el-pagination)

Script logic:
- On mount: fetch tasks via `taskApi.getTasks()`, start SSE connection via `EventSource('/api/v2/tasks/stream')`
- SSE handler: update task status in real-time, refresh queue status
- Filter: computed property filters by status and search keyword
- Actions: cancel calls `taskApi.cancelTask()`, retry calls `taskApi.retryTask()`
- On unmount: close SSE connection

- [ ] **Step 2: Style with new theme**

Status-specific styles:
- 排队中: blue tag with `$gradient-info` bg
- 发布中: purple tag with `$gradient-brand-subtle` bg + CSS pulse animation
- 成功: green tag with `$gradient-success` bg
- 失败: red tag with `$gradient-danger` bg

- [ ] **Step 3: Verify and commit**

```bash
git add frontend/src/views/TaskCenter.vue
git commit -m "feat: implement task center with SSE real-time updates"
```

---

## Task 10: Implement Publish History (NEW)

**Files:**
- Rewrite: `frontend/src/views/PublishHistory.vue`

Full implementation with stats cards, filters, paginated table, and expandable rows.

- [ ] **Step 1: Create PublishHistory.vue with full functionality**

Template structure:
1. Page header
2. Stats row: 3 gradient stat cards (total publishes, success rate, this month) — data from `statsApi.getStats()`
3. Filter toolbar: time range selector (今天/7天/30天/自定义 date picker), platform filter dropdown, status filter, refresh button
4. History table with columns: platform tag, account, title, status, publish time, duration
5. Row click expands to show detail: description, tags, error message (if failed), publish URL (if success)
6. Pagination

Script logic:
- On mount: fetch history via `historyApi.getHistory()` and stats via `statsApi.getStats()`
- Filters update query params and refetch
- Success rows get left green border via CSS class, failed rows get left red border

- [ ] **Step 2: Verify and commit**

```bash
git add frontend/src/views/PublishHistory.vue
git commit -m "feat: implement publish history with stats and filters"
```

---

## Task 11: Implement Settings (NEW)

**Files:**
- Rewrite: `frontend/src/views/Settings.vue`

Full implementation with grouped settings cards, load/save via API.

- [ ] **Step 1: Create Settings.vue with full functionality**

Template structure:
1. Page header
2. Settings cards (4 groups):
   - General: API base URL input, max concurrent tasks select (1-5), default retry count select (1-5)
   - Publish: default platform select, original declaration switch, draft switch
   - Account: cookie expiration days input, auto-verify switch
   - About: static info card (version, tech stack, platforms)
3. Save button at bottom (gradient primary)

Script logic:
- On mount: fetch settings via `settingsApi.getSettings()`, populate form
- Save: collect form data, call `settingsApi.updateSettings()`, show success message
- About card: hardcoded version and platform info

- [ ] **Step 2: Verify and commit**

```bash
git add frontend/src/views/Settings.vue
git commit -m "feat: implement settings page with grouped configuration"
```

---

## Task 12: Polish — Animations and Final Touches

**Files:**
- Modify: `frontend/src/styles/index.scss` — add keyframe animations
- Modify: `frontend/src/App.vue` — page transition animation

- [ ] **Step 1: Add global animations to `index.scss`**

Add these keyframes:
```scss
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 8px rgba($brand-start, 0.2); }
  50% { box-shadow: 0 0 16px rgba($brand-start, 0.4); }
}

@keyframes fade-slide-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

Add utility classes:
```scss
.animate-pulse { animation: pulse-glow 2s ease-in-out infinite; }
.animate-spin { animation: spin 1s linear infinite; }
.animate-fade-in { animation: fade-slide-in 0.3s ease-out; }
```

- [ ] **Step 2: Add page transition to `App.vue`**

Wrap `<router-view>` with transition:
```html
<router-view v-slot="{ Component }">
  <transition name="fade-slide" mode="out-in">
    <component :is="Component" />
  </transition>
</router-view>
```

Add transition CSS in App.vue styles:
```scss
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 150ms ease, transform 150ms ease;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
```

- [ ] **Step 3: Final visual check — run dev server and browse all pages**

Run: `cd /home/czy/workspace/ai/social-auto-upload/frontend && npx vite`
Check each page for visual consistency:
- Dashboard: 4 gradient stat cards, quick actions, table
- Account Management: gradient filters, platform tags, card picker dialog
- Material Management: gradient upload zone, styled table
- Publish Center: two-column layout, platform cards
- Task Center: SSE status updates, pulse animation
- Publish History: stats cards, color-coded rows
- Settings: grouped cards, gradient save button

- [ ] **Step 4: Commit**

```bash
git add frontend/src/styles/index.scss frontend/src/App.vue
git commit -m "feat: add page transitions and global animations"
```

---

## Spec Coverage Check

| Spec Section | Task | Status |
|---|---|---|
| 1. Design System Tokens | Task 1 | Covered |
| 2. Layout Shell (Icon Rail) | Task 4 | Covered |
| 3. Component Library (overrides) | Task 2, 3 | Covered |
| 4.1 Dashboard | Task 5 | Covered |
| 4.2 Account Management | Task 6 | Covered |
| 4.3 Material Management | Task 7 | Covered |
| 4.4 Publish Center | Task 8 | Covered |
| 4.5 Task Center (NEW) | Task 9 | Covered |
| 4.6 Publish History (NEW) | Task 10 | Covered |
| 4.7 Settings (NEW) | Task 11 | Covered |
| 5. Polish | Task 12 | Covered |
| 6. Constraints (dark only, no external fonts, desktop-first) | All tasks | Enforced |

All spec requirements are covered by tasks. No placeholders. No TBDs.
