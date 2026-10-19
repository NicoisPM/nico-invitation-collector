"""Modern mobile invitation themes.

Six editorial art directions sharing one content contract.
Python stdlib only; every asset is inlined into a single HTML file.
"""
from html import escape
from urllib.parse import urlparse
from pathlib import Path
import json
import re

# Each theme changes composition, not only colour. Tokens feed CSS variables;
# the rest of the art direction lives in assets/invitation.css keyed by data-theme.
THEMES = {
    'harbor': dict(
        name='海湾蓝金', label='研修 · 峰会 · 城市交流',
        bg='#eef2f5', ink='#0f2b3d', muted='#5b7285',
        accent='#1b5b85', surface='#e3ebf0', line='#cfdae2', metal='#a8854e',
        band='#0f2b3d', bandink='#eef3f6', bandmuted='#9db4c4', contrast='#d9c39a',
        glass='rgba(238,242,245,.86)', accent_soft='rgba(27,91,133,.10)', accent_line='rgba(27,91,133,.34)',
    ),
    'arcade': dict(
        name='青绿创作室', label='创作招募 · 开发者活动',
        bg='#ecefe4', ink='#123c35', muted='#57705f',
        accent='#1a6b57', surface='#e0e6d4', line='#c8d2bd', metal='#a8873c',
        band='#123c35', bandink='#f0f2e2', bandmuted='#a7bda9', contrast='#e8d9a8',
        glass='rgba(236,239,228,.86)', accent_soft='rgba(26,107,87,.10)', accent_line='rgba(26,107,87,.32)',
    ),
    'neon': dict(
        name='极夜荧绿', label='Coding · AI 竞赛',
        bg='#08100d', ink='#edf3ee', muted='#94a89c',
        accent='#c2f06f', surface='#111d18', line='#26382f', metal='#cfd8d1',
        band='#c2f06f', bandink='#08130d', bandmuted='#3c5c34', contrast='#c2f06f',
        glass='rgba(8,16,13,.78)', accent_soft='rgba(194,240,111,.10)', accent_line='rgba(194,240,111,.42)',
    ),
    'midnight': dict(
        name='曜石香槟', label='企业创新 · 项目路演',
        bg='#0e1520', ink='#f2eee6', muted='#9fa9ba',
        accent='#dcc08c', surface='#18212f', line='#314054', metal='#dcc08c',
        band='#18212f', bandink='#f6f2e9', bandmuted='#a7b0bf', contrast='#dcc08c',
        glass='rgba(14,21,32,.80)', accent_soft='rgba(220,192,140,.10)', accent_line='rgba(220,192,140,.36)',
    ),
    'prism': dict(
        name='棱镜未来', label='智能硬件 · 产品发布',
        bg='#070c14', ink='#f2f6f9', muted='#93a6b7',
        accent='#8fdcea', surface='#111b28', line='#263644', metal='#cfdde5',
        band='#0d1622', bandink='#f2f6f9', bandmuted='#93a6b7', contrast='#8fdcea',
        glass='rgba(7,12,20,.80)', accent_soft='rgba(143,220,234,.10)', accent_line='rgba(143,220,234,.34)',
    ),
    'editorial': dict(
        name='纸上共创', label='社区共创 · 设计征集',
        bg='#f6f4ee', ink='#23271f', muted='#6a7063',
        accent='#3f6b4f', surface='#ece9dc', line='#d6d5c5', metal='#a08a63',
        band='#23271f', bandink='#f4f2e9', bandmuted='#a9ab9c', contrast='#c9a86a',
        glass='rgba(246,244,238,.86)', accent_soft='rgba(63,107,79,.09)', accent_line='rgba(63,107,79,.30)',
    ),
}

TOKEN_KEYS = ('bg', 'ink', 'muted', 'accent', 'surface', 'line', 'metal', 'band', 'bandink', 'bandmuted',
              'contrast', 'glass', 'accent_soft', 'accent_line')


def e(v):
    return escape(str(v if v is not None else ''), quote=True)


def text(v):
    return e(v).replace('\n', '<br>')


def url(v):
    v = str(v or '').strip()
    p = urlparse(v)
    return v if p.scheme in ('https', 'http') and p.netloc else ''


def slug(v):
    return re.sub(r'[^a-z0-9_-]+', '-', str(v).lower()).strip('-')[:80] or 'invitation'


def li(items):
    return ''.join('<li>' + text(i) + '</li>' for i in items if i)


def title_lines(hero, title):
    raw = hero.get('lines') or [title]
    out = []
    for item in raw:
        out.extend(str(item).split('\n'))
    out = [x.strip() for x in out if x.strip()]
    return out or [str(title or '诚邀相聚')]


# ---------------------------------------------------------------- hero art

# (x, width, height) — deliberately uneven so the skyline reads as a city,
# not as a bar chart.
HARBOR_BLOCKS = [
    (10, 24, 52), (40, 16, 94), (60, 28, 68), (94, 14, 132), (112, 22, 88),
    (138, 30, 60), (174, 18, 116), (196, 26, 80), (226, 14, 152), (244, 26, 100),
    (276, 20, 62), (300, 30, 112), (336, 16, 74), (358, 24, 140), (386, 28, 90),
    (420, 18, 58), (442, 26, 106), (474, 16, 82), (494, 30, 126), (530, 20, 66),
    (554, 26, 94), (586, 22, 74),
]


def _harbor_city(y, scale=1.0, dx=0.0):
    out = []
    for i, (x, w, h) in enumerate(HARBOR_BLOCKS):
        hh = h * scale
        x += dx
        out.append(f'<path d="M{x:.1f} {y} V{y - hh:.1f} H{x + w:.1f} V{y}"/>')
        if i % 5 == 2:
            out.append(
                f'<path d="M{x + w * .26:.1f} {y - hh:.1f} V{y - hh - h * .16:.1f} '
                f'H{x + w * .74:.1f} V{y - hh:.1f}"/>'
            )
        if i % 7 == 3:
            out.append(f'<path d="M{x + w * .5:.1f} {y - hh:.1f} V{y - hh - h * .22:.1f}"/>')
    return ''.join(out)


def _harbor_art(display):
    return (
        '<svg class="art-svg art-harbor" viewBox="0 0 640 336" preserveAspectRatio="xMidYMax meet" xmlns="http://www.w3.org/2000/svg">'
        '<circle class="hb-sun" cx="566" cy="238" r="30"/>'
        '<circle class="hb-sun-ring" cx="566" cy="238" r="42"/>'
        '<g class="hb-far">' + _harbor_city(292, .58, 12) + '</g>'
        '<g class="hb-sky">' + _harbor_city(292) + '</g>'
        '<line class="hb-horizon" x1="0" y1="292" x2="640" y2="292"/>'
        '<g class="hb-reflect" transform="translate(0 584) scale(1 -1)">' + _harbor_city(292) + '</g>'
        '<g class="hb-ripples">' + ''.join(
            f'<line x1="{36 + i * 58}" y1="{306 + (i % 3) * 12}" x2="{36 + i * 58 + 22 + (i % 4) * 26}" y2="{306 + (i % 3) * 12}"/>'
            for i in range(11)
        ) + '</g>'
        '</svg>'
    )


def _neon_art(display):
    ticks = ''.join(
        f'<line class="neon-tick" x1="300" y1="34" x2="300" y2="46" transform="rotate({a} 300 220)"/>'
        for a in range(0, 360, 15)
    )
    return (
        '<svg class="art-svg art-neon" viewBox="0 0 600 440" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">'
        '<circle class="neon-ring neon-ring-1" cx="300" cy="220" r="176"/>'
        '<circle class="neon-ring neon-ring-2" cx="300" cy="220" r="132"/>'
        '<path class="neon-arc" d="M300 44 A176 176 0 0 1 476 220"/>'
        '<path class="neon-arc neon-arc-2" d="M124 220 A176 176 0 0 1 300 396"/>'
        '<g class="neon-ticks">' + ticks + '</g>'
        '<circle class="neon-node" cx="476" cy="220" r="5"/>'
        '<circle class="neon-node neon-node-2" cx="124" cy="220" r="3"/>'
        '</svg>'
    )


def _midnight_art(display):
    arcs = ''.join(
        f'<ellipse class="md-arc" cx="300" cy="222" rx="{206 - i * 28}" ry="{206 - i * 28}" '
        f'transform="rotate({-18 + i * 12} 300 222)"/>'
        for i in range(4)
    )
    return (
        '<svg class="art-svg art-midnight" viewBox="0 0 600 430" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">'
        '<g class="md-orn">'
        '<line x1="236" y1="26" x2="286" y2="26"/><path d="M300 20 l6 6 -6 6 -6 -6 Z"/>'
        '<line x1="314" y1="26" x2="364" y2="26"/></g>'
        '<rect class="md-plate" x="156" y="104" width="288" height="236"/>'
        '<rect class="md-plate-in" x="167" y="115" width="266" height="214"/>'
        '<g class="md-arcs">' + arcs + '</g>'
        '<line class="md-line" x1="52" y1="366" x2="548" y2="366"/>'
        '</svg>'
    )


def _prism_art(display):
    rays = ''.join(
        f'<line class="prism-ray r{i % 4}" x1="392" y1="250" x2="{600 + 40 * (i % 3)}" y2="{128 + i * 42}"/>'
        for i in range(6)
    )
    return (
        '<svg class="art-svg art-prism" viewBox="0 0 600 380" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">'
        '<path class="prism-tri" d="M392 58 L626 356 L158 356 Z"/>'
        '<path class="prism-tri-in" d="M392 112 L576 336 L208 336 Z"/>'
        '<g class="prism-rays">' + rays + '</g>'
        '</svg>'
    )


def _arcade_art(display):
    number = f'<p class="aw-number">{e(display)}</p>' if display else ''
    return (
        '<div class="arcade-window">'
        '<div class="aw-bar"><i></i><i></i><i></i><span>invitation.session</span></div>'
        '<div class="aw-body">'
        '<p class="aw-line"><b>$</b> open invitation</p>'
        + number +
        '<p class="aw-line aw-dim">reading your folder…</p>'
        '<p class="aw-line aw-cursor"><b>&gt;</b> <span>invitation.ready</span><i class="aw-caret"></i></p>'
        '</div>'
        '<div class="aw-foot"><span>READY</span><span>01</span></div>'
        '</div>'
    )


def _editorial_art(display):
    return (
        '<div class="ed-card">'
        '<span class="ed-card-rule"></span>'
        '<p class="ed-card-kicker">AN INVITATION</p>'
        '<p class="ed-card-note">纸上 · 共创 · 相见</p>'
        '<span class="ed-card-seal" aria-hidden="true">邀</span>'
        '<span class="ed-card-rule ed-card-rule-short"></span>'
        '</div>'
    )


ART = {
    'harbor': _harbor_art,
    'arcade': _arcade_art,
    'neon': _neon_art,
    'midnight': _midnight_art,
    'prism': _prism_art,
    'editorial': _editorial_art,
}


def hero_figure(theme, display):
    art = ART[theme](display)
    disp = ''
    if display and theme != 'arcade':
        long = ' data-long="true"' if len(str(display)) > 5 else ''
        disp = f'<div class="art-display"{long} aria-hidden="true">{e(display)}</div>'
    return f'<div class="hero-figure" aria-hidden="true">{art}{disp}</div>'


# ---------------------------------------------------------------- blocks

def section_head(s, i):
    raw_title = str(s.get('title', ''))
    index = str(i).zfill(2)
    label = s.get('kicker') or ''
    kicker = f'<span>{e(label)}</span>' if label else ''
    return (
        '<header class="section-head">'
        f'<p class="section-index"><b>{index}</b>{kicker}</p>'
        f'<h2>{text(raw_title)}</h2>'
        + (f'<p class="section-lead">{text(s["lead"])}</p>' if s.get('lead') else '')
        + '</header>'
    )


def render_block(s, i):
    typ = s.get('type', 'paragraph')
    sid = slug(s.get('id') or f'section-{i}')
    head = section_head(s, i)
    body = ''

    if typ in ('highlights', 'benefits'):
        body = '<div class="facts' + (' benefit-facts' if typ == 'benefits' else '') + '">'
        for a in s.get('items', []):
            body += (
                '<article class="fact">'
                f'<b class="fact-value">{e(a.get("value", ""))}</b>'
                f'<h3>{text(a.get("label", ""))}</h3>'
                + (f'<p>{text(a["detail"])}</p>' if a.get('detail') else '')
                + '</article>'
            )
        body += '</div>'

    elif typ == 'prize':
        body = (
            '<div class="prize-plate">'
            '<p class="prize-kicker">MAIN AWARD</p>'
            f'<p class="prize-value"><b>{e(s.get("value", ""))}</b><span>{e(s.get("unit", ""))}</span></p>'
            f'<p class="prize-label">{text(s.get("label", ""))}</p>'
            + ('<ul class="prize-extra">' + ''.join(f'<li>{text(x)}</li>' for x in s.get('extras', [])) + '</ul>'
               if s.get('extras') else '')
            + '</div>'
        )

    elif typ == 'tracks':
        for n, a in enumerate(s.get('items', []), 1):
            rewards = ''.join(
                '<div class="rank">'
                f'<span class="rank-label">{e(r.get("rank", ""))}</span>'
                f'<b>{e(r.get("cash", ""))}</b>'
                + (f'<p>{text(r["extra"])}</p>' if r.get('extra') else '')
                + '</div>'
                for r in a.get('rewards', [])
            )
            body += (
                f'<details class="track"{" open" if n == 1 else ""}>'
                '<summary>'
                f'<span class="track-index">{str(n).zfill(2)}</span>'
                f'<span class="track-title"><b>{text(a.get("name", ""))}</b>'
                + (f'<small>{text(a["sponsor"])}</small>' if a.get('sponsor') else '')
                + '</span><span class="track-toggle" aria-hidden="true"></span>'
                '</summary>'
                '<div class="track-body">'
                + (f'<p class="track-tagline">{text(a["tagline"])}</p>' if a.get('tagline') else '')
                + (f'<div class="ranks">{rewards}</div>' if rewards else '')
                + ('<ul class="track-list">' + li(a.get('details', [])) + '</ul>' if a.get('details') else '')
                + '</div></details>'
            )

    elif typ == 'partners':
        body = '<div class="partner-groups">'
        for g in s.get('groups', []):
            body += (
                '<div class="partner-group">'
                f'<span class="partner-label">{e(g.get("label", ""))}</span>'
                '<p>' + ''.join(f'<b>{e(n)}</b>' for n in g.get('names', [])) + '</p></div>'
            )
        body += '</div>'

    elif typ == 'rules':
        body = '<div class="rules">'
        for a in s.get('items', []):
            body += (
                '<article class="rule">'
                f'<h3>{text(a.get("title", ""))}</h3>'
                f'<p>{text(a.get("body", ""))}</p></article>'
            )
        body += '</div>'

    elif typ == 'timeline':
        body = '<div class="timeline">'
        for n, d in enumerate(s.get('days', []), 1):
            body += (
                '<article class="day">'
                '<header class="day-head">'
                f'<b class="day-date">{e(d.get("date", ""))}</b>'
                '<div class="day-title">'
                f'<span class="day-tag">DAY {str(n).zfill(2)}</span>'
                f'<p>{text(d.get("title", ""))}</p>'
                '</div></header>'
                '<ol class="day-list">'
                + ''.join(
                    f'<li><time>{e(a.get("time", ""))}</time><div><h3>{text(a.get("title", ""))}</h3>'
                    + (f'<p>{text(a["detail"])}</p>' if a.get('detail') else '')
                    + '</div></li>'
                    for a in d.get('items', [])
                )
                + '</ol></article>'
            )
        body += '</div>'

    elif typ == 'faq':
        body = '<div class="questions">'
        for a in s.get('items', []):
            body += (
                f'<details class="question"><summary>{text(a.get("question", ""))}'
                '<span class="q-toggle" aria-hidden="true"></span></summary>'
                f'<p>{text(a.get("answer", ""))}</p></details>'
            )
        body += '</div>'

    elif typ == 'quote':
        body = (
            '<figure class="pullquote"><blockquote>'
            + text(s.get('body', ''))
            + '</blockquote>'
            + (f'<figcaption>{text(s["cite"])}</figcaption>' if s.get('cite') else '')
            + '</figure>'
        )

    else:
        body = ('<p class="prose">' + text(s.get('body', '')) + '</p>') + (
            '<ul class="prose-list">' + li(s.get('items', [])) + '</ul>' if s.get('items') else ''
        )

    return f'<section class="content-section sec-{typ}" id="{sid}" data-reveal>{head}{body}</section>'


def render_signup(config, mode, external, cta_label):
    title = config.get('closing_title') or '为你的想法，留一个位置。'
    copy = config.get('closing_copy') or '期待与你相遇。'
    out = (
        '<section class="signup" id="enroll" data-reveal>'
        '<div class="signup-inner">'
        '<p class="section-index"><b>JOIN</b><span>报名</span></p>'
        f'<h2 class="signup-title">{text(title)}</h2>'
        f'<p class="signup-copy">{text(copy)}</p>'
    )
    if mode == 'external':
        steps = config.get('registration_steps') or []
        if steps:
            out += '<ol class="signup-steps">' + ''.join(
                f'<li><span>{str(n).zfill(2)}</span>{text(a)}</li>' for n, a in enumerate(steps, 1)
            ) + '</ol>'
        if external:
            out += (
                f'<a class="button button-primary" id="official-register" href="{e(external)}" '
                'target="_blank" rel="noopener noreferrer">'
                f'<span>{e(cta_label)}</span><i class="btn-arrow" aria-hidden="true"></i></a>'
                f'<p class="registration-host">{e(urlparse(external).netloc)}</p>'
            )
        else:
            out += '<button class="button" disabled>报名入口待配置</button>'
    else:
        out += (
            '<form id="enrollForm"><div class="form-grid">'
            '<label>姓名<input name="name" required autocomplete="name" maxlength="40"></label>'
            '<label>单位<input name="company" autocomplete="organization" maxlength="100"></label>'
            '<label>职务<input name="title" autocomplete="organization-title" maxlength="80"></label>'
            '<label>手机号码<input name="phone" type="tel" inputmode="tel" autocomplete="tel" required pattern="1[0-9]{10}" maxlength="11"></label>'
            '<label>参会人数<input name="count" type="number" min="1" max="100" value="1" required></label>'
            '<label class="form-wide">备注<textarea name="note" rows="3" maxlength="1000"></textarea></label>'
            '</div>'
            '<button class="button button-primary" type="submit"><span>提交报名</span><i class="btn-arrow" aria-hidden="true"></i></button>'
            '<p class="form-status" id="formStatus" role="status" aria-live="polite"></p></form>'
        )
    return out + '</div></section>'


def render_envelope(title, date):
    return (
        '<div class="envelope-overlay" id="invitation-envelope" hidden>'
        '<div class="envelope-scene" role="dialog" aria-modal="true" aria-labelledby="envelope-title">'
        '<p class="envelope-eyebrow">A LETTER FOR YOU</p>'
        '<h2 id="envelope-title">你有一封<br>特别的邀请</h2>'
        '<div class="envelope-art">'
        '<div class="env-shadow"></div>'
        f'<div class="env-letter"><span class="env-letter-rule"></span><b>{e(title)}</b><i>{e(date)}</i></div>'
        '<div class="env-flap"></div>'
        '<div class="env-front"><span class="env-fold"></span></div>'
        '<button id="open-invitation" class="seal" aria-label="打开邀请函"><span>启</span></button>'
        '</div>'
        '<button class="envelope-skip" id="skip-envelope">直接查看活动</button>'
        '</div></div>'
    )


def render_invitation(config):
    if not isinstance(config, dict):
        raise ValueError('Invitation config must be a dictionary')
    theme = config.get('theme', 'neon')
    t = THEMES.get(theme)
    if not t:
        raise ValueError('Unknown invitation theme: ' + str(theme))

    title = str(config.get('title') or '诚邀相聚')
    hero = config.get('hero') or {}
    display = hero.get('display', '')
    lines = title_lines(hero, title)
    sections = config.get('sections') or []
    if not isinstance(sections, list):
        raise ValueError('sections must be a list')

    mode = config.get('registration_mode', 'local')
    if mode not in ('external', 'local'):
        raise ValueError('registration_mode must be external or local')
    external = url(config.get('registration_url'))
    event_slug = slug(config.get('event_slug') or config.get('slug') or title)

    css = (Path(__file__).parent / 'assets/invitation.css').read_text(encoding='utf-8')
    js = (Path(__file__).parent / 'assets/invitation.js').read_text(encoding='utf-8')
    tokens = ':root{' + ''.join(
        '--' + k.replace('_', '-') + ':' + v + ';' for k, v in t.items() if k in TOKEN_KEYS
    ) + '}'

    metadata = ''.join(
        f'<div><dt>{label}</dt><dd>{text(config.get(key, ""))}</dd></div>'
        for key, label in [('date', '时间'), ('location', '地点')] if config.get(key)
    )
    cta_label = config.get('registration_label') or ('前往官网报名' if mode == 'external' else '预约参与')

    allsections = ''.join(render_block(s, i) for i, s in enumerate(sections, 1))
    navsections = [s for s in sections if s.get('nav')]
    nav = ''.join(
        '<a href="#' + slug(s.get('id') or 'section-' + str(sections.index(s) + 1)) + '">' + e(s['nav']) + '</a>'
        for s in navsections[:3]
    )
    brand = config.get('brand') or 'NICO INVITATION'

    footer = (
        '<footer class="endnote"><div class="endnote-mark" aria-hidden="true"></div>'
        + (f'<p class="endnote-organizer">{text(config["organizer"])}</p>' if config.get('organizer') else '')
        + (f'<p>{text(config["price"])}</p>' if config.get('price') else '')
        + (f'<a href="tel:{e(re.sub(r"[^+0-9]", "", str(config["phone"])))}">咨询 {e(config["phone"])}</a>'
           if config.get('phone') else '')
        + f'<p class="endnote-line">{e(config.get("footer", "期待与你，在现场相见。"))}</p>'
        '<button id="replay-envelope" type="button">重新打开邀请函</button></footer>'
    )

    description = str(config.get('subtitle') or title)
    canonical = '<link rel="canonical" href="' + e(config['page_url']) + '">' if url(config.get('page_url')) else ''
    boot = json.dumps(
        dict(theme=theme, slug=event_slug, registrationMode=mode, apiUrl=config.get('api_url', ''), eventTitle=title),
        ensure_ascii=False,
    ).replace('<', '\\u003c')

    eyebrow = hero.get('eyebrow') or '诚邀相聚'
    stamp = hero.get('stamp') or 'INVITATION'
    hero_title = ''.join(f'<span class="tt-line"><i>{text(x)}</i></span>' for x in lines)

    html = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="{e(description)}">
<meta name="theme-color" content="{t['bg']}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}">
<meta property="og:type" content="website"><title>{e(title)} · 活动邀请函</title>{canonical}
<style>{tokens}{css}</style></head>
<body data-theme="{e(theme)}" data-motion="{'none' if config.get('motion') == 'none' else 'subtle'}" data-envelope="{'true' if config.get('envelope') else 'false'}">
<a class="skip-link" href="#content">跳到活动介绍</a>
<div class="reading-progress" aria-hidden="true"><i></i></div>
<header class="masthead"><a href="#cover" class="brand"><span class="brand-dot" aria-hidden="true"></span>{e(brand)}</a>
<div class="masthead-actions"><button type="button" id="motion-toggle" aria-pressed="false" aria-label="关闭轻动效">动效 开</button><a href="#enroll" class="masthead-cta">报名</a></div></header>
<main id="content">
<section class="hero" id="cover">
<div class="hero-field" aria-hidden="true"><span class="hf-grid"></span><span class="hf-light"></span><span class="hf-glow"></span></div>
<div class="hero-body">
<p class="hero-eyebrow"><span class="eb-rule" aria-hidden="true"></span><span class="eb-text">{e(eyebrow)}</span></p>
<h1 class="hero-title">{hero_title}</h1>
<p class="hero-copy">{text(config.get('subtitle', ''))}</p>
{hero_figure(theme, display)}
<dl class="hero-meta">{metadata}</dl>
{f'<p class="hero-statement">{text(hero["statement"])}</p>' if hero.get('statement') else ''}
<p class="hero-stamp" aria-hidden="true"><span>{e(stamp)}</span></p>
</div>
</section>
{allsections}
{render_signup(config, mode, external, cta_label)}
</main>
{footer}
<nav class="bottom-dock" aria-label="活动快捷导航"><div class="dock-links">{nav}</div><a class="dock-cta" href="#enroll"><span>{e(cta_label)}</span><i class="btn-arrow" aria-hidden="true"></i></a></nav>
{render_envelope(title, config.get('date', '')) if config.get('envelope') else ''}
<script>window.NICO_EVENT={boot};</script><script>{js}</script></body></html>'''
    return html
