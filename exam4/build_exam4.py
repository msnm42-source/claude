# -*- coding: utf-8 -*-
"""가락중 2026학년도 2학기 중간고사 1학년 수학 원본 시험지 복원.

원본 스캔(1415x2000px)의 좌표를 그대로 써서 문항과 그림을 배치하고,
그림은 모두 SVG로 새로 그린 뒤 Chromium으로 A4 PDF를 만든다.
  python3 exam4/build_exam4.py
"""
import math
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------ 좌표 변환
# 각 면 스캔에서 바깥 테두리의 (왼쪽, 위, 오른쪽, 아래) 픽셀 위치
FRAMES = {1: (65, 88, 1342, 1916), 2: (86, 68, 1361, 1896), 3: (88, 96, 1319, 1854),
          4: (86, 107, 1318, 1865), 5: (88, 77, 1365, 1907)}
FL, FT, FW, FH = 10.5, 12.0, 189.0, 264.0  # 출력 테두리(mm)


def X(pg, x):
    x0, _, x1, _ = FRAMES[pg]
    return FL + (x - x0) / (x1 - x0) * FW


def Y(pg, y):
    _, y0, _, y1 = FRAMES[pg]
    return FT + (y - y0) / (y1 - y0) * FH


def S(pg):
    x0, y0, x1, y1 = FRAMES[pg]
    return (FW / (x1 - x0) + FH / (y1 - y0)) / 2  # mm per px


COL = {'L': (FL + 2.5, FL + FW / 2 - 2.3), 'R': (FL + FW / 2 + 2.6, FL + FW - 2.3)}
LH = 6.4  # 본문 줄 높이(mm)


# ------------------------------------------------------------ 글자 표기
def fmt(s):
    """$...$ 안: 수식(세리프). [AB] 선분, {AB} 반직선, ~AB~ 직선, _P_ 기울임,
    한 글자 소문자는 자동 기울임, ^2 위첨자."""
    def math_run(mo):
        t = mo.group(1)
        t = t.replace('=', '\x01').replace('≡', '\x02')
        t = re.sub(r'(?<![A-Za-z])([a-z])(?![A-Za-z])', lambda mo: '\x03' + mo.group(1) + '\x04', t)
        t = re.sub(r'\[([^\]]+)\]', r'<span class="ov">\1</span>', t)
        t = re.sub(r'\{([^}]+)\}', r'<span class="ray">\1</span>', t)
        t = re.sub(r'~([^~]+)~', r'<span class="lin">\1</span>', t)
        t = re.sub(r'_([^_]+)_', r'<i>\1</i>', t)
        t = re.sub(r'\^(\w)', r'<sup>\1</sup>', t)
        t = t.replace('\x03', '<i>').replace('\x04', '</i>')
        t = t.replace('\x01', '<span class="op">=</span>').replace('\x02', '<span class="op">≡</span>')
        return f'<span class="m">{t}</span>'
    return re.sub(r'\$([^$]+)\$', math_run, s)


def fr(n, d):
    """분수(본문용)"""
    return (f'<span class="fr"><span class="fn">{fmt("$" + str(n) + "$")}</span>'
            f'<span class="fd">{fmt("$" + str(d) + "$")}</span></span>')


def place(pg, x_mm, y_mm, html, w=None, cls=''):
    ws = f'width:{w:.2f}mm;' if w else ''
    return f'<div class="abs {cls}" style="left:{x_mm:.2f}mm;top:{y_mm:.2f}mm;{ws}">{html}</div>'


def lines(pg, col, ys, texts, first_indent=0, cls='q', ind2=5.6):
    """원본 줄바꿈 그대로: 각 줄을 따로 두고 마지막 줄 외에는 양쪽 정렬.
    '>>' 오른쪽 정렬, '<<' 왼쪽 정렬 강제."""
    l, r = COL[col]
    out = []
    for i, (yy, t) in enumerate(zip(ys, texts)):
        last = (i == len(texts) - 1)
        ind = first_indent if i == 0 else ind2
        just = 'jl' if last else 'jj'
        if t.startswith('>>'):
            t, just = t[2:], 'jr'
        elif t.startswith('<<'):
            t, just = t[2:], 'jl'
        out.append(place(pg, l + ind, Y(pg, yy) - LH / 2, fmt(t), w=r - l - ind, cls=f'{cls} {just}'))
    return ''.join(out)


def qlines(pg, col, ys, texts):
    num, rest = texts[0].split(' ', 1)
    l, r = COL[col]
    ind = 4.4 if len(num) < 3 else 5.6
    out = place(pg, l, Y(pg, ys[0]) - LH / 2, num, cls='qn')
    return out + lines(pg, col, ys, [rest] + texts[1:], first_indent=ind, ind2=ind)


MARK = '①②③④⑤'


def choices(pg, col, ys, items, ncol, indent=1.5):
    l, r = COL[col]
    w = r - l - indent
    out = []
    for i, t in enumerate(items):
        row, c = divmod(i, ncol)
        cx = l + indent + c * w / ncol
        out.append(place(pg, cx, Y(pg, ys[row]) - LH / 2, f'<span class="cm">{MARK[i]}</span> {fmt(t)}', cls='ch'))
    return ''.join(out)


def choice_lines(pg, col, rows, indent=1.5):
    """긴 선택지: rows = [(y, 번호 or None, 텍스트)]  ('|'로 끝나면 양쪽 정렬)"""
    l, r = COL[col]
    out = []
    for yy, k, t in rows:
        just = ' jj' if t.endswith('|') else ''
        t = t.rstrip('|')
        if k is not None:
            out.append(place(pg, l + indent, Y(pg, yy) - LH / 2, MARK[k], cls='ch'))
        out.append(place(pg, l + indent + 5.4, Y(pg, yy) - LH / 2, fmt(t), w=r - l - indent - 5.4, cls='ch' + just))
    return ''.join(out)


def box_html(pg, x0, y0, x1, y1, inner, cls='box'):
    s = S(pg)
    return (f'<div class="abs {cls}" style="left:{X(pg, x0):.2f}mm;top:{Y(pg, y0):.2f}mm;'
            f'width:{(x1 - x0) * s:.2f}mm;height:{(y1 - y0) * s:.2f}mm">{inner}</div>')


def inbox(pg, x0, y0, rows, w=None):
    """상자 안 줄들: rows = [(x, y, text)] 또는 (x, y, text, 오른쪽x) (양쪽 정렬)"""
    s = S(pg)
    out = ''
    for row in rows:
        x, y, t = row[:3]
        if len(row) == 4:
            out += place(pg, (x - x0) * s, (y - y0) * s - LH / 2, fmt(t), w=(row[3] - x) * s, cls='bx jj')
        else:
            out += place(pg, (x - x0) * s, (y - y0) * s - LH / 2, fmt(t), cls='bx')
    return out


def bogi(pg, x0, y0, x1, y1, rows, title='&lt;보기&gt;'):
    t = f'<div class="bogi-t"><span>{title}</span></div>'
    return box_html(pg, x0, y0, x1, y1, t + inbox(pg, x0, y0, rows))


def cont(pg, y, text):
    l, r = COL['R']
    return place(pg, l, Y(pg, y) - LH / 2, text, w=r - l, cls='cont')


# ------------------------------------------------------------ 기하 도우미
def sub(p, q): return (p[0] - q[0], p[1] - q[1])
def add(p, q): return (p[0] + q[0], p[1] + q[1])
def mul(p, k): return (p[0] * k, p[1] * k)
def mid(p, q): return ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
def dist(p, q): return math.hypot(p[0] - q[0], p[1] - q[1])
def lerp(p, q, t): return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def unit(v):
    L = math.hypot(*v)
    return (v[0] / L, v[1] / L)


def foot(p, a, b):
    d = sub(b, a)
    t = ((p[0] - a[0]) * d[0] + (p[1] - a[1]) * d[1]) / (d[0] ** 2 + d[1] ** 2)
    return lerp(a, b, t)


def inter(p1, p2, p3, p4):
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def incenter(a, b, c):
    la, lb, lc = dist(b, c), dist(a, c), dist(a, b)
    s = la + lb + lc
    return ((la * a[0] + lb * b[0] + lc * c[0]) / s, (la * a[1] + lb * b[1] + lc * c[1]) / s)


def circumcenter(a, b, c):
    ax, ay = a; bx, by = b; cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return (ux, uy)


def ang(c, p):
    """c에서 p 방향의 각(도, 반시계, 화면 y는 아래)"""
    return math.degrees(math.atan2(-(p[1] - c[1]), p[0] - c[0]))


def polar(c, r, deg):
    return (c[0] + r * math.cos(math.radians(deg)), c[1] - r * math.sin(math.radians(deg)))


# ------------------------------------------------------------ SVG 도우미
SW = 1.7


def ln(p, q, sw=SW, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<line x1="{p[0]:.2f}" y1="{p[1]:.2f}" x2="{q[0]:.2f}" y2="{q[1]:.2f}" stroke="#000" '
            f'stroke-width="{sw}" stroke-linecap="round"{d}/>')


def pg_(pts, fill='none', sw=SW):
    d = ' '.join(f'{x:.2f},{y:.2f}' for x, y in pts)
    return f'<polygon points="{d}" fill="{fill}" stroke="#000" stroke-width="{sw}" stroke-linejoin="round"/>'


def tx(p, s, size=24, anchor='middle', italic=False):
    st = ' font-style="italic"' if italic else ''
    return (f'<text x="{p[0]:.2f}" y="{p[1]:.2f}" font-size="{size}" text-anchor="{anchor}" '
            f'dominant-baseline="central"{st}>{s}</text>')


def dot(p, r=3.2):
    return f'<circle cx="{p[0]:.2f}" cy="{p[1]:.2f}" r="{r}" fill="#000"/>'


def arc_pts(c, r, a1, a2, sw=1.2):
    """a1→a2 중 작은 쪽 각을 잇는 호"""
    sweep = (a2 - a1) % 360
    if sweep > 180:
        a1, a2 = a2, a1
        sweep = 360 - sweep
    p1, p2 = polar(c, r, a1), polar(c, r, a1 + sweep)
    return (f'<path d="M{p1[0]:.2f},{p1[1]:.2f} A{r},{r} 0 0 0 {p2[0]:.2f},{p2[1]:.2f}" fill="none" '
            f'stroke="#000" stroke-width="{sw}"/>')


def arc_at(c, p1, p2, r, sw=1.2):
    return arc_pts(c, r, ang(c, p1), ang(c, p2), sw)


def bis_dir(c, p1, p2):
    a1, a2 = ang(c, p1), ang(c, p2)
    sweep = (a2 - a1) % 360
    if sweep > 180:
        a1, sweep = a2, 360 - sweep
    return a1 + sweep / 2


def right(c, p1, p2, s=9):
    u, w = unit(sub(p1, c)), unit(sub(p2, c))
    a, b, d = add(c, mul(u, s)), add(c, add(mul(u, s), mul(w, s))), add(c, mul(w, s))
    return (f'<polyline points="{a[0]:.2f},{a[1]:.2f} {b[0]:.2f},{b[1]:.2f} {d[0]:.2f},{d[1]:.2f}" '
            f'fill="none" stroke="#000" stroke-width="1.1"/>')


def ticks(p, q, n=2, L=6, gap=3.2):
    m_, u = mid(p, q), unit(sub(q, p))
    nrm = (-u[1], u[0])
    out = ''
    for i in range(n):
        o = (i - (n - 1) / 2) * gap
        c = add(m_, mul(u, o))
        out += ln(add(c, mul(nrm, L)), sub(c, mul(nrm, L)), 1.1)
    return out


def arrowhead(tip, d, size=8, open_=True):
    u = unit(d)
    nrm = (-u[1], u[0])
    b = sub(tip, mul(u, size))
    p1, p2 = add(b, mul(nrm, size * 0.45)), sub(b, mul(nrm, size * 0.45))
    if open_:
        return (f'<polyline points="{p1[0]:.2f},{p1[1]:.2f} {tip[0]:.2f},{tip[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}" '
                f'fill="none" stroke="#000" stroke-width="1.2"/>')
    return f'<polygon points="{p1[0]:.2f},{p1[1]:.2f} {tip[0]:.2f},{tip[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}" fill="#000"/>'


def mid_arrow(p, q, t=0.5):
    return arrowhead(add(lerp(p, q, t), mul(unit(sub(q, p)), 4)), sub(q, p), 7)


def dash_bulge(p, q, k, dash='5,4'):
    m_, d = mid(p, q), sub(q, p)
    L = math.hypot(*d)
    c = (m_[0] + d[1] / L * k, m_[1] - d[0] / L * k)
    return (f'<path d="M{p[0]:.2f},{p[1]:.2f} Q{c[0]:.2f},{c[1]:.2f} {q[0]:.2f},{q[1]:.2f}" fill="none" '
            f'stroke="#000" stroke-width="1.1" stroke-dasharray="{dash}"/>')


def curve(p, c, q, sw=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<path d="M{p[0]:.2f},{p[1]:.2f} Q{c[0]:.2f},{c[1]:.2f} {q[0]:.2f},{q[1]:.2f}" fill="none" '
            f'stroke="#000" stroke-width="{sw}"{d}/>')


STIPPLE = ('<defs><pattern id="stip" width="7" height="7" patternUnits="userSpaceOnUse">'
           '<circle cx="1.2" cy="1.5" r="0.75" fill="#555"/><circle cx="4.6" cy="3.1" r="0.7" fill="#555"/>'
           '<circle cx="2.4" cy="5.6" r="0.65" fill="#555"/><circle cx="6.1" cy="6.2" r="0.6" fill="#555"/>'
           '</pattern></defs>')


def fig(pg, box, inner, defs=''):
    x0, y0, x1, y1 = box
    s = S(pg)
    return (f'<svg class="abs fig" style="left:{X(pg, x0):.2f}mm;top:{Y(pg, y0):.2f}mm;'
            f'width:{(x1 - x0) * s:.2f}mm;height:{(y1 - y0) * s:.2f}mm" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}" '
            f'xmlns="http://www.w3.org/2000/svg">{defs}{inner}</svg>')




def sfr(cx, cy, lead, n, d, trail='', size=22):
    """SVG 안 'y = n/d x' 꼴 표기. cx: 분수 가로 중심"""
    w = max(len(str(n)), len(str(d))) * size * 0.55 + 4
    s = (f'<text x="{cx - w / 2 - 3:.1f}" y="{cy:.1f}" font-size="{size}" text-anchor="end" '
         f'dominant-baseline="central">{lead}</text>')
    s += tx((cx, cy - size * 0.62), n, size, italic=str(n).isalpha())
    s += ln((cx - w / 2, cy), (cx + w / 2, cy), 1.1)
    s += tx((cx, cy + size * 0.68), d, size, italic=str(d).isalpha())
    if trail:
        s += tx((cx + w / 2 + 3, cy), trail, size, anchor='start', italic=True)
    return s


def lbl(p, s, size=22):
    """흰 배경을 깐 글자(점선 위 길이 표시용)"""
    w = len(s) * size * 0.55
    return (f'<rect x="{p[0] - w / 2 - 2:.1f}" y="{p[1] - size * 0.55:.1f}" width="{w + 4:.1f}" '
            f'height="{size * 1.1:.1f}" fill="#fff"/>') + tx(p, s, size)


def ti(p, s, size=24):
    return tx(p, s, size, italic=True)


def poly_path(pts):
    return 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in pts)


# ================================================================ 그림
def f3():
    O, k = (1025, 1075), 40.7
    s = ln((840, 1075), (1192, 1075), 1.3) + arrowhead((1199, 1075), (1, 0), 9, False)
    s += ln((1025, 1133), (1025, 866), 1.3) + arrowhead((1025, 859), (0, -1), 9, False)
    yl = lambda x: 1075 + 4 / 3 * (x - 1025)
    s += ln((864, yl(864)), (1068, yl(1068)), 1.7)
    P = (1025 - 3 * k, 1075 - 4 * k)
    s += ln(P, (1025, P[1]), 1.3, '6,4') + ln(P, (P[0], 1075), 1.3, '6,4')
    s += right((1025, P[1]), (1015, P[1]), (1025, P[1] + 10), 8) + right((P[0], 1075), (P[0], 1065), (P[0] + 10, 1075), 8)
    s += ti((1000, 872), 'y') + tx((1046, 913), '4') + tx((900, 1094), '−3') + tx((1003, 1097), 'O') + ti((1182, 1095), 'x')
    return fig(1, (830, 850, 1205, 1142), s)


def hyper(c, k, f, x0, x1, n=80):
    pts = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        pts.append((c[0] + x * k, c[1] - f(x) * k))
    return f'<path d="{poly_path(pts)}" fill="none" stroke="#000" stroke-width="1.6"/>'


def f5():
    O, k = (401.5, 574), 39
    P = lambda x, y: (O[0] + x * k, O[1] - y * k)
    clip = '<defs><clipPath id="c5"><rect x="205" y="362" width="400" height="350"/></clipPath></defs>'
    cv = '<g clip-path="url(#c5)">'
    cv += hyper(O, k, lambda x: -8 / x, -6, -0.8) + hyper(O, k, lambda x: -8 / x, 0.8, 6)
    cv += hyper(O, k, lambda x: 5 / x, 0.5, 6) + hyper(O, k, lambda x: 5 / x, -6, -0.5) + '</g>'
    s = cv + ln((205, 574), (598, 574), 1.3) + arrowhead((605, 574), (1, 0), 9, False)
    s += ln((401.5, 712), (401.5, 370), 1.3) + arrowhead((401.5, 363), (0, -1), 9, False)
    A, B, C = P(-2, 4), P(-2, -2.5), P(3.2, -2.5)
    s += ln(A, P(0, 4), 1.3, '6,4') + ln(A, B, 1.3, '6,4') + ln(B, C, 1.3, '6,4')
    s += right(P(0, 4), add(P(0, 4), (-10, 0)), add(P(0, 4), (0, 10)), 8)
    s += right(P(-2, 0), add(P(-2, 0), (0, -10)), add(P(-2, 0), (10, 0)), 8)
    s += right(B, add(B, (0, -10)), add(B, (10, 0)), 8)
    s += right(P(0, -2.5), add(P(0, -2.5), (-10, 0)), add(P(0, -2.5), (0, -10)), 8)
    s += sfr(270, 447, '<tspan font-style="italic">y</tspan> =', 'a', 'x') + sfr(540, 470, '<tspan font-style="italic">y</tspan> =', '5', 'x')
    s += tx((308, 412), 'A') + tx((415, 417), '4') + tx((306, 562), '−2') + tx((385, 589), 'O')
    s += tx((312, 682), 'B') + tx((537, 673), 'C') + ti((587, 586), 'x') + ti((388, 378), 'y')
    return fig(2, (195, 355, 612, 715), clip + s)


def f6():
    O, k = (410, 1381), 23
    A, B = (O[0] - 8 / 3 * k, O[1] - 4 * k), (O[0] + 20 / 3 * k, O[1] - 4 * k)
    s = f'<path d="{poly_path([A, O, B])} Z" fill="url(#stip)" stroke="none"/>'
    s += ln((190, 1381), (605, 1381), 1.3) + arrowhead((612, 1381), (1, 0), 9, False)
    s += ln((410, 1445), (410, 1208), 1.3) + arrowhead((410, 1201), (0, -1), 9, False)
    y1 = lambda x: O[1] + 1.5 * (x - O[0])
    y2 = lambda x: O[1] - 0.6 * (x - O[0])
    s += ln((295, y1(295)), (452, y1(452)), 1.6) + ln((310, y2(310)), (612, y2(612)), 1.6) + ln(A, B, 2.2)
    s += right((410, A[1]), (400, A[1]), (410, A[1] + 10), 8)
    s += sfr(279, 1245, '<tspan font-style="italic">y</tspan> = −', '3', '2', 'x')
    s += sfr(557, 1245, '<tspan font-style="italic">y</tspan> =', '3', '5', 'x')
    s += tx((425, 1270), '4') + tx((337, 1301), 'A') + tx((574, 1301), 'B') + tx((396, 1407), 'O')
    s += ti((395, 1222), 'y') + ti((604, 1397), 'x')
    return fig(2, (185, 1195, 620, 1450), s, STIPPLE)


def f7():
    A, N, P, M, B = (882, 302), (961, 302), (1000.5, 302), (1040, 302), (1198, 302)
    s = ln(A, B, 2.0) + ''.join(dot(p, 3.6) for p in (A, N, P, M, B))
    s += dash_bulge(A, B, 80, '5,4') + lbl((1040, 263), '16cm')
    for p, t in ((A, 'A'), (N, 'N'), (P, 'P'), (M, 'M'), (B, 'B')):
        s += tx((p[0], 323), t)
    return fig(2, (870, 240, 1212, 338), s)


def f8():
    O = (1038, 818)
    D, E = polar(O, 152, 47), polar(O, 135, 227)
    F = polar(O, 150, -43)
    s = (f'<path d="M{O[0]},{O[1]} L{O[0] + 24},{O[1]} A24,24 0 0 1 {polar(O, 24, -43)[0]:.2f},'
         f'{polar(O, 24, -43)[1]:.2f} Z" fill="url(#stipd)" stroke="none"/>')
    s += ln((893, 818), (1195, 818)) + ln(O, (1038, 670)) + ln(D, E) + ln(O, F)
    s += right(O, (1038, 700), (900, 818), 10) + right(O, E, F, 10)
    s += arc_at(O, (1038, 700), D, 22) + tx((1070, 770), '43°', 22)
    s += tx((1026, 681), 'C') + tx((1160, 715), 'D') + tx((896, 841), 'A') + tx((1043, 849), 'O')
    s += tx((1192, 839), 'B') + tx((925, 933), 'E') + tx((1167, 929), 'F')
    defs = ('<defs><pattern id="stipd" width="3" height="3" patternUnits="userSpaceOnUse">'
            '<rect width="3" height="3" fill="#888"/><circle cx="1" cy="1" r="0.9" fill="#111"/></pattern></defs>')
    return fig(2, (880, 660, 1210, 950), s, defs)


def f9():
    A, D, B, E, C = (948, 1300), (1040, 1300), (860, 1480), (1040, 1480), (1222, 1480)
    F = mid(D, E)
    G = inter(A, F, B, C)
    s = pg_([A, B, C, D], sw=1.6) + ln(D, E, 1.6) + ln(A, G, 1.6) + ticks(D, F, 1) + ticks(F, E, 1)
    s += right(E, D, C, 8)
    s += tx((925, 1302), 'A') + tx((1057, 1302), 'D') + tx((1057, 1386), 'F') + tx((860, 1500), 'B')
    s += tx((1028, 1500), 'E') + tx((G[0], 1500), 'G') + tx((1227, 1500), 'C')
    return fig(2, (848, 1285, 1240, 1512), s)


def f10():
    A, H, B = (319, 415), (319, 520), (454, 520)
    L0, L1 = (370, 615), (560, 400)
    fy = 579
    Fp = (L0[0] + (L0[1] - fy) / (L0[1] - L1[1]) * (L1[0] - L0[0]), fy)
    s = pg_([(185, 579), (362.5, 490), (620, 490), (470, 579)], fill='url(#stipl)', sw=1.6)
    s += ln(A, H, 1.6, '5,4') + dot(A, 3) + right(H, (319, 510), (309, 520), 7)
    s += ln(B, L1, 1.6) + ln(B, Fp, 1.6, '6,4') + ln(Fp, L0, 1.6)
    s += tx((340, 400), 'A') + ti((571, 396), 'l') + tx((346, 527), 'H') + tx((492, 520), 'B') + ti((475, 560), 'P')
    defs = ('<defs><pattern id="stipl" width="4" height="4" patternUnits="userSpaceOnUse">'
            '<rect width="4" height="4" fill="#e0e0e0"/><circle cx="1" cy="1" r="0.7" fill="#888"/>'
            '<circle cx="3" cy="3" r="0.6" fill="#999"/></pattern></defs>')
    return fig(3, (175, 385, 590, 625), s, defs)


def f11():
    L1 = ((365, 1182.5), (512.5, 1380))
    L2 = ((411, 1185), (335, 1397.5))
    L3 = ((295, 1367.5), (515, 1319))
    T, Lf, Rt = inter(*L1, *L2), inter(*L2, *L3), inter(*L1, *L3)
    s = ln(*L1, 1.6) + ln(*L2, 1.6) + ln(*L3, 1.6)
    for c in (T, Lf, Rt):
        s += f'<circle cx="{c[0]:.2f}" cy="{c[1]:.2f}" r="9" fill="none" stroke="#000" stroke-width="1.1"/>'
    for c, labs in ((T, (('a', -1, -19), ('b', -19, 5), ('d', 17, 3), ('c', 2, 22))),
                    (Lf, (('e', -10, -21), ('h', 20, -22), ('f', -22, 24), ('g', 8, 28))),
                    (Rt, (('q', -20, -13), ('p', 6, -27), ('s', 24, -1), ('r', -6, 20)))):
        for t, dx, dy in labs:
            s += ti((c[0] + dx, c[1] + dy), t, 22)
    return fig(3, (285, 1170, 525, 1400), s)


def f12():
    p, q, r = ((917.5, 317.5), (915, 530)), ((1011.5, 320), (1012.5, 530)), ((1100, 320), (1095, 530))
    l, m = ((865, 369), (1147.5, 369)), ((860, 466.5), (1150, 476))
    s = ''.join(ln(*z, 1.7) for z in (p, q, r, l, m))
    c1, c2, c3, c4 = inter(*p, *l), inter(*q, *l), inter(*p, *m), inter(*r, *m)
    s += arc_at(c1, p[0], l[0], 14) + arc_at(c2, q[1], l[1], 14) + arc_at(c3, p[0], m[1], 14) + arc_at(c4, r[0], m[0], 14)
    s += tx((882, 348), '91°') + tx((1048, 393), '89°') + tx((955, 443), '91°') + tx((1065, 455), '89°')
    s += ti((935, 300), 'p') + ti((1028, 304), 'q') + ti((1115, 303), 'r') + ti((1168, 371), 'l') + ti((1166, 480), 'm')
    return fig(3, (848, 283, 1185, 535), s)


def f13():
    T, V, Bm = (1092.5, 822.5), (1106, 919), (989, 960)
    s = ln((877.5, 822.5), (1180, 822.5), 1.7) + ln((877.5, 960), (1187.5, 960), 1.7)
    s += ln(T, V, 1.7) + ln(V, Bm, 1.7)
    s += arc_at(T, (1000, 822.5), V, 17) + arc_at(V, T, Bm, 15) + arc_at(Bm, (1100, 960), V, 18)
    s += tx((997, 845), '3<tspan font-style="italic">x</tspan>° +10°', 22)
    s += tx((1037, 923), '100°', 22) + tx((1066, 949), '20°', 22)
    s += ti((852, 826), 'l') + ti((855, 956), 'm')
    return fig(3, (838, 805, 1195, 975), s)


def tri15(bl, ap, br, sides, angles, sz=17):
    s = pg_([bl, ap, br], sw=1.4)
    for (p, q_) in sides:
        s += dash_bulge(p, q_, 13, '3,3')
    for c, p1, p2 in angles:
        s += arc_at(c, p1, p2, 9, 1)
    return s


def f15():
    s = ''
    T = {'ㄱ': ((157.5, 289), (252.5, 220), (297.5, 289)), 'ㄴ': ((337.5, 290), (435, 221), (467.5, 290)),
         'ㄷ': ((512.5, 289), (612.5, 218.5), (650, 289)), 'ㄹ': ((160, 403.5), (262.5, 331), (297.5, 403.5)),
         'ㅁ': ((340, 402.5), (440, 331), (480, 402.5)), 'ㅂ': ((514, 401), (613.5, 330), (650, 401))}
    side = {'ㄱ': ('L', 'R', 'B'), 'ㄴ': ('L', 'R'), 'ㄷ': ('L',), 'ㄹ': ('L', 'B'), 'ㅁ': ('L',), 'ㅂ': ()}
    angs = {'ㄱ': (), 'ㄴ': ('T',), 'ㄷ': ('T', 'R'), 'ㄹ': ('L',), 'ㅁ': ('L', 'T'), 'ㅂ': ('L', 'T', 'R')}
    for key, (bl, ap, br) in T.items():
        sd = {'L': (bl, ap), 'R': (ap, br), 'B': (br, bl)}
        an = {'L': (bl, br, ap), 'T': (ap, bl, br), 'R': (br, ap, bl)}
        s += tri15(bl, ap, br, [sd[x] for x in side[key]], [an[x] for x in angs[key]])
    labels = [((147.5, 222.5), 'ㄱ.'), ((192.5, 240), '6cm'), ((301, 248), '4cm'), ((227.5, 307), '7cm'),
              ((327.5, 222.5), 'ㄴ.'), ((372.5, 242), '6cm'), ((427, 247), '80°'), ((481, 249), '4cm'),
              ((500, 220), 'ㄷ.'), ((550, 235), '7cm'), ((605, 237), '80°'), ((635, 277), '65°'),
              ((150, 331), 'ㄹ.'), ((195, 357), '6cm'), ((198, 392), '35°'), ((225, 421), '7cm'),
              ((326, 330), 'ㅁ.'), ((375, 350), '7cm'), ((435, 352), '80°'), ((378, 392), '35°'),
              ((500, 330), 'ㅂ.'), ((605, 347), '80°'), ((553, 390), '35°'), ((634, 389), '65°')]
    for p, t in labels:
        if t.endswith('.'):
            s += (f'<text x="{p[0]:.1f}" y="{p[1]:.1f}" font-size="16" text-anchor="middle" dominant-baseline="central" '
                  f'class="ko">{t}</text>')
        elif 'cm' in t:
            s += lbl(p, t, 17)
        else:
            s += tx(p, t, 16)
    return fig(4, (120, 200, 672, 432), s)


def f18():
    C, B = (1284, 419), (1005, 419)
    A = inter(C, polar(C, 100, 140), B, polar(B, 100, 50))
    D = (863, 419)
    s = ln((722, 419), C, 1.7) + ln(B, A, 1.7) + ln(A, C, 1.7) + dot(D, 3.5)
    s += arc_at(A, B, C, 14) + arc_at(B, D, A, 16) + arc_at(C, A, B, 20)
    s += tx((A[0], A[1] - 18), 'A') + tx((968, 386), '130°') + tx((1221, 396), '40°')
    s += tx((865, 443), 'D') + tx((1007, 441), 'B') + tx((1284, 441), 'C')
    return fig(4, (715, 250, 1300, 455), s)


def f19():
    B, C = (852, 1061), (1111, 1061)
    A = ((B[0] + C[0]) / 2, 1061 - (C[0] - B[0]) / 2 * math.tan(math.radians(21)))
    AC = dist(A, C)
    D = add(A, mul(unit(sub(A, B)), 2 * AC * math.cos(math.radians(42))))
    s = pg_([B, C, D], sw=1.7) + ln(A, C, 1.7) + ticks(B, A) + ticks(A, C) + ticks(C, D)
    s += arc_at(B, C, A, 22) + arc_at(C, A, D, 16)
    s += tx((1192, 916), 'D') + tx((970, 997), 'A') + tx((943, 1047), '21°') + tx((849, 1082), 'B') + tx((1112, 1082), 'C')
    return fig(4, (830, 895, 1210, 1098), s)


def f22():
    A, B, E, C, D = (425, 646), (312.5, 776), (500, 776), (327.5, 850), (442.5, 850)
    s = pg_([A, B, C, D, E], sw=1.6) + ln(B, E, 1.6, '2,4')
    s += arc_at(A, B, E, 14) + arc_at(B, E, C, 14) + arc_at(C, B, D, 14)
    s += tx((425, 634), 'A') + tx((425, 680), '70°', 22) + tx((301, 784), 'B') + tx((344, 797), '80°', 22)
    s += tx((509, 790), 'E') + tx((364, 854), '100°', 22) + tx((328, 876), 'C') + tx((443, 876), 'D')
    return fig(5, (285, 615, 525, 892), s)


def f23():
    sd = 134
    B, C = (334, 1366.5), (468, 1366.5)
    c36, s36, c72, s72 = math.cos(math.radians(36)), math.sin(math.radians(36)), math.cos(math.radians(72)), math.sin(math.radians(72))
    A, D = (B[0] - sd * c36, B[1] + sd * s36), (C[0] + sd * c36, C[1] + sd * s36)
    yw = 1506
    t = (yw - A[1]) / (sd * s72)
    A2, D2 = (A[0] - sd * c72 * t, yw), (D[0] + sd * c72 * t, yw)
    E, F = lerp(B, C, 0.65), lerp(C, D, 0.65)
    G = inter(A, E, B, F)
    wave = []
    for i in range(121):
        x = A2[0] + (D2[0] - A2[0]) * i / 120
        wave.append((x, yw - 5 * math.sin(2 * math.pi * 4.5 * i / 120)))
    s = f'<path d="{poly_path([A2, A, B, C, D, D2])}" fill="none" stroke="#000" stroke-width="2"/>'
    s += f'<path d="{poly_path(wave)}" fill="none" stroke="#000" stroke-width="2"/>'
    s += ln(A, E, 1.8) + ln(B, F, 1.8) + ticks(B, E) + ticks(C, F)
    s += tx((328, 1351), 'B') + tx((E[0], 1349), 'E') + tx((465, 1351), 'C') + tx((212, 1434), 'A')
    s += tx((556, 1403), 'F') + tx((595, 1446), 'D') + tx((G[0] - 2, G[1] + 21), 'G')
    return fig(5, (195, 1335, 610, 1515), s)


def fs1():
    B, C = (917, 722), (1172, 722)
    A = ((B[0] + C[0]) / 2, 722 - (C[0] - B[0]) * math.sqrt(3) / 2)
    D, E = lerp(B, A, 0.25), lerp(B, C, 0.25)
    s = pg_([A, B, C], sw=1.7) + ln(A, E, 1.7) + ln(C, D, 1.7) + ticks(B, D, 2, 5, 3) + ticks(B, E, 2, 5, 3)
    s += tx((A[0], A[1] - 16), 'A') + tx((D[0] - 15, D[1] - 13), 'D') + tx((900, 722), 'B') + tx((E[0] - 5, 742), 'E') + tx((1190, 722), 'C')
    return fig(5, (885, 470, 1205, 755), s)


# ================================================================ 페이지 내용
def mini_table(pg, colx, rowy, cells, cls='tb'):
    s = S(pg)
    ws = [(colx[i + 1] - colx[i]) * s for i in range(len(colx) - 1)]
    hs = [(rowy[i + 1] - rowy[i]) * s for i in range(len(rowy) - 1)]
    t = f'<table class="{cls}" style="left:{X(pg, colx[0]):.2f}mm;top:{Y(pg, rowy[0]):.2f}mm">'
    for r_, row in enumerate(cells):
        t += f'<tr style="height:{hs[r_]:.2f}mm">' + ''.join(
            f'<td style="width:{ws[c]:.2f}mm">{fmt(v)}</td>' for c, v in enumerate(row)) + '</tr>'
    return t + '</table>'


BP = '<span class="bp">(</span>', '<span class="bp">)</span>'


def P1():
    s = ('<div class="abs hd" style="left:%.2fmm;top:%.2fmm;width:%.2fmm;height:%.2fmm">'
         % (FL, FT, FW, Y(1, 242) - FT))
    s += ('<div class="hd-top">2026학년도 &nbsp;제2학기 &nbsp;중간고사</div><div class="hd-row">'
          '<div class="hd-c"><div>학년</div><div class="big">1</div></div>'
          '<div class="hd-c"><div>과목코드</div><div class="big">05</div></div>'
          '<div class="hd-t">수 &nbsp; &nbsp;학</div>'
          '<div class="hd-c w"><div>고사 일시</div><div class="dt">2026년 &nbsp; 10월 &nbsp; 13일 &nbsp; 2교시</div></div>'
          '</div></div>')
    note = [(86, 297, '∘'), (105, 297, '선택형 ( 23 )문항, 서술형 ( 2 )문항입니다.'),
            (86, 336, '∘'), (105, 336, '문제지는 ( 3 )장, ( 5 )면입니다.'),
            (86, 376, '∘'), (105, 376, '문항에 따라 배점이 다르니, 각 문항에 표시된 배점을', 676), (105, 414, '참고하세요.'),
            (86, 453, '∘'), (105, 453, 'OMR 답안지에 필요한 기재사항을 정확하게 기재한 후', 676), (105, 492, '옳은 답을 바르게 표기하세요.'),
            (86, 530, '∘'), (105, 530, '서답형 답안은 서답형 답안지에 검정색 펜으로 바르게', 676),
            (105, 568, '작성하세요.(서술형 답안 작성 시 <u>연필, 붉은 계열 볼펜</u>', 676),
            (105, 606, '<u>사용을 금지</u>하며, 사용 시 해당 부분은 오답 처리함.)'),
            (86, 645, '∘'), (105, 645, '시험시간은 ( 45 )분입니다.')]
    s += box_html(1, 78, 277, 682, 667, inbox(1, 78, 277, note), cls='box nb')
    s += qlines(1, 'L', [730, 773], ['1. 가락이와 석촌이의 대화에서 ㉠, ㉡, ㉢에 들어갈',
                                     '말을 옳게 짝지은 것은? [4점]'])
    dia = [(100, 820, '가락:'), (172, 820, '홀수 중 $x$번째 자연수를 $y$라고 하면, $x$와', 660),
           (172, 862, '$y$는 정비례 관계일까?'), (100, 903, '석촌:'), (172, 903, '표를 만들어 보면 알 수 있어.'),
           (100, 1043, '가락:'), (172, 1043, '아하, $x$와 $y$는 정비례 관계가 ( ㉠ ).'),
           (100, 1085, '석촌:'), (172, 1085, '짝수 중 $a$번째 자연수를 $b$라고 하면, $a$와', 660),
           (172, 1127, '$b$는 정비례 관계일까?'),
           (100, 1170, '가락:'), (172, 1170, '식으로 표현하면 ( ㉡ )가 되니까, $a$와 $b$는', 660),
           (172, 1212, '정비례 관계가 ( ㉢ ).')]
    s += box_html(1, 85, 800, 670, 1230, inbox(1, 85, 800, dia))
    s += mini_table(1, [205, 274, 344, 413, 482, 551], [940, 973, 1006],
                    [['$x$', '1', '2', '3', '…'], ['$y$', '1', '3', '5', '…']], 'tb in')
    xs = (226, 399, 557)
    for x, t in zip(xs, '㉠㉡㉢'):
        s += place(1, X(1, x) - 10, Y(1, 1270) - LH / 2, f'<u>{t}</u>', w=20, cls='ch jc')
    rows = [('맞아', '$a=b$', '맞아'), ('맞아', '$a=2b$', '아니야'), ('아니야', '$a=2b$', '맞아'),
            ('아니야', '$b=2a$', '아니야'), ('아니야', '$b=2a$', '맞아')]
    for i, (y, row) in enumerate(zip((1313, 1358, 1403, 1447, 1492), rows)):
        s += place(1, X(1, 100) - 2.5, Y(1, y) - LH / 2, MARK[i], cls='ch')
        for x, t in zip(xs, row):
            s += place(1, X(1, x) - 15, Y(1, y) - LH / 2, fmt(t), w=30, cls='ch jc')
    s += qlines(1, 'R', [290, 332, 376], ['2. 두 변수 $x$, $y$가 반비례 관계일 때, $x$와 $y$ 사이의 관계를',
                                          '<<나타낸 그래프에 대한 설명으로 옳은 것은?', '>>[3점]'])
    s += choice_lines(1, 'R', [(418, 0, '원점을 지난다.'), (460, 1, '한 쌍의 매끄러운 곡선 모양이다.'),
                               (503, 2, '$x$의 값이 커질 때 $y$의 값은 작아진다.'),
                               (546, 3, '$x$의 값이 커질 때 $y$축에 점점 가까워진다.'),
                               (606, 4, '그래프가 $(1, 2)$를 지나면 ' + BP[0] + '$−$' + fr(1, 2) + '$, −1$' + BP[1] + '을 지난다.')])
    s += qlines(1, 'R', [785, 828], ['3. 두 변수 $x$, $y$ 사이의 관계를 나타낸 그래프이다.', '$x$, $y$의 관계식은? [4점]'])
    s += f3()
    s += choices(1, 'R', [1183, 1250], ['$y=−4x$', '$y=−3x$', '$y=−$' + fr(4, 3) + '$x$', '$y=$' + fr(4, 3) + '$x$', '$y=4x$'], 3)
    s += qlines(1, 'R', [1447, 1507], ['4. 두 식 $y=4x$, $y=$' + fr('k', 'x') + '의 그래프의 교점의 좌표가',
                                       '$(a, 2a+3)$일 때, 상수 $k$의 값은? [4점]'])
    s += choices(1, 'R', [1572, 1642], [fr(2, 3), '1', fr(3, 2), fr(26, 9), '9'], 3)
    return s + cont(1, 1862, '뒷면에 계속')


def P2():
    s = qlines(2, 'L', [118, 195, 272, 333], ['5. 식 $y=$' + fr('a', 'x') + '의 그래프가 점 $A(−2, 4)$를 지난다. 점',
                                             '$A$에서 $x$축에 내린 수선과 식 $y=$' + fr(5, 'x') + '의 그래프의 교점을',
                                             '$B$, 점 $B$에서 $y$축에 내린 수선과 식 $y=$' + fr('a', 'x') + '의 그래프의',
                                             '교점을 $C$라고 할 때, 점 $C$의 $x$좌표는? [4점]'])
    s += f5()
    s += choices(2, 'L', [765, 830], [fr(4, 5), fr(5, 4), '3', fr(16, 5), fr(18, 5)], 3)
    s += qlines(2, 'L', [1072, 1130, 1170], ['6. 두 점 $A$, $B$가 각각 두 식 $y=−$' + fr(3, 2) + '$x$, $y=$' + fr(3, 5) + '$x$의 그래프',
                                             '위의 점일 때, $△AOB$의 넓이는? (단, $O$는 원점이다.)', '>>[4점]'])
    s += f6()
    s += choices(2, 'L', [1535, 1605], ['8', fr(46, 3), '16', '18', fr(56, 3)], 3)
    s += qlines(2, 'R', [105, 150, 195], ['7. $[AB]=16 cm$이고, $[AB]$의 중점을 $M$, $[AM]$의 중점을',
                                          '$N$, $[MN]$의 중점을 $P$라 할 때, $[AP]$의 길이는?', '>>[3점]'])
    s += f7()
    s += choices(2, 'R', [408, 455], ['$3 cm$', '$4 cm$', '$5 cm$', '$6 cm$', '$7 cm$'], 3)
    s += qlines(2, 'R', [590, 632], ['8. $∠AOB$와 $∠DOE$는 평각이고, $[AB]⊥[CO]$, $[DE]⊥[FO]$',
                                     '이다. $∠COD=43°$일 때, $∠FOB$의 크기는? [3점]'])
    s += f8()
    s += choices(2, 'R', [987, 1035], ['$43°$', '$44°$', '$45°$', '$46°$', '$47°$'], 3)
    s += qlines(2, 'R', [1163, 1210, 1252], ['9. 사각형 $ABCD$의 꼭짓점 $D$에서 변 $BC$에 내린',
                                             '수선의 발을 $E$, $[DE]$의 중점을 $F$, ${AF}$와 변 $BC$의',
                                             '교점을 $G$라 할 때, 옳지 <u>않은</u> 것은? [4점]'])
    s += f9()
    s += choice_lines(2, 'R', [(1540, 0, '$[DE]=2[EF]$'), (1586, 1, '점 $C$는 ${DC}$와 $~BE~$의 교점이다.'),
                               (1634, 2, '$~DE~$는 $[BC]$의 수직이등분선이다.'),
                               (1683, 3, '점 $D$와 $[BC]$ 사이의 거리는 $[DE]$의 길이이다.'),
                               (1730, 4, '두 점 $A$와 $G$사이의 거리는 $[AG]$의 길이이다.')])
    return s + cont(2, 1857, '다음 장에 계속')


def P3():
    s = qlines(3, 'L', [128, 170, 212, 254, 295, 335], [
        '10. 평면 $_P_$ 위에 있지 않은 점 $A$와 평면 $_P_$ 위의',
        '한 점 $H$에 대해 직선 $AH$는 평면 $_P_$와 직교하고,',
        '평면 $_P_$와 한 점 $B$에서 만나면서 평면 $_P_$와 직교하지',
        '않는 직선을 $l$이라고 할 때, &lt;보기&gt; 중 옳은 것<u>만</u>을',
        '<b><u>있는 대로</u></b> 고른 것은? (단, 점 $H$와 점 $B$는 서로', '다른 점이다.) [4점]'])
    s += f10()
    s += bogi(3, 115, 655, 682, 842, [(125, 690, 'ㄱ. $~HB~⊥~AH~$'), (125, 738, 'ㄴ. 직선 $l$과 $~AH~$는 꼬인 위치에 있다.'),
                                      (125, 780, 'ㄷ. 직선 $AH$에 수직인 직선과 평면 $_P_$는 평행하다.'),
                                      (125, 825, 'ㄹ. 직선 $HB$와 점 $A$ 사이의 거리는 $[AH]$의 길이이다.')])
    s += choices(3, 'L', [868, 910], ['ㄱ, ㄷ', 'ㄱ, ㄹ', 'ㄴ, ㄹ', 'ㄱ, ㄴ, ㄷ', 'ㄱ, ㄴ, ㄹ'], 3)
    s += qlines(3, 'L', [1112, 1152], ['11. 그림과 같이 세 직선이 만날 때, 다음 중 옳지 <u>않은</u>', '것은? [4점]'])
    s += f11()
    s += choice_lines(3, 'L', [(1440, 0, '$∠a$의 동위각은 $∠e$와 $∠p$이다.'), (1483, 1, '$∠g$의 동위각은 $∠d$와 $∠s$이다.'),
                               (1527, 2, '$∠e$의 엇각은 $∠c$이다.'), (1570, 3, '$∠q$의 엇각은 $∠d$와 $∠g$이다.'),
                               (1612, 4, '$∠p$와 $∠r$은 맞꼭지각으로 크기가 같다.')])
    s += qlines(3, 'R', [128, 170, 213, 255], ['12. 한 평면 위의 서로 다른 세 직선 $p$, $q$, $r$이 서로',
                                               '다른 두 직선 $l$, $m$과 만나서 생기는 교각의 크기가',
                                               '그림과 같을 때, 다섯 개의 직선 중 평행한 두', '직선은? [4점]'])
    s += f12()
    s += choices(3, 'R', [568, 612], ['$l, m$', '$p, q$', '$p, r$', '$q, l$', '$q, r$'], 3)
    s += qlines(3, 'R', [775], ['13. $l$∥$m$일 때, $x$의 값은? [4점]'])
    s += f13()
    s += choices(3, 'R', [1012, 1056], ['30', '35', '40', '45', '50'], 3)
    s += qlines(3, 'R', [1262, 1300], ['14. &lt;보기&gt;에서 $∠A$의 크기가 더 주어지면 $△ABC$가',
                                       '하나로 정해지는 것의 개수는? [4점]'])
    s += bogi(3, 820, 1343, 1205, 1575, [(832, 1375, '•'), (870, 1375, '$∠B$의 크기, $∠C$의 크기'),
                                         (832, 1421, '•'), (870, 1421, '$∠B$의 크기, $[AB]$의 길이'),
                                         (832, 1467, '•'), (870, 1467, '$[AB]$의 길이, $[BC]$의 길이'),
                                         (832, 1513, '•'), (870, 1513, '$[AB]$의 길이, $[CA]$의 길이'),
                                         (832, 1559, '•'), (870, 1559, '$[BC]$의 길이, $[CA]$의 길이')])
    s += choices(3, 'R', [1620, 1666], ['1 개', '2 개', '3개', '4 개', '5 개'], 3)
    return s + cont(3, 1830, '뒷면에 계속')


def P4():
    s = qlines(4, 'L', [143], ['15. &lt;보기&gt; 중 서로 합동인 두 삼각형은? [4점]'])
    s += box_html(4, 107, 188, 686, 438, '<div class="bogi-t"><span>&lt;보기&gt;</span></div>') + f15()
    s += choices(4, 'L', [482, 528], ['ㄱ, ㄴ', 'ㄱ, ㄹ', 'ㄴ, ㄹ', 'ㄷ, ㅁ', 'ㅁ, ㅂ'], 3)
    s += qlines(4, 'L', [770, 810, 850], ['16. 어떤 다각형의 한 꼭짓점에서 한 개의 대각선을',
                                          '그었더니 이십각형과 이십육각형으로 나누어',
                                          '졌을 때, 이 다각형의 대각선의 개수는? [4점]'])
    s += choices(4, 'L', [903, 948], ['892 개', '902 개', '912 개', '922 개', '932 개'], 3)
    s += qlines(4, 'L', [1313, 1353, 1393, 1433], ['17. 어떤 다각형에서 어느 두 점도 서로 이웃하지 않도록',
                                                   '꼭짓점 세 개를 선택하고 이 세 개의 꼭짓점에서',
                                                   '대각선을 그었더니 모두 18개였을 때, 이 다각형은?', '>>[4점]'])
    s += choices(4, 'L', [1487, 1530], ['팔각형', '구각형', '십각형', '십일각형', '십이각형'], 3)
    s += qlines(4, 'R', [140, 180, 222], ['18. 삼각형 $ABC$에 대하여 $∠C=40°$, 선분 $CB$위에',
                                          '있지 않고 반직선 $CB$ 위에 있는 점 $D$에 대하여',
                                          '$∠ABD=130°$일 때, $∠A$의 크기는? [4점]'])
    s += f18()
    s += choices(4, 'R', [492], ['$90°$', '$100°$', '$110°$', '$120°$', '$130°$'], 5)
    s += qlines(4, 'R', [735, 775, 820, 860], ['19. $[AB]=[AC]$이고 $∠B=21°$인 삼각형 $ABC$에서 변 $AB$',
                                               '위에 있지 않고, 반직선 $BA$ 위에 있는 점 $D$는',
                                               '$[AC]=[CD]$를 만족한다고 할 때, $∠DCA$의 크기는?', '>>[4점]'])
    s += f19()
    s += choices(4, 'R', [1130], ['$92°$', '$93°$', '$94°$', '$95°$', '$96°$'], 5)
    s += qlines(4, 'R', [1328, 1368], ['20. 다각형에 대한 설명으로 옳은 것을 <u>모두</u> 고르면?', '(정답 2개) [4점]'])
    s += choice_lines(4, 'R', [(1410, 0, '십각형의 내각의 크기의 합은 $1260°$이다.'),
                               (1450, 1, '정십이각형의 한 내각의 크기는 $135°$이다.'),
                               (1492, 2, '한 내각과 한 외각의 크기의 비가 $7:2$인 정다각형은|'), (1532, None, '정이십각형이다.'),
                               (1573, 3, '모든 내각과 외각의 크기의 합이 $1620°$인 다각형의|'), (1614, None, '변의 개수는 9개이다.'),
                               (1655, 4, '정다각형의 한 외각의 크기는 꼭짓점의 개수가|'), (1697, None, '많아질수록 작아진다.')])
    return s + cont(4, 1813, '다음 장에 계속')


def P5():
    s = qlines(5, 'L', [110, 152, 196], ['21. 80보다 크고, 100보다 작은 소수 $a$, $b$에 대하여',
                                         '어떤 사각형의 외각이 $a°$, $b°$, $79°$, $101°$이고,',
                                         '$a<b$일 때, $b−a$의 값은? [5점]'])
    s += choices(5, 'L', [243], ['14', '15', '16', '17', '18'], 5)
    s += qlines(5, 'L', [493, 535, 578, 619], ['22. 오각형 $ABCDE$에서 $∠A=70°$이고, $∠EBC=80°$,',
                                               '<<$∠BCD=100°$이다.',
                                               '$∠AED=∠EDC=∠ABC−10°$일 때, $∠BED$의', '값은? [4점]'])
    s += f22()
    s += choices(5, 'L', [917], ['$50°$', '$55°$', '$60°$', '$65°$', '$70°$'], 5)
    s += qlines(5, 'L', [1163, 1212, 1260, 1302], ['23. 그림은 정십각형의 일부이다. 변 $BC$ 위의 점 $E$,',
                                                   '변 $CD$ 위의 점 $F$에 대하여 $[BE]=[CF]$이고 $[AE]$와',
                                                   '$[BF]$의 교점을 $G$라 할 때, $∠AGF$의 크기와',
                                                   '$∠EGF$의 크기의 비는? [4점]'])
    s += f23()
    s += choices(5, 'L', [1582, 1630], ['$4:1$', '$5:1$', '$6:1$', '$3:2$', '$5:2$'], 3)
    l, r = COL['R']
    s += place(5, l, Y(5, 112) - LH / 2, '* 서답형 답안은 <b><u>서답형 답안지</u></b>에 <b><u>검정색 펜</u></b>으로 <b><u>바르게 작성</u></b>',
               w=r - l, cls='q jj tight')
    s += place(5, l + 4.2, Y(5, 150) - LH / 2, '하세요.(서술형 답안 작성 시 <b><u>연필, 붉은 계열 볼펜 사용</u></b>', w=r - l - 4.2, cls='q jj')
    s += place(5, l + 4.2, Y(5, 188) - LH / 2, '<b><u>을 금지</u></b>하며, 사용 시 해당 부분은 오답 처리함.)', cls='q')
    s += lines(5, 'R', [290, 348, 390, 432],
               ['<b>[서답형 1]</b> 정삼각형 $ABC$에서 $[BD]=$' + fr(1, 4) + '$[AB]$, $[BE]=$' + fr(1, 4) + '$[BC]$',
                '이다. 합동인 삼각형 한 쌍을 찾아 기호 $≡$를', '사용하여 나타내고 합동인 이유를 서술하시오.', '>>[5점]'],
               ind2=5.6)
    s += fs1()
    s += lines(5, 'R', [1043, 1085, 1125, 1166],
               ['<b>[서답형 2]</b> $n$각형의 내각의 크기의 합을 구하는 식을', '이용하여 $n$각형의 외각의 크기의 합이 $360°$임을',
                '설명하는 과정이다. 밑줄 친 곳에 알맞은 식을', '쓰시오. (단, 각도 단위를 반드시 쓰시오.) [5점]'], ind2=5.6)
    blank = '<span class="ul" style="width:%smm"></span>'
    rows = [(750, 1216, '일반적으로 $n$각형의 한 꼭짓점에서 내각과 외각의', 1335), (750, 1255, '크기를 더하면 평각이 되므로'),
            (750, 1298, '(내각의 크기의 합)+(외각의 크기의 합)=(1)' + blank % 12 + '이다.', 1338),
            (750, 1340, '따라서 $n$각형의 내각의 크기의 합을 우변으로', 1338),
            (750, 1379, '이항하면 외각의 크기의 합은 다음과 같다.'), (750, 1421, '(외각의 크기의 합)='),
            (750, 1466, '(2)' + blank % 76), (750, 1510, '위 식을 전개하고, 동류항끼리 계산하면 다음과 같다.', 1338),
            (750, 1553, '(3)' + blank % 76)]
    s += box_html(5, 738, 1196, 1347, 1571, inbox(5, 738, 1196, rows), cls='box sm')
    s += place(5, l, Y(5, 1810) - LH / 2, '- 끝 -', w=r - l, cls='q jc')
    s += place(5, l, Y(5, 1862) - 5, '★★★ 수고하셨습니다 ★★★', w=r - l, cls='thx')
    return s


def page(n, body):
    foot = (f'<div class="foot"><span>본 시험 문제의 저작권은 &lt;가락중학교&gt;에 있습니다.</span>'
            f'<span>&lt;수학&gt; &nbsp;총( 5 )면 중 ( {n} )면</span></div>')
    top = Y(1, 242) if n == 1 else FT
    return (f'<section class="page"><div class="frame"></div>'
            f'<div class="divider" style="top:{top:.2f}mm"></div>{body}{foot}</section>')


CSS = r'''
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #fff; color: #000; }
body { font-family: "NanumMyeongjo", "Noto Serif CJK KR", serif; font-size: 10.2pt; }
.page { width: 210mm; height: 297mm; position: relative; page-break-after: always; overflow: hidden; }
.page:last-child { page-break-after: auto; }
.frame { position: absolute; left: 10.5mm; top: 12mm; width: 189mm; height: 264mm; border: 1.6px solid #000; }
.divider { position: absolute; left: 105mm; bottom: 21mm; border-left: 1.2px solid #000; }
.abs { position: absolute; white-space: nowrap; line-height: 6.4mm; }
.q, .qn, .ch, .bx, .cont { height: 6.4mm; }
.q { letter-spacing: -0.2px; }
.q.tight { letter-spacing: -0.6px; }
.jj { text-align: justify; text-align-last: justify; }
.jl { text-align: left; }
.jr { text-align: right; }
.jc { text-align: center; }
.m { font-family: "Liberation Serif", "Times New Roman", serif; font-size: 1.07em; }
.m i { font-style: italic; }
.m sup { font-size: 0.68em; vertical-align: 0.5em; line-height: 0; }
.op { margin: 0 0.12em; }
.ov { display: inline-block; border-top: 1px solid #000; line-height: 1.05; padding-top: 0.5px; }
.ray, .lin { display: inline-block; line-height: 1.05; padding-top: 0.42em; background-repeat: no-repeat; }
.ray { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 10 10'%3E%3Cpath d='M1 1 L9 5 L1 9' fill='none' stroke='black' stroke-width='1.6'/%3E%3C/svg%3E"), linear-gradient(#000, #000);
  background-size: 0.36em 0.36em, calc(100% - 0.1em) 1px; background-position: right 0.04em, left 0.21em; }
.lin { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 10 10'%3E%3Cpath d='M1 1 L9 5 L1 9' fill='none' stroke='black' stroke-width='1.6'/%3E%3C/svg%3E"), url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 10 10'%3E%3Cpath d='M9 1 L1 5 L9 9' fill='none' stroke='black' stroke-width='1.6'/%3E%3C/svg%3E"), linear-gradient(#000, #000);
  background-size: 0.36em 0.36em, 0.36em 0.36em, calc(100% - 0.1em) 1px; background-position: right 0.04em, left 0.04em, 0.05em 0.21em; }
.fr { display: inline-flex; flex-direction: column; vertical-align: middle; text-align: center; line-height: 1.12; margin: 0 1px; }
.fr .fn { border-bottom: 1px solid #000; padding: 0 1px; }
.fr .m { font-size: 0.95em; }
.bp { font-family: "Liberation Serif", serif; font-size: 1.9em; vertical-align: middle; line-height: 0; font-weight: 300; }
.ch { }
.cm { font-family: "NanumMyeongjo", serif; }
.box { border: 1.3px solid #000; white-space: normal; }
.box.nb { border-width: 1.6px; }
.box.nb .bx { font-size: 9.8pt; }
.box.sm .bx { font-size: 9.7pt; }
.bogi-t { position: absolute; top: -3.3mm; left: 0; right: 0; text-align: center; line-height: 6.4mm; }
.bogi-t span { background: #fff; padding: 0 2mm; }
table.tb { position: absolute; border-collapse: collapse; text-align: center; }
table.tb td { border: 1px solid #000; padding: 0; line-height: 1; }
.fig { overflow: visible; }
.fig text { font-family: "Liberation Serif", "Times New Roman", serif; fill: #000; }
.fig text.ko { font-family: "NanumMyeongjo", serif; }
.ul { display: inline-block; border-bottom: 1px solid #000; height: 1em; vertical-align: -0.15em; }
.cont { font-family: "NanumGothic", sans-serif; font-weight: bold; text-align: right; }
.thx { font-family: "NanumGothic", sans-serif; font-size: 17pt; text-align: center; line-height: 10mm; }
.hd { border-bottom: 1.6px solid #000; font-family: "NanumGothic", sans-serif; font-weight: bold; }
.hd-top { height: 27%; border-bottom: 1.4px solid #000; text-align: center; font-size: 12.5pt; letter-spacing: 1.5px; line-height: 1;
  display: flex; align-items: center; justify-content: center; }
.hd-row { display: flex; height: 73%; }
.hd-c { width: 16.7%; border-right: 1.4px solid #000; display: flex; flex-direction: column; }
.hd-c > div { display: flex; align-items: center; justify-content: center; }
.hd-c > div:first-child { height: 43%; border-bottom: 1.4px solid #000; font-size: 12.5pt; }
.hd-c > div:last-child { flex: 1; }
.hd-c .big { font-size: 21pt; }
.hd-c.w { width: 33.3%; border-right: none; border-left: 1.4px solid #000; }
.hd-c .dt { font-size: 11.5pt; }
.hd-t { flex: 1; display: flex; align-items: center; justify-content: center; font-size: 34pt; font-weight: 800; }
.foot { position: absolute; left: 17mm; right: 15mm; top: 277.6mm; display: flex; justify-content: space-between;
  font-family: "NanumGothic", sans-serif; font-weight: bold; font-size: 10pt; letter-spacing: 0.8px; }
'''

PAGES = [P1(), P2(), P3(), P4(), P5()]
HTML = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>2026 2학기 중간고사 1학년 수학</title>'
        f'<style>{CSS}</style></head><body>'
        + ''.join(page(i + 1, b) for i, b in enumerate(PAGES)) + '</body></html>')

if __name__ == '__main__':
    html_path = os.path.join(HERE, 'exam4.html')
    pdf_path = os.path.join(HERE, '2026_2학기_중간고사_1학년_수학.pdf')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(HTML)
    chrome = os.environ.get('CHROME', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    subprocess.run([chrome, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                    '--virtual-time-budget=5000', f'--print-to-pdf={pdf_path}', 'file://' + html_path], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(pdf_path)
