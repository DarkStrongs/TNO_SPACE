# TNO 风格 HOI4 终极 GUI 与交互脚本开发规范
### `TNO_UI_Framework_Guide.md` · v1.0

> **适用范围**：Hearts of Iron IV（当前正式版）Mod 开发 · Scripted GUI / Interface / GFX / Variables / Scripted Localisation
> **权威来源**：HOI4 Wiki 词条 *Interface modding*、*Scripted GUI modding*、*Graphical asset modding*、*Data structures*、*Localisation*、*Console commands*、*Troubleshooting*、*Sound modding*（Wiki 镜像版本：2025-11-27）。
> **术语约定**：所有引擎关键字、文件夹名、属性名保持 Wiki 原文英文写法，不做翻译。

---

## 目录

1. [引言与 TNO UI 架构哲学](#1-引言与-tno-ui-架构哲学)
2. [工作流规范与文件树](#2-工作流规范与文件树)
3. [GUI 核心组件接口速查](#3-gui-核心组件接口速查)
4. [数据绑定：底层引擎与 UI 的桥梁](#4-数据绑定底层引擎与-ui-的桥梁)
5. [交互逻辑：Triggers 与 Effects 的结合](#5-交互逻辑triggers-与-effects-的结合)
6. [进阶实战：TNO 风格“代理人战争”面板](#6-进阶实战tno-风格代理人战争面板)
7. [调试与报错排查指南](#7-调试与报错排查指南)
8. [附录：团队编码规范清单](#8-附录团队编码规范清单)

---

## 1. 引言与 TNO UI 架构哲学

TNO 的 UI 不是“给原版换皮”，而是**在 Paradox 引擎之上搭建一个独立的、由变量驱动的信息终端**。本规范把这一哲学拆成两层。

### 1.1 视觉层（Visual Layer）

| 特征 | 实现手段 | 引擎接口 |
|---|---|---|
| **CRT / 终端感** | 深色底（近黑蓝灰）+ 扫描线纹理叠层 + 轻微辉光 | `iconType` 叠加半透明扫描线 DDS；`spriteType.animation`（`animationtype = scrolling`）做滚动扫描线 |
| **极简网格** | 1px 细线边框、严格 4/8px 栅格对齐、无装饰性浮雕 | `corneredTileSpriteType`（九宫格边框，`borderSize` 控制角）|
| **高对比度霓虹配色** | 冷战三色：信号绿（稳定）、琥珀黄（警戒）、警报红（危机）| §-颜色码；`[?var\|+]` 动态着色；`textcolors` 扩展 |
| **等宽 / 打字机字体** | 数据栏、编号、日志全部等宽 | 原版 `hoi_16typewriter`、`hoi4_typewriter16`、`hoi_22typewriter`；或自建 `bitmapfont` |
| **代码化排版** | 全大写标签、`>>`、`//`、方括号编号 `[03]`、日期戳 | 纯本地化文本约定 |
| **克制的动效** | 只用于状态切换（窗口淡入、警报脉冲）| 容器 `fade_time` / `animation_type`；`animationtype = pulsing` |

### 1.2 逻辑层（Logic Layer）

1. **变量是唯一真相源（Single Source of Truth）**：所有数值（紧张度、资金、派系支持）存在 `variable` 中，UI 只“读”和“发出请求”，绝不在 UI 层硬编码数值。
2. **深度 Scripted GUI**：用自定义 `containerWindowType` + `scripted_gui` 取代原生决议（Decision）面板，以获得任意布局、进度条、多状态按钮、右键/Shift 修饰键操作。
3. **逻辑与表现分离**：按钮的 `effects` 只调用 `scripted_effects`；`_click_enabled` 只调用 `scripted_triggers`。Wiki 明确指出：*“Scripted effects and triggers can be used in scripted GUIs, and can be useful to separate the GUI logic and the gameplay logic.”*
4. **高频变量 + 低频刷新**：数据在后台每日/每次操作更新，UI 用 `dirty` 变量控制刷新，避免每 tick 重算。
5. **一切可解释**：每个按钮都有 `pdx_tooltip`，并用 `[!<element>_click]` / `[!<element>_click_enabled]` 自动生成“效果 / 条件”提示，玩家永远知道为何置灰。

---

## 2. 工作流规范与文件树

### 2.1 标准文件树（以模块前缀 `PXW_` = Proxy War 为例）

```text
mod/
├── common/
│   ├── scripted_guis/                     # ⚠ 文件夹名必须为复数
│   │   └── PXW_scripted_guis.txt          # scripted_gui = { ... }：窗口绑定、按钮效果、触发器、properties
│   ├── scripted_effects/
│   │   └── PXW_scripted_effects.txt       # 所有游戏逻辑（扣 PP、改变量、发事件）
│   ├── scripted_triggers/
│   │   └── PXW_scripted_triggers.txt      # 可复用的条件判定
│   ├── scripted_localisation/
│   │   └── PXW_scripted_localisation.txt  # defined_text = { ... }：动态文本 / 动态贴图名
│   └── on_actions/
│       └── PXW_on_actions.txt             # 变量初始化（on_startup）、每日/每周 tick
├── events/
│   └── PXW_events.txt                     # 隐藏事件（hidden = yes）与叙事事件
├── interface/
│   ├── PXW_panel.gui                      # guiTypes = { containerWindowType ... }
│   └── PXW_panel.gfx                      # spriteTypes = { spriteType / corneredTileSpriteType ... }
├── gfx/
│   └── interface/PXW/                     # *.dds 贴图（边框、按钮、进度帧、扫描线）
├── sound/
│   └── PXW_ui_sounds.asset                # 自定义 UI 音效（sound / soundeffect）
└── localisation/
    ├── english/PXW_l_english.yml
    └── simp_chinese/PXW_l_simp_chinese.yml   # ⚠ UTF-8 with BOM
```

### 2.2 协同工作流（数据流向）

```text
 ┌────────────── on_actions / events ───────────────┐
 │ 初始化 & 周期性更新 variables / flags             │
 └──────────────────────┬───────────────────────────┘
                        ▼
              [ Variables / Flags ]  ◄──────────────┐
                        │                            │ effects（scripted_effects）
        读取            ▼                            │
 ┌──── scripted_localisation ────┐     ┌──── scripted_gui ────────────┐
 │ defined_text → 文本/颜色/GFX名 │◄───►│ visible / triggers / effects │
 └──────────────┬────────────────┘     │ properties（frame/image/x/y）│
                ▼                      └──────────────┬───────────────┘
        localisation/*.yml                            │ window_name 绑定
                └──────────────► interface/*.gui ◄────┘
                                        │ spriteType 引用
                                        ▼
                                 interface/*.gfx → gfx/*.dds
```

### 2.3 开发顺序（推荐）

1. **数据契约**：先写变量清单（名称、作用域、取值范围、谁写谁读）。
2. `.gfx` → `.gui`：先出静态布局，用 `scripted_gui` 的 `visible = { always = yes }` 临时常显，`guibounds` 对齐。
3. `scripted_triggers` / `scripted_effects`：写纯逻辑，可在控制台用 `set_var` / `get_var` 单测。
4. `scripted_gui`：绑定 `effects` / `triggers` / `properties` / `dirty`。
5. `scripted_localisation` + `.yml`：动态文本、颜色、tooltip。
6. `events` / `on_actions`：接入游戏循环。
7. AI：`ai_enabled` / `ai_weights`（若 AI 需要使用此面板）。

---

## 3. GUI 核心组件接口速查

### 3.1 `.gfx` 资源类型

| 类型 | 用途 | 关键属性 |
|---|---|---|
| `spriteType` | 静态图、按钮、多帧图（进度帧、状态灯）| `name`、`texturefile`、`noOfFrames`、`effectFile`、`legacy_lazy_load`、`transparencecheck`、`animation = { ... }` |
| `corneredTileSpriteType` | 可拉伸九宫格边框 / 窗口背景 | `texturefile`、`size = { x y }`、`borderSize = { x y }`、`tilingCenter` |
| `frameAnimatedSpriteType` | 帧动画（闪烁警报灯）| `noOfFrames`、`animation_rate_fps`、`looping`、`play_on_show`、`pause_on_loop` |
| `progressbartype` | 原版进度条资源 | `textureFile1`、`textureFile2`、`color`、`colortwo`、`size`、`horizontal`、`steps` |
| `textcolors` | 自定义 § 颜色键（`core.gfx`）| 单字符键，⚠ 同首字母会覆盖已有颜色 |
| `bitmapfont` | 自定义（等宽）字体 | 见 Wiki *Graphical asset modding § bitmapfont* |

```paradox_script
# interface/PXW_panel.gfx
spriteTypes = {
    corneredTileSpriteType = {
        name = "GFX_PXW_window_frame"
        texturefile = "gfx/interface/PXW/pxw_window_frame.dds"   # 路径相对 mod 根目录
        size = { x = 64 y = 64 }
        borderSize = { x = 8 y = 8 }       # 8px 角不拉伸，中间平铺
    }
    spriteType = {
        name = "GFX_PXW_button_terminal"
        texturefile = "gfx/interface/PXW/pxw_button_terminal.dds"
        effectFile = "gfx/FX/buttonstate.lua"   # 悬停 / 按下 / 禁用 状态由按钮着色器处理
    }
}
```

> **多帧约定**：`noOfFrames = N` 的贴图是**横向等宽排列**的 N 帧条带。GUI 中 `frame` 建议从 **1** 开始计数（原版惯例）。

### 3.2 `.gui` 容器：`containerWindowType`

| 属性 | 说明 |
|---|---|
| `name` | 唯一名称；独立容器必须唯一，`scripted_gui.window_name` 绑定它 |
| `position` / `size` | 像素或百分比（`.gui` 中百分号写作 `%%` 或 `%`）|
| `orientation` / `origo` | 锚点：`UPPER_LEFT`、`CENTER`、`LOWER_RIGHT`、`CENTER_UP` 等 |
| `background = { name spriteType/quadTextureSprite }` | 背景；**滚动条必须有 background** |
| `clipping` | 默认 `yes`；滚动必须为 `yes` |
| `moveable = yes` | 玩家可拖拽 |
| `verticalScrollbar` / `scroll_wheel_factor` / `smooth_scrolling` / `margin` | 滚动 |
| `fade_time` / `fade_type` / `animation_type` / `animation_time` / `show_position` / `hide_position` | 动效 |
| `show_sound` / `hide_sound` | 窗口打开 / 关闭音效 |

> ⚠ **Scripted GUI 只能绑定独立容器**（不嵌套于其他容器中的 `containerWindowType`）。但它会作用于容器内所有子元素，包括更深层嵌套容器。

### 3.3 元素速查

| 元素 | 可被 Scripted GUI 驱动 | 关键属性 |
|---|:---:|---|
| `iconType` | ✅ | `name`、`position`、`orientation`、`spriteType` / `quadTextureSprite`、`frame`、`alwaystransparent`、`pdx_tooltip`、`pdx_tooltip_delayed`、`centerposition` |
| `instantTextBoxType` | ✅ | `name`、`position`、`text`、`font`、`maxWidth`、`maxHeight`、`format`（`left`/`center`/`right`）、`fixedsize`、`borderSize`、`alwaystransparent`、`pdx_tooltip` |
| `buttonType` | ✅ | `name`、`position`、`spriteType` / `quadTextureSprite`、`frame`、`buttonText`、`buttonFont`、`shortcut`、**`clicksound`**、**`oversound`**、`pdx_tooltip`、`pdx_tooltip_delayed`、`scale`、`web_link` |
| `gridBoxType` | ✅（配合 `dynamic_lists`）| `name`、`size`、`slotsize`、`format`、`max_slots_horizontal`、`max_slots_vertical` |
| `smoothListboxType` / `listboxType` / `checkboxType` / `editBoxType` / `OverlappingElementsBoxType` | ❌ 依赖内部代码 | 新建不会被填充数据 |

> 旧写法 `guiButtonType` = `buttonType`，`textBoxType` = `instantTextBoxType`，新代码一律使用新写法。

### 3.4 TNO 风格字体选型

| 场景 | 原版字体 | 备注 |
|---|---|---|
| 终端数据、编号、日志 | `hoi_16typewriter`、`hoi4_typewriter16` | 最接近等宽打字机感 |
| 面板大标题 | `hoi_22typewriter`、`hoi4_typewriter22`、`hoi_24header` | 全大写 |
| 按钮文本 | `hoi_16mbs`、`hoi_18mbs` | 清晰度最高 |
| 小号注释 | `Arial12` | 只用于次要信息 |

> 需要真正的等宽霓虹字体时，自建 `bitmapfont`（Wiki *Graphical asset modding*），并在其中为特定 § 颜色字符重定义颜色。

### 3.5 音效接口（`clicksound` / `oversound` / `show_sound` / `hide_sound`）

TNO 风格要求“机械键盘 / 继电器 / 电传打字机”式的短促反馈。做法是**在 `sound/*.asset` 中定义自己的 `soundeffect`，再在 `.gui` 中按名字引用**。

```paradox_script
# sound/PXW_ui_sounds.asset
sound = {
    name = "pxw_relay_click_wav"
    file = "pxw/relay_click.wav"          # 相对 mod/sound/
}
sound = {
    name = "pxw_teletype_wav"
    file = "pxw/teletype_burst.wav"
}

soundeffect = {
    name = pxw_ui_click                   # ← .gui 中 clicksound = pxw_ui_click
    sounds = { sound = pxw_relay_click_wav }
    volume = 0.6
    max_audible = 1
    playbackrate_random_offset = { 0.95 1.05 }   # 轻微随机，避免机械重复
}
soundeffect = {
    name = pxw_ui_open
    sounds = { sound = pxw_teletype_wav }
    volume = 0.5
}
```

| 接口 | 挂载位置 | 推荐用法 |
|---|---|---|
| `clicksound` | `buttonType` / `checkboxType` | 每个可点击按钮必须有；危险操作用更“重”的音 |
| `oversound` | `buttonType` | 悬停短嘀声；全局统一一种，避免噪音 |
| `show_sound` / `hide_sound` | `containerWindowType` | 面板开 / 关（电传 / 继电器）|
| 原版回退 | — | `click_default`、`click_close`、`click_ok` 等原版音效名可直接引用 |

> 音效名在 `.gui` 中不加引号亦可；**名字写错不会报“红狗”**，只会无声，务必在 `error.log` 中搜索 `sound`。

---

## 4. 数据绑定：底层引擎与 UI 的桥梁

### 4.1 变量基础（Wiki: *Data structures § Variables*）

| 要点 | 规范 |
|---|---|
| 精度 | 定点数，精度 1/1000；范围 **-2 147 483.648 ~ 2 147 483.647**，溢出会回绕 |
| 命名 | 字母/数字/下划线，**不能以数字开头**；必须加模块前缀（`PXW_`）避免与内置游戏变量（如 `capital`）冲突 |
| 作用域 | 默认当前 scope；`global.var` 全局；`GER.var`、`PREV.var`；变量链用 `:`（如 `GER.capital:var`）|
| 作用域化变量 | 变量存国家/州时，用作 scope 必须 `var:my_var = { ... }` |
| 未设置的变量 | 读取视为 `0`（这也是“读取为 0”Bug 的根源，见第 7 章）|
| 临时变量 | `set_temp_variable` 等，仅在当前效果/触发器块内存在 |
| 布尔状态 | 优先用 **flag**（`set_country_flag`），比变量更省 |

### 4.2 常用运算 Effects

```paradox_script
set_variable          = { PXW_funds = 100 }                # 设值 / 创建
set_variable          = { var = PXW_funds value = 100 tooltip = PXW_set_funds_tt }
add_to_variable       = { PXW_funds = 25 }
subtract_from_variable= { PXW_funds = 10 }
multiply_variable     = { PXW_funds = 1.1 }
divide_variable       = { PXW_funds = 2 }
modulo_variable       = { PXW_funds = 7 }
round_variable        = PXW_funds
clamp_variable        = { var = PXW_funds min = 0 max = 500 }
set_variable_to_random= { var = PXW_roll min = 0 max = 100 integer = yes }

set_temp_variable     = { t_cost = PXW_base_cost }         # 临时变量同名族：*_temp_variable
multiply_temp_variable= { t_cost = modifier@political_power_cost }  # 可读取 modifier@ 值

set_variable = { global.PXW_tension = 0 }                  # 在任意 scope 写全局变量
```

### 4.3 常用判定 Triggers

```paradox_script
check_variable = { PXW_funds > 50 }                        # 简写
check_variable = { var = PXW_funds value = 50 compare = greater_than_or_equals }
check_variable = { global.PXW_tension >= 75 }
has_variable   = PXW_funds                                 # 是否已初始化
```

### 4.4 在 UI 上显示变量：`[?var|格式]`

`.gui` 的 `text` / `buttonText` 写**本地化键**，在 `.yml` 中用 `[?...]` 读取。（`?` 是必须的，用于区分变量与 event target。）

| 格式字符 | 效果 |
|---|---|
| `0`–`3` | 小数位数（最多 3 位）；原版惯例写作 `.1` |
| `%` | ×100 并追加 `%` |
| `%%` | 不乘 100，只追加 `%` |
| `*` / `^` | SI 缩写（K / M）|
| `=` | 强制显示正负号 |
| `+` | 正绿 / 零黄 / 负红（“好数字”）|
| `-` | 正红 / 零黄 / 负绿（“坏数字”，适合紧张度、通胀）|
| `R` `G` `Y` `W` … | 静态着色（**优先级低于 `+` / `-`**）|

```yaml
l_english:
 PXW_TENSION_VALUE: "[?global.PXW_tension|Y0] / 100"
 PXW_FUNDS_VALUE: "$ [?PXW_funds|*1]"                    # 1250000 → 1.2M
 PXW_DELTA_VALUE: "[?PXW_tension_delta|=-1]"             # 带符号，上升为红色
 PXW_SUPPORT_PCT: "[?PXW_support|%G0]"                   # 0.42 → 42%
```

> **作用域提示**：`[?var]` 读取的是 **scripted GUI 当前默认 scope**（由 `context_type` 决定）。`player_context` 下就是玩家国家；读全局必须写 `global.`。

### 4.5 动态文本：Scripted Localisation（`defined_text`）

定义于 `common/scripted_localisation/*.txt`；**自上而下取第一个 `trigger` 为真的 `text`**。注意关键字为美式拼写 `localization_key`。

```paradox_script
defined_text = {
    name = GetPXWStatus
    text = {
        trigger = { check_variable = { global.PXW_tension >= 75 } }
        localization_key = PXW_STATUS_CRISIS
    }
    text = {
        trigger = { check_variable = { global.PXW_tension >= 40 } }
        localization_key = PXW_STATUS_TENSE
    }
    text = {
        localization_key = PXW_STATUS_STABLE          # 无 trigger = 兜底
    }
}
```

```yaml
l_english:
 PXW_STATUS_LABEL: "STATUS >> [GetPXWStatus]"
 PXW_STATUS_STABLE: "§GSTABLE§!"
 PXW_STATUS_TENSE:  "§YESCALATING§!"
 PXW_STATUS_CRISIS: "§RCRISIS§!"
```

**颜色码规范（TNO 冷战三色）**

| 码 | 颜色 | 语义 |
|---|---|---|
| `§G` | 绿 (0,159,3) | 稳定 / 正面 / 可执行 |
| `§Y` / `§H` | 黄 (255,189,0) | 警戒 / 数值高亮 |
| `§O` | 橙 (255,112,25) | 升级中 |
| `§R` | 红 (255,50,50) | 危机 / 不可执行 / 负面 |
| `§g` | 浅灰 (176,176,176) | 次要信息、注释、置灰文本 |
| `§W` / `§T` | 白 | 标题 |
| `§!` | 结束着色 | **每个 § 必须以 `§!` 闭合** |

**进阶技巧**

- **Dynamic Scripted Localisation**：`localization_key = "PXW_phase_[?PXW_phase]"` → 自动选 `PXW_phase_1/2/3`，省去长串 `text` 块。
- **临时变量做数学**：`trigger` 中设置的临时变量在显示该 key 时仍有效（可做百分比、差值等计算后显示）。
- **动态贴图**：`properties` 的 `image` 接受 scripted loc，让 `defined_text` 返回 `GFX_` 名字即可切换图标（见 6.4）。

---

## 5. 交互逻辑：Triggers 与 Effects 的结合

### 5.1 `scripted_gui` 结构总览（Wiki 模板）

```paradox_script
scripted_gui = {
    <id> = {
        context_type = player_context          # 不设则 UI 拿不到任何游戏状态
        window_name = "<independent_container>"
        parent_window_token = top_bar          # 或 parent_window_name = xxx(_instance)
        dirty = <variable>                     # 可选：只在该变量变化时刷新 properties

        visible  = { <triggers> }              # 整个窗口是否显示
        effects  = { <element>_click = { } <element>_right_click = { } ... }
        triggers = { <element>_click_enabled = { } <element>_visible = { } }
        properties = { <element> = { image = "" frame = <var> x = <var> y = <var> } }
        dynamic_lists = { <gridbox> = { array = ... entry_container = "..." } }

        ai_enabled = { } ai_weights = { } ...
    }
}
```

**`context_type` 选择**

| 值 | 默认 scope | 典型用途 |
|---|---|---|
| `player_context` | 玩家国家（= ROOT）| 绝大多数 TNO 风格面板 |
| `selected_country_context` | 当前选中国家 | 外交侧栏扩展（对他国施加代理人支持）|
| `selected_state_context` | 当前选中州 | 州级面板 |
| `decision_category` | 决议类别 | 嵌入决议类别描述（类别中写 `scripted_gui = <id>`，不设 parent）|
| `national_focus_context` | 国策树所属国 | 国策界面叠层 |
| `country_mapicon` / `state_mapicon` | 每个国家 / 州 | 地图图标 |
| `diplomatic_action` | 外交行动 | Scripted diplomatic actions |

> 默认 scope 与 ROOT 不同时，用 `PREV` 回指。**禁止在 Scripted GUI 中使用 event target / `save_event_target_as`**——Wiki 原话 *“it will break everything”*，用变量 scope 代替。

### 5.2 Visible：显示 / 隐藏

| 层级 | 写法 | 说明 |
|---|---|---|
| 窗口 | `visible = { has_country_flag = PXW_panel_open }` | TNO 标准“开关面板”模式：按钮设 flag，窗口读 flag |
| 元素 | `triggers = { <element>_visible = { ... } }` | 适用于任意元素（icon / text / button）|

> - `dirty` **不影响** 窗口 `visible` 的刷新。
> - 元素不可见时 AI 也无法点击。
> - 窗口 `visible` 每次评估都会跑，保持轻量；昂贵判定放在元素级 trigger 或用 flag 缓存结果。

### 5.3 Available：`_click_enabled` 与“条件未满足”置灰

HOI4 中“available”的引擎写法为 **`<element>_click_enabled`**：

```paradox_script
triggers = {
    PXW_fund_button_click_enabled = {
        PXW_can_fund_insurgents = yes          # scripted_trigger
    }
    PXW_fund_button_right_click_enabled = { ... }   # 可单独控制修饰键
}
```

- `_click_enabled` 为假时按钮进入禁用态（配合 `effectFile = "gfx/FX/buttonstate.lua"` 的按钮着色器呈现置灰）。
- ⚠ `<element>_click_enabled` **会覆盖** `<element>_right_click_enabled` 等更具体的触发器。
- **TNO 式“为何置灰”**：在按钮 `pdx_tooltip` 中放 `[!PXW_fund_button_click_enabled]`，引擎会自动列出条件及其满足情况（✔/✘）；再追加 `[!PXW_fund_button_click]` 列出效果。
- 想要更强烈的视觉（“LOCKED” 印章 / 红色遮罩），用额外 `iconType` + `_visible` 取反条件叠加在按钮上，并设 `alwaystransparent = yes`。

### 5.4 点击响应：Effects

```paradox_script
effects = {
    PXW_fund_button_click = {                     # 左键
        PXW_fund_insurgents = yes                 # scripted_effect：扣 PP、改变量、发事件
    }
    PXW_fund_button_shift_click = { ... }         # 修饰键：right / alt / control / shift，可串联
    PXW_fund_button_alt_right_click = { ... }
}
```

**常用效果速查**

| 目的 | Effect |
|---|---|
| 扣 / 加政治点数 | `add_political_power = -25` |
| 改稳定度 / 战争支持 | `add_stability = -0.02` / `add_war_support = 0.01` |
| 改变量 | `add_to_variable` / `clamp_variable` 等（4.2）|
| 开关面板 | `set_country_flag` / `clr_country_flag` |
| 触发隐藏事件 | `country_event = { id = pxw.10 hours = 1 }`（事件中 `hidden = yes`）|
| 给出无副作用的提示行 | `custom_effect_tooltip = PXW_some_tt` |
| 隐藏执行（不进 tooltip）| `hidden_effect = { ... }` |
| 冷却 | `set_country_flag = { flag = PXW_cd days = 30 value = 1 }` |
| 强制刷新 dirty GUI | `add_to_variable = { PXW_gui_dirty = 1 }` |

> **防作弊原则**：`effects` 内**再次校验**关键条件（`if = { limit = { ... } }`），不要只依赖 `_click_enabled`——多人联机与 AI 调用时这是最后防线。

---

## 6. 进阶实战：TNO 风格“代理人战争”面板

### 6.0 需求规格

| 项 | 规格 |
|---|---|
| 数据 | `global.PXW_tension`（0–100，全球紧张度）；`PXW_support`（0–10，本国对代理方的支持等级）|
| 显示 | 标题、20 格帧式进度条、紧张度数值、支持等级、状态文本（稳定 / 升级 / 危机，变色）|
| 按钮 1 | **[FUND]** 左键：-25 PP，`PXW_support +1`，`tension +5`；条件：PP ≥ 25、支持 < 10、无冷却 |
| 按钮 1 右键 | **撤资**：`PXW_support -1`，`tension -3`；条件：支持 > 0 |
| 按钮 2 | **[CLOSE]** 关闭面板 |
| 开关 | 顶栏小按钮切换 `PXW_panel_open` flag |
| 事件 | 紧张度首次达到 100 → 隐藏事件分发危机；支持达到 10 → 叙事事件 |
| 性能 | `dirty = PXW_gui_dirty` |

### 6.1 `.gfx` —— `interface/PXW_panel.gfx`

```paradox_script
spriteTypes = {
    # —— 窗口九宫格边框：深色底 + 1px 霓虹绿描边 ——
    corneredTileSpriteType = {
        name = "GFX_PXW_window_frame"
        texturefile = "gfx/interface/PXW/pxw_window_frame.dds"
        size = { x = 64 y = 64 }
        borderSize = { x = 8 y = 8 }
    }

    # —— CRT 扫描线叠层（半透明，滚动动画）——
    spriteType = {
        name = "GFX_PXW_scanlines"
        texturefile = "gfx/interface/PXW/pxw_scanlines.dds"
        alwaystransparent = yes
        animation = {
            animationmaskfile = "gfx/interface/PXW/pxw_scanlines.dds"
            animationtexturefile = "gfx/interface/PXW/pxw_scanline_sweep.dds"
            animationrotation = -90.0
            animationlooping = yes
            animationtime = 6.0
            animationdelay = 0.0
            animationblendmode = "add"
            animationtype = "scrolling"
            animationrotationoffset = { x = 0.0 y = 0.0 }
            animationtexturescale = { x = 1.0 y = 1.0 }
        }
    }

    # —— 终端风按钮（三态由 buttonstate.lua 处理）——
    spriteType = {
        name = "GFX_PXW_button_terminal"
        texturefile = "gfx/interface/PXW/pxw_button_terminal.dds"   # 160x28
        effectFile = "gfx/FX/buttonstate.lua"
    }
    spriteType = {
        name = "GFX_PXW_button_close"
        texturefile = "gfx/interface/PXW/pxw_button_close.dds"      # 20x20
        effectFile = "gfx/FX/buttonstate.lua"
    }
    spriteType = {
        name = "GFX_PXW_topbar_toggle"
        texturefile = "gfx/interface/PXW/pxw_topbar_toggle.dds"
        effectFile = "gfx/FX/buttonstate.lua"
    }

    # —— 帧式进度条：21 帧（0%,5%,...,100%），横向条带 21 x (240x14) ——
    spriteType = {
        name = "GFX_PXW_tension_bar"
        texturefile = "gfx/interface/PXW/pxw_tension_bar_strip.dds"
        noOfFrames = 21
        legacy_lazy_load = no
    }

    # —— 状态指示灯：3 帧 绿/黄/红 ——
    spriteType = {
        name = "GFX_PXW_status_lamp"
        texturefile = "gfx/interface/PXW/pxw_status_lamp.dds"
        noOfFrames = 3
        legacy_lazy_load = no
    }

    # —— 危机印章（动态 image 切换示例）——
    spriteType = { name = "GFX_PXW_stamp_none"   texturefile = "gfx/interface/PXW/pxw_stamp_none.dds" }
    spriteType = { name = "GFX_PXW_stamp_crisis" texturefile = "gfx/interface/PXW/pxw_stamp_crisis.dds" }
}
```

> 为什么用**帧式进度条**而不是 `progressbarType`？Wiki 列出的 `properties` 只暴露 `image` / `frame` / `x` / `y`，用 `frame = <var>` 驱动多帧贴图是脚本端唯一完全可控、且能做出 TNO 式“分格 LED”外观的方案。

### 6.2 `.gui` —— `interface/PXW_panel.gui`

```paradox_script
guiTypes = {

    # ============ 顶栏开关按钮（独立容器）============
    containerWindowType = {
        name = "PXW_topbar_toggle_window"
        position = { x = 560 y = 4 }
        size = { width = 32 height = 32 }

        buttonType = {
            name = "PXW_toggle_button"
            position = { x = 0 y = 0 }
            spriteType = "GFX_PXW_topbar_toggle"
            clicksound = pxw_ui_click
            oversound = click_default
            pdx_tooltip = "PXW_TOGGLE_TT"
        }
    }

    # ============ 主面板（独立容器）============
    containerWindowType = {
        name = "PXW_main_window"
        position = { x = -200 y = -150 }
        size = { width = 400 height = 300 }
        orientation = CENTER
        moveable = yes
        fade_time = 200
        fade_type = linear
        show_sound = pxw_ui_open
        hide_sound = click_close

        background = {
            name = "Background"
            quadTextureSprite = "GFX_PXW_window_frame"
        }

        # --- 标题行（等宽、全大写、代码化）---
        instantTextBoxType = {
            name = "PXW_title"
            position = { x = 16 y = 12 }
            font = "hoi_22typewriter"
            text = "PXW_TITLE"
            maxWidth = 330
            maxHeight = 24
            format = left
            fixedsize = yes
        }
        buttonType = {
            name = "PXW_close_button"
            position = { x = 366 y = 12 }
            spriteType = "GFX_PXW_button_close"
            clicksound = click_close
            pdx_tooltip = "PXW_CLOSE_TT"
        }

        # --- 分隔注释行 ---
        instantTextBoxType = {
            name = "PXW_subtitle"
            position = { x = 16 y = 40 }
            font = "hoi_16typewriter"
            text = "PXW_SUBTITLE"
            maxWidth = 368
            maxHeight = 16
            format = left
        }

        # --- 紧张度：标签 + 帧式进度条 + 数值 ---
        instantTextBoxType = {
            name = "PXW_tension_label"
            position = { x = 16 y = 72 }
            font = "hoi_16typewriter"
            text = "PXW_TENSION_LABEL"
            maxWidth = 120
            maxHeight = 16
        }
        iconType = {
            name = "PXW_tension_bar"
            position = { x = 16 y = 92 }
            spriteType = "GFX_PXW_tension_bar"
            frame = 1
            pdx_tooltip = "PXW_TENSION_TT"
        }
        instantTextBoxType = {
            name = "PXW_tension_value"
            position = { x = 264 y = 90 }
            font = "hoi_16typewriter"
            text = "PXW_TENSION_VALUE"
            maxWidth = 120
            maxHeight = 16
            format = right
        }

        # --- 支持等级 ---
        instantTextBoxType = {
            name = "PXW_support_value"
            position = { x = 16 y = 124 }
            font = "hoi_16typewriter"
            text = "PXW_SUPPORT_VALUE"
            maxWidth = 368
            maxHeight = 16
        }

        # --- 状态行：指示灯 + 动态文本 + 危机印章 ---
        iconType = {
            name = "PXW_status_lamp"
            position = { x = 16 y = 154 }
            spriteType = "GFX_PXW_status_lamp"
            frame = 1
        }
        instantTextBoxType = {
            name = "PXW_status_text"
            position = { x = 40 y = 154 }
            font = "hoi_18mbs"
            text = "PXW_STATUS_LABEL"
            maxWidth = 240
            maxHeight = 20
        }
        iconType = {
            name = "PXW_crisis_stamp"
            position = { x = 280 y = 140 }
            spriteType = "GFX_PXW_stamp_none"
            alwaystransparent = yes
        }

        # --- 操作按钮 ---
        buttonType = {
            name = "PXW_fund_button"
            position = { x = 16 y = 240 }
            spriteType = "GFX_PXW_button_terminal"
            buttonText = "PXW_FUND_BUTTON"
            buttonFont = "hoi_16mbs"
            clicksound = pxw_ui_click
            oversound = click_default
            pdx_tooltip = "PXW_FUND_TT"
        }
        instantTextBoxType = {
            name = "PXW_cost_hint"
            position = { x = 190 y = 246 }
            font = "hoi_16typewriter"
            text = "PXW_COST_HINT"
            maxWidth = 190
            maxHeight = 16
            format = right
        }

        # --- CRT 扫描线叠层：最后定义 = 最上层；alwaystransparent 保证点击穿透 ---
        iconType = {
            name = "PXW_scanlines"
            position = { x = 0 y = 0 }
            spriteType = "GFX_PXW_scanlines"
            alwaystransparent = yes
        }
    }
}
```

> **绘制顺序**：后定义者在上层。扫描线放最后，并且**必须** `alwaystransparent = yes`，否则会挡住所有按钮点击。

### 6.3 `scripted_triggers` —— `common/scripted_triggers/PXW_scripted_triggers.txt`

```paradox_script
PXW_can_fund_insurgents = {
    custom_trigger_tooltip = {
        tooltip = PXW_TT_NEED_PP
        has_political_power > 24.999
    }
    custom_trigger_tooltip = {
        tooltip = PXW_TT_SUPPORT_CAP
        check_variable = { PXW_support < 10 }
    }
    custom_trigger_tooltip = {
        tooltip = PXW_TT_COOLDOWN
        NOT = { has_country_flag = PXW_fund_cooldown }
    }
}

PXW_can_withdraw = {
    custom_trigger_tooltip = {
        tooltip = PXW_TT_NOTHING_TO_WITHDRAW
        check_variable = { PXW_support > 0 }
    }
}
```

### 6.4 `scripted_effects` —— `common/scripted_effects/PXW_scripted_effects.txt`

```paradox_script
PXW_init = {
    if = {
        limit = { NOT = { has_global_flag = PXW_initialised } }
        set_global_flag = PXW_initialised
        set_variable = { global.PXW_tension = 20 }
    }
    set_variable = { PXW_support = 0 }
    set_variable = { PXW_gui_dirty = 0 }
}

PXW_fund_insurgents = {
    if = {
        limit = { PXW_can_fund_insurgents = yes }       # effects 内二次校验
        add_political_power = -25
        add_to_variable = { PXW_support = 1 }           # ← 核心：变量 +1
        clamp_variable = { var = PXW_support min = 0 max = 10 }
        add_to_variable = { global.PXW_tension = 5 }
        clamp_variable = { var = global.PXW_tension min = 0 max = 100 }
        set_country_flag = { flag = PXW_fund_cooldown days = 7 value = 1 }
        PXW_post_change = yes
    }
}

PXW_withdraw_support = {
    if = {
        limit = { PXW_can_withdraw = yes }
        subtract_from_variable = { PXW_support = 1 }
        subtract_from_variable = { global.PXW_tension = 3 }
        clamp_variable = { var = global.PXW_tension min = 0 max = 100 }
        PXW_post_change = yes
    }
}

# 每次数据变化后的统一收口：发事件 + 刷新 GUI
PXW_post_change = {
    hidden_effect = {
        if = {
            limit = {
                check_variable = { global.PXW_tension >= 100 }
                NOT = { has_global_flag = PXW_crisis_fired }
            }
            set_global_flag = PXW_crisis_fired
            country_event = { id = pxw.10 hours = 1 }          # 隐藏分发事件
        }
        if = {
            limit = {
                check_variable = { PXW_support >= 10 }
                NOT = { has_country_flag = PXW_max_support_fired }
            }
            set_country_flag = PXW_max_support_fired
            country_event = { id = pxw.2 days = 1 }            # 叙事事件
        }
        add_to_variable = { PXW_gui_dirty = 1 }                # 触发 dirty 刷新
    }
}
```

### 6.5 `scripted_gui` —— `common/scripted_guis/PXW_scripted_guis.txt`

```paradox_script
scripted_gui = {

    # ---------- 顶栏开关 ----------
    PXW_topbar_toggle = {
        context_type = player_context
        window_name = "PXW_topbar_toggle_window"
        parent_window_token = top_bar           # 会被国策/政治等弹出菜单遮挡
        visible = { has_global_flag = PXW_initialised }

        effects = {
            PXW_toggle_button_click = {
                if = {
                    limit = { has_country_flag = PXW_panel_open }
                    clr_country_flag = PXW_panel_open
                }
                else = { set_country_flag = PXW_panel_open }
            }
        }
        ai_enabled = { always = no }
    }

    # ---------- 主面板 ----------
    PXW_main_panel = {
        context_type = player_context
        window_name = "PXW_main_window"
        dirty = PXW_gui_dirty

        visible = { has_country_flag = PXW_panel_open }

        effects = {
            PXW_fund_button_click        = { PXW_fund_insurgents = yes }
            PXW_fund_button_right_click  = { PXW_withdraw_support = yes }
            PXW_close_button_click       = { clr_country_flag = PXW_panel_open }
        }

        triggers = {
            # “available” → _click_enabled
            PXW_fund_button_click_enabled       = { PXW_can_fund_insurgents = yes }
            PXW_fund_button_right_click_enabled = { PXW_can_withdraw = yes }
            # ⚠ 未写 PXW_fund_button_click_enabled 以外的通用覆盖，否则会吞掉右键条件

            # 计算进度帧与状态帧（临时变量供 properties 使用）
            PXW_tension_bar_visible = {
                set_temp_variable = { t_bar = global.PXW_tension }
                divide_temp_variable = { t_bar = 5 }
                round_temp_variable = t_bar
                add_to_temp_variable = { t_bar = 1 }          # 帧 1..21
                clamp_temp_variable = { var = t_bar min = 1 max = 21 }
                always = yes
            }
            PXW_status_lamp_visible = {
                if = {
                    limit = { check_variable = { global.PXW_tension >= 75 } }
                    set_temp_variable = { t_lamp = 3 }
                }
                else_if = {
                    limit = { check_variable = { global.PXW_tension >= 40 } }
                    set_temp_variable = { t_lamp = 2 }
                }
                else = { set_temp_variable = { t_lamp = 1 } }
                always = yes
            }
        }

        properties = {
            PXW_tension_bar  = { frame = t_bar }
            PXW_status_lamp  = { frame = t_lamp }
            PXW_crisis_stamp = { image = "[GetPXWStamp]" }      # 由 scripted loc 返回 GFX 名
        }

        # AI 也可使用该面板（示例：支持低于 3 且 PP 充足时投资）
        ai_enabled = { always = yes }
        ai_test_interval = 168
        ai_weights = {
            PXW_fund_button_click = {
                ai_will_do = {
                    base = 1
                    modifier = { factor = 0 check_variable = { PXW_support >= 3 } }
                    modifier = { factor = 0 has_political_power < 100 }
                }
            }
        }
    }
}
```

> 注：在 `triggers` 块中用 `if/else` 设置临时变量属于 Wiki 认可的“Temporary variable usage”模式；块末 `always = yes` 保证元素仍可见。AI 只能点击**可见**的元素，且需要窗口 `visible` 对 AI 也为真——若 AI 永远不设 `PXW_panel_open`，请把 AI 逻辑改为 `on_actions` 驱动，或在 `visible` 中加入 `is_ai = yes` 分支。

### 6.6 `scripted_localisation` —— `common/scripted_localisation/PXW_scripted_localisation.txt`

```paradox_script
defined_text = {
    name = GetPXWStatus
    text = {
        trigger = { check_variable = { global.PXW_tension >= 75 } }
        localization_key = PXW_STATUS_CRISIS          # “危机”
    }
    text = {
        trigger = { check_variable = { global.PXW_tension >= 40 } }
        localization_key = PXW_STATUS_TENSE
    }
    text = {
        localization_key = PXW_STATUS_STABLE          # “稳定”
    }
}

defined_text = {
    name = GetPXWStamp
    text = {
        trigger = { check_variable = { global.PXW_tension >= 75 } }
        localization_key = GFX_PXW_stamp_crisis
    }
    text = {
        localization_key = GFX_PXW_stamp_none
    }
}
```

> `GetPXWStamp` 返回的“本地化键”直接就是 `GFX_` 名。为保险起见，在 `.yml` 中也写一份同名键，值等于自身（`GFX_PXW_stamp_crisis: "GFX_PXW_stamp_crisis"`），避免 `text.log` 报缺键。

### 6.7 `localisation` —— 中英文

```yaml
# localisation/english/PXW_l_english.yml   (UTF-8 with BOM)
l_english:
 PXW_TITLE: "§W// PROXY WAR DESK§!"
 PXW_SUBTITLE: "§gTERMINAL 03 >> COVERT ALLOCATION LEDGER§!"
 PXW_TENSION_LABEL: "GLOBAL TENSION"
 PXW_TENSION_VALUE: "[?global.PXW_tension|-0] / 100"
 PXW_TENSION_TT: "Global tension rises with every covert escalation.\nAt §R100§! a crisis is triggered."
 PXW_SUPPORT_VALUE: "SUPPORT LEVEL >> [?PXW_support|Y0] / 10"
 PXW_STATUS_LABEL: "STATUS >> [GetPXWStatus]"
 PXW_STATUS_STABLE: "§GSTABLE§!"
 PXW_STATUS_TENSE: "§YESCALATING§!"
 PXW_STATUS_CRISIS: "§RCRISIS§!"
 PXW_FUND_BUTTON: "[ FUND ]"
 PXW_FUND_TT: "§YLeft-click§!: fund the insurgency.\n§YRight-click§!: withdraw support.\n\n[!PXW_fund_button_click_enabled]\n--------------\n[!PXW_fund_button_click]"
 PXW_COST_HINT: "§g-25 PP / +5 TENSION§!"
 PXW_TOGGLE_TT: "Open the Proxy War Desk"
 PXW_CLOSE_TT: "Close"
 PXW_TT_NEED_PP: "Has at least §Y25§! political power"
 PXW_TT_SUPPORT_CAP: "Support level is below §Y10§!"
 PXW_TT_COOLDOWN: "Funding channel is not on cooldown"
 PXW_TT_NOTHING_TO_WITHDRAW: "Support level is above §Y0§!"
 GFX_PXW_stamp_none: "GFX_PXW_stamp_none"
 GFX_PXW_stamp_crisis: "GFX_PXW_stamp_crisis"
```

```yaml
# localisation/simp_chinese/PXW_l_simp_chinese.yml   (UTF-8 with BOM)
l_simp_chinese:
 PXW_TITLE: "§W// 代理人战争指挥台§!"
 PXW_SUBTITLE: "§g终端 03 >> 秘密拨款账簿§!"
 PXW_TENSION_LABEL: "全球紧张度"
 PXW_TENSION_VALUE: "[?global.PXW_tension|-0] / 100"
 PXW_TENSION_TT: "每一次秘密升级都会推高全球紧张度。\n达到 §R100§! 时将爆发危机。"
 PXW_SUPPORT_VALUE: "支持等级 >> [?PXW_support|Y0] / 10"
 PXW_STATUS_LABEL: "局势 >> [GetPXWStatus]"
 PXW_STATUS_STABLE: "§G稳定§!"
 PXW_STATUS_TENSE: "§Y升级中§!"
 PXW_STATUS_CRISIS: "§R危机§!"
 PXW_FUND_BUTTON: "[ 拨款 ]"
 PXW_FUND_TT: "§Y左键§!：资助叛军。\n§Y右键§!：撤回支持。\n\n[!PXW_fund_button_click_enabled]\n--------------\n[!PXW_fund_button_click]"
 PXW_COST_HINT: "§g-25 政治点数 / +5 紧张度§!"
 PXW_TOGGLE_TT: "打开代理人战争指挥台"
 PXW_CLOSE_TT: "关闭"
 PXW_TT_NEED_PP: "拥有至少 §Y25§! 政治点数"
 PXW_TT_SUPPORT_CAP: "支持等级低于 §Y10§!"
 PXW_TT_COOLDOWN: "拨款渠道不在冷却中"
 PXW_TT_NOTHING_TO_WITHDRAW: "支持等级高于 §Y0§!"
 GFX_PXW_stamp_none: "GFX_PXW_stamp_none"
 GFX_PXW_stamp_crisis: "GFX_PXW_stamp_crisis"
```

### 6.8 `on_actions` 与 `events`

```paradox_script
# common/on_actions/PXW_on_actions.txt
on_actions = {
    on_startup = {
        effect = {
            every_country = { PXW_init = yes }
        }
    }
    on_weekly = {
        effect = {
            # 紧张度自然回落（全局只需执行一次：仅由一个国家执行）
            if = {
                limit = { tag = USA }
                subtract_from_variable = { global.PXW_tension = 1 }
                clamp_variable = { var = global.PXW_tension min = 0 max = 100 }
            }
        }
    }
}
```

```paradox_script
# events/PXW_events.txt
add_namespace = pxw

country_event = {                 # 隐藏分发事件：危机
    id = pxw.10
    hidden = yes
    immediate = {
        every_country = {
            limit = { check_variable = { PXW_support > 0 } }
            country_event = { id = pxw.11 }
        }
    }
}

country_event = {                 # 支持度满级叙事事件
    id = pxw.2
    title = pxw.2.t
    desc = pxw.2.d
    picture = GFX_report_event_generic_read_write
    is_triggered_only = yes
    option = { name = pxw.2.a add_stability = -0.02 }
}
```

> `on_weekly` 对每个国家都会触发——全局变量的“只做一次”必须加限定（示例用 `tag = USA`；正式项目建议用一个专门的“管理国”或 `on_startup` 中记录的 `global.PXW_manager` 变量）。

### 6.9 联动时序

```text
玩家左键 [FUND]
  → 引擎检查 PXW_fund_button_click_enabled（PXW_can_fund_insurgents）
  → effects: PXW_fund_insurgents
      ├─ -25 PP
      ├─ PXW_support +1（clamp 0..10）
      ├─ global.PXW_tension +5（clamp 0..100）
      ├─ 冷却 flag 7 天
      └─ PXW_post_change → (tension≥100 ? pxw.10) (support≥10 ? pxw.2) → PXW_gui_dirty +1
  → dirty 变化 → properties 重算：进度帧 t_bar、状态灯 t_lamp、印章 image
  → 本地化重读：[?global.PXW_tension|-0]、[GetPXWStatus]（≥75 时 “稳定/升级中” → §R危机§!）
```

---

## 7. 调试与报错排查指南

### 7.1 启动准备

- 启动参数加 **`-debug`**：启用调试模式，保存文件时自动热重载，并在屏幕角落显示“错误狗”（error dog）。
- 关键日志（`Documents/Paradox Interactive/Hearts of Iron IV/logs/`）：

| 日志 | 内容 | 用途 |
|---|---|---|
| `error.log` | 非致命错误 | **首查**：语法、缺失 sprite、无效变量 |
| `exceptions.log` | 致命错误（闪退）| CTD 排查 |
| `system_debug.log` | 界面错误 | GUI 相关 |
| `text.log` | 本地化键断言 | 缺键、乱码 |
| `setup.log` | 加载进度 | 定位加载时崩溃文件 |
| `game.log` | `log = "..."` 输出 | 变量追踪 |
| `scripted_ai.log` | `human_ai` 下的 AI 检查 | Scripted GUI AI 调试 |

### 7.2 常见问题排查表

| 症状 | 可能原因 | 排查 / 修复 |
|---|---|---|
| **面板完全不显示** | ① `window_name` 与 `.gui` `name` 不一致 ② 容器被嵌套在其他容器中 ③ 未设 `context_type` ④ `visible` 恒假 ⑤ 文件夹名写成 `scripted_gui`（应为复数 `scripted_guis`）| 临时 `visible = { always = yes }`；`error.log` 搜容器名 |
| **UI 错位 / 偏移** | `orientation` 继承自父容器；`origo` 与 `orientation` 混淆；百分比尺寸 | `guibounds` 查看边界；元素显式写 `orientation = UPPER_LEFT` |
| **面板被遮挡 / 在菜单之上** | `parent_window_token` 设置不当 | 需被菜单遮挡 → `top_bar`；需挂到某窗口 → `parent_window_name`（嵌套容器加 `_instance`）|
| **“红狗”/ 贴图丢失（不显示或显示错误）** | ① `spriteType` 名拼写 ② `texturefile` 路径错误（应相对游戏/mod 根目录）③ DDS 格式问题 ④ `.gfx` 未以 `spriteTypes = { }` 包裹 | `error.log` 搜 `GFX_`；`guibounds` 悬停可显示 sprite 名；`reload texture`；DDS 用 8.8.8.8 ARGB 或 DXT5、尺寸合理（单张 < ~16MB）|
| **多帧图显示整条 / 错帧** | 缺 `noOfFrames`；帧从 0 开始 | 补 `noOfFrames`；`frame` 从 1 起；`legacy_lazy_load = no` |
| **点击无反应** | ① 效果名非 `<element>_click` ② 上层元素（扫描线、透明 icon）拦截点击 ③ `_click_enabled` 为假 ④ 元素名重复 | 叠层设 `alwaystransparent = yes`；检查绘制顺序；tooltip 中放 `[!x_click_enabled]` |
| **右键条件无效** | 写了 `<element>_click_enabled`，其覆盖了 `_right_click_enabled` | 拆分逻辑，或在 `_click_enabled` 中同时兼容 |
| **按钮可点但条件不满足仍执行** | 只在 `_click_enabled` 校验 | effects 内 `if = { limit = { ... } }` 二次校验 |
| **变量读取为 0** | ① 作用域错：全局变量漏写 `global.` ② `context_type` 默认 scope 不是你以为的国家 ③ 变量从未初始化（未设即为 0）④ 变量名拼写 / 大小写 ⑤ 临时变量跨块使用 | `get_var` / `list_vars`；`log = "[?global.PXW_tension]"`；检查 `on_startup` 是否执行 |
| **数值不刷新** | `dirty` 变量未在效果中改变 | 每次数据变化 `add_to_variable = { PXW_gui_dirty = 1 }` |
| **文本显示原始键名** | 键不存在；yml 非 UTF-8 BOM；缩进/冒号错误；文件名不以 `_l_<language>.yml` 结尾 | `text.log`；`reload loc` |
| **`Could not find coloring for character`** | `§` 后跟非法字符 / 漏写 `§!` | 搜 `§"` 和 `§ `；每个颜色块用 `§!` 闭合 |
| **`[GetXXX]` 原样显示** | scripted loc 名错；该 UI 不支持动态本地化；`pdx_tooltip` 嵌 `$key$` | 改用 scripted loc 包一层 |
| **AI 不使用面板** | `ai_enabled` 为假；窗口对 AI 不可见；元素不可见；`ai_will_do` 为 0 | `human_ai` + `scripted_ai.log` |
| **游戏卡顿** | 大面板每 tick 重算 | 使用 `dirty`；昂贵逻辑缓存到 flag / 变量 |
| **使用 event target 后 GUI 失常** | Scripted GUI 中禁止 event target | 改用 `var:` 变量 scope |

### 7.3 控制台指令速查

| 指令 | 作用 |
|---|---|
| `reloadinterface` | 重载全部 `.gui` |
| `reload <file>.gui` | 重载单个界面文件（如 `reload PXW_panel.gui`）|
| `reload loc` / `reload localization` | 重载本地化 |
| `update_loc [key]` | 更新指定本地化键 |
| `reload texture` | 重载大部分贴图 |
| `reloadfx all` | 重载着色器效果 |
| `guibounds`（`gui`）| 显示 GUI 边界框，并显示悬停元素名与 sprite 名 |
| `tdebug` | 调试信息提示（州 ID、省份 ID、国家 tag）|
| `set_var <var> <value>` | 设置变量 |
| `get_var <var>` | 显示变量值 |
| `list_vars` | 列出所选 scope 的全部变量 |
| `set_country_flag <flag>` / `set_global_flag <flag>` | 直接打开面板 / 跳过前置 |
| `event <id> [TAG]` | 手动触发事件（如 `event pxw.10`）|
| `human_ai` | 让 AI 接管玩家国，输出 `scripted_ai.log` |
| `error` | 打开 `error.log` |
| `debug_textures` | 将贴图信息写入调试日志 |

> **关于 `var_show`**：该指令不在 HOI4 Wiki 的控制台指令列表中。查看变量请使用 `get_var` / `list_vars`，或在效果中写 `log = "PXW_tension = [?global.PXW_tension]"` 输出到 `game.log`。

---

## 8. 附录：团队编码规范清单

**命名**
- [ ] 所有对象使用模块前缀：`PXW_`（变量、flag、元素、GFX、loc 键、scripted effect/trigger）。
- [ ] GFX 统一 `GFX_<MODULE>_<what>`；元素名 = 本地化键语义一致。
- [ ] scripted loc 用 `Get<Module><What>` 帕斯卡命名，便于在 `.yml` 中辨识。

**架构**
- [ ] GUI 层不写数值：effects 只调用 `scripted_effects`，`_click_enabled` 只调用 `scripted_triggers`。
- [ ] 每个按钮：`clicksound` + `pdx_tooltip`（含 `[!x_click_enabled]` 与 `[!x_click]`）。
- [ ] 每次数据写入后统一走 `*_post_change` 收口（事件 + dirty）。
- [ ] 所有可累加变量写完立即 `clamp_variable`。
- [ ] 全局变量的周期性更新只由一个执行者完成。

**视觉**
- [ ] 8px 栅格；边框统一 `corneredTileSpriteType`。
- [ ] 色彩语义固定：`§G` 稳定 / `§Y` 警戒 / `§R` 危机 / `§g` 注释。
- [ ] 叠层装饰元素一律 `alwaystransparent = yes`。
- [ ] 数据字段一律等宽字体，右对齐数字（`format = right`）。

**性能与安全**
- [ ] 大面板必设 `dirty`。
- [ ] 不在 Scripted GUI 中使用 event target。
- [ ] 不需要 AI 的面板：`ai_enabled = { always = no }`。
- [ ] effects 内二次校验关键条件（联机安全）。

---

*本规范基于 HOI4 Wiki 现行词条整理；文中 “TNO 风格” 指设计模式与视觉语言，示例代码为原创实现，不包含 TNO 的任何原始资产或代码。*
