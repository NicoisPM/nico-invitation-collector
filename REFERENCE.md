# REFERENCE · 设计系统 / 交互引擎 / 踩坑记录

## 1. 设计系统（暖纸金调）

| Token | 值 | 用途 |
|---|---|---|
| 纸 `--paper` | `#F4EFE3` | 页面底色（暖米纸） |
| 卡 `#FAF8F5` | | 卡片/表单底色 |
| 墨 `--ink-900` | `#0b1e36` | 主文字 |
| 墨阶 | ink-600 `#0a1b2d` / ink-500 `#0f263f` / ink-400 `#183352` / ink-300 `#2d4663` | 次级文字 |
| 金 `--gold` | `#BE9A52` | 强调/描边/分隔线 |
| 金深 `--gold-700` | `#654612` | 金色文字（保证对比度） |
| 朱红 | `rgb(166,59,42)` | 截止/警示标签 |

字体：标题衬线 `"Noto Serif SC", "Songti SC", serif`；正文无衬线 `PingFang SC / Noto Sans SC`；封面主标题书法体 `Ma Shan Zheng`（Google Fonts，无网时回退 `STXingkai/KaiTi`）。字号多用 `clamp()` 随屏宽/高自适应。

## 2. 外壳结构（`<body>` 内）

```
#root
└─ .app-shell
   └─ .relative.max-w-[520px]            ← 手机卡片容器
      ├─ nav.top-chapter-nav             ← 顶部章节导航（每页一个 .chapter-tab，data-target=sectionId）
      ├─ .floating-controls              ← 右下角悬浮按钮（背景音乐 / 自动翻页）
      ├─ #progressBar                    ← 顶部 32px 处的进度线
      └─ #snapRoot                       ← 竖向 scroll-snap 滚动容器
         └─ section.screen-page × N      ← 每页一屏（100svh）
```

- 每页 `<section id="xxx" class="screen-page relative">`，内部首个 `div.reveal` 是左上角标题块（`p.kicker` + `h2`），页脚是 `mt-auto` 的页码行。
- 页与页之间用 `scroll-snap-type: y mandatory` 强吸附；`padding` 由 CSS 变量 `--pt/--px/--pb` 控制。

## 3. 交互引擎（文件末尾 `<script>`）

| 能力 | 说明 |
|---|---|
| `smoothScrollTo(y, dur)` | 缓动翻页；**动画期间临时关闭 scroll-snap** 以避免生硬吸附 |
| `.reveal` | 进入视口 60ms 后加 `.is-in` 淡入上移；`transition-delay` 做错峰 |
| `applyFit()` | **内容自适应缩放**：内容超出可用高度时按比例 `zoom` 缩小（下限 0.6）；`#schedule-1/2` 两页强制同一缩放比 |
| 键盘翻页 | 方向键 / PageUp/Down / 空格 / Home / End |
| 背景音乐 | `#bgmAudio` 自动播放 + `.music-btn` 旋转动画（**需自备 `bgm.mp3`，缺失只报无害 404**） |
| 自动播放 | `#autoScrollBtn` 定时翻页 |
| 表单提交 | `#enrollForm` 提交 → 校验（姓名/企业/手机号）→ `POST /api/signup` → 成功后 `form.reset()` |

**`fit-inner` 机制（重要）**：
- 默认 `shrink-0` + `my-auto`：内容偏矮时**垂直居中**（会留上下白），偏高时 `applyFit` 缩小。
- 想让某页内容**撑满**（如讲师列表），改为 `flex-1` + 内层 `flex flex-col justify-between`——有空间才均分、无空间不挤压，且不写死像素值。

## 4. 踩坑记录（务必注意）

### 4.1 内联 Tailwind 工具类会「静默缺失」
框架里的 Tailwind CSS 是**事先编译好并内联**的快照，**不是** CDN 运行时编译。若你写了一个从未出现在快照里的类（如 `text-[28px]`、`gap-x-12`、`min-h-full`、`tracking-[-0.01em]`），它**不会报错，只是不生效**——排障时极易踩坑。

**排查方法**：F12 看该元素的 computed style 是否等于预期；或搜 `<style>` 里是否存在 `.<类名>{`。

**已知缺失（模板已用显式 CSS 兜底，见自定义 `<style>`）**：`text-[28px]`、`tracking-[-0.01em]`、`gap-x-8`、`gap-x-12`、`gap-y-11`、`min-h-full`。

**规避**：要么用显式行内/CSS 写死（推荐），要么**换 Tailwind Play CDN**（`<script src="https://cdn.tailwindcss.com"></script>`，但需联网、首屏略慢），要么重新编译。

### 4.2 上传文档 + 二维码
- 文档（如「温馨提示」）转成**一个自包含 HTML** 放服务器 `/uploads/` 下，再用二维码指向它。
- 二维码**内联 base64**（用任意在线 QR 接口生成后转 base64 嵌入），自包含、无外链依赖。
- **缓存**：nginx `/uploads/` 常配 `expires 7d`。更新文档后 URL 带版本号（`?v=2`）并同步换二维码，否则用户端 7 天内看不到更新。

### 4.3 部署（nginx 片段）
```nginx
server {
  listen 8082;
  charset utf-8;
  location /invite/  { proxy_pass http://127.0.0.1:3000/invite/; }   # 反代到 Node
  location /api/     { proxy_pass http://127.0.0.1:3000/api/; }
  location /uploads/ { alias /opt/app/server/uploads/; expires 7d; } # 静态：邀请函/文档/bgm
}
```
> 仅做"邀请函 + 报名收集"时**不需要** Chromium；只有还要生成合同 PDF 时才需装无头浏览器（内存占用会明显上升）。

## 5. 后端数据模型

**`nico_invitations`**（邀请函）：`id, title, slug(唯一), file_path, event_time, deadline, organizer, status(active/closed), view_count, created_at, updated_at`

**`nico_invitation_signups`**（报名记录）：`id, nico_invitation_id(FK,SET NULL), nico_invitation_title, name*, phone*, company*, title, count, note, status(pending/contacted/confirmed/cancelled), admin_remark, ip, created_at, updated_at`

> 字段如需增删：改迁移 + `routes/nico-invitation.js` 的 `insertData`/校验 + `SignupList.vue` 表单/表格三处。

---

## 6. 3D 信封与 Web Audio 物理声学引擎架构

### 6.1 3D 信封折叠矩阵 (CSS 3D Flap)
- **透视视口**：封套容器配置 `perspective: 1200px`。
- **折叠轴心**：信封翻盖设置 `transform-origin: top center`。
- **开合动画**：未拆封态为 `rotateX(0deg)`，点击火漆印章后添加 `.opened` 状态，执行 `transform: rotateX(-180deg)`，过渡曲线采用物理弹簧阻尼：
  ```css
  transition: transform 0.85s cubic-bezier(0.4, 0, 0.2, 1);
  ```
- **层叠上下文管理（Z-Index）**：
  - 合拢态：火漆印章 (`z-index: 50`) > 翻盖 (`z-index: 40`) > 信封口袋前袋 (`z-index: 30`) > 内部信纸 (`z-index: 20`) > 信封背板 (`z-index: 10`)。
  - 展开态：内部信纸向上平移 (`translateY(-70%)`) 并提升至最上层 (`z-index: 60`)，完成从信封抽出至撑满全屏的过渡。

### 6.2 零外链 Web Audio API 撕纸音效合成算法
为避免加载外部音效 mp3 导致的延迟与跨域/防盗链风险，信封版采用纯算法实时合成白噪声物理音效：
1. **音频上下文**：在用户点击火漆印章的手势事件内实例化 `AudioContext`（避开移动端浏览器自动播放限制）。
2. **白噪声生成**：通过 `createBuffer(1, sampleRate * 0.18, sampleRate)` 生成 180ms 的随机高斯噪声采样。
3. **频段塑造（Bandpass Filter）**：连接双二阶带通滤波器（`BiquadFilterNode`），中心频率设为 `1200Hz ~ 1800Hz`，Q 值设为 `1.8`，模拟纸质纤维被撕裂时的摩擦共振。
4. **包络衰减（Gain Envelope）**：利用 `gainNode.gain.exponentialRampToValueAtTime(0.001, t + 0.18)` 快速指数衰减，形成干脆物理“刺啦”感。

### 6.3 零依赖轻量本地服务 (`server.js`) 架构
- 基于 Node.js 原生 `http` / `fs` / `path`，完全不需要运行 `npm install`。
- 内置 CORS 跨域放行，兼容前端在不同端口或开发环境下的请求。
- 自动向 CSV 输出添加 `\uFEFF` (UTF-8 BOM)，避免 Excel 打开导出的中文名单出现乱码。

