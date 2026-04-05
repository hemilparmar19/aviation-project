# Aviation HUD UI Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the UI to an aviation cockpit/HUD theme with radar-green accents, instrument-panel aesthetics, and enhance Dynamic Analysis to generate full dashboards from uploaded CSVs.

**Architecture:** CSS-first approach - rewrite the theme layer, update chart colors, then propagate HUD-styled HTML components across all pages. Dynamic Analysis gets a complete rewrite with tabbed dashboard generation matching the main dashboard's capabilities.

**Tech Stack:** Streamlit, Plotly, CSS3 (animations, backdrop-filter, keyframes), Python

---

## File Map

- **Modify:** `assets/style.css` — Complete HUD theme rewrite
- **Modify:** `utils/charts.py` — Update THEME dict + chart styling to HUD green
- **Modify:** `app.py` — Fix home page redirect + HUD sidebar branding
- **Modify:** `pages/1_Home.py` — HUD-styled hero, KPIs, nav cards, sidebar
- **Modify:** `pages/2_Dashboard.py` — HUD header/sidebar styling
- **Modify:** `pages/4_Risk_Predictor.py` — HUD header/sidebar/result cards
- **Modify:** `pages/5_Trend_Forecast.py` — HUD header/sidebar styling
- **Modify:** `pages/6_Geographic_Analysis.py` — HUD header/sidebar styling
- **Modify:** `pages/7_Report_Generator.py` — HUD header/sidebar styling
- **Modify:** `pages/8_Dynamic_Analysis.py` — Complete rewrite: full dashboard generation with tabs

---

### Task 1: CSS HUD Theme Rewrite

**Files:**
- Modify: `assets/style.css` (complete rewrite)

- [ ] **Step 1: Rewrite style.css with aviation HUD theme**

Replace entire CSS with cockpit-inspired theme:
- Colors: `#060a0f` bg, `#00ff41` primary (radar green), `#00d4ff` secondary (cyan)
- Corner bracket decorations on panels via `::before`/`::after` pseudo-elements
- Scanline animation overlay on cards
- Monospace font (`'Share Tech Mono'`) for data values
- Pulsing glow effects on critical metrics
- Instrument panel borders with green glow
- HUD-style section headers with horizontal lines
- Cockpit warning light colors for severity indicators

- [ ] **Step 2: Commit**

---

### Task 2: Charts Theme Update

**Files:**
- Modify: `utils/charts.py:1-17` (THEME dict)
- Modify: `utils/charts.py:19-35` (apply_dark_theme function)

- [ ] **Step 1: Update THEME dict and apply_dark_theme**

Change color palette to HUD green:
- `line`: `#00ff41`, `fill`: `rgba(0,255,65,0.08)`, `accent`: `#00ff41`
- `bg`: `#060a0f`, `card_bg`: `#0a0f14`
- `grid`: `#0d1a0d` (dark green tint)
- `safe`: `#00ff41`, `danger`: `#ff0044`, `warning`: `#ff9500`
- Add cyan `#00d4ff` as secondary color

- [ ] **Step 2: Commit**

---

### Task 3: Fix Home Page Default + App.py HUD Branding

**Files:**
- Modify: `app.py:51` (uncomment switch_page)
- Modify: `app.py:21-48` (sidebar branding to HUD style)

- [ ] **Step 1: Uncomment st.switch_page and update sidebar to HUD style**

- [ ] **Step 2: Commit**

---

### Task 4: Home Page HUD Styling

**Files:**
- Modify: `pages/1_Home.py` (hero, KPIs, insights, nav cards, sidebar)

- [ ] **Step 1: Update Home page with HUD-styled components**

- Hero section with cockpit HUD frame
- KPI cards with corner bracket decoration via CSS classes
- Navigation cards as instrument panels
- HUD-styled sidebar branding
- Scanline section headers

- [ ] **Step 2: Commit**

---

### Task 5: Update All Other Pages (Dashboard, Risk Predictor, Forecast, Geographic, Report)

**Files:**
- Modify: `pages/2_Dashboard.py` — sidebar + header
- Modify: `pages/4_Risk_Predictor.py` — sidebar + header + result cards
- Modify: `pages/5_Trend_Forecast.py` — sidebar + header
- Modify: `pages/6_Geographic_Analysis.py` — sidebar + header + map colors
- Modify: `pages/7_Report_Generator.py` — sidebar + header

- [ ] **Step 1: Update headers and sidebars across all pages to HUD theme**

Each page gets:
- HUD-styled header with `#00ff41` accent
- Updated sidebar branding
- Consistent color references changed from `#4da6ff` to `#00ff41`/`#00d4ff`

- [ ] **Step 2: Commit**

---

### Task 6: Dynamic Analysis Full Dashboard Rewrite

**Files:**
- Modify: `pages/8_Dynamic_Analysis.py` (complete rewrite)

- [ ] **Step 1: Rewrite Dynamic Analysis with full dashboard generation**

When CSV uploaded with matching columns, generate:
- KPI cards (total accidents, fatalities, fatal %, severity breakdown)
- 3-tab dashboard layout:
  - Tab 1: Overview (trend + top countries + aircraft + YOY)
  - Tab 2: Risk & Severity (severity donut + cause analysis + damage breakdown)
  - Tab 3: Data Explorer (filterable table + statistical summary + quality report)
- Monthly heatmap
- All charts reuse HUD theme styling
- Download filtered data option

- [ ] **Step 2: Commit**
