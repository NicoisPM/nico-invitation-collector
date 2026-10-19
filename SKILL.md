---
name: nico-invitation-collector
description: 制作和优化手机优先的活动邀请函 H5、活动宣传长页与报名页面；支持六套参考提炼主题、轻动效、可选信封，以及原有本地报名收集与名单管理后台。适用于会议、研修、沙龙、黑客松、创作比赛和企业活动，用户提到邀请函、活动报名页或 nico-invitation-collector 时使用。
---

# 活动邀请函与报名收集

产出是适合手机阅读和微信转发的**纵向活动邀请函 H5**。按活动内容组织自然长页，首屏交代活动名称、核心吸引力、时间地点与报名入口。可选信封是进入仪式，打开后仍是一张活动邀请函。

## 内容与主题选择

1. 从用户给出的通知、文章、PDF 或文案提取活动事实、参与价值、日程、规则与报名方式。参考文档中的活动名称、品牌、嘉宾和奖金额只作为参考内容，不能自动成为本次活动事实。
2. 用户已选主题时直接使用；否则按活动调性推荐一套并推进。需要对比时打开 [`templates/design-gallery.html`](templates/design-gallery.html)，提供六套预览和可选主题。已有文案足够时先生成可审阅结果，只询问会影响结果且无法合理推断的信息。
3. 页面块数随内容变化。奖项、赛道、福利、日程、嘉宾、地点和参与规则按需要加入；没有嘉宾资料就省略嘉宾块。不强制七屏、两页议程或固定卡片数量。
4. 已提供官方报名网址时连接原入口；需要自建报名收集时使用本地表单与原后台契约。不要把展示页或点击外链表述为报名完成。

## 六套新主题

主题改变封面构图、标题节奏、容器语法和信息组织，而不只是配色。设计前阅读 [`references/visual-system.md`](references/visual-system.md)；对照原参考时阅读 [`references/reference-map.md`](references/reference-map.md)。

| 配置键 | 可选主题 | 首屏与版式方法 | 适用活动 |
|---|---|---|---|
| `harbor` | 海湾蓝金 | 衬线大数字压在细线城市天际线上，金色地平线与水面倒影；内容块用金线分隔、编号价值块 | 研修、峰会、湾区论坛、招商推介 |
| `arcade` | 青绿创作室 | 奶油色终端窗口微微倾斜作为首屏装置，等宽字与光标；奖励做票根、规则做便签 | 创作招募、社区科技、开发者活动 |
| `neon` | 极夜荧绿 | 近黑舞台 + 扫描线，荧绿斜体大数字套在细环与刻度里；章节序号、榜单式名次 | Coding、AI 黑客松、游戏赛事 |
| `midnight` | 曜石香槟 | 居中对称请柬式构图，香槟金细线与菱形花饰，数字嵌在切角铭牌里 | 企业创新、项目路演、年度盛典 |
| `prism` | 棱镜未来 | 左对齐光谱渐变数字，右侧细线三角与折射光束；极轻字重与青色细线 | 智能硬件、产品发布、技术大会 |
| `editorial` | 纸上共创 | 衬线标题错行缩进，纸张卡片与印章压在超大衬线数字上；正文用边注编号 | 设计征集、学术沙龙、社区共创 |

六套共用一套版式骨架：细线、噪点、发丝分隔、超大主视觉数字、封闭式报名色带。换主题时先看构图是否成立，再调色。

默认 `motion: "subtle"`：标题逐行遮罩上升、内容上移 14px、细线展开。`motion: "none"` 关闭装饰动效，系统减少动态效果偏好也应生效。`envelope` 按用户要求开启，未要求时可直接进入。

需要重新排布主题预览或刷新母版快照时运行 `python3 build_gallery.py`；加 `--snapshots` 会同时按 `event.modern.example.json` 重生成 `templates/nico-invitation-<theme>[-envelope].html`。画廊直接内嵌真实渲染结果，改样式后重跑即可，不要手改 `design-gallery.html`。

## 生成与配置

从本技能目录运行已有 Python；按用户的软件偏好检查现有运行环境，不自动安装软件或依赖。

```bash
python generator.py --config event.json
```

新主题由 `invitation_design.py` 的 `render_invitation(config) -> str` 渲染，CLI 负责保存 HTML 与配置。主要配置项：

| 字段 | 用途 |
|---|---|
| `theme` | 六个新主题键，或兼容旧主题 |
| `title`, `subtitle`, `date`, `location`, `organizer` | 已知活动信息；不要补造未提供事实 |
| `hero` | 可选 `display / eyebrow / lines[] / statement / stamp`，分别控制主视觉短字、小标、标题换行、强调句与竖排小字；`display` 留空则该主题不渲染大数字 |
| `sections` | 按叙事顺序排列的内容块，具体结构见下表 |
| `registration_mode` | `external` 连接官方入口；`local` 使用原报名接口 |
| `registration_url` | 外链报名的真实网址 |
| `registration_label`, `registration_steps` | 报名按钮文字与说明步骤 |
| `event_slug` | 活动的稳定短标识，用于名单归属 |
| `envelope`, `motion` | 信封开关；`subtle` 或 `none` |
| `output` | 活动专属目录内的 HTML 路径 |

每个 `section` 支持 `type / id / title / lead`，可选 `nav` 设置快捷入口文字（最多显示三项），可选 `kicker` 在序号旁加一行小标签（如 `AWARD`、`SCHEDULE`）。当前内容块契约：

| `type` | 内容字段 |
|---|---|
| `highlights`, `benefits` | `items: [{value, label, detail}]`，适合关键数字、亮点与福利 |
| `prize` | `value, unit, label, extras: []`，适合主奖项 |
| `tracks` | `items: [{name, sponsor, tagline, rewards: [{rank, cash, extra}], details: []}]` |
| `partners` | `groups: [{label, names: []}]` |
| `rules` | `items: [{title, body}]` |
| `timeline` | `days: [{date, title, items: [{time, title, detail}]}]` |
| `faq` | `items: [{question, answer}]` |
| `quote` | `body` 与可选 `cite`，做一句被引用的主张，用来断开长页节奏 |
| `paragraph` | `body` 与可选字符串数组 `items` |

可直接调用：

```python
from invitation_design import render_invitation

html = render_invitation({
    "theme": "neon",
    "title": "AI 创作周末",
    "subtitle": "带上电脑，让一个想法发生",
    "date": "10月24日—25日",
    "location": "各城市会场与线上赛区",
    "sections": [{
        "id": "about", "type": "paragraph", "title": "一起把想法做出来",
        "body": "选择一件你想做的事，独立开发或与伙伴组队。"
    }],
    "registration_mode": "external",
    "registration_url": "https://events.waytoagi.com/collections/qiecuo1024",
    "envelope": False,
    "motion": "subtle"
})
```

示例中的网址仅用于对应活动，其他活动须替换为用户提供或核验后的入口。字符串会作为文本转义，不以未支持的任意 HTML 代替内容块。

每次生成保留 `event.json`，便于换主题与再次生成。默认使用技能下 `output/<活动标识>/index.html`；用户或会话指定成果目录时优先服从该路径，保持一活动一目录。定制活动不能覆盖 `templates/` 母版。

## 兼容原有八款模板

旧主题 `red / green / hk / default` 仍各有直入与信封两种版本：

| 主题键 | 直入模板 | 信封模板 |
|---|---|---|
| `red` | `nico-invitation-red-party.html` | `nico-invitation-red-party-envelope.html` |
| `green` | `nico-invitation-green-eco.html` | `nico-invitation-green-eco-envelope.html` |
| `hk` | `nico-invitation-hk-skyline.html` | `nico-invitation-hk-skyline-envelope.html` |
| `default` | `nico-invitation-framework.html` | `nico-invitation-envelope.html` |

上述文件均在 `templates/`。仅在使用旧吸附母版时参考 [`REFERENCE.md`](REFERENCE.md) 的 `snapRoot / screen-page / fit-inner` 机制及 Web Audio 细节；旧文件中的固定屏数、整屏缩放与自动播放示例不构成新主题要求。原有功能可保留，不为新活动无故增加音乐、撕纸音效或自动翻页。

## 报名与后台契约

- **外链报名**：CTA 连接 `registration_url`，首屏、长页末尾或手机底部操作区可提供入口。使用“前往官网报名”等真实动作，不显示虚假报名成功，不额外采集姓名和电话。
- **本地收集**：使用 `form#enrollForm`，保留 `name / company / title / phone / count / note`。向 `POST /api/signup` 提交并附带活动 slug；姓名必填，电话与后端一致（当前为中国大陆 11 位、以 1 开头）。只有接口明确返回成功才显示提交成功，失败保留输入并允许重试。
- **兼容后台**：`node server.js` 启动原生 Node 本地服务，入口 `/admin`，名单保存于 `data/signups.json`；保留统计、搜索、筛选和 UTF-8 BOM CSV 导出。现有后端集成文件位于 `templates/backend/`。
- **运行方式**：静态 HTML 可预览页面；本地报名需要已启动服务。`file://` 预览表单可使用渲染器已有的本机接口回退；对外发布配置实际同源接口。浏览器本地状态不能证明数据已保存。

## 交付前检查

- 手机宽度检查首屏、最长文字块、奖项规则与报名入口；内容增长时自然延伸，不整块缩小塞进一屏。
- 核对金额、名额、日期、单位和参与条件；分清总奖池、现金、临时算力与永久算力，赞助总价值不描述成现金总额。
- 检查按钮、锚点、信封跳过与减少动态效果；`motion: none` 时内容完整可见。固定底栏不遮挡末尾内容。
- 本地报名验证接口失败与成功行为；外链报名验证链接正确且不写入本地名单。
- HTML/CSS/SVG/脚本优先内嵌，无网络时主体可读；使用已有或用户提供的可用素材，不强行安装字体、浏览器或下载软件。
- 交付独立活动目录、配置与预览入口。技能升级另交付技能包，并明确邀请函技能位置。
