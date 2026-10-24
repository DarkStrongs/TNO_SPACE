# TNO_SPACE（NSP 国家太空计划）开发日志

> 规则：每次开发都在这里追加一条，最新的在最上面。
> 格式：日期（Asia/Shanghai）· 轮次 · 改了什么（文件）· 为什么 · 已知问题 / 待测项。

---

## 2026-10-24 · r99k · 滚动列表滚轮修复 + 修正列表隐形滚动条
- 原因：用户反馈很多滚动列表滚轮滑不动；修正列表的滚动条压住右列图标。
- 查明：NSP_mc_box / NSP_site_box / NSP_dest_box / NSP_palette_box / NSP_tl_scroll 的 background 用 GFX_NSP_scroll_bg（8×8 普通 spriteType）。普通 sprite 当背景只按原尺寸画、接不到鼠标（DEVLOG r16 研发树已踩过），滚轮事件进不来；能滚的研发树用的是原版 GFX_tiled_window_transparent + margin。用户参考 DS 也记了同样规则（背景不能 alwaystransparent、margin 要写）。
- interface/NSP_space.gui：五个滚动容器背景改 quadTextureSprite = GFX_tiled_window_transparent，补 margin 全 0；新增 NSP_hidden_slider（宽 1，全部子元素透明 + alwaystransparent），修正列表 NSP_palette_box 改用它。
- interface/NSP_space.gfx：删 GFX_NSP_scroll_bg，新增 GFX_NSP_scroll_clear（同一张 nsp_scroll_bg.dds 做九宫格）。
- 待测：Mission Control、出发地、目的地、修正列表、时间线五处鼠标停在条目上滚轮能滚；修正列表看不到滚动条、右列图标能点、滚轮能滚到底；其他滚动条外观不变。若隐形滚动条导致滚轮失效，退回 NSP_right_slider 并改走「只列可装修正」方案。

## 2026-10-24 · r99j · 研发槽条改 7 格
- 原因：底部研发槽条只有 3 个固定格，研发槽上限会涨到 7（初始 3 + 科技第 4/7/10 级 + 载人航天中心），多出的研发不显示。
- interface/NSP_rd.gui：NSP_rd_qstrip 高 36 → 48（y 646 → 636），树区高 548 → 538；7 格 NSP_rd_q_cell/name/bar/pct_0..6，每格 126×40，上行名称、下行进度条 + 百分比。
- interface/NSP_rd.gfx：新增 GFX_NSP_rd_qslot（3 帧：空闲 / 研发中 / 未解锁斜线底纹 + 锁头）、GFX_NSP_rd_qbar_s（72×6，11 帧）；删除 GFX_NSP_rd_qbar 及 nsp_rd_qbar.dds（只有这里用）。图由 tools/gen_rd_qslot.py 生成。
- NSP_rd_effects.txt（NSP_rd_recalc 队列段）：NSP_rd_q_shown = 研发槽上限 + 还没拿到的来源数（最多 7）；NSP_rd_q_lksrc 按顺序列出未拿到的来源（1004/1007/1010 = 科技等级，其余 = 带研发槽奖励的研发 id），分给未解锁格的 NSP_rd_q_lk0..6；格子帧 NSP_rd_q_cf0..6。
- NSP_03_rd_guis.txt：格子 / 名称按 NSP_rd_q_shown 显示，进度条 / 百分比按 NSP_rd_q_n 显示。
- 本地化 NSP_rd：NSP_RD_Q_*_0..6、NSP_RD_Q_IDLE（空闲）、NSP_RD_Q_LOCK_T1004/1007/1010（科技第 N 级解锁）、NSP_RD_Q_LOCK_RD0..6（研发 X）。scripted loc GetNSPRDQ0..6 / GetNSPRDQLk0..6 / GetNSPRDQPct0..6。
- 删了文件：解压前先删旧文件夹。
- 待测：开局 3 格空闲 + 4 格锁定（科技第 4/7/10 级、研发 载人航天中心）；开始研发后格子变亮、进度条走；升到第 4 级后第 4 格变空闲；研发满 3 个后无法再开始（原规则不变）；锁定格文字是否被截断。

## 2026-10-24 · r99i · 审查事件接口提示
- 逐个核对 NSP_ev_* 的提示条件和实际效果（NSP_api_effects.txt）。
- NSP_ev_add_tech：ev_val ≤ 0 时实际不加经验，但提示仍显示「+0」→ 提示加条件 ev_val > 0。
- NSP_ev_mission_return_rel：无人任务也显示「返程可靠性 ±」→ 只对载人任务显示。新增任务数组 NSP_m_crewed（NSP_crew_pad 补齐、开始任务时写 NSP_pl_crewed^p、NSP_hist_archive_init 清空）。
- 已确认无问题：经费 / 支持度 / 研发 / 成功率 / 下一次任务 的正负分色和条件；NSP_ev_finish 清 ev_val 不影响已生成的提示（r99g 截图里显示的是调用时的值）。
- 未改（提示显示的是请求值，不是实际值）：支持度、成功率被 0..100 截断；提前天数被「最少剩 1 天」截断；下一次成本被 -90% 截断；研发进度加到 100 会直接完成但提示只写 +X%。
- EVENT_API：返程可靠性一行注明无人任务无效。
- 待测：新档开一个无人任务和一个载人任务，nsp_dbg.4 选项 d 只在载人任务时显示「返程可靠性 -100%」；nsp_dbg.2 太空科技经验正常。

## 2026-10-24 · r99h · 事件描述 §F 刷屏报错
- error.log：bitmapfont.cpp「Could not find coloring for character 'F'」每帧刷屏。事件描述用的字体没有定义 §F（TNO 的 §F 只在部分字体的 textcolors 里），tooltip 字体有。
- NSP_space_l_simp_chinese.yml：NSP_DBG_READOUT（调试事件描述）去掉全部 §F…§!，标签用默认色。
- 规则：事件 desc / 选项名不用 §F；§F 只用于 tooltip 和本 mod 自己的 GUI。
- 待测：打开 nsp_dbg.* 时 error.log 不再刷这条。

## 2026-10-24 · r99h · 事件选项「当前阶段提前 30 天」没有提示
- 现象：nsp_dbg.4 选项 c 悬停只有「触发事件」，没有「本次任务当前阶段：提前 30 天」。
- 推断原因（未实机确认是哪一个，两处都改了）：
  1. NSP_ev_newest_mission 在选项里跑 for_each_loop 求 ev_mid，tooltip 生成时可能没执行 → ev_mid 不对 → 提示条件不满足。
  2. NSP_ev_mission_delay / NSP_ev_next_cost 开头在 if 块里算绝对值 ev_abs。
- NSP_api_effects.txt：NSP_ev_newest_mission 改为直接读 NSP_newest_mid；新增 NSP_newest_mid_update（循环求最大任务 id）。ev_abs 改为无条件 = -ev_val，只给负数分支用。
- 调用 NSP_newest_mid_update：NSP_init（置 -1）、开始任务（add_to_array NSP_missions 之后）、每日结算删除已结束任务之后。
- 本地化：NSP_EV_TT_MDAY_P、NSP_EV_TT_NCOST_P 改读 ev_val。EVENT_API 已注明。
- 待测：新开档开一个任务 → nsp_dbg.4 四个选项都有提示；「推迟 14 天」显示红色「推迟 14 天」；nsp_dbg.5 下一次任务成本正负显示正确。旧档里 NSP_newest_mid 不存在，要开新档或先开一次任务。

## 2026-10-24 · r99g · 事件研发进度为负时显示「+-30%」
- 原因：NSP_ev_rd_progress 只有一条 tooltip NSP_EV_TT_RD_PROG，写死「§G+」，负值显示成绿色「+-30%」。
- NSP_api_effects.txt：按 ev_val 正负选 NSP_EV_TT_RD_PROG_P / _N（同其他 NSP_ev_* 接口）。
- 本地化：NSP_EV_TT_RD_PROG 拆成 _P（§G+）/ _N（§R，数值自带负号）。
- 待测：nsp_dbg.3 「进度 -30%」显示红色「-30%」，「+50%」显示绿色「+50%」。

## 2026-10-24 · r99f · 每日 / 每周结算只在窗口打开时刷新界面
- 原因：NSP_daily_tick / NSP_weekly_tick 无条件调 NSP_recalc_home（末尾 NSP_dirty +1），窗口关着也每天重算主页并让所有 scripted_gui 重评。
- NSP_ui_effects.txt：新增 NSP_tick_refresh_ui —— 主页可见（home_open 且不在规划器 / 研发页）才 NSP_recalc_home；规划器 / 研发页 / 乘组窗口开着只 dirty +1（与原行为一致）；都关着什么都不做。打开窗口时 NSP_toggle_home 本来就会重算。
- 预算历史峰值 NSP_budget_peak 是游戏状态，原来夹在 recalc_home 里：抽成 NSP_budget_peak_update，recalc_home 和每日 / 每周结算都无条件调用。
- NSP_core_effects.txt：daily / weekly tick 末尾改为 NSP_budget_peak_update + NSP_tick_refresh_ui。
- NSP_mission_effects.txt：NSP_crew_paused_refresh 的 dirty 只在主窗或乘组窗口开着时加；看门狗「队首任务没了，关窗」处补一次 dirty（原来靠 paused_refresh 那一下关窗）。
- 待测：窗口关着跑几周后打开，预算条 / 目标进度 / 任务卡正确；主页开着时每日任务进度照常动；研发页开着研发进度照常动；乘组窗口在主窗关着时能正常弹出和关闭；五倍速对比卡顿。

## 2026-10-24 · r99e · 火箭 / 载荷决定修正槽位数
- 用户要求：不同火箭、载荷的修正槽位数不同，越先进越多，初始试验型没有槽位。
- NSP_core_effects.txt：NSP_data_vehicles 新增 NSP_ve_lslots（发射类槽位），NSP_data_payloads 新增 NSP_pl_pslots（载荷类槽位）。
  - 火箭：试验性 0、红石 1、宇宙神 LV-3B 1、泰坦 II GLV 2、宇宙神-阿金纳 2、宇宙神-半人马 2、泰坦 IIIC 3、土星 IB 3、土星五号 4。
  - 载荷：试验性 0、TIROS 1、水星 1、Syncom 1、科研卫星 1、水手号 2、雨云号 2、勘测者号 2、月球轨道器 2、双子星 3、阿波罗 4、天空实验室 4。
- NSP_ui_effects.txt：NSP_recalc_planner 先算 NSP_calc_lslots / NSP_calc_pslots，新增 NSP_mod_drop_overflow（换成槽位更少的火箭 / 载荷时，按修正编号保留、超出的卸下）；算 NSP_calc_lused / pused 和 8 个槽位框帧 NSP_f_lslot_k / NSP_f_pslot_k（1 可用 / 3 锁定）。
- NSP_triggers.txt：NSP_can_add_mod 上限从写死 4 改为当前槽位数。scripted loc GetNSPPalHead 分发射类 / 载荷类两条「已满」提示。
- NSP_01_planner_guis.txt：properties 绑定 NSP_lslot_0..3 / NSP_pslot_0..3 的 frame。
- 美术：nsp_modifier_slot_launch.dds、nsp_modifier_slot.dds 加第 3 帧「锁定」（边框压暗 + 斜线），noOfFrames 2 → 3，去掉无用的 buttonstate effectFile（只用作 iconType）。
- 本地化：栏目标题显示「已用 / 上限」；NSP_TT_SLOTS_FULL 拆成 NSP_TT_LSLOTS_FULL / NSP_TT_PSLOTS_FULL；NSP_COND_MOD_FULL 拆成 _L / _P。
- API：NSP_reg_payload / NSP_reg_vehicle 新增可选 reg_slots（0 = 默认 2，-1 = 无）；新增 NSP_reg_payload_slots / NSP_reg_vehicle_slots。SUBMOD_API 已更新。
- 待测：开局试验性组合两栏都显示 0/0、4 格全锁、修正点不了且提示正确；换到土星五号 + 阿波罗出现 4/4 格；从 3 个修正的火箭换到 1 槽火箭时自动卸下多余修正；锁定帧显示正常（iconType frame 由 properties 驱动）。

## 2026-10-24 · r99d · 规划器「任务成功后」改为实际奖励
- 原因：用户反馈规划器显示「+200 科学 目标 +1 +50 声望」与游戏实际效果不符。这行是写死的旧文案；NSP_science / NSP_reputation 只写不读，玩家看不到也不起作用。实际成功奖励是 nsp.1：支持度 +3、太空科技经验（NSP_dest_xp[目的地]，载人 +3）、符合条件的计划目标 +1，阿波罗地月转移另有研发加成。
- common/scripted_effects/NSP_ui_effects.txt：NSP_recalc_planner 末尾新增 NSP_calc_win_pop / NSP_calc_win_xp（照搬 nsp.1、NSP_tier_mission_xp、NSP_rdfx_success / NSP_rdfx_suit_success 的算法）。
- localisation NSP_SUCCESS_LINE 改为「支持度 +X   科技经验 +Y」。目标进度只对特定载荷 / 目的地组合生效，一行放不下，没写进去；子模组 NSP_hook_on_success 的额外奖励也预览不到。
- 待测：切换目的地 / 载荷时数字变化；阿波罗 + 地月转移且完成 19/20/76 号研发时支持度显示 +10；结束任务后实际加的支持度和经验与预览一致；文字不超出 246 宽。

## 2026-10-24 · r99c · 本地化文件内按功能 / 区域排序
- 用户要求：本地化内容按功能与区域（GUI、事件、人物）重新排序，不拆文件。
- 4 个 yml 文件名不变，每个键仍在原文件里；文件内按 通用 → 主页 → 规划器 → 乘组窗口 → 事件 → 人物 → 调试 分大段、再分小段（见 CODE_MAP）。旧轮次注释换成段落标题。研发项目按 id 把名称 / 描述 / 解锁 / 前置排在一起，事件按编号排。
- 只移动行：每个文件的键值行与 r99b 逐行比对完全相同（space 893、rd 609、bodies 64、help 28），无重复键。
- 脚本 work/loc/reorg.py（备份 work/loc/bak_r99b）。
- 待测：游戏内无缺失本地化。文件名没变，直接覆盖即可。

## 2026-10-24 · r99b · 事件接口 NSP_ev_*
- 用户要求：写新事件时，效果直接在选项里配置，不用改其他文件。
- `common/scripted_effects/NSP_api_effects.txt` 末尾新增事件接口（参数用临时变量 ev_val / ev_id / ev_mid，自带选项提示，实际改动在 hidden_effect）：
  - 国家：`NSP_ev_add_budget`（B）、`NSP_ev_add_popularity`、`NSP_ev_add_tech`
  - 研发：`NSP_ev_complete_rd`、`NSP_ev_rd_progress`
  - 任务：`NSP_ev_this_mission` / `NSP_ev_newest_mission` 选任务，`NSP_ev_mission_rel`、`NSP_ev_mission_return_rel`、`NSP_ev_mission_delay`
  - 下一次任务：`NSP_ev_next_rel`、`NSP_ev_next_cost`（NSP_recalc_planner 计入，NSP_start_mission 清零；可靠性 / 成本提示里显示「事件」一项）
- 本地化 NSP_EV_TT_* / NSP_BD_REL_EV_* / NSP_BD_CP_EV_*（NSP_space_l_simp_chinese.yml 末尾），defined_text GetNSPEvRDName / GetNSPBD_rel_ev / GetNSPBD_cp_ev。
- 文档 documentation/EVENT_API.md；示例子模组 documentation/examples/NSP_event_api_example/（3 个事件 + 调试决议）。
- 提示只在效果会生效时显示（任务 / 研发状态不满足时不显示）。
- 调试事件 events/NSP_debug_events.txt（命名空间 nsp_dbg，菜单 + 国家 / 研发 / 任务 / 下一次任务 4 页，描述显示读数，选项执行后重弹同一事件）；入口调试决议 NSP_dbg_event_api；读数效果 NSP_ev_dbg_readout（NSP_api_effects.txt 末尾）。
- 待测：选项提示里 [?ev_val] 等临时变量能否显示正确数值、GetNSPEvRDName 能否显示研发名；已掷骰任务改成功率后发射动画与结局一致；下一次任务加成在规划器里显示、启动后清零。

## 2026-10-24 · r99 · 结构与可读性整理（不改行为）
- scripted_guis 按窗口拆成 6 个文件，文件名用数字标注册顺序：`NSP_00_home_guis` / `01_planner` / `02_focus` / `03_rd` / `08_help` / `09_crew`（原 `NSP_space_guis`、`NSP_space_rd_guis`、`NSP_zz_help_guis`、`NSP_zzz_crew_guis`）。注册顺序与 r98c 完全相同。
- 主页、聚焦窗的 effects / triggers / properties 按界面区域分段；约 2200 个轨道命中块（点击 1380 项、可见 814 项）移到各段末尾，每项改成一行调用：点击 → 新效果 `NSP_focus_planet`（`nsp_fp` 传行星），可见 → 新触发器 `NSP_ss_hit_visible`。内容与原来逐字等价。
- scripted_triggers 合并为 `NSP_triggers.txt`，加目录，按 数据表 / 发射场 / 目的地 / 修正 / 规划器 / 主页 / 研发 分段，被调用的判断排在前面。旧文件头里过时的下标表删掉，改指向 CODE_MAP 第 3 节。
- 改名：`interface/NSP_focus_v22.gui` → `NSP_focus.gui`；`NSP_crew_face_sl.txt` → `NSP_crew_scripted_loc.txt`；`NSP_help_sl.txt` → `NSP_help_scripted_loc.txt`。work/r69/gen.py 输出路径同步改。
- 注释清理：去掉 effects / guis / gui / 事件 / 本地化脚本注释里的轮次、版本号（r31、v22 等），删掉「@ retired」注释掉的旧代码（时代框、旧任务卡、旧研发抽屉、预渲染连线、座位条）。
- 校验（work/r99/verify_all.py）：除新增的 1 个效果、1 个触发器外，所有脚本文件去掉注释后的 token 与 r98c 完全一致；scripted gui 逐项比对 2691 项一致，注册顺序一致；无未定义调用；花括号平衡。
- ⚠ 改名 / 删文件：解压前先删掉旧 TNO_SPACE 文件夹，否则旧的 NSP_space_guis.txt 等会和新文件重复定义。
- 待测：与 r98c 相同；另外点太阳系行星 / 轨道能否聚焦、退出动画后再点能否重新聚焦。

## 2026-10-24 · r98c · 修复 r98 数据表为空
- 用户截图：试验性载荷 / 火箭质量、成本、可靠性全是 0，任务名「Explorer 0」，实际 Delta-V 0。
- 原因：r98 生成 NSP_data_payloads / NSP_data_vehicles / NSP_data_modifiers 时脚本 bug（zip 迭代器被读了两次），三张表只剩注释、没有数值行，数组全空。目的地和计划表不受影响。
- 修复：从 r95y 原值重新生成三张表（载荷 12 行、火箭 9 行、修正 20 行），数值与 r95y 一致。另外逐个数组比对了 r95y 与 r98 的初始化条数，其余差异都来自删掉的补丁 / 补齐循环，已核对无缺。
- 追加审计（用户要求「再看看有没有严重漏洞」）：逐个函数对比 r95y 与 r98c 的有效代码差异（18 个改动函数、9 个删除函数），确认删除的只是补丁 / 补齐逻辑，新开局初始化结果一致；所有 `= yes` 调用都有定义；sprite 无重名、引用都有定义；贴图路径都存在；BOM 正确；本地化无重复 key。未发现其他严重问题。
- 要测：开新档，规划器里载荷 / 火箭数值、余量、可靠性、成本正常；任务名序号正常；修正图标点上去有效果。

---

## 2026-10-24 · r98b · 图像文件夹按界面区域重新划分
- 用户要求：图像文件夹按功能区域划分。
- gfx/interface/NSP 下的 3d / style / common / map / mission / badges / portraits 七个文件夹取消，按界面区域重分为 shared / home（programs、solar_system、mission_control、tech、director）/ planner（selection、destination、modifiers、stats、timeline）/ rd（tree、cards、links、drawer、tech、small）/ crew / help。148 个文件移动，详细对照见 work/r98b/mapping.json；目录说明见 CODE_MAP.md。
- 去掉文件名和 sprite 名里的轮次号（11 个：GFX_NSP_dir_frame_r33 → GFX_NSP_dir_frame、GFX_NSP_rd_sdiv_r34 → GFX_NSP_rd_sdiv 等），.gfx / .gui 同步改。
- 删除未被任何 sprite 引用的 common/nsp_tab_mc.dds（Mission Control 页签用的是 style 那张，已移到 home/mission_control/）。
- 所有 .gfx 的 texturefile 路径已逐个核对存在（只剩 3 条已注释掉的旧 sprite）；tools/ 里的生成脚本输出路径同步改。
- 要测：主页、规划器、研发页、乘组窗口、帮助层的贴图全部正常（error.log 里查 texture not found）。解压前先删旧 TNO_SPACE 文件夹。

---

## 2026-10-24 · r98 · 代码整理：去掉补丁层和老存档迁移（基于 r95y）
- 用户要求：代码到处是补丁，难读；手动改要轻松；不再维护老存档。
- scripted_effects 重新分文件（仍为 9 个）：core / ui / mission / rd / launchpad / api / ext_slot_1..3。每个文件开头有目录，按「# ===== N. 段名 =====」分段。删除 NSP_space_effects、NSP_rd_content_effects。
- 新增 documentation/CODE_MAP.md：文件一览、数据流、下标表、「新增 X 要改哪里」清单、改名对照表。
- 数值集中：新增 NSP_data_payloads / vehicles / destinations / modifiers / programs（在 NSP_core_effects），载荷 12、火箭 9、目的地 8、修正 20、计划目标 14 全在一张表里；原来 NSP_init + r51 / r57 / r92b / r93 补项拆成的五处合并。
- 研发：88..94 直接写进 NSP_rd_init / NSP_rd_init_unlocks，NSP_rd_count 开局即 95；1962 开局完成项（含 88 / 89 / 91）合并进 NSP_rd_start_1962，由 NSP_init 调用一次。
- 改名（按功能命名，不再带轮次号）：见 CODE_MAP.md §5。
- 删除老存档维护：
  - NSP_rd_patch_r53 / r56 / r57 / r93、NSP_planner_tables_r51 / r93、NSP_programs_extend、NSP_clear_missions、NSP_pad_remove_old_buildings；
  - 旗标 NSP_rd_ready / NSP_rd_v2 / NSP_rd_v3 / NSP_m_v2 / NSP_tier_v2 / NSP_r85_start / NSP_r56_sites / NSP_pad_entity_r94f 及其判断；
  - 每日结算里的补丁调用、NSP_sat_sync、NSP_programs_extend、载荷属性表长度检查；
  - 发射台旧建筑：common/buildings/NSP_launchpad_buildings.txt、gfx/entities/NSP_launchpad_sites.asset、map/buildings.txt、NSP_launchpad.asset 里的 building_NSP_pad_* entity、对应本地化 key。
- 注释：去掉「rNN 手加」「重新生成本文件时必须保留」「原 xxx.txt」等历史标记，文案里的「民意 / 国会支持」改为「支持度」。轮次细节以本 DEVLOG 为准。
- 保留：on_daily 里「装 mod 前开的档首次初始化」那道闸门（中途装 mod 用）；任务数组按任务 id 补齐（新任务要用）。
- 校验：所有 `NSP_xxx = yes` 调用都有定义；花括号平衡；无 >= / <= 的 check_variable；yml 带 BOM。
- 风险 / 要测（必须开新档）：
  - 研发树 0..94 全部显示，88 / 89 / 91 及 1962 开局科技为已完成，KSC 等发射场解锁正常；
  - 规划器能切到全部 12 种载荷、9 种火箭，试验性载荷 / 火箭开局可用，修正 20 个；
  - 计划页签 7 个，双子星 / 阿波罗按日期开放；
  - 卫星 tooltip：每日不再刷新 NSP_sat_sync，切视图、任务成功时会刷新，看是否有过期显示；
  - 地图发射台实体正常，error.log 无旧建筑相关报错。
- 旧版备份：work/archive/mod_before_r98/

---

## 2026-10-24 · r95y · 修正件 tooltip 加延迟第二层介绍
- NSP_palette_icon、NSP_slot_icon 加 pdx_tooltip_delayed = "NSP_MOD_TT_D"，内容来自 GetNSPModIntro（新增）。
- 20 个修正件的介绍写在 NSP_MOD_INTRO_0..19，全文 §g 灰字。
- 新增修正件时，要同时补 NSP_MOD_INTRO_<id>。
- 要测：在调色板和已装配的槽位上悬停，延迟后应出现介绍。

---

## 2026-10-24 · r95x · 规划面板 性能 / 可靠性 / 成本 tooltip 列出全部加成
- 用户要求：这三块的 tooltip 像原版稳定度那样，把每一项加成都列出来。
- NSP_recalc（NSP_space_effects.txt）在各计算步骤之间存快照 NSP_bd_*，用差值得出每类加成。另在 NSP_rd_r52_rel / NSP_rd_r52_cost（NSP_rd_content_effects.txt）里、局长特质之前各补一个快照（NSP_bd_p1/v1、NSP_bd_c1）。计算结果没有改动。
- 性能：
  - 实际 = 火箭方程（含载荷质量）+ 改装件 + 研发项目。
  - 需求 = 目的地 + 发射场纬度 + 研发项目。
  - 余量。
- 可靠性：载荷和火箭各自列出：
  - 基础值，以及按 75% 计算后扣掉的部分。
  - 改装件、研发被动加成、太空科技等级（仅火箭）、研发项目、局长特质。
  - 加成合计为正时减半的部分。
  - 最后是总计 = 载荷 × 火箭。
- 成本：
  - 载荷 / 火箭 / 改装件按「原型 × NSP_cost_mult ÷ 1000」折成 B。
  - 修正按连乘百分比列出：发射场、研发项目、局长特质、研发成本减免。
  - 最后是预算。
- 每行由 defined_text GetNSPBD_*（scripted loc 末尾）输出：值为 0 不显示，正负分绿红；需求 ΔV 和成本则反过来，增加显示为红。
- 加成按类汇总，不逐个科技列出。可靠性被夹到 0 / 100 时没有单独一行。
- _D 延迟层（公式说明）保留。
- 要测：
  - 换不同的载荷、火箭、发射场、改装件，看各行是否随之出现或消失。
  - 各行相加是否等于面板上的数值。
  - $ 是否正常显示。

---

## 2026-10-24 · r95w · 太空科技 tooltip 精简
- NSP_tech_bar 去掉 pdx_tooltip_delayed（NSP_TECH_TT_D：获取方式和升级规则），NSP_TECH_TT 末尾的「把鼠标移到左右两侧…」提示删除。NSP_TECH_TT_D 键保留但已不再引用。
- 研发槽写进「当前效果」：GetNSPTierSlotsGot 改为恒显示，0 级也会显示「研发槽：+0（第 4 / 7 / 10 级各 +1）」；左侧圆圈的 NSP_TIER_L_TT 同步受影响。
- 要测：鼠标悬停科技条，只出现一层 tooltip，且研发槽一行始终显示。

---

## 2026-10-24 · r95v · 历史 tooltip 乘组名按生死着色
- 新增数组 NSP_m_kia（按任务 id，1 = 乘组遇难）：在 NSP_crew_pad 里补齐，NSP_crew_release 在 nsp_alive = 0 时写 1，和 NSP_m_rrel 在同一处清空。
- GetNSPHCrewA/B/C 按 NSP_m_kia^v 选键：生还显示 §G名§!，遇难显示 §R名（遇难）§!。纯名字改由 GetNSPHCrewNA/B/C 读取。
- 「乘组：」标签改为 §F，和其他行一致。
- 返程失败（nsp.3）是唯一会写入遇难的路径；发射失败靠逃逸生还、在轨失败后平安返回的都按生还显示绿名。
- 要测：成功的载人任务显示绿名；返程失败的显示红名加（遇难）。

---

## 2026-10-24 · r95u · 科技卡面拆成单张（用户：科技不要用帧图）
- 删除了 7 张帧图：nsp_rd_tech_0..5.dds（按分类，每帧 239×117，共 94 帧）和 nsp_rd_small.dds（35 帧 72×72）。备份在 work/r95u/bak。
- 改成一项研发一张图：
  - 大卡：rd/tech/nsp_rdart_<id>.dds，94 张，sprite 为 GFX_NSP_rdart_<id>。
  - 方卡：rd/small/nsp_rdsart_<id>.dds，34 张，sprite 为 GFX_NSP_rdsart_<id>。rd46 从 r93 起是大卡，方卡图不再输出。
  - 图是按 # id 注释里的 (trk, art) 从旧帧图原样裁的；用 gen_rd_small 重跑方卡，结果和裁出来的逐字节一致。
- 元素合并：
  - 卡片上的 NSP_rdc_tech_0..5 合成一个 NSP_rdc_tech，显示条件只剩「非空格且非方卡」。
  - 弹窗里的 NSP_rd_d_tech_0..5 合成一个 NSP_rd_d_tech。
  - NSP_rdc_sart 保留，改为单张图。
- 换图都改成 properties image：
  - [GetNSPRDArt] 读键 NSP_RDART_[?v]
  - [GetNSPRDSArt] 读键 NSP_RDSART_[?v]
  - [GetNSPRDSelArt] 读键 NSP_RDART_[?NSP_rd_sel]
  - 这些键的值是 sprite 名，加在 NSP_rd_l_simp_chinese.yml 末尾。
- NSP_rd_art、NSP_rd_sart、NSP_rd_f_selart 不再用于显示，只保留数据。
- tools/gen_rd_small.py 改成读单张大卡、写单张方卡。
- API：研发卡面改由本地化里的 NSP_RDART_<id> / NSP_RDSART_<id> 指定 sprite，子模组终于能用自己画的卡面了；reg_art 不再影响显示。SUBMOD_API.md 已同步。
- 新增研发卡面的步骤：放 rd/tech/nsp_rdart_<id>.dds，在 NSP_rd.gfx 加一行 sprite，在 loc 加 NSP_RDART_<id>。
- 要测：六个分类的大卡、方卡、点开弹窗时的科技图，都要确认显示的是对应项目的图。

---

## 2026-10-24 · r95t · 乘组头像拆成单张（用户：不要帧图）
- 原来的 32 帧图集 nsp_crew_face.dds（4992×210）已删除。现在每张头像单独一个 156×210 的 dds，放在 gfx/interface/NSP/crew/faces/：
  - nsp_crew_face_empty（空座）
  - nsp_crew_face_na（不适用）
  - nsp_astro_00_shepard … nsp_astro_29_williams（编号 = 宇航员 id，后缀是英文姓）
- sprite 定义（NSP_crew.gfx）：GFX_NSP_crew_face 现在是单张的空座图，同时当元素的基准 sprite；另有 GFX_NSP_crew_face_na 和 GFX_NSP_astro_0..29。
- 换图方式：properties 从 frame = NSP_crew_pf0..2 改成 image = "[GetNSPCrewFace0..2]"，跟 NSP_prog_badge 用 [GetNSPProgramBadge] 是同一种写法。
  - scripted loc 在新文件 common/scripted_localisation/NSP_crew_face_sl.txt，用动态键 NSP_CREW_FACE_[?NSP_crew_pf0]。
  - 键 NSP_CREW_FACE_1..32 的值就是 sprite 名，加在 NSP_space_l_simp_chinese.yml 末尾。
  - NSP_crew_pf 的算法没变：1 空座、2 不适用、宇航员为 id + 3。
- tools/gen_crew_gui.py 改成逐张输出。
- 新增宇航员的步骤：放 tools/crew_portraits_src/k.png，在 SUR 列表里加姓氏，再补 gfx 里的一行 sprite 和 loc 里的 NSP_CREW_FACE_(k+3)。
- 要测：三个座位的头像能不能正确切换，包括空座和不适用。

---

## 2026-10-24 · r95s · 整理 gfx/interface/NSP 根目录（用户：优化文件夹）
- 根目录散放的 37 张 dds 分进四个子文件夹，原有子文件夹（3d / crew / help / planner / portraits / rd / style）不动：
  - badges/：12 张 nsp_badge_*（计划徽章）。
  - mission/：任务控制用的 nsp_mc_bar / nsp_mc_card / nsp_mc_dash / nsp_mc_iconbox，以及 nsp_mission_icons、nsp_obj_bar、nsp_prog_done、nsp_program_tabs、nsp_bar_mission。
  - map/：nsp_map_earth、nsp_map_frame、nsp_lsite_marker、nsp_station_marker。
  - common/：通用框和按钮，即 nsp_window_frame / nsp_panel_frame / nsp_card_frame、nsp_scroll_bg、nsp_button_*、nsp_bar_budget、nsp_small_icons、nsp_tab_bra、nsp_tab_mc。
- texturefile 路径已同步：NSP_space.gfx 和 NSP_style.gfx。
- 生成脚本的输出路径已同步：gen_mc_card / gen_lsite_marker / gen_mission_icons / gen_prog_icons。
- sprite 名一个没改，所以 .gui 和脚本都不用动。lint 结果跟之前一样（texture missing 3 条，都是旧的）。
- 要测：各页的贴图有没有变成粉色或缺图。

---

## 2026-10-24 · r95r · 任务卡图标扩到 12 帧（一种载荷一帧）
- 原问题：nsp_mission_icons.dds 只有 4 帧，第 4 帧是废弃的红星。结果 9 种无人载荷都显示成水星符号 ☿，天空实验室借用了阿波罗图标。
- 新图集 264×22，帧号 = 载荷 id + 1。由 tools/gen_mission_icons.py 生成，旧图备份在 tools/mission_icons_src_r88.dds。
- 双子星、阿波罗、水星三帧照搬旧图。其余九帧是新画的 1px 白描：TIROS 鼓形、水手（帆板加天线盘）、Syncom（鼓加电波）、雨云（双帆板加环）、勘测者三脚架、天空实验室（单翼加风车）、试验性载荷（铅笔星加鞭状天线）、科研卫星（同心环）、月球轨道器（月牙加卫星）。试过加粗到 2px，糊成一团，没用。
- NSP_calc_mission_frames：载荷 0..11 直接用 id + 1 当帧号，12 号以后的扩展载荷仍读 NSP_pl_icon，越界时回退到 11。
- API 的 reg_icon 改成帧号 1..12，默认 11。SUBMOD_API.md 已同步。
- 要测：任务控制和历史卡片上每种载荷的图标是否对应。

---

## 2026-10-24 · r95q · 确定键重做（用户：按钮优化）
- nsp_crew_ok.dds 仍是 572×80、2 帧，去掉了两侧横线和中间的内框。
- 新样式照 EL TAPADO 标题格：直角双线框，两端各一个柱头玫瑰饰（取自 map_bg.dds 456..473,14..31，放大 2 倍），旁边加竖分隔线。
- 第 1 帧（可点）用亮青色 (89,199,194) 加暗青底，第 2 帧（未选满）用暗青灰。
- NSP_crew_ok_label 改到 x = 80、maxWidth = 412，正好在两条分隔线中间。

---

## 2026-10-24 · r95p · 装饰柱改用 TNO 原图 map_bg.dds
- 用户嫌脚本画的柱子难看，发来墨西哥面板原图 map_bg.dds（487×295 的线稿框），放在 tools/crew_frame_src/map_bg.dds。
- tools/gen_crew_gui.py 从原图截左右两条柱：x 0..49 和 437..486。飘带的绿色 (36,95,61) 改成蓝色 (44,66,138)，配星条旗；红白不动。
- 柱身轮廓里填窗口底色，因为原图中间是透明的，直接压在地图上看不清。最后用最近邻放大 2 倍，得到 100×590。
- 柱子放在 x = -100 和 1060、y = 10，贴在窗口左右外侧。
- 手画柱子的旧代码已作废，备份在 work/r95e/gen_pillar_r95o_retired.py。

---

## 2026-10-24 · r95o · 装饰柱飘带重画，取消卡牌区水印
- 用户发来预览截图（柱子 / 卡牌区）。原因：飘带是抗锯齿的细线，背面那段压在柱身上又暗又糊，尾巴也乱；卡牌区水印被不透明的卡挡住，只露出零碎的线。
- 飘带改为逐列像素绘制，每圈依次是描边、红 2、白 2、蓝 2、描边，从左上斜到右下，两侧折边压暗。背面一段被柱子挡住不画，末端从右侧垂下一条尖口尾巴。
- 卡牌区水印已注释掉，九宫格保留。

---

## 2026-10-24 · r95n · 卡牌区和卡框照 El Tapado 原文件
- 卡牌区（nsp_crew_bg.dds 16..588,214..488）照 el_tapado_background：分成三段，每段是九宫格青线，段与段之间用双线隔开。
- 每段底下有一枚淡色线稿水印，依次是 NASA 徽标、火箭、月球轨道。卡是不透明的，所以水印只从卡的边缘露出来。
- 卡框从圆角改为直角双线框，照 El Tapado 的肖像框，红 / 青两帧的含义不变。
- 版式和坐标都没动，.gui 没有改。预览脚本放在 work/r95e/preview_crew.py。

---

## 2026-10-24 · r95m · 空座头像改为 El Tapado 风格线稿
- 照用户给的 TNO 原文件 El_Tapado_portrait(_tes_nation).dds：主体是 1px 青色线稿，不抗锯齿，只有少量重点上色（原文件里是国旗绶带）。
- nsp_crew_face.dds 第 1 帧（空座）改画成「空头盔宇航服」：面罩里没有脸，对应 El Tapado 的无头西装；左肩是星条旗臂章，右胸是 NASA 徽标，底衬暗格线（照 el_tapado_background 的九宫格）。
- 尺寸仍是 156×210，其他帧不变。生成位置在 tools/gen_crew_gui.py 的 r95m 段。

---

## 2026-10-24 · r95l · 乘组窗口两侧加装饰柱（学习 TNO 墨西哥面板）
- 版式保持 r95h 不动，只在两侧加了 iconType NSP_crew_pillar_l / _r。柱子是像素风石柱，缠一条星条旗红白蓝的螺旋飘带，末端向外飘。
- 柱子尺寸 72×650，放在 x = -60 和 x = 1048、y = -20，伸出窗口外，所以窗口加了 clipping = no。
- 贴图由 tools/gen_crew_gui.py 的 pillar() 生成：先画 36×325，再最近邻放大成 nsp_crew_pillar(_r).dds。
- 待测：clipping = no 后伸出窗口的部分能不能显示；柱子要设 alwaystransparent，不能挡住窗口拖动。

---

## 2026-10-24 · r95k · 乘组窗口回退到 r95h 版式（用户：r95i / r95j 都不如 r95h）
- interface/NSP_crew.gui、生成器 tools/gen_crew_gui.py 和 crew 的 loc 都退回 r95h 原样，贴图用 r95h 生成器重新生成。
- NSP_crew.gfx 保留 r95i 的修复：r95h 原包里这个文件是空的，现在 7 条 spriteType 都在。
- 已经撤掉的：Situations 风格（r95i，备份 work/r95e/gen_crew_gui_r95i.py）、统一版式（r95j）、i 信息格和 NSP_CREW_HELP_TT。
- ⚠ 风格偏好：用户嫌杂糅多套参考的 Situations 风格难看，以后在 r95h（New Mission Concept 风格）上做小改，别整体换风格。

---

## 2026-10-24 · r95j · 乘组窗口统一版式（用户嫌 r95i 风格杂、难看）
- 配色和元素只按三条规则走：
  - 结构（面板、标签条）一律用青色细线。
  - 可点的东西（列表行、卡、确定键）一律是暗底细框加角括号，照 Situations 列表按钮。
  - 红色加斜纹只表示「还需要你处理」，也就是空座和没选满时的确定键。
- 去掉的东西：轨道水印、任务名旁边的两个装饰斜纹格、假滚动条、切角框、暖色照片。头像改回中性灰。
- 两栏标签条对齐在 70..94：左边是任务名加「飞行乘组」，右边是「待命宇航员」加人数。
- 左面板 102..508，卡 y = 183；确定键缩到 572×80，放在 y = 518；网格从 610,110 起，槽 216×32，行 212×26。
- r95i 的生成器备份在 work/r95e/gen_crew_gui_r95i.py。

---

## 2026-10-24 · r95i · 乘组窗口改为 TNO Situations / 危机面板风格
- 生成器 tools/gen_crew_gui.py 整个重写，旧版备份在 work/r95e/gen_crew_gui_r95h.py。
- 标题栏：虚线双框，左边是头盔图标格，右边是 i 信息格（NSP_crew_info，悬停显示 NSP_CREW_HELP_TT 操作说明）加圆和三角装饰。
- 左栏：任务名放在切角框里，旁边两个红斜纹装饰格；「飞行乘组」做成标签条；卡牌区底下有轨道徽记水印；确定键 572×120，选满时是浅色双切角框（照 OUTCOMES），没选满时是红框加红斜纹、红字（照 EFFECTS）。
- 卡片：切角卡框，红色 = 空座 / 不适用，浅色 = 已选。空座照片窗是红斜纹加剪影，不适用是暗斜纹。头像改成暖灰双色调（照危机配图），贴图仍是 156×210。
- 右栏：两个标签格（「待命宇航员」，以及红斜纹格里的「N 人待命」）；左侧加了装饰滚动条；列表行是 206×26 的浅色切角框，姓名居中、白字，飞行次数在右侧小方格里。
- 卡片姓名和任务名去掉了颜色码，改成默认白字。
- ⚠ 修复：r95h 包里的 interface/NSP_crew.gfx 被误清空，所有 GFX_NSP_crew_* 都未定义，窗口会缺图。这一版已恢复，r95h 作废。
- 待测：虚线标题栏的观感、i 的 tooltip、确定键两种状态。

---

## 2026-10-23 · r95h · 头像显示缩小，贴图仍保持原版 156×210
- 头像改为 iconType NSP_crew_face_0..2，用 scale = 0.75 显示成 117×158。贴图 nsp_crew_face.dds 没动，仍是原版头像尺寸 156×210，以后可以直接换原版人像。
- 卡框缩到 133×244，整张卡就是按钮 NSP_crew_seat_0..2（frame = NSP_crew_cf），点击撤下这个人。头像叠在卡上，设了 alwaystransparent。
- 窗口压到 1060×610：卡牌区 214..488，确定键 y=498；列表行改为 210×26，槽 214×28。
- 待测：iconType 的 scale 显示是否正常，卡片点击撤下是否生效。

---

## 2026-10-23 · r95g · 删除乘组窗口里的「任务倒计时：暂停」文字
- 按用户要求删掉 NSP_crew_status 文本框（loc 键还在，没有地方引用）。任务名在框里垂直居中，y=95。
- 倒计时暂停的逻辑没动，Mission Control 卡片上仍然显示红色「暂停」。

---

## 2026-10-23 · r95f · 乘组窗口改为 TNO New Mission Concept 面板风格
- 顶部加了全宽标题栏「选拔飞行乘组」（NSP_CREW_HEAD）。
- 左栏：任务框里是青色任务名，下面一行红色暂停；然后是分区头「1 飞行乘组」（左侧数字格）、卡牌区，底部是 START MISSION 式的大确定键（572×80，外双框 + 两侧横线 + 中央内框，选满显示绿色，未选满显示灰色）。确定键文字用 GetNSPCrewOkT 随状态变色。
- 右栏：分区头「2 待命宇航员」，下面是 FROM 式药丸分隔，里面写待命人数；列表行 210×28，左侧方格是飞行次数（§D），右侧是白字姓名，网格槽 214×31。
- 去掉了斜纹底。卡牌逻辑和帧绑定都没变。
- 待测：标题栏和分区数字的字体、确定键颜色切换、列表 30 人是否放得下。

---

## 2026-10-23 · r95e · 删除座位分段条和经验加成区（用户要求）
- B 区只保留任务名。分段条 NSP_crew_bar、计数文字 NSP_crew_count、整个 D 区经验加成框（NSP_crew_bonus / _d）都删掉了。
- GFX_NSP_crew_bar 已注释为 retired，dds 移到 work/r95e/quarantine。生成器里也注释掉，不再输出这个文件。
- 窗口改为 1060×650：C 卡牌区 172..546，卡牌 y=216，确定键 y=560，右侧面板 80..631（够放 30 人 / 15 行）。
- 经验加成的逻辑没动（NSP_crew_add_bonus 照常生效），只是界面上不再显示。

---

## 2026-10-23 · r95d · 乘组区改成 TNO 卡牌样式（参考五月风暴小游戏）
- 每个座位是一张 172×312 的卡（GFX_NSP_crew_card，2 帧）：红框表示空座或该座位不适用，青框表示已选人。帧号绑在 NSP_crew_cf0..2，在 NSP_crew_gui_build 里计算。
- 卡的结构从上到下：顶栏是飞行次数（NSP_crew_fl0..2 → GetNSPCrewFlT），中间是黑白头像（156×210，自动对比度），名字栏是黄字姓名，底栏是职位加座位号。
- 乘组区底纹改为青色斜纹（烘进 bg）。窗口改为 1060×760；加成区和确定键下移。
- 待测：卡框颜色、飞行次数显示、头像帧。

---

## 2026-10-23 · 第 95c 轮 · 乘组选拔窗口显示宇航员头像
- 乘组区改为 3 张原版尺寸头像（156×210），可以点头像把人撤下。精灵是 GFX_NSP_crew_face，共 32 帧：1 = 空座（青色剪影），2 = 不适用，3 起依次对应宇航员 0..29。
- 帧号 NSP_crew_pf0..2 在 NSP_crew_gui_build 里计算。
- 头像来源：维基百科上的 NASA 官方照（公有领域），裁成 156×210，原图存在 tools/crew_portraits_src/k.png。
- 窗口改为 1060×720，左格加宽。职位和姓名分两行显示：职位在 GetNSPCrewRoleT0..2，姓名在 GetNSPCrewSeat0..2。
- 待测：头像帧是否对应正确，点头像能否撤下，有没有 error.log 报错。

---

## 2026-10-23 · 第 95b 轮 · 乘组选拔窗口改为 TNO 最高法院面板版式
- 用户给的参考图是 TNO 的最高法院面板，按它改了外观：亮青双线框，左右两大格，左格分成状态 / 任务 / 乘组 / 加成四个区。待命列表是黄字行，右侧方块里显示飞行次数。座位用红 / 绿分段条表示。
- 窗口 920×660，所有框线都烘在底图 nsp_crew_bg.dds 里。贴图由 tools/gen_crew_gui.py 生成，改坐标时要同步改这个脚本。
- 新增元素：
  - NSP_crew_status（任务倒计时：§R暂停§!）
  - NSP_crew_bar（9 帧，NSP_crew_bar_frame 在 NSP_crew_gui_build 里算）
  - NSP_crew_seat_0..2_t（座位行文字）
  - NSP_crew_office、NSP_crew_bonus
- 座位数不足时，多出来的座位行显示「不适用」，不再隐藏。座位行文字由 GetNSPCrewSeat0..2 生成。
- 已删除旧 key：NSP_CREW_SUB / INFO / NAME_x / ROLE_x / EMPTY，以及 nsp_crew_line.dds。
- 待测：
  - 底图有没有拉伸或错位。
  - 分段条的帧对不对。
  - 中文在 aldrich_32 / 28 下是否正常显示。
  - 网格是否 2 列 × 15 行、能放下全部宇航员。

---

## 2026-10-23 · 第 95 轮 · 乘组选拔改为独立 GUI（取代事件 nsp.40 / nsp.41）
- 用户要求：选乘组不再用事件，改成一个独立的 GUI。原来弹事件的地方改为弹这个窗口。窗口没有退出键，只有「确定」。选完之前，任务倒计时显示红色的「暂停」。
- 新文件：
  - `interface/NSP_crew.gui`：顶层窗口 NSP_crew_window，760×520，居中，可拖动。左栏是座位 0..2、加成说明和确定键，右栏是待命宇航员网格（2 列，196×28）。
  - `interface/NSP_crew.gfx` 和 `gfx/interface/NSP/crew/*.dds`：贴图由 tools/gen_crew_gui.py 生成，可以重跑。
  - `common/scripted_guis/NSP_zzz_crew_guis.txt`：没有 parent，所以太空计划面板关着也会弹出来。
- `NSP_mission_effects.txt`：
  - NSP_crew_fire 不再弹事件，改为 NSP_crew_gui_open。窗口已经开着时不会重置已选的人。
  - 新增 NSP_crew_gui_build / _pick / _add_bonus / _open / _confirm / _confirm_ai，以及 NSP_crew_paused_refresh。
  - 点待命宇航员 = 填进第一个空座位；点座位 = 撤下。
  - 需要人数 = min(座位数, 已上座 + 待命)。人数够了确定键才可点（frame 1 / 2 + click_enabled）。
  - 确定后一次性调用 NSP_crew_assign_do 上座，然后处理队列里的下一个任务。
  - AI 不开窗口，按顺序自动填满。
  - 看门狗：队列里有任务但窗口没开（旧存档）时直接打开。
- 暂停：
  - NSP_advance_mission 开头：任务在 NSP_crew_queue 里、并且处于阶段 4 时，phase_left / total_left 先加 1 再扣 1，等于暂停。
  - 卡片 NSP_ME_ETA 改为读 GetNSPMEEta，按 NSP_m_paused^v 显示 NSP_ME_ETA_P1「预计完成：§R暂停§!」或原文。
  - NSP_m_paused 由 NSP_crew_paused_refresh 维护，队列变化时和每日都会调用。
- 事件 nsp.40 / nsp.41 的定义和本地化保留，只是不再触发。
- 待测：
  - 载人任务进入乘组阶段时弹出窗口，没有关闭键，按 ESC 也关不掉。
  - 点人上座、点座位撤下、选满后确定键亮起。
  - 选拔期间 Mission Control 卡片显示红色「暂停」，天数不变；确定后恢复倒计时。
  - 两个载人任务同时排队时，确定后马上换成下一个任务。
  - error.log 里有没有 NSP_crew_* 相关报错。

---

## 2026-10-23 · 第 94m 轮 · 删除按天数倒数
- 用户要求删除 r94k 的按天数倒数。`common/scripted_effects/NSP_launchpad_effects.txt` 恢复到 r94j 的版本：去掉 NSP_pe_hold 数组和状态 5 的分支，min_zoom = 3000 保留。
- 播完切回空台现在只靠 r94l 的 next_state = "empty"。

---

## 2026-10-23 · 第 94l 轮 · 动画播完立刻切回空台
- 用户要求：动画一播完，马上切成空台状态，不要按游戏天数等。
- `gfx/entities/NSP_launchpad.asset`：NSP_launchpad_entity 的 launch、fail_pad、fail_air 三个 state 加了 `next_state = "empty"`。先例是 MD units_vehicles.asset，它在 looping = no 的 state 上用 next_state 接下一个状态。这样动画按真实时间播完后由引擎自动切换，跟游戏速度无关；keep_particle 的尾迹、烟雾照常留着。
- r94k 的 NSP_pe_hold 留作保底：如果 set_entity_animation 绕过 state、next_state 不生效，30 天后脚本会再切一次空台（原来是 7 天）。
- 待测：发射动画播完后，台子会不会立刻回到空台，有没有闪烁或消失。

---

## 2026-10-23 · 第 94k 轮 · 任务结束后发射台消失
- 用户反馈：任务结束后，地图上的发射台不见了。
- 原因（推断）：create_entity 创建的实体在 looping = no 的动画（launch / fail_pad / fail_air）播完后会被引擎移除。r94f 为了不截断 93 秒的发射动画，选择一直停在末帧，结果末帧之后实体就没了。
- 修复：`common/scripted_effects/NSP_launchpad_effects.txt`
  - 新数组 NSP_pe_hold（8 项）：进入状态 2/3/4 时设为 7，之后每天减 1。
  - 倒数到 0 后切到状态 5：空台，并且记住这次发射已经播过，同一任务不会重播。pd = 1（新火箭上台）或 -1 时照常切换。
  - 7 个 NSP_pe_set_k 都加了 nsp_ps = 5 → set_entity_animation empty。
- 如果高速下尾迹被截断太早，可以把 eval 末尾的 `NSP_pe_hold^nsp_pk = 7` 调大。
- 待测：发射以后 7 天内保持动画，第 8 天变回空台，之后一直在；新任务进入准备阶段时火箭能重新上台。

---

## 2026-10-23 · 第 94j 轮 · 发射台忽明忽暗（用户视频）
- 用户视频（9 秒）：发射台在任何缩放级别都能看到，说明 r94i 的 min_zoom 生效了。但模型在「亮灰带细节」和「整体暗灰」之间来回切换，切换和镜头高度 / 俯仰角相关，静止时也可能是暗的。暗的时候圆顶、塔架的结构还在，说明贴图没丢，是着色变了。旁边原版的桥一直是暗灰。
- 判断：PdxMeshAdvanced 的明暗受视角影响。MD 的建筑和地标（包括航天飞机地标）统一用 PdxMeshAdvancedSnow，所以改成和它们一样（gfx/entities/NSP_launchpad.gfx）。
- 待测：镜头拉近、拉远、平移时，发射台的明暗和旁边原版建筑一致，不再闪。如果还是闪，就要确认是不是 FoW：游戏暂停、镜头不动的时候，它会不会自己变暗？

---

## 2026-10-23 · 第 94i 轮 · 发射台实体拉远消失（更正 r94h）+ 代码体检
- 更正 r94h：r94f 起发射台已经是 create_entity 实体，不再是建筑。r94h 给建筑加的 drawn_at_distance 只作用在退役的建筑定义上，没有效果，但也无害。
- 真正原因：create_entity 没写 min_zoom，引擎按默认可见距离裁掉了实体。7 处 create_entity 全部加上 min_zoom = 3000（原版最远镜头约 3000；MD 的 EH 墙体用 300，传送门用 150）。
- r94h 给 normal / specular 补的 mip 链保留。
- 体检用的是 tools_lint/nsp_lint.py 外加专项检查，结果全部为 0：
  - 大括号、BOM、yml 格式和裸换行、loc 重复、§ 配对；
  - 未定义 effect / trigger / event、事件 loc、defined_text 及其 key、sprite / 贴图、container 重名；
  - scripted_gui 窗口和元素；element _visible 写在 triggers 外；_click 没 bump NSP_dirty；check_variable 写成 >= / <=；temp 变量叫 id、prev 等。
  - 动态 key NSP_PLART_ / VEART_ / TRAJART_ 在本体里没有定义，但只有子模组设 *_cart = 1 时才会读到，本体不受影响。
- 待测：战略视角下发射台仍然可见；error.log 里没有 create_entity / min_zoom 报错。

---

## 2026-10-23 · 第 94h 轮 · 发射架拉远消失、偶尔丢贴图
- 拉远消失：NSP_pad_* / NSP_spad_* 建筑都缺 drawn_at_distance，引擎超过 MAP_BUILDINGS_SHRINK_DISTANCE（原版 180）就把模型缩没。照 MD / 原版 landmark 给 10 个建筑都加上 drawn_at_distance = yes（common/buildings/NSP_launchpad_buildings.txt）。
- 丢贴图：nsp_launchpad_normal / specular.dds 只有 1 级 mip，diffuse 却有 11 级。拉远时采样器会去取不存在的 mip，有的显卡上就会显示成白模或黑模。两张都补成 32→1 共 6 级 mip，像素值不变，header 还是 128 字节。
- 待测：拉到战略视角发射架还在；反复缩放、切地图模式时贴图不丢。如果仍然偶尔丢，下一步改 diffuse 为 DXT5，并给 entity 加 cull_radius（动画里火箭飞出 bind-pose 包围盒后会被视锥裁掉）。

---

## 2026-10-23 · 第 94g 轮 · 修复帮助层 NSP_help_box_NSP_HELP_IDX_0
- 现象：error.log 报 Undefined GUI_TYPE: NSP_help_box_NSP_HELP_IDX_0。
- 原因：NSP_help_l_simp_chinese.yml 里 NSP_HELP_D_6 的字符串中间有真实换行，YAML 解析在这里断掉，后面的 NSP_HELP_IDX_0..6 都没加载。GetNSPHelpBox 拿不到文本，就把 key 名原样拼进了 entry_container。
- 修复：把真实换行改成 \n\n。规则：loc 字符串内禁止真实换行，一律写 \n。
- 待测：帮助层能正常打开、翻页，error.log 不再报这三行。

---

## 2026-10-23 · 第 94f 轮 · 地图发射台改为脚本实体（用户要求：「换建筑太死板，发射动画经常没播完就被切成空台」）
- 原因：发射阶段只有 12 天。高速运行时这 12 天只有几秒，而发射动画约 93 秒，阶段一结束就被换成空台，动画被截断。
- 新做法：
  - 不再使用 NSP_pad_* 和 NSP_spad_* 建筑。改为 create_entity 放置实体 NSP_launchpad_entity，再用 set_entity_animation 切换状态。两个效果都是 1.11 起的原版效果。
  - 实体有 5 个状态（empty / ready / launch / fail_pad / fail_air），状态名和动画 id 相同。
  - 实体 id = 7700 + 发射场下标，坐标沿用 buildings.txt 原来那几行。
  - 每次切换状态前先用同一个 id 重新 create_entity（同 id 会替换旧实体），这样读档后实体丢失也能自愈。
- 防截断规则：发射和爆炸动画播放后保持不动，任务离开发射阶段时不再切回空台（发射动画最后一帧本来就是空架）。下一枚火箭上台时才替换。
- 老存档：通过 NSP_pad_entity_r94f 旗标，一次性拆掉所有旧发射台建筑，然后全部重建为实体。建筑定义、building_* entity 和 buildings.txt 的行都保留，因为拆旧建筑时还要用到。
- 文件：
  - NSP_launchpad_effects.txt 由 work/r94f/gen.py 重新生成（原文件备份在 work/r94f/bak）；
  - NSP_launchpad.asset 末尾新增实体。
  - 调试决议 0..4 和「恢复自动」继续可用，「恢复自动」会强制全部重建。
- 待测项：
  1. 实体位置。create_entity 的 y 填的是 buildings.txt 第 5 列（地图纵坐标）；如果位置偏了，改用 province = 省号。
  2. set_entity_animation 能切换状态，并从头播放。
  3. 发射动画能完整播完。
  4. 读档后实体还在。
  5. 老存档的旧建筑已经拆除。
  6. error.log 里没有 entity 相关报错。

## 2026-10-23 · 第 94e 轮 · 发射时镜头拉近（用户要求）
- 新增 NSP_launch_camera（NSP_launchpad_effects.txt）：按任务的发射场 goto_province 到发射台所在省。
  - 没有写事件：goto_province 是普通效果。TNO 把它放在事件的 immediate 里，只是为了弹窗时镜头已经到位。
- 调用位置：NSP_advance_mission 中 ph = 5 那一行，跟在 NSP_preroll_mission 后面，和发射台动画同一天触发。
  - 载人任务没选好乘组时会停在 ph = 4，此时不会拉镜头。
- 省号：1→6881、2→3917、3→7112、4→12791、6→19996、7→17228；其余（卡角、KSC、-1）→17301。
- 待测项：
  1. 发射当天镜头跳到对应发射台；
  2. 和事件弹窗、发射动画的先后顺序；
  3. 同一天多个发射时，镜头停在最后一个；
  4. error.log 里不出现 goto_province 相关报错。

## 2026-10-23 · 第 94d 轮 · 民意和国会支持合并为「NASA公众支持度」（用户要求）
- 变量：删掉 NSP_support，只保留 NSP_popularity。
  - NSP_econ_weekly 里「国会支持向民意靠拢」那段删掉了。
  - 拨款公式不变（每周 30 + 支持度 × 0.8，单位百万美元），只是改为直接读 NSP_popularity（NSP_budget_disp / NSP_budget_weekly）。
  - 初始化里的 NSP_support = 50 已删。老存档里残留的这个变量不再被读取。
- GUI：局长面板删掉 NSP_support_button。公众支持度页签改用 222 宽的新贴图 GFX_NSP_dir_tab_wide_r94d，和人气条同宽。
  - 贴图由 work/r94d/tab.py 生成，原理是拉伸原页签的中段。原来 110 宽的贴图已移到 work/r94d/。
- 本地化：
  - NSP_POPULARITY 改为「NASA公众支持度」；TT 合并了下次拨款预估，TT_D 合并了两边的规则说明。
  - 删除 NSP_SUPPORT / _TT / _TT_D。
  - 三个 yml 里的「民意」全部改为「公众支持度」，「国会支持」改为「NASA公众支持度」。涉及事件 TT、研发解锁文案、帮助第 6 页和 nsp.12.d。
- 待测项：
  1. 页签文字完整显示；
  2. tooltip 里的下次拨款预估正常；
  3. 半年拨款随公众支持度变化。

## 2026-10-23 · 第 94c 轮 · 其他发射场的发射台改为省级建筑（用户要求）
- 原因：NSP_spad_* 原来是州级建筑（state_max），会出现在州界面顶部那一排，排在第 6 格，被 TNO 的「地区文化」图标挡住，没有发射场的州也会显示等级 0。用户要求和卡角一样，只在省份地形视图里显示。
- NSP_launchpad_buildings.txt：NSP_spad_* 的 state_max 改为 province_max = 1。
- NSP_launchpad_effects.txt：remove_building 和 add_building_construction 都加上 province：
  - 378 → 6881
  - 362 → 3917
  - 629 → 7112
  - 376 → 12791
  - 2518 → 19996
  - 463 → 17228
- 省号来源：用户上传的 TNO provinces.bmp（5120x2560）和 definition.csv，按 buildings.txt 里的坐标逐像素查出（像素位置为 x，H-1-z）。脚本 work/r94c_prov.py；bmp 存在 work/r94c/。
  - 校验：卡角那 21 行坐标查出来正好包含 17301。
- buildings.txt 的 NSP_spad 行没改，原坐标就落在上面这些省里。
- 老存档：NSP_spad_init 首次运行时把模式全部置为 -9（用 flag NSP_spad_prov_r94c 记录），强制按省级重建一次。
- 待测项：
  1. 新开局解锁其他发射场后，州界面顶部那一排不再出现发射架，点开对应省份能看到；
  2. 地图模型位置不变，5 种状态都能正常切换；
  3. 老存档里原来的州级建筑会不会残留，或者 error.log 有没有报错。

## 2026-10-23 · 第 94b 轮 · 合并文件（用户：文件太多）
- scripted_effects 从 33 个合并为 9 个：
  - NSP_api_effects：原 00_api + 02_hooks
  - NSP_ext_slot_1..3：扩展槽从 6 个减到 3 个，改名
  - NSP_space_effects：space + budget + help
  - NSP_mission_effects：aa_evq / aa_director / aa_hist_stamp / crew_r92f / programs_r92 / hist_archive / sat
  - NSP_rd_effects：rd_aa_links / rd / rd_unlock / rd_zdebug
  - NSP_rd_content_effects：rd_r51 / r52 / r53 / r57 / r77 / r85 / r86_tier / r92b / r93
  - NSP_launchpad_effects：launchpad_a_sites + launchpad
- scripted_localisation 从 7 个合并为 4 个：
  - space 合并了 cond_sl、anim_sl；
  - rd 合并了 rd_unlock_sl；
  - help_sl（work/r69/gen.py 会重写这个文件）和 bodies（work/tt/add_body_tt.py 会重写这个文件）保持独立。
- interface 的 gfx 从 10 个合并为 4 个：click_v20 / focus_v22 / orbit_v24 / r32 / r33 / r34 都并进了 NSP_space.gfx。NSP_style.gfx 由 gen_style.py 重写，所以保持独立。.gui 文件之间有加载顺序要求，没有动。
- 只是搬位置，代码一行没改。每段开头都标了「原 xxx.txt」，按旧文件名能搜到。
- 核对结果：
  - scripted effects 174 个、defined_text 197 个、sprite 199 个，合并前后数量一致，没有重名；
  - 大括号平衡；
  - audit 结果和合并前相同。
- 合并前的完整副本存在 work/archive/TNO_SPACE_r94_before_merge。
- ⚠ 用户安装时要先删掉旧的 TNO_SPACE 文件夹再解压，不然旧文件会和合并后的文件同时存在，导致重复定义。
- 之前的规则「被调用的文件要排在前面」其实不成立：r77 起就有被调用者排在后面的情况，游戏里也正常。scripted_effects 不依赖文件顺序。

## 2026-10-23 · 第 94 轮 · 扩展 API（方便别人做 sub 的 sub）
- 用户要求：优化代码，让第三方编辑、新增内容更容易，做 sub 的 sub 更简单。
- 新增文件：
  - `common/scripted_effects/NSP_00_api_effects.txt`：注册 API。
    - `NSP_reg_payload / vehicle / dest / rd / rd_small`：参数用临时变量 reg_*。按 id 写入、可重复执行；数组不够长会自动补齐。
    - `NSP_reg_allow / deny`：载荷 × 目的地许可。
    - `NSP_reg_payload_crewed / vehicle_limits / dest_attrs / dest_order`：只改单项属性或列表顺序。
    - `NSP_api_apply_unlocks`：按 *_urd 解锁子模组内容。
  - `NSP_01_slot_1..6_effects.txt`：6 个空扩展槽，每个槽有 5 个钩子：register / on_unlocks / on_recalc / on_success / on_daily。子模组用同名文件覆盖一个槽即可接入。
  - `NSP_02_hooks_effects.txt`：
    - `NSP_api_base_tables`：本体规则改成查表；
    - 钩子分发；
    - `NSP_api_register`。
  - `documentation/SUBMOD_API.md`：给子模组作者的完整说明，包括 id 段、参数、本地化键、空格表、登记表和自检清单。
  - `documentation/examples/NSP_addon_example/`：可直接运行的示例子模组，内容为研发 200、载荷 50、火箭 50、目的地 16。
- 写死的规则改为查表：
  - 载人判定：原来写死为 p < 2 / 4 / 8，现在查 NSP_pl_crewed。改了 7 处：recalc ×2、advance、tier_xp、evq_xp、scripted_loc、mod_fits ×2。
  - 载荷能去哪里：NSP_dest_allowed 和 NSP_dest_allowed_pl 里的两大段 OR，改为查 NSP_pd_ok（下标 = 载荷 × 32 + 目的地）。新触发器 NSP_pl_dest_ok。
  - 载人去月球需要研发 30：改为查 NSP_dest_crd，新触发器 NSP_dest_crew_ok，主条件和条件提示共用。
  - 土星 IB / V 的发射台、土星 V 只能在 KSC 发射：改为查 NSP_ve_pad / NSP_ve_site，新触发器 NSP_ve_pad_ok / NSP_ve_site_ok，触发器和条件提示共用。
  - 目的地 XP（两处）、卫星天体、Mission Control 行（筛选和计数两处）：改为查 NSP_dest_xp / body / view / row。
  - 载荷、火箭左右切换的上限：原来写死为 11 / 8，改为读数组长度。
  - 规划器三张大图：GUI 属性加了 `image = "[GetNSPPayloadArt]"` 等，`*_cart = 1` 时用子模组自己的 sprite 和帧。
- 调用点：
  - `NSP_rd_apply_unlocks` 末尾依次调用：
    - register；
    - 研发 id ≥ 95 的 uk 效果（之后重新做一次上限截断）；
    - `NSP_api_apply_unlocks`；
    - on_unlocks。
  - `NSP_rd_daily`：NSP_pl_crewed 比载荷数组短时，补跑一次 register（老存档第一次结算时用）。
  - `NSP_recalc_planner` 末尾调用 on_recalc，`NSP_apply_objectives` 末尾调用 on_success，`NSP_daily_tick` 调用 on_daily。
- 本体数值不变。属性表里的值和原来写死的规则逐条对照过。
- 待测：
  - 新开局和老存档都要测：规划器 8 个目的地的可选 / 不可选状态和 r93 一致；双子星、阿波罗去地月转移 / 月球轨道仍然需要研发 30；土星 IB / V 的发射台和 KSC 限制正常；载人任务有乘组和返程阶段；XP、卫星落点、Mission Control 筛选计数正常。
  - 规划器大图仍然正常显示（GUI 属性改成了 image + frame）。
  - 把示例子模组和本体一起启用，完成研发 200 后：能切到先驱者 5 号、雷神-艾布尔、日心轨道；余量约 +0.1；任务成功后民意额外 +3；error.log 里没有数组越界。
  - 这个示例会占用槽 1，正式游玩时不要一起开。

---

## 2026-10-23 · 第 93d 轮 · 徽章去锯齿
- 用户反馈 r93c 的新徽章锯齿严重。
- 原因：直接按 1px 画斜线和曲线，台阶不规则。
- 修改：badges.py 改为 8 倍超采样绘制（SD 代理），再按覆盖率 50% 取整到 48px，斜线和曲线的台阶变得均匀。
- 原子符号中心改为空心加小核；月球轨道器简化为月牙加探测器。
- 只改了 8 个 dds。

---

## 2026-10-23 · 第 93c 轮 · 徽章重画
- 用户反馈 r93b 的线框徽章「好难看」，改为和原徽章一样的粗符号，用实心块，金色分高光 / 中 / 暗三档。
- 各徽章图案：
  - sat：圆形本体加两翼
  - lander：三角本体加三条腿
  - planet：火星符号 ♂
  - station：舱体加太阳翼
  - comm：鼓形本体加电波
  - explorer：五角星
  - science：原子符号
  - lunarorb：月牙加轨道环
- 文件只改了 badges.py 和 8 个 dds，对应关系不变。

---

## 2026-10-23 · 第 93b 轮 · 载荷徽章
- 用户反馈：规划器里载荷徽章显示「?」（unassigned），要求加新图标；另外 r92 的徽章和原版阿波罗 / 双子星风格不一样。
- 新脚本 work/r93/badges.py 按原徽章的画法重画：
  - 底色按对角渐变重建；NASA 字行保留原样；
  - 字形用 2px 金线，左 / 上缘高光，外圈 1px 黑描边，部分徽章加左右「+」星。
- 重画了 sat / lander / planet / station（r92 旧版备份在 work/r93/bak/badges）。
- 新增 comm / explorer / science / lunarorb 四个徽章，NSP_space.gfx 加了 4 个 spriteType。
- NSP_PLBADGE 对应关系：
  - 2 TIROS、6 雨云 → sat
  - 3 水手 → planet
  - 5 Syncom → comm
  - 7 勘测者 → lander
  - 8 天空实验室 → station
  - 9 试验性 → explorer
  - 10 科研卫星 → science
  - 11 月球轨道器 → lunarorb
- ⚠ tools/gen_prog_icons.py 重跑会覆盖这 4 个徽章（文件头已加警告）。
- 待测：规划器切换各载荷时徽章正确，计划页的计划徽章（3..6）显示为新画法。

---

## 2026-10-23 · 第 93 轮 · 中地球轨道 / 月球轨道 + 科研卫星
- 用户反馈：轨道行「中地球轨道」「月球轨道」没有任何任务能去。另外要求加科研卫星的科技和载荷。
- 新文件 NSP_rd_r93_effects.txt，按数组长度补齐，老存档自动补上：
  - 目的地 6 中地球轨道（所需 Delta-V 10.2），由研发 94 科研卫星解锁。
  - 目的地 7 月球轨道（11.1），由研发 46 月球轨道器解锁。46 原本是小科技（方卡），改成大卡（NSP_rd_small^46 = 0）。
  - 载荷 10 科研卫星（OGO）：0.49 t，成本 8，可靠性 80，无人；可去近地轨道 / 极地轨道 / 中地球轨道。
  - 载荷 11 月球轨道器：0.39 t，成本 10，可靠性 75，无人；只能去月球轨道。
  - 阿波罗也可以去月球轨道。载人去月球轨道和地月转移一样，需要先研发 30「月球返回再入」。
  - 研发 94 科研卫星：无人探测第 5 行（新行标签「科学卫星」），第 2 列，没有前置；成本 30，工期 240，科技 3，完成后民意 +2。NSP_rd_count 改为 95。
  - 规划器目的地列表按顺序重建：近地 / 交会 / 中地球 / 静止 / 极地 / 地月转移 / 月球轨道 / 逃逸。
- Delta-V 校核：
  - 科研卫星：宇宙神-阿金纳 10.27、泰坦 II 10.31
  - 月球轨道器：宇宙神-半人马 11.30、泰坦 IIIC 11.28
- 其他接入：
  - 轨道行计数和 MC 筛选：中地球 → 地球视图第 2 行；月球轨道 → 月球视图第 2 行。
  - 任务成功后卫星显示：中地球 → 地球，月球轨道 → 月球。
  - 任务经验：中地球 7，月球轨道 12。
  - 核动力上面级 Delta-V 加成，以及徘徊者号的无人可靠性加成，现在也对月球轨道生效。
  - 载荷切换上限 9 → 11。
  - NSP_dest_allowed 和 _pl 两处都改了，NSP_cond_sl 的载人条件也同步改了。
  - 补了漏掉的 NSP_PLBADGE_9。
  - r53 的 NSP_rd_count 改成只增不减。
- 美术（work/r93/art.py，原图在 work/r93/bak）：
  - payload_art 12 帧：+OGO、+月球轨道器
  - trajectory 8 帧：+中地球、+月球轨道
  - rd_tech_4 14 帧：+OGO 线稿
- 待测：
  - 研发 94 / 46 后，规划器能选到新载荷和新目的地，Delta-V 余量为正；
  - 研发树无人探测第 5 行显示科研卫星卡，46 显示为大卡；
  - 发射成功后，轨道行计数为 1，卫星出现在地球 / 月球；
  - 老存档读档后，目的地列表有 8 行。

---

## 2026-10-23 · 第 92s 轮 · 局长特质合并
- 用户要求合成一个特质：三个特质合并为「精明官僚」，效果不变：
  - 半年拨款 +10%
  - 任务成本 -5%
  - 火箭可靠性 -2
- 只改了 NSP_DIRECTOR_TT 的文案。

---

## 2026-10-23 · 第 92r 轮 · 局长特质
- 用户要求：局长要像领导人一样有特质，并且特质有实际效果。
- 新文件 NSP_aa_director_effects.txt，按 NSP_dir_id 判断（未设置时为 0，即韦伯），效果都是现算：
  - 华盛顿老手：半年拨款 +10%。NSP_dir_income 在 NSP_budget_disp 和 NSP_budget_weekly 算完 NSP_income 后调用。
  - 精于管理：任务成本 -5%。NSP_dir_cost 放在 NSP_rd_r52_cost 末尾。
  - 外行局长：火箭可靠性 -2。NSP_dir_rel 放在 NSP_rd_r52_rel 末尾。
- tooltip：NSP_DIRECTOR_TT 在「现任局长」下面加了特质段，照 TNO 格式：黄色特质名，下一行「 - 效果：§G值§!」。
- 以后换局长：设置 NSP_dir_id，在 3 个效果里加分支，再改 tooltip。
- 待测：
  - 悬停局长时能否看到特质；
  - 拨款预估和实际拨款是否都 ×1.1；
  - 规划器里的总成本和火箭可靠性是否随特质变化。

---

## 2026-10-23 · 第 92q 轮 · 历史卡片：结束日期 + 载荷 / 火箭
- 用户反馈：游玩中结束的任务，历史卡片不显示日期（开局档案有）；tooltip 里也看不到用了哪种载荷、哪种火箭。
- 改动：
  - 新文件 NSP_aa_hist_stamp_effects.txt，提供 NSP_hist_stamp：任务进入历史时，把 global.date 写进 NSP_m_end^id，数组按任务 id 补齐。
    - 在 NSP_resolve_mission 和 NSP_resolve_return 中调用；
    - 两处 init 会清空该数组。
  - 卡片第三行：有结束日期时用 NSP_IE_ETA_D，显示「§g日期§! · 目的地」，与档案格式一致；老存档里的任务没有日期，保留原来的「目的地：…」。
  - tooltip（NSP_IE_TT_N）：
    - 第二行改为「目的地 · 发射场」；
    - 新增「载荷」「火箭」两行，以及乘组、结束日期。
    - 新增 defined_text：GetNSPHistPL / VE / Site / End。
- 待测：
  - [?NSP_m_end^v.GetDateStringNoHour] 能否显示日期。数组元素后面接 .GetDateString* 的写法没有先例。如果显示成数字或空白，就改成在 stamp 时另存年、月、日三个数。
  - 新结束的任务，卡片和 tooltip 是否正确。

---

## 2026-10-23 · 第 92p 轮 · 其他发射场也放发射台
- 用户要求：卡角以外的发射场也要有地图发射台。
- 做法：
  - 用州级建筑，不用省级。原因：卡角用的省级写法需要省号（17301），其他州没有省号表；州级建筑不需要省号（同原版 landmark）。
  - 新增 5 种类型 NSP_spad_empty / ready / launch / fail_pad / fail_air，level_cap 设为 state_max = 1。
  - 模型和动画完全复用卡角，entity 在 gfx/entities/NSP_launchpad_sites.asset，只改了名字。
- 位置：州号与原版一致（佛州 366 已验证）。用 map/buildings.txt 里各州坐标拟合经纬度，再取每州离真实发射场最近的 bunker 坐标，每州每种类型一行，共 30 行（CRLF，结尾不换行）：
  - 1 范登堡：州 378，坐标 (850, 1776)
  - 2 沃洛普斯：州 362，(1484, 1823)
  - 3 考艾岛 PMRF：州 629，(292, 1580)
  - 4 白沙：州 376，(1052, 1739)
  - 6 约翰斯顿环礁：州 2518，(151, 1503)
  - 7 波克平原：州 463，(457, 2282)
- 脚本：
  - 新文件 NSP_launchpad_a_sites_effects.txt，排在 NSP_launchpad_effects 之前；
  - 每个发射场的模式存在 NSP_spad_mode^k，规则与卡角相同；
  - 发射场未研发时不显示（模式 -1），研发后显示空台；
  - NSP_pad_update 每天同时更新；
  - 调试决议 0～4 和「恢复自动」对所有发射场一起生效。
- 待测：
  - 研发解锁后，各发射场出现空台；
  - 从该发射场发射，经历总装、发射、爆炸，模型对得上；
  - 位置偏离太多或落在海里时，告诉我，改 buildings.txt 末尾 30 行的坐标；
  - 州里没有空位时，error.log 是否报 add_building_construction 失败。

---

## 2026-10-23 · 第 92o 轮 · 时间线只有超出时才出滚动条
- 现象：无人任务只有 6 行，也一直显示滚动条（用户反馈）。
- 原因：NSP_timeline_grid 的 size 写死成 8 行高（216）。滚动容器按 grid 的 size 算内容高度，所以总是判定超出。另外上下边距 2+2，加上 6 行的 162，正好等于容器高 166。
- 修改（interface/NSP_space.gui）：
  - grid 高度 216 → 162，只按 6 行占位；
  - 容器下边距 2 → 0；
  - autohide 用默认值。
- 待测：
  - 无人任务（6 行）不出现滚动条；
  - 载人任务（8 行）出现滚动条，能滚到第 8 行；
  - 如果 8 行被截断、不能滚动，说明 grid 不随行数长高，需要改回 216 并换方案。

---

## 2026-10-23 · 第 92n 轮 · 成本显示改为 B
- 用户要求，以下显示改用 B（内部仍按百万记账，只在显示时 ÷1000）：
  - 规划器载荷成本 NSP_PAYLOAD_COST：原「$x 百万」，改为 NSP_pl_cost_b，保留 3 位小数；
  - 规划器火箭成本 NSP_VEHICLE_COST：改为 NSP_ve_cost_b，保留 3 位小数；
  - 总成本 NSP_COST_V1：改为 NSP_calc_cost_b，保留 2 位小数（格子只有 62px 宽）；
  - 研发卡成本 NSP_RD_C_COST：改为 NSP_rd_sel_cost_b，保留 3 位小数。
- 换算变量在 NSP_recalc_planner（算完 NSP_calc_cost 后）和 NSP_rd_effects 的选中项派生值里计算。
- 本轮推翻了 r54 的「单项成本保持 M」。修正描述 NSP_MOD_DESC_* 里的「+6M」暂未改。
- 待测：
  - 4 处数字显示正确，没有被截断；
  - 总成本格不溢出。

---

## 2026-10-23 · 第 92m 轮 · 全部事件排查 + 效果移到选项提示
- 排查结果：
  - 选项里触发自己的情况只有 nsp.40（r92l 已修）。其他事件的选项只会触发别的事件（nsp.1 → 升级 nsp.11），不受影响。
  - 发现同类隐患，任务结果事件 nsp.1..7：
    - 描述和选项效果都读全局变量 NSP_last_mission / NSP_evt_mid。几天内有两个任务出结果时，后一个会覆盖前一个：描述显示成另一个任务，nsp.1 的经验和目标进度会记到错的任务上（一个算两次，一个漏掉）。
    - 同一事件也可能同时有多份待处理。
- 修复：新文件 NSP_aa_evq_effects.txt，任务结果事件改为排队。
  - 结果先入队（NSP_evq_mid / NSP_evq_kind），一次只弹一个。
  - 点选项时 NSP_evq_pop 出队，并把指针拉回本事件的任务；第二天的每日结算 NSP_evq_tick 再弹下一个。
  - 事件开着超过 20 天，重弹队首。
  - resolve_mission、resolve_return 和推进阶段时的 nsp.4 / nsp.6，都改为调用 NSP_evq_push。
  - NSP_last_mission 不再在结算时写入。
- 效果放进选项提示（用户要求）：所有事件的选项改为 custom_effect_tooltip = NSP_EVT_TT_* 加 hidden_effect，不再显示「变量 +x」之类的原始效果行。
  - 描述里原来的「§R任务失败 / 民意 -5」、新计划和民意、拨款金额、研发效果、等级奖励，都挪到选项提示里。
  - nsp.10 / 11 / 12 的效果在触发时就已经生效，选项提示只做显示。
  - nsp.1 的经验数值由 NSP_evq_xp_preview 预先算好，存在 NSP_evt_xp 里。改 NSP_tier_mission_xp 的公式时，两处要同步改。
  - 乘组选项显示座位、人名，以及任务和返程可靠性加成（新数组 NSP_crew_cand_bn）。
  - NSP_reputation / NSP_science 界面上没有显示，所以提示里不写。
- 待测：
  - 每个事件选项的悬停提示能显示效果，且没有原始变量行；
  - 两个任务同一天出结果时，事件一个接一个弹出，各自显示自己的任务名；
  - 乘组选项提示里的加成数字正确。

---

## 2026-10-23 · 第 92l 轮 · 修复乘组选拔事件只弹一次、之后任务卡住
- 现象：第一席选完后，第二席不再弹出；或者下一个载人任务进入乘组阶段后没有事件。任务停在「乘组」，因为 r92i 规定座位没选完不能发射。
- 原因：第二席、换一批人选、队列里的下一个任务，都是在 nsp.40 的选项里再触发 nsp.40。同一个事件在自己的选项里触发自己会被引擎丢掉，队列因此一直卡住，后面的任务也排不上。
- 修复：
  - events：新增 nsp.41，内容与 nsp.40 完全相同，共用 nsp.40.* 的本地化。immediate 里记下 NSP_crew_evt。
  - NSP_crew_fire：nsp.40 和 nsp.41 交替触发。NSP_crew_begin、NSP_crew_next_seat 和「看看其他人选」都改走这里。以后不要直接写 country_event = { id = nsp.40 }。
  - NSP_crew_watchdog：每日由 NSP_astro_date_check 调用。
    - 队首任务已不在 NSP_missions 里（取消或已结算）→ 移出队列，接着处理下一个。
    - 队列非空但 15 天没弹出选人事件 → 重弹当前这一席，不从头开始，所以不会重复上人或重复加可靠性。
  - 已经卡住的存档：读档后最多 15 天会自动重新弹出。
- 备份：work/r92l/bak/。
- 待测：
  - 双子星（2 席）和阿波罗（3 席）能连续选完；
  - 「看看其他人选」点两次都能弹出；
  - 两个载人任务同时进入乘组阶段，第一个选完后马上弹出第二个；
  - 选完第二天进入发射。

---

## 2026-10-23 · 第 92k 轮 · 载人任务在轨失败后仍要返程
- 以前载人任务在轨失败就直接结束任务，不再判定返程。现在改为：
  - 在轨阶段结束时主任务失败 → 弹 nsp.6「在轨任务失败」（声望 -25、民意 -5，乘组紧急返程），任务继续进入返程阶段。
  - 返程阶段结束时 NSP_resolve_return 用预掷判断主任务成没成：
    - 主任务成功、返程成功 → nsp.1；
    - 主任务失败、返程成功 → nsp.7「乘组平安返回」（民意 +2），乘组计一次飞行；
    - 返程失败 → nsp.3，乘组遇难。
  - NSP_hist_fail 只写一次。
- 发射失败（台上 / 空中爆炸）仍然直接结束（逃逸中止，乘组生还，不计飞行）。
- 新增 GetNSPLastCrewSafe 和 NSP_CREW_SAFE_0..3。
- 待测：载人任务在轨失败后时间线继续走「返程」，结束时弹 nsp.7 或 nsp.3。

---

## 2026-10-23 · 第 92j 轮 · 时间线 8 行压到页脚
- 原因：NSP_tl_scroll 没有 background，滚动容器的边界被忽略，既不裁切也不出滚动条。r74b 时只有 6 行刚好放满，所以一直没暴露；r92f 加到 8 行后，第 7、8 行压到了「预计完成」上。
- 修复：给 NSP_tl_scroll 加 background GFX_NSP_scroll_bg（和 NSP_mc_box 同一写法）。滚动条仍用原版的 right_vertical_slider。
- 待测：载人任务的时间线裁在 166 高度内，右侧出现原版滚动条，滚轮能滚到「返程」；无人任务 6 行不出滚动条。

---

## 2026-10-23 · 第 92i 轮 · 乘组没选齐就不发射
- NSP_advance_mission：任务要进入阶段 5 时，如果是载人任务而且还在 NSP_crew_queue 里（座位没选完），就停在阶段 4，phase_left 设为 1，每天重查，总剩余天数不减。
- 选完最后一席，或者选了「没有待命的宇航员」，任务就离开队列，第二天进入发射。
- 待测：总装结束后先不选人，确认时间线一直停在「乘组」；选完后第二天进入发射。

---

## 2026-10-23 · 第 92h 轮 · 删掉苏联（国际）任务的残留代码
- 苏联的内容（任务种子、载荷槽、贴图帧）r88 / r89 已经删了，这轮把剩下的国际任务框架也拿掉：
  - NSP_missions_intl 数组和 NSP_m_intl 数组；
  - 任务控制本国页签里的国际任务循环；
  - 每日推进和清理里的国际任务循环；
  - 发射、在轨、返程、乘组各处的 intl = 0 条件；
  - 档案任务里对 NSP_m_intl 的写入。
- NSP_mc_intl_grid / NSP_intl_entry 只是名字带 intl，实际显示的是「历史」页签，保留不动。
- 旧存档里残留的 NSP_missions_intl 不会再被读取。需要新开局。

---

## 2026-10-23 · 第 92g 轮 · 审查 r92f 代码后修的几处问题
- 国际任务（NSP_m_intl = 1）进入阶段 4 时也会调用 NSP_crew_request，弹出 nsp.40 让玩家给苏联任务挑美国宇航员。现在加了 intl = 0 条件。
- 乘组事件拖到发射预掷之后才选：新上的人会改动 NSP_m_rel，结果和预掷对不上；如果任务已经结算，宇航员会永远卡在「执行任务」。现在 NSP_crew_assign 只在 NSP_m_phase < 5 时才上人（拆出 NSP_crew_assign_do），否则直接跳到下一席。
- 「看看其他人选」可能抽回同一批人。现在先排除上一批候选，排除后没人可选再放回。换座位或换任务时清空 NSP_crew_cand。NSP_crew_pool_n 改为总待命人数。
- 已核对：载人判定 0 / 1 / 4 / 8 和 r89 的载荷编号一致；座位数为水星 1、双子星 2、阿波罗和天空实验室 3；无人任务跳过阶段 4 和 7，预掷、发射判定和结算路径都没断；主任务失败释放乘组（生还、不计飞行次数）；只有返程才计飞行或遇难；任务历史不会重复写入。
- 已知小问题（未改）：从玩家没选完乘组到发射之间不会提醒，空座位照样能发射。

---

## 2026-10-23 · 第 92f 轮 · 载人任务的乘组和返程阶段；发射、返程分别判定并弹事件
- 阶段改为 8 个：0 规划、1 建造、2 验证、3 总装、4 乘组（仅载人，20 天）、5 发射、6 在轨、7 返程（仅载人，6 天），8 为已结束。无人任务自动跳过 4 和 7。
  - 发射场占用改为 < 6，预掷改为在 ph = 5 时进行。
  - 地图发射台：火箭在 3 / 4 阶段立在台上，5 阶段发射。档案任务的 phase 改为 8。
- 判定和事件：
  - 发射阶段结束时：台上或空中爆炸 → nsp.5「发射失败」，任务结束；否则弹 nsp.4「发射成功」（民意 +1），进入在轨。
  - 在轨阶段结束：入轨后失败（fkind 5）→ nsp.2「在轨任务失败」。无人任务成功 → nsp.1。载人任务成功 → 进入返程。
  - 返程阶段结束：用 NSP_m_rrel 再掷一次。成功 → nsp.1；失败 → nsp.3「返程失败」，乘组遇难，民意 -12。
  - 返程可靠性 = 100 − (100 − 载荷可靠性) ÷ 5，在开任务时写入。
- 乘组（新文件 NSP_crew_r92f_effects.txt）：
  - 30 名史实宇航员，NSP_astro_grp / st / fl 三个数组。批次：水星七人开局可用，新九人 1962.9.17 入选，第三批十四人 1963.10.18 入选。
  - 开局谢泼德、格里索姆各有 1 次飞行，两次档案飞行也写上了乘组。
  - 进入乘组阶段时调用 NSP_crew_request 排队，事件 nsp.40 逐席选人：每次随机给 4 名候选，可以「看看其他人选」，没人可选时座位空着。座位数：水星 1、双子星 2、阿波罗和天空实验室 3。
  - 每名宇航员每次飞行经验 +0.5 可靠性（最多 +2），主任务和返程都加。
  - 任务结束时释放乘组：生还且成功的计一次飞行；主任务失败的生还但不计；返程失败的标为遇难，不再能选。
- 界面：
  - 时间线由 NSP_recalc_planner 按载人或无人重建 NSP_phase_ids。行号用 GetNSPTLNum，无人任务的行号连续。
  - 行框 8 帧（tools/gen_r92f_tlrow.py：第 5 帧乘组为紫色，第 8 帧返程为蓝色）。grid 高度 216，载人任务的第 7、8 行要在 NSP_tl_scroll 里滚动。
  - 历史卡片 tooltip 加了乘组行（GetNSPHistCrew）。NSP_REL_TT_D 补充了返程和经验的说明。
- 需要新开局。待测：
  - 水星任务时间线有 8 行，滚动条可用。
  - 总装结束后弹 nsp.40，选人后能继续下一席。
  - 发射结束时弹 nsp.4 或 nsp.5；返程结束时弹 nsp.1 或 nsp.3。
  - §L / §B 的颜色是否存在。

---

## 2026-10-23 · 第 92e 轮 · 太空科技等级 tooltip 重写，左右圆圈可查看本级和下一级效果
- 用户反馈等级 tooltip 看不懂，希望把鼠标放在两侧圆圈上就能看前一级和后一级的效果。
- NSP_tech_circle_l / _r 去掉 alwaystransparent，加 pdx_tooltip：
  - 左边 NSP_TIER_L_TT：本级累计效果，加下一个里程碑。
  - 右边 NSP_TIER_R_TT：还差多少点、升级时立即获得什么、升级后的累计效果（括号里注明增量），以及里程碑研发槽。
- NSP_TECH_TT 重写为分段结构：等级、进度和还差多少，然后是当前效果，最后提示可以看两侧圆圈。
- NSP_TECH_TT_D 重写成「怎么获得 / 升级规则」两段，并注明火箭可靠性加成按 50% 计（r92d）。
- NSP_tier_refresh 新增显示变量：NSP_tier_next_rdspd、NSP_tier_next_rel、NSP_tier_need、NSP_tier_slots_got。
- 新增 scripted loc：GetNSPTierNameNext（逐级写死）、GetNSPTierSlotsGot、GetNSPTierNextSlotLine、GetNSPTierMilestone。
- 待测：两个圆圈能否悬停（圆圈上的数字文本框本来就是 alwaystransparent）；第 3 级时右边应显示研发槽 +1。

---

## 2026-10-23 · 第 92d 轮 · 可靠性公式改为「基础 × 75%、加成减半」
- 用户要求：不再对最终结果 × 50%，改成所有基础可靠性降到 75%、加成可靠性减半。
- NSP_recalc_planner 分别算载荷和火箭：
  - 可靠性 = 基础 × 0.75 + 净加成。净加成为正时 × 0.5；为负时（修正的惩罚）照算。
  - 然后再截到 0..100，最后总计 = 载荷 × 火箭 ÷ 100。删掉了 r62 的 × 0.5。
- 规划器里的「基础可靠性」改为显示 × 75% 后的值（NSP_calc_rel_pl_base / NSP_calc_rel_ve_base）。NSP_REL_TT_D 的公式文字同步更新。
- 例子：双子星 80 + 泰坦 IIIC 80，不带加成。旧公式 80 × 80 ÷ 100 × 50% = 32%，新公式 60 × 60 ÷ 100 = 36%。

---

## 2026-10-23 · 第 92c 轮 · 开局历史档案（1957–1961 年的 14 次发射）
- 新文件 NSP_hist_archive_effects.txt，NSP_init 在清空任务数组后调用 NSP_hist_archive_init。
  - 写入 14 条史实发射，从 Vanguard TV-3 一直到 Mercury-Atlas 5，其中失败 3 次：TV-3、Pioneer 1 和 MR-1。
  - 占用任务 id 0..13，数据进 NSP_m_* 和 NSP_missions_hist，失败的进 NSP_hist_fail。不进 NSP_missions，所以不影响发射场、卫星、目标和经验。
- 档案标记用新数组 NSP_m_arch^v，值为档案号 k；值为 -1 或下标越界的是普通任务。NSP_clear_missions 会一起清空它。
- 历史卡片：
  - 名称改读 GetNSPHistName，档案任务用史实名。
  - 底行改读 GetNSPHistEta，档案任务显示「日期 · 目的地」，可以是亚轨道。
  - NSP_ie_name 加了 pdx_tooltip NSP_IE_TT。档案任务显示史实简介、火箭和结果；普通任务显示名称、目的地和结果。
- 文本在 NSP_ARCH_NAME_k、NSP_ARCH_ETA_k、NSP_ARCH_TT_k。
- 待测（需要新开局）：
  - 历史页签有 14 张卡，最新的 Mercury-Atlas 5 排第一。
  - 三张失败卡显示红色。
  - instantTextBox 上的 pdx_tooltip 能否显示。不行的话改用透明 buttonType 盖住整张卡。

---

## 2026-10-23 · 第 92b 轮 · 默认试验性载荷 / 火箭、1962.1.1 开局的计划进度修正
- 问题（用户实机截图）：开局规划器默认选中双子星飞船 + 泰坦 IIIC，但没有任何科技解锁它们；双子星计划写着 1962.1.12 开始，开局却已完成 2/3、1/2，任务编号也是 Gemini 19。
- 新增常开的默认组合（NSP_rd_r92b_effects.txt → NSP_planner_r92b，由 NSP_rd_apply_unlocks 末尾调用）：
  - 载荷 9「试验性载荷」：Explorer，0.014 t，原型成本 1，可靠性 75，无人，可去近地轨道 / 极地轨道。
  - 火箭 8「试验性火箭」：干重 4 t，燃料 21 t，比冲 255 s，原型成本 2，可靠性 70；ΔV 约 9.8，刚好够近地轨道。
  - NSP_reset_planner 默认选 9 / 8；载荷、火箭切换上限分别改成 9 / 8。
  - NSP_dest_allowed_pl 的两处都加了载荷 9。
  - 美术：tools/gen_r92b_art.py 生成 payload_art 第 10 帧（探险者式）、vehicle_art 第 9 帧（朱诺 I 式），从 work/r92b/bak 读原图。
- 计划：开局只解锁水星计划，默认显示水星。
  - 双子星 1962.1.12（nsp.34）、阿波罗 1962.5.25（nsp.35，按用户要求推迟一年）改为日期事件解锁。
  - 目标进度按史实重置：只保留水星 A 2/2（1961 年两次亚轨道飞行），其余全部为 0。
  - 任务编号重置：Gemini 1、Apollo 1、TIROS 4、Mariner 1。
- 必须新开局测试。
- 待测：开局规划器显示试验性载荷 / 火箭和新美术、能发射近地轨道；1.12 弹双子星事件，5.25 弹阿波罗事件。

---

## 2026-10-22 · 第 92 轮 · 研发效果改成原版科技写法、卡片 TNO 式 tooltip、新增 4 个日期解锁的计划
### 研发效果（参照原版 / TNO 科技 tooltip 截图）
- 94 条 NSP_RD_UNLOCK_* 全部改成多行，由 work/r92/conv_unlock.py 转换：
  - 解锁类写成「§D解锁火箭§!§Y名称§!」。
  - 数值写成「火箭可靠性：§G+3%§!」。
  - 有作用范围的（土星 IB / V、阿波罗、带舱外活动系统时……）先写「范围：」，再缩进列数值。
  - 去掉「xxx ·」风味前缀和 $$。
- 标题「§Y效果：§!」由外层加：弹窗 NSP_RD_D_UNLOCK、NSP_RD_D_UNLOCK_TT、研发完成事件 nsp.10。
- 弹窗加高 470 → 540，效果区 y288 共 6 行，下面的元素整体下移 78。
- 卡片 tooltip NSP_RDC_TT 改成 TNO 科技样式：名称、研究所需时间（超前时 ×1.5 并显示红字警告，含太空科技加速）、研发中 / 已完成、效果、「点击查看详情」。
  - 新增 defined_text GetNSPRDCardName / Days / State / Unlock，在 tooltip 里读 v（先例：r67 的 GetNSPPtabTT）。
### 新计划（日期到了触发事件解锁）
- 新文件 NSP_programs_r92_effects.txt：
  - 3 应用卫星计划 1963.7.1；4 勘测者计划 1964.6.1；5 水手计划 1964.11.1；6 天空实验室计划 1966.1.1。
  - NSP_programs_extend：按长度补计划 / 目标数组，NSP_init 和每天都会调用。
  - NSP_programs_date_check：每个计划用一个 flag，只发一次 nsp.30～33。
  - NSP_program_unlock：解锁、切到该计划、翻到它所在页，民意 +2。
  - NSP_programs_objectives：新目标 6～13 的推进规则，未解锁时不计。
- NSP_space_effects：NSP_init / NSP_daily_tick / NSP_apply_objectives 接入；目标钳制循环 end 6 → 14。
- 页签贴图 nsp_program_tabs.dds 14 → 22 帧，新增 4 枚 48×48 徽章（tools/gen_prog_icons.py，从 work/r92/bak 读原图，可重跑）。
- 共 7 个计划加「?」= 8 格，超过 7 格，自动进入 r67 的分页（‹ + 5 格 + ›）。
- loc：PROG_NAME / STARTED / BADGE / OBJ_DESC_6～13；未解锁页签 tooltip 显示公布日期（GetNSPPtabDate）；事件文案 nsp.30～33。
- 备份：work/r92/bak/。
- 待测：
  - 卡片 tooltip 里 v 能读到（名称、工期、效果对应正确）。
  - 效果多行缩进显示正常。
  - 控制台 `set_date 1963.7.2` 后弹出 nsp.30，页签解锁并切到新计划。
  - 分页 ‹ › 正常；新计划目标在任务成功后推进。
  - 页签 / 徽章贴图对应。

---

## 2026-10-22 · 第 91b 轮 · 太空科技 tooltip 修复：等级名为空、拨款显示 $$
- 用户实机截图：「太空科技 · 第 8 级「 」」等级名为空；「拨款 +$$0.75B」多一个 $。
- GetNSPTierName：动态拼键 "NSP_TIER_NAME_[?NSP_tech_tier|0]" 实机显示为空（其他不带 |0 的拼键正常）。改为 2～10 级逐级写死，>10 为 11、其余为 1，先 set_temp_variable 再比较。
- NSP_TECH_TT：iconType 的 pdx_tooltip 里 $$ 不会转义成 $，改成「拨款 +0.75B」（和启动任务 tooltip 的 −xM 写法一致）。其他 tooltip 键已 grep，没有 $$。
- 备份：work/r91b/bak/。
- 待测：等级名正确显示；拨款一行不再出现 $$。

---

## 2026-10-22 · 第 91 轮 · 研发页：底部抽屉改成点击弹出的详情窗
- 用户要求科技界面改为「点击后弹出窗口显示详细信息」，参照 TNO_GNG_Map_GUI_Info_Window 的做法。
- NSP_rd.gui：
  - 新增顶层窗口 NSP_rd_pop（290×470，NSP_home_window 坐标 (754,116)），外层 clipping = yes，内层 NSP_rd_pop_inner 从右侧 x=300 滑到 0（decelerated，300ms），背景用 GFX_tiled_window_thin_border2，右上角放 GFX_crt_closebutton。
  - 原抽屉 ①②③ 栏（名称、时代、线稿、描述、前置、解锁、启动按钮、成本/工期/科技、状态、排队）竖排搬进弹窗，元素名不变；栏宽 330 → 254，描述高 34 → 68。
  - 原抽屉 ④ 研发槽改为底部 36 高横条 NSP_rd_qstrip（y646），三个槽横排。
  - 树区高度 438 → 548。旧抽屉整段注释保留，标 @ retired-20261022 r91。
- NSP_space_rd_guis.txt：
  - 新增 scripted_gui NSP_rd_pop（visible = NSP_rd_open + NSP_rd_pop_open，dirty = NSP_dirty），d_tech_N_visible、start 的 click_enabled / properties / _click 从 NSP_rd 条目搬过来。
  - 卡片点击：选中并弹出；再点同一张已选中的卡则收起。
- NSP_rd_effects：NSP_open_rd / NSP_close_rd / NSP_rd_set_track 都会清 NSP_rd_pop_open（进页、退出、切分类时收起弹窗）。
- loc：新增 NSP_RD_POP_CLOSE_TT。
- 备份：work/r91/bak/。
- 待测：
  - 点卡片后弹窗从右侧滑出，切换卡片时内容即时更新，关闭后再点能重播滑入。
  - 弹窗盖住树区右侧时，点击不穿透到下面的卡片。
  - 弹窗在研发页之上（层级正确），没有跑到屏幕 0,0。
  - 描述 4 行是否够用、有没有截断；启动按钮禁用态正常。
  - 底部研发槽横条对齐；树区拉高后滚动条和右下角正常。
  - 帮助覆盖层（help overlay）截图里的抽屉是旧布局，需要重拍。

---

## 2026-10-22 · 第 90 轮 · tooltip 改成 TNO 决议式，图标走本地化 £
- 用户给了 TNO 决议 tooltip 的截图做参考：黄色小节标题，条件前面放红叉/绿勾，图标直接写在本地化文本里。
- 启动任务按钮 NSP_START_TT 改成三段：
  - 标题「§Y启动任务§!」，下面一行总结论（GetNSPStartHead）。
  - §Y先决条件：§! 每条都列出来，满足的用 £trigger_yes（新增 NSP_COND_Y_*），没满足的用 £trigger_no（NSP_COND_S_*）。先进双子星改装 / 对接系统只在需要时才出现。
  - §Y启动后的效果：§! 预算 −xM、预计成功率、任务周期（NSP_calc_total_days）。
- NSP_cond_sl：GetNSPCS_PL/VE/PAD/DEST/SITE/MARGIN/BUDGET 满足时不再返回空，改为返回 NSP_COND_Y_*；GetNSPCS_ALT/DOCK 拆成三档：不需要、已装配、缺失。
- 规划器的发射场 / 目的地行 tooltip（NSP_COND_T_* / D_*，共 16 条）把「§R·§!」换成 £trigger_no，仍然只列没满足的条件。
- 研发状态行 NSP_RD_REASON_0~4/6 加上 £trigger_no / £trigger_yes。
- 图标名用的是原版 GFX_trigger_yes / GFX_trigger_no（TNO 有自己的重绘版，截图里就是），写法 £trigger_yes，不用写 GFX_ 前缀。
- 备份：work/r90/bak/。
- 待测：
  - 在 scripted GUI 的 pdx_tooltip 里，£ 图标能正常渲染，不显示成「£trigger_yes」字样。
  - 图标和中文基线是否对齐。
  - 先决条件逐条列出来后 tooltip 长度能否接受。
  - error.log 里没有 texticon / sprite 报错。

---

## 2026-10-22 · 第 89 轮 · 彻底删掉苏联载荷空位，载荷重新编号（不兼容老存档）
- 用户确认不需要兼容老存档，载荷下标 4 不再保留。新编号：0 Gemini、1 Apollo、2 TIROS、3 Mariner、4 Mercury、5 Syncom、6 Nimbus、7 Surveyor、8 Skylab（原 5～9 整体 −1）。
- NSP_space_effects：NSP_init 删掉第 5 行空载荷；载人判断改为 p<2 / 4 / 8；水星 LEO 规则 p=5 → 4；载荷切换上限 >9 → >8。
- NSP_rd_r51_effects：数组补项触发条件 ^num = 5 → 4；pl_next / pl_unl 长度 10 → 9；解锁下标 5～9 → 4～8；删掉 pl_unl^4 空位行。
- NSP_rd_r52：无人载荷 p=6/7/8 → 5/6/7。NSP_rd_r77：天空实验室 p=9 → 8。NSP_rd_r86_tier：载人经验 5/9 → 4/8。
- NSP_space_triggers：NSP_sel_payload = 5～9 共 14 处 → 4～8（目的地限制、载人 / 无人判断）。
- loc：NSP_PLBADGE / NSP_PL_NAME / NSP_PL_TYPE / NSP_PL_SHORT 的 5～9 → 4～8。
- nsp_payload_art.dds：删掉第 5 帧（原苏联空帧，alpha 全 0），10 帧 → 9 帧，GFX_NSP_payload_art 的 noOfFrames = 9。
- 备份：work/r88b/bak/。必须新开局测试。
- 待测：规划器依次切换 9 种载荷，名称、徽章、图片对应正确；水星只能去 LEO、勘测者只能去地月转移；水星和天空实验室吃载人可靠性加成。

---

## 2026-10-22 · 第 88 轮 · 删除苏联任务
- 删掉 NSP_PL_SHORT_4（r87c 刚改成的 Vostok）和 NSP_init 里两条注释掉的苏联种子任务。
- 载荷下标 4 保留为空位（NSP_pl_unl^4 永远为 0，规划器里本来就不出现）。真删掉这个下标会让 5～9 号载荷（Mercury、Syncom、Nimbus、Surveyor、Skylab）在所有数组和老存档里整体错位。
- 相关注释同步改为「空位」：NSP_space_effects / NSP_rd_r51_effects / NSP_space_triggers / NSP_space.gfx。
- 待测：规划器载荷切换仍跳过下标 4；error.log 没有 NSP_PL_SHORT_4 缺键报错（正常不会被读到）。

---

## 2026-10-22 · 第 87c 轮 · 任务（飞船）命名改为英文
- NSP_PL_SHORT_0..9 改为英文：Gemini / Apollo / TIROS / Mariner / Vostok（4 号原为「苏联」，国际任务用）/ Mercury / Syncom / Nimbus / Surveyor / Skylab。
- 这组键只用于任务名：任务卡 NSP_ME_NAME / NSP_IE_NAME，以及规划器的 NSP_PL_NAME。载荷全称 NSP_PL_NAME_* 仍是中文。
- 待测：规划器标题显示「Gemini 21」；任务卡和历史卡显示英文名。

---

## 2026-10-22 · 第 87b 轮 · 任务卡贴图 DDS 头修复
- gen_mc_card.py 写出的 DDS 头是 136 字节，比标准的 128 字节多 8 字节，导致四张 nsp_mc_* 贴图的像素整体错位 2 px，框线跑偏。
- 改用和 gen_lsite_marker.py 相同的 128 字节头，加了 assert 校验后重新生成。
- 预览图：work/r87/mc_card_preview.png。

---

## 2026-10-22 · 第 87 轮 · Mission Control 任务卡改成 TNO 原版样式
- 用户给了 TNO 原版任务卡截图作为参考（Gemini 9 / Apollo 1）。
- 新增 tools/gen_mc_card.py，生成以下贴图：
  - nsp_mc_card.dds：方角双线框，外线亮、内线暗，borderSize 5；
  - nsp_mc_iconbox.dds：28×28 方形图标框；
  - nsp_mc_dash.dds：180×2 虚线分隔；
  - nsp_mc_bar.dds：214×24 粗进度条，2px 白框，41 个空心分格，21 帧，沿用原 t_bar 帧映射。
- NSP_space.gfx：新增 GFX_NSP_mc_card / mc_iconbox / mc_dash / mc_bar。
- NSP_space.gui：NSP_mission_entry 和 NSP_intl_entry 改为 226×118。布局：图标框 (7,7)、白色标题 aldrich_20 y11、虚线 y38、阶段 y43、进度条 (6,64)、预计时间 y94。两个 gridbox 的 slotsize 高度 96 改为 122。旧条目注释保留，标 @ retired-20261022。
- 元素名都没改，scripted_gui 和 properties 不用动。
- loc：NSP_ME_NAME / NSP_IE_NAME 标题由黄色改为白色；NSP_ME_ETA 改成「预计完成：N 天后」。
- 待测：任务卡在滚动区内对齐；进度条帧正确；图标在框内居中；中文标题不被截断。

---

## 2026-10-22 · 第 86b 轮 · 修复发射场在没有任务时也显示“占用中”，以及 tooltip 名称显示成 $KEY$
- 现象：一个任务都没有，地图上所有发射场仍显示琥珀色“占用中”；tooltip 原样显示 $NSP_SITE_2$ 和 $NSP_SITE_DESC_2$。
- 原因：NSP_site_busy 用 any_of 现场判断数组，在空数组时实机也判成占用；GUI tooltip 里嵌套的 $KEY$ 没有展开。
- 修复：
  - NSP_lsite_update 先把数组 NSP_lsite_busy（8 项）清成 0，再遍历 NSP_missions：发射场 ≥ 0 且阶段 < 5 的记为 1；帧值 = 数组值 + 1。
  - NSP_site_busy 改为直接读这个数组，加了 ^num 越界保护。
  - NSP_reset_planner 改为先刷新占用，再调用 NSP_pick_free_site。
  - NSP_LSITE_TT_0..7 和 _D 不再用 $KEY$ 引用，直接写入发射场名称和说明。
- 待测：没有任务时全部为青色空闲；开一个任务后只有该发射场变琥珀；tooltip 显示中文名称。

---

## 2026-10-22 · 第 86 轮 · 太空科技等级系统优化
- 原来的问题：门槛每级 +50，开局就是 3 级 110/200；全部研发加起来约 494 点，打完也只到 5 级左右。升级只给一次性拨款和民意，等级本身没有任何作用。任务成功固定只给 +4。
- 新文件 common/scripted_effects/NSP_rd_r86_tier_effects.txt：
  - 门槛 = 30 + 10 × 等级。1962 开局是第 2 级 0/50，正常一局能到 9～10 级。
  - 被动加成按等级现算：研发速度每级 +4%（NSP_tier_rdspd），火箭可靠性每级 +1（NSP_tier_rel）。
  - 里程碑：第 4、7、10 级各 +1 研发槽，用 flag 记账，老存档自动补发。
  - 升级奖励：拨款 300 + 50 × 新等级（百万美元），民意 +3。可以连升，nsp.11 只弹一次。
  - 任务经验 NSP_tier_mission_xp：近地 5、极地 6、交会和地球静止 8、逃逸 10、地月转移 12，载人再 +3，由 nsp.1 调用，立即判定升级。
  - 老存档迁移（flag NSP_tier_v2）：等级保留，门槛按新曲线重设，进度截到门槛以内。
- NSP_rd_unlock_effects.txt：NSP_tech_tier_check 改为调用 NSP_tier_levelup；NSP_rd_daily 末尾加 NSP_tier_refresh。
- NSP_rd_effects.txt（NSP_rd_recalc）：研发工期 × 100 / (100 + 研发速度加成)，开工时锁进 deff，进行中的项目不受影响。
- NSP_space_effects.txt：火箭可靠性加上 NSP_tier_rel；NSP_init 改为 tier 2、0/50。
- NSP_rd_zdebug_effects.txt：DEBUG 一键完成也走新曲线。
- 等级名称（GetNSPTierName）：1 探空火箭、2 亚轨道飞行、3 近地轨道、4 轨道交会、5 长期驻留、6 地月空间、7 登月、8 月面驻留、9 空间站、10 行星际、11 级起为深空。
- 改动的 loc：标题改成「太空科技 · 等级名」；NSP_TECH_TT 显示当前加成和下一级奖励；_D 层写来源、公式、里程碑；nsp.11 写本次奖励和当前加成。
- 备份：work/r86/bak/。
- 待测：新开局显示 2 级 0/50「亚轨道飞行」；研发完成后升级只弹一次事件；R&D 工期是否按加成缩短；规划器火箭可靠性是否 +1/级；老存档读档后门槛变成 30+10×等级；到 4 级研发槽 +1。

---

## 2026-10-22 · 第 85 轮（续）· 地图地标改成发射场，同一发射场一次只能发射一次
- 用户要求：地图上的地标改成发射场，解锁了才显示；一个发射场同一时间只能发射一次，要等上一次发射完。
- interface/NSP_space.gui：注释掉 6 个跟踪站 NSP_st_*，新增 8 个 NSP_lsite_0..7，下标同规划器发射场（0 CCAFS、1 VAFB、2 WFF、3 PMRF、4 WSMR、5 KSC、6 约翰斯顿、7 波克平原）。坐标按等距圆柱投影算，肯尼迪东移、沃洛普斯略南移，避免东海岸三个重叠。
- 新贴图 gfx/interface/NSP/nsp_lsite_marker.dds：16×16，2 帧（1 空闲青色、2 占用琥珀）。由 tools/gen_lsite_marker.py 生成，可重跑。GFX 是 GFX_NSP_lsite_marker。
- 显示条件 NSP_lsite_k_visible：地球视图，且 NSP_site_unl^k = 1。帧取 NSP_f_lsite_k。
- 新 scripted trigger NSP_site_busy（t_S）：本国进行中任务里有从该场发射、NSP_m_phase < 5 的，就算占用。从规划到「发射」阶段结束都占着，升空进入在轨阶段就空出来。没有发射场记录的老任务不算占用。
- NSP_site_allowed 新增条件 NSP_TT_SITE_BUSY。因此占用的发射场在规划器里点不了，开始任务按钮也会拦下，发射场行 tooltip 多一条 GetNSPCT_BUSY。
- 新 effect NSP_lsite_update：刷新 8 个帧变量，每日结算、开任务、重置规划器时调用。新 effect NSP_pick_free_site：重置规划器时卡角被占，就自动换成第一个空闲的已解锁发射场。
- tooltip 分两层：NSP_LSITE_TT_k 显示名称和状态，_D 显示发射场介绍（复用 NSP_SITE_DESC_k）和占用规则。
- 备份：work/r85/bak2/。
- 待测：开局只显示卡角、范登堡、沃洛普斯、白沙 4 个标记（r56 开局已解锁）；开一个卡角任务后标记变琥珀，规划器里卡角变灰；任务过了发射阶段后标记变回青色、卡角可以再选；研发 39 号复合体后肯尼迪标记出现。

---

## 2026-10-22 · 第 85 轮 · 1962 开局科技
- 用户要求：游戏 1962 年开局，给一些开局就有的科技。
- 新文件 common/scripted_effects/NSP_rd_r85_effects.txt：NSP_rd_start_1962，一次性（flag NSP_r85_start），新开局和老存档都生效。
- 开局完成的 14 项：红石 MRLV、宇宙神 LV-3B、H-1 改进型、水星飞船、水星加压服、镀铝尼龙加压层、海上回收、烧蚀防热罩、遥测网、先锋号、TIROS、LC-14、水星控制中心、马歇尔试车台。加上 r56 的沃洛普斯、范登堡、白沙。
- 效果：开局就能用红石、宇宙神 LV-3B、水星飞船、TIROS，开放近地轨道，另有若干可靠性和工期加成。
- 只改状态和进度，不加太空科技，不发一次性拨款和民意，以免开局连续升级、弹事件。
- 没给的：阿金纳（会直接解锁交会目的地）、双子星、LC-19、徘徊者。
- NSP_rd_unlock_effects.txt：NSP_rd_apply_unlocks 开头手加一行 NSP_rd_start_1962 = yes，放在按状态重算解锁之前，重新生成时要保留。
- 备份：work/r85/bak/。
- 待测：新开局 R&D 里这 14 项是绿色已完成；双子星、宇宙神-阿金纳等后续项可研发；规划器能选水星 + 宇宙神 + 近地轨道；老存档读档后补齐。

---

## 2026-10-22 · 第 84 轮 · 去掉 R&D 当前时代橙框
- 用户要求：科技树里框住当前年代列的琥珀橙竖框去掉。
- 改动（按退役规范注释保留，未删除）：
  - interface/NSP_rd.gui：NSP_rd_era_box_0..7 共 8 个 iconType 注释掉，标记 # @ retired-20261022。
  - interface/NSP_rd.gfx：GFX_NSP_rd_era_box 注释掉；nsp_rd_era_box.dds 移到 work/r84/quarantine/。
  - common/scripted_guis/NSP_space_rd_guis.txt：对应 8 条 _visible 注释掉。
- NSP_rd_era_now 变量仍保留，研发时代限制逻辑还在用它，只是不再显示框。
- 备份：work/r84/bak/。
- 待测：R&D 不再出现橙框；error.log 无 GFX_NSP_rd_era_box / NSP_rd_era_box 相关报错。

---

## 2026-10-22 · 第 83 轮 · 长 tooltip 拆成 pdx_tooltip + pdx_tooltip_delayed 两层
- 用户要求：tooltip 改成两层，悬停先出短 tt，停留后再出详细说明（行星 tt 已有先例 NSP_TT_*_D）。
- 拆分规则：第一层只放标题和当前数值；第二层（_D）放规则、公式、背景文字，统一用 §g。
- 改动的 8 组（interface/NSP_space.gui 共 28 处加 pdx_tooltip_delayed，loc 新增 8 个 _D 键）：
  - NSP_DIRECTOR_TT：姓名 + 分隔线 + 现任职务 → _D 放人物介绍
  - NSP_BUDGET_TT：余额、历史最高、下次/上次拨款 → _D 放账户与拨款规则
  - NSP_TECH_TT：等级、进度、奖励 → _D 放升级规则
  - NSP_POPULARITY_TT：支持度数值 → _D 放增减规则
  - NSP_SUPPORT_TT：国会支持、下次拨款 → _D 放拨款公式
  - NSP_PERF_TT / NSP_REL_TT / NSP_COST_TT（规划器 3 个统计块，每块 7 处）：一句话说明 → _D 放计算公式
- 短 tt（ESC、翻页等）、动态拼接的 tt（SITE_ROW、START、SAT 等）没动。
- 待测：两层显示正常；_D 里的 [?var] 数值能刷新；§ 颜色没有串色。

---

## 2026-10-22 · 第 82 轮 · 局长头像加简介 tooltip
- 用户要求：主页局长头像仿 TNO 领导人肖像，鼠标悬停显示人物介绍。
- 改动：
  - interface/NSP_space.gui：NSP_director_portrait 加 pdx_tooltip = "NSP_DIRECTOR_TT"；NSP_director_name 去掉 alwaystransparent，也挂同一个 tooltip。
  - localisation/simp_chinese/NSP_space_l_simp_chinese.yml：新增 NSP_DIRECTOR_TT。格式照 TNO 领导人 tt：§Y 姓名、§g 分隔线，正文分 3 段，最后一行 §g 写现任职务。文案按 TNO 世界观改写（德国火箭领先、冷战）。
- 注：局长目前是静态的（韦伯）。以后要换人，就把 NSP_DIRECTOR_NAME / TT 改成 scripted_loc。
- 待测：悬停头像和名字都能弹出 tt，换行和颜色正常；头像上方的 NSP_director_frame（alwaystransparent）不挡悬停。

---

## 2026-10-22 · 第 81b 轮 · 帮助遮罩去掉青框（取代 r81 的原生分辨率方案）
- 用户反馈：发糊主要是青框边缘明显，暗底边缘发虚看不出，不要青框即可。
- 改动：
  - nsp_help_overlay.dds 恢复 r69 的半分辨率 550x359/帧（共 3850x359），gui 仍为 scale = 2；青框像素全部改成暗底色 (2,8,10,190)。
  - interface/NSP_help.gui、NSP_help.gfx 回到 r80 版本（只改了 gfx 注释）。
  - 脚本 tools/fix_help_overlay_nocyan.py（只读 work/r81/bak 原图，可重复运行）。r81 的 7700 宽贴图作废。
- 待测：各页挖空区域位置正确、边缘无青色；error.log 无 GFX_NSP_help_overlay 报错。

---

## 2026-10-22 · 第 80 轮 · 研发卡片换成 TNO 科技边框
- 依据：用户给的 TNO 科技边框（Antarctica_Decision_GUI_AAA_Technology_*，大 239×117、小 72×72；研发中的版本带箭头动画）。按要求改名后放入：
  - nsp_rd_frame_l.dds / nsp_rd_frame_s.dds：4 帧，依次是不可研发 / 可研发 / 研发中静帧 / 已研发，帧号 = t_rdf = state+1；
  - nsp_rd_frame_l_anim.dds（8 帧）/ nsp_rd_frame_s_anim.dds（6 帧）：研发中用的 frameAnimated，looping = yes，8 / 6 fps。
- 新元素：NSP_rdc_frame / NSP_rdc_frame_r（大卡）、NSP_rdc_sframe / NSP_rdc_sframe_r（小卡），叠在科技图上；state = 2 时显示 _r 动画版。
- 布局：
  - 大卡底板、科技图、边框都在 (10,12)，范围 x10..248、y12..128；
  - 小卡在 (10,34)，72×72；
  - 选中框按新尺寸重拼角标（247×125 在 (6,8)，80×80 在 (6,30)）；
  - 进度条在 (16,105) / (16,98)。
- nsp_rd_card / nsp_rd_scard 改成纯底色（只当点击区和衬底），边框交给 TNO 贴图。
- 连线 gen_rd_links.py：
  - H 段从父卡右缘 x249 起；
  - L 竖干从 y129 / y11 起，lu 帧顶改为 -288；
  - tail 改成 x82..248。
- 科技图 tools/fix_rd_art_corner.py（只跑一次，原图备份在 work/r80/bak/art/）：给右上状态方块让位，第一行注释左移 16px，自带竖线 y<24 那段擦掉。
- 小科技图标重出为 72×72；标签 ≤ 46px，避开状态方块，GEMINI CPU / TEST STAND / AUTO DOCK / EVA TOOLS 缩写成 GEM CPU / TEST STD / AUTODOCK / EVA TOOL。
- 备份：work/r80/bak/。离线预览：work/r80/preview_*.png。
- 待测：
  - 研发中的边框动画会不会循环播放（尤其 gridbox 条目复用之后）；
  - 连线和边框是否对齐；
  - 点击和 tooltip。

## 2026-10-22 · 第 79 轮 · 小科技方卡（照 TNO 小科技：只给加成、不解锁东西）
- 依据：用户发的 TNO 小科技截图和 5 张 72×72 图标。小科技是方卡，左上角一个短英文标签，中间是线稿。
- 名单：35 项只给加成、什么都不解锁的科技改成方卡，效果和前置都不动：
  8、18、21、22、24、25、27、28、33、34、35、39、44、46、50、51、54、56、57、58、59、62、69、70、74、75、76、77、78、79、80、81、82、84、85。
  - 解锁火箭 / 载荷 / 目的地 / 修正 / 发射场 / 允许发射 / 研发槽的科技保持大卡。
  - 名义上的大里程碑（15、19、20、49、60、63–67、71、73）也保持大卡。
- 方卡：74×74，放在 (10,33)，竖直居中，中线和大卡一样在 y69.5，所以连线的几何不用改。
  - 新元素：NSP_rdc_sbg（按钮，tooltip 和点击都和大卡一样）、NSP_rdc_sart、NSP_rdc_ssel、NSP_rdc_sprog、NSP_rdc_ltail。
  - 大卡元素的 _visible 加了 NSP_rd_small^v = 0，方卡元素是 = 1。
- 贴图：
  - nsp_rd_scard（照大卡边框配色，4 帧）、nsp_rd_ssel（照大卡选中框的角标）、nsp_rd_sprog（大卡进度条缩成 60×3）；
  - nsp_rd_small（35 帧 70×70，tools/gen_rd_small.py 生成：从大卡科技图中间自动裁出线稿，加粗后缩小，再加 VT323 标签）；
  - nsp_rdl_tail（gen_rd_links.py 新增）。
- 数据：NSP_rd_small_init（在 NSP_rd_aa_links_effects.txt 里）每次 recalc 按字面表重写 NSP_rd_small / NSP_rd_sart，老存档不需要迁移。
- 连线：
  - 父项目是小科技时不走 L 形，因为方卡下面没有底边可以落线，改走 Z 形；
  - 方卡右缘 x84 到格位右缘 x252 补一段出线 NSP_rd_ltail，颜色取它所有子项目里状态最高的那条。
- 改名单要两处一起改：gen_rd_small.py 的 SMALL 和 NSP_rd_small_init。
- 备份：work/r79/bak/。离线预览：work/r79/preview_*.png。
- 待测：
  - 方卡显示和点击；
  - 选中框和研发进度条；
  - 方卡的 tooltip；
  - 小科技后面的出线有没有接上；
  - error.log 里没有 NSP_rd_small / sart / ltail 相关的报错。

## 2026-10-22 · 第 78b 轮 · 研发树连线改成 TNO 科技树样式
- 依据：用户发的 TNO 科技树录屏。从里面看到四点：
  - 2px 实线，没有端点方块；
  - 线的颜色跟着它通向的科技走：已完成绿 (139,228,147)，可研发青 (97,192,187)，锁定红 (212,133,137)。线都是从录屏里取的色；
  - 同一行的科技直接从中线连过去；
  - 分叉时从父卡底边（或顶边）、靠右侧大约 82% 的位置竖直落下，再横着进子卡左边中线，几张子卡共用同一根竖干。
- 改动：
  - tools/gen_rd_links.py 重写：4 种颜色，研发中用黄 (220,218,80)；去掉端点；新增 L 形贴图 nsp_rdl_lu.dds / nsp_rdl_ld.dds（各 13 帧）。h / vu 各 17 帧，vd 13 帧。
  - NSP_rd_links_calc 改了两处：
    - 颜色改成子项目状态 NSP_rd_state^p；
    - dx = 1、dy ≠ 0 时走 L 形（LU / LD）。如果父列在父行和子行之间（含子行）有卡挡路，就退回 Z 形。用 NSP_rd_index 查格位。
  - 卡片条目新增 NSP_rdc_l{1,2}lu / ld，共 22 个连线 icon；properties 同步。
- r78 的版本备份在 work/r78/bak/gen_rd_links_r78.py。
- 离线预览：work/r78/preview_r78b.png（6 个分类，状态是随机设的）。
- 待测：同 r78，另外看 L 形竖干落在父卡底边的位置，以及线和卡片边框颜色是否协调。

## 2026-10-22 · 第 78 轮 · 研发树动态连线（取代预渲染连线图）
- 原因：连线原来是一张 6 帧的整图 nsp_rd_links.dds（8.7MB），也找不到生成它的脚本，一改前置就和连线对不上。
- 做法：每张卡片在自己的条目里画「从 req1 / req2 连过来」的线；帧由 effect 预算进数组，properties 只读。
  - 新 effect：common/scripted_effects/NSP_rd_aa_links_effects.txt 里的 NSP_rd_links_calc，在 NSP_rd_recalc 末尾调用。
    - 数组 NSP_rd_l{1,2}h0..6 和 NSP_rd_l{1,2}vu / vd，下标为项目 id。
  - 卡片条目 NSP_rd_card_entry 最前面加了 18 个 iconType：NSP_rdc_l{1,2}h0..6、NSP_rdc_l{1,2}vu / vd。
    - h 是父卡所在行的水平段，按 dy 各一个元素；vu / vd 是拐点竖线加进卡短线。
  - 贴图由 tools/gen_rd_links.py 生成（可重跑）：nsp_rdl_h.dds（13 帧）、nsp_rdl_vu.dds（13 帧）、nsp_rdl_vd.dds（10 帧）。2px 线，端点带小方块。
  - 颜色跟着父项目状态走：未完成是原来的青 (70,160,154)，研发中是黄 (220,218,80)，已完成是绿 (120,220,90)。
  - 支持范围：dx = 子列 - 父列为 1..4，dy = 子行 - 父行为 -3..3。超出范围不画线。目前的数据最多是 dx 3、dy ±2。
- 退役：GFX_NSP_rd_links（gfx 注释保留）、NSP_rd_links 图标及其 property。nsp_rd_links.dds 移到 work/r78/quarantine/。
- 以后改前置：只改 NSP_rd_req1 / req2（NSP_rd_init 或 r53 补项），连线自动跟着变，不用改图。
- 备份：work/r78/bak/。
- 待测：
  - 6 个分类的连线位置和原来一致（离线预览已对过运载火箭、地面设施两类）；
  - 研究完成后连线变绿，开始研发变黄；
  - 卡片点击不受透明连线图标影响；
  - error.log 里没有 NSP_rd_l* 越界。

## 2026-10-22 · 第 77 轮 · 科技树迭代：宇航员装备线落地 + 数值顺链
- 原因：生命保障线 76–86 的宇航员装备大多只写「（预留）」加载人可靠性 +1%，研究了也几乎没感觉；另有两项比前置还便宜、还快。
- 新文件 common/scripted_effects/NSP_rd_r77_effects.txt（在 NSP_rd_r52_rel / _cost / _success 末尾调用，按 state 现算，幂等）：
  - 78 面窗：带舱外活动系统时载荷可靠性 +2
  - 79 LCG：阿波罗地月转移载荷可靠性 +2
  - 80 PLSS：阿波罗地月转移载荷可靠性 +3
  - 81 β 布：阿波罗载荷可靠性 +3
  - 82 EMU：天空实验室载荷可靠性 +5
  - 84 舱外工具组：带舱外活动系统时任务成本 ×0.95
  - 76 A7LB：阿波罗地月转移成功，民意 +2
  - 85 地质工具：阿波罗地月转移成功，科研 +50
  - 原有的载人可靠性 +1% 被动加成不变。
- NSP_rd_l_simp_chinese.yml：NSP_RD_UNLOCK_76、78–86 改写，去掉「（预留）」；80 原文「A7L 前置」与实际前置（24 + 27）不符，已删。
- NSP_rd_init 数值顺链：
  - 20 月球车：tech 5→9，工期 360→480（前置登月舱是 8 / 420）；
  - 36 惯性测量单元：tech 5→7，工期 300→360（前置制导计算机是 6 / 330）。
  - 只对新开局生效（老存档的数组不重建）。
- 没改前置关系：nsp_rd_links.dds 是预渲染的连线图，改前置就会和连线对不上。
- ⚠ 不要再跑旧的 nsp_r35/gen.py，它会覆盖 NSP_RD_UNLOCK_* 文案。
- 备份：work/r77/bak/。
- 待测：规划器选阿波罗 + 地月转移，研究 79 / 80 / 81 前后可靠性的差值；带舱外活动系统时，研究 84 后成本少 5%。

---

## 2026-10-22 · 第 76 轮 · 清理冗余代码
- 删除死代码（全仓库没有任何引用）：
  - scripted effect：NSP_rd_weekly（r37 起改为每日，已不调用）、NSP_seed_mission（r49b 起没有开局任务）；
  - scripted trigger：NSP_program_unlocked、NSP_rd_has_*（16 个宇航员装备判定，r17 预留后一直没用）；
  - NSP_init 里 NSP_prog_budget / NSP_prog_budget_max 的初始化（r36 起统一预算）。NSP_clear_arrays 里的 clear 保留，用于清理老存档。
  - sprite：GFX_NSP3D_focus_<行星> ×8（NSP_space.gfx）、GFX_NSP3D_focusout_<行星>(_b) ×16（NSP_focus_v22.gfx），r31 起聚焦动画已改用 focusbt / focusoutbt；
  - 随之删除不再被引用的 gfx/FX/nsp_focus.shader、nsp_focus_out.shader；
  - localisation/simp_chinese/NSP_anim_l_simp_chinese.yml（r27 A/B 切图实验遗留，把 GFX 名映射给自己）。
- 合并重复：r75 发射台「卡角发射场」判断原来写了两遍，合并为 scripted trigger NSP_pad_cape_mission（NSP_space_triggers.txt 末尾）。
- 体检结果：BOM、括号、GFX 引用、贴图文件、scripted gui 元素名、scripted localisation、loc key 都没有问题。
- 保留：814 个 NSP_ss_* 点击行是生成的，scripted gui 不支持通配，无法合并。
- 备份：work/r76/bak/（含两个 shader）。
- 待测：error.log 里没有 missing sprite / shader；行星聚焦进入和退出动画正常。

## 2026-10-22 · 第 75 轮 · 任务失败时地图发射台自动播放爆炸
- 原因：r48 做的两种爆炸动画一直只能用调试决议触发，实际任务失败时发射台照常播放成功发射。
- NSP_space_effects.txt：
  - 新增 NSP_preroll_mission：任务进入「发射」阶段（ph = 4）时预先掷出成败，存进 NSP_m_roll / NSP_m_fkind 两个新数组（老存档按 nsp_mid 补 -1 / 0）。
  - 失败类型：25% 台上爆炸（fkind 3）、35% 空中爆炸（4）、40% 入轨后失败（5，地图正常发射）。
  - NSP_resolve_mission 沿用预掷的 roll，结局和动画一致；没有预掷记录的老任务照旧现场掷。
  - NSP_clear_missions 同时清空两个新数组。
  - game.log 会输出「NSP preroll: mission … roll … rel … kind …」。
- NSP_launchpad_effects.txt：NSP_pad_update_auto 在发射阶段按 fkind 选模式 2 / 3 / 4；待发射和发射都只看卡角发射的任务（发射场 0 CCAFS、5 KSC、老任务 -1），范登堡等地发射不再让卡角发射台动。
- 备份：work/r75/bak/。
- 待测：
  - 把可靠性压低后发射，game.log 的 kind 和地图动画对应；
  - 爆炸后进入下一阶段，发射台回到空台；
  - 失败事件 nsp.2 仍在任务结束时弹出。

## 2026-10-22 · 第 74g 轮 · 卫星去像素化
- 卫星图改为 8 倍超采样绘制，再用 Lanczos 缩小到 25x11（含 1px 透明边），仍放在 (2,1)。
  - 细节：电池板渐变、栅格和反光，金箔明暗起伏，柔和暗描边。
- nsp_sat_bt.shader：最近邻采样改为手动双线性（4 次采样，预乘 alpha），旋转时边缘平滑，不再有台阶。
- sat_data.py 的 _render / sim 已同步修改；备份为 work/r74/bak/*.r74f.*。
- 待测：
  - shader 能否编译（新增 4 次 tex2D）；
  - 卫星边缘是否平滑；
  - 图集角落没有误显示。

---

## 2026-10-22 · 第 74f 轮 · 卫星加 1px 黑描边
- sat_data.py 里新增 _outline：在 19x7 图外围加一圈 8 邻域黑描边，图集变为 21x9，仍放在 (2,1)。
- nsp_sat_bt.shader 的采样常量改为 10.5 / 4.5，范围 su 2..22、sv 1..9。
- 备份：work/r74/bak/*.r74e.*。
- 待测：卫星在亮月面和地球上的轮廓是否清楚；横向 ±4.5px 仍在轨道带（6px）内。

---

## 2026-10-22 · 第 74e 轮 · 轨道卫星贴图写实化
- 卫星图集从 15x5 改为 19x7。
  - 电池板：深蓝，带灰框、栅格和高光。
  - 中间：桁架连接金色多层隔热本体，本体有明暗。
  - 上方天线，下方发动机。
- 青色光晕改为微弱的中性反光：强度从 0.35 降到 0.12，范围缩小。
- 文件：
  - work/r64/sat_data.py：改了 SPRITE 和 sim；已重跑，重新生成 nsp3d_satl/sats_1..10.dds；
  - gfx/FX/nsp_sat_bt.shader：图集采样范围改为 su 2..20、sv 1..7。
  - 备份在 work/r74/bak/（sat_data.py、shader、sat/*.dds）。
- 待测：
  - 卫星显示和朝向是否正常；
  - 图集角落没有误显示（alpha 100 < 128，按理会被丢弃）；
  - 选中轨道线不受影响。

---

## 2026-10-22 · 第 74d 轮 · 「国家太空计划」改称「美国航空航天局」
- NSP_TITLE_HOME 和 NSP_TOPBAR_TT 改为「美国航空航天局」。
- NSP_HELP_D_0 改为「美国航空航天局（NASA）的指挥中心」。
- 泛指的「太空计划」保留，例如民意说明、地球描述。
- 待测：主窗标题长度是否溢出标题栏。

---

## 2026-10-22 · 第 74c 轮 · tooltip 优化：修正 / 发射场 / 启动条件
- 文件：NSP_space_l_simp_chinese.yml（备份在 work/r74/bak/*.r74b）。
- 修正说明 NSP_MOD_DESC_0..19：每项效果单独一行，写成「§F标签：§! 值」；说明句用 §g，放在最前；金额去掉 $$。
- NSP_PALETTE_TT / NSP_SLOT_TT / NSP_SITE_ROW_TT：
  - 标题改为 §W；
  - 原来的「------」改为空行分段。
- NSP_SITE_DESC_0..7：
  - 简介用 §g；
  - Delta-V 需求逐行列出；
  - 原来「不能发射重型火箭 · 成本 · 工期」挤在一行，现在拆成三行。
- 启动 / 选择条件：
  - 标题改为「还不能启动任务」「不能选择」，去掉冒号；
  - 每条原因写成「§R·§! §F原因：§! 值」，处理建议另起一行、缩进，用 §g；
  - 「可以启动」时成功率、成本、余量各占一行。
- 待测：TT 换行和缩进是否正常；中文全角冒号显示是否正常。

---

## 2026-10-22 · 第 74b 轮 · 时间线滚动条改为原版
- 删除左侧自绘的双向箭头装饰。
- 行区包进 containerWindowType NSP_tl_scroll，挂原版滚动条 verticalScrollbar = "right_vertical_slider"，与 R&D 树区同款，放在右侧。
- 行区左移到 x=8，列分隔线改到 x=138；表头和页脚文字随之对齐。
- art.py 已重跑，生成 nsp_tl_table 和 nsp_timeline_row。
- 待测：
  - 6 行刚好放满（162/162），原版滚动条在不需要滚动时可能自动隐藏；
  - dynamic list 嵌在滚动容器里能否正常填充。

---

## 2026-10-22 · 第 74 轮 · 计划任务时间线重构（按用户参考图 Planned Mission Timeline）
- 推翻 r73 的甘特条，改为表格式。
- 结构：
  - 标题行；
  - 表头「任务阶段 ┊ 完成」；
  - 6 行彩框，每行三格：序号格 | 阶段名 | 第 X 天（累计）；
  - 页脚「预计完成 ┊ 第 N 天」；
  - 左侧是青色双向箭头装饰，带珊瑚红游标。
- 美术：work/r74/art.py。
  - nsp_tl_table.dds（260×266，表格线和箭头）为新文件。
  - nsp_timeline_row.dds 改为 222×24、6 帧，6 色描边：黄 / 绿 / 青 / 米白 / 橙 / 珊瑚红。
- 文字配色：序号和阶段名按行着色，分别为 §Y §G §D §W §O §R，对应 NSP_TL_N_i / NSP_TL_NAME_i，由 GetNSPTLNum / GetNSPTLName 取用。
- 删除：
  - GFX_NSP_tl_gantt / _mask 及其贴图，gen_style.py 已同步去掉；
  - 本地化 NSP_IDX_0..5、NSP_TL_COL_BAR、NSP_TL_AXIS_L/R；
  - defined_text GetNSPIdxRow。
- scripted gui：NSP_tl_row_visible 只算 t_tlc = v + 1；properties 中 NSP_tl_row 的 frame 取 t_tlc。
- 备份：work/r74/bak/。
- 待测：
  - 6 行颜色和帧是否对应；
  - §D 在 TNO 下是不是偏青蓝（不合适再换）；
  - 行 tooltip 是否正常。

---

## 2026-10-22 · 第 73 轮 · 规划器「计划任务时间线」改版
- 甘特条从 70×8 / 15 帧（每帧 5px，分段竖纹）改为 100×10 / 50 帧（每帧 2px，实心黄条）。
  - 底槽带 25% / 50% / 75% 刻度；前序阶段用中间 2px 暗青细线表示。
  - 生成：work/style/gen_style.py 的 gantt() / gantt_mask()，NSP_style.gfx 的 noOfFrames 由 15 改为 50。
  - gen_style.py 去掉了 r68 已删的 nsp_tab_view，重跑不会再把它生成回来。
- NSP_tl_row_visible 帧公式：×14 改为 ×49，上限 15 改为 50。
- 布局：
  - 表头改为「阶段 / 时间轴 / 工期」；
  - 甘特轨在行内 x = 68；
  - 工期列的数字用 §Y，「天」用 §g；
  - 时间轴下方新增轴标 D0 … D<总天数>（NSP_tl_axis_l / r）；
  - 分隔线和总工期整体下移 12px。
- 行 tooltip 改为：阶段名、工期、第 X 天 → 第 Y 天、图例。
  - 新增数组 NSP_calc_phase_start，在 recalc_planner 里与 phase_days 同步写入。
- 预览器 _tl_cb 同步改为 ×49。
- 备份：work/r73/bak/。
- 待测：
  - 6 行黄条位置与工期比例是否对得上；
  - 行 tooltip 里的起止天数；
  - 底部总工期是否压到面板边框。

---

## 2026-10-22 · 第 72 轮 · 优化轨道行、太空科技、预算、国会的 tooltip
- 轨道行：tooltip 由公用的 NSP_ORBIT_TT 改为每行一个，NSP_ORBIT_TIP_0..2。
  - 内容：标题（轨道名）、计入哪些目的地（NSP_ORBIT_DESC_<view>_<row>）、相关任务数，以及操作提示。
  - 操作提示按当前筛选状态切换：筛选中显示「再次点击取消」。defined_text 为 GetNSPOrbitDesc/Act0..2，写在 NSP_space_scripted_loc.txt。
- 以下三个 tooltip 都改为「标题 / 数值 / 说明」分段，标签用 §F、数值用 §Y/§G、说明用 §g：
  - NSP_TECH_TT：标题显示当前等级。
  - NSP_BUDGET_TT：上次拨款为 0 时显示「尚未拨款」（GetNSPPayLast）。
  - NSP_SUPPORT_TT
- 修复：tooltip 里 `$$` 在实机会原样显示成「$$」，这三个 TT 已去掉美元符号，改成「9.80B」。
- 修复：开局第一周结算前，NSP_income 未计算，导致「下次拨款」显示 +0.00B。现在 NSP_budget_disp 会按当前国会支持现算。
- 删除 key：NSP_ORBIT_TT。
- 备份：work/r72/bak/。tooltip 示意图用 work/r72/tt_preview.py 生成（只渲染色码，不代表游戏实际排版）。
- 待测：
  - 四个 tooltip 的换行和颜色；
  - 轨道行筛选前后，提示是否切换；
  - 开局时「下次拨款」不再是 0。

---

## 2026-10-22 · 第 71 轮 · 规划器箭头到头置灰；默认局长肖像替换
- 改动 1：载荷、火箭的左右切换改为到头即止，不再循环回绕。
  - NSP_cycle_payload / NSP_cycle_vehicle（NSP_space_effects.txt）按 step 方向找下一个已解锁项；找不到就不动。
  - 新增 4 个 trigger：NSP_payload_has_prev/next、NSP_vehicle_has_prev/next（NSP_space_triggers.txt），用 any_of 遍历解锁数组，比较下标。
  - 显示：亮箭头的 _visible 和 _click_enabled 都用上面的 trigger；同一位置下面垫一张灰色箭头 iconType（NSP_*_off，贴图 nsp_arrow_*_off.dds）。没有下一项时亮箭头隐藏，露出灰箭头。
- 改动 2：默认局长肖像 nsp_director_generic.dds 换成用户给的图，156x210，尺寸不变。
- 备份：work/r71/bak/。
- 待测：
  - 开局只有双子星和泰坦时，载荷、火箭的两侧箭头都是灰的；
  - 研发解锁后，对应方向的箭头变亮；
  - 选到最后一项时，右箭头变灰。

---

## 2026-10-22 · 第 70 轮 · 帮助遮罩内缩；主窗关闭键加 ESC
- 改动 1：遮罩不再压住外窗的青色边框。
  - 原因：r69 实机里遮罩盖满整个外窗。
  - 现在只盖 body 内框以内，四边各内缩 4px。
  - 文件：work/r69/art.py，nsp_help_overlay.dds 已重新生成。
- 改动 2：主窗关闭按钮 NSP_close_button 加 shortcut = "ESCAPE"，tooltip 改为「关闭（ESC）」。
  - 帮助开着时，按 ESC 或点红 X 只关帮助；再按一次才关主窗（NSP_space_guis.txt）。
  - 帮助自己的 × 按钮去掉了 ESC，避免两个按钮抢同一个键。
- 待测：
  - 主页按 ESC 能关主窗；
  - 帮助开着时，第一次按 ESC 只关帮助；
  - 规划器里按 ESC 仍然是返回（NSP_back_button 原本就有 ESC）。

---

## 2026-10-22 · 第 69 轮 · i 按钮改为 Kartenhaus 式帮助层
- 用户要求仿照 TNO 的 Kartenhaus_Help 做帮助层。
- 新增文件：
  - interface/NSP_help.gui、NSP_help.gfx
  - common/scripted_guis/NSP_zz_help_guis.txt：文件名带 zz，保证最后注册、叠在最上层
  - common/scripted_effects/NSP_help_effects.txt
  - common/scripted_localisation/NSP_help_sl.txt
  - localisation/simp_chinese/NSP_help_l_simp_chinese.yml
  - gfx/interface/NSP/help/*.dds
- 结构：
  - NSP_help_window 挂在 NSP_home_window 上，visible 条件：NSP_help_arr 非空，且规划器、R&D 都没打开。
  - 遮罩 GFX_NSP_help_overlay：7 帧，半分辨率，显示时 scale 2；frame = 页码 + 1，只挖空当前页讲解的区域，边上加青框。
  - 假 gridbox 由 NSP_help_arr 驱动，数组只有 1 个元素；entry_container = "NSP_help_box_[GetNSPHelpBox]"，每页一个容器，所以对话框能换位置。
- 交互：
  - 对话框：‹ › 翻页、页码、≡ 回目录、× 关闭（ESC）。
  - 第 0 页是目录，有 6 个链接按钮。
  - i 按钮 = NSP_help_toggle。关闭主窗、打开规划器、打开 R&D 时都会关掉帮助。
- 删除：事件 nsp.100 及其本地化。
- 生成脚本：
  - work/r69/gen.py 生成结构，work/r69/art.py 生成遮罩和按钮，work/r69/preview_help.py 生成预览。
  - 加页：两个脚本的 PAGES / BOXES 各追加一项，在本地化里补 NSP_HELP_T_n / D_n / IDX_n，重跑两个脚本。
- 备份：work/r69/bak/。
- ⚠ 实机待确认：
  - entry_container 名字里带 [defined_text] 能不能生效（Kartenhaus 同款写法）；
  - 帮助层是否叠在主页之上；
  - 遮罩的 scale = 2 是否生效；
  - ESC 会不会同时关掉主窗。

---

## 2026-10-22 · 第 68 轮 · 清理废弃的着色器、贴图、本地化和 gfx
- 用户要求删除不再使用的资源。
- 判定方法：脚本静态扫描，不算注释和 documentation。
  - 扫描范围：gui / gfx / txt / yml / shader / asset 的全部引用。
  - 动态拼接的 key（如 `KEY_[?x]` 这类前缀）按“已使用”处理，不删。
- 删除内容：
  - gfx 定义 47 个：
    - 旧 2D 行星图、hover 图、旧环图（NSP_orbit_v24 的 ring_*）、hit_24 / hit_40、focus_hit；
    - 旧 UI：民意 / 科技条、checkbox、director_frame、global_tab、tab_mc、tab_view / view2、tech_circle、start_button、orbit_row；
    - 自制滚动条 scroll_*、rd_cell。
  - 文件 60 个，共 13.4MB：
    - 对应的 dds；
    - 没有 sprite 引用的 nsp_map_lunar / solar、rd_art、rd_sb_*；
    - 着色器 nsp_planet.shader、nsp_ring.shader；
    - 空文件 interface/NSP_orbit_row.gfx。
  - 本地化 key 127 个：
    - OBJ_A/B*_TEXT、PROG_TAB_*_TT、RDC_NAME / NOTE*、RD_NOTE_0..93、SOV_*、5 个已废弃的测站 ST_*；
    - COST / PERF / REL_BODY、SUCCESS_TEXT、GTAB_CONFLICTS、OBJ_DONE / TODO。
  - defined_text 29 个：fin / fout 行星图、GetNSPObjA0..B2、RD 卡片名 / 备注 / 规格、SelReq1 / 2、RDTrack、SovietName。
  - NSP_space.gui 末尾注释掉的滚动条骨架。
- 备份：
  - 改动前的文件在 work/r68/bak/；
  - 删掉的文件按原路径放在 work/r68/bak/deleted/。
  - 扫描脚本没有保存，需要时可以重写。
- 待测：
  - 各页面贴图正常，error.log 里没有 missing sprite 或 missing texture；
  - 3D 聚焦动画正常；
  - R&D 卡片的文字和 tooltip 正常。

---

## 2026-10-22 · 第 67 轮 · 计划页签改为 dynamic_lists，支持任意数量计划
- 用户同意：以后计划会变多，页签不再写死。
- GUI：
  - 删掉 `NSP_prog_tab_0..6` 和 `NSP_prog_done_0..2`；
  - 新增 gridbox `NSP_prog_tab_grid`（7 格，每格 34x28）和条目 `NSP_ptab_entry`（按钮 `NSP_ptab` + 角标 `NSP_ptab_done`）。
- 列表：`NSP_prog_tabs_build` 在 recalc_home 里调用。
  - 计划数 = NSP_prog_unlocked 的长度。
  - 不足 6 个时补 -2（锁定占位），末尾加 -1（?）。
  - 总共不超过 7 格时全部显示；超过时分页：‹(-3) + 5 格 + ›(-4)，页码存在 NSP_prog_page / NSP_prog_pages。
- 触发器（NSP_space_triggers.txt）：
  - NSP_ptab_frame：帧号 = 图标×2+1，选中再 +1。图标：0 锁，1 ?，2 ‹，3 ›，4+p 计划 p；未解锁的计划显示锁。
  - NSP_ptab_enabled
  - NSP_ptab_is_done
- 效果：NSP_ptab_press 处理选中计划和翻页。
- tooltip：GetNSPPtabTT，按 v 分别显示计划名、未解锁、上一页 / 下一页、未知。
- 美术：work/r67/art.py 重排页签帧，现在共 14 帧。
- 新增计划 p 的步骤：
  1. NSP_seed_mission 里，给 NSP_prog_unlocked、NSP_prog_budget、NSP_prog_budget_max 各追加一项，NSP_obj_req / NSP_obj_prog 各追加两项；老存档要写迁移补长度。
  2. art.py 的 PROG_ICONS 里追加图标，gfx 的 noOfFrames 加 2。
  3. 本地化补 NSP_PROG_NAME_p、STARTED_p、BADGE_p、OBJ_DESC_(2p)、OBJ_DESC_(2p+1)。
- 预览器：新增 home_paged 状态，用 mock 数据画分页样式。
- 备份：work/r67/bak/。
- ⚠ 风险：defined_text 里用 `v` 和 `NSP_prog_unlocked^v`，dynamic list 条目的 tooltip 能不能读到 v，需要实机确认。
- 待测：
  - 三个计划切换正常；
  - 锁 / ? 不能点击；
  - 水星页签显示对勾；
  - tooltip 正常；
  - 调试时把 NSP_prog_unlocked 加到 9 项以上，检查翻页。

---

## 2026-10-22 · 第 66 轮 · 计划页签重绘 + 完成角标
- 用户要求：优化顶部 7 个计划页签。
- 美术（work/r66/art.py，原图在 work/r66/bak/）：
  - nsp_program_tabs.dds 重绘。帧号不变：1..5 普通，6..10 选中。
  - 普通状态：暗青灰边框，图标降亮。原来是红框，在 TNO 色表里红色表示「坏」，和「未选中」的意思冲突。
  - 选中状态：亮青双线边框、背景提亮、底部加一条高亮条。
  - 锁定 / 未知：灰色虚线框，图标也改成灰色。
- 新增 nsp_prog_done.dds（10x10 绿色对勾）：`NSP_prog_done_0..2` 叠在页签右上角，alwaystransparent，不挡点击。
  - 显示条件 NSP_prog_done_k_visible：两个目标的 prog 都不小于 req。
  - 开局水星计划就是已完成状态，会显示对勾。
- 锁定 / 未知页签的 tooltip 标题从 §R 改成 §F。
- 待测：
  - 只有完成的计划显示对勾；
  - 对勾不挡页签点击；
  - 悬停高亮正常。

---

## 2026-10-22 · 第 65 轮 · 「进行中的计划」目标卡改版
- 用户要求：优化左栏目标卡的 UI。原来三个大勾选框加三行「已完成 / 未完成」，占地方，信息也少。
- 新布局：每张卡 238x124。
  - 第一行：左边「目标 A / B」，右边状态（§Y进行中§! 2/3，或 §G已达成§!）；
  - 下面是分段进度条（GFX_NSP_obj_bar，218x12，9 帧，带 tooltip）；
  - 再下面是描述。
- 预算行上移约 7px。
- 改动文件：
  - `NSP_space.gui`：删除 `NSP_obj_[ab][0-2]_box/text`；新增 `NSP_obj_[ab]_tag/stat/bar`。
  - `NSP_space_guis.txt`：删除对应的 visible 触发器；properties 改为 `NSP_obj_[ab]_bar = { frame = NSP_f_obj_[ab]_bar }`。
  - `NSP_space_effects.txt`（recalc_home）：算 NSP_obj_[ab]_done / _req（done 不超过 req），帧号 = base(总数) + done + 1，base 为 1→0、2→2、3→5。
  - scripted_loc：GetNSPObjStatA / B。
  - 本地化：NSP_OBJ_TAG_* / STAT_* / BAR_*_TT；NSP_PROG_MET 改为「目标达成 X/2」。
  - 美术：work/r65/art.py → nsp_obj_bar.dds。GFX_NSP_checkbox 保留，但已不再使用。
- ⚠ 如果目标次数超过 3，要给进度条加帧。
- 待测：
  - 切换三个计划时，进度条段数是否正确（水星 2/1、双子星 3/2、阿波罗 1/2）；
  - 完成后是否显示「已达成」；
  - tooltip 是否正常。

---

## 2026-10-22 · 第 64 轮 · 卫星从光点改成像素卫星
- 用户反馈：卫星只是一个光点。
- 改动：
  - `work/r64/sat_data.py` 重新生成 20 张轨道数据贴图，文件名和尺寸都不变。
    - B 通道改为带符号的横向偏移（128 + d×20）；
    - 参数像素的 B 改存周长 /8；
    - 在 (2,1) 放一张 15x5 的卫星小图集：蓝色太阳能板 + 金色本体，A = 不透明度×100，所以图集自身不会显示出来。
  - `nsp_sat_bt.shader` 按「沿轨距离 = 相位差×周长」和横向偏移去采样图集。卫星会自动贴着轨道切线旋转；在椭圆两端会被压短，相当于透视。外圈带一层淡淡的青色辉光。
  - 线 shader 只读 R 通道，不受影响。
- ⚠ 再改轨道参数时，要保证左上角 (0..17, 0..6) 没有轨道像素（脚本里有 assert）。
- 待测：
  - 卫星形状清楚、朝向随轨道转动、没有残缺；
  - error.log 里没有 shader 报错。

---

## 2026-10-22 · 第 63 轮 · 轨道线默认隐藏，点右侧图标显示选中卫星的轨道
- 用户要求：轨道线默认不显示，只有点击右侧按钮，才显示当前选中卫星的轨道。
- shader：
  - `nsp_sat_bt.shader` 只画运动的卫星（la = 0）。
  - 新增 `nsp_sat_line.shader`：只画 R 通道的轨道线，0.25 s 淡入，带轻微呼吸。
  - 新 sprite `GFX_NSP3D_satlH_i` / `satsH_i`，和卫星层共用同一张贴图。
- GUI：
  - 行星（fx 窗口）：`NSP_satH_l_i` / `NSP_satH_s_i`；月球：`NSP_satmH_i`。都放在卫星层之前，让卫星压在线上。
  - 右侧图标改为可点击：`NSP_sat_mk_i_click` / `NSP_satm_mk_i_click` → `NSP_sat_select`（t_P 天体，t_i 槽位，再点一次取消）。
  - 选中的图标叠一个黄框 `NSP_sat_mks_i` / `NSP_satm_mks_i`（nsp_sat_marker_sel.dds）。
- 变量：`NSP_sat_sel`（槽位，-1 表示没选）、`NSP_sat_sel_b`（天体 1..9）。NSP_sat_sub 删掉选中的那颗时会自动取消选中。
- tooltip 末尾加了「点击：显示 / 隐藏轨道」。
- 待测：
  - 默认只看到卫星；
  - 点图标后出现对应轨道，再点一次消失；
  - 切换行星或月球后，不会残留别的天体的选中状态；
  - 土星使用 sats 线。

---

## 2026-10-22 · 第 62 轮 · 条件提示优化 + 可靠性减半
- 条件提示：
  - 新增 `common/scripted_localisation/NSP_cond_sl.txt`。启动任务、发射场行、目的地行、修正调色板这四处，不再使用 `[!xxx_click_enabled]`（它会连已满足的条件一起列出来）。
  - 现在只列出没满足的条件：红色「- 原因」，带具体数值和解决办法，例如 Delta-V 余量、成本和预算、所选载荷/火箭名。
  - 条件全部满足时，只给一行绿色结论；启动任务还会附上成功率、成本、余量。
  - 修正调色板会区分四种情况：不适用、已装配、可装配、槽位已满。
  - 新增 trigger `NSP_dest_allowed_pl`：从 NSP_dest_allowed 第一段拆出来的「载荷能否前往」。⚠ 以后改目的地规则，两处要同步。
  - 每条原因各对应一个 defined_text（GetNSPCS_* / CT_* / CD_*），满足时返回空串 NSP_EMPTY。以后 NSP_can_start_mission 新增条件，也要在这里补一条。
- 可靠性：
  - `NSP_calc_rel_final` ×0.5 后取整，载荷、火箭分项不变。
  - 预置任务的可靠性 75 → 38。
  - NSP_REL_TT 公式文案已同步。
- 待测：
  - defined_text 的 trigger 里用 v（行上下文）和 set_temp_variable 能否正常求值：悬停发射场、目的地行时原因是否正确；
  - 启动按钮 tooltip 在各种不满足情况下的显示；
  - 规划器总计可靠性是否为原来的一半。

---

## 2026-10-22 · 第 61 轮 · 卫星轨道平滑 + 卫星运动 + 卫星详情 tooltip
- 用户反馈（r58b 已能显示）：
  1. 轨道线像素感太强；
  2. 卫星不动；
  3. 卫星要有 tooltip，显示发射信息，调试添加的显示默认文字。
- 轨道 / 运动：
  - `work/r61/sat_data.py` 生成 480x270 的数据贴图，GUI 里改为 scale 1。文件名仍是 `nsp3d_satl_i` 和 `nsp3d_sats_i`。
  - 贴图通道：
    - R：4 倍超采样的抗锯齿线，远侧亮度 55%；
    - G 加上 A 的低 7 位：15 位轨道相位 θ；
    - B：卫星轨迹带的径向衰减；
    - 像素 (0,0)：初相、周期（18..约 80 s，外圈慢）、eps。
  - `nsp_sat_bt.shader` 按 frac(Time / 周期 + 初相) 画白芯加青色辉光的圆点。远侧被遮挡的轨道段贴图里不存在，所以卫星绕到行星背后会消失。
  - 必须用 Point 采样。
- tooltip：
  - 卫星由 shader 驱动，命中区跟不上，所以每颗卫星在视图右侧放一个 16px 小图标 `GFX_NSP_sat_marker`，悬停显示该卫星的详情。
    - 行星：`NSP_sat_mk_0..9`（x 452）；
    - 月球：`NSP_satm_mk_0..9`（x 482）。
  - 数据：
    - 每次任务新记录 `NSP_m_veh` / `NSP_m_site`，开始任务和预置任务两处都写；老存档先用 -1 补齐长度。
    - `NSP_sat_mid^(天体×10+槽位)` 存「任务 id + 1」，0 表示调试添加。
    - `NSP_sat_sync` 把当前天体的 10 颗卫星展开到 `NSP_sat_s_*^i`。
  - 本地化：
    - `NSP_SAT_TT_i` → GetNSPSatTTi；
    - 调试卫星用 `NSP_SAT_TT_DBG`；
    - 真实卫星用 REAL_i：载荷名 + 序号、火箭、发射场、目的地、可靠性。
- 待测：
  - 轨道线顺滑，没有锯齿；
  - 卫星沿轨道移动，绕到背面时消失；
  - 调试 + 之后，悬停图标显示「调试卫星」；
  - 地球轨道 / 地月转移任务成功后，悬停显示正确的载荷、火箭和发射场；
  - error.log 里没有 shader 编译错误（这次在 shader 里用了 if-return）。

---

## 2026-10-22 · 第 60 轮 · 发射类 / 载荷类修正用颜色区分
- 原因：用户反馈两类修正看起来一样，不好区分。
- 发射类（id 0..2、8..12）改为橙色：
  - 图标帧的外框改成橙色，第二圈改成暗橙描边。
  - 新增 `nsp_modifier_frame_launch.dds` 和 `nsp_modifier_slot_launch.dds`，并注册 sprite：`GFX_NSP_modifier_frame_launch` / `GFX_NSP_modifier_slot_launch`。
  - 「发射类修正」框和 4 个槽位改用这两个 sprite。
  - 标题改为 §Y。
- 载荷类（3..7、13..19）保持原来的紫色。
- 脚本：`work/r60/recolor.py`，原图备份在 `work/r60/bak/`。
- ⚠ 以后新增修正：
  - 发射类要把它的帧号加进 recolor 的 LAUNCH 列表；
  - 然后同时补画外框（外框 1px 橙色，第二圈暗橙 120,72,28）。
- 待测：调色板和已装配槽位里，两类修正的边框颜色正确。

---

## 2026-10-22 · 第 59 轮 · 重画规划器修正图标 1..6
- 原因：用户截图里的原有修正图标（捆绑助推器、半人马、改进发动机、先进双子星、对接、舱外活动）太简陋。
- 改动：`gfx/interface/NSP/planner/nsp_modifier_icons.dds` 的帧 1..6。
  - 重画风格与 r57 新增图标一致：36px 像素帧、TNO 青 / 白 / 黄 / 红配色。
  - 帧 7、8 和 9..20 保持不动。
- 生成脚本：`work/r59/icons.py`，原图备份在 `work/r59/bak/`。
- 待测：规划器修正调色板和已装配槽位里的图标显示正常，没有错帧。

---

## 2026-10-22 · 第 58b 轮 · 修复：卫星轨道不显示 + 月球加卫星
- 用户反馈（截图）：计数显示 10 / 10，但轨道一条都没有；月球视图也没有。
- 判断：计数文本正常，说明 `NSP_sat_cnt` 和 sync 都没问题。卫星按钮一直停在第 1 帧（全空帧），也就是 buttonType 加自定义 effect 的精灵不吃 properties 里的 frame。
  - 旁证：聚焦动画本身也只用固定的第 1 帧。
- 改法：不再用多帧。
  - 每颗行星改为 10 个单帧按钮 `NSP_sat_<p>_<i>`，click_enabled = 聚焦该行星 且 `NSP_sat_cnt^p > i-1`。
  - 禁用态由 shader 输出全透明。从禁用切到启用时 AnimationTime 会刷新，所以新加的轨道也会淡入。
- 图：
  - `nsp3d_satl_1..10`：普通行星和月球，半径 120。
  - `nsp3d_sats_1..10`：土星，半径 100。
  - 由 `work/r58/sat_art.py` 生成。
  - 删除 r58 的 `nsp3d_sat_<p>.dds`（11 帧）、NSP_satf_* 变量和 properties。
- 月球：
  - `NSP_sat_cnt^9`；地月转移任务成功后 +1。
  - `NSP_space.gui` 地图列在 `NSP_moon_hit` 前加 `NSP_sat_moon_1..10`（位置 30,10，scale 2）。
  - 加计数文本 `NSP_SAT_MOON_COUNT` 和调试按钮 `NSP_sat_moon_add/sub`（is_debug）。
  - 触发器写在 NSP_home 条目；`NSP_set_view` 里调用 NSP_sat_sync 刷新 dirty。
- ⚠ 本轮删除了文件，解压前要先删掉旧文件夹。
- 待测：
  - 带 -debug 启动，在地球聚焦视图和月球视图里点 +，轨道逐条淡入；
  - 土星的轨道不应和行星本体错位；
  - 如果仍然不显示，说明是 nsp_sat_bt.shader 的问题：去 error.log 里搜 shader，再改用 buttonstate.lua 做临时验证。

---

## 2026-10-22 · 第 58 轮 · 行星聚焦视图：卫星轨道 + 调试加减按钮
- 原因：用户要求成功送达行星的卫星显示在放大后的行星轨道上；每颗行星预设 10 条空轨道，发送成功才显示；旁边加调试按钮增减卫星。
- 数据：
  - `NSP_sat_cnt^p`（p = 1..8）是每颗行星的卫星数，上限 10。
  - `NSP_satf_<p>` = 卫星数 + 1，用作帧号。
  - `NSP_sat_cur` 是当前聚焦行星的卫星数。
  - 代码在新文件 `common/scripted_effects/NSP_sat_effects.txt`（init / sync / add / sub / on_success）。
- 成功计数规则（NSP_sat_on_success，由 NSP_apply_objectives 调用）：
  - 目的地 0..3 → 地球。
  - 地月转移 → 不计。
  - 逃逸地球：水手号序号为奇数 → 金星，为偶数 → 火星；其他载荷 → 火星。
  - 木星及更外侧的行星暂时没有对应目的地，只能用调试按钮加。
- 美术（`work/r58/sat_art.py`）：
  - `nsp3d_sat_<p>.dds`：每张 240×135，共 11 帧，scale 2。
  - 第 k 帧画前 k-1 条轨道，每条轨道上一颗卫星。
  - 轨道是倾角交错的扁椭圆；远侧落在行星盘面内的部分不画。
  - 调试按钮图：`nsp_sat_btn.dds`，2 帧，分别是 + 和 −。
- shader `gfx/FX/nsp_sat_bt.shader`：
  - 采样当前帧，在 0.7–1.1 s 内淡入，等行星飞到中央后再出现。
  - Disable 状态全透明。
  - 时间轴沿用 r31 的 AnimationTime 机制。
- GUI：
  - `NSP_focus_fx_window` 新增 8 个按钮 `NSP_sat_<p>`，放在 fin/fout 之后。
  - 启用条件与 `NSP_fin_<p>` 相同；帧号由 NSP_focus_fx 的 properties 提供。
  - `NSP_focus_in_window` 在返回命中区之后加：
    - 计数文本 `NSP_SAT_COUNT`（右上角）；
    - `NSP_sat_dbg_add` / `NSP_sat_dbg_sub`，只在 is_debug 下可见，与 r38 相同。
- 调用点：
  - `NSP_fanim_refresh` 开头调用 NSP_sat_sync，切换聚焦时刷新计数；
  - `NSP_daily_tick` 调用 sync，为老存档补数组；
  - `NSP_init` 清空数组。
- 待测：
  - 带 -debug 启动，放大任意行星，点 + 后轨道逐条出现，点 − 后逐条消失，计数随之变化。
  - 叠加层在行星飞入后才淡入；退出时立即消失。
  - 近地轨道任务成功后，地球多一条轨道。
  - 若轨道叠加层没有随帧变化：说明 buttonType 不认 properties 里的 frame，需改成 iconType 或动态列表。
  - error.log 里查 nsp_sat_bt.shader 编译错误。

---

## 2026-10-22 · 第 57 轮 · 更多科技解锁可装配修正（8 → 20 个）
- 原因：用户要求「让更多科技解锁新的可装配修正」。
- 新增修正 8..19，完整数值表见 common/scripted_effects/NSP_rd_r57_effects.txt 文件头。
  - 发射类：
    - 8 冗余制导（科技 36）
    - 9 S-IVB 二次点火（科技 6）
    - 10 F-1 推力提升（科技 9）
    - 11 NERVA 核热上面级（科技 61）
    - 12 快速发射流程（科技 37，工期 -15%）
  - 载荷类：
    - 13 交会雷达（31）
    - 14 加厚防热罩（29）
    - 15 生存装备包（83）
    - 16 MMU（86）
    - 17 S 波段应答机（38）
    - 18 RTG（72）
    - 19 闭环生保（68）
- 适用性：新增 trigger NSP_mod_fits，调色板过滤和自动卸下共用。
  - 3 仅双子星，沿用原规则。
  - 9 / 10 / 11 仅土星 IB / V。
  - 14 / 15 / 16 / 19 仅载人；18 仅无人。
  - 换载荷或火箭后，不适用的修正自动卸下：NSP_mod_drop_unfit_r57。
- 数组：
  - NSP_rd_patch_r57 按长度把 NSP_mod_type / dv / rel / cost 补到 20 项，NSP_mod_sel / unl 也补到 20 项，新开局和老存档都适用。
  - 解锁由 NSP_rd_apply_r57 按研发状态重算。
- 文件：
  - 新增 NSP_rd_r57_effects.txt
  - NSP_space_effects.txt：调色板循环、修正结算循环、reset_planner 改为 20；工期加上 12 号修正。
  - NSP_rd_unlock_effects.txt：手加两行。
  - NSP_space_triggers.txt：NSP_mod_fits。
  - NSP_space.gfx：modifier_icons noOfFrames 20。
  - nsp_modifier_icons.dds 追加 12 帧：work/r57/icons.py，原图在 work/r57/bak/。
  - 两个 yml：MOD_NAME / DESC 8..19，12 个科技的 RD_UNLOCK 文案。
  - 预览器加了 planner_r57 状态。
- 测试：
  - 用调试决议完成全部研发后，调色板可滚动，能看到最多 20 个修正。
  - 选红石时看不到 9 / 10 / 11；选无人载荷时看不到 14 / 15 / 16 / 19，选载人载荷时看不到 18。
  - 装配后切换火箭或载荷，不适用的修正自动消失。
  - 快速发射流程使总工期缩短。
  - error.log 里没有 NSP_mod_* 越界。

---

## 2026-10-22 · 第 56 轮 · 发射场按 TNO 世界观修正（开局 1962.1.1）
- 原因：用户提醒开局是 1962.1.1、TNO 世界观。
  - TNO 里马绍尔群岛（夸贾林）属于日本统治下的微克罗尼西亚，美国不能用。
  - 沃洛普斯（1945）、白沙（1945）、范登堡（1958 首射）在开局前就已建成。
- 改动：
  - site 6 / 科技 92：夸贾林环礁改为约翰斯顿环礁（北纬 16.7°，1962 年雷神发射地）。
    - 地球静止 -0.2，极地 +0.3；不能发重型，成本 +10%。
  - 科技 88、89、91 开局即完成（state 3，prog 100），对应发射场开局可用。
  - 老存档：新增 NSP_rd_patch_r56，带 flag NSP_r56_sites，只执行一次。若这几项在研发队列里，移出队列，不退经费。
  - 仍需研发：90 太平洋导弹靶场、92 约翰斯顿、93 波克平原。KSC 仍由 53 解锁。
  - 卡片线稿第 16 帧重画为 JOHNSTON ATOLL：work/r56/art.py（复制自 r53）。
- 文件：
  - NSP_rd_r53_effects.txt
  - NSP_space_effects.txt（注释）
  - NSP_space_triggers.txt（注释）
  - 两个 yml 文件
  - nsp_rd_tech_5.dds、nsp_rd_links.dds
- 测试：
  - 新开局发射场列表里沃洛普斯、范登堡、白沙可选。
  - 研发树里这三项显示已完成。
  - 太平洋导弹靶场直接可研发（前置范登堡已完成）。
  - 老存档读档后同样补完。

---

## 2026-10-22 · 第 55 轮 · 修复：地面设施第 4、5 行的发射场卡片不显示
- 原因：用户截图显示，地面设施第 4、5 行只有连线和接点，没有卡片。
  - 卡片条目的可见性触发器写的是 `v < NSP_rd_blank`。NSP_rd_blank 是 87，即空格占位 id。
  - r53 新增的研发项目 id 是 88..93，都大于 87，所以整张卡（底板、图标、状态、选中框、进度条）都被隐藏。
  - 预览器不跑触发器，所以 r53 预览里能看到卡片，没有发现这个问题。
- 修复：
  - NSP_space_rd_guis.txt 里共 11 处改为 `NOT = { check_variable = { v = NSP_rd_blank } }`。
  - 行标签 rowlab_3、rowlab_4 的显示条件补上 track 5（发射场 / 远程靶场）。r53 只加了本地化，漏改了触发器。
- 规则：以后研发项目的 id 都会大于占位 87。判断「是否为空格」只能用「等于 / 不等于 blank」，不要用小于。
- 测试：
  - 地面设施页签第 4 行能看到沃洛普斯、范登堡、太平洋导弹靶场、夸贾林；第 5 行能看到白沙、波克平原。
  - 这些卡片可以点击、选中、开始研发。
  - 行标签正常显示。

---

## 2026-10-22 · 第 54 轮 · 预算单位改为 B + 每半年拨款一次
- 原因：用户要求「预算单位改成B，每半年才发一次预算」。
- 做法：
  - 内部仍按百万美元记账，NSP_space_budget 和所有成本都不变。
  - 显示时 ÷1000，变量为 NSP_bud_b / NSP_left_b / NSP_peak_b / NSP_pay_est_b / NSP_pay_last_b，本地化用 |.2 显示。
  - 预算、剩余、拨款、一次性拨款文案（0.5 / 0.6 / 0.8 / 1.2B）改为 B。
  - 单项成本（载荷、火箭、修正、任务总计、研发费用）保持 M。
- 拨款：
  - 每周仍按当周国会支持累计 30 + 支持 × 0.8（M），存进 NSP_pay_accum。
  - 满 26 周一次拨付并弹事件 nsp.12；年总额不变。
  - 预算 tooltip 和国会支持 tooltip 显示下次拨款预估和剩余周数。
- 文件：
  - 新增 common/scripted_effects/NSP_budget_effects.txt：NSP_budget_disp、NSP_budget_weekly。文件名排在最前，其他文件都能调用。
  - NSP_rd_unlock_effects.txt：econ_weekly 的拨款段改为调用 NSP_budget_weekly（手加）。
  - NSP_rd_effects.txt：NSP_rd_recalc 手加 NSP_budget_disp。
  - NSP_space_effects.txt：recalc_home、recalc_planner 调用 NSP_budget_disp；init 初始化 pay_* 变量。
  - events/NSP_space_events.txt：新增 nsp.12。
  - 两个 yml 文件。
  - work/preview/render_preview.py：加 BUDGET_DEMO 示例值。
- 测试：
  - 主页、规划器、研发页的预算显示为 $9.80B 这种格式。
  - 悬停预算显示下次拨款和剩余周数。
  - 26 周后弹出 nsp.12，预算增加约 $1.8B（支持度 50% 时）。
  - 老存档读档后从 0 开始累计。

---

## 2026-10-22 · 第 53 轮 · 发射场改为研发解锁 + 新增 3 个发射场
- 原因：用户要求「加入更多发射场地，发射场地也需要科技研究解锁」。
- 发射场从 5 个扩到 8 个。卡纳维拉尔角开局可用，其余都要研发：
  - 范登堡：89
  - 沃洛普斯：88
  - 太平洋导弹靶场：90
  - 白沙：91
  - 肯尼迪航天中心（新）：53，即 39 号发射复合体
  - 夸贾林环礁（新）：92
  - 波克平原（新）：93
- 新规则：
  - 土星 V 只能从肯尼迪航天中心发射。
  - 夸贾林、波克平原不能发射重型火箭；波克平原算小型发射场。
  - 夸贾林成本 +10%。
- 纬度修正：
  - 太平洋导弹靶场：地球静止 -0.1
  - 夸贾林：地球静止 -0.3；近地、交会、地月转移 -0.1；极地 +0.3
  - 波克平原：极地 -0.4，其他 +0.4
  - 肯尼迪：同卡纳维拉尔角，极地 +0.3
- 新研发项目 88..93，放在地面设施分类：
  - 第 4 行「发射场」、第 5 行「远程靶场」；第 1 行改名「发射工位」。
  - 线稿和连线由 work/r53/art.py 生成。它借用 work/rd/gen_rd.py 的绘制函数，不跑 main，因为 gen_rd 的数据还是 r49 之前的。
  - tech_5 图集从 11 帧扩到 17 帧，宽 4063，已到 4096 上限，这个分类不能再加帧。
- 文件：
  - 新增 common/scripted_effects/NSP_rd_r53_effects.txt：
    - NSP_rd_patch_r53：按数组长度把研发数组补到 94，NSP_rd_count 改为 94，写入格位。
    - NSP_rd_apply_r53：生成 NSP_site_unl，把 NSP_site_ids 补到 8；选中的发射场没解锁时退回 0。
    - NSP_site_req_r53：纬度修正。
  - NSP_rd_unlock_effects.txt：
    - NSP_rd_apply_unlocks 末尾手加 NSP_rd_apply_r53。
    - NSP_rd_daily 手加 NSP_rd_patch_r53。
  - NSP_space_effects.txt：所需 ΔV 改为调用 NSP_site_req_r53；夸贾林成本；初始化 site_ids 改为 0..7。
  - NSP_space_triggers.txt：
    - NSP_site_allowed 增加三个条件：已解锁、重型限制、土星 V 只能在肯尼迪。
    - NSP_small_site 加入 7。
  - interface/NSP_rd.gfx：tech_5 noOfFrames = 17。
  - 本地化：
    - 发射场名、简称、说明（NSP_SITE_DESC_k）
    - 发射场行的 tooltip 先显示说明再显示条件
    - 研发项目 88..93 的文案；53 的 UNLOCK 文案；行标签
  - 预览脚本：work/r53/preview.py
- 测试：
  - 新开局：规划器里只有卡纳维拉尔角能选，其余为灰色，悬停显示「发射场已研发」条件不满足。
  - 研发沃洛普斯岛后，沃洛普斯可选。
  - 调试全部完成后 8 个发射场都能选。
  - 选土星 V 时，只有肯尼迪可选。
  - 老存档：读档后地面设施分类第 4、5 行出现新项目；error.log 中没有数组越界。
  - 研发树向下滚动能看到新卡片，线稿与连线正确。

---

## 2026-10-22 · 第 52 轮 · 科技效果落地（只写了文字的科技补上真实效果）
- 文件：
  - 新增 common/scripted_effects/NSP_rd_r52_effects.txt
  - NSP_space_effects.txt：NSP_recalc_planner 加 4 处调用（ΔV / 可靠性 / 所需 ΔV / 成本），NSP_apply_objectives 加 1 处调用（成功奖励）
  - NSP_rd_l_simp_chinese.yml：21 条 UNLOCK 文案改成实际效果，并新增 NSP_RD_D_UNLOCK_TT
  - interface/NSP_rd.gui：研发详情「解锁」行加 pdx_tooltip（文字过长被截断时悬停看全文）
- 原因：用户要求「继续优化科技效果」。原来很多科技的效果只是一句描述，没有实际作用，例如「土星 V 一级发动机」「修正：月球车」「目的地：木星」「发射场：卡纳维拉尔角」。
- 效果全部按 NSP_rd_state^id = 3 现算，读档和重算都幂等。
- ΔV：
  - S-IVB：土星 IB / V +0.3
  - H-1：土星 IB +0.2
  - J-2：土星 IB / V +0.2
  - F-1：土星 V +0.4
  - NERVA：土星 IB / V +0.5
  - 核动力上面级：地月转移 / 逃逸地球 +0.6
- 所需 ΔV：
  - 惯性测量单元：-0.1
  - SLC-6：范登堡发射 -0.2
- 火箭可靠性：
  - LC-14：宇宙神系列 +3
  - LC-19：泰坦系列 +3
- 载荷可靠性：
  - 双子星计算机：双子星 +3
  - Block II：阿波罗 +5
  - 阿波罗制导计算机：阿波罗 +3
  - MOL：交会任务 +5
  - AMU：带舱外活动系统时 +3
  - 徘徊者号：无人载荷去地月转移 +3
  - 先驱者 10 号 / 旅行者号：逃逸地球任务各 +5
- 成本：土星 INT-21，土星 IB / V 任务 -10%。
- 成功奖励：
  - 登月舱：阿波罗地月转移成功，民意 +3
  - 月球车：阿波罗地月转移成功，民意 +2、科研 +100
- 测试：
  - 调试决议完成全部研发后，土星 V + 阿波罗 + 地月转移的实际 ΔV 应比 r51 高 2.0（0.3 + 0.2 + 0.4 + 0.5 + 0.6），所需 ΔV 低 0.1。
  - 规划器选宇宙神系列，火箭可靠性比 r51 高 3。
  - 研发详情悬停「解锁」行，显示完整效果。

---

## 2026-10-22 · 第 51 轮 · 根据科技新增载荷与运载火箭
- 文件：
  - 新增 common/scripted_effects/NSP_rd_r51_effects.txt（数值表补项 + 解锁）
  - NSP_rd_unlock_effects.txt：NSP_rd_apply_unlocks 末尾加一行 `NSP_rd_apply_r51 = yes`。⚠ 用 unlock_table.py / gen.py 重新生成这个文件时，必须把这一行加回去
  - NSP_space_effects.txt：载荷 / 火箭的循环上限；载人可靠性判定；水星目标
  - NSP_space_triggers.txt：NSP_dest_allowed 新载荷规则；发射台条件放行新火箭
  - interface/NSP_space.gfx：载荷图 noOfFrames 4→10，火箭图 4→8
  - gfx/interface/NSP/planner/nsp_payload_art.dds / nsp_vehicle_art.dds：追加新帧（work/r51/art.py 生成，原图备份在 work/r51/bak/）
  - 本地化：NSP_space（名称 / 类型 / 简称 / 徽章）、NSP_rd（9 条 UNLOCK 文案）
- 原因：用户要求「根据科技设计出更多的载荷和运载火箭」。
- 新载荷（下标 4 = 苏联占位，不可选）：

| # | 载荷 | 解锁科技 | 质量 | 原型成本 | 可靠性 | 目的地 |
|---|---|---|---|---|---|---|
| 5 | 水星飞船（载人） | 12 水星飞船 | 1.4 t | 6 | 85 | 近地轨道 |
| 6 | Syncom 通信卫星 | 42 Syncom | 0.07 t | 4 | 80 | 近地 / 地球静止 |
| 7 | 雨云号气象卫星 | 43 雨云号 | 0.38 t | 6 | 85 | 近地 / 极地 |
| 8 | 勘测者号着陆器 | 45 勘测者号 | 1.0 t | 10 | 70 | 地月转移 |
| 9 | 天空实验室（载人） | 16 天空实验室 | 77 t | 90 | 75 | 近地轨道 |

- 新火箭：

| # | 火箭 | 解锁科技 | 干重 / 燃料 / 比冲 | 原型成本 | 可靠性 | 定位 |
|---|---|---|---|---|---|---|
| 4 | 红石 MRLV | 0 红石 MRLV | 5 / 27 / 235 | 3 | 90 | 不加修正进不了近地轨道 |
| 5 | 宇宙神 LV-3B | 1 宇宙神 LV-3B | 20 / 74 / 309 | 7 | 82 | 水星飞船 9.70 刚好入轨；双子星 9.23 进不了 |
| 6 | 宇宙神-阿金纳 | 4 阿金纳上面级 | 21 / 80 / 315 | 9 | 80 | 双子星 9.59 入轨；加半人马修正后水手号可逃逸地球 |
| 7 | 宇宙神-半人马 | 5 半人马上面级 | 22 / 92 / 330 | 12 | 75 | 勘测者号 11.15 地月转移；水手号 11.33 逃逸地球 |

- 规则：
  - 载人可靠性加成适用于载荷 0 / 1 / 5 / 9。
  - 水星飞船去近地轨道成功后，水星目标 B +1。
  - 新火箭都不算重型，小发射场可以发射，也不需要 LC-34/37、39 号发射台。
  - 天空实验室只有土星 IB（9.75）或土星 V 推得动。
- 老存档：首次重算解锁时按数组长度自动补齐（pl 5→10、ve 4→8、pl_next 补 1），不需要新开档。
- 测试：
  - 调试决议完成全部研发，规划器里载荷应能在 9 种之间切换（跳过苏联），火箭在 8 种之间切换，图片对应。
  - 水星飞船 + 宇宙神 LV-3B → 近地轨道，余量为正。
  - 勘测者号只能选地月转移。
  - Syncom 去地球静止轨道需要加发射修正。
  - error.log 里查 array index 报错。

---

## 2026-10-21 · 第 50 轮 · Mission Control「建设」页签改为「历史」
- 文件：common/scripted_effects/NSP_space_effects.txt、common/scripted_localisation/NSP_space_scripted_loc.txt、common/scripted_guis/NSP_space_guis.txt、NSP_space_l_simp_chinese.yml
- 原因：用户要求把建设页签改成历史，历史发射任务都放在这里。
- 内容：
  - NSP_resolve_mission 把结束的本国任务插到 NSP_missions_hist 开头（最新在前）；失败的任务另记入 NSP_hist_fail。
  - NSP_mc_sync 在 tab 1 时用历史数组填 NSP_mc_intl_view。
  - NSP_intl_entry 卡片改为显示：本国任务图标、载荷名 + 编号、§G任务成功§! / §R任务失败§!、目的地。
  - NSP_init 和 NSP_clear_missions 会清空历史数组。
- 测试：完成一个任务后切到「历史」页签，应该出现卡片，成功和失败颜色不同；本国页签里不再有它。

## 2026-10-21 · 第 49b 轮 · 去掉全部开局发射任务
- 文件：common/scripted_effects/NSP_space_effects.txt
- 原因：用户要求去掉默认的所有发射项目。
- 内容：
  - NSP_init 里 4 条 NSP_seed_mission（Gemini 9、Apollo 1、两条苏联任务）全部注释掉，新开局任务列表为空，并设置 flag NSP_m_v2。
  - 新增 NSP_clear_missions；NSP_daily_tick 开头检查，老存档没有 NSP_m_v2 时清空一次全部任务数组。
- 测试：新开局任务控制里没有任何任务；老存档过一天后任务清空；发射架自动回到空架。

## 2026-10-21 · 第 49 轮 · 零科技开局：没研发就什么都不解锁
- 文件：common/scripted_effects/NSP_rd_effects.txt（NSP_rd_init 手改：gen_rd.py 已找不到，原文件备份 nsp_r35/NSP_rd_effects.txt.pre_r49）；nsp_r35/unlock_table.py + gen.py → NSP_rd_unlock_effects.txt、NSP_rd loc。
- 原因：用户要求「没有科技根本不会解锁任何东西」。原来开局就有 32 个预完成项目、3 个研发中项目，近地轨道和地月转移也是默认开放的。
- 内容：
  - 开局所有研发项目 state=0、prog=0，研发队列为空；根节点由 NSP_rd_recalc 置为可研发。
  - 去掉目的地默认开放。近地轨道改由研发 1「宇宙神 LV-3B」解锁；地月转移由研发 30「月球返回再入」或研发 47「水手号」解锁。
  - 新增 flag NSP_rd_v3：老存档第一次运行时重置为零科技一次，并刷新解锁表。
- 测试：新开局时，规划器里的载荷、火箭、目的地、修正应该全部锁定；研发宇宙神 LV-3B 后近地轨道解锁；老存档研发进度会清零一次。

## 2026-10-21 · 第 48 轮 · 发射失败分支动画（发射台爆炸 / 中途爆炸）
- 文件：nsp_r44_pad/build_v3.py（新增 boom 骨骼 + fail_pad / fail_air 动画）→ gfx/models/NSP/launchpad/*（mesh、2 个新 .anim、anims.asset）；gfx/entities/NSP_launchpad.gfx / .asset（2 个新 entity）；gfx/particles/NSP/NSP_launchpad_particles.asset + gfx/entities/NSP_launchpad_particles.gfx（8 个新粒子）；common/buildings/NSP_launchpad_buildings.txt（NSP_pad_fail_pad / NSP_pad_fail_air）；common/scripted_effects/NSP_launchpad_effects.txt（mode 3/4、NSP_pad_fail_pad / NSP_pad_fail_air、debug_3/4）；common/decisions/NSP_debug_decisions.txt（2 个调试决议）；loc；map/buildings.txt（每个新建筑复制 launch 的 21 行，共 105 行，结尾无换行）。
- 原因：用户要求两个分支：发射台上爆炸、起飞十几秒后爆炸。
- 内容：
  - 发射台爆炸（900 帧 / 30 s）：2.0 s 点火，3.0 s 离架，升约 4 m 后倾斜下坠，4.5 s 在台上爆炸（火箭 scale→EPS），火球 + 碎片 + 黑烟，5 s 起台上残火 25 s。
  - 中途爆炸（1080 帧 / 36 s）：轨迹和速度与正常发射一致，16.0 s（起飞后 13 s）空中爆炸；尾焰 14 s、尾迹 13 s 后截断，尾迹留在空中慢慢散。
  - boom 骨骼没有几何，跟着火箭走，爆炸后停在爆点，挂爆炸粒子（避免挂在被缩成 EPS 的 rocket/plume 上）。
  - 自动规则暂不产生 3/4；任务失败可直接调 NSP_pad_fail_pad / NSP_pad_fail_air。
- 测试：调试决议「发射架：发射台爆炸」「发射架：中途爆炸」；看火球/黑烟大小、碎片是否下落、爆点是否在火箭位置；error.log 里 node boom / particle 报错。

## 2026-10-21 · 第 47b 轮 · 尾焰方向取反

- 用户实机截图：尾焰朝上，盖住了火箭。
- 实测结论：粒子局部 Z = 世界向上，与 r47 的推断相反。换算规则更正为：世界方向 (x, y, z) 对应局部 (x, -z, y)，竖直分量直接对应局部 +Z。
- `NSP_launchpad_particles.asset` 里所有 force direction 的 z 分量取反：
  - 尾焰：(0,0,-1)，朝下。
  - 地面烟 L/R：(±0.45, 0, 0.7)，向外并上升。
  - 中心烟云：(0,0,1)，上升。
  - 尾迹：(0.8, 0, 0.25)，向东并上升。
  - 排气：(0.7, 0, -0.5)，下沉。

---

## 2026-10-21 · 第 47 轮 · 修正尾焰方向，地面烟不再排成一条线

- 用户实机反馈，附视频：尾焰很怪，朝屏幕上方喷；地面烟排成一条横线。
- 原因：导出后骨骼的局部轴转了 90°。回读 mesh 的 tx 确认：局部 Y 对应世界 Z（南北），局部 Z 对应世界 -Y（向下）。
  - 粒子的 local force 和 box_emitter 都是按骨骼局部轴算的。
  - 所以原来的"向下"实际变成了水平方向，烟盒的"高度"实际变成了南北厚度。
- 换算规则：世界方向 (x, y, z) 对应局部 (x, z, -y)。以后改粒子都按这个换算。
- `gfx/particles/NSP/NSP_launchpad_particles.asset` 的改动：
  - 尾焰：推力方向改为 (0,0,1)，即真正朝下。发射量提高到 220 + 120，粒子更小，形成连续火舌。
  - 地面烟 L/R：发射盒改为水平铺开（x 0.25 / y 0.7 / z 0.08），推力改为向外加明显上升 (±0.45, 0, -0.7)。
  - 新增 `NSP_pad_smoke_C_asset`：挂在 root（发射台中心），水平 0.9×0.9 范围铺开后上升，形成环形烟云。2.3 s 触发，持续 10 s。
  - 尾迹：风向修正为向东飘并微微上升，发射量提高到 55。
  - 排气：方向修正为下沉并顺风。
- `gfx/entities/NSP_launchpad_particles.gfx` 和 `NSP_launchpad.asset` 已加上 smoke_C 的声明和事件。
- r46 的粒子文件备份在 `work/nsp_r44_pad/particles/r46_particles.asset.bak`。

---

## 2026-10-21 · 第 46b 轮 · 恢复 r44 速度，只延长时长

- 用户纠正：要延长的是动画时长，不是把火箭放慢。
- 轨迹恢复 r44：加速度 a = 2 + 3.2t m/s²，起飞后 4~9 s 向东偏转 14°。飞行时长保持 90 s，共 2790 帧。
- 粒子时长不变：尾焰 91 s，尾迹 88 s。
- 作废：下面 r46 写的 s = 0.25t² 和 35° 转弯。

---

## 2026-10-21 · 第 46 轮 · 发射飞行时间延长到 90 秒

- 用户实机反馈：r45 的粒子效果正常，但飞行时间太短，希望延长约 10 倍。
- 动画由 `build_v3.py` 生成：launch 从 360 帧改为 2790 帧（30 fps，约 93 秒）。
  - 时间线：f60 点火，f90 起飞，之后飞行 90 秒，最后 3 秒远去缩小，末帧回到空架姿态。
  - 轨迹：沿路径的距离 s = 0.25t² m。约 10 秒越过塔顶，60 秒时约 900 m。
  - 转弯：起飞 10 秒后开始重力转弯，60 秒时向东偏约 35°。
  - 机体抖动在起飞后约 8 秒内逐渐消失。
- 粒子 `NSP_launchpad_particles.asset`：
  - 尾焰 duration 改为 91 s。
  - 尾迹 duration 改为 88 s，life 9~12 s，max_amount 600。
  - 地面烟 duration 改为 14 s，life 9~12 s。
- 实机检查：火箭和尾焰是否全程同步，尾迹长度是否合适，飞出视野的时间是否合适。速度可以改 `build_v3.py` 里的 `0.25` 系数，总时长改 `FLIGHT_S`。

---

## 2026-10-21 · 第 45 轮 · 烟雾和尾焰改成粒子

- 用户反馈：烟雾和尾焰太奇怪。原因是 r44 用的是不透明网格：烟是一团团白球，尾焰是一根实心橙色锥，而且网格做不了半透明。
- 改法照 Millennium Dawn 的 `building_landmark_shuttle_launch`：在 entity 的 state 里写 `event = { time node particle keep_particle }`，把粒子挂到骨骼上。
- 模型：新脚本 `work/nsp_r44_pad/build_v3.py`，去掉了烟团和尾焰网格，现在约 1.56 万三角面、9 根骨骼。新增 3 根挂点骨骼：
  - `vent`：一级顶部排气口，跟着火箭。
  - `smoke_l` / `smoke_r`：导流槽两端。
  - `plume`：喷口，原来就有。
  - ready 动画改成 60 帧静态。
- 粒子文件：
  - `gfx/particles/NSP/NSP_launchpad_particles.asset`：6 个粒子，结构照 MD 的 `shuttle_smoke.asset` 和 `shuttle_flame.asset`。
  - `gfx/entities/NSP_launchpad_particles.gfx`：对应的 pdxparticle 声明。
  - `gfx/particles/NSP/nsp_smoke_puff.dds`：256 烟团，软边加噪声，下暗上亮。生成脚本 `particles/gen_tex.py`。
  - `gfx/particles/NSP/nsp_flame_puff.dds`：128 火团。
  - 尾焰：ParticleAdditive，局部空间，两层（白黄内核加橙色外焰），向下推力，寿命约 0.4 s。
  - 地面烟：ParticleAlphaBlend，世界空间，从两个槽口向外铺开并上升，寿命 7~9 s，淡入淡出、逐渐变大。
  - 尾迹：世界空间，从 3 s 开始留在火箭经过的路径上，顺风飘散。
  - 排气：ready 状态一直排，launch 状态只排前 1.8 s。
- `gfx/entities/NSP_launchpad.asset` 的事件时间：0 s 排气，2.0 s 点火（尾焰和地面烟），3.0 s 起飞（尾迹）。
- 粒子尺寸单位等于 mesh 单位（1 m = 0.05）。按 MD 航天飞机 mesh 约 22 单位高推算，数值大约是 MD 的 1/8。
- 实机检查：
  - 粒子是否出现，大小是否合适。太大或太小的话，改 `.gfx` 里的 pdxparticle scale，或者 `.asset` 里的 size。
  - error.log 里有没有 particle 或 node 相关报错。
  - ready 状态的排气是否持续。

---

## 2026-10-21 · 第 44 轮 · 发射架模型与动画重做

- 用户反馈：动画生硬，模型粗糙。
- 新的生成脚本是 `work/nsp_r44_pad/build_v2.py`，从建场景一路跑到导出 PDX，可以重复运行。DDS 由 `make_dds.py` 生成，回读渲染检查用 `verify_v2.py`。
  - 旧的 r40 脚本 `build_scene.py` 和 `export_pdx.py` 不再使用，但没有删除。
  - r43c 的旧模型备份在 `nsp_r44_pad/r43c_backup/`。
- 模型（约 2.1 万三角面，42 根骨骼）：
  - 场地：八角地坪和草边，截头硬台，中间开导流槽和楔形导流器。
  - 发射架：四腿发射台架，带中孔、夹持臂和栏杆。
  - 脐带塔：每 8 m 一层平台，加电梯井、侧挂设备间、锤头吊臂和避雷针。
  - 三根桁架摆臂。
  - 周边：两个燃料球罐（带支腿和管线），三栋小楼，水塔，两根避雷塔，爬行道。
  - 火箭：5 台发动机，梯形尾翼，Saturn 式四象限滚转标识，级间段桁条，尖拱整流罩，逃逸塔。
- 贴图：
  - 1024 图集，烘焙程序材质颜色乘 AO，带完整 mipmap，大约 5.6 MB。
  - UV 顶部 10% 是程序贴图条：左半给烟团用（下暗上亮），右半给尾焰用（喷口白黄 → 橙 → 烟褐）。
  - normal 和 specular 仍按 r43c 的通道写。
- 动画（30 fps）：
  - empty：静态，摆臂收起。
  - ready：120 帧循环，4 个液氧排气烟团从一级顶部冒出，下沉后顺风飘散，首尾无缝。
  - launch：360 帧，12 秒，时间线如下：
    - 第 12 帧顶臂开始收，第 40 帧二级臂开始收，都用 back-out 缓动。
    - 第 60 帧点火，尾焰先闪一下再长满，三频叠加闪烁。
    - 第 60~90 帧夹持期间箭体微震。
    - 第 90 帧起飞，一级臂带回弹收回；加速度 a = 2 + 3.2t m/s²，先慢后快。
    - t > 4 s 后缓慢转向东，最大 14°；尾焰随高度变长变宽。
    - 22 簇地面烟团从导流槽两端依次喷出，ease-out 扩散后飘升。10 簇尾迹烟团留在火箭经过的高度。
    - 第 250 帧后烟团逐渐消散；第 318~352 帧火箭远去缩小。
    - 末帧等于 empty 的姿态。
- 改动文件：
  - `gfx/models/NSP/launchpad/` 下的 mesh、3 个 anim、3 个 dds。
  - `NSP_launchpad_anims.asset` 和 `gfx/entities/NSP_launchpad.asset`（只改了注释）。
- 实机检查：
  - 颜色和贴图细节是否正常。
  - 比例：entity scale 还是 1.0，场地直径约 5 格。
  - ready 的排气循环。
  - launch 是否顺滑，播完是否停在空架。
  - error.log 里有没有 bone 数或 mesh 相关报错。42 根骨骼如果超限，就把烟团减半。

---

## 2026-10-21 · 第 43c 轮 · 发射架模型发白

- 实测（截图）：r43b 之后模型已经出现在卡纳维拉尔角，但整体是纯白色块。
- 原因：贴图通道和 HOI4 的约定不一致。对照 Millennium Dawn 的 `shuttle_normaltex.dds` 和 `shuttle_speculartex.dds`（解码后统计）：
  - 法线图 ≈ (126,125,0,125)，B=0，A≈128；我们原来写的是 (128,128,255,255)。
  - 高光图全是 0；我们原来 A=255，RGB 在 15~160 之间。
- 修复：
  - `nsp_launchpad_normal.dds` 改成纯色 (128,128,0,128)。
  - `nsp_launchpad_specular.dds` 改成全 0。
  - diffuse 调色板没动。
  - `nsp_r40_blender/export_pdx.py` 同步修改，以后重新导出也是这个结果。
- 实机检查：火箭应为白和黑，塔架橙色，平台灰色。如果还是白的，就是 diffuse 或光照的问题，再往下查。

---

## 2026-10-21 · 第 43b 轮 · 发射架模型落点修复

- 实测（game.log）：三个决议都依次出现 clicked → apply → EXISTS，说明建筑确实建出来了；error.log 没有 NSP、mesh、mapbuildings 相关报错，但地图上看不到模型。
- 判断：
  - `map/buildings.txt` 末列不是省号。TNO 的 bunker 等省级建筑这一列全是 0，海军类填的是相邻海省。
  - 引擎按坐标判断落在哪个省。原来的坐标 1415/1664 是估出来的，很可能不在 17301 里（甚至可能在海上）。
- 修复：照 bunker 的写法，把州 366 的 21 个 bunker 坐标各复制一行，三个建筑共 63 行，末列都填 0。这样 17301 那一行一定在。
- 实机检查：
  - 模型应该出现在卡纳维拉尔角那个省的 bunker 位置。
  - 太小就把 `NSP_launchpad.asset` 里的 scale 调大；位置想挪的话用 nudger 改 17301 那一行。

---

## 2026-10-21 · 第 43 轮 · 地图发射架重写（照 Millennium Dawn JFK 航天飞机发射）

- 用户要求删掉 r41/r42 的写法，照 wiki 或其他模组重写。
- 先例：Millennium Dawn 的 JFK 航天飞机发射：
  - `common/buildings/01_landmark_buildings.txt`：`landmark_shuttle` / `landmark_shuttle_launch`
  - `common/scripted_effects/00_spaceshuttle.txt`：`launch_rocket` / `reset_launch_rocket`
  - `gfx/entities/landmarks.asset` / `landmarks.gfx`
  - `gfx/models/buildings/landmarks/MD_animation_landmark.asset`：动画 `file` 只写文件名
- 重写的文件：
  - `NSP_launchpad_buildings.txt`：字段照 MD 地标抄，不用自定义 spawn_point。
  - `NSP_launchpad_effects.txt`：照 MD 写法，在州 366 scope 里执行：
    - `if NSP_pad_x > 0` → `remove_building` 加 `province = 17301`；
    - `add_building_construction` 加 `instant_build`、`province = 17301`。
    - 去掉 `NSP_pad_state` 变量和 `var:` scope，州号、省号都写死成字面量。
  - `NSP_launchpad.gfx`：加 `meshsettings`，把 shader 覆盖成 `PdxMeshAdvanced`。
  - `NSP_launchpad.asset`：launch entity 照 MD 写成 `default_state = "move"`，`looping = no`。
- `map/buildings.txt`：三行建筑名，末列填省 17301，文件结尾不留换行。
- 探针（写进 game.log）：
  - 决议 complete_effect：`NSP pad decision N clicked`
  - apply：`NSP pad apply` 和 `NSP pad: x EXISTS`
- 实机检查：
  1. 点决议后 game.log 是否有 clicked → apply → EXISTS 三行。
  2. 点省 17301，看有没有图标。
  3. 地图上看模型。
  - 有 clicked 没 apply：effect 文件加载失败，看 error.log。

---

## 2026-10-21 · 第 42c 轮 · 探针：发射架什么都没出现

- 用户反馈：r42b 地图上和州面板都没有发射架。
- `NSP_pad_apply` 加了 game.log 探针：
  - `NSP pad apply: in state ... mode ...`
  - `NSP pad: <状态> EXISTS in 17301`
  - `NSP pad apply done ...`
- 判断：
  - 没有任何 `NSP pad` 行 → 决议或 daily 没调用到。
  - 有 apply、没有 EXISTS → `set_building_level` 没建出来。
  - 有 EXISTS → 建筑在，问题出在模型或坐标。
- 注意：`only_display_if_exists` 的图标只在省份地形面板显示（点 17301 那个省），不在州的建筑列表里。

---

## 2026-10-21 · 第 42b 轮 · 修复动画找不到、spawn 不认

- **动画 `Failed to find animation`**
  - 原因：按 wiki Entity modding，animation 的 `file` 是相对本 `.asset` 所在目录的路径。r41 写的是完整路径，r41e 又把声明挪到 gfx/entities，两次都报错。
  - 修复：声明放回 `gfx/models/NSP/launchpad/NSP_launchpad_anims.asset`，只写文件名；entities 的 .asset 里删掉这三行。
- **`Building NSP_pad_spawn doesn't have an entity` / `mesh entity doesn't exist`**
  - 原因：引擎没认自定义 `spawn_points`。
  - 修复：去掉 `spawn_point` 和 `spawn_points` 块，`map/buildings.txt` 改回三行建筑名。末列 province 改为 17301，像 bunker 等省级建筑一样。
- **`line 140527 invalid arguments count`**
  - 原因：文件结尾多了一个空行。
  - 修复：去掉结尾换行，和 TNO 原文件一致。
- 不用管：`PdxMeshAdvancedAnim`，是原版/TNO 坦克履带 shader 的已知报错，和发射架无关；其余 music、loc collision、frontend 报错同样无关。
- 实机检查：上述报错消失后，看模型和动画是否正常。

---

## 2026-10-21 · 第 42 轮 · 发射架改成地标式省级建筑

- 原因：用户想照原版地标（Götterdämmerung landmark）的做法，不占建筑栏，也不在州面板常驻三行。
- `common/buildings/NSP_launchpad_buildings.txt`
  - 三个建筑统一改为 `is_buildable = no`、`province_max = 1`、`only_display_if_exists = yes`、`disable_grow_animation = yes`、`spawn_point = NSP_pad_spawn`。
  - 新增 `spawn_points { NSP_pad_spawn = { type = province max = 1 disable_auto_nudging = yes } }`。
- `common/scripted_effects/NSP_launchpad_effects.txt`
  - `NSP_pad_apply` 改为在州 scope 里执行 `set_building_level ... province = { id = 17301 }`。
  - 清除用 `level = 0`，因为 remove_building 没有 province 参数。
- 删除隐藏科技 `NSP_launchpad_gate`。
  - 文件移到 `work/nsp_r42_quarantine/`。
  - 删除对应 loc 两行。
- `map/buildings.txt`
  - 删除 r41c 的三行。
  - 只追加一行：`366;NSP_pad_spawn;1415.00;10.15;1664.00;0.00;17301`。
- r41e 的修复保留：animation 声明在 `gfx/entities/NSP_launchpad.asset`。
- 实机检查：
  - 模型是否显示。若 error.log 有 `not over the land`，或模型不显示，可能是坐标不在 province 17301 内，需要用 nudger 重取。
  - 17301 若已有 naval_base 等省级建筑，模型可能不渲染，需换一个省。
  - 州面板只显示一个发射架图标。
  - 调试决议：空 / 待命 / 发射 / 恢复自动。

---

## 2026-10-21 · 第 41e 轮 · 修复：找不到发射架动画

- error.log：`pdxmeshtype.cpp:607 Failed to find animation "NSP_launchpad_empty/ready/launch_anim"`。
  - 原因：动画声明放在 `gfx/models/NSP/launchpad/NSP_launchpad_anims.asset`，游戏没读这个子目录的 .asset。
  - mesh 加载时找不到动画名。
- 修复：3 行 `animation = {}` 移到 `gfx/entities/NSP_launchpad.asset` 顶部，删除原文件。`.anim` 文件位置不变。
- 实机检查：这 3 条报错消失，且没有新的 `.anim` 读取报错。

---

## 2026-10-21 · 第 41d 轮 · NASA 调试决议

- 新增 `common/decisions/categories/NSP_debug_categories.txt`：分类 `NSP_debug_category`，`visible = is_debug`，`allowed = tag USA`。
- 新增 `common/decisions/NSP_debug_decisions.txt`：5 个决议，费用 0，可重复，AI 不会选。
  - 发射架：空 / 火箭待命 / 发射（强制切换并加 flag `NSP_pad_debug_lock`，每天的任务条件不再覆盖）。
  - 发射架：恢复自动（清除 flag，立即按任务阶段重算）。
  - 完成所有研发（调用 `NSP_rd_debug_all`）。
- `NSP_launchpad_effects.txt`：
  - 重排为先定义后调用（init → apply → update_auto → update → debug）。
  - `NSP_pad_update` 被锁定时跳过自动判断。
- loc：分类和 5 个决议的名称与描述。
- ⚠ 待实机确认：同一 tick 内「拆掉再建」同一种建筑（连点发射）是否会重建模型。如果动画不重播，先点「空」再点「发射」。
- ⚠ 决议图标用的是原版 `generic_research`；TNO 里不显示的话再换。

---

## 2026-10-21 · 第 41c 轮 · 发射架地图坐标

- 新增 `map/buildings.txt`：复制用户上传的 TNO 原文件（140,524 行，CRLF，无 BOM），在末尾追加 3 行。
  - 三个建筑共用一个坐标：`366;NSP_pad_xxx;1415.00;10.15;1664.00;0.00;0`。
  - 位置在 Florida 东海岸，Daytona 海军基地（1412,1670）以南、海岸碉堡（1417,1656）以北，大致是卡纳维拉尔角。
  - 高度 10.15 参照附近建筑。
  - 坐标按州内现有建筑的经纬度插值推算：低分辨率的 provinces 图颜色不准，无法按 province 17301 精确取点。
- ⚠ 这是 TNO 整文件覆盖。TNO 更新 buildings.txt 后，需要用新版原文件重新追加这 3 行，否则会丢失 TNO 新增的建筑位置。
- 实机检查：
  - 模型是否在卡纳维拉尔角附近、大小是否合适。
  - 位置偏的话用 nudger 拖动后保存，或直接改这 3 行。
  - 尺寸改 `gfx/entities/NSP_launchpad.asset` 的 scale。
  - 想直接看效果：在 文档/Paradox Interactive/Hearts of Iron IV/ 下新建 `pad.txt`，写入 `NSP_pad_debug_2 = yes`，然后在控制台（先 `tag USA`）执行 `run pad.txt`。

---

## 2026-10-21 · 第 41b 轮 · 发射架州 ID

- `NSP_launchpad_effects.txt`：`NSP_pad_state` 默认值从首都改为 366（TNO 的 Florida，卡纳维拉尔角 VP 在 province 17301）。用户上传的 states 里没有 map/buildings.txt，坐标仍待补。
- 旧存档里已有 `NSP_pad_state` 变量的不会被覆盖；需要时在控制台执行 `set_var NSP_pad_state 366`。

---

## 2026-10-21 · 第 41 轮 · 地图 3D 发射架：空 / 火箭 / 发射 三状态

用户澄清：不接 GUI，要把发射台放在地图地块上，有「空架 / 带火箭 / 发射」三个状态，用条件控制动画。

- 撤掉 r40 的 GUI sprite：删除 `gfx/interface/NSP/launch/`、`interface/NSP_r40_launch.gfx`。
- 模型：
  - 由 `work/nsp_r40_blender/export_pdx.py` 用 io_pdx_mesh 导出（Blender 4.3 headless）。
  - 产物放在 `gfx/models/NSP/launchpad/`：
    - `nsp_launchpad.mesh`：带 29 根骨骼（root / arm0 / arm1 / rocket / plume / smoke00–23），材质 PdxMeshStandard。
    - 3 张 32×32 调色板贴图：diffuse / normal / specular。
    - 3 段动画：`empty`、`ready`、`launch`。
  - `launch` 共 216 帧（9 秒）：点火 → 第 18 帧起摆臂回收 → 第 30 帧起飞（a = 20 m/s²）→ 第 150 帧火箭消失 → 烟雾在第 210 帧前散尽。
  - 已用插件回读 `.mesh` / `.anim` 渲染核对。
- 新增 `gfx/entities/NSP_launchpad.gfx`（pdxmesh）、`gfx/models/NSP/launchpad/NSP_launchpad_anims.asset`（animation）和 `gfx/entities/NSP_launchpad.asset`。
  - 三个 entity：`building_NSP_pad_empty` / `_ready` / `_launch`。
  - launch 的 `looping = no`：模型出现时播一次，然后停在空架。
- `common/buildings/NSP_launchpad_buildings.txt`：三个建筑。
  - `show_on_map = 1`、`always_shown`、`state_max = 1`，不占建筑槽，没有任何效果。
  - 用科技 `NSP_launchpad_gate`（allow = no）锁住，玩家和 AI 都不能手动建造。
- `common/scripted_effects/NSP_launchpad_effects.txt`：`NSP_pad_update` 每天由 `NSP_daily_tick` 调用。
  - 本国任务中有「发射」阶段（phase 4）→ 发射。
  - 否则有「总装」阶段（phase 3）→ 火箭待命。
  - 否则 → 空架。
  - 只在状态变化时拆旧建新：模型会重建，所以发射动画从头播。
  - 调试用 `NSP_pad_debug_0/1/2`。
- 所在州：变量 `NSP_pad_state`，默认取首都。⚠ 需要换成 TNO 里卡纳维拉尔角所在州的 ID。
- ⚠ 必须给这三个建筑在 `map/buildings.txt` 里配坐标，否则地图上不显示。TNO 的 buildings.txt 是整文件，需要复制一份追加：
  - 每个建筑一行：`州ID;NSP_pad_empty;X;Y;Z;旋转;0`
  - 坐标可用 nudger 生成。
- ⚠ 未实机验证：
  1. 尺度（entity 的 scale）。
  2. 调色板贴图在 PdxMeshStandard 下的效果。
  3. `looping = no` 是否停在最后一帧。
  4. `hide_if_missing_tech` + 无 folder 科技是否报错。

---

## 2026-10-21 · 第 40 轮 · Blender 建模：发射台 + 通用两级火箭（素材预备）

用户要求：用 Blender 建发射台和通用火箭模型，留给以后的火箭发射动画用。

- 源文件在 mod 外：`work/nsp_r40_blender/`。
  - `build_scene.py`：参数化建模脚本，可重复运行；改顶部参数即可换火箭外形。
  - `nsp_launchpad_rocket.blend` / `.glb`
  - 渲染帧
- 模型内容：
  - 发射台：台基、导流槽、导流器、带中孔的发射台架、4 个压紧装置、52 m 橙色桁架脐带塔（带 2 根摆臂）、水塔、避雷针。
  - 火箭：一级 24 m、级间段、二级 9 m、尖拱整流罩，直径 3.7 m，4 台发动机，带尾翼，总高约 43.6 m。
  - 所有火箭部件都挂在 `Rocket_Root` 下。
- 动画（24 fps，第 1–120 帧）：
  - 第 1 帧点火，尾焰在 12 帧内长满。
  - 第 18 帧起，两根摆臂依次回收。
  - 第 30 帧起飞，按 z = ½·6·t² 加速上升。
  - 两侧导流槽持续喷出烟团。
- 渲染：Cycles，透明背景。产出静止帧和每 4 帧一张的 30 帧序列。
- mod 内新增（未接入 GUI，不影响现有界面）：
  - `gfx/interface/NSP/launch/nsp_launch_idle.dds`：192×288
  - `gfx/interface/NSP/launch/nsp_launch_seq.dds`：30 帧 × 192×288，横排
  - `interface/NSP_r40_launch.gfx`：`GFX_NSP_launch_idle` / `GFX_NSP_launch_seq`（noOfFrames = 30）
- 接入时注意：frameAnimated 重播问题见 r27–r31 结论。可以用 `_click_enabled` 切换触发 AnimationTime 的方案，也可以用 frame 属性逐帧推进。

---

## 2026-10-21 · 第 39 轮 · 地图只留美国站点；Mission Control「国际」改为「建设」

用户要求：地图站点只保留美国的；「国际」页签改为「建设」，暂时没有内容。

- `interface/NSP_space.gui`：注释掉非美国站点：百慕大、马德里、加那利群岛、卡那封、日本。
  - 保留：卡纳维拉尔角、休斯敦、白沙、范登堡、夏威夷、关岛。
  - 只做了注释，没删除行，坐标都还在。
- loc `NSP_MC_INTL`：「国际」→「建设」（key 不变）。
- `NSP_mc_sync`：
  - 页签 1 不再填任何条目，显示为空。
  - 旧存档里的国际任务（`NSP_missions_intl`）并入「本国」页显示，避免任务消失。

**待测**：
1. 地图上只剩 6 个点。
2. 点「建设」后列表为空、无报错。
3. 切回「本国」，任务正常显示。

---

## 2026-10-21 · 第 38b 轮 · 调试按钮改为照常加太空科技

用户纠正：一键完成应该加太空科技。

- `NSP_rd_debug_all` 现在逐项执行正常完成流程：`NSP_tech += NSP_rd_tech^p`，并调用 `NSP_rd_on_complete`（一次性奖励）。
- 之后用 `while_loop_effect` 连续升级，直到太空科技低于门槛。每级照常获得：等级 +1、门槛 +50、民意 +3、预算 +500。
- 升级时不逐级弹 `nsp.11`，避免连弹多个通知。
- 同步更新 tooltip。

**待测**：点击后太空科技等级连升多级，科技条显示正常，`error.log` 无 NSP 报错。

---

## 2026-10-21 · 第 38 轮 · 研发页调试按钮：一键完成全部研发

用户要求：在研究面板加一个调试按钮（仅 debug 可见），一键完成所有科技。

- `interface/NSP_rd.gui`：页眉左上角新增 `NSP_rd_debug_all`，坐标 x=14 y=26，复用 `GFX_NSP_rd_tab` 贴图（150×28），按钮文字为「DEBUG 全部完成」。
- `NSP_space_rd_guis.txt`（gen_rd.py 生成的文件，本轮手动加了两行，均标注 r38）：
  - `NSP_rd_debug_all_visible = { is_debug = yes }`
  - 点击时调用 `NSP_rd_debug_all`
- 新增 `common/scripted_effects/NSP_rd_zdebug_effects.txt`，定义 `NSP_rd_debug_all`：
  - 把所有未完成项目设为已完成、进度设为 100。
  - 载人航天中心的研发槽奖励照常发放。
  - 清空研发队列。
  - 重算解锁，刷新界面。
  - 不扣预算，不加太空科技，不弹通知。
- 新增 localisation：`NSP_RD_DEBUG_ALL` / `_TT`。
- ⚠ 如果以后重跑 gen_rd.py，需要把这两行同步进去。

**待测**：
1. 以 `-debug` 启动时按钮可见，普通启动时不可见。
2. 点击后所有卡片变绿，队列清空。
3. 规划器里土星 V 等全部可选。

---

## 2026-10-21 · 第 37 轮 · 研发进度、任务阶段改为每日结算

用户反馈：研发抽屉里的「预计 N 天后完成」要七天才变一次。原因是进度只在 on_weekly 里推进，GUI 本身不是按周刷新的。

- `on_actions`：on_daily（tag = USA，且已初始化）新增调用 `NSP_daily_tick`。
- `NSP_daily_tick`（原 `NSP_weekly_tick` 的内容）：
  - 研发：改调 `NSP_rd_daily`，每天进度 +100/工期。总速度和原来的每周 +700/工期一样。
  - 任务：`NSP_advance_mission` 由每周 -7 天改为每天 -1 天。阶段溢出、完成结算的逻辑不变。
  - 最后调用 `NSP_recalc_home` 刷新面板。
- `NSP_weekly_tick` 现在只负责经济（`NSP_econ_weekly`）和刷新。
- `NSP_rd_daily` 写在 `NSP_rd_unlock_effects.txt` 里，由 `nsp_r35/gen.py` 生成：
  - 完成判定、状态、科技、研发槽的处理沿用 `NSP_rd_weekly`。
  - 完成时触发通知、重算解锁、检查科技升级。
  - ⭐ 不再把太空科技截到上限，升级时溢出部分会保留。
- `NSP_rd_weekly`（gen_rd.py 生成）和 `NSP_rd_post_weekly` 保留定义，但已不再被调用。
- gen.py 现在从 r35 前的备份读取原始解锁文字，重复运行不会叠加。

**待测**：
1. 「预计 N 天后完成」每天减 1。
2. 研发进度条每 1–3 天前进一格。
3. Mission Control 的任务进度条每天推进。
4. 拨款仍是每周到账一次。
5. 一周完成的研发量与以前一致。

---

## 2026-10-21 · 第 36 轮 · 各计划预算改为 NASA 统一预算

用户要求：各计划不再有独立预算，统一使用 NASA 预算。

- `NSP_recalc_home`：
  - `NSP_cur_budget` 改为直接取 `NSP_space_budget`（原为 `NSP_prog_budget^P`）。
  - 预算条 `NSP_f_budget` 改为「当前预算 / 历史峰值 `NSP_budget_peak`」，峰值会随拨款上涨自动更新。
- localisation：
  - `NSP_BUDGET_TEXT` 改为「NASA 预算：$xxx 百万」。
  - `NSP_BUDGET_TT` 改为说明统一预算、每周拨款，以及进度条的含义。
- 切换计划页签时，预算显示保持不变。
- 任务和研发本来就从 `NSP_space_budget` 扣款，扣款逻辑无需修改。
- `NSP_prog_budget` / `_max` 数组仍会初始化，但已不再被读取（保留是为了兼容老存档）。

**待测**：
1. 三个计划页签显示的是同一个预算数字。
2. 开始任务或研发后，预算数字和进度条都会下降。
3. tooltip 显示的数值正确。

---

## 2026-10-21 · 第 35 轮 · 内容实现：研发解锁、被动加成、经济、科技升级、轨道筛选

用户反馈：GUI 只是骨架，科技解锁不了任何东西。

### 1. 研发 → 规划器解锁（核心）
- 新增 `common/scripted_effects/NSP_rd_unlock_effects.txt`，由 `nsp_r35/gen.py` + `unlock_table.py` 生成。文件名排在 NSP_rd_effects 和 NSP_space_effects 之间，保证调用顺序。
  - 每个研发项目最多两条效果，存在 `NSP_rd_uk1/uv1/uk2/uv2` 中（88 格，含占位格）。
  - kind 含义：1 载荷 / 2 火箭 / 3 目的地 / 4 修正 / 5 火箭可靠性 / 6 载人可靠性 / 7 无人可靠性 / 8 成本-% / 9 工期-% / 10 一次性拨款 / 11 一次性民意 / 12 发射台。
  - `NSP_rd_apply_unlocks`：根据所有「已完成」项目重算 `NSP_pl_unl` / `NSP_ve_unl` / `NSP_dest_unl` / `NSP_mod_unl`，以及被动加成 `NSP_rd_b_vrel/prel/probe/cost/time`。重算是幂等的，老存档可直接用。
  - 加成上限：成本、工期最多 -40%；可靠性最多 +25。
  - 基础开放：近地轨道、地月转移；发射场全部开放。
- 主要映射：
  - 载荷：双子星←13，阿波罗←17，TIROS←41，水手←47。
  - 火箭：泰坦 IIIC←3，泰坦 II←2，土星 IB←10，土星 V←11。
  - 目的地：MOL 2←4（阿金纳），GEO←42，极地←43，逃逸←48。
  - 修正：捆绑助推器←3，半人马←5，改进型发动机←7，先进双子星←14，对接←32，EVA←23，太阳能板←40，燃料电池←26。
  - 其余项目给可靠性、成本、工期加成，或一次性拨款 / 民意。
- 规划器（`NSP_space_effects.txt` / `NSP_space_triggers.txt`）：
  - 载荷 / 火箭左右切换时跳过未解锁项。
  - 调色板只显示已解锁的修正。
  - 未解锁目的地显示为禁用行，并带 tooltip。
  - 载人（双子星 / 阿波罗）去地月转移需要研发 30「月球返回再入」。
  - 土星 IB 需要研发 52（LC-34/37），土星 V 需要研发 53（39 号复合体）。
  - 开始任务时再检查一次载荷和火箭是否已解锁。
  - 被动加成计入可靠性、成本和工期。
  - ⚠ 规划器默认目的地从地月转移改为近地轨道，也不再预装「先进双子星改装」（否则开局默认方案就不合法）。
- 研发抽屉里的「解锁」文字改为显示真实效果（`NSP_RD_UNLOCK_*`），原文件备份在 `nsp_r35/NSP_rd_l_simp_chinese.yml.bak`。

### 2. 周结算新增 `NSP_rd_post_weekly`（紧跟 NSP_rd_weekly 调用）
- 本周完成的项目（读 `NSP_rd_done_tmp`）：执行一次性效果，并弹出事件 nsp.10「研发完成」，显示最后完成的一项和本周完成总数。
- 重算解锁。
- 太空科技升级：达到上限后等级 +1，进度扣除上限，下一级上限 +50，拨款 +500M，民意 +3，弹出事件 nsp.11。任务成功额外 +4 太空科技。
- 经济：
  - 民意每周向 50 回落 1%。
  - 国会支持 `NSP_support` 每周向民意靠拢 2%。
  - 每周拨款 `NSP_income` = 30 + 支持度 × 0.8（M），计入 `NSP_space_budget`。
  - 「国会」按钮的 tooltip 现在显示支持度和每周拨款。

### 3. 轨道行
- 点击某一行：Mission Control 只显示目的地落在该行的任务；再点一次取消筛选。
- 行的选中帧表示「正在筛选」。切换视图时清除筛选。

### 未改动
- `NSP_rd_effects.txt`（gen_rd.py 生成）没有动。⚠ 研发完成时太空科技仍会被那里的 clamp 截到上限，溢出部分会丢失；如果要保留溢出，需要改 gen_rd.py。
- 计划页签 3–6、计划预算条、民意按钮点击仍是占位。

**待测**：
- 开新档：规划器里土星 IB/V 切不到；GEO、极地显示禁用。
- 研发完成后弹出通知，对应项目变为可选。
- 等级满后升级。
- 国会 tooltip 显示的数值正确。
- 点击轨道行能筛选任务。
- 老存档：打开规划器或过一周后，解锁表自动生成。
- 检查 error.log。

---

## 2026-10-21 · 第 34 轮 · 研发抽屉（NSP_rd_drawer）减负

用户反馈：内容太拥挤。抽屉尺寸不变（1055×146），只调间距和视觉权重。
- 四栏重新分配：① 信息 16..346 | ② 线稿 370..613 | ③ 操作 637..891 | ④ 队列 915..1041。栏间留 12px，中间放两端渐隐的竖线 GFX_NSP_rd_vdiv_r34（x=358/625/903）。
- ① 删除横分隔线 NSP_rd_d_div；描述 16→14 号（两行），宽 330。
- ③ 删除三个数值格方框 NSP_rd_cell_0..2，改为无框三栏（各 84 宽），中间用 GFX_NSP_rd_sdiv_r34 竖线分隔；标签改 §g 灰色，数值仍为 18 号。
- ④ 标题 18→16 号；条目名 16→14 号，宽 126；行距 36（y=38/72/106）。
- 文件：NSP_rd.gui 抽屉段（旧段存 nsp_r34/old_drawer.txt）；新增 interface/NSP_r34.gfx 和 gfx/interface/NSP/rd/nsp_rd_{vdiv,sdiv}_r34.dds；NSP_rd yml 三个标签键。scripted_gui 没有改动，元素名、frame/visible 绑定都不变。
- 旧精灵 GFX_NSP_rd_cell 仍保留，只是不再引用。

**待测**：描述最长的项目两行能否放下（放不下会被截断）；队列第三行百分比是否贴底。

---

## 2026-10-21 · 第 33 轮 · 底栏「科技等级」+「局长」面板重设计（参考用户第 3 图）

- 科技等级（NSP_tech_panel）：
  - 进度条换成 GFX_NSP_tech_bar_r33：268×24×21 帧，双线框，空心刻度（亮 = 已达成，暗 = 未达成），位置 34,80。
  - 圆环换成 GFX_NSP_tech_ring_r33：44×44 深色实心 + 青环，压在条两端，位置 12/279,70。
  - 等级数字改为 aldrich_24。数值去掉 §Y，与参考图一致。
- 局长（NSP_director_panel）：
  - 肖像 scale 0.4→0.5，位置 12,13；双线框 GFX_NSP_dir_frame_r33（86×113，位置 8,9）。
  - 原名牌容器 NSP_director_tag 删除，改为三格名牌 GFX_NSP_dir_head_r33（222×40，位置 104,10）；label/name 文本框直接放在面板里，位置 134,11 / 134,26。
  - 人气条换成 GFX_NSP_pop_bar_r33：222×22×21 帧，青色 > 从左推进，红色 < 从右推进，位置 104,58。
  - 两个按钮改用括号式页签 GFX_NSP_dir_tab_r33（110×36，位置 104/216,88）；「民意」改 §D。
- 文件：新增 interface/NSP_r33.gfx 和 6 张贴图（gfx/interface/NSP/style/*_r33.dds，生成脚本 nsp_r33/gen.py）；修改 NSP_space.gui 两段和 yml 两个键。旧精灵未删，只是不再引用。
- frame 驱动不变：NSP_f_tech / NSP_f_popularity。

**待测**：圆环里的数字是否垂直居中；人气条 50% 时交界位置是否正确；肖像 0.5 倍是否清晰。

---

## 2026-10-21 · 第 32 轮 · 地图下方（视图页签 + 轨道列表）重设计

用户反馈：这一块的排版和设计不好看。原来的问题：行宽 500、x=20，跟地图（30..510）对不齐；页签浮在最底下，和列表之间空了约 40px；页签居中却不贴边；任务数挤在名称后面。
- 新布局（NSP_map_col 内坐标）：
  - 视图页签：三格 160×26 无缝拼接，x=30/190/350，y=286，贴在地图底边。选中格有底部亮条，顶部小三角指向地图。
  - 段标题：「轨道目标」（aldrich_14，§g）在 30,318；分隔线 GFX_NSP_rule_r32 在 110,325。
  - 轨道行：480×30，右上切角，x=30，y=340/376/412。行内左侧 30px 编号格（01/02/03）；名称在 x=72；任务数右对齐在 336..486（「§Y n§! §g项任务」）；右端是箭头。选中行左侧有亮条，边框也提亮。
- 文件：
  - 新增 `interface/NSP_r32.gfx`，3 个精灵，不挂 buttonstate.lua。
  - 新增贴图 `gfx/interface/NSP/style/nsp_view_tab_r32.dds`、`nsp_orbit_row_r32.dds`、`nsp_rule_r32.dds`（生成脚本 nsp_r32/gen.py）。
  - `interface/NSP_space.gui`：替换 NSP_orbit_* / NSP_view_* 这一段，新增 NSP_orbit_hdr / _rule / _N_idx / _N_n。
  - yml：`NSP_ORBIT_N_TEXT` 只保留名称；新增 `NSP_ORBIT_N_N`、`NSP_ORBIT_IDX_N`、`NSP_ORBIT_HDR`。
- 帧约定和 scripted_gui 没变：frame 1 = 未选中，2 = 选中，仍由 NSP_f_view_N / NSP_f_orbit_N 驱动。
- 旧精灵 GFX_NSP_tab_view2、GFX_NSP_orbit_row_v19 保留未删，不再被引用。

**待测**：页签选中态、行选中态是否正常切换；文字纵向是否居中（不居中就微调 y 的 +6）。

---

## 2026-10-21 · 第 31 轮 · 聚焦动画：常驻按钮 + click_enabled 切换状态

r30 实机视频：调试角标全程是绿的，说明 AnimationTime 有效；但每颗行星的进入、退出动画各只播第一次（第二次直接跳到终态）。
→ 结论：AnimationTime 只在按钮**状态切换**时更新。动态列表条目也不是真的重建，而是被复用。
- 改动：
  - `interface/NSP_focus_v22.gui`：删掉 16 个 gridbox 和 16 个条目容器。新增常驻窗口 `NSP_focus_fx_window`（310,96，声明在 in/out 窗口之前），里面直接放 `NSP_fin_<p>` / `NSP_fout_<p>` 16 个 buttonType。
  - `common/scripted_guis/NSP_space_guis.txt`：新增条目 `NSP_focus_fx`（只看太阳系视图，不看 fmode，dirty = NSP_dirty）。triggers 里：
    - `NSP_fin_<p>_click_enabled` = focus=p 且 fmode=1
    - `NSP_fout_<p>_click_enabled` = focus=p 且 fmode=2
    同时删掉 in/out 条目里的 dynamic_lists。`NSP_fanim_refresh` 照旧被调用，数组现在没有用处了，无害。
  - `nsp_focus_bt.shader` / `nsp_focus_out_bt.shader`：Effect Disable 改成 `PixelShaderNSPHidden`（全透明）；删掉调试角标。
- 原理：禁用 → 启用是一次状态切换，引擎在这一刻刷新 AnimationTime，shader 的 t 从 0 开始。

**✅ 实机确认（2026-10-21）：每次进出都会重播。** 原测试项：同一颗行星连续进出 3 次；进出过程中换别的行星。若动画画在了地图边框上面，说明窗口绘制顺序和预期相反，需要调换。

---

## 2026-10-21 · 第 30 轮 · 聚焦动画改用 AnimationTime（buttonType）

用户提供了原版 `sprite_animation.fxh`：它服务的是 spriteType 的 `animation = { }` 块（scrolling / rotating / pulse），与帧动画无关。原版里找不到 `buttonstate.lua`（引擎把它映射到 gfx/FX/buttonstate.shader）。
- 依据：`buttonstate.fxh` 的 `AnimationTime`，在 Clausewitz 的 buttonstate 里用于按钮状态切换后的渐变（`Time - AnimationTime` = 进入当前状态后经过的秒数）。v27 把它用在 iconType 上，iconType 没有按钮状态，所以无效。
- 改动：
  - 新增 `gfx/FX/nsp_focus_bt.shader` 和 `nsp_focus_out_bt.shader`，复制自原 shader，时间轴改为 `saturate( ( Time - AnimationTime ) / 0.8 )`。拿不到有效起点时直接显示终态。
  - `interface/NSP_focus_v22.gfx` 新增 16 个普通 spriteType：`GFX_NSP3D_focusbt_<p>` / `GFX_NSP3D_focusoutbt_<p>`（20 格，固定第 1 格）。
  - 动态列表条目里的 `NSP_fin_<p>` / `NSP_fout_<p>` 由 iconType 改成 buttonType（alwaystransparent，scale 2）。每次点击都会重建条目，相当于新按钮、新起点。
  - 旧 frameAnimated 精灵和旧 shader 保留，不再被引用。
- 🔧 调试角标：聚焦画面左上角 8×8 px。绿 = AnimationTime 有效，红 = 无效。确认后删除。

**待测**：连续进出同一颗行星；看角标颜色。
- 绿且每次都播 → 完成。
- 绿但只播第一次 → AnimationTime 只在状态切换时更新，下一步改成可悬停按钮。
- 红 → 按钮静止时引擎不给 AnimationTime，同上。

---

## 2026-10-21 · 第 29 轮 · 撤销 r28 shader

用户反馈：r28 动画直接没了。
- 结论：UV 不按帧裁剪，k1 恒为 0，帧序号只来自 `Offset.x`。第二次不播，说明引擎的帧动画本身没有重启。已排除的办法：窗口显隐（v22）、A/B 精灵（v25）、AnimationTime 用在 iconType 上（v27）、动态列表重建条目（r27）。
- 修复：shader 恢复 `max( k1, k2 )`，至少第一次能播。
- 下一步需要原版 `gfx/FX/buttonstate.lua` 和 `gfx/FX/sprite_animation.fxh`，确认 AnimationTime / Offset 的真实含义，再定方案（备选：buttonType 状态切换计时；容器 show 动画当计时器）。

---

## 2026-10-21 · 第 28 轮 · 聚焦动画重播：shader 帧序号的根因

用户反馈：r27 仍然只播第一次。查 Wiki（Graphical asset modding · frameAnimatedSpriteType）：`play_on_show` = 元素变为可见时开始播放。也就是说 v22 以来每次重新显示时动画很可能【确实重播了】，问题出在 shader：
- `nsp_focus.shader` / `nsp_focus_out.shader` 的时间轴原来是 `max( k1, k2 )`：k1 = UV 所在帧格（引擎按当前帧裁剪 UV），k2 = `Offset.x` 换算的帧。
- 重播时 k1 从 0 开始，但 k2 停在上次的末帧，所以 max 一直是 19，t = 1，直接显示终态。第一次能播，是因为 Offset 初始为 0。
- 修复：只用 k1。
- r27 的动态列表重建结构保留，作为双保险。

**待测**：同一颗行星连续进出 3 次以上；换一颗行星。如果动画变成完全不动（行星停在原位、背景不暗），说明 UV 不按帧裁剪，回报，我改回用 Offset 并做差值。

---

## 2026-10-21 · 第 27 轮 · 聚焦动画每次都重播 + 天体 tooltip 拆两层

**A. 聚焦动画只播第一次**（已试失败：v22 隐藏/显示窗口、v25 A/B 精灵切换、v27 shader 读 AnimationTime）
- 思路：play_on_show 只在元素【新建】时从第 0 帧播放。dynamic_lists 的条目在数组变化时会被销毁重建，因此改由动态列表承载动画图标。
- `interface/NSP_focus_v22.gui`：in/out 两个窗口里的 16 个 `NSP_fin_* / NSP_fout_*` iconType 换成 gridBox `NSP_fin_grid_<p>` / `NSP_fout_grid_<p>`（480×270，1 格）；文件末尾新增 16 个条目容器 `NSP_fin_entry_<p>` / `NSP_fout_entry_<p>`，图标原样放在里面（scale 2）。
- `common/scripted_guis/NSP_space_guis.txt`：`NSP_focus_in/out` 删掉 A/B properties 和 `_visible`，改成 dynamic_lists（数组 `NSP_fin_arr_1..8` / `NSP_fout_arr_1..8`，互斥）。1373 个点击 effect 里的 `NSP_anim_ab` 切换替换成 `NSP_fanim_refresh = yes`，8 个旧 `NSP_ss_<p>_click` 也补上。
- `common/scripted_effects/NSP_space_effects.txt` 顶部新增 `NSP_fanim_refresh`：清空 16 个数组，再按 NSP_fmode / NSP_focus 往对应数组里放一个递增的 `NSP_fanim_seq`。
- `gfx/FX/nsp_focus*.shader`：撤销 v27 的 AnimationTime，只用帧序号。
- `NSP_anim_sl.txt` / `NSP_anim_l_simp_chinese.yml` / `_b` 精灵已不再引用，暂时保留。
- 老存档：如果读档时正停在聚焦画面，要再点一次行星才会出现。

**B. tooltip 两层**
- `NSP_TT_<天体>` 只留名称、类型和操作提示（pdx_tooltip）；参数和说明移到 `NSP_TT_<天体>_D`（pdx_tooltip_delayed）。聚焦视图也一样：新增 `GetNSPFocusTTD` / `NSP_TT_FOCUS_D`。
- 两个 .gui 文件里 1375 处 pdx_tooltip 都补了 delayed。
- ⚠ `work/tt/add_body_tt.py` 已过时，别重跑。

**待测**
1. 同一颗行星连续进出 3 次以上，进入和退出动画每次都要播；换一颗行星也要播。
2. 悬停：先出短 tooltip，停留一会儿再展开详细参数。
3. 如果动画完全不显示：说明 gridbox 条目没生成，回报 error.log。

---

## 2026-10-21 · 第 26 轮 · shader 注释漏写 #

用户的 error.log 报：`Could not open file: gfx/FX/+`、`sprite_animation.fxh，取其`、`Time。`、`Includes`、`=`、`{`。
- 原因：`nsp_atmo.shader` 和 `nsp_clouds.shader` 第 9 行是注释，但行首漏了 `#`。引擎把它当成 Includes 语句解析，把这一行的每个词都当作要加载的文件名。结果是大气层和云层 shader 加载失败或表现异常（地球动态云、大气层）。
- 修复：补上 `#`。
- 同一份日志里其他报错（TNO_PostApoc / radio_tno_music 本地化、fow 贴图、frontendmainview、opening_screen 的 dds）都来自 TNO 本体或原版，与本 mod 无关。

---

## 2026-10-21 · 第 25 轮 · 太阳/月球 tooltip 修复

用户反馈：月球和太阳的 tooltip 不显示。
- 原因：`GFX_NSP3D_sun` / `GFX_NSP3D_moon` 在 `NSP_space.gfx` 的 spriteType 上写了 `alwaystransparent = yes`。r15 只删掉了 .gui 里 iconType 的透明属性，但 sprite 层的透明仍然生效，所以鼠标事件和 tooltip 都穿透了。
- 修复：仿照行星的做法，用隐形命中按钮承载 tooltip（nsp_hit.shader，贴图实心、画面不可见）。
  - `NSP_moon_hit`：150×150，(195,70)，月球视图（NSP_view = 1）。
  - `NSP_sun_hit`：48×14，(246,138)，太阳系视图（NSP_view = 2），且不在聚焦模式（NOT NSP_fmode = 1）。太阳命中区限制在水星轨道内侧，已用脚本确认不与水星命中块重叠。
  - iconType 上的 pdx_tooltip 已移除。shader 贴图的 alwaystransparent 保留，否则会挡住轨道点击。
- 新增文件：`gfx/interface/NSP/3d/nsp3d_hit_sun.dds`、`nsp3d_hit_moon.dds`。gfx 定义在 `NSP_orbit_v24.gfx`。
- `work/tt/add_body_tt.py` 里处理太阳/月球的那一段已作废，重跑脚本不会把旧写法加回来。
- 待实机：太阳 tooltip 的命中范围偏小（只有中心一条），如果觉得难以触发，可以加高，但会与水星轨道相交。

---

## 2026-10-21 · 第 24 轮 · 修复周结算的 remove_from_array 报错

用户的 error.log 报：`Invalid index to remove: NSP_space_effects.txt:507 remove_from_array`。
- 原因：`NSP_weekly_tick` 处理完成的任务时，会把任务 ID 同时从 `NSP_missions` 和 `NSP_missions_intl` 两个数组里删除，但任务只会在其中一个数组里，删不存在的值就报这个错。
- 修复：删除前先用 `is_in_array` 判断，在哪个数组里就只从哪个数组删。行为不变，只是不再刷报错。

- ✅ 用户实机确认：r24 中科技树可以拖动，鼠标滚轮可用，外窗口仍可拖动。拖动问题已关闭。

---

## 2026-10-21 · 第 23 轮 · 修复 GUI 全部消失（BOM）

用户反馈：「GUI 不见了」。error.log 报 Undefined GUI_TYPE NSP_topbar_window / NSP_home_window / NSP_home_body / NSP_planner_body，这几个窗口都定义在 NSP_space.gui 里。
- 原因：r20/r21 修改 `interface/NSP_space.gui` 时，用 utf-8-sig 写回文件，给它加上了 UTF-8 BOM，导致整份 .gui 解析失败。
- 修复：删除 BOM。
- ⛔ 规则：.gui / .gfx 一律无 BOM（只有 localisation yml 需要 BOM）。脚本写回文件时用 `encoding="utf-8"`，不要用 utf-8-sig。

---

## 2026-10-21 · 第 22 轮 · 照用户旧模组 DS_ovl_viewport 修树区拖动

用户提供了旧模组的 `DS_deep_state.gui`。里面 `DS_ovl_viewport` 在可移动主窗里实机能拖动平移。逐项对照后，差异如下：
- 视口 background：旧模组用原版 `GFX_tiled_window_transparent`。我们用的是 `GFX_NSP_scroll_bg`，它是普通 spriteType，被硬当 quadTextureSprite 用，**接不到鼠标事件**。拖动于是冒泡给外壳（r16 视频里整窗被拖走）。→ 已改成 `GFX_tiled_window_transparent`。
- 画布 `DS_ovl_canvas` 没有 background，上面的元素全部 `alwaystransparent = yes`。→ `NSP_rd_canvas` 去掉 background 和 min。年代、行标签文本框补上 alwaystransparent。
- 外壳保持 `moveable = yes`（r21）。

### 待实机
- 在空白网格上左键拖动能否平移，外窗是否仍可拖动。
- 卡片能否点击。

---

## 2026-10-21 · 第 21 轮 · 撤销 r20

用户明确要求：外窗口必须能拖动，里面的子窗口（科技树）也必须能拖动平移，两者同时生效。用户说他之前的模组就做到过。
- `NSP_home_window` 恢复 `moveable = yes`。
- 树区拖动平移仍未解决，已向用户要他旧模组里能用的那段 gui，照着它的结构改。

---

## 2026-10-21 · 第 20 轮 · 主外壳改为不可移动

用户：「窗口内还是无法鼠标点击拖动」（r19 画布子容器无效）。
- 原因判断：等同于「点击穿透」。各内容页背景是 alwaystransparent，空白处的左键按下会一路传到可移动外壳 `NSP_home_window`。外壳把拖动当成「移动窗口」接走，drag_scroll 收不到。
- 改动：`interface/NSP_space.gui` 中 `NSP_home_window` 改为 `moveable = no`（r19 预设的后备方案）。画布子容器、margin 保留。
- 代价：整个太空计划窗口不能再拖动位置。
- 待实机：空白网格上左键拖动能否平移；卡片和按钮照常可点。

---

## 2026-10-21 · 第 19 轮 · 撤销 r18 独立外壳；照原版加画布子容器修拖动

用户反馈（附视频）：「还是没法拖动……还莫名有了两个窗口」。

### 诊断
- 「两个窗口」：r18 切页时，主外壳上滑、R&D 外壳下滑，两个窗口同时出现在屏幕上。
- 拖动：外壳不可移动之后，左键拖动完全没反应。说明 r18 的「被外壳抢走」只是表象，问题出在 drag_scroll 容器本身。
- 查 wiki（Interface modding / Technology modding）和原版 `countrytechtreeview.gui`：
  - 原版 `infantry_folder`（drag_scroll 容器）里还套着一个子容器 `techtree_stripes`。
  - 这个子容器尺寸 2800×1100（min 100%%），有自己的 background，`clipping = no`。
  - 所有科技内容都放在子容器里。
  - 我们 r14–r18 是把内容直接放进滚动容器：滚轮和滚动条能用，左键拖动却不被接收。
- wiki 还写了：只有 left 键实测有效；拖动要求该轴存在滚动条（满足）。

### 改动
- `work/rd/gen_rd.py`：
  - 删除 r18 的 `NSP_rd_window` / `NSP_rd_frame`。`NSP_rd` 恢复 `parent_window_name = NSP_home_window`，visible 恢复只看 rd_open。
  - 树区 `NSP_rd_tree` 内新增子容器 `NSP_rd_canvas`：2232×753，min 100%%，`clipping = no`，透明 background。网格、年代、行标签、时代框、连线、gridbox、pad 全部移入。
  - 保留 r18 的 margin（下 24 / 右 25）。
- `common/scripted_guis/NSP_space_guis.txt`：`NSP_home_frame` 和 `NSP_home` 的 visible 恢复 r17 写法。

### 待实机
- 在空白网格上左键拖动能否平移；在卡片上拖动预计不行（原版科技也一样）。
- 如果左键拖动仍然拖走整个窗口，下一步把外壳 `NSP_home_window` 改成 `moveable = no`。
- 动态列表 `NSP_rd_grid` 放在子容器里后，卡片是否照常显示、能否点击。

---

## 2026-10-21 · 第 18 轮 · R&D 独立外壳：修复左键拖动 + 滚动条让位

用户反馈（附视频）：「还是没法拖动，而且滚动条重叠了」。

### 视频诊断
- 在树区按住左键拖动，被拖走的是**整个窗口**，内容没有平移。
  - 原因：R&D 页挂在 `moveable = yes` 的 `NSP_home_window` 上，左键拖动被可移动的外壳抢走了，`drag_scroll` 拿不到。
  - 原版科技树能拖，是因为科技树窗口本身不可移动。
- 滚动条（原版 / TNO 细线样式已生效）压在卡片上，横向和竖向两条在右下角交叉。

### 改动
- `work/rd/gen_rd.py`：
  - 新增顶层窗口 `NSP_rd_window`，设 `moveable = no`。几何、滑入动画、背景、页签照抄 `NSP_home_window`。
  - 新增 scripted gui `NSP_rd_frame`，visible = home_open AND rd_open，写在 `NSP_rd` 前面，保证父窗先创建。
  - `NSP_rd` 的 `parent_window_name` 改为 `NSP_rd_window`，visible 改为 `always = yes`（开关交给外壳，同 r5 规则）。
  - 树区加 `margin = { bottom = 24 right = 25 }`，照原版科技树给滚动条让位。
- `common/scripted_guis/NSP_space_guis.txt`（手写）：
  - `NSP_home_frame` visible 加 `NOT = { has_country_flag = NSP_rd_open }`。打开 R&D 时，主外壳上滑让出，R&D 外壳滑下；返回时反过来。
  - `NSP_home` visible 去掉 `NOT rd_open`，让主页内容跟着外壳一起滑走。

### 代价 / 待实机验证
- R&D 窗口不能再拖动位置，固定在屏幕中央。主窗口仍可拖动，但拖过之后打开 R&D，会在中央出现。
- 左键、中键拖动树区都应能平移，单击卡片仍能选中。
- 切页时两个外壳一上一下的动画观感。
- margin 是否足够让滚动条不压卡片，右下角两条滚动条是否仍交叉。

---

## 2026-10-21 · 第 17 轮 · 航天服 / 宇航员装备科技

用户要求：加入与宇航服相关的科技，为以后的宇航员装备做准备。

### 改动
所有改动都写在生成器里：`work/rd/gen_rd.py`、`tech_en.py`、`art_bp.py`。改完重新生成了 R&D 全部文件。
- 「生命保障」分类新增两行：「航天服组件」「舱外装备」。科技从 76 项增加到 87 项，新增 11 项：
  - 舱外活动行：A7LB 加长型月面服（1973）。
  - 航天服组件行：
    - 镀铝尼龙加压层（已完成）
    - 防眩光头盔面窗（已完成）
    - 液冷内衣 LCG
    - 便携式生保系统 PLSS
    - β 布阻燃外层
    - 航天飞机舱外服 EMU（1976）
  - 舱外装备行：
    - 生存装备包（已完成）
    - 舱外工具组
    - 月面地质工具
    - 载人机动装置 MMU
- A7L 月面服的前置增加 PLSS。
- 新增线稿类型 helmet / layers / pack / tools / mmu。
- ⭐ 预留接口：`common/scripted_triggers/NSP_rd_triggers.txt` 新增 16 个 `NSP_rd_has_<key>` 触发器。
  - 覆盖全部航天服 / 舱外科技，包括原有的 mercsuit、g4c、eva、amu、a7l。
  - 以后的宇航员装备系统直接写 `NSP_rd_has_plss = yes` 判断解锁。
  - 解锁文字统一写成「宇航员装备：XXX（预留）」。
- 预览新增 `rd_suit` 状态，选中生命保障 / PLSS。

### 注意 / 待实机
- 新科技追加在数组末尾（索引 76–86）。⚠ 旧存档已经初始化过（有 `NSP_rd_ready`），不会补上这些项，测试请开新档。
- 两行新科技在树区第 4、5 行，需要往下滚动或拖动才能看到。

---

## 2026-10-21 · 第 16 轮 · 科技树：按住拖动 + 原版/TNO 滚动条

用户反馈：「目前科技无法点击拖动，而且样式不是 TNO 原版的」。

### 改动
- 改了 `work/rd/gen_rd.py`，并重新生成 `interface/NSP_rd.gui` / `NSP_rd.gfx`。树区容器 `NSP_rd_tree` 的改动：
  - `verticalScrollbar = "right_vertical_slider"`、`horizontalScrollbar = "bottom_horizontal_slider"`：直接引用原版 core.gui 的滚动条。TNO 已重绘这两个滚动条，所以显示的就是 TNO 原版样式。
  - 新增 `drag_scroll = { left middle }`：左键或中键按住即可拖动平移。写法照抄原版科技树 `countrytechtreeview.gui`。
- 删除自制滚动条：`NSP_rd_vslider` / `NSP_rd_hslider`，以及对应的 `GFX_NSP_rd_sb_*` 和 `nsp_rd_sb_*.dds`。
  - ⚠ 这一轮删了文件，安装前要先删掉旧的 TNO_SPACE 文件夹。
- 预览脚本：横向滚动条改成原版位置的示意画法。

### 待实机验证
- 拖动时单击卡片仍能选中。原版科技树就是这样，应该没问题。
- 两条滚动条的位置。原版科技树容器有 margin，我们没加，滚动条可能贴边、压住卡片边缘。
- 如果卡片还是点不动，用 `-debug` 模式把鼠标悬停在卡片上，看 GUI 提示停在哪个元素上。

---

## 2026-10-21 · 第 15 轮 · 太阳 / 月球 / 行星详细 tooltip

用户要求：给月亮、太阳和行星加 tt（详细文本）。

### 改动
- 新增 `work/tt/add_body_tt.py`。脚本幂等，可以重复跑；**改 tooltip 文案只改这个脚本，然后重跑**。
- `interface/NSP_space.gui`
  - 太阳系视图里，8 颗行星的 814 个轨道命中块都加上 `pdx_tooltip = NSP_TT_<行星>`。
  - `NSP_ss_sun`、`NSP_moon3d` 去掉 `alwaystransparent`，挂上 `NSP_TT_SUN` / `NSP_TT_MOON`。
- `interface/NSP_focus_v22.gui`
  - 聚焦外视图的 558 个命中块也加上 tooltip。
  - 聚焦内视图的返回按钮 `NSP_focus_back` 挂 `NSP_TT_FOCUS`：用 scripted loc `GetNSPFocusTT` 按 `NSP_focus` 显示当前行星，末尾提示改为「点击：返回太阳系」。
- 新增 `localisation/simp_chinese/NSP_bodies_l_simp_chinese.yml`（BOM）和 `common/scripted_localisation/NSP_bodies_scripted_loc.txt`。
- tooltip 格式：
  - 标题 §W，类型 §F，分隔线；
  - 参数行「§F标签：§!§Y数值§!」；
  - 一段说明，结合太空竞赛玩法：发射窗口、引力助推、RTG、行星大旅行等；
  - 可点击的天体最后加一行 §G 操作提示。
  - 卫星数按 1960 年代已知数量：木 12、土 10、天王 5、海王 2。

### 检查
- 花括号配平 ✔
- §X / §! 配对：300 / 300 ✔
- `>=/<=` 为 0 ✔

### 待实机验证
- 3D shader 图标（太阳、月球）上 tooltip 能否触发。
- 太阳图标去掉 `alwaystransparent` 后，会不会挡住水星内圈命中块。按理不会，因为命中块在它之后定义。
- `NSP_focus_back` 的 tooltip 会不会盖住整张地图、显得太频繁。
- 仍然只有中文本地化。

---

## 2026-10-21 · 第 14 轮 · 科技树：双向滚动 + TNO 原尺寸科技卡（239×117）

用户反馈：「太挤了，加滚动条，可以放更多科技，图也放大」，并发来 TNO 科技图 DDS 作参考：`USA_Tactical_Bomber_*.dds`、`WSB_*.dds` 等，主图 239×117。

### 滚动
- 树区（网格、年代、行标签、时代框、连线、卡片）整体放进一个滚动容器 `NSP_rd_tree`：窗内 x=10 y=92，1055×438。
  - 竖向：滚轮 + 滚动条；横向：滚动条。
  - 遵守 r9 规则：只有一层滚动容器。
- 新增滚动条 `NSP_rd_vslider` / `NSP_rd_hslider`，仿 TNO 细线风：一条青线轨道、两端带三角的 18×18 小方框、青色滑块。结构照抄原版 core.gui，贴图为 `nsp_rd_sb_*.dds`。
- 列数 5 → 8（新增 1973 / 1976 / 1979 三个时代）；行数 4 → 5。`NSP_rd_era_now` 增加到 7。
- 新增 17 项后期科技，总数 59 → 76：土星 INT-21、航天飞机、NERVA、RIFT、火星运载器、天空实验室 B、模块化空间站、火星远征舱、LESA、闭环生保、自动对接、70 米天线、地球资源卫星、先驱者 10 号、旅行者号、39B、SLC-6。
- 行标签：「核推进」（运载火箭第 5 行）、「外行星」（无人探测第 4 行）。

### TNO 科技卡
- 新增 `work/rd/art_bp.py: render_tech()`，每个项目生成一张 239×117 的不透明蓝图卡：
  - 3 行一循环的暗色扫描线底；
  - 英文粗体标题印在图里；
  - 外轮廓青色 89,199,194，内部细节白色，红色点缀；
  - 右上两行参数 + 引线，左下一行参数，底基线和右竖线做尺寸线。
- 新增 `work/rd/tech_en.py`（76 项的英文标题和参数）和 `work/rd/pixfont.py`（5×7 位图字，带小写和下伸部）。
- 图集按分类拆成 `GFX_NSP_rd_tech_0..5`（单张不超过 17×239 宽）。
  - `NSP_rd_art^p` 的含义改为「本分类内的帧序」。
  - 卡片条目放 6 个 icon，按 `NSP_rd_track` 只显示一个。
- 卡片框 243×121，格位 263×139；实心状态方块改成独立 icon `GFX_NSP_rd_state`，叠在最上层；卡上中文名去掉（标题已印在图里），中文名留在 tooltip 和抽屉里。
- 抽屉：② 栏显示同一张科技图（1:1）；成本/工期/科技三格移到 ③ 栏按钮下方；预算移到页眉右侧。
- 删除旧的 `nsp_rd_art.dds` / `nsp_rd_art_big.dds`（⚠ 覆盖安装会残留，必须删旧文件夹）。
- 预览脚本：嵌套容器改为 alpha 合成（修正半透明元素变实色）；画出 R&D 两条滚动条。

### 检查
- 花括号配平 ✔
- `>=/<=` 为 0 ✔
- BOM ✔
- gfx 引用的贴图全部存在 ✔

### 待实机验证
- 横向滚动条位置、`orientation/origo` 写法是否正确。
- 鼠标滚轮只滚竖向；横向要拖滚动条。
- 网格 / 连线 DDS 较大：网格约 6 MB，连线约 8 MB。
- 5×7 字在 1080p 下的清晰度。

---

## 2026-10-21 · 第 13 轮 · 科技树改成 TNO 原生科技树风格

用户反馈：r12 的科技树「好难看，不是 TNO 风格」。这一轮对照 TNO 科技树参考图（files/uploads/image-dd5b10fe031c.webp）重做。

- **新增 `work/rd/art_bp.py`：蓝图线稿**
  - 23 种线稿全部重画成矢量：米白主线、灰色剖线、珊瑚红点缀，加引线英文标注（自带 3×5 像素字）。
  - 1px 硬边，原生尺寸显示：卡片 160×40，scale 1；抽屉新增 `GFX_NSP_rd_art_big` 240×60，不再 ×3 放大。
  - 锁定项目用压暗偏粉的副本帧，帧号规则和以前一样（N+1..2N）。
- **卡片**
  - 2px 单色框：锁定粉，其余青；表头只留一条细线。
  - 状态格改回实心方块（TNO 原版就是实心）：粉 = 锁定，青 = 可研发，黄 = 研发中，绿 = 已完成。r12 的空心方案作废。
- **背景**：新增 `GFX_NSP_rd_grid` 坐标纸网格（20px 细格、100px 粗格），压在树区最底层。
- **当前时代框**：改为 TNO 琥珀橙细框 + 极淡橙色填充（r12 改成黄色是错的）。
- **行标签**：字号 24，和卡片顶部对齐；「重型发动机」改为「重型引擎」，避免超宽。
- **卡片内排版**：线稿 y 从 CY+22 移到 CY+17，注释 y 从 CY+64 移到 CY+61。
- **检查**：花括号配平 ✔、`>=/<=` 为 0 ✔、BOM ✔
- **待实机验证**
  - 3×5 标注字在 1080p 下是否看得清。
  - 网格 DDS（950×448）的显存占用和加载情况。
  - 半透明卡底（alpha 235）叠在网格上的效果。

---

## 2026-10-21 · 第 12 轮 · 按 TNO 原生风格统一 UI

依据：`documentation/TNO_STYLE_REFERENCE.md` §7。

**生成器**（改这里，别手改生成的文件）：
- `work/rd/gen_rd.py`：
  - 新色板常量 BG / LINE2 / CREAM / CORAL / GRN
  - 新增 `stripes()` 分段竖纹函数
  - 卡片：纯底色 + 双线框，表头去填色，状态格改空心（红 / 米白 / 黄 / 绿，完成带实心点）
  - 页签：选中态改为整块青色填充，未选中只描次线
  - 卡片进度条、队列进度条改为分段竖纹
  - 开始研发按钮：可研发 = 珊瑚红 3px 粗框；研发中 = 米白；已完成 = 绿；不可 = 灰
  - 大线稿框改双线框；数值格表头去填色
  - 当前时代框：橙色改为 TNO 黄
- `work/style/gen_style.py`：
  - 甘特条和遮罩改为竖纹
  - 新增 `GFX_NSP_start_btn2`：规划器启动按钮，原生 254×48 红框
  - 新增 `GFX_NSP_tab_view2` / `GFX_NSP_tab_mc2`：主页页签，青色反色

**手改**：
- `interface/NSP_space.gui`：视图页签 ×3、任务控制页签 ×2 换成新贴图；启动按钮换成 start_btn2，去掉 `scale = 0.745`（守 1:1 像素规则）。
- `localisation/simp_chinese/NSP_space_l_simp_chinese.yml`：
  - 去掉全部 `§D`：名称改 §Y；可靠性改 §F 标签 + §G 值；科学改 §G；三个指标标题统一 §W
  - 「启动任务」改为 §R
- R&D 本地化（由生成器写出）统一「标签：值」：
  - 研发槽：3/3
  - 状态：可以研发
  - 进度：30% · 剩余 231 天
  - 前置：… / 解锁：…
  - 可用预算：$…M

**检查**：
- 花括号配平 ✔
- `>=/<=` 为 0 ✔
- yml BOM ✔
- §X / §! 逐行配对 ✔

**待实机**：
- 青色选中页签上的 outline 字是否清晰（引擎不能改 buttonText 颜色；看不清就把填充色调暗）。
- 启动按钮去掉 scale 后的位置（811,630，254×48）和文字是否居中。
- 竖纹甘特遮罩是否和黄纹对齐。
- 旧贴图 GFX_NSP_tab_view / tab_mc / start_button 仍留在 NSP_space.gfx，已不再引用。

**预览已知偏差**：rd_probe 图里槽满时按钮显示「研发中」，这是预览脚本解析 defined_text 的偏差；按脚本逻辑，实机应显示灰框 + 灰色「开始研发」。

---

## 2026-10-21 · 学习 · TNO 原生风格参考

- 新增 `documentation/TNO_STYLE_REFERENCE.md`，内容来自用户提供的三张参考图（最高法院页、Raiders of Russia、日本 BAPD 地图 GIF）：
  - 色板（取样色值）
  - 框线
  - 字体
  - 控件
  - 插画
  - 与当前 TNO_SPACE 界面的 8 条差距
- 没有改动 mod 代码，等用户确认后在 r12 应用。

---

## 2026-10-21 · 第 11 轮 · UI 整体风格优化（轨道面板 / 任务时间线 / 研发抽屉）

**用户要求**：三块一起改，并统一整体风格。

### 新增：通用像素部件
生成脚本：`work/style/gen_style.py`
- 输出 `interface/NSP_style.gfx`
- 输出 `gfx/interface/NSP/style/` 下的贴图：
  - `GFX_NSP_divider`：230×3 分隔线，两端各一个亮点
  - `GFX_NSP_tl_gantt`：70×8，15 帧
  - `GFX_NSP_tl_gantt_mask`：70×8，15 帧

### 1 · 轨道示意（`NSP_route_panel`）
- Delta-V 下方加分隔线。
- 「必需修正」和修正条目全部居中（原来条目左对齐、标题居中，看着像散在外面）。
- 文案统一为「先进双子星改装 · 已装配 / 缺失」。
- 没有必需修正时显示「无需额外修正」。

### 2 · 任务时间线（`NSP_timeline_panel` / `NSP_timeline_entry`）
- 表头拆成三列：阶段 / 进度 / 本阶段。
- 每行改为显示**本阶段天数**（`NSP_calc_phase_days^v`），累计天数移到行 tooltip（`NSP_TL_ROW_TT`）。
- 新增甘特条，两层贴图叠加：
  - 底条：亮黄填到本阶段结束。
  - 遮罩：把之前的阶段盖成暗青。
  - 效果：每行只有本阶段那一段是亮黄。
- 帧在 `NSP_tl_row_visible` 里计算，写入 `t_tlb` / `t_tlm`，由 properties 读取。改动文件：`NSP_space_guis.txt`。
- 总工期改为 18 号字、居中，上方加分隔线。

### 3 · 研发页底部抽屉（`gen_rd.py`）
重排为四栏：
1. 名称 / 归属 / 描述 / 前置 / 解锁（前置和解锁各占一行）。
2. 选中项目的大线稿（×3 整数倍）+ 成本 / 工期 / 太空科技三个数值格。
3. 开始按钮、状态、超前提示、可用预算。
   - 按钮改为原生 254×48、4 帧：可研发绿 / 不可灰 / 研发中黄 / 已完成暗绿。
   - 帧来自 `NSP_rd_f_start`。
   - 去掉 `scale 0.745`，符合像素 1:1 规则。
   - 按钮文字颜色随状态变化：不可研发时文字为灰色「开始研发」。
4. 研发队列：字号从 14 改为 16，每行加进度条（`GFX_NSP_rd_qbar`，帧来自 `NSP_rd_q_f0..2`）。

### 预览工具
- `render_preview.py`：planner 状态新增时间线甘特的 `entry_cb`。
- `rd_preview_state.py`：补上按钮、大线稿、队列条的帧。
- 预览不跑 scripted loc 触发器，所以 rd_probe 里按钮文字显示的是第一个分支「研发中」。实机中「槽已满」会显示灰色的「开始研发」。

### 待测
1. 甘特条的帧：`NSP_tl_row_visible` 在 trigger 里用 `clamp_temp_variable`、`divide_temp_variable` 计算，看 error.log 是否报错。
2. 研发按钮 4 帧是否随状态切换。
3. 队列空行的进度条是否隐藏。
4. 大线稿 ×3 是否清晰。
5. 时间线行 tooltip 是否显示累计天数。

---

## 2026-10-21 · 第 10b 轮 · 修复：研发页脱离主窗，跑到屏幕左上角

**实机现象**
- 研发页贴在屏幕左上角（坐标 12,16 被当成屏幕坐标）。
- 外壳 `NSP_home_window` 仍在屏幕中间，但里面是空的。

**原因（推断）**
- 引擎按文件名顺序创建 scripted gui。
- `NSP_rd_guis.txt` 排在 `NSP_space_guis.txt` 前面，创建 NSP_rd 时父窗 `NSP_home_window` 还不存在，`parent_window_name` 落空，页面被挂到了根上。
- 规划器 / 聚焦窗和外壳定义在同一个文件里，而且排在外壳后面，所以一直正常。

**修复**
- 文件改名为 `common/scripted_guis/NSP_space_rd_guis.txt`，`g` < `r`，排在主文件之后。
- `gen_rd.py` 输出路径同步修改。

**规则**：凡是用 `parent_window_name` 挂外壳的 scripted gui，所在文件名必须按字母序排在 `NSP_space_guis.txt` 之后，或者直接写进同一个文件、放在外壳后面。

**待测**：研发页是否出现在外壳里，并且随外壳一起拖动、一起播放滑入 / 滑出动画。

---

## 2026-10-21 · 第 10 轮 · 研究与发展页（方案 B：TNO 原生蓝图科技树）

**用户选择**：方案 B。

**生成方式**：全部由 `work/rd/gen_rd.py` 一个脚本生成（单一数据源，**不要手改生成的文件**）。改项目或布局时，改脚本后重跑。

**新增文件**
- `interface/NSP_rd.gui` / `NSP_rd.gfx`
  - 页面 `NSP_rd_body`：独立容器，挂在 `NSP_home_window` 上，visible 只看 flag `NSP_rd_open`（同 r4/r5 架构）。
  - 卡片条目 `NSP_rd_card_entry`。
- `common/scripted_guis/NSP_rd_guis.txt`、`common/scripted_effects/NSP_rd_effects.txt`、`common/scripted_triggers/NSP_rd_triggers.txt`、`common/scripted_localisation/NSP_rd_scripted_loc.txt`
- `localisation/simp_chinese/NSP_rd_l_simp_chinese.yml`
- `gfx/interface/NSP/rd/*.dds`，7 张像素风贴图：
  - 卡片 4 帧（需前置 / 可研发 / 研发中 / 已完成，右上角色块）
  - 线稿图集：23 种 × 亮暗两组
  - 连线图：每个分类一帧
  - 橙色时代框、进度条、选中角标、页签

**布局**（1075×690）
- 6 个分类页签
- 年代轴：1958 / 1961 / 1964 / 1967 / 1970
- 左侧行标签（随分类变化）
- 5×4 卡片格：gridbox，固定 20 格，空格位用占位 id
- 底部抽屉：名称、分类 / 时代、描述、成本 / 工期 / 奖励、前置 / 解锁、开始按钮、状态、超前提示、研发队列（3 行）、预算

**数据**：59 个项目，分 6 个方向。开局状态与现有任务数据一致（双子星、泰坦 II/IIIC、阿波罗 Block I 等已完成）。开局研发中：半人马、F-1、阿波罗制导计算机，3 个研发槽全部占满。

**规则**
- 当前时代按 `date` 计算（1962 开局 = 1961 时代）。
- 可以研发下一个时代的项目，但工期 ×1.5。
- 前置全部完成后状态变为「可研发」。
- 点「开始研发」立刻扣成本。
- 每周进度 += 700 / 实际工期（%）。
- 完成后：太空科技 + 奖励值。载人航天中心额外给研发槽 +1。

**改动的现有文件**
- `NSP_space_guis.txt`
  - 主页和两个聚焦窗的 visible 加上 `NOT NSP_rd_open`
  - R&D 按钮启用，点击调用 `NSP_open_rd`
- `NSP_space_effects.txt`
  - 开窗时清除 `NSP_rd_open`
  - `NSP_weekly_tick` 开头调用 `NSP_rd_weekly`（老存档会自动 init）
  - `NSP_init` 末尾调用 `NSP_rd_init`
- `NSP_space_l_simp_chinese.yml`：`NSP_RD_TT` 改为正式说明。

**预览工具**
- `render_preview.py` 新增 `entry_cb`（逐条目设置帧 / 隐藏 / 变量）和 `page_vars`。
- R&D 状态模拟在 `work/rd/rd_preview_state.py`。

**尚未做**
- 解锁内容还没接入规划器：规划器目前仍可直接选土星 IB / 土星 V 等。
- 没有完成通知事件。
- 承包商、测试阶段、突破 / 挫折事件留给后续轮次。
- 只有中文本地化。

**待测**
1. R&D 按钮能切到研发页，返回 / Esc 能回主页；关窗再开时回到主页。
2. 页签帧切换，连线图跟着分类切换。
3. 卡片帧、线稿帧、进度条帧正确（条目帧依赖 `NSP_rdc_name_visible` 写的临时变量）。
4. 空格位完全隐藏。
5. 选中角标跟随点击。
6. 「开始研发」的启用条件正确；扣预算后队列增加。
7. 每周进度增长；完成后状态变绿、太空科技增加。
8. 老存档：一周后 R&D 数据自动出现；打开 R&D 页时也会自动 init。
9. 检查 error.log：是否有 `for_loop_effect end = 变量`、`array^temp` 写法报错。
10. `aldrich_14_outline` 字体在 TNO 中存在。

---

## 2026-10-21 · 设计 · R&D 多方案 v2（未实现）

- `RD_DESIGN.md` 追加 v2：
  - 方案 B：TNO 原生蓝图科技树
  - 方案 C：合同看板
  - 方案 D：竞赛时间轴
  - 10 个可组合的玩法模块
- 新增概念图 `files/out/concept_B/C/D_*.png`（生成器 `work/rd_mock/concepts.py`）。
- mod 代码没有改动。

---

## 2026-10-21 · 设计 · 研究与发展页（未实现）

- 新增 `documentation/RD_DESIGN.md`：R&D 页的界面结构、引擎实现方案、玩法和分期（r10–r13）。
- Mockup 图：`files/out/rd_mock_v1.png`，由 `work/rd_mock/gen_mock.py` 生成，用的是现有贴图，不进 mod。
- mod 代码没有改动。

---

## 2026-10-21 · 第 9 轮 · 滚动条：重叠、位置、滚轮、按内容出现

**问题**（实机截图）：
1. Mission Control 有两条滚动条叠在一起。
2. 滚动条压在卡片右边。
3. 鼠标滚轮滑不动。
4. 内容没超出时滚动条也常驻，而且能滚到空白处。

**原因**
1. `NSP_mc_national_box` 和 `NSP_mc_intl_box` 是两个重叠的滚动容器。嵌套容器的 `_visible` 不生效（r3 已实证），所以两条滚动条都画出来了；上层那个空的 intl 容器还把滚轮事件吃掉了。
2. 原版 `right_vertical_slider` 是 `position x = -5`、宽 18，会占容器右侧 23px，而卡片宽 226、容器只有 240–242。
3. 出发地 / 目的地 / 调色板容器没写 `scroll_wheel_factor`；MC 写了，但被上层的 intl 容器挡住。
4. gridbox 高度写死成 2000 / 400，滚动范围就固定是这么大；再加上 r6 的 `autohide_scrollbars = no`。

**改动**（`interface/NSP_space.gui`）
- 文件开头新增 `extendedScrollbarType NSP_right_slider`：结构照抄原版 core.gui，`position x = 0` 贴右边；贴图仍用 `GFX_scroll_*`，TNO 已经把它重绘成青色。
- MC：两个容器合并成一个 `NSP_mc_box`（2,62 / 246×402），两个 gridbox 都放在 y=0。recalc 只填当前页签的数组，另一个为空、不占位置。
- 所有滚动容器：
  - 改用 `NSP_right_slider`
  - 加 `scroll_wheel_factor` 和 `smooth_scrolling = yes`
  - 去掉 `autohide_scrollbars = no`（内容超出才出现）
  - gridbox `height = 100%%`（原版写法，高度随条目增长）
- 出发地 / 目的地容器改为 x=8、宽 246：卡片在 8..234，滚动条在 236..254，不碰路线面板（256）。
- `gfx/interface/NSP/nsp_scroll_bg.dds`：alpha 从 0 改成 3/255（肉眼看不见）。这是保险措施，防止全透明背景导致鼠标事件穿透。

**待测**
1. MC 只出现一条滚动条，滚轮可用，切到「国际」页签后列表正确。
2. 出发地只有 5 条（130 高，刚好装满），应当不出现滚动条；目的地 6 条，应当出现。
3. 如果 `GFX_scrollbar_vertical_bg` 等原版贴图名在 1.19 被改过，滚动条会缺图，这时把 `verticalScrollbar` 改回 `right_vertical_slider` 即可回退。
4. 如果 `height = 100%%` 的 gridbox 不随条目增长（滚不到底），改回较大的固定值。

---

## 2026-10-21 · 第 8 轮 · 计划徽章改像素风

**问题**：用户反馈 `nsp_badge_*` 是 96×96 的平滑抗锯齿矢量风，和 TNO 的像素美术不统一；而且 GUI 里用 `scale = 0.7 / 0.8` 做非整数缩放，像素会被插值糊掉。

**改动**
- `gfx/interface/NSP/nsp_badge_{mercury,gemini,apollo,unassigned}.dds`：按 48×48 原生像素重画，存为 legacy A8R8G8B8 DDS。
  - 画法：有限色板、硬边、1px 深色描边，左上受光、右下背光，过渡用棋盘抖动；米白外环 + 海军蓝内盘 + 金色符号，未分配的用灰色问号。
  - 顶部 NASA 字样用 3×5 像素字（N 为 4 宽，避免看成 M）。
  - 阿波罗的 A 不碰外圈，避免看起来像无政府符号Ⓐ。
  - 生成脚本：`work/badges/make_badges.py`，以后改图重跑它即可。
- `interface/NSP_space.gui`：`NSP_prog_badge` 和 `NSP_pl_badge` 去掉 scale，改为 1:1 显示；位置按原中心点重算（18,72 和 26,24）。
- `.gfx` 不用改：DDS 尺寸由引擎读取。

**待测**：48px 在实机里会不会显得太小。如果要更大，应该整数倍（2×，96px）出图，而不是用 scale。

---

## 2026-10-21 · 工具 · 离线预览图

- 新增项目工具 `work/preview/render_preview.py`（不在 mod 内，不随 zip 发布）：它会解析 `interface/*.gfx`、`*.gui`、简中本地化和 scripted_localisation，按坐标出两张布局预览，分别是主页和规划器页。
- 从这一轮起，每次改 UI 都附上预览图（用户要求）。
- 局限：不运行触发器，`_visible` 用规则近似；3D shader 天体只标出「3D shader」字样；数值是示例值（128 / 12.3）；字体用 Aldrich 加 Noto Sans SC 近似。

---

## 2026-10-21 · 第 7 轮 · 规划器右下角 UI 优化

**问题**（截图）：
1. 性能 / 可靠性 / 成本三个竖框只有 82–84 宽，「$4292M」「剩余」被挤得折行、溢出框外。
2. 「任务成功后」一行太长，折成 3 行，「声望」被裁掉。
3. 「启动任务」按钮 `scale = 0.745` 后 buttonText 没跟着缩放，字偏右偏下。

**改动**
- `interface/NSP_space.gui`
  - 三个竖框改成三条 254×50 的横向指标条（y = 414 / 468 / 522），沿用原蓝 / 紫 / 黄框。左侧是标题，中间一条竖分隔线，右侧三格「标签在上 / 数值在下」，每格 62 宽，全部 `fixedsize = yes` 居中。悬停提示放在标题和每一格上。
  - 成功面板移到 y=576，高 48：标题一行 + 奖励一行（`fixedsize`，不再折行）。
  - 启动按钮移到 y=630，去掉 buttonText，叠一个居中的 `NSP_start_label`（alwaystransparent，点击照常穿透到按钮）。底边 678，没超出页面。
- `localisation/simp_chinese/NSP_space_l_simp_chinese.yml`：新增 `NSP_PERF/REL/COST_L1..3 / V1..3`、`NSP_SUCCESS_TITLE`、`NSP_SUCCESS_LINE`（「完成 1 项计划目标」缩写为「目标 +1」）。旧 BODY / SUCCESS_TEXT 键保留未删。BOM 已核对。
- `gfx/interface/NSP/planner/nsp_stat_sep.dds`（新增，2×34 青色半透明）+ `interface/NSP_space.gfx`：`GFX_NSP_stat_sep`。

**已知 / 待测**
1. 按钮不可点时，叠加的文字不会跟着变灰。如果需要，再加一个灰色文字版本，用 `_visible` 切换。
2. 预算到 5 位数（如 $12000M）时，62 宽的格子会比较紧。
3. 实机确认各行没有溢出，以及中文回退字体的宽度。

---

## 2026-10-21 · 第 6 轮 · 列表滚动条不显示

**现象**：任务控制（本国/国际）、出发地、目的地列表右侧留了滚动条位置，但滚动条从没出现过（初版截图里也没有，不是 r3–r5 引入的）。目的地 6 项只露 5 项，第 6 项滚不出来。

**原因（Wiki Interface modding → Scrolling）**：滚动容器**必须有 `background`**，否则边界被忽略、滚动条不工作；另外滚动条默认 `autohide_scrollbars`，内容不溢出时不显示。5 个带 `verticalScrollbar` 的容器都没写 background。

**改动**
- `interface/NSP_space.gui`：`NSP_mc_national_box`、`NSP_mc_intl_box`、`NSP_site_box`、`NSP_dest_box`、`NSP_palette_box` 加 `background = { name = "Background" spriteType = "GFX_NSP_scroll_bg" }`；前四个加 `autohide_scrollbars = no`（常显）。调色板宽 74、图标占满，常显会压住图标 → 保持自动隐藏。
- `gfx/interface/NSP/nsp_scroll_bg.dds`：新增 8×8 全透明 legacy DDS。
- `interface/NSP_space.gfx`：`GFX_NSP_scroll_bg`。

**待测**
1. 四个列表右侧出现原版滚动条；目的地能滚到第 6 项。
2. 滚动范围：gridbox 写死了高度（任务控制 2000、出发/目的地 400）。若滚动条能拖到一大片空白，回报，我把 gridbox 高度改小或改成按条目数。
3. 列表空白处现在会吃鼠标（背景），在列表上按住拖不动窗口属正常。

---

## 2026-10-21 · 第 5 轮 · 行星点不中 + 关窗动画内容消失

### A. 太阳系行星有时点不中
**原因**：命中区是沿轨道排的 6×6 / 8×8 隐形按钮（`NSP_ss_<行星>_s<n>`，nsp_hit.shader 画成透明）。块太小、块间距最大 12–16px，行星正好转到缝里就点不到；块也只覆盖轨道线一条细带。
**改动**
- `interface/NSP_space.gui`：重新生成全部命中块。每块尺寸按「到相邻轨道最近块的切比雪夫距离」自适应，取 4..16px（保证不同轨道的块不重叠）；块间缝隙大于块尺寸 85% 处插值补块。块数 558 → 814（水 52 / 金 70 / 地 89 / 火 109 / 木 71 / 土 94 / 天 157 / 海 172）。内圈轨道之间本身只有 ~7px，最窄处仍是 6px，左右两侧放大到 11–16px。
- `common/scripted_guis/NSP_space_guis.txt`：对应的 `_click` / `_visible` 按原模板重新生成（每颗行星的 effect 内容不变）。
- `gfx/interface/NSP/3d/nsp3d_seg_6..16.dds`：新增 7、9–16 尺寸（legacy 未压缩 32 位，alpha 255，克隆原 seg_6 头）。
- `interface/NSP_orbit_v24.gfx`：`GFX_NSP_seg_6..16` 精灵。
- 技术债：这些按钮全是生成的，以后改轨道请用脚本重生成，别手改。

### B. 关窗向上滑出时内容全没了，只剩空壳
**原因**：r4 子页 visible 带 `has_country_flag = NSP_home_open`。点关闭清 flag 的同一帧，子页 visible 变假立刻消失，只有外壳在播滑出动画。
**改动**（Wiki Parent window：子窗只在父窗可见时显示、跟随父窗动画）
- `NSP_home_frame` visible = `has_country_flag = NSP_home_open`（只有外壳管开关）。
- 主页 `NSP_home` visible = `NOT planner_open`；规划器 `NSP_planner` visible = `planner_open`；`NSP_focus_in/out` 也去掉 home_open。
- `NSP_toggle_home`（scripted_effects）：关窗只清 home_open，**不再清 planner_open**（在规划器页关窗，规划器内容也跟着滑走）；打开时先清 planner_open → 每次打开都回主页，并 +dirty。

**待测**
1. 主页、规划器页分别关窗：内容跟着外壳一起滑出。
2. 各行星（尤其外圈和左右两侧）点击命中率；内圈上下最窄处是否会点到隔壁轨道。
3. 再打开回到主页。

---

## 2026-10-21 · 第 4 轮 · 修 r3：规划器页常显、返回键无效 → 外壳 + 两个独立内容页

**现象**（实机截图）：打开面板只有「新任务概念」页；点返回（Esc）没反应。

**原因（查 Wiki 确认）**：Scripted GUI modding 页 "Window assignment"：scripted GUI 只能挂在**独立**容器上，嵌套容器不能单独作为目标；r3 把两页嵌进同一个窗口、靠 `NSP_home_body_visible` / `NSP_planner_body_visible` 切换，实机这两个容器级 `_visible` 不生效 → 两页都常显，规划器页画在上层盖住主页；返回键清掉 flag 也没有任何东西会隐藏。（与旧注释"嵌套容器 _visible 引擎不认"一致，r3 判断错误。）

**方案**（Wiki "Parent window"：`parent_window_name` 挂上的窗口会跟随父窗显示、绘制在父窗元素之上、跟随父窗动画）：
- `NSP_home_window` 变成**外壳**：只剩窗框背景（拖拽把手）、滑入动画、页签。`moveable = yes`。
- `NSP_home_body`、`NSP_planner_body` 从外壳里拆出，成为两个**顶层独立容器**，各自由 scripted_gui 用 `parent_window_name = NSP_home_window` 挂回外壳，坐标 (12,16) 不变。
- 两页背景都是 `alwaystransparent = yes`，鼠标按下会落到外壳 Background → 在任意一页都能拖动整窗；子窗跟随外壳移动。
- 用 scripted_gui 的**窗口级 `visible`** 切页（这个是确定生效的），不再用容器级 `_visible`。

**改动**
- `interface/NSP_space.gui`：两页移出外壳成为顶层容器；两页各加 `clipping = no`（标题 y=-16 探出页面上沿）；外壳注释更新。
- `common/scripted_guis/NSP_space_guis.txt`
  - 新增 `NSP_home_frame`：window = NSP_home_window，visible = OR(home_open, planner_open)。
  - `NSP_home`：window_name 改为 `NSP_home_body`，加 `parent_window_name = NSP_home_window`，visible = home_open 且 NOT planner_open；删掉 r3 并入的规划器内容和两条 body_visible。
  - 恢复 `NSP_planner`：window = `NSP_planner_body`，parent = NSP_home_window，visible = planner_open，dirty = NSP_dirty；dynamic_lists / effects / triggers / properties 原样搬回。
  - 顺序：frame → home → planner → focus_in → focus_out（后挂的画在上层，聚焦窗仍在主页之上）。
- `common/scripted_effects/NSP_space_effects.txt`：切页注释更新（逻辑未变，NSP_open_planner 仍 +dirty）。
- 花括号配平：gui 1644/1644，scripted_guis 9314/9314。

**待测**（重启游戏）
1. 顶栏按钮打开 → 显示主页；创建任务 → 规划器页；返回 → 主页。
2. 两页都能拖动整窗。
3. 关闭面板（主页 ✕ / 顶栏按钮）→ 外壳带着内容一起滑出。
4. 行星聚焦动画仍在主页地图上。
5. 若拖不动：说明子窗口吃了鼠标，回报，我给两页加不吃鼠标的处理或在页面上留拖拽条。

**卡住的旧存档**：读档后若仍停在规划器页，控制台 `clr_country_flag NSP_planner_open`（需在 USA 下）。

---

## 2026-10-21 · 第 3 轮 · 改成单窗口：用 flag 切换主页 / 规划器内容（❌ 失败，见第 4 轮）

**问题**：r2 把 planner 挂成主窗子窗口后，planner 页面不能拖动（子窗 moveable = no）。用户要求不要第二个窗口，用 flag 切内容。

**方案**：删掉 `NSP_planner_window`，把它的内容 `NSP_planner_body` 原样搬进 `NSP_home_window`，与 `NSP_home_body` 同位置（12,16）同尺寸（1075x690）叠放；用容器级 `_visible` 互斥显示。整个面板只有一个可拖动窗口。

**改动**
- `interface/NSP_space.gui`
  - `NSP_planner_body` 整块移入 `NSP_home_window`（放在 `NSP_home_body` 之后）。
  - 删除 `NSP_planner_window` 外壳（含它的动画参数、`NSP_pl_gtab_space` 页签按钮——主窗已有同款页签）。
  - 主窗 `moveable = yes` 保持。
- `common/scripted_guis/NSP_space_guis.txt`
  - 删除 `NSP_planner` scripted_gui；其 dynamic_lists（6 个）、effects、triggers、properties 全部并入 `NSP_home`（各段内标注「r3 从 NSP_planner 并入」）。
  - 新增 `NSP_home_body_visible = NOT planner_open`、`NSP_planner_body_visible = planner_open`。
  - 元素名、临时变量名（t_row / t_drow / t_mod / t_pmod / t_S / t_D / t_M）已核对，与主页无冲突。
- `common/scripted_effects/NSP_space_effects.txt`
  - `NSP_open_planner` 设 flag 后补一次 `NSP_dirty +1`（主窗有 dirty，不刷新 _visible 不会重算）。
  - 更新切页注释。
- 花括号配平检查：gui 1644/1644，scripted_guis 9306/9306。

**行为变化**
- 切页是瞬切，没有 r0–r2 的抽屉滑动动画（打开 / 关闭整个面板的滑入动画还在）。
- 3D 行星聚焦窗 `NSP_focus_in/out` 仍是主窗子窗口，visible 已含 NOT planner_open，不受影响。

**待测**（重启游戏）
1. 创建任务 → 主页内容消失、规划器内容出现，只有一个窗口；在规划器页能拖动窗口。
2. 返回 → 回到主页。
3. 规划器里的列表（发射场、目的地、修正槽、时间线）和按钮都正常。
4. ⚠ 关键风险：旧注释写过"嵌套容器 _visible 引擎不认"（当时是 MC 列表场景）。如果两页叠在一起都显示，说明容器级 _visible 不生效，回报 error.log，我改成把开关挪到元素级或用 properties 的 x 坐标把隐藏页移出可视区。
5. 若想要切页动画，可以后续加一层帧动画遮罩（frameAnimatedSpriteType，play_on_show）。

**备份**：r2 版本在 `files/out/TNO_SPACE_20261021_r2.zip`。

---

## 2026-10-21 · 第 2 轮 · 保留拖动 + 动画：planner 改为主窗子窗口

**需求**：第 1 轮靠禁止拖动解决"两窗并排"，用户要求保留拖动与滑入动画。

**方案**：把 `NSP_planner_window` 挂进 `NSP_home_window` 当子窗口（`parent_window_name`），坐标相对主窗左上角。拖主窗 → planner 跟着走，两窗永远对齐；动画仍是 planner 自己从主窗上方滑下 / 弹回（抽屉式不变）。先例：同文件 `NSP_focus_in` / `NSP_focus_out` 已经这样挂在主窗上并实机可用。

**改动**
- `common/scripted_guis/NSP_space_guis.txt`：`NSP_planner` 加 `parent_window_name = NSP_home_window`。
- `interface/NSP_space.gui`
  - `NSP_home_window`：`moveable = no` → `yes`（恢复拖动）。
  - `NSP_planner_window`：去掉 `orientation = center`；`position {-550,-1167}` → `{0,-808}`（关闭位 = 主窗上方 808px，位移与主窗滑入相同）；`show_position {-550,-359}` → `{0,0}`（正好盖住主窗）；保持 `moveable = no`（子窗不能自己拖，否则在主窗内部错位）。
- 动画参数（decelerated / accelerated / 1000ms）、声音、clipping 均未动。主窗 `clipping = no`，planner 从主窗上沿外滑入不会被裁。

**待测**（重启游戏后）
1. 拖动主窗到任意位置 → 创建任务：planner 应从该位置正上方滑下并完全盖住主窗。
2. 返回：planner 弹回上方，主窗原位不动。
3. planner 打开时按住 planner 空白处拖动：看能否带动整体（不能的话属预期，回主页再拖）。
4. planner 打开时，主窗的按钮不应能被点穿（planner 有 background，应吃掉点击）。
5. 返回瞬间：focus 窗（行星聚焦）条件是 NOT planner_open，会在 planner 弹回过程中立刻出现，可能压在正在滑走的 planner 上——观察是否刺眼。
6. 若子窗口上 show/hide 动画不生效（直接出现/消失），回报，我改成别的过渡方案。

**风险**：子窗口挂 `show_position` 滑动动画在本 mod 内无先例（focus 窗用的是帧动画）。

---

## 2026-10-21 · 第 1 轮 · 修复"打开规划器后出现两个窗口"

**现象**（实机截图）：点「创建任务」后，`NSP_planner_window`（新任务概念）和 `NSP_home_window`（国家太空计划）左右并排同时显示，没有叠在一起。

**原因**：抽屉式切页（同日早先改动）让 home 在 planner 打开时保持显示，靠两窗【完全同位置】叠放让 planner 盖住 home。但两个窗口都是 `moveable = yes`：拖动过任一窗口后，引擎记住的是各自拖过的位置，两窗位置分家 → planner 滑下来落在自己的位置，home 留在原处 → 并排两窗。

**改动**
- `interface/NSP_space.gui`：`NSP_home_window`、`NSP_planner_window` 的 `moveable = yes` → `moveable = no`，并加注释说明原因。

**待测**
1. 打开主界面 → 创建任务：planner 应从上方滑下，完全盖住 home，只看到一个窗口。
2. 规划器点返回：planner 弹回上方，露出 home。
3. 顶栏按钮关闭整个面板：两窗一起消失，无残影。
4. 注意：游戏可能缓存了旧拖动位置，测试前**重启游戏**（不要只 reloadinterface）。

**备选方案（未采用）**：保留拖拽，把 `NSP_planner` 改成 `parent_window_name = NSP_home_window` 的子窗口（本 mod 的 focus 窗口已有此先例，scripted_guis 1445/1477 行），planner 跟随 home 一起移动。风险：子窗口上的 show/hide 滑动动画和 `clipping` 行为未实测。

---

## 2026-10-21 · 第 0 轮 · 接手与盘点（未改代码）

**接手版本**：`descriptor.mod` version 1.0.0，name="SPACE"，依赖 TNO，supported_version 1.19.*

**结构盘点**
- 前缀统一 `NSP_`；挂 USA；`on_startup` 用 `USA = { }` 切 scope（scope=None），`on_daily` 老存档自愈，`on_weekly` 跑 `NSP_weekly_tick`
- GUI 架构：模式 B（`NSP_topbar` 挂 `top_bar` 开关 → `NSP_home_window` 主窗 + `NSP_planner_window` 抽屉式规划页），`dirty = NSP_dirty`
- 动态列表：`NSP_mc_national_grid` / `NSP_mc_intl_grid`（数组 `NSP_mc_nat_view` / `NSP_mc_intl_view`）
- 3D 太阳系：自定义 shader（`gfx/FX/nsp_*.shader`）+ `frameAnimatedSpriteType`（focus in/out 20 帧）+ 隐形命中区 `nsp_hit.shader`
- 逻辑收口：`NSP_recalc_home` / `NSP_recalc_planner`
- 文件规模：scripted_guis 2051 行、NSP_space.gui 1275 行、effects 605 行

**静态检查**
- `check_variable` 内无 `>=` / `<=` ✓
- 只有 `simp_chinese` 本地化，缺 `english`（手册 §3.3 要求双语）
- scripted_guis 文件头写着"dynamic_lists 条目中的帧在条目自己的 `_visible` 触发器里写临时变量"——与手册 §7 第 8 条（properties 只引用持久变量/数组，主 mod 无先例）冲突，属风险点，需实机确认
- 行星点击 effects 有大量逐行重复（`NSP_ss_<planet>_s0..s27_click`），可考虑收成 scripted_effect

**文档**：`documentation/TNO_UI_Framework_Guide.md`（通用规范）、`documentation/TNOAR_GUI_DEV_HANDBOOK.md`（整合版手册，优先级：实际代码 > 主 mod 惯例 > 通用规范）
