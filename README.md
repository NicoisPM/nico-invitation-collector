# nico-invitation-collector

手机优先的**活动邀请函 H5 + 报名收集**技能：一份配置生成一张可转发的纵向邀请函长页，六套构图各异的视觉方向，可选信封入场，或接本地报名表单与名单后台。

## 六套视觉方向

主题改变首屏构图、标题节奏、容器语法与信息组织，而不是只换配色。

| 键 | 主题 | 首屏方法 | 适合 |
|---|---|---|---|
| `harbor` | 海湾蓝金 | 衬线大数字压在城市天际线上，金色地平线 | 研修、峰会、湾区论坛 |
| `arcade` | 青绿创作室 | 奶油色终端窗口作为首屏装置 | 创作招募、社区科技 |
| `neon` | 极夜荧绿 | 近黑舞台＋扫描线，荧绿斜体数字 | Coding、AI 黑客松 |
| `midnight` | 曜石香槟 | 居中对称请柬，香槟金细线铭牌 | 企业创新、项目路演 |
| `prism` | 棱镜未来 | 光谱渐变数字＋细线三角折射 | 智能硬件、产品发布 |
| `editorial` | 纸上共创 | 衬线大字错行、纸卡印章压字 | 设计征集、学术沙龙 |

对比六套可直接打开 [`templates/design-gallery.html`](templates/design-gallery.html)（内嵌真实渲染结果）。

## 快速开始

```bash
python3 generator.py --config event.modern.example.json --theme neon
python3 generator.py                     # 交互式向导
node server.js                           # 本地报名服务 + /admin 名单后台
```

产物是单文件 HTML，CSS/JS/SVG 全部内嵌，离线可读。

## 目录

```
invitation_design.py     六套主题渲染器（render_invitation(config)）
assets/                  invitation.css / invitation.js（内联进产物）
generator.py             命令行与交互式生成
server.js                报名接口 + 名单后台
build_gallery.py         重建 design-gallery.html，--snapshots 同时刷新母版快照
references/              视觉系统与参考映射说明
templates/               母版快照、后台与旧版四主题
event.modern.example.json  新主题配置示例
```

## 兼容旧版

`red / green / hk / default` 四套吸附式模板仍然可用，各有直入与信封两个版本，机制见 [`REFERENCE.md`](REFERENCE.md)。新主题不使用固定屏数与整屏缩放。

## 说明

参考图只用于提炼构图、形状与阅读节奏；主题内不含任何第三方品牌素材与人物照片。示例中的活动名称、时间与报名入口均为占位内容，正式使用请替换为真实信息。
