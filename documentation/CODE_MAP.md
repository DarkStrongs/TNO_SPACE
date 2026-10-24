# TNO_SPACE 代码地图

手动改代码之前先看这一页：每个系统写在哪个文件、数据怎么流动、「新增一个 X」要改哪几处。
每个 scripted_effects 文件开头都有目录，文件内部按「# ===== N. 段名 =====」分段。

> 约定（r98 起）：不再做老存档兼容。所有数组在开新局时一次建全长，没有「按长度补项」「flag 只跑一次」这类迁移代码。改完数据请开新档测试。

---

## 1. 文件一览

### common/scripted_effects（9 个文件）

| 文件 | 内容 |
|---|---|
| `NSP_core_effects.txt` | 开新局 `NSP_init`、**静态数据表 `NSP_data_*`（全部数值）**、每日 / 每周结算、预算拨款、通用工具 |
| `NSP_ui_effects.txt` | 主窗开关、页面切换、主页显示、任务规划器（选择 + `NSP_recalc_planner` 数值重算）、帮助层 |
| `NSP_mission_effects.txt` | 任务生命周期、结果事件队列、计划与目标、历史档案、卫星、宇航员与乘组、局长特质 |
| `NSP_rd_effects.txt` | 研发树数据表、研发页操作、每日推进、解锁重算、科技效果、太空科技等级 |
| `NSP_launchpad_effects.txt` | 地图发射台脚本实体、发射镜头 |
| `NSP_api_effects.txt` | **事件接口 `NSP_ev_*`**（文件末尾，见 EVENT_API.md）、子模组注册 API + **本体规则表 `NSP_api_base_tables`**（载人、载荷 × 目的地许可、目的地属性、火箭发射限制）+ 钩子分发 |
| `NSP_ext_slot_1..3_effects.txt` | 子模组扩展槽空壳（子模组整文件覆盖） |

### 图像（gfx/interface/NSP，r98b 起按界面区域分）

| 文件夹 | 内容 | sprite 定义 |
|---|---|---|
| `shared/` | 几个界面共用：窗口框、面板框、卡片框、滚动底、返回按钮 | NSP_space.gfx |
| `home/` | 主页右上 i / × 按钮、创建任务 / 研发按钮、主窗页签 | NSP_space.gfx |
| `home/programs/` | 左栏「进行中的计划」：计划页签、目标进度条、预算条与小图标；`badges/` 计划徽章 | NSP_space.gfx |
| `home/solar_system/` | 中栏地图：`bodies/` 行星、太阳、月球、背景、云；`orbits/` 轨道线段；`satellites/` 卫星轨道、标记与 +/- 按钮；`hitmasks/` 点击遮罩；`earth_map/` 地球平面图、发射场 / 测控站标记；`controls/` 视图页签、轨道目标行 | NSP_space.gfx / NSP_style.gfx |
| `home/mission_control/` | 右栏任务控制：任务卡、进度条、任务图标、本国 / 历史页签 | NSP_space.gfx / NSP_style.gfx |
| `home/tech/` | 左下太空科技条、等级圆圈 | NSP_style.gfx |
| `home/director/` | 右下局长面板：头像、框、公众支持度条 | NSP_space.gfx / NSP_style.gfx |
| `planner/` | 任务规划器：`selection/` 载荷 / 火箭图、左右箭头、段号、列表行；`destination/` 轨迹图；`modifiers/` 修正框、槽、图标；`stats/` 性能 / 可靠性 / 成本框；`timeline/` 时间线；根目录放「启动任务」按钮 | NSP_space.gfx / NSP_style.gfx |
| `rd/` | 研发页：`tree/` 网格、分类页签；`cards/` 卡片底、框、选中、进度、状态；`links/` 连线；`drawer/` 详情抽屉与队列；`tech/` 大卡卡面（每项一张）；`small/` 小科技方卡 | NSP_rd.gfx |
| `crew/`（`faces/`） | 乘组选拔窗口、宇航员头像 | NSP_crew.gfx |
| `help/` | 帮助层 | NSP_help.gfx |

新加图片：放进它所在界面区域的文件夹，在对应 .gfx 里写 `texturefile = "gfx/interface/NSP/<区域>/<文件>.dds"`。文件名、sprite 名都不带轮次号。

### common/scripted_guis（按窗口分，文件名数字 = 注册顺序）

引擎按文件名排序创建 scripted gui。外壳 `NSP_home_window` 在 00 号文件里，必须最先创建，用 `parent_window_name` 挂外壳的页面才挂得上；帮助层（08）、乘组窗口（09）最后创建，叠在最上面。新加窗口按这个规则选编号。

| 文件 | scripted gui | 窗口 |
|---|---|---|
| `NSP_00_home_guis.txt` | `NSP_topbar`、`NSP_home_frame`、`NSP_home` | 顶栏按钮、外壳、主页 |
| `NSP_01_planner_guis.txt` | `NSP_planner` | 任务规划器 |
| `NSP_02_focus_guis.txt` | `NSP_focus_fx`、`NSP_focus_in`、`NSP_focus_out` | 太阳系行星聚焦动画 |
| `NSP_03_rd_guis.txt` | `NSP_rd`、`NSP_rd_pop` | 研发页、研发详情弹窗 |
| `NSP_08_help_guis.txt` | `NSP_help` | 帮助层 |
| `NSP_09_crew_guis.txt` | `NSP_crew` | 乘组选拔（顶层窗口） |

每个 gui 的 effects / triggers / properties 内部按界面区域分段（`# ---- 区域 ----`）。太阳系轨道命中块（每颗行星的轨道切成几十个小方块按钮，共约 2200 项）放在各段最后，每项一行：点击统一调 `NSP_focus_planet`（`nsp_fp` = 1 水星 … 8 海王星），可见统一调 `NSP_ss_hit_visible`。

### 其他目录

| 位置 | 内容 |
|---|---|
| `common/on_actions/NSP_space_on_actions.txt` | on_startup → `NSP_init`；on_daily → `NSP_daily_tick`；on_weekly → `NSP_weekly_tick` |
| `common/scripted_triggers/NSP_triggers.txt` | 全部条件判断，按 数据表 / 发射场 / 目的地 / 修正 / 规划器 / 主页 / 研发 分段；被调用的写在前面 |
| `common/scripted_localisation/` | defined_text：`NSP_space_*`（主页、规划器、条件提示、动画）、`NSP_rd_*`、`NSP_bodies_*`（行星 tooltip）、`NSP_crew_*`（头像）、`NSP_help_*` |
| `events/NSP_space_events.txt` | nsp.* 事件（任务结果、乘组选拔、计划开放等） |
| `interface/*.gui`、`interface/*.gfx` | 界面布局 / 贴图定义：`NSP_space`（主窗 + 规划器）、`NSP_focus`（聚焦动画）、`NSP_rd`、`NSP_help`、`NSP_crew`；`NSP_style.gfx` 由生成脚本重写 |
| `localisation/simp_chinese/` | 本地化（目前只有简体中文），4 个文件不变，文件内按功能 / 区域排序：`NSP_space`（通用 → 主页：左栏、地图、Mission Control、底栏 → 规划器：栏目、载荷、发射场与目的地、火箭、修正、概要、时间线、性能可靠性成本、启动、启动条件 → 乘组窗口 → 事件：按编号，再是选项提示、事件接口提示 → 人物：局长、宇航员姓名与肖像、座位称谓 → 调试）/ `NSP_rd`（研发树 → 卡片与弹窗 → 研发项目按 id → 卡片图 → 调试按钮）/ `NSP_bodies`（天体与卫星提示 → 调试）/ `NSP_help`。新键插到对应段落，不追加到末尾；排序脚本 `work/loc/reorg.py` |

---

## 2. 数据流

```
开新局 on_startup
  └ NSP_init
      ├ 全局变量（预算 / 太空科技 / 支持度 …）
      ├ NSP_data_payloads / vehicles / destinations / modifiers / programs   ← 所有数值
      ├ 阶段天数、gridbox 下标列表、卫星、宇航员名册、历史档案
      ├ NSP_rd_init → NSP_tier_refresh → NSP_rd_init_unlocks → NSP_rd_start_1962 → NSP_rd_apply_unlocks
      └ NSP_reset_planner → NSP_recalc_home

每天 on_daily → NSP_daily_tick
  ├ NSP_rd_daily（研发进度、完成 → NSP_rd_on_complete → 一次性奖励 + NSP_rd_apply_unlocks）
  ├ 每个进行中的任务 NSP_advance_mission（阶段推进、发射结算、结果入事件队列）
  ├ 发射台实体 / 发射场标记 / 计划日期事件 / 事件队列弹出 / 扩展槽 on_daily
  ├ NSP_budget_peak_update（预算峰值，无条件）
  └ NSP_tick_refresh_ui（主页可见才 NSP_recalc_home；其他页 / 乘组窗只 dirty +1；全关不刷）

每周 on_weekly → NSP_weekly_tick
  └ NSP_econ_weekly（支持度回归）→ NSP_budget_weekly（拨款累计，每 26 周发一次）

GUI 点击 → ui / rd / mission 里的效果 → NSP_recalc_planner / NSP_recalc_home，NSP_dirty + 1
```

`NSP_rd_apply_unlocks` 是「从完成状态从头重算」：先清零解锁表，再按每个已完成研发的 uk/uv 表叠加，最后调各个 `NSP_unlock_*` 和子模组注册。可以随时重复调用。

---

## 3. 下标表（本体）

| 种类 | 数组前缀 | 下标 |
|---|---|---|
| 载荷 | `NSP_pl_*` | 0 双子星 · 1 阿波罗 · 2 TIROS · 3 水手号 · 4 水星 · 5 Syncom · 6 雨云号 · 7 勘测者号 · 8 天空实验室 · 9 试验性载荷 · 10 科研卫星 · 11 月球轨道器 |
| 火箭 | `NSP_ve_*` | 0 泰坦 IIIC · 1 泰坦 II GLV · 2 土星 IB · 3 土星五号 · 4 红石 · 5 宇宙神 LV-3B · 6 宇宙神-阿金纳 · 7 宇宙神-半人马 · 8 试验性火箭 |
| 目的地 | `NSP_dest_*` | 0 近地 · 1 交会 · 2 地球静止 · 3 极地 · 4 地月转移 · 5 逃逸 · 6 中地球 · 7 月球轨道（显示顺序见 `NSP_dest_ids`） |
| 发射场 | `NSP_site_*` | 0 CCAFS · 1 VAFB · 2 WFF · 3 PMRF · 4 WSMR · 5 KSC · 6 约翰斯顿 · 7 波克平原 |
| 修正 | `NSP_mod_*` | 0..7 基础，8..19 由科技解锁（名字见 `NSP_data_modifiers` 行尾注释） |
| 研发 | `NSP_rd_*` | 0..94，87 = 空格占位 `NSP_rd_blank` |
| 子模组 | — | 载荷 / 火箭 50 起 · 目的地 16..31 · 研发 200 起（见 SUBMOD_API.md） |

载人载荷：0 / 1 / 4 / 8（`NSP_api_base_tables` 里登记，代码只查 `NSP_pl_crewed`）。

---

## 4. 「新增 X」清单

### 新增载荷（下标 = 现有数量，即 12）
1. `NSP_core_effects.txt` → `NSP_data_payloads` 表尾加一行（质量 / 成本 / 可靠性 / 下一任务编号 / 图标帧）。
2. `NSP_api_effects.txt` → `NSP_api_base_tables`：载人登记、可去的目的地（`NSP_reg_allow`）；`end = 12` 的循环上限 +1，`NSP_pd_ok` 的 384（= 载荷数 × 32）同步加。
3. 解锁：在 `NSP_rd_effects.txt` → `NSP_unlock_payloads_vehicles` 加一行「研发 X 完成 → `NSP_pl_unl^新下标 = 1`」；或者在 `NSP_rd_init_unlocks` 里把某研发的 uk/uv 设成 `1 / 新下标`。
4. 解锁表长度：`NSP_rd_init_unlocks` 里 `NSP_pl_unl` 的 `end = 12` +1。
5. 贴图：gfx 的 `noOfFrames` +1，美术脚本追加一帧。
6. 本地化：`NSP_PL_NAME_` / `TYPE_` / `SHORT_` / `PLBADGE_` + 解锁文案。

### 新增火箭
1. `NSP_data_vehicles` 表尾加一行。
2. `NSP_rd_init_unlocks` 里 `NSP_ve_unl` 的 `end = 9` +1；`NSP_api_base_tables` 火箭限制循环 `end = 9` +1（如需限制发射场 / 发射台，加一行 `NSP_reg_vehicle_limits`）。
3. 解锁写进 `NSP_unlock_payloads_vehicles`。
4. 贴图帧 + 本地化 `NSP_VE_NAME_` / `TYPE_`。

### 新增目的地
1. `NSP_data_destinations`：`NSP_dest_dv` 加一行，并把下标插进 `NSP_dest_ids` 的显示顺序。
2. `NSP_rd_init_unlocks` 里 `NSP_dest_unl` 的 `end = 8` +1。
3. `NSP_api_base_tables`：目的地属性一行（经验 / 天体 / 视图 / 行），以及哪些载荷能去（`NSP_reg_allow`）。
4. 解锁（研发 uk = 3 或写进 `NSP_unlock_science_orbits` 那样的专门函数）+ 本地化 `NSP_DEST_`。

### 新增修正
1. `NSP_data_modifiers` 加一行，`for_loop ... end = 20` 改成新数量；`NSP_rd_init_unlocks` 里 `NSP_mod_unl` 的 `end = 20` 同步。
2. 适用条件：trigger `NSP_mod_fits`。
3. 解锁：`NSP_unlock_modifiers` 加一行。
4. 图标帧（发射类橙框、载荷类紫框）+ 本地化 `NSP_MOD_NAME_` / `NSP_MOD_INTRO_`。

### 新增研发项目（id = 95 起顺延，或走子模组 200 起）
1. `NSP_rd_init`：在 88..94 那段后面照格式加一行（分类 / 列 / 行 / 前置 / 成本 / 工期 / 太空科技 / 卡面 / 状态 …），再写格位 `NSP_rd_index^(分类×40 + 行×8 + 列)`；把 `NSP_rd_count` 改成新数量。
2. `NSP_rd_init_unlocks`：加一行 uk1/uv1/uk2/uv2（kind 表见该段注释）。`NSP_rd_apply_unlocks` 第一个循环的 `end = 95` 同步。
3. 有专门效果的写进第 3 段 `NSP_unlock_*` 或第 4 段 `NSP_rdfx_*`。
4. 卡面单张图 + 本地化（名称 / 描述 / `NSP_RD_UNLOCK_<id>`）；新行要改 rowlab 可见性 trigger。

### 新增发射场
1. `NSP_init` 的 `NSP_site_ids`（`end = 8`）+1；`NSP_unlock_sites` 加解锁行。
2. 纬度修正：`NSP_site_req_dv`。
3. 地图发射台：`NSP_launchpad_effects.txt` 照抄一组 `NSP_pe_set_<k>`，在 `NSP_pad_update` 加一行 `NSP_pe_eval`。
4. 本地化 + 规划器发射场图标帧。

### 新增计划
1. `NSP_data_programs`：`NSP_prog_unlocked` 的 `end = 7` +1，再加两行目标（所需次数 / 已完成次数）。
2. 开放方式：日期事件写在 `NSP_programs_date_check`，进度判定写在 `NSP_programs_objectives`。
3. 计划图标帧 + 本地化。

---

## 5. r98 改名对照（旧名 → 新名）

DEVLOG 里的旧记录还用旧名，查的时候对照这里。

| 旧名 | 新名 |
|---|---|
| `NSP_rd_apply_r51` | `NSP_unlock_payloads_vehicles` |
| `NSP_rd_apply_r53` | `NSP_unlock_sites` |
| `NSP_rd_apply_r57` | `NSP_unlock_modifiers` |
| `NSP_planner_r92b` | `NSP_unlock_defaults` |
| `NSP_rd_apply_r93` | `NSP_unlock_science_orbits` |
| `NSP_rd_r52_dv` / `_req` / `_rel` / `_cost` / `_success` | `NSP_rdfx_dv` / `NSP_rdfx_req_dv` / `NSP_rdfx_rel` / `NSP_rdfx_cost` / `NSP_rdfx_success` |
| `NSP_rd_r77_rel` / `_cost` / `_success` | `NSP_rdfx_suit_rel` / `NSP_rdfx_suit_cost` / `NSP_rdfx_suit_success` |
| `NSP_site_req_r53` | `NSP_site_req_dv` |
| `NSP_mod_drop_unfit_r57` | `NSP_mod_drop_unfit` |
| `NSP_planner_tables_r51` / `_r93`、`NSP_rd_patch_r53` / `_r56` / `_r57` / `_r93`、`NSP_programs_extend` | 删除，数据并入 `NSP_data_*` 和 `NSP_rd_init` / `NSP_rd_init_unlocks` |
| `NSP_clear_missions`、`NSP_pad_remove_old_buildings` | 删除（只为老存档服务） |

旧文件 → 新文件：`NSP_space_effects` 拆成 `NSP_core_effects` + `NSP_ui_effects`（任务流程移到 `NSP_mission_effects`）；`NSP_rd_content_effects` 并入 `NSP_rd_effects`。
