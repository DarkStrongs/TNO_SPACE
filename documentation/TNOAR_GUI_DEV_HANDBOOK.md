# TNOAR GUI 开发手册（整合版）

> **本文件由三部分整合而成**：
> 1. `TNO_UI_Framework_Guide.md`（**用户指定的重点参考规范**，v1.0，1105 行）— 引擎语法与排错的权威来源
> 2. TNOAR 现有代码的**实际写法**（修正了规范中若干与本项目不符之处）
> 3. 主 mod TNO 1.10.0b（`workshop/394360/2438003901`）的参考实现
>
> **规范的两个副本**（内容相同，后者随仓库走）：
> - `C:\Users\30408\Downloads\TNO_UI_Framework_Guide.md`
> - `<mod 根目录>/TNO_UI_Framework_Guide.md`
>
> **冲突时的优先级：TNOAR 实际代码 > 主 mod 惯例 > 通用规范。**
> 本文件只做「整合 + 修正」，**不做语法百科**。凡是本手册未覆盖的组件属性、变量运算、
> 报错排查，一律回查 `TNO_UI_Framework_Guide.md` 的第 3 章（GUI 核心组件接口速查）、
> 第 4 章（数据绑定）、第 7 章（调试与报错排查）。

---

## 0. 环境与依赖

| 项 | 值 |
|---|---|
| 游戏版本 | HOI4 `1.19.*` |
| 主 mod | The New Order: Last Days of Europe `1.10.0b` |
| 依赖 | `"The New Order: Last Days of Europe"` + `"The New Order: Last Days of Europe(CN.Ver)"` |
| TNOAR descriptor | `version="0.1.0-us-overhaul"`，`replace_path="gfx/loadingscreens"` |
| 主 mod `replace_path` | **包含** `common/scripted_guis`、`common/scripted_effects`、`common/scripted_triggers`、`common/scripted_localisation`、`common/decisions`、`common/decisions/categories` |

> ⚠ **关键约束**：主 mod 对上面这些目录用了 `replace_path`。TNOAR 是**覆盖式 submod**，新增 `scripted_effect` / `scripted_trigger` / `defined_text` 时**必须新建新名字**，不能指望"追加"到主 mod 的同名文件里。反过来，TNOAR 自己目录下的同名文件会整体替换主 mod 文件（如 `TNO_USA_categories.txt`），改它时要先把主 mod 原文件 diff 一遍。

---

## 1. ⚠ 对通用规范的修正（必读）

### 1.1 颜色码：规范里给的是原版值，TNO 实际是另一套

规范第 4.5 节写的 `§G(0,159,3)` / `§R(255,50,50)` 是**原版**配色。TNO 在 `interface/TNO_fonts.gfx` 里给字体重定义了 `textcolors`，**TNOAR 实际生效的是这套**：

| 码 | RGB | 语义 | TNOAR 实际用法 |
|---|---|---|---|
| `§F` | 178 201 194 | **默认正文色**（淡 CRT 青灰） | 长段说明文本 |
| `§D` | 89 199 194 | CRT 婴儿蓝 | 终端感数据 |
| `§M` | 35 206 255 | 霓虹亮蓝 | 高亮数值 |
| `§L` | 195 176 145 | 棕黄（人物简介默认色） | 人物 bios |
| `§W` | 255 255 255 | 白 | 标题 |
| `§G` | 133 234 142 | **绿：正面 / 可执行 / 低负荷** | 「强制休养」「医疗膳食」 |
| `§Y` / `§H` | 220 218 80 | **黄：警戒 / 数值高亮** | 指标名、阈值提示 |
| `§O` | 234 161 14 | 橙 | 升级中 |
| `§R` | 224 130 130 | **红：危机 / 不可执行 / 负面** | 「严重警报」「紧急兴奋剂」 |
| `§g` | 176 176 176 | 灰 | 注释、置灰 |
| `§e` | 146 0 0 | 暗红 | 强调负面 |
| `§n` | 60 180 60 | 暗绿 | 强调正面 |
| `§w` | 211 201 0 | 金 | 特殊强调 |
| `§C` | 253 100 144 | 热力粉 | 派系/特殊 |
| `§B` | 47 138 135 | 蓝 | — |

> ⚠ **上表只在「aldrich + vt323_72」这一族字体下成立。**
> `textcolors` 是**按 bitmapfont 逐个定义**的，换了字体同一串 `§X` 可能变色、甚至无效。
> 逐字体实测结果见 §1.2 的「色表族」一栏。颜色不出效果先确认字体。

### 1.2 字体：只用 TNO 主 mod 的字体（`interface/TNO_fonts.gfx`）

**唯一来源**：主 mod `interface/TNO_fonts.gfx`，共 **31 个 `bitmapfont`**，资源在 `gfx/fonts/*.fnt` + `*.tga`。
**TNOAR 自己不定义任何字体**（`grep -rn bitmapfont interface/` 无结果），全部继承自主 mod。

> ❌ **规范 §3.4 推荐的原版打字机字体不要用** —— 而且其中两个**在 TNO 里根本不存在**：
> `hoi_16typewriter`、`hoi_22typewriter` 查无此字体（TNO 的 `interface/core.gfx` 里只有
> `hoi4_typewriter16` / `hoi4_typewriter22`，命名顺序是反的）。照规范抄会直接渲染失败。

#### 主字体族（色表族 A：完整 TNO 色表，§1.1 表格适用）

以下 **13 个字体共享完全相同的 textcolors**，是 TNOAR 的日常工作集：
`aldrich_12/14/16/18/20/22/24/28/30/32/36/48_outline` + `vt323_72_WT_outline`

| 场景 | 字体 | TNOAR 实例 |
|---|---|---|
| **面板大标题** | `vt323_72_WT_outline` | 中国军阀面板标题 |
| 超大 / 次大标题 | `aldrich_36/32/30/28/24_outline` | — |
| 分栏小标题（18–21px 行） | `aldrich_18_outline` | Lee 的「全身扫描 / 生理指标 / 系统诊断」 |
| **正文 / 标签 / 数值（默认）** | **`aldrich_16_outline`** | 90% 的元素都用它 |
| 小号注释 | `aldrich_14_outline` | 血压、脉搏 |
| 极小号 | `aldrich_12_outline` | — |

#### 其他族（⚠ 色表不同，别混用）

| 字体 | 默认色 | 色表族 | 说明 / 风险 |
|---|---|---|---|
| `aldrich_24_outline_closing` | 0xffb2c9c2 | **B（独有）** | 国家结局画面专用。`§G={151,156,159}` 是灰、`§C` 是紫、`§M` 是深蓝 —— **语义与族 A 完全不同**，别拿它写正文 |
| `Bomb_16..36` | 0xffffffff | **C（缩减）** | 只有 W/b/G/R/Y/O/H/T/g 约 10 个色。`§F` `§D` `§M` `§L` **无效** |
| `tnr_53/39/26_numbers`（含 `_naa`） | 0xffffffff | **无 textcolors** | 纯数字排印。只有引擎原版色，默认白 |
| `vt323_32_outline` / `vt323_36_outline` | 0xffffffff | **无 textcolors** | ⚠ 与 `vt323_72_WT_outline` **不是同一族**，没有 TNO 色表 |
| `invisiblefont` | 0xffffffff | 无 textcolors | 隐藏文字 |
| `Blank` | 0xffffffff | 仅 W / b | 占位 |

#### 不用的字体（TNO 里有，TNOAR 不碰）

`interface/core.gfx` 里的原版族：`hoi_*` / `hoi4_typewriter*` / `Main_*` / `vic_*` / `garamond_*` / `Arial12` / `standard_*` / `cg_*` / `ToolTip_Font` 等。

> **新增元素时：从「主字体族」里按字号挑一个，别出这个集合。**
> 只有做结局画面才用 `aldrich_24_outline_closing`，做爆炸 / 倒计时特效才用 `Bomb_*`。

### 1.3 贴图格式：legacy DDS（非 DX10），PNG 不可靠

`interface/USA/Jan/*.gfx` 里的注释写得很明确：

> *Keep GUI textures in legacy DXT5 DDS. HOI4's Clausewitz GUI loader does not reliably create sprites from PNG files. These exports use the legacy DXT5 header (not DX10), so they are safe for the interface renderer.*

**实测更正（2026-10-08）**：把主 mod `gfx/interface` 下的 DDS 逐个解头后发现，
TNO 现役贴图**并不是 DXT5，而是未压缩 32 位 ARGB**：

```
Antarctica_Decision_GUI_AAB_Cover.dds  74x62
  dwFlags = 0x0100F      mipMapCount = 0
  pf.dwFlags = 0x41 (DDPF_ALPHAPIXELS | DDPF_RGB)   32 bpp
  caps = 0x1000 (DDSCAPS_TEXTURE)
  bytes = 128 + 74*62*4 = 18480   ✓
```

所以真正的硬约束只有两条：**非 DX10 头**、**非 PNG**。满足这两条的 DDS 都能加载，
未压缩 ARGB 反而最省事（占位图可以直接脚本生成，无需压缩器）。
DXT5 仍然可用，只是不是必需的。

- GUI 用图：**legacy DDS（未压缩 ARGB 或 DXT5 均可）；禁止 DX10 头、禁止 PNG**。
- 多帧图：`noOfFrames` + `legacy_lazy_load = no`，`frame` 从 1 起；
  `corneredTileSpriteType` **不支持** `noOfFrames`，需要多帧就改用普通 `spriteType`。
- `transparencecheck = yes` 用于带透明区的图。
- 事件图片可以用 PNG（`gfx/event_pictures/**` 下有大量 PNG），但 **interface sprite 不要**。
- 贴图放 `gfx/interface/USA/<President>/*.dds`（ president GUI）或 `gfx/interface/<模块>/*.dds`。

### 1.4 音效：TNOAR 目前复用原版，没有自建 soundeffect

规范第 3.5 节建议自建 `sound/*.asset`。**TNOAR 现状**是所有 GUI 都用原版音效名：

| 音效 | 用途 |
|---|---|
| `click_default` | 通用按钮点击（Lee 的区域按钮、急救按钮） |
| `click_ok` | 确认型按钮（Lee 的休养 / 膳食） |
| `click_close` | 关闭窗口 |
| `decisions_ui_button` | 决议面板按钮（Jan 的 `book_pull`、军阀入口按钮） |

> 新增按钮按上表选一个即可，**不要凭空写规范里的 `pxw_ui_click` 这类名字**（写错不报红狗，只会静音）。

---

## 2. TNOAR 的两套 GUI 架构模式

规范只给了「顶栏开关 + flag」一种模式。TNOAR 实际有**两套**，新增功能时先选对。

### 模式 A：`decision_category`（总统机制面板）— 最常用

用于：**某个总统专属的机制面板**，挂在决议类别下。

- `context_type = decision_category`
- **不写** `parent_window_token` / `parent_window_name`
- 由决议类别挂载，**不需要**自己写开关 flag / 关闭按钮
- 只有在用了 `dynamic_lists` 时才需要 `dirty`

**接线三处**（以 Lee 为例）：

```paradox_script
# ① common/decisions/categories/TNO_USA_categories.txt
TNOAR_USA_Lee_Physical_Condition_category = {
    icon = GFX_...
    priority = 10
    scripted_gui = TNOAR_USA_Lee_Physical_Condition     # ← 绑定
}

# ② common/decisions/AR_USA_Lee_decisons.txt   （空壳类别，仅用于让类别存在）
TNOAR_USA_Lee_Physical_Condition_category = { }

# ③ common/scripted_guis/TNOAR_USA_*.txt
scripted_gui = {
    TNOAR_USA_Lee_Physical_Condition = {
        context_type = decision_category
        window_name = "TNOAR_USA_Lee_Physical_Condition_container"
        visible = { has_country_leader = { character = USA_Lee_D_Young ruling_only = yes } }
        ...
    }
}
```

现有采用者：`TNO_USA_categories.txt` 里 20+ 个总统面板全部如此（Nixon / Wallace / Stevenson / Reagan / Rockefeller / JFK / RFK / Connally / Hart / Humphrey / Goldwater / Chisholm / Reuther / Romney / Schlafly / Yorty / Burton / Jan / Lee）。

### 模式 B：`player_context` + `top_bar`（独立可开关窗口）

用于：**不属于某个总统的全局面板**（如中国军阀地图）。

```paradox_script
# 入口按钮容器
TNOAR_CHI_WARLORD_entry_gui = {
    context_type = player_context
    parent_window_token = top_bar
    window_name = "TNOAR_CHI_WARLORD_entry_window"
    visible = { TNOAR_CHI_WARLORD_player_can_use = yes }
    triggers = { TNOAR_CHI_WARLORD_entry_button_click_enabled = { TNOAR_CHI_WARLORD_player_can_use = yes } }
    effects  = { TNOAR_CHI_WARLORD_entry_button_click = { TNOAR_CHI_WARLORD_toggle_gui = yes } }
}

# 主窗口
TNOAR_CHI_WARLORD_main_gui = {
    context_type = player_context
    parent_window_token = top_bar
    window_name = "TNOAR_CHI_WARLORD_main_window"
    dirty = TNOAR_CHI_WARLORD_dirty
    visible = {
        TNOAR_CHI_WARLORD_player_can_use = yes
        has_country_flag = TNOAR_CHI_WARLORD_window_open
        NOT = { has_country_flag = WI_GUI_map_open }
    }
    ...
}
```

> 主 mod 的 `Antarctica_GUI_Open` 也是这个套路，但它用 `parent_window_token = politics_tab`（挂在政治页签下）。TNOAR 用 `top_bar`。

---

## 3. 文件树与命名规范（TNOAR 定制版）

### 3.1 USA 总统功能标准布局

```text
TNOAR/
├── common/
│   ├── decisions/categories/TNO_USA_categories.txt   # 追加类别 + scripted_gui 绑定
│   ├── decisions/AR_USA_<President>_decisons.txt      # 空壳类别（可选）
│   ├── scripted_guis/TNOAR_USA_<President>_<Feature>.txt
│   ├── scripted_effects/TNOAR_USA_<President>_<Feature>_effects.txt
│   ├── scripted_triggers/（通常并入 effects 或 TNO_US_scripted_triggers.txt）
│   ├── scripted_localisation/TNOAR_USA_<President>_<Feature>_scripted_loc.txt
│   └── on_actions/TNOAR_USA_<President>_<Feature>_on_actions.txt   # 初始化 + 周期 tick
├── interface/USA/<President>/
│   ├── TNOAR_USA_<President>_<Feature>.gfx
│   └── TNOAR_USA_<President>_<Feature>.gui
├── gfx/interface/USA/USA_president_GUIs/<President>/*.dds
└── localisation/
    ├── english/TNOAR_USA_<President>_<Feature>_l_english.yml      # ⚠ 见 3.3
    └── simp_chinese/TNOAR_USA_<President>_<Feature>_l_simp_chinese.yml
```

### 3.2 前缀约定

| 前缀 | 含义 | 示例 |
|---|---|---|
| `TNOAR_USA_` | AR 自研的美国内容（新） | `TNOAR_USA_Lee_Physical_Condition`、`TNOAR_USA_Jan_Library` |
| `TNOAR_CHI_` | AR 自研的中国内容 | `TNOAR_CHI_WARLORD_*` |
| `AR_` | 早期 / 跨总统共享的 AR 内容 | `AR_USA_health`、`AR_USA_max_health`、`AR_monthly_health_change` |
| `TNO_USA_` / `TNO_US_` | 从主 mod 带回/改造的美国内容 | `TNO_USA_Budget`、`TNO_US_Voting` |

> **新增内容一律用 `TNOAR_USA_<President>_<Feature>_`，不要新造前缀。**
> 变量、flag、元素名、GFX 名、loc 键、scripted effect/trigger **全部共享同一前缀串**。

### 3.3 ⚠ 本地化现状与硬要求

- `localisation/simp_chinese/`：72 个文件（完善）
- `localisation/english/`：只有 1 个（`TNOAR_china_warlord_l_english.yml`）
- **UTF-8 with BOM 已验证**：抽样两个文件首字节均为 `EF BB BF` ✓

> **规范**：新增功能**必须同时提供** `english` 与 `simp_chinese` 两份，且都带 BOM。
> 现有英文缺失是技术债，新增功能不要再欠。
> 文件名格式：`<前缀>_l_english.yml` / `<前缀>_l_simp_chinese.yml`。
> 键名前**留一个空格**（项目惯例，见 `USA_CUSTOM_PRESIDENT_GUIDE_zh.md`）。

---

## 4. 标准实现模板（模式 A：总统机制面板）

下面是可以照抄的骨架，取自 Lee / Jan 的实际代码。

### 4.1 `.gui` —— 双层容器结构

```paradox_script
guiTypes = {
    containerWindowType = {
        name = "TNOAR_USA_<P>_<F>_container"       # ← scripted_gui.window_name 绑定这一层
        position = { x = 0 y = 0 }
        size = { width = 482 height = 500 }         # 决议面板常见宽度 482
        clipping = no

        containerWindowType = {                     # 内层用于整体偏移微调
            name = "TNOAR_USA_<P>_<F>_offset"
            position = { x = 11 y = -10 }
            size = { width = 482 height = 500 }
            clipping = no

            iconType = {
                name = "health_background"
                position = { x = 0 y = 0 }
                spriteType = "GFX_TNOAR_USA_<P>_<F>_background"
                alwaysTransparent = yes             # ← 装饰层必须透明，否则吃掉点击
            }

            instantTextBoxType = {
                name = "indicators_title"
                position = { x = 163 y = 41 }
                font = "aldrich_18_outline"
                text = TNOAR_USA_<P>_indicators_title   # loc 键不加引号也可以
                maxWidth = 152
                maxHeight = 21
                format = center
            }

            # 数值行：标签左对齐 + 数值右对齐（固定 x 偏移）
            instantTextBoxType = {
                name = "cardio_label"
                position = { x = 165 y = 117 }
                font = "aldrich_16_outline"
                text = TNOAR_USA_<P>_cardio_label
                maxWidth = 88 maxHeight = 20 format = left
            }
            instantTextBoxType = {
                name = "cardio_value"
                position = { x = 253 y = 117 }
                font = "aldrich_16_outline"
                text = TNOAR_USA_<P>_cardio_value
                maxWidth = 60 maxHeight = 20 format = right
            }
            iconType = {
                name = "cardio_bar"                 # ← properties 驱动 frame
                position = { x = 164 y = 141 }
                spriteType = "GFX_TNOAR_USA_<P>_<F>_bar_risk"
                pdx_tooltip = TNOAR_USA_<P>_cardio_tt
            }

            buttonType = {
                name = "prescribe_rest"
                position = { x = 5 y = 460 }
                quadTextureSprite = "GFX_sort_button_140x29"   # 复用原版按钮底
                buttonText = TNOAR_USA_<P>_prescribe_rest
                buttonFont = "aldrich_16_outline"
                pdx_tooltip = TNOAR_USA_<P>_prescribe_rest_tt
                clicksound = click_ok
            }
        }
    }
}
```

**TNOAR 的 `.gui` 铁律**

1. `size = { width = .. height = .. }` 只用于 `containerWindowType`；`buttonType` 要写 `size = { x = .. y = .. }`；`iconType` 不写 size（从 sprite 取）。
2. 装饰层（背景、选中高亮、扫描线）一律 `alwaysTransparent = yes`。
3. **唯一的例外**：要**阻挡**点击的遮罩层（Lee 的 `block_overlay`）必须 `alwaystransparent = no`，这样物理吃掉点击。
4. 绘制顺序 = 定义顺序，后定义者在上。
5. `pdx_tooltip` 值可加引号也可不加，TNOAR 两种都在用，保持一致即可。

### 4.2 `.gfx`

```paradox_script
spriteTypes = {
    spriteType = {
        name = "GFX_TNOAR_USA_<P>_<F>_background"
        textureFile = "gfx/interface/USA/USA_president_GUIs/<P>/GFX_TNOAR_USA_<P>_<F>_background.dds"
    }
    # 带透明区的图
    spriteType = {
        name = "GFX_TNOAR_USA_<P>_<F>_bar_risk"
        textureFile = "gfx/interface/USA/USA_president_GUIs/<P>/GFX_TNOAR_USA_<P>_<F>_bar_risk.dds"
        transparencecheck = yes
        noOfFrames = 21          # 帧式进度条：0%,5%,...,100%
        legacy_lazy_load = no
    }
}
```

- 多帧图是**横向等宽条带**，`frame` 从 **1** 起计。
- `noOfFrames` 与 `legacy_lazy_load = no` 必须成对出现，否则显示整条。

### 4.3 `scripted_gui`

```paradox_script
scripted_gui = {
    TNOAR_USA_<P>_<F> = {
        context_type = decision_category
        window_name = "TNOAR_USA_<P>_<F>_container"

        visible = {
            has_country_leader = { character = USA_<President> ruling_only = yes }
        }

        # —— 逻辑只调用 scripted_effect / scripted_trigger ——
        effects = {
            prescribe_rest_click = { TNOAR_USA_<P>_prescribe_rest = yes }
            zone_cardiovascular_click = { set_variable = { TNOAR_USA_<P>_selected_system = 2 } }
        }

        triggers = {
            prescribe_rest_click_enabled = {
                has_political_power > 34.99
                NOT = { check_variable = { TNOAR_USA_<P>_rest_cooldown > 0 } }
            }
            # 选中态高亮：变量驱动元素显隐
            zone_cardiovascular_selected_visible = {
                check_variable = { TNOAR_USA_<P>_selected_system = 2 }
            }
            # 遮罩层
            block_overlay_visible = { has_country_flag = TNOAR_USA_<P>_gui_blocked }
        }

        properties = {
            cardio_bar  = { frame = TNOAR_USA_<P>_cardio_load }
            vitality_bar= { frame = TNOAR_USA_<P>_health_percent }
            organ_diagram = { frame = TNOAR_USA_<P>_selected_system }
        }
    }
}
```

> ⚠ **TNOAR 现状提醒**：Lee 的 `effects` 里直接写了 `add_political_power` / `add_to_variable`，**违反了"GUI 层不写数值"的规范**。新增功能请走 `scripted_effects`（见 4.4），这是规范第 8 章明确要求项。

### 4.4 `scripted_effects` —— 逻辑与重算收口

```paradox_script
# ① 初始化（幂等）
TNOAR_USA_<P>_initialize_<F> = {
    if = {
        limit = { NOT = { has_country_flag = TNOAR_USA_<P>_<F>_initialized } }
        TNOAR_USA_<P>_reset_<F> = yes
    }
}

TNOAR_USA_<P>_reset_<F> = {
    set_variable = { TNOAR_USA_<P>_selected_system = 1 }
    set_variable = { TNOAR_USA_<P>_cardio_load = 46 }
    set_variable = { TNOAR_USA_<P>_rest_cooldown = 0 }
    set_country_flag = TNOAR_USA_<P>_<F>_initialized
    TNOAR_USA_<P>_recalculate_<F> = yes
}

# ② 玩家操作
TNOAR_USA_<P>_prescribe_rest = {
    if = {
        limit = { TNOAR_USA_<P>_can_prescribe_rest = yes }    # ← 二次校验（联机安全）
        add_political_power = -35
        add_to_variable = { TNOAR_USA_<P>_cardio_load = -12 }
        set_variable = { TNOAR_USA_<P>_rest_cooldown = 45 }
        TNOAR_USA_<P>_recalculate_<F> = yes
    }
}

# ③ 统一重算收口（所有数值写完之后必须调用）
TNOAR_USA_<P>_recalculate_<F> = {
    # clamp 每一个可累加变量
    clamp_variable = { var = TNOAR_USA_<P>_cardio_load min = 0 max = 100 }
    # 派生显示值
    set_variable = { TNOAR_USA_<P>_health_percent = AR_USA_health }
    divide_variable = { TNOAR_USA_<P>_health_percent = AR_USA_max_health }
    multiply_variable = { TNOAR_USA_<P>_health_percent = 100 }
    # 帧索引 clamp 到合法范围
    # dirty 刷新（仅当用了 dynamic_lists）
    add_to_variable = { TNOAR_USA_<P>_dirty = 1 }
}
```

> **TNOAR 的 clamp 惯例**：Lee 用 `if / else_if` 手写边界检查（`< 0 → 0`，`> 100 → 100`），而规范推荐 `clamp_variable`。两者都行，**新代码优先 `clamp_variable`**（更短、不易漏）。

### 4.5 `scripted_localisation`

```paradox_script
defined_text = {
    name = TNOAR_USA_<P>_system_name          # 命名用下划线式，非规范的 GetXxx 帕斯卡
    text = {
        trigger = { check_variable = { TNOAR_USA_<P>_selected_system = 1 } }
        localization_key = TNOAR_USA_<P>_system_overview
    }
    text = { localization_key = TNOAR_USA_<P>_system_cardiovascular }   # 兜底
}
```

> **TNOAR 命名**：`TNOAR_USA_Lee_system_name`、`TNOAR_USA_Lee_condition_status` —— 下划线式，**不用**规范建议的 `Get<Module><What>`。跟随项目现状。

### 4.6 `on_actions` —— 接入游戏循环

```paradox_script
on_actions = {
    on_startup = { effect = { USA = { TNOAR_USA_<P>_initialize_<F> = yes } } }
    on_weekly  = { effect = { USA = { TNOAR_USA_<P>_monthly_tick = yes } } }
}
```

> ⚠ 见 `documentation/USA_OVERHAUL_PORT.md`：`TNO_on_startup_actions.txt` 只改了 USA 初始化块；`ZZZZ_TNOAR_USA_overhaul_bridge.txt` 用 **ZZZZ 前缀保证加载顺序最后**。新增 on_action 若与 USA 经济圈初始化冲突，优先挂到后者或新建文件，**不要改 `TNO_OFN_on_actions.txt`**。

---

## 5. 进阶模式：动态列表（`dynamic_lists`）

Jan 图书馆是 TNOAR 的标准范例——**所有槽位重叠在 gridbox 原点，用变量数组给绝对坐标**：

```paradox_script
# .gui
gridboxtype = {
    name = "TNOAR_Jan_books"
    position = { x = 0 y = 0 }
    size = { width = 0 height = 0 }
    slotsize = { width = 0 height = 0 }
    add_horizontal = no
}
containerWindowType = {
    name = "TNOAR_Jan_book"          # entry_container
    size = { width = 0 height = 0 }
    position = { x = 0 y = 0 }
    buttonType = {
        name = "book_pull"
        spriteType = "empty"          # 透明占位 sprite
        position = { x = 0 y = 0 }
        size = { x = 182 y = 317 }    # 按钮要显式给尺寸 = 点击热区
        clicksound = decisions_ui_button
    }
    icontype = { name = "book" spriteType = "empty" alwaystransparent = yes }
}

# scripted_gui
dynamic_lists = {
    TNOAR_Jan_books = {
        array = USA.TNOAR_USA_Jan_Library_Books   # ⚠ decision_category 下必须显式写国家 scope
        value = book_slot
        index = idx
        entry_container = TNOAR_Jan_book
    }
}
properties = {
    book_pull = { x = TNOAR_USA_Jan_X^idx  y = TNOAR_USA_Jan_Y^idx  image = "GFX_USA_Jan_Book_4" }
    book      = { x = TNOAR_USA_Jan_X^idx  y = TNOAR_USA_Jan_Y^idx
                  image = "GFX_USA_Jan_Book_[?TNOAR_USA_Jan_Art^idx]" }   # 动态 GFX 名
}
```

**要点**

- `array = <TAG>.<array_var>`：`decision_category` 上下文**必须**显式写国家 scope，否则数组取不到。
- `TNOAR_USA_Jan_X^idx` / `Y^idx` 是**变量数组**，`idx` 来自 `index =`。
- `image = "...[?array^idx]"` 可以做**动态贴图名**——这是 TNOAR 的招牌技巧（Burton 香烟盒、军阀地图同款）。
- 用了 `dynamic_lists` **必须设 `dirty`**，并在点击 effect 里 `add_to_variable = { <prefix>_dirty = 1 }` 强制刷新。

主 mod 更进一步：`Antarctica_GUI_Main_Zoom` 用 `entry_container = "[get_Antarctica_GUI_Main_Zoom_Array]"` —— 容器名本身由 scripted loc 动态返回。需要时参考。

---

## 6. 主 mod 可借鉴的其他技巧

| 位置 | 技巧 |
|---|---|
| `common/scripted_guis/TNO_Antarctica_GUI.txt` | `parent_window_name = <window>` 把子窗口挂到已有窗口下 |
| 同上 | `entry_container` 用 scripted loc 动态返回 |
| `interface/TNO_fonts.gfx` | 99 个 `bitmapfont` + 自定义 `textcolors`，全套 TNO 视觉语言 |
| `interface/TNO_CHI_GUI.gui` 等 | 各国 GUI 的布局惯例（中国 / 广东 / 冷战 / 国家信息屏） |

---

## 7. 调试速查（HOI4 1.19 实测可用）

| 指令 | 作用 |
|---|---|
| `-debug` 启动参数 | 热重载 + 显示错误狗 |
| `reload <file>.gui` / `reloadinterface` | 重载界面 |
| `reload loc` | 重载本地化 |
| `reload texture` / `reloadfx all` | 重载贴图 / 着色器 |
| `guibounds` | 显示边界框 + 悬停元素名与 sprite 名 |
| `set_var <var> <value>` / `get_var <var>` / `list_vars` | 变量调试 |
| `set_country_flag <flag>` | 跳过前置直接显示面板 |
| `tdebug` | 州/省/TAG 信息 |
| `human_ai` | AI 接管，输出 `scripted_ai.log` |

**日志文件**（`Documents/Paradox Interactive/Hearts of Iron IV/logs/`）

| 文件 | 用途 |
|---|---|
| `error.log` | **首查**：语法、缺 sprite、无效变量 |
| `exceptions.log` | CTD |
| `system_debug.log` | 界面错误 |
| `text.log` | 本地化缺键 / 乱码 |
| `game.log` | `log = "..."` 输出 |

**高频坑（按 TNOAR 经验排序）**

1. **面板不显示** → `window_name` 与 `.gui` 的 `name` 不一致 / 类别里 `scripted_gui =` 没写 / `visible` 恒假。临时改 `visible = { always = yes }` 二分。
2. **点击无反应** → 上层装饰层没 `alwaysTransparent`；或 `block_overlay` 忘了关。
3. **变量读成 0** → 未初始化（未设即 0）；`decision_category` 下 scope 不是你以为的国家（用 `USA.xxx` 显式写）。
4. **多帧图显示整条** → 缺 `noOfFrames` 或 `frame` 从 0 起。
5. **文本显示原始键名** → yml 非 UTF-8 BOM / 键名前没空格 / 文件名不以 `_l_<lang>.yml` 结尾。
6. **模式 B 挂载**（TNO 主 mod `TNO_Country_Info_Screen` 权威先例）：opener 的 scripted_gui 写 `parent_window_token = top_bar`；**主窗口不写任何 parent**（默认挂屏幕层），用 country_flag 控制 `visible`；`.gui` 主窗口 `orientation = center` + 负坐标 `{-w/2, -h/2}` 居中。topbar 容器要用 `size = { width = 100%% height = 100%% }`（`%%` 转义）。
7. **⚠ `check_variable` 禁用 `>=` / `<=`**（2026-10-08 error.log 实锤）：简写只支持 `=` `>` `<`。写 `check_variable = { X >= 75 }` 会让解析器报 `unexpected token ... ( 75 )` 并**连锁 desync 整个文件**——后面的所有触发器报 `Invalid trigger`、`properties` 块整体报废、DSL 文件整体失效（表现为：页签全显示、横幅常显、`[Get...]` 文本全空白）。"≥" 一律写 `check_variable = { var = X value = 75 compare = greater_than_or_equals }`（TNO 主 mod 0 处 `>=`、491 处 compare 形式；`compare =` 可用值：`equals` / `not_equals` / `greater_than` / `less_than` / `greater_than_or_equals` / `less_than_or_equals`）。**一个 `>=` 毁掉的不只是这一行，是整个文件。**
8. **`properties` 只引用持久变量/数组**：帧数值由 scripted_effects 预算好（如 `DS_refresh_frames`），`properties` 里写 `frame = 变量` 或 `frame = 数组^索引`（先例：`frame = TNO_BoP_Tabs_Frames^Tab_i`、`frame = Antarctica_GUI_AAO_PERT_Event_Frames^0`）。不要在 `_visible` 触发器里 set 临时变量给 properties 用——主 mod 无此先例。
9. **带 `animation` 的 sprite 必须 `legacy_lazy_load = no`**，否则 error.log 报 `animation are not supported in legacy lazy load`（先例：`TNO_*_goals_shine.gfx`）。

---

## 8. 新增功能自检清单（交付前逐项打勾）

**接线**
- [ ] `decisions/categories/TNO_USA_categories.txt` 已加类别并 `scripted_gui = <id>`
- [ ] `scripted_gui.window_name` == `.gui` 里**外层独立容器**的 `name`
- [ ] `visible` 用 `has_country_leader = { character = <token> ruling_only = yes }` 限定总统
- [ ] 用了 `dynamic_lists` → 已设 `dirty` 且 effect 里 +1

**命名**
- [ ] 全部对象统一 `TNOAR_USA_<President>_<Feature>_` 前缀
- [ ] GFX 名 `GFX_TNOAR_USA_<P>_<F>_<what>`
- [ ] 变量/flag/元素/loc 键不与其他总统冲突（`grep -r` 确认）

**逻辑**
- [ ] `effects` 只调 `scripted_effects`；`_click_enabled` 只调 `scripted_triggers`
- [ ] **全项目无 `check_variable ... >=` / `<=`**（`grep -rn "check_variable[^}]*>=" common/` 应为空）；"≥" 写 `compare = greater_than_or_equals`
- [ ] `properties` 里的 `frame`/`image` 只引用持久变量/数组，帧数值由 scripted_effects 预算
- [ ] effect 内 `if = { limit = { <scripted_trigger> = yes } }` 二次校验
- [ ] 每个可累加变量写完立即 `clamp_variable`
- [ ] 所有数值写入后统一走 `TNOAR_USA_<P>_recalculate_<F>`
- [ ] `on_actions` 初始化幂等（用 flag 判重）

**视觉**
- [ ] 字体只用主字体族（`aldrich_*_outline` / `vt323_72_WT_outline`），见 §1.2
- [ ] 没用 `vt323_32/36_outline`、`tnr_*`、`Bomb_*`、`aldrich_24_outline_closing`（这些没有完整 TNO 色表）
- [ ] 颜色只用第 1.1 节的 TNO 色码，每个 `§X` 有 `§!` 闭合
- [ ] 贴图是 legacy DDS（非 DX10 头、非 PNG），多帧图有 `noOfFrames` + `legacy_lazy_load = no`
- [ ] `.gui` 里调用 `defined_text` 写的是 `text = "[GetXxx]"`，不是裸键名
- [ ] 装饰层 `alwaysTransparent = yes`；只有遮罩层是 `no`
- [ ] 按钮有 `clicksound` + `pdx_tooltip`

**本地化**
- [ ] `english` 与 `simp_chinese` **两份都有**
- [ ] 都是 UTF-8 **with BOM**，键名前一个空格
- [ ] 文件名以 `_l_english.yml` / `_l_simp_chinese.yml` 结尾
- [ ] tooltip 用 `\n` 换行，长说明用 `§F` 正文色

---

## 9. 参考实现索引（照抄优先选这些）

| 想做什么 | 看哪个文件 |
|---|---|
| 总统机制面板（完整、最新） | `common/scripted_guis/TNOAR_USA_Lee_Physical_Condition.txt` + `interface/USA/Lee/*.gui` |
| 动态列表 / 变量数组定位 | `common/scripted_guis/TNOAR_USA_Jan_Library.txt` + `interface/USA/Jan/*.gui` |
| **独立窗口 + 顶栏开关（权威，照抄这个）** | **主 mod** `common/scripted_guis/TNO_Country_Info_Screen.txt` + `interface/TNO_Country_Info_Screen.gui`（opener 挂 top_bar、主窗口挂屏幕层、country_flag 开关、`orientation = center` 负坐标居中） |
| 顶栏图标 scripted_gui 最小样例 | 主 mod `common/scripted_guis/TNO_Antarctica_GUI_topbar.txt` |
| 页签帧数组 / dynamic_lists 按数组切换 | 主 mod `common/scripted_guis/TNO_BoP_Tabs.txt` |
| 容器级 `_visible` 显隐 | 主 mod `common/scripted_guis/TNO_fopo_gui.txt`（`info_tab_visible`） |
| 复杂布局、大数据量面板 | `interface/USA/TNO_USA_NationalOverview.gui`、`TNO_USA_Budget.gui` |
| **引擎语法百科（权威）** | `TNO_UI_Framework_Guide.md` — 第 3 章组件速查 / 第 4 章数据绑定 / 第 7 章排错 |
| 自定义总统接入流程 | `documentation/USA_CUSTOM_PRESIDENT_GUIDE_zh.md` |

> ⚠ **不要参考** `TNOAR_china_warlord_gui.txt` / `TNOAR_china_warlord.gui`（2026-10-08 用户确认其实现本身有错，仅作反面教材）。
| USA 覆盖层边界 | `documentation/USA_OVERHAUL_PORT.md` |
| TNO 全部字体与完整色码（**字体唯一来源**） | 主 mod `interface/TNO_fonts.gfx`（31 个 bitmapfont）；资源 `gfx/fonts/*.fnt`+`*.tga` |
| 原版字体（**不用**，仅备查） | 主 mod `interface/core.gfx` |

## 10. 股票事件信号接口（第 28 轮，给事件 / 国策 / 决议调用）

让某只标的在未来 N 个月走出确定趋势。实现：市场主机 USA 挂每月漂移
`DS_sig_d^s`（剩余月数 `DS_sig_len^s`），`DS_stk_monthly` 生成收盘价时
在随机振幅与 AI 冲击**之后**叠乘 → 趋势保证兑现、不被噪声吞掉。

### 10.1 调用方式（⚠ 整块必须在 `USA = { }` scope 内）

```paradox
USA = {
    set_variable = { DS_sig_stk = 2 }    # 标的 0..5：0 RWK / 1 SO / 2 MTS / 3 SMR / 4 FIA / 5 ICI
    set_variable = { DS_sig_len = 4 }    # 未来 4 个月（可省略，缺省 3）
    DS_sig_up_big = yes                  # 大幅上涨
}
```

六个速记 effect：`DS_sig_up_small / DS_sig_up_big / DS_sig_up_huge`、
`DS_sig_down_small / DS_sig_down_big / DS_sig_down_huge`。
核心入口 `DS_stk_signal`（dir=1涨/2跌，mag=1小幅/2大幅/3巨幅）一般不直接调。

### 10.2 幅度口径

累计涨跌幅均摊到每月：小幅 **±8%** / 大幅 **±20%** / 巨幅 **±40%**。
调档只改 `DS_stk_signal` 里的三处字面量。重复调用 = 覆盖该标的旧信号（不叠加）。

⭐ **信号结束后会自动接一段反向的「回撤期」**（3 个月，幅度 = 原幅度 × 0.5），
涨过会回落、跌过会回升 —— 见 **§12.4**。写事件文案时不必额外说明，
`DS_SIG_DESC_<N>` 只描述主信号段。

### 10.3 事件文案（第 35 轮：改成【按标的下标】渲染）

信号缓存 `DS_sig_last_dir / _mag / _len` 是**数组，下标 = 标的号 0..5**
（第 35 轮前是单槽标量 —— 同一次 option 里连打多只标的会互相覆盖，
文案只显示最后一只，2026-10-12 用户截图指出后改掉）。

显示链路三步：

1. `DS_stk_signal` 写入 USA 上的 `DS_sig_last_dir^stk / _mag^stk / _len^stk`；
2. **`DS_sig_view_sync`** 把 USA 的三条数组镜像成本地 `DS_sig_vdir / _vmag / _vlen`
   （跨 scope 数组读只有「先转 temp 下标」一种可靠写法，见 `DS_price_prefetch`）；
3. loc / scripted_loc 一律用**无 scope 前缀 + 字面下标**读：
   `[?DS_sig_vlen^3|0]`、`check_variable = { DS_sig_vmag^3 = 1 }`。
   ⚠ **带 scope 前缀 + 数组下标（`[?USA.X^3|0]`）全库 0 处先例，不要写** ——
   这是要镜像的根本原因（无前缀写法主 mod 有先例：`loc` 的
   `[?Antarctica_GUI_AAO_PERT_Event_Time_To^1|0]`、`trigger` 的 `AAC_Skill_Array^0`）。

事件里按标的挑对应下标那一条，一次打多只就写多行：

```paradox
option = {
    name = ds.26.a
    DS_we_apply_6 = yes
    custom_effect_tooltip = DS_SIG_DESC_0      # 六只全列
    custom_effect_tooltip = DS_SIG_DESC_1
    # …… 一直到 _5
}
```

七个世界事件的对照：`ds.21→0`、`ds.22→5`、`ds.23→4`、`ds.24→2`、`ds.25→3`、
`ds.26→0..5`、`ds.27→0`。

⚠ 显示前**必须先跑过 `DS_sig_view_sync`**（挂在 `DS_wnews_prep_at` 与每个
`DS_we_apply_<n>` 末尾，所以在 `immediate` 里调用 apply 才有正确文案）。

### 10.4 实现索引

| 部件 | 位置 |
|---|---|
| 数组 init（`DS_sig_last_*` 撑 6 槽，旗 `DS_sig_v3`） | `DS_sig_last_init`（`DS_stk_signal` 与 `DS_ai_init` 各调一次） |
| 显示镜像 | `DS_sig_view_sync`（USA 三条数组 → 本地 `DS_sig_vdir/_vmag/_vlen`） |
| 收盘价叠乘 + 相位推进 | `DS_stk_monthly` 内 `DS_sig_len^sa > 0.5` 分支（见 §12.4） |
| 核心 + 速记 + 老档迁移旗 `DS_sig_v1` / `DS_sig_v2` | `DS_stk_signal` 及其后 6 个 wrapper |
| 文案 | scripted_loc `GetDSSigName0..5 / GetDSSignalMove0..5`，yml 键 `DS_SIG_DESC_0..5`、`DS_SIG_UP_*` / `DS_SIG_DOWN_*` |

## 11. 延时新闻接口（第 31 轮：行动 5 → 30 天后弹 `ds.11`）

「玩家点了某个行动 → N 天后弹一条新闻，标题与正文全部由动态本地化拼装」的
标准模板。当前只挂在行动 5（行政托市）上，要挂别的行动照抄三步即可。

### 11.1 三步走

| 步 | effect / 事件 | 作用 |
|---|---|---|
| ① 上膛 | `DS_news_arm`（在行动的 `hidden_effect` 里调） | 缓存标的 → 随机定口径 → 置倒计时 `DS_news_cd = 30` |
| ② 倒计时 | `DS_news_tick`（挂在 `DS_me_daily`，玩家腿） | 每天 −1，共 30 天，递减后归零 → `news_event = { id = ds.11 }` |
| ③ 备数 | `DS_news_prep`（被 `ds.11` 的 `immediate` 调） | 把文案要用的数算完写进国家变量 |

### 11.2 两条不能踩的红线

**① 标的一定要缓存**。30 天里玩家可以切到别的票，`DS_stk_sel`（当前选中项）会变。
新闻必须报【当时被托的那一只】→ 一律读 `DS_news_stk`，用专用的
`GetDSNewsStockName`（**不要**用 `GetDSStockName`，那个读 `DS_stk_sel`）。

**② 数据必须算在 `immediate`**。事件文本（title / desc / option name）**先渲染**、
option effect **后执行** → 写在 option 里的赋值玩家看不到。

### 11.3 动态本地化的两层拼装

```paradox
# ① 模板层：title / desc 不写死键名，直接挂 defined_text
news_event = {
    id = ds.11
    immediate = { DS_news_prep = yes }     # ← 必须先跑
    title = [GetDSNewsTitle]               # → DS_NEWS_T_[?DS_news_i]
    desc  = [GetDSNewsDesc]                # → DS_NEWS_D_[?DS_news_i]
    picture = GFX_news_event_generic_industry          # 新闻图，见下方 ⚠
    is_triggered_only = yes
    major = yes
    option = { name = DS_NEWS_OK }
}
```
先例：主 mod `TNO_USA_sen_bill.txt` 的 `title = [GetBillStatusTitle]`。

> ✅ **同一套拼装也用在 GUI 文本框上**（第 33 轮）：顶栏大标题下的风味小标题
> `DS_subtitle`（aldrich_16，与大标题同 x/宽 600 居中）挂 `text = "DS_SUBTITLE"`
> → `"§g[GetDSSubtitle]§!"` → `DS_SUB_[?DS_sub_i]`。随机重抽不走事件，而是把
> `DS_sub_roll`（十等分分支赋字面量，见 11.4）挂在 `DS_toggle_panel` 的开面板
> 分支尾部 —— **每次点开面板换一条**。给「面板打开时随机出文案」做新例时照抄这套。

> ⚠⚠ **两套贴图命名空间别混用**：`news_event` 要用 **`GFX_news_event_*`**
> （定义在 `interface/TNO_news_events.gfx`）；`GFX_report_event_*` 是 **country_event** 的
> （定义在 `interface/eventpictures.gfx`）。两者都是 sprite，混用不报错，但风格不属于同一套。
> ⚠ picture **不能动态化**：`picture = { trigger = ... }` 块语法在原版与主 mod 均 0 处，
> 30608 处用法全是写死的静态值（`GFX_xxx` 或直接 `"xxx.dds"`）。十个口径共用一张图；
> 真要「图随口径变」，只能按组分多个 news_event，各自写死 picture，文案仍共用 defined_text。

```paradox
# ② 数值层：文案内部再插缓存的标的名 + 实时数值
DS_NEWS_D_2:0 "...现持有 §Y[GetDSNewsStockName]§! 共 §F[?DS_news_sh|0]§! 股；
按今日 §G$[?DS_news_px|2]§! 的报价计算，账面市值约 §G[?DS_news_amt|2]B§!..."
```

### 11.4 ⚠ 随机口径不要用 `round`

`localization_key = "DS_NEWS_T_[?DS_news_i]"` 是靠**变量渲染成字符串**拼键的。
走 `random × 10 → round_variable` 得到的是 `7.0` 这种浮点，一旦渲染成 `7.00`
就拼出缺失键。**十等分分支直接赋字面量整数**才安全：

```paradox
set_variable = { DS_newsr = random }        # ∈ [0,1)，主 mod ledger_quicksort.txt:31 同款
if      = { limit = { check_variable = { DS_newsr < 0.1 } } set_variable = { DS_news_i = 0 } }
else_if = { limit = { check_variable = { DS_newsr < 0.2 } } set_variable = { DS_news_i = 1 } }
#                    …… 中间同理，步长 0.1 ……
else_if = { limit = { check_variable = { DS_newsr < 0.9 } } set_variable = { DS_news_i = 8 } }
else    = { set_variable = { DS_news_i = 9 } }              # 兜底
```

### 11.5 实现索引

| 部件 | 位置 |
|---|---|
| 事件定义 | `events/DS_deep_state_events.txt` → `news_event ds.11` |
| 上膛 / 倒计时 / 备数 | `DS_news_arm` / `DS_news_tick` / `DS_news_prep` |
| 挂载点 | `DS_action_5` 的 `hidden_effect`；`DS_me_daily` 冷却段之后 |
| 动态键 | scripted_loc `GetDSNewsTitle / GetDSNewsDesc / GetDSNewsStockName` |
| 文案 | yml 键 `DS_NEWS_T_0..9`（标题）/ `DS_NEWS_D_0..9`（正文）/ `DS_NEWS_OK` |

### 11.6 十条口径清单与标题写法

十个视角报道同一件事，`DS_news_i` 十等分随机命中其一：

| i | 视角 | i | 视角 |
|---|---|---|---|
| 0 | 官方通稿 | 5 | 散户营业部彻夜排队 |
| 1 | 交易大厅 / 做市商 | 6 | 车间视角（订单没涨股价先涨） |
| 2 | 内部人对账单 | 7 | 同业协会抗议 |
| 3 | 交易所问询函 | 8 | 质押估值被连夜上调 |
| 4 | 外资行机构内参 | 9 | 本报稿件被撤，仅余更正 |

⚠ **标题统一以主 mod 的报纸抬头 `[Get_newspaper_header]` 开头**（定义在
`TNO_custom_news_headers.txt:7`，同南极新闻事件标题写法）。因此 **T_n 的文案必须写成谓语形式**，
要接在 `[GetDSNewsStockName]` 后面读得通，不能自带主语：

```
 DS_NEWS_T_3:0 "[Get_newspaper_header]§Y[GetDSNewsStockName]§!遭交易所问询，须书面说明买盘来源"
                                                              ^^^^^^^^^^^^^^^^ 谓语开头，无主语
```

⚠ **增删口径要三处同步**：`DS_news_arm` 的分支数与步长 + 中英两份 `DS_NEWS_T_n / D_n`。
少一条键 = 拼出缺失键，标题直接显示成 `DS_NEWS_T_7`。

> ⚠ 倒计时挂在**玩家腿**（`is_ai = no`）：新闻是给「点了行动的那个玩家」看的，
> 状态存在玩家国自己身上。玩家中途控制台切 tag 会让原 tag 的倒计时冻结
> （新 tag 的 `DS_news_cd` 是 0），属预期行为。

## 12. AI 追政策（第 31 轮：让信号影响 AI 买卖）

### 12.1 为什么要做

用户实测「托市（+20%/3 月）看不到 AI 有任何反应」。诊断：AI 唯一的反应通道是
`DS_ai_trade` 里的动量项 `mf = 1 + 0.20 × mom`，而 `mom` 是**小数形式的 3 个月
收益率**（clamp ±0.3）→ 权重封顶仅 ±6%；且 `DS_ai_monthly` 在 `DS_stk_monthly`
里**先跑**、用的是**上月收盘** → 还要滞后一个月。**AI 完全看不到信号本身。**

用户拍板：**托市时 AI 跟风买入（追政策）**。

### 12.2 实现（`DS_ai_trade` 的调仓循环内）

```paradox
# ① 预期剩余总漂移（外生，不随 AI 行为变化 → 主反馈环不存在）
#    ⚠⚠ 只看【主信号】相位 ph = 1：回撤是市场自发修正，AI 不前瞻（见 12.5）
set_temp_variable = { sgx = 0 }
set_temp_variable = { sph = PREV.DS_sig_ph^s }
if = {
    limit = {
        check_variable = { sph > 0.5 }      # 拼等号：check_variable 没有 equals
        check_variable = { sph < 1.5 }
    }
    set_temp_variable = { sgx = PREV.DS_sig_d^s }
    multiply_temp_variable = { sgx = PREV.DS_sig_len^s }
}
# ② 只乘【活跃仓】，绝不碰底仓 sd（红线：tg 整体乘会砍战略头寸 → 正反馈爆炸）
set_temp_variable = { sfk = sgx }
multiply_temp_variable = { sfk = 3 }        # SIG_K
add_to_temp_variable = { sfk = 1 }
multiply_temp_variable = { tg = sfk }
# …… tg += sd 得到目标；算出 d 并写入 sh 之后 ……
# ③ 底仓沉淀：跟风买卖的一半转入 sd（涨加仓 / 跌减仓），使跟风不随信号结束回吐
if = {
    limit = { check_variable = { d > 0 } check_variable = { sgx > 0.001 } }
    set_temp_variable = { snk = d }
    multiply_temp_variable = { snk = 0.5 }  # SINK = 0.5
    add_to_variable = { DS_ai_sd^s = snk }
}
else_if = {
    limit = { check_variable = { d < 0 } check_variable = { sgx < -0.001 } }
    set_temp_variable = { snk = d }
    multiply_temp_variable = { snk = 0.5 }  # SINK_DN = 0.5（第 32 轮）
    add_to_variable = { DS_ai_sd^s = snk }
    if = {                                  # 兜底：底仓为负会算出负市值
        limit = { check_variable = { DS_ai_sd^s < 0 } }
        set_variable = { DS_ai_sd^s = 0 }
    }
}
```

⚠ `PREV` = USA（信号数组在市场主机上），与 `PREV.DS_ai_mom^s` 同款读法。
⚠ 沉淀必须在 **hv 计算之前**（`hv = ns − sd`，顺序反了冲击分母就错）。

### 12.3 ⚠ 标定脚本的指标口径（2026-10-12 修正过一次）

`tools/mc_signal_calib.py` 早期的所有指标都用 `idx = 六只票的指数平均`，
把**被干预那只票**的真实涨幅稀释了约 6 倍，导致**回撤扫描的结论一度是反的**
（看起来「完全回撤能压住发散」，实际把累积从 +182% 推到 +786%）。
**已改为一律盯 `pxs[SIG_STK]`（被干预标的自身价格）。**

**别踩的三个坑**（都是实测出来的）：

* **方案 A（信号进权重 `w`）方向是反的**：`w` 参与 `w/wsum` 归一化，母国
  `base = 12` 已被 clamp 到 3.0，抬高其他股的 `w` 反而**摊薄母国占比** →
  母国（最大持有者）减仓 → 净效果是**卖出**。K 越大托市效果越弱。**已废弃。**
* **让 AI 也前瞻回撤 = 把回撤变成发散放大器**：相位 2 时 `sgx = −0.2` →
  目标仓 `×(1 + 3×−0.2)` 砍六成 → AI 砸盘 → 回撤结束后**暴力回补**，在低位
  买入把价格顶得比峰前还高。连托 12 次累积 **+229%**（连不沉淀也一样）。
  → `AI_SEE_REVERT = False`，AI 只在相位 1 看信号。
* **`spb` 是按初始价写死的常量**（`DS_ai_init:902-907`），不随价格更新 →
  估值通道是断的，AI 不会因为贵了少买。

### 12.4 ⭐ 回撤（均值回归，第 32 轮：涨过要回落、跌过要回升）

用户要求「行动效果（涨或跌）过了之后就会触底回（升降）」。实现 = 给信号加
一个**相位机**，跑完主信号再走一段反向行情。

| 变量 | 含义 |
|---|---|
| `DS_sig_ph^s` | 相位：**1** 主信号 / **2** 回撤 / **0** 无 |
| `DS_sig_rv^s` | 待回撤的**总**幅度（与信号反号），启动回撤后清零防连锁 |

`DS_stk_signal` 上膛时：`rv = mg × (−REVERT)`、`ph = 1`。
`DS_stk_monthly` 在信号块内递减完 `len` 后推进相位：

```paradox
if = {          # 相位 1 跑完 → 切回撤
    limit = { check_variable = { DS_sig_len^sa < 0.5 }
              check_variable = { DS_sig_ph^sa > 0.5 }
              check_variable = { DS_sig_ph^sa < 1.5 } }
    set_temp_variable = { rd = DS_sig_rv^sa }
    set_temp_variable = { rl = 3 }                 # REV_LEN
    divide_temp_variable = { rd = rl }             # ⚠ 除字面量不可信，走 temp
    set_variable = { DS_sig_d^sa = rd }
    set_variable = { DS_sig_len^sa = 3 }
    set_variable = { DS_sig_ph^sa = 2 }
    set_variable = { DS_sig_rv^sa = 0 }
}
else_if = {     # 相位 2 跑完 → 归零（不清 ph 会让下条信号误判、回撤连锁）
    limit = { check_variable = { DS_sig_len^sa < 0.5 }
              check_variable = { DS_sig_ph^sa > 1.5 }
              check_variable = { DS_sig_ph^sa < 2.5 } }
    set_variable = { DS_sig_d^sa = 0 }
    set_variable = { DS_sig_len^sa = 0 }
    set_variable = { DS_sig_ph^sa = 0 }
}
```

⚠⚠ **新数组必须配独立版本旗 `DS_sig_v2`**：复用 `DS_sig_v1` 会漏——老存档
已打过 v1 旗，回撤数组永远不会 `add_to_array` 撑开 → 按下标写无效 →
**回撤静默不生效**（`DS_ai_init` 里的 `for_loop` 同样要加两行）。

**相位推演（纯外生部分，`REV = 0.5`）**：

| | 月 0–2（主信号） | 月 3–5（回撤） | 月 6+ |
|---|---|---|---|
| 托市 +20%/3 月 | 100 → **121.4（峰 +21.4%）** | → 109.6 | 稳在 +9.6% |
| 放料 −8%/3 月 | 100 → **92.2（谷 −7.8%）** | → 96.0 | 稳在 −4.1% |

边界：回撤期（相位 2）中途再托一次 → `DS_stk_signal` 直接覆盖成相位 1 的新
主信号，**不连锁**（`.workbuddy/tmp/dbg_phase.py` 已推演验证）。

### 12.5 落地档标定（`tools/mc_signal_calib.py`，150 月 × 12 次配对同种子）

**REVERT × SINK 联合扫描**（冷却改 365 天后 = 150 月内最多托 12 次）：

| REVERT | SINK | 3 月（峰） | 6 月 | 12 月（净） | **12 次累积** |
|---|---|---|---|---|---|
| 0.0 | 0.5 | +31.37% | +16.78% | +9.72% | **+182%** ❌ 发散 |
| 0.3 | 0.5 | +28.75% | +9.57% | +3.78% | +52% |
| 0.4 | 0.5 | +27.87% | +7.25% | +1.84% | +23% |
| **0.5** | **0.5** | **+26.99%** | **+4.97%** | **−0.06%** | **−0%** ✅ 落地 |
| 0.6 | 0.5 | +26.12% | +2.73% | −1.94% | −19% |
| 0.7 | 0.5 | +25.24% | +0.53% | −3.79% | −34% |
| 1.0 | 0.5 | +22.61% | −5.84% | −9.23% | −64% ❌ 塌陷 |

**落地档体检**（REVERT=0.5 / SINK=0.5 / SINK_DN=0.5 / SIG_K=3.0）：

| | 跟风（信号窗口净买卖） | 持仓 | 3 月 | 6 月 | 12 月 | 12 次累积 | 顶格 |
|---|---|---|---|---|---|---|---|
| 托市 +20%/3 月 | **+0.0431B** | +1.74% | **+26.99%** | +4.97% | −0.06% | **−0%** | 19.4% |
| 放料 −8%/3 月 | **−0.0190B** | −0.71% | **−14.00%** | −5.77% | −3.82% | −25% | 22.2% |

读法：**托市 3 个月见效（+27%），之后回落，一年后基本回到原点，连托 12 次
也不发散**；放料对称，AI 真金白银跟着卖（−0.019B）、持仓真减 0.71%。

⚠ **下跌侧不沉淀的话 AI 等于没抛**：`SINK_DN = 0` 时持仓增幅 −0.00%
（卖完信号一结束又原样买回来）。`SINK_DN = 0.5` 才真的减仓。

> 调参：只改 `sfk` 的乘数（SIG_K）、`snk` 的乘数（SINK / SINK_DN）、
> `rv` 的乘数（REVERT），改完必须重跑 `tools/mc_signal_calib.py`
> 的 `joint_scan()` + `confirm()`，不要凭手感调。


---

## 13. 做空与杠杆（第 45 轮 · 2026-10-20）

### 13.1 状态变量

| 变量 | 口径 | 说明 |
|---|---|---|
| `DS_stk_side` | 标量 1 / 2 | 交易方向：1 = 做多（默认）/ 2 = 做空 |
| `DS_stk_sqty^s` | 数组（股） | 空头股数，恒 ≥ 0 |
| `DS_stk_scost^s` | 数组（美元/股） | 空头开仓均价（移动加权，与多头 `DS_ai_cost` 同款）|
| `DS_stk_sfee` | 标量（十亿） | 累计借券费 |
| `DS_stk_lev` | 标量 2 / 3 / 5 | 融资倍数（默认 2），仅来源 = 3 生效 |
| `DS_stk_margin` | 标量（十亿） | 保证金借款余额（本金），恒 ≥ 0 |
| `DS_stk_mfee` | 标量（十亿） | 累计融资利息 |

⛔⛔ **绝不用负持仓表示空头**：负市值进不了世界榜 / 股东卡
（2026-10-11 美德日负持仓血案，玩家当场发现）。空头独立记账。

⛔ **借款不能记进 `money_reserves` / `national_debt`**：那两个是 TNO
经济系统自己的账，混进去会污染财政结算（准备金被利息打负 →
连锁触发经济事件）。借款只走 `DS_stk_margin`。

### 13.2 结算来源（`DS_fund_src`）

| 值 | 账户 | 买入扣款 |
|---|---|---|
| 1 | 流动准备金 | 全额扣准备金 |
| 2 | 国债 | 全额记国债（信用买入，不设资金上限）|
| 3 | 保证金账户 | 自付 = 金额 ÷ 倍数；借款 = 金额 − 自付 |

UI：**结算来源按钮普通点击**循环 1→2→3→1；**Shift+点击**循环倍数
2x→3x→5x（`_shift_click` 后缀，主 mod `TNO_Antarctica_GUI_AAA.txt` 先例）。

风控：准备金 ≤ 0 时 `DS_stk_can_buy` 已拒绝买入 → 不会无限加杠杆。
月息 = `DS_stk_margin × 1%`（≈年化 12.7%），准备金够就扣、不够转记国债。
⛔ 利息**不计入** `DS_stk_margin`（那是本金），一旦资本化会滚成指数。

### 13.3 做空链路

- **开空** `DS_stk_short_open`：借 q 股卖出 → 所得入准备金；`DS_stk_sqty += q`；
  移动加权更新 `DS_stk_scost`；占本月**卖出**额度（`DS_stk_sdone`）；
  回执 side = 3；`DS_me_flow -= amt`（净流出 → 抛售压价）。
- **平空** `DS_stk_short_close`：买 q 股还券 → 按 `DS_fund_src` 扣款；
  `DS_stk_sqty -= q`；已实现 = `(scost − px) × q ÷ 1e9`（方向与多头**相反**）；
  占本月**买入**额度（`DS_stk_bdone`）；回执 side = 4；`DS_me_flow += amt`。
- **月度借券费**：空头市值 × 0.5%/月，扣准备金（不够转国债）。

⭐ **冲击链路零改动**：`DS_me_flow` 本来就带符号，`imp = flow ÷ 流通盘 × 18`
现成可用 —— 玩家做空直接压价，与"操纵市场"的玩法闭环。

### 13.4 老存档守卫

新增的标量变量（`DS_stk_lev` / `DS_stk_margin` / `DS_stk_mfee` /
`DS_stk_side` / `DS_stk_sfee`）在老存档里**不存在**，而 `DS_me_ready`
已置位 → `DS_stk_init` 不会再跑 → 未定义变量运算会**静默得 0**。
已于 `DS_stk_trade_refresh` 开头统一补默认值。
