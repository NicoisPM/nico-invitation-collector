#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild templates/design-gallery.html from the live renderer.

The gallery embeds one real render per theme, so what you compare is exactly
what generator.py produces — no hand-drawn mockups that drift from the code.

    python3 build_gallery.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from invitation_design import THEMES, render_invitation  # noqa: E402

TEMPLATES = HERE / 'templates'

COPY = {
    'harbor': ('浅蓝纸面上一条金色地平线。城市线稿只出现一次，把正式感做轻。',
               '研修 · 峰会 · 湾区论坛 · 招商推介'),
    'arcade': ('一台还开着的终端，一张能撕下的票根。把招募写得像邀请朋友。',
               '创作招募 · 社区科技 · 开发者活动'),
    'neon': ('近黑舞台、荧绿大字。像赛事计分板，数字先说话，正文安静。',
             'Coding · AI 黑客松 · 游戏赛事'),
    'midnight': ('居中对称、烫金细线、切角铭牌，按正式请柬的规矩排。',
                 '企业创新 · 项目路演 · 年度盛典'),
    'prism': ('一束光穿过三角，标题浮在留白里。适合讲一个新产品。',
              '智能硬件 · 产品发布 · 技术大会'),
    'editorial': ('衬线大字、边注、便签。把手机长页做成一本杂志。',
                  '设计征集 · 学术沙龙 · 社区共创'),
}

PREVIEW = {
    'hero': {'display': '1024', 'eyebrow': 'TRAE FRIENDS · 中山站', 'lines': ['把想法', '做成现场。'],
             'statement': '两天时间，一次公开的成果展示。'},
    'title': '创造者相聚计划',
    'brand': 'NICO INVITATION',
    'subtitle': '一次把想法变成现场的聚会。带上你的电脑，也带上你想做的事。',
    'date': '2026年10月24日—25日',
    'location': '中山 · 翠亨新区 湾区设计中心 3F',
    'organizer': '主办 · 西湾智慧研究院',
    'registration_mode': 'external',
    'registration_url': 'https://events.example.com/zhongshan1024',
    'registration_label': '前往官网报名',
    'sections': [
        {'id': 'why', 'type': 'highlights', 'nav': '为什么来', 'title': '为一次出发，\n找到值得的理由。',
         'lead': '不是听课，是把手里那件没做完的事，推到能被人看见的位置。',
         'items': [{'value': '48', 'label': '小时在场', 'detail': '全程开放工位与导师巡场。'},
                   {'value': '12', 'label': '位导师', 'detail': '产品、设计、工程三条线。'},
                   {'value': '300', 'label': '位同行者', 'detail': '本地团队、高校与独立创作者。'},
                   {'value': '01', 'label': '次公开演示', 'detail': '最后半天，所有人上台讲三分钟。'}]},
        {'id': 'tracks', 'type': 'tracks', 'nav': '赛道', 'title': '三条路，\n选一条走到底。',
         'items': [{'name': '智能体应用', 'sponsor': '官方提供开发环境',
                    'tagline': '从一个真实麻烦出发，做一个能替人省下时间的东西。',
                    'rewards': [{'rank': '一等奖', 'cash': '30,000', 'extra': '含算力支持'},
                                {'rank': '二等奖', 'cash': '10,000', 'extra': ''},
                                {'rank': '三等奖', 'cash': '5,000', 'extra': ''}],
                    'details': ['作品需在活动期间完成主要开发', '允许基于已有开源项目改造']}]},
    ],
    'closing_title': '10月24日，\n在中山见。',
    'closing_copy': '名额不多，报名后会收到一封确认短信。',
    'footer': 'TRAE Friends · 中山站 · 2026',
    'motion': 'subtle',
}

PAGE = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nico · 活动邀请函六套视觉方向</title>
<style>
*{{box-sizing:border-box}}
:root{{
  --ink:#1b1e19; --muted:#6c7267; --line:#d8d6cb; --paper:#f4f3ec; --card:#fbfaf5;
  --sans:"PingFang SC","HarmonyOS Sans SC","Microsoft YaHei",system-ui,sans-serif;
  --serif:"Songti SC","STSong","Noto Serif SC",Georgia,serif;
  --mono:ui-monospace,"SF Mono",Menlo,monospace;
}}
body{{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);-webkit-font-smoothing:antialiased}}
a{{color:inherit}}
.gbar{{position:sticky;top:0;z-index:10;display:flex;justify-content:space-between;gap:20px;
  max-width:1360px;margin:0 auto;padding:20px 40px;font-size:11px;
  background:rgba(244,243,236,.9);backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}}
.gbar strong{{font:500 11px var(--mono);letter-spacing:.22em}}
.gbar span{{color:var(--muted);letter-spacing:.08em}}
.wrap{{max-width:1360px;margin:0 auto;padding:0 40px 90px}}
.intro{{padding:64px 0 44px;max-width:760px}}
.intro .eyebrow{{font:400 10px var(--mono);letter-spacing:.24em;color:var(--muted);margin:0 0 18px}}
.intro h1{{font-size:clamp(34px,4.4vw,58px);line-height:1.14;font-weight:500;letter-spacing:-.045em;margin:0}}
.intro p{{margin:18px 0 0;font-size:14.5px;line-height:1.95;color:var(--muted);max-width:44em}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:44px 34px}}
.card{{min-width:0}}
.shot{{position:relative;overflow:hidden;border:1px solid var(--line);border-radius:20px;background:#fff;
  max-width:390px;margin:0 auto;box-shadow:0 26px 44px -38px rgba(27,30,25,.55)}}
.shot iframe{{width:390px;height:720px;border:0;display:block;transform-origin:top left;background:#fff}}
.card h2{{margin:18px 0 0;font-size:19px;font-weight:500;letter-spacing:-.02em}}
.card .cn{{color:var(--muted);font-size:11.5px;letter-spacing:.06em;margin:7px 0 0}}
.card .desc{{margin:12px 0 0;font-size:13px;line-height:1.9;color:#4d534a}}
.chips{{display:flex;gap:7px;margin:14px 0 0;padding:0;list-style:none}}
.chips li{{width:22px;height:22px;border-radius:50%;border:1px solid rgba(0,0,0,.14)}}
.card .link{{display:inline-flex;align-items:center;gap:7px;margin-top:14px;font-size:11.5px;
  color:var(--muted);text-decoration:none;border-bottom:1px solid var(--line);padding-bottom:3px}}
.card .link:hover{{color:var(--ink);border-color:var(--ink)}}
.principles{{margin-top:86px;border-top:1px solid var(--line);padding-top:44px;
  display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:34px}}
.principles h3{{margin:0 0 10px;font-size:13px;font-weight:600;letter-spacing:.02em}}
.principles p{{margin:0;font-size:12.5px;line-height:1.95;color:var(--muted)}}
.note{{margin-top:56px;padding:22px 24px;border:1px solid var(--line);background:var(--card);
  font-size:12.5px;line-height:1.95;color:var(--muted);max-width:820px}}
.note b{{color:var(--ink);font-weight:500}}
@media(max-width:700px){{
  .gbar,.wrap{{padding-left:22px;padding-right:22px}}
  .intro{{padding-top:44px}}
  .grid{{gap:36px 22px}}
}}
</style></head><body>
<header class="gbar"><strong>NICO · INVITATION</strong><span>六套视觉方向 · 共用一套内容契约</span></header>
<div class="wrap">
  <section class="intro">
    <p class="eyebrow">DESIGN DIRECTIONS</p>
    <h1>六套方向，<br>同一份邀请。</h1>
    <p>每一套都换构图，而不只是换颜色：首屏的主视觉、标题节奏、容器形状和信息组织方式各自不同。下面是真实渲染结果，可直接与生成器产出的页面逐像素对照。</p>
  </section>
  <section class="grid">
{cards}
  </section>
  <section class="principles">
    <div><h3>版式</h3><p>首屏先给主张，再给时间地点；正文按叙事顺序自然延伸，不把内容压进固定屏数。手机 22–28px 边距，段落之间留 56–88px。</p></div>
    <div><h3>字体</h3><p>中文用系统字体，拉丁数字用窄字距的无衬线，注释用等宽体。每套主题最多三种字体角色，靠字号、字重与字距建立层次。</p></div>
    <div><h3>材质</h3><p>细线、噪点、渐变光与金属色只做点缀。容器以细线和留白为主，不为每段加卡片或阴影。</p></div>
    <div><h3>动效</h3><p>标题逐行遮罩上升，内容上移 14px 后静止。默认 450–900ms；系统减少动态效果时全部关闭，内容照常可读。</p></div>
  </section>
  <div class="note"><b>关于素材：</b>主题只用 HTML / CSS / SVG 表达构图，不包含参考案例里的品牌素材与人物照片。活动名称、时间、奖项与报名入口全部来自配置，示例中的活动信息只用于预览。</div>
</div>
<script>
const DATA = {data};
document.querySelectorAll('iframe[data-key]').forEach(function (frame) {{
  const html = DATA[frame.getAttribute('data-key')];
  if (html) frame.srcdoc = html;
}});
function fit() {{
  document.querySelectorAll('.shot').forEach(function (box) {{
    const frame = box.querySelector('iframe');
    const scale = box.clientWidth / 390;
    frame.style.transform = 'scale(' + scale + ')';
    box.style.height = (720 * scale) + 'px';
  }});
}}
addEventListener('resize', fit);
fit();
</script>
</body></html>'''


def build():
    cards = []
    data = {}
    for key, t in THEMES.items():
        cfg = dict(PREVIEW, theme=key, event_slug='gallery-' + key)
        data[key] = render_invitation(cfg)
        name, scene = t['name'], t['label']
        desc, usage = COPY[key]
        chips = ''.join(
            f'<li style="background:{t[c]}" title="{t[c]}"></li>'
            for c in ('bg', 'ink', 'accent', 'metal')
        )
        cards.append(
            f'''    <article class="card">
      <div class="shot"><iframe data-key="{key}" title="{name} 主题预览" loading="lazy"></iframe></div>
      <h2>{name}</h2>
      <p class="cn">{scene} · {usage}</p>
      <p class="desc">{desc}</p>
      <ul class="chips">{chips}</ul>
      <a class="link" href="nico-invitation-{key}.html" target="_blank" rel="noopener">打开完整页面 ↗</a>
    </article>'''
        )
    payload = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    html = PAGE.format(cards='\n'.join(cards), data=payload)
    target = TEMPLATES / 'design-gallery.html'
    target.write_text(html, encoding='utf-8')
    print(f'gallery → {target} ({target.stat().st_size // 1024} KB)')


def snapshots():
    """Refresh the six standalone template previews from the same renderer."""
    example = json.loads((HERE / 'event.modern.example.json').read_text(encoding='utf-8'))
    for key in THEMES:
        cfg = dict(example, theme=key, event_slug='template-' + key, envelope=False)
        (TEMPLATES / f'nico-invitation-{key}.html').write_text(render_invitation(cfg), encoding='utf-8')
        cfg['envelope'] = True
        (TEMPLATES / f'nico-invitation-{key}-envelope.html').write_text(render_invitation(cfg), encoding='utf-8')
    print('templates refreshed')


if __name__ == '__main__':
    if '--snapshots' in sys.argv:
        snapshots()
    build()
