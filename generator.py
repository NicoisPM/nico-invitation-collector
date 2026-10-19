#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
活动邀请函参数化脚手架与内容生成工具 (Generator CLI)
支持交互式向导模式与 JSON 配置文件模式，快速生成定制版 H5 邀请函。

使用方式：
1. 交互式向导：
   python generator.py

2. 命令行指定配置：
   python generator.py --config event.example.json

3. 命令行参数直接指定：
   python generator.py --theme red --envelope --title "深中高质量发展论坛" --output dist/invite.html
"""

import os
import sys
import json
import argparse
import re

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

THEME_MAP = {
    '1': ('red', '红色党建国资版（示例跨海通道）', 'nico-invitation-red-party.html', 'nico-invitation-red-party-envelope.html'),
    'red': ('red', '红色党建国资版（示例跨海通道）', 'nico-invitation-red-party.html', 'nico-invitation-red-party-envelope.html'),
    '2': ('green', '绿色青年生态版（五桂山）', 'nico-invitation-green-eco.html', 'nico-invitation-green-eco-envelope.html'),
    'green': ('green', '绿色青年生态版（五桂山）', 'nico-invitation-green-eco.html', 'nico-invitation-green-eco-envelope.html'),
    '3': ('hk', '维港夜景港澳版（香港天际线）', 'nico-invitation-hk-skyline.html', 'nico-invitation-hk-skyline-envelope.html'),
    'hk': ('hk', '维港夜景港澳版（香港天际线）', 'nico-invitation-hk-skyline.html', 'nico-invitation-hk-skyline-envelope.html'),
    '4': ('default', '典雅金调标准版（暖纸烫金）', 'nico-invitation-framework.html', 'nico-invitation-envelope.html'),
    'default': ('default', '典雅金调标准版（暖纸烫金）', 'nico-invitation-framework.html', 'nico-invitation-envelope.html'),
}

OUTPUT_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

def render_nico_invitation(theme='red', envelope=True, config_data=None, output_path=None):
    if config_data is None:
        config_data = {}

    theme_info = THEME_MAP.get(str(theme).lower(), THEME_MAP['red'])
    slug, name, plain_file, env_file = theme_info
    
    src_filename = env_file if envelope else plain_file
    src_path = os.path.join(TEMPLATES_DIR, src_filename)

    if not os.path.exists(src_path):
        print(f"❌ 错误: 找不到模板源文件 {src_path}")
        return False

    with open(src_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 替换规则映射
    title = config_data.get('title', '')
    subtitle = config_data.get('subtitle', '')
    date_str = config_data.get('date', '')
    location = config_data.get('location', '')
    organizer = config_data.get('organizer', '')
    price = config_data.get('price', '')
    phone = config_data.get('phone', '')

    # ==================== 产出隔离规则：严禁污染 templates 目录 ====================
    import time
    timestamp_slug = time.strftime('%Y%m%d_%H%M%S')
    folder_name = re.sub(r'[^\w\u4e00-\u9fa5_-]', '_', title)[:30] if title else f'{slug}_{timestamp_slug}'
    if not folder_name:
        folder_name = f'invite_{timestamp_slug}'

    # 如果未指定 output_path，默认创建独立专属目录：output/<folder_name>/index.html
    if not output_path:
        project_dir = os.path.join(OUTPUT_BASE_DIR, folder_name)
        output_path = os.path.join(project_dir, 'index.html')
    else:
        # 安全防御：严禁写入 templates 目录
        abs_target = os.path.abspath(output_path)
        if abs_target.startswith(os.path.abspath(TEMPLATES_DIR)):
            print("⚠️ [安全防御生效] 严禁直接修改或覆盖 templates/ 模板目录！已自动重定向至 output/ 专属目录。")
            project_dir = os.path.join(OUTPUT_BASE_DIR, folder_name)
            output_path = os.path.join(project_dir, 'index.html')
        elif not os.path.isabs(output_path) and not output_path.startswith(('output', 'dist')):
            # 如果是相对文件名，默认统一归入 output/<folder_name>/
            project_dir = os.path.join(OUTPUT_BASE_DIR, folder_name)
            output_path = os.path.join(project_dir, os.path.basename(output_path))
        else:
            project_dir = os.path.dirname(os.path.abspath(output_path))

    os.makedirs(project_dir, exist_ok=True)
    price = config_data.get('price')
    phone = config_data.get('phone')

    # 1. 如果模板中存在直接的占位符 {{...}}
    replacements = {
        '{{活动标题}}': title,
        '{{主标题}}': title,
        '{{副标题}}': subtitle,
        '{{时间}}': date_str,
        '{{活动时间}}': date_str,
        '{{地点}}': location,
        '{{活动地点}}': location,
        '{{主办方}}': organizer,
        '{{主办单位}}': organizer,
        '{{费用说明}}': price,
        '{{咨询电话}}': phone,
    }

    for k, v in replacements.items():
        if v:
            html = html.replace(k, v)

    # 2. 如果模板中已有之前设定的具象文本，根据主题精准替换关键字段
    if title:
        # 替换标题
        html = re.sub(r'(<h1[^>]*>).*?(</h1>)', r'\g<1>' + title + r'\g<2>', html, count=1, flags=re.DOTALL)
        html = re.sub(r'(<title>).*?(</title>)', r'\g<1>' + title + r'\g<2>', html, count=1, flags=re.DOTALL)
    
    if subtitle:
        # 替换副标题标语
        html = re.sub(r'(class="[^"]*tracking-[^"]*text-gold-700[^"]*">).*?(</p>)', r'\g<1>' + subtitle + r'\g<2>', html, count=1)

    if date_str:
        html = re.sub(r'(活动时间：</span><span[^>]*>).*?(</span>)', r'\g<1>' + date_str + r'\g<2>', html, count=1)

    if location:
        html = re.sub(r'(活动地点：</span><span[^>]*>).*?(</span>)', r'\g<1>' + location + r'\g<2>', html, count=1)

    if price:
        html = re.sub(r'(报名费用：<span[^>]*>).*?(</span>)', r'\g<1>' + price + r'\g<2>', html, count=1)

    # 3. 动态替换导师/嘉宾阵容 (若配置中提供了 speakers 列表)
    speakers = config_data.get('speakers')
    if speakers and isinstance(speakers, list) and len(speakers) > 0:
        spk_items = []
        for idx, spk in enumerate(speakers[:4]):
            spk_name = spk.get('name', f'嘉宾 {idx+1}')
            spk_title = spk.get('title', '')
            spk_tag = spk.get('tag', '特邀嘉宾')
            spk_desc = spk.get('desc', '')
            num_str = f"0{idx+1}"
            border_pt = 'border-t border-line-soft pt-1.5' if idx > 0 else ''
            delay = f'style="transition-delay: {idx * 30}ms;"' if idx > 0 else ''
            spk_items.append(f'''
                    <div class="reveal {border_pt}" {delay}>
                      <div class="flex items-center justify-between">
                        <div class="flex items-baseline gap-2">
                          <span class="tnum font-serif text-[16px] font-bold text-gold-700">{num_str}</span>
                          <h3 class="font-serif text-[18px] sm:text-[19px] font-bold text-ink-900 leading-none">{spk_name}</h3>
                        </div>
                        <span class="border border-gold-400/80 bg-gold-50/50 px-2 py-[1px] text-[10.5px] font-medium tracking-[0.08em] text-gold-800">{spk_tag}</span>
                      </div>
                      <p class="mt-0.5 text-[13px] font-semibold leading-[1.35] text-ink-900">{spk_title}</p>
                      <p class="mt-0.5 text-[12px] leading-[1.42] text-ink-700">{spk_desc}</p>
                    </div>''')
        
        new_speakers_block = '<div class="flex flex-1 flex-col justify-between gap-2.5 sm:gap-3">' + ''.join(spk_items) + '\n                  </div>'
        html = re.sub(
            r'<section id="speakers".*?<div class="w-full fit-inner flex-1 flex flex-col">\s*<div class="flex flex-1 flex-col justify-between[^>]*>.*?</div>\s*<p class="mt-2\.5 text-\[11\.5px\]',
            lambda m: m.group(0).split('<div class="flex flex-1 flex-col justify-between')[0] + new_speakers_block + '\n\n                  <p class="mt-2.5 text-[11.5px]',
            html,
            flags=re.DOTALL
        )

    # 4. 自动化 DOM 结构安全校验与自愈防护（杜绝任何 section 标签嵌套导致的吸附滑动异常）
    open_sec_count = len(re.findall(r'<section\b', html))
    close_sec_count = len(re.findall(r'</section>', html))
    if open_sec_count != close_sec_count:
        print(f"⚠️ [DOM 防护预警] 检测到 section 标签不闭合 (open: {open_sec_count}, close: {close_sec_count})，启动自动修复...")
        # 针对常见在 cover 底部误闭合情况进行平滑校正
        html = re.sub(r'(</section>\s*)+</section>(\s*<footer)', r'</section>\2', html)
        # 再次复核
        new_open = len(re.findall(r'<section\b', html))
        new_close = len(re.findall(r'</section>', html))
        if new_open == new_close:
            print("✅ [DOM 防护完成] section 标签层级已自动修复闭合平衡！")
        else:
            print(f"ℹ️ [DOM 状态] 当前校验结果: open={new_open}, close={new_close}")

    # 确保输出目录存在
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    # 隔离规则配套：同步保存 event.json 到专属目录，便于打包交付与回溯
    event_json_path = os.path.join(out_dir, 'event.json')
    try:
        with open(event_json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'theme': slug,
                'envelope': envelope,
                **config_data,
                'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        pass

    print("\n" + "="*56)
    print(f"🎉 邀请函成功生成！(已完全隔离至独立产出目录)")
    print(f"📌 所用主题: {name}")
    print(f"✉️  信封形态: {'【3D撕火漆开信封版】' if envelope else '【直接进入版】'}")
    print(f"📁 专属目录: {os.path.abspath(out_dir)}")
    print(f"📄 页面路径: {os.path.abspath(output_path)}")
    print(f"📋 参数备份: {os.path.abspath(event_json_path)}")
    print(f"💡 预览方式: 双击打开，或运行 `node server.js` 启动全栈测试！")
    print("="*56 + "\n")
    return True

def interactive_wizard():
    print("\n" + "="*58)
    print("✨ 欢迎使用「活动邀请函 + 报名信息收集」脚手架向导 ✨")
    print("="*58)
    
    print("\n【步骤 1/4】请选择视觉设计主题：")
    print("  [1] 红色党建国资版（示例跨海通道海景 · 庄重宏大）")
    print("  [2] 绿色青年生态版（五桂山清新水墨 · 活力创新）")
    print("  [3] 维港夜景港澳版（香港天际线深蓝 · 国际高端）")
    print("  [4] 典雅金调标准版（暖纸烫金宣纸 · 通用政商）")
    
    choice = input("👉 请输入序号 (1-4，默认 1): ").strip() or "1"
    
    print("\n【步骤 2/4】是否需要 3D 撕火漆开信封动画？")
    print("  • 信封版：含物理撕纸音效、手势触发 BGM、180°翻折封盖与专属火漆（强仪式感）")
    print("  • 直入版：免拆封，加载即刻呈现卷首（高效直接）")
    env_choice = input("👉 开启信封动画吗？[Y/n，默认 Y]: ").strip().lower()
    envelope = False if env_choice == 'n' else True

    print("\n【步骤 3/4】请输入活动核心信息（直接回车使用示例默认值）：")
    title = input("• 活动主标题 [默认: 2026大湾区国资党建与产业高质量发展论坛]: ").strip() or "2026大湾区国资党建与产业高质量发展论坛"
    subtitle = input("• 副标题/标语 [默认: 深中协同 · 智领未来 · 赋能新质生产力]: ").strip() or "深中协同 · 智领未来 · 赋能新质生产力"
    date_str = input("• 活动时间 [默认: 2026年10月28日 09:00 - 17:30]: ").strip() or "2026年10月28日 09:00 - 17:30"
    location = input("• 活动地点 [默认: 示例市高新区国际会议中心]: ").strip() or "示例市高新区国际会议中心"
    organizer = input("• 主办单位 [默认: 示例科技集团]: ").strip() or "示例科技集团"
    price = input("• 报名费用 [默认: 免费预约（限额审核）]: ").strip() or "免费预约（限额审核）"

    print("\n【步骤 4/4】输出设置（遵循成果隔离铁律，默认保存至独立目录）：")
    out_file = input("• 输出路径 [回车默认: output/<活动名称>/index.html]: ").strip() or None

    config_data = {
        'title': title,
        'subtitle': subtitle,
        'date': date_str,
        'location': location,
        'organizer': organizer,
        'price': price,
    }

    render_nico_invitation(theme=choice, envelope=envelope, config_data=config_data, output_path=out_file)

def main():
    parser = argparse.ArgumentParser(description="H5 邀请函生成工具")
    parser.add_argument('--config', type=str, help="指定 JSON 配置文件路径")
    parser.add_argument('--theme', type=str, choices=['red', 'green', 'hk', 'default', '1', '2', '3', '4'], default='red', help="主题风格")
    parser.add_argument('--envelope', action='store_true', default=None, help="启用 3D 信封动画")
    parser.add_argument('--no-envelope', action='store_true', help="禁用 3D 信封动画")
    parser.add_argument('--title', type=str, help="活动标题")
    parser.add_argument('--subtitle', type=str, help="活动副标题")
    parser.add_argument('--date', type=str, help="活动时间")
    parser.add_argument('--location', type=str, help="活动地点")
    parser.add_argument('--organizer', type=str, help="主办单位")
    parser.add_argument('--price', type=str, help="报名费用说明")
    parser.add_argument('--output', '-o', type=str, default=None, help="输出 HTML 文件路径 (默认创建独立目录 output/<活动名>/index.html)")

    args = parser.parse_args()

    # 如果没有传递任何参数，默认进入交互式向导
    if len(sys.argv) == 1:
        interactive_wizard()
        return

    config_data = {}
    if args.config:
        if os.path.exists(args.config):
            with open(args.config, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        else:
            print(f"❌ 找不到配置文件: {args.config}")
            return

    # 命令行覆盖 JSON 参数
    if args.title: config_data['title'] = args.title
    if args.subtitle: config_data['subtitle'] = args.subtitle
    if args.date: config_data['date'] = args.date
    if args.location: config_data['location'] = args.location
    if args.organizer: config_data['organizer'] = args.organizer
    if args.price: config_data['price'] = args.price

    theme = config_data.get('theme', args.theme)
    envelope = True
    if args.no_envelope:
        envelope = False
    elif args.envelope:
        envelope = True
    elif 'envelope' in config_data:
        envelope = bool(config_data['envelope'])

    output = args.output or config_data.get('output', 'my-nico-invitation.html')

    render_nico_invitation(theme=theme, envelope=envelope, config_data=config_data, output_path=output)

if __name__ == '__main__':
    main()
