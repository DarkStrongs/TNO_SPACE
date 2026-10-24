# TNO_SPACE 扩展 API（r94 起）

这份文档写给想在 SPACE 上面再做子模组的人。目标：**不改本体任何文件**，只加自己的文件，就能新增载荷、火箭、目的地、研发项目，并在几个固定时机插入自己的逻辑。

> 只想写事件（选项里加经费、完成研发、改本次任务成功率等）：看 `EVENT_API.md`，不用做下面这些注册。

完整可运行的例子在 `documentation/examples/NSP_addon_example/`：加了 1 个研发、1 种载荷、1 种火箭、1 个目的地。复制这个文件夹，改名，改内容，基本就能用。

---

## 1. 接入方式：扩展槽

本体留了 3 个空的扩展槽文件：

```
common/scripted_effects/NSP_ext_slot_1_effects.txt
common/scripted_effects/NSP_ext_slot_2_effects.txt
common/scripted_effects/NSP_ext_slot_3_effects.txt
```

你的子模组放一个**同名文件**把其中一个槽覆盖掉，填上 5 个钩子：

| 钩子 | 什么时候跑 | 能读到的临时变量 | 一般用来 |
|---|---|---|---|
| `NSP_slotN_register` | 新开局、打开主窗、研发完成、老存档第一次结算 | — | 调 `NSP_reg_*` 注册数据 |
| `NSP_slotN_on_unlocks` | 解锁刷新之后 | — | 自定义解锁规则，改 `NSP_*_unl` |
| `NSP_slotN_on_recalc` | 规划器每次重算之后 | `p` 载荷 / `ve` 火箭 / `s` 发射场 / `d` 目的地 | 改 `NSP_calc_*` 结果 |
| `NSP_slotN_on_success` | 任务成功结算之后 | `p` / `d` / `nsp_mid` 任务 id | 额外奖励、触发事件 |
| `NSP_slotN_on_daily` | 每日结算末尾 | — | 自己的每日逻辑 |

规则：

- 5 个钩子**都要写**，用不到的写成 `NSP_slotN_xxx = { }`，不然本体调用时会报「未知效果」。
- 一个槽只能一个子模组用。用之前先看 §8 的登记表，用了就在表里登记。
- `register` 会被反复调用，里面只能放「按 id 写入」的 `NSP_reg_*`，不要放 `add_to_variable` 这种每跑一次就累加的东西。
- 你自己的其他效果直接写在槽文件里就行；想另开文件也可以，文件名别和本体重复。

---

## 2. id 怎么选

本体的载荷、火箭、目的地、研发都是「数组下标 = id」，本地化键也按 id 取名（`NSP_PL_NAME_<id>`）。所以 id 要**固定写死**，不能按加载顺序自动分配。

| 类型 | 本体占用 | 子模组从这里起 | 上限 |
|---|---|---|---|
| 载荷 | 0..11（保留到 49） | 50 | 没有硬上限 |
| 火箭 | 0..8（保留到 49） | 50 | 没有硬上限 |
| 目的地 | 0..7（保留到 15） | 16 | **31**（许可表每个载荷 32 格） |
| 研发 | 0..94（保留到 199） | 200 | 没有硬上限 |

id 可以跳着用：API 会把中间缺的格子补成「锁定 / 空」的值，规划器切换时会跳过。

---

## 3. 参数怎么传

HOI4 的 scripted effect 不方便带参数，所以 API 统一用**临时变量**：

```
set_temp_variable = { reg_id = 50 }
set_temp_variable = { reg_mass = 0.043 }
...
NSP_reg_payload = yes
```

- 每个主注册效果（`NSP_reg_payload / vehicle / dest / rd / rd_small`）跑完都会把所有 `reg_*` 清零，所以下一次注册不会带上上一次的值。
- 只改属性的小效果（`NSP_reg_allow`、`NSP_reg_dest_attrs` 等）**不清零**，所以可以连着设 `reg_dest` 调好几次。
- 没写的参数读作 0。⚠ 凡是「研发 id / 发射场 id」的参数都必须明写，不需要就写 `-1`；不写会读成 0，也就是研发 0「红石」或发射场 0「卡纳维拉尔角」。

---

## 4. API 一览

全部定义在 `common/scripted_effects/NSP_api_effects.txt`，文件头有每个参数的说明，这里只列要点。

### 4.1 载荷 `NSP_reg_payload`

| 参数 | 必填 | 说明 |
|---|---|---|
| `reg_id` | ✓ | 载荷 id |
| `reg_mass` | ✓ | 质量，吨 |
| `reg_cost` | ✓ | 原型成本（百万，显示时 ×18 再换成 B） |
| `reg_rel` | ✓ | 基础可靠性 0..100 |
| `reg_unlock_rd` | ✓ | 解锁它的研发 id，`-1` = 开局就有 |
| `reg_crewed` | | 1 = 载人：吃载人加成，有乘组 / 返程阶段，去带 `crew_rd` 的目的地要先完成那项研发 |
| `reg_icon` | | 任务卡小图标：GFX_NSP_mission_icons 帧号 1..12（帧 = 本体载荷 id + 1；默认 11 科研卫星）。本体载荷 0..11 固定按 id 取帧，只有 12 号以后的扩展载荷读这个值 |
| `reg_slots` | | 载荷类修正槽位 1..4；`0`（不写）= 默认 2 个，`-1` = 没有槽位 |
| `reg_custom_art` / `reg_art_frame` | | 见 §5 |

注册完还要用 `NSP_reg_allow` 登记它能去哪些目的地（默认哪儿都不能去）：

```
set_temp_variable = { reg_id = 50 } set_temp_variable = { reg_dest = 5 } NSP_reg_allow = yes
```

`NSP_reg_deny` 是反操作，可以用来改本体的规则。`NSP_reg_payload_crewed` 只改载人标记；`NSP_reg_payload_slots`（`reg_id reg_slots`，这里 0 就是没有槽位）只改载荷类修正槽位，本体载荷也能用。

### 4.2 火箭 `NSP_reg_vehicle`

必填：`reg_id reg_dry reg_fuel reg_isp reg_cost reg_rel reg_unlock_rd reg_pad_rd reg_site`

- `reg_heavy = 1`：重型，小发射场（2 / 4 / 6 / 7）不能发射。
- `reg_pad_rd`：需要哪项研发完成才有发射台，`-1` = 不需要。
- `reg_site`：只能从哪个发射场发射，`-1` = 不限。
- `reg_slots`：发射类修正槽位 1..4；`0`（不写）= 默认 2 个，`-1` = 没有槽位。`NSP_reg_vehicle_slots`（`reg_id reg_slots`）只改槽位，本体火箭也能用。

规划器 Delta-V 公式（无修正）：`比冲 × 9.81 × ln((干重 + 载荷 + 推进剂) / (干重 + 载荷)) / 1000 × 2.14`。新火箭先用这个公式算一下，保证常用载荷能到目的地，余量为正。

`NSP_reg_vehicle_limits` 只改发射台 / 发射场限制，本体火箭也能用。

### 4.3 目的地 `NSP_reg_dest`

必填：`reg_id reg_dv reg_crew_rd reg_unlock_rd`

| 参数 | 说明 |
|---|---|
| `reg_xp` | 成功经验（默认 5） |
| `reg_body` | 卫星显示在哪个天体：3 地球（默认）/ 9 月球 / 2 金星 / 4 火星…；`-1` = 逃逸地球规则；`-2` = 不显示 |
| `reg_view` / `reg_row` | Mission Control 视图（0 地球 / 1 月球 / 2 行星际）和轨道行（0..2）。界面只有 3 行，可以和别的目的地共用一行 |
| `reg_crew_rd` | 载人前往要先完成的研发，`-1` = 不需要 |

新目的地会接在规划器列表末尾。想排到某个目的地后面：

```
set_temp_variable = { reg_id = 16 } set_temp_variable = { reg_dest = 5 } NSP_reg_dest_order = yes
```

`reg_dest = -1` 表示排到最前。`NSP_reg_dest_attrs` 只改经验 / 天体 / 视图行 / 载人研发，本体目的地也能用（这个效果不做默认值替换，6 个参数要写全）。

### 4.4 研发 `NSP_reg_rd`

必填：`reg_id reg_track reg_col reg_row reg_cost reg_days reg_tech reg_req1 reg_req2`

- 位置：分类 `reg_track`（0..5）、列 `reg_col`（0..7，也决定时代）、行 `reg_row`（0..4）。**格子必须是空的**，被占了就只登记数据、不上树。空格查法见 §7。
- 连线：前置和本项目的列差 1..4、行差 -3..3 才画得出线，超出范围逻辑照常生效，只是不画线。
- 卡面（r95t 起）：在本地化写 `NSP_RDART_<id>: "GFX_你的图"`，图是 239×117 的单张 sprite。想借本体的图，就直接填 `GFX_NSP_rdart_<本体id>`。`reg_art` 不再参与显示。
- `reg_bonus = 1`：完成后研发槽 +1。
- `reg_uk1 / reg_uv1 / reg_uk2 / reg_uv2`：完成时的效果。

| uk | 效果 | uv |
|---|---|---|
| 1..4 | 解锁载荷 / 火箭 / 目的地 / 修正 | 对应 id（给本体内容用；子模组内容建议用 `reg_unlock_rd`） |
| 5..9 | 被动加成：火箭可靠性 / 载人可靠性 / 无人可靠性 / 成本减免 % / 工期减免 % | 数值 |
| 10 | 一次性拨款 | 百万 |
| 11 | 一次性民意 | 点数 |

`NSP_reg_rd_small`（`reg_id`）把项目画成小科技方卡。方卡图写本地化 `NSP_RDSART_<id>: "GFX_你的图"`（72×72 单张）。

---

## 5. 图和本地化

### 规划器大图（载荷 / 火箭 / 轨迹）

`reg_custom_art = 1` 时，规划器从本地化取 sprite 名，帧号用 `reg_art_frame`：

| 类型 | 本地化键 | 本体图集（可以直接借帧） |
|---|---|---|
| 载荷 | `NSP_PLART_<id>` | `GFX_NSP_payload_art`（帧 1..12 = 载荷 0..11） |
| 火箭 | `NSP_VEART_<id>` | `GFX_NSP_vehicle_art`（帧 1..9 = 火箭 0..8） |
| 轨迹 | `NSP_TRAJART_<id>` | `GFX_NSP_trajectory`（帧 1..8 = 目的地 0..7） |

自己画的话：在你自己的 `.gfx` 里定义 sprite（单帧或多帧都行，多帧记得写 `noOfFrames`），本地化写上 sprite 名。尺寸照本体：载荷图、火箭图、轨迹图分别和对应图集的单帧一样大，像素风只能 1:1 显示。

`reg_custom_art = 0`（默认）时直接用本体图集的第 id+1 帧。子模组的 id ≥ 50，超出本体帧数会显示空白，所以子模组内容**一定要设 `reg_custom_art = 1`**。

### 本地化键清单

| 类型 | 必须有的键 |
|---|---|
| 载荷 | `NSP_PL_NAME_<id>`、`NSP_PL_SHORT_<id>`、`NSP_PL_TYPE_<id>`、`NSP_PLBADGE_<id>`（徽章 sprite 名）、`NSP_PLART_<id>` |
| 火箭 | `NSP_VE_NAME_<id>`、`NSP_VE_TYPE_<id>`、`NSP_VEART_<id>` |
| 目的地 | `NSP_DEST_<id>`、`NSP_DEST_PHRASE_<id>`、`NSP_TRAJART_<id>` |
| 研发 | `NSP_RD_N_<id>`、`NSP_RD_DESC_<id>`、`NSP_RD_UNLOCK_<id>`、`NSP_RD_REQS_<id>` |

徽章可以直接用本体的：`GFX_NSP_badge_sat / lander / planet / station / comm / explorer / science / lunarorb / apollo / gemini / mercury`。

文字格式照本体：标签 `§F`、值 `§Y`、好 `§G`、坏 `§R`，每个 `§X` 都要配 `§!`；文案里写 `Delta-V`，不要写 `Δ`。

本体目前只有简体中文，你的 yml 放 `localisation/simp_chinese/`，文件名要以 `_l_simp_chinese.yml` 结尾，并且**带 BOM**。

---

## 6. 现在做不到的事

下面这些在 r94 还没开放，要做只能覆盖本体文件（会和别的子模组冲突）：

- ~~研发卡面自己画~~：r95t 起已支持，见上面的 `NSP_RDART_<id>`。
- **修正（发射 / 载荷修正）**：数量 20 个、规划器调色板都还是写死的，没有注册 API。
- **发射场**：8 个发射场和地图标记绑在一起，没有注册 API。
- **计划页签（水星 / 双子星 / 阿波罗…）和计划目标**：没有注册 API。
- **Mission Control 轨道行**：每个视图固定 3 行。
- 本体的 `NSP_mod_fits` 里，土星专用修正（9 / 10 / 11）仍然按火箭 2 / 3 判断，子模组火箭用不了这几个修正。

---

## 7. 研发树空格

研发树格位查表 `NSP_rd_index^(分类 × 40 + 行 × 8 + 列)`，空格的值等于 `NSP_rd_blank`（87）。r94 时的占用情况（`.` = 空）：

```
分类 0 运载火箭         分类 1 载人航天器       分类 2 生命保障
  0  1  2  3  .  . 60  .   12 13 14 15 16 64  . 65   21 22 23 24 25 76  .  .
  .  4  5  6  .  .  .  .    .  . 17 18  .  . 66  .    . 26 27  .  . 68  .  .
  .  7  8 10 11 59  .  .    .  .  . 19 20 67  .  .   28 29 30  .  .  .  .  .
  .  .  9  .  .  .  .  .    .  .  .  .  .  .  .  .   77 78 79 80 81  . 82  .
  .  .  .  .  . 61 62 63    .  .  .  .  .  .  .  .    . 83 84 85  . 86  .  .
分类 3 导航与对接       分类 4 无人探测         分类 5 地面设施
  . 31 32 33  . 69  .  .   40 41 42 43  . 71  .  .   50 51 52 53  . 74 75  .
  . 34 35 36  .  .  .  .    . 44 45 46  .  .  .  .   54  . 55  .  .  .  .  .
 37  . 38 39  . 70  .  .    . 47 48  . 49  .  .  .   56 57 58  .  .  .  .  .
  .  .  .  .  .  .  .  .    .  .  . 72  . 73  .  .   88 89 90 92  .  .  .  .
  .  .  .  .  .  .  .  .    . 94  .  .  .  .  .  .   91  . 93  .  .  .  .  .
```

（示例子模组占了分类 4「无人探测」第 5 行第 3 列，紧挨着 94 科研卫星。）

---

## 8. 扩展槽 / id 登记表

做了子模组请在这里登记一行，避免撞槽撞号。

| 槽 | 子模组 | 载荷 id | 火箭 id | 目的地 id | 研发 id |
|---|---|---|---|---|---|
| 1 | 示例：先驱者号（`examples/NSP_addon_example`，不要和别的子模组同时开） | 50 | 50 | 16 | 200 |
| 2 | | | | | |
| 3 | | | | | |

---

## 9. 本体里已经改成查表的规则（r94）

以前散在各个文件里、按 id 写死的判断，现在都查数组。本体的值写在 `NSP_api_effects.txt` 的 `NSP_api_base_tables`，子模组的 `register` 在它之后跑，所以可以用 API 改本体的值：

| 规则 | 数组 | 改法 |
|---|---|---|
| 哪些载荷载人 | `NSP_pl_crewed` | `NSP_reg_payload_crewed` |
| 载荷能去哪些目的地 | `NSP_pd_ok`（载荷 × 32 + 目的地） | `NSP_reg_allow` / `NSP_reg_deny` |
| 目的地经验、卫星天体、Mission Control 行、载人所需研发 | `NSP_dest_xp / body / view / row / crd` | `NSP_reg_dest_attrs` |
| 火箭需要的发射台研发、限定发射场 | `NSP_ve_pad / NSP_ve_site` | `NSP_reg_vehicle_limits` |
| 规划器载荷 / 火箭切换上限 | 读数组长度 | 自动 |

---

## 10. 自检清单

- [ ] 槽文件里 5 个钩子都在，名字里的 N 和文件名一致。
- [ ] 所有研发 id / 发射场 id 参数都明写了（不需要写 -1）。
- [ ] 子模组内容都设了 `reg_custom_art = 1`，本地化里有对应的 `*ART_<id>`。
- [ ] 新载荷至少 `NSP_reg_allow` 了一个目的地。
- [ ] 研发格子是空的，前置的列差 / 行差在连线范围内。
- [ ] yml 带 BOM，txt / gui / gfx 不带 BOM。
- [ ] `check_variable` 里没有 `>=` / `<=`（HOI4 不支持，用 `NOT = { check_variable = { a < b } }`）。
- [ ] 进游戏用调试决议完成全部研发，切换到你的载荷 / 火箭 / 目的地，确认 Delta-V 余量为正、能开始任务、error.log 里没有数组越界。
