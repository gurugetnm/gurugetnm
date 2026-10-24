#!/usr/bin/env python3
"""Refresh public GitHub snapshots and prepare locally generated snake SVGs.

Python standard library only. Network failures leave existing assets intact.
The repository list is public-only and excludes forks; languages count each
repository's primary language, not lines of code, proficiency, or time spent.
"""
from collections import Counter
from datetime import datetime, timezone
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'profile'
USER = 'gurugetnm'


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'gurugetnm-profile-assets', 'Accept': 'application/vnd.github+json' if 'api.github.com' in url else 'text/html'})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode()


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'td' and 'data-date' in attrs and 'data-level' in attrs:
            level = int(attrs['data-level'])
            if level not in range(5):
                raise ValueError('Unexpected contribution level')
            self.days[attrs['data-date']] = level


def parse_calendar(html):
    parser = CalendarParser()
    parser.feed(html)
    total = re.search(r'([\d,]+)\s+contributions\s+in the last year', html)
    if not total or len(parser.days) < 350:
        raise ValueError('GitHub calendar format changed; keeping previous snapshots')
    return int(total.group(1).replace(',', '')), sorted(parser.days.items())


def svg(width, height, title, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img"><title>{escape(title)}</title><style>text{{font-family:Arial,Helvetica,sans-serif}}</style>{body}</svg>\n'


def render(repos, total, days, stamp):
    langs = Counter(r['language'] for r in repos if r['language'])
    outputs = {}
    for mode in ['dark', 'light']:
        dark = mode == 'dark'
        bg, fg, muted, border = ('#0b1020', '#f5f3ff', '#aab4cf', '#25304c') if dark else ('#f4f5ff', '#192342', '#556080', '#d8def0')
        accent = '#a78bfa' if dark else '#6d28d9'
        cyan = '#22d3ee' if dark else '#08778c'
        base = f'<rect x="1" y="1" width="358" height="218" rx="16" fill="{bg}" stroke="{border}"/>'
        body = base + f'<text x="22" y="32" fill="{accent}" font-size="11" letter-spacing="1.8">GITHUB / ACTIVITY SNAPSHOT</text><text x="22" y="91" fill="{fg}" font-size="46" font-weight="700">{total:,}</text><text x="22" y="116" fill="{muted}" font-size="13">contributions · GitHub’s last-year calendar</text><path d="M22 139H338" stroke="{border}"/><text x="22" y="173" fill="{cyan}" font-size="25" font-weight="700">{len(repos)}</text><text x="64" y="171" fill="{muted}" font-size="13">public non-fork repositories</text><text x="22" y="202" fill="{muted}" font-size="11">Snapshot: {stamp} UTC · Not a live counter</text>'
        outputs[f'stats-{mode}.svg'] = svg(360, 220, f'{total:,} contributions on the public GitHub last-year calendar; {len(repos)} public non-fork repositories. Snapshot {stamp} UTC.', body)
        body = base + f'<text x="22" y="32" fill="{accent}" font-size="11" letter-spacing="1.8">REPOSITORIES / PRIMARY LANGUAGE</text>'
        palette = [accent, cyan, '#60a5fa' if dark else '#2563eb', '#34d399' if dark else '#047857', '#c084fc' if dark else '#9333ea']
        for i, (language, count) in enumerate(langs.most_common(5)):
            y = 62 + i * 27
            body += f'<text x="22" y="{y}" fill="{fg}" font-size="12">{escape(language)}</text><rect x="150" y="{y-9}" width="160" height="7" rx="3.5" fill="{border}"/><rect x="150" y="{y-9}" width="{160*count/max(langs.values()):.1f}" height="7" rx="3.5" fill="{palette[i]}"/><text x="337" y="{y}" text-anchor="end" fill="{muted}" font-size="12">{count}</text>'
        body += f'<text x="22" y="202" fill="{muted}" font-size="11">Repository counts, not code share · {stamp}</text>'
        outputs[f'languages-{mode}.svg'] = svg(360, 220, 'Public non-fork repositories by primary language: '+', '.join(f'{k}: {v}' for k,v in langs.most_common())+f'. Snapshot {stamp}.', body)
        # Genuine static calendar used for reduced motion, and as a stable fallback.
        colors = ['#151d32','#2e2254','#5a3693','#8b5cf6','#c4b5fd'] if dark else ['#e8eaf2','#ddd6fe','#a78bfa','#8b5cf6','#6d28d9']
        body = f'<rect x="1" y="1" width="878" height="188" rx="16" fill="{bg}" stroke="{border}"/><text x="22" y="27" fill="{accent}" font-size="12" letter-spacing="1.5">CONTRIBUTION CALENDAR</text>'
        first = datetime.fromisoformat(days[0][0]).date()
        for date, level in days:
            day = datetime.fromisoformat(date).date()
            weekday = (day.weekday()+1)%7
            x = 22 + ((day-first).days+(first.weekday()+1)%7)//7*15.8
            y = 44 + weekday*15
            body += f'<rect x="{x:.1f}" y="{y}" width="12" height="12" rx="3" fill="{colors[level]}"><title>{date}: contribution intensity {level} of 4</title></rect>'
        body += f'<text x="22" y="171" fill="{muted}" font-size="12">{days[0][0]} — {days[-1][0]} · GitHub public calendar · Snapshot {stamp}</text>'
        outputs[f'calendar-{mode}.svg'] = svg(880,190,'Static contribution calendar. '+f'{total:,} contributions in the GitHub last-year period. Snapshot {stamp}.',body)
    return outputs


def main():
    repos = []
    for page in range(1, 20):
        batch = json.loads(fetch(f'https://api.github.com/users/{USER}/repos?per_page=100&page={page}'))
        if not isinstance(batch, list):
            raise ValueError('Unexpected GitHub API response')
        repos.extend(r for r in batch if not r['fork'] and not r['private'])
        if len(batch) < 100:
            break
    else:
        raise ValueError('Pagination limit reached; refusing incomplete statistics')
    total, days = parse_calendar(fetch(f'https://github.com/users/{USER}/contributions'))
    stamp = datetime.now(timezone.utc).date().isoformat()
    outputs = render(repos, total, days, stamp)
    for mode in ['dark','light']:
        path = OUT/f'snake-{mode}.svg'
        if path.exists():
            content = path.read_text()
            existing_title = re.search(r'<title>(Animated snake traversing.*?)</title>', content, re.S)
            snake_title = existing_title.group(1) if existing_title else f'Animated snake traversing gurugetnm’s GitHub contribution calendar. Generated {stamp} UTC.'
            content = re.sub(r'<title>.*?</title>', '', content, flags=re.S)
            content = re.sub(r'<desc>.*?</desc>', '', content, flags=re.S)
            content = re.sub(r'<style id="profile-motion">.*?</style>', '', content, flags=re.S)
            end = content.index('>') + 1
            content = content[:end] + f'<title>{snake_title}</title><desc>Decorative traversal of actual contribution intensity; not a live activity indicator.</desc><style id="profile-motion">@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>' + content[end:]
            outputs[path.name] = content
    for name, content in outputs.items():
        ET.fromstring(content)
    OUT.mkdir(parents=True, exist_ok=True)
    for name, content in outputs.items():
        temporary = OUT/(name+'.tmp')
        temporary.write_text(content)
        temporary.replace(OUT/name)
    snapshot = {'fetched_at_utc': datetime.now(timezone.utc).isoformat(), 'user': USER, 'contributions_last_year': total, 'calendar_start': days[0][0], 'calendar_end': days[-1][0], 'public_nonfork_repositories': len(repos), 'primary_language_repository_counts': dict(Counter(r['language'] for r in repos if r['language'])), 'sources': [f'https://api.github.com/users/{USER}/repos', f'https://github.com/users/{USER}/contributions']}
    (OUT/'snapshot.json').write_text(json.dumps(snapshot, indent=2)+'\n')
    print(f'Refreshed {len(outputs)} SVG assets from public GitHub data ({stamp}).')


if __name__ == '__main__':
    main()
