# 事件接口（NSP_ev_*）

写新事件时，效果直接在选项里调用这些接口，**不用改 SPACE 本体的任何文件**，只需要你自己的事件文件和本地化。
代码在 `common/scripted_effects/NSP_api_effects.txt` 末尾；完整示例在 `documentation/examples/NSP_event_api_example/`（可以直接当子模组加载，-debug 模式下调试决议里能触发 3 个示例事件）。

## 测试

-debug 启动 → 调试决议「事件接口测试」，打开 `events/NSP_debug_events.txt` 的测试事件：每个接口都有选项，事件描述显示当前读数，点完会重新弹出同一事件方便对照。

## 用法

HOI4 的 scripted effect 不收参数，所以**先写临时变量，再调用**：

```
option = {
	name = my_event.1.a
	set_temp_variable = { ev_val = 0.5 }  NSP_ev_add_budget = yes      # 经费 +0.5B
	set_temp_variable = { ev_id = 53 }    NSP_ev_complete_rd = yes     # 立即完成研发 53
	NSP_ev_this_mission = yes                                           # 选中「本次任务」
	set_temp_variable = { ev_val = 10 }   NSP_ev_mission_rel = yes     # 本次任务成功率 +10
}
```

- 每个接口**自带选项提示**（正数绿色、负数红色），实际改动都在 `hidden_effect` 里，选项里不用再写 `custom_effect_tooltip`。
- 不会生效的效果不显示提示：没有选中进行中的任务、研发已完成、研发没在进行时，对应接口既不改数值也不出提示。
- 想自己写提示：先 `set_temp_variable = { ev_silent = 1 }`，接口就不显示自带提示。
- 每个接口执行完会把 `ev_val`、`ev_id` 清零；`ev_mid` 保留，选一次任务可以连用几个任务接口。
- 接口会自己刷新主页 / 规划器显示，不用再调 `NSP_recalc_*`。

## 参数

| 参数 | 含义 |
|---|---|
| `ev_val` | 数值，单位见下表；可为负的接口会注明 |
| `ev_id` | 研发 id（本体 0..94，名称见 `NSP_rd_l_simp_chinese.yml` 的 `NSP_RD_N_<id>`） |
| `ev_mid` | 任务 id；-1 = 没有任务，任务接口什么也不做。用下面两个接口来选，不要手写数字 |
| `ev_silent` | 1 = 不显示自带提示 |

## 接口一览

### 国家层面

| 接口 | 参数 | 效果 |
|---|---|---|
| `NSP_ev_add_budget` | `ev_val` B（可负） | 经费 ± ev_val B（0.5 = 5 亿美元） |
| `NSP_ev_add_popularity` | `ev_val` 点（可负） | NASA公众支持度 ±，结果限制在 0..100 |
| `NSP_ev_add_tech` | `ev_val` 点 | 太空科技经验 +；够门槛立即升级，照常给升级奖励、弹升级事件 |

### 研发

| 接口 | 参数 | 效果 |
|---|---|---|
| `NSP_ev_complete_rd` | `ev_id` | 立即完成该研发（不管前置、不管是否在研；已完成则无效）。和正常完成一样给太空科技经验、一次性奖励、研发槽，重算解锁 |
| `NSP_ev_rd_progress` | `ev_id`、`ev_val` %（可负） | 正在研发的项目进度 ±；到 100 立即完成。没在研发时无效 |

### 进行中的任务（先选任务）

| 接口 | 参数 | 效果 |
|---|---|---|
| `NSP_ev_this_mission` | — | `ev_mid` = 本次任务。本体任务事件 nsp.1..7，以及从它们的选项里触发的事件，指的就是事件说的那个任务 |
| `NSP_ev_newest_mission` | — | `ev_mid` = 最新开始、还没结束的任务；没有时 -1（读 `NSP_newest_mid`，选项里直接用，提示正常） |
| `NSP_ev_mission_rel` | `ev_mid`、`ev_val` 百分点（可负） | 任务成功率 ±（0..100）。发射阶段已经掷过骰的任务也生效：结局按新成功率重新对照那次骰子，发射动画随之变化 |
| `NSP_ev_mission_return_rel` | `ev_mid`、`ev_val` 百分点（可负） | 载人任务返程可靠性 ±（0..100），决定乘组能否生还。无人任务不显示提示、也不起作用 |
| `NSP_ev_mission_delay` | `ev_mid`、`ev_val` 天（可负） | 当前阶段推迟 ev_val 天；负数 = 提前，当前阶段最少剩 1 天 |

### 下一次任务

在规划器的可靠性 / 成本提示里显示为「事件」一项，点「启动任务」时生效并清零；多次触发会叠加。

| 接口 | 参数 | 效果 |
|---|---|---|
| `NSP_ev_next_rel` | `ev_val` 百分点（可负） | 下一次任务成功率 ± |
| `NSP_ev_next_cost` | `ev_val` %（可负） | 下一次任务成本 ±%，-20 = 打八折，最多 -90 |

## 注意

- 事件文件放 `events/`，本地化放 `localisation/simp_chinese/`（带 BOM）。命名空间别用 `nsp`（本体在用）。
- 想在条件里判断，可以直接读本体变量：`NSP_space_budget`（百万美元）、`NSP_popularity`、`NSP_rd_state^<id> = 3`（已完成）、`NSP_missions`（进行中的任务数组）。
- 需要新的接口（例如解锁某个载荷、改局长），告诉维护者在 `NSP_api_effects.txt` 末尾加一个 `NSP_ev_*`，不要在你的事件里直接改本体数组。
