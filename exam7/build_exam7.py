# -*- coding: utf-8 -*-
"""잠실여자중학교 2025학년도 2학기 기말고사 3학년 수학 원본 시험지 복원.

원본(1080px 폭 화면 캡처)의 좌표를 그대로 써서 글자 줄과 그림을 배치하고,
그림은 모두 SVG로 새로 그린 뒤 Chromium으로 A4 PDF를 만든다.
  python3 exam7/build_exam7.py
"""
import math
import os
import random
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))

# 각 쪽 캡처에서 테두리 위쪽 선의 y(px). 테두리 왼쪽 x=62, 오른쪽 x=1021, 높이 1411px
TOP = {1: 56, 2: 57, 3: 68, 4: 72, 5: 52, 6: 56, 7: 57}
K = 189.0 / (1021 - 62)          # px → mm
FL, FT = 10.5, 7.5               # 출력 테두리 왼쪽·위(mm)
FH = 1411 * K


def X(x):
    return FL + (x - 62) * K


def Y(pg, y):
    return FT + (y - TOP[pg]) * K


LCOL, RCOL = (85, 517), (562, 996)


# ------------------------------------------------------------ 글자 표기
def fmt(s):
    """$...$ 안: 수식. [AB] 선분, ^AB^ 호, ~PT~ 직선(양쪽 화살표), 소문자 한 글자는 기울임."""
    def run(mo):
        t = mo.group(1)
        parts = re.split(r'(<[^>]*>|&[a-z]+;)', t)
        for i in range(0, len(parts), 2):
            q = parts[i]
            q = re.sub(r'([a-z])', lambda z: '\x03' + z.group(1) + '\x04', q)
            q = q.replace('-', '−').replace('=', '\x05=\x06')
            parts[i] = q
        t = ''.join(parts)
        t = re.sub(r'\[([^\]]+)\]', r'<span class="ov">\1</span>', t)
        t = re.sub(r'\^([^^]+)\^', r'<span class="arc">\1</span>', t)
        t = re.sub(r'~([^~]+)~', r'<span class="lin">\1</span>', t)
        t = t.replace('\x03', '<i>').replace('\x04', '</i>').replace('&lt;', '<span class="op">&lt;</span>')
        t = t.replace('\x05=\x06', '<span class="op">=</span>')
        return f'<span class="m">{t}</span>'
    return re.sub(r'\$([^$]+)\$', run, s)


def sq(x):
    return f'<span class="sq">√<span class="rc">{x}</span></span>'


def fr(n, d):
    return f'<span class="fr"><span class="fn">{n}</span><span class="fd">{d}</span></span>'


def L(pg, y, x, html, right=None, cls=''):
    """(x, y=줄 가운데)에 한 줄. right가 있으면 양쪽 정렬."""
    w = f'width:{(right - x) * K:.2f}mm;' if right else ''
    c = 'ln' + (' jj' if right else '') + (' ' + cls if cls else '')
    return f'<div class="{c}" style="left:{X(x):.2f}mm;top:{Y(pg, y):.2f}mm;{w}">{fmt(html)}</div>'


def Q(pg, col, ys, lines):
    """문항 본문: 마지막 줄 외에는 단 폭에 맞춰 양쪽 정렬"""
    l, r = LCOL if col == 'L' else RCOL
    out = ''
    for i, (y, t) in enumerate(zip(ys, lines)):
        right = None if (i == len(lines) - 1 or t.startswith('<<')) else r
        out += L(pg, y, l, t.lstrip('<'), right)
    return out


MARK = '①②③④⑤'


def CH(pg, col, ys, items, xs=None):
    xs = xs or ((90, 222, 355) if col == 'L' else (565, 698, 832))
    out = ''
    for i, t in enumerate(items):
        r, c = divmod(i, len(xs))
        out += L(pg, ys[r], xs[c], f'<span class="cm">{MARK[i]}</span> {t}', cls='ch')
    return out


def CHL(pg, col, rows):
    """긴 선택지: rows=[(y, 번호 or None, 글)] ('|'로 끝나면 양쪽 정렬)"""
    l, r = LCOL if col == 'L' else RCOL
    out = ''
    for y, k, t in rows:
        j = t.endswith('|')
        t = t.rstrip('|')
        if k is not None:
            out += L(pg, y, l + 3, f'<span class="cm">{MARK[k]}</span>', cls='ch')
        out += L(pg, y, l + 30, t, r if j else None, cls='ch')
    return out


def box(pg, x0, y0, x1, y1, cls='bx', inner=''):
    return (f'<div class="{cls}" style="left:{X(x0):.2f}mm;top:{Y(pg, y0):.2f}mm;'
            f'width:{(x1 - x0) * K:.2f}mm;height:{(y1 - y0) * K:.2f}mm">{inner}</div>')


def table(pg, colx, rowy, cells, shade):
    """shade(r, c) → 음영 여부"""
    ws = [(colx[i + 1] - colx[i]) * K for i in range(len(colx) - 1)]
    hs = [(rowy[i + 1] - rowy[i]) * K for i in range(len(rowy) - 1)]
    t = f'<table class="tb" style="left:{X(colx[0]):.2f}mm;top:{Y(pg, rowy[0]):.2f}mm">'
    for r, row in enumerate(cells):
        t += f'<tr style="height:{hs[r]:.2f}mm">'
        c = 0
        for v in row:
            span = 1
            if isinstance(v, tuple):
                v, span = v
            w = sum(ws[c:c + span])
            sh = ' class="sh"' if shade(r, c) else ''
            t += f'<td{sh} colspan="{span}" style="width:{w:.2f}mm">{fmt(str(v))}</td>'
            c += span
        t += '</tr>'
    return t + '</table>'


# ------------------------------------------------------------ 기하·SVG
def sub(p, q): return (p[0] - q[0], p[1] - q[1])
def add(p, q): return (p[0] + q[0], p[1] + q[1])
def mul(p, k): return (p[0] * k, p[1] * k)
def mid(p, q): return ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
def lerp(p, q, t): return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def unit(v):
    n = math.hypot(*v)
    return (v[0] / n, v[1] / n)


def polar(c, r, deg):
    return (c[0] + r * math.cos(math.radians(deg)), c[1] - r * math.sin(math.radians(deg)))


def ang(c, p):
    return math.degrees(math.atan2(-(p[1] - c[1]), p[0] - c[0]))


def inter(p1, p2, p3, p4):
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def circ3(a, b, c):
    ax, ay = a; bx, by = b; cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return (ux, uy), math.hypot(ax - ux, ay - uy)


def second_hit(c, r, p, q):
    """p(원 위)에서 q 방향 직선이 원과 다시 만나는 점"""
    d = unit(sub(q, p))
    f = sub(p, c)
    t = -2 * (f[0] * d[0] + f[1] * d[1])
    return add(p, mul(d, t))


SW = 1.4


def ln(p, q, sw=SW, dash=None, col='#111'):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<line x1="{p[0]:.2f}" y1="{p[1]:.2f}" x2="{q[0]:.2f}" y2="{q[1]:.2f}" stroke="{col}" '
            f'stroke-width="{sw}" stroke-linecap="round"{d}/>')


def poly(pts, fill='none', sw=SW, close=True, col='#111'):
    d = ' '.join(f'{x:.2f},{y:.2f}' for x, y in pts)
    t = 'polygon' if close else 'polyline'
    return f'<{t} points="{d}" fill="{fill}" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round"/>'


def circle(c, r, sw=SW, fill='none'):
    return f'<circle cx="{c[0]:.2f}" cy="{c[1]:.2f}" r="{r:.2f}" fill="{fill}" stroke="#111" stroke-width="{sw}"/>'


def dot(p, r=2.4):
    return f'<circle cx="{p[0]:.2f}" cy="{p[1]:.2f}" r="{r}" fill="#111"/>'


def tx(p, s, size=19, anchor='middle', cls='', italic=False):
    st = ' font-style="italic"' if italic else ''
    c = f' class="{cls}"' if cls else ''
    return (f'<text x="{p[0]:.2f}" y="{p[1]:.2f}" font-size="{size}" text-anchor="{anchor}" '
            f'dominant-baseline="central"{st}{c}>{s}</text>')


def arcp(c, r, a1, a2, sw=1.0, dash=None):
    """a1→a2 반시계(도) 원호"""
    sw_ = (a2 - a1) % 360
    p1, p2 = polar(c, r, a1), polar(c, r, a1 + sw_)
    large = 1 if sw_ > 180 else 0
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<path d="M{p1[0]:.2f},{p1[1]:.2f} A{r:.2f},{r:.2f} 0 {large} 0 {p2[0]:.2f},{p2[1]:.2f}" '
            f'fill="none" stroke="#111" stroke-width="{sw}"{d}/>')


def angle_arc(c, p1, p2, r, sw=1.0):
    a1, a2 = ang(c, p1), ang(c, p2)
    if (a2 - a1) % 360 > 180:
        a1, a2 = a2, a1
    return arcp(c, r, a1, a2, sw)


def arrowhead(tip, d, size=7, col='#111'):
    u = unit(d)
    nr = (-u[1], u[0])
    b = sub(tip, mul(u, size))
    p1, p2 = add(b, mul(nr, size * 0.42)), sub(b, mul(nr, size * 0.42))
    return f'<polygon points="{p1[0]:.2f},{p1[1]:.2f} {tip[0]:.2f},{tip[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}" fill="{col}"/>'


def qcurve(p, c, q, sw=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<path d="M{p[0]:.2f},{p[1]:.2f} Q{c[0]:.2f},{c[1]:.2f} {q[0]:.2f},{q[1]:.2f}" fill="none" '
            f'stroke="#111" stroke-width="{sw}"{d}/>')


def ticks_at(p, direction, n=2, L=5, gap=3):
    u = unit(direction)
    nr = (-u[1], u[0])
    out = ''
    for i in range(n):
        c = add(p, mul(u, (i - (n - 1) / 2) * gap))
        out += ln(add(c, mul(nr, L)), sub(c, mul(nr, L)), 1.0)
    return out


DOTS = ('<defs><pattern id="dots" width="3" height="3" patternUnits="userSpaceOnUse">'
        '<rect width="3" height="3" fill="#e6e6e6"/><circle cx="1" cy="1" r="0.6" fill="#999"/></pattern>'
        '<pattern id="dots2" width="3" height="3" patternUnits="userSpaceOnUse">'
        '<rect width="3" height="3" fill="#cfcfcf"/><circle cx="1" cy="1" r="0.7" fill="#777"/></pattern></defs>')


def fig(pg, box_, inner, defs=DOTS):
    x0, y0, x1, y1 = box_
    return (f'<svg class="fig" style="left:{X(x0):.2f}mm;top:{Y(pg, y0):.2f}mm;width:{(x1 - x0) * K:.2f}mm;'
            f'height:{(y1 - y0) * K:.2f}mm" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}" '
            f'xmlns="http://www.w3.org/2000/svg">{defs}{inner}</svg>')


# ================================================================ 그림
def f1():
    x0, x1, y0 = 233.3, 412, 554.3
    unit_ = 29.5
    s = f'<rect x="{x0}" y="376.7" width="{x1 - x0}" height="{y0 - 376.7}" fill="none" stroke="#111" stroke-width="1.3"/>'
    for v in range(1, 6):
        y = y0 - v * unit_
        s += ln((x0, y), (x1, y), 0.7, '1.5,2', '#888')
    for (a, b), h in zip(((255, 274), (284.7, 304), (314.3, 334), (344.7, 364), (375, 394.3)), (2, 4, 5, 3, 1)):
        s += f'<rect x="{a}" y="{y0 - h * unit_:.1f}" width="{b - a:.1f}" height="{h * unit_:.1f}" fill="url(#dots)" stroke="#111" stroke-width="1.8"/>'
    for v in range(0, 6):
        s += tx((223.3, y0 - v * unit_), str(v), 17)
    for i, x in enumerate((264, 294, 324, 354, 384.3)):
        s += tx((x, 566.7), str(i + 1), 17)
    s += tx((404, 566.7), '(회)', 15, cls='ko') + tx((218, 381.7), '(명)', 15, cls='ko')
    return fig(1, (205, 368, 425, 578), s)


def cloud(o, cen, a, b, deg, n, seed, rim=False):
    rnd = random.Random(seed)
    th = math.radians(deg)
    out = ''
    pts = []
    while len(pts) < n:
        u, v = rnd.uniform(-1, 1), rnd.uniform(-1, 1)
        if u * u + v * v <= 1:
            pts.append((u, v))
    if rim:
        pts += [(math.cos(t * 2 * math.pi / 44), math.sin(t * 2 * math.pi / 44)) for t in range(44)]
    for u, v in pts:
        x = cen[0] + u * a * math.cos(th) - v * b * math.sin(th)
        y = cen[1] - (u * a * math.sin(th) + v * b * math.cos(th))
        out += f'<circle cx="{o[0] + x:.2f}" cy="{o[1] + y:.2f}" r="0.95" fill="#222"/>'
    return out


def f2():
    s = ''
    panels = [((125, 919), (37, -36), 40, 8.5, -45, 100, True), ((258, 919), (36, -35), 36, 21, -35, 190, False),
              ((391, 919), (35, -39), 16, 32, 0, 140, False), ((125, 1015), (35, -35), 40, 8.5, 45, 100, True),
              ((258, 1015), (34, -38), 36, 21, 40, 190, False)]
    for k, (o, cen, a, b, deg, n, rim) in enumerate(panels):
        s += ln(o, (o[0] + 72, o[1]), 1.1) + arrowhead((o[0] + 75, o[1]), (1, 0), 5)
        s += ln(o, (o[0], o[1] - 72), 1.1) + arrowhead((o[0], o[1] - 75), (0, -1), 5)
        s += tx((o[0] - 6, o[1] - 72), 'y', 11, italic=True) + tx((o[0] + 74, o[1] + 8), 'x', 11, italic=True)
        s += cloud(o, cen, a, b, deg, n, k + 7, rim)
        s += tx((o[0] - 25, o[1] - 32), MARK[k], 16, cls='ko')
    return fig(1, (88, 840, 475, 1030), s)


def f4():
    c, r = (777.7, 356.3), 107
    s = circle(c, r, 1.3)
    for dy, (l1, l2) in ((-55.3, ('A', 'D')), (65.4, ('B', 'C'))):
        y = c[1] + dy
        dx = math.sqrt(r * r - dy * dy)
        p, q = (c[0] - dx, y), (c[0] + dx, y)
        s += ln(p, q, 1.3) + dot(p, 2) + dot(q, 2) + arrowhead((c[0] + 4, y), (1, 0), 7)
        s += tx((p[0] - 9, y - 4), l1, 14, cls='sf') + tx((q[0] + 9, y - 4), l2, 14, cls='sf')
    s += dot(c, 2) + tx((c[0], c[1] + 12), 'O', 14, cls='sf')
    return fig(1, (655, 240, 900, 470), s)


def f6():
    c, r = (302, 367), 115
    hb = 4.5 / 6 * r
    B, C = (c[0] - hb, c[1] + math.sqrt(r * r - hb * hb)), (c[0] + hb, c[1] + math.sqrt(r * r - hb * hb))
    A = (c[0], c[1] - r)
    s = circle(c, r, 1.6) + poly([A, B, C], sw=1.6) + ln(c, B, 1.6) + dot(c, 3)
    s += qcurve(add(c, (2, 8)), (290, 420), add(B, (8, 2)), 1.1, '4,3')
    s += qcurve(add(B, (6, 3)), (302, 468), add(C, (-6, 3)), 1.1, '4,3')
    s += tx((299, 418), '6cm', 21) + '<rect x="282" y="455" width="40" height="18" fill="#fff"/>' + tx((302, 464), '9cm', 21)
    s += tx((A[0], A[1] - 14), 'A', 22) + tx((c[0] + 22, c[1] - 7), 'O', 22)
    s += tx((B[0] - 18, B[1] + 6), 'B', 22) + tx((C[0] + 17, C[1] + 6), 'C', 22)
    return fig(2, (180, 225, 425, 485), s)


def f7():
    c, r = (304.3, 987.7), 114.2
    A, B, P = (247.7, 888.3), (382.7, 905.7), (194.3, 1101.7)
    A = polar(c, r, ang(c, A))
    B = polar(c, r, ang(c, B))
    T = (c[0], c[1] + r)
    Cc = second_hit(c, r, B, P)
    s = circle(c, r, 1.6) + ln((162, T[1]), (447, T[1]), 1.6) + ln(P, B, 1.6) + ln(A, T, 1.6) + ln(A, B, 1.6) + dot(c, 4)
    s += angle_arc(A, B, T, 17) + angle_arc(P, T, B, 22)
    s += tx((278, 917), '66°', 21) + tx((231, 1091), 'x', 20, italic=True)
    s += tx((A[0] - 10, A[1] - 13), 'A', 22) + tx((B[0] + 16, B[1] - 8), 'B', 22) + tx((c[0] + 4, c[1] + 22), 'O', 22)
    s += tx((Cc[0] - 13, Cc[1] - 9), 'C', 22) + tx((P[0], P[1] + 16), 'P', 22) + tx((T[0], T[1] + 16), 'T', 22)
    return fig(2, (155, 855, 455, 1130), s)


def f11():
    c, r = (397.6, 1008), 94.2
    P = (132.5, 1008)
    A, B, Cc, D = polar(c, r, 111), polar(c, r, 249), polar(c, r, 37), polar(c, r, -37)
    far = lambda q: add(P, mul(unit(sub(q, P)), 335))
    s = circle(c, r, 1.6) + ln(P, far(A), 1.2) + ln(P, far(B), 1.2)
    s += ln(c, A, 1.2) + ln(c, B, 1.2) + ln(A, D, 1.2) + ln(B, Cc, 1.2) + ln(B, D, 1.2) + dot(c, 3)
    s += angle_arc(P, A, B, 26) + tx((172, 1008), '42°', 19)
    X_ = inter(A, D, B, Cc)
    s += angle_arc(X_, Cc, D, 16) + tx((X_[0] + 27, X_[1]), 'x', 19, italic=True)
    for a in (74, 286, 0):
        p = polar(c, r, a)
        s += ticks_at(p, (-math.sin(math.radians(a)), -math.cos(math.radians(a))), 2, 4.5, 3)
    s += tx((A[0] - 4, A[1] - 15), 'A', 20) + tx((Cc[0] + 13, Cc[1] - 11), 'C', 20) + tx((D[0] + 13, D[1] + 13), 'D', 20)
    s += tx((B[0] - 3, B[1] + 17), 'B', 20) + tx((P[0] - 12, P[1]), 'P', 20) + tx((c[0] - 13, c[1]), 'O', 20)
    return fig(3, (100, 885, 510, 1132), s)


def f12():
    O = (681.7, 500)
    s = ln((660, 500), (890, 500), 1.1) + arrowhead((895, 500), (1, 0), 7)
    s += ln((681.7, 521.7), (681.7, 322), 1.1) + arrowhead((681.7, 316), (0, -1), 7)
    s += poly([(681.7, 436), (743.3, 436), (793.3, 386.7), (895, 386.7)], close=False, sw=1.4)
    s += ln((743.3, 436), (743.3, 500), 1.1, '4,3') + ln((793.3, 386.7), (793.3, 500), 1.1, '4,3')
    s += tx((665, 323), 'y', 15, italic=True) + tx((887, 510), 'x', 15, italic=True) + tx((670, 510), 'O', 14, cls='sf')
    s += tx((743.3, 513), '㉠', 13, cls='ko') + tx((793.3, 513), '㉡', 13, cls='ko')
    return fig(3, (655, 312, 900, 522), s)


def f13():
    s = ''
    for k, (title, vals, fill) in enumerate((('A', (2, 2, 2, 2, 2), 'dots'), ('B', (1, 2, 4, 2, 1), 'dots'),
                                             ('C', (3, 1, 2, 1, 3), 'dots2'))):
        dx = k * 156.1
        x0, x1, y0, yt = 593.3 + dx, 697.5 + dx, 1016.7, 936.3
        u = (y0 - 953.75) / 4
        s += f'<rect x="{x0:.1f}" y="{yt}" width="{x1 - x0:.1f}" height="{y0 - yt:.1f}" fill="none" stroke="#111" stroke-width="1.1"/>'
        for v in range(1, 5):
            s += ln((x0, y0 - v * u), (x1, y0 - v * u), 0.6, '1.5,1.5', '#777')
        for i, (cx, h) in enumerate(zip((607, 625.8, 644.6, 663.3, 680.8), vals)):
            cx += dx
            s += f'<rect x="{cx - 4.5:.1f}" y="{y0 - h * u:.1f}" width="9" height="{h * u:.1f}" fill="url(#{fill})" stroke="#111" stroke-width="1"/>'
            s += tx((cx, 1026), str(6 + i), 10.5, cls='bd')
        for v in range(0, 5):
            s += tx((x0 - 6.5, y0 - v * u), str(v), 10.5, cls='bd')
        s += tx((x0 - 13, 935.5), '(명)', 9.5, cls='ko bd') + tx((x1 + 12, 1026), '(점)', 9.5, cls='ko bd')
        s += tx(((x0 + x1) / 2 - 2, 923.7), title, 12, cls='bd')
    return fig(3, (562, 912, 1015, 1034), s)


def f14():
    c, r = (299.7, 384.6), 109.5
    P = (300, 375.5)
    s = circle(c, r, 1.6)
    pts = {}
    for name, dirn in (('AB', 20.5), ('CD', -19.5)):
        u = (math.cos(math.radians(dirn)), -math.sin(math.radians(dirn)))
        f = sub(P, c)
        b_ = f[0] * u[0] + f[1] * u[1]
        disc = math.sqrt(b_ * b_ - (f[0] ** 2 + f[1] ** 2 - r * r))
        p1, p2 = add(P, mul(u, -b_ + disc)), add(P, mul(u, -b_ - disc))
        pts[name[1]], pts[name[0]] = p1, p2
        s += ln(p1, p2, 1.5)
    A, B, C, D = pts['A'], pts['B'], pts['C'], pts['D']
    s += dot(c, 3.2) + angle_arc(P, B, D, 22)
    s += tx((351, 375), '40°', 22) + tx((P[0], P[1] - 17), 'P', 22) + tx((c[0], c[1] + 18), 'O', 22)
    s += tx((B[0] + 14, B[1] - 6), 'B', 22) + tx((A[0] - 13, A[1] + 9), 'A', 22)
    s += tx((C[0] - 13, C[1] - 9), 'C', 22) + tx((D[0] + 14, D[1] + 7), 'D', 22)
    return fig(4, (170, 268, 430, 500), s)


SC = [(60, 60), (65, 95), (65, 70), (65, 65), (70, 85), (70, 65), (75, 80), (75, 75), (80, 90), (80, 80),
      (80, 75), (80, 70), (80, 65), (85, 85), (85, 75), (85, 70), (90, 95), (90, 90), (90, 80), (95, 95)]


def f16():
    Xs = lambda v: 753.1 + (v - 60) * 3.172
    Ys = lambda v: 397.2 - (v - 60) * 3.22
    s = ''
    for v in range(55, 106, 5):
        s += ln((Xs(v), Ys(50)), (Xs(v), Ys(105)), 0.6, '1.2,1.2', '#666')
        s += ln((Xs(50), Ys(v)), (Xs(105), Ys(v)), 0.6, '1.2,1.2', '#666')
    s += ln((Xs(105), Ys(50)), (Xs(105), Ys(105)), 0.8) + ln((Xs(50), Ys(105)), (Xs(105), Ys(105)), 0.8)
    s += ln((Xs(50), Ys(50)), (892, Ys(50)), 1.1) + arrowhead((896, Ys(50)), (1, 0), 6)
    s += ln((Xs(50), Ys(50)), (Xs(50), 257), 1.1) + arrowhead((Xs(50), 253), (0, -1), 6)
    for p in ((Xs(51.6), Ys(50)), (Xs(50), Ys(51.6))):
        s += f'<rect x="{p[0] - 2.5:.1f}" y="{p[1] - 2.5:.1f}" width="5" height="5" fill="#fff"/>'
    s += qcurve((Xs(51.6) - 2.5, Ys(50) + 3), (Xs(51.6) - 1, Ys(50)), (Xs(51.6) - 2.5, Ys(50) - 3), 0.7)
    s += qcurve((Xs(51.6) + 1.5, Ys(50) + 3), (Xs(51.6) + 3, Ys(50)), (Xs(51.6) + 1.5, Ys(50) - 3), 0.7)
    s += qcurve((Xs(50) - 3, Ys(51.6) + 2.5), (Xs(50), Ys(51.6) + 1), (Xs(50) + 3, Ys(51.6) + 2.5), 0.7)
    s += qcurve((Xs(50) - 3, Ys(51.6) - 1.5), (Xs(50), Ys(51.6) - 3), (Xs(50) + 3, Ys(51.6) - 1.5), 0.7)
    for v in (60, 70, 80, 90, 100):
        s += tx((711, Ys(v)), str(v), 12.5, anchor='end') + tx((Xs(v), 441.5), str(v), 12.5)
    s += tx((714, 441.5), 'O', 12.5)
    for x_, y_ in SC:
        s += dot((Xs(x_), Ys(y_)), 2.3)
    s += tx((668.8, 259), '실', 12, cls='ko') + tx((668.8, 277), '기', 12, cls='ko') + tx((668.8, 297), '(점)', 11, cls='ko')
    s += tx((873, 460.5), '필기(점)', 12, cls='ko')
    return fig(4, (655, 248, 905, 472), s)


def f18():
    c, r = (236.2, 1061.2), 103.8
    A, B, D, C = polar(c, r, 130), polar(c, r, 50), polar(c, r, 1), polar(c, r, 240)
    E = inter(A, B, C, D)
    s = circle(c, r, 1.5) + ln(A, E, 1.5) + ln(C, E, 1.5) + ln(A, D, 1.5)
    rr = r + 7
    s += arcp(c, rr, 54, 126, 0.9) + arrowhead(polar(c, rr, 128), (-0.65, 0.76), 6) + arrowhead(polar(c, rr, 52), (0.65, 0.76), 6)
    s += arcp(c, rr, 244, 357, 0.9) + arrowhead(polar(c, rr, 242), (-0.87, -0.5), 6) + arrowhead(polar(c, rr, 359), (0, -1), 6)
    s += angle_arc(A, B, D, 20) + angle_arc(E, A, C, 22)
    s += tx((233.5, 945), '4π cm', 21) + tx((340, 1146), '6π cm', 21) + tx((404, 998), '30°', 21)
    s += tx((222, 1054.6), 'O.', 21, cls='bd') + tx((A[0] - 13, A[1] - 3), 'A', 21) + tx((B[0] + 12, B[1] - 10), 'B', 21)
    s += tx((D[0] + 15, D[1] + 7), 'D', 21) + tx((C[0] - 7, C[1] + 13), 'C', 21)
    return fig(5, (130, 930, 478, 1178), s)


def f19():
    side = 243
    A = (776.2, 296.3)
    B, C = (A[0] - side / 2, A[1] + side * math.sqrt(3) / 2), (A[0] + side / 2, A[1] + side * math.sqrt(3) / 2)
    c, r = (A[0], A[1] + side / math.sqrt(3)), side / math.sqrt(3)
    D, E, F = mid(A, B), mid(A, C), mid(B, C)
    Xp, Yp = second_hit(c, r, polar(c, r, 0), polar(c, r, 0)) if False else (None, None)

    def ext(p, q):
        u = unit(sub(q, p))
        f = sub(p, c)
        b_ = f[0] * u[0] + f[1] * u[1]
        disc = math.sqrt(b_ * b_ - (f[0] ** 2 + f[1] ** 2 - r * r))
        return add(p, mul(u, -b_ + disc)), add(p, mul(u, -b_ - disc))
    Y_, X_ = ext(D, F)
    Z_, W_ = ext(E, F)
    s = poly([A, B, C], fill='url(#dots)', sw=1.6) + circle(c, r, 1.6) + ln(X_, Y_, 1.6) + ln(W_, Z_, 1.6)
    for p in (X_, Y_, Z_, W_, F):
        s += dot(p, 1.6)
    lab = lambda p, t, dx, dy: tx((p[0] + dx, p[1] + dy), t, 13, cls='sf')
    s += lab(A, 'A', 0, -11) + lab(X_, 'X', -9, -10) + lab(W_, 'W', 11, -10) + lab(D, 'D', -12, 0) + lab(E, 'E', 12, 0)
    s += lab(B, 'B', -14, 0) + lab(C, 'C', 13, 0) + lab(F, 'F', 0, 13) + lab(Z_, 'Z', -4, 15) + lab(Y_, 'Y', 4, 15)
    return fig(5, (630, 278, 925, 605), s)


def f20():
    c, r = (303.3, 421.6), 146.7
    A, B, T = polar(c, r, 50), polar(c, r, 230), (c[0], c[1] + r)
    P = inter(A, B, T, (T[0] + 10, T[1]))
    tb = (-math.sin(math.radians(230)), -math.cos(math.radians(230)))
    Qp = inter(B, add(B, tb), T, (T[0] + 10, T[1]))
    Cc = (421.7, T[1])
    s = circle(c, r, 1.1) + ln(P, A, 1.1) + ln(A, T, 1.1) + ln((P[0] - 4, T[1]), (465, T[1]), 1.1)
    u = unit(sub(Qp, B))
    s += ln(sub(B, mul(u, 50)), add(Qp, mul(u, 38)), 1.1)
    for p in (A, c, B, P, Qp, T, Cc):
        s += dot(p, 2.4)
    s += angle_arc(T, Cc, A, 13, 0.9) + tx((T[0] + 30, T[1] - 20), '70°', 12)
    lab = lambda p, t, dx, dy: tx((p[0] + dx, p[1] + dy), t, 14, cls='sf')
    s += lab(A, 'A', 13, -8) + lab(c, 'O', -14, -8) + lab(B, 'B', -18, -2) + lab(P, 'P', -6, 15)
    s += lab(Qp, 'Q', -6, 17) + lab(T, 'T', 0, 17) + lab(Cc, 'C', 0, 17)
    return fig(6, (130, 268, 475, 598), s)


def f21():
    A, B, F, G, C = (813.2, 401.8), (581.8, 689.1), (695.5, 689.1), (873.6, 689.1), (971.4, 689.1)
    c, r = circ3(A, F, G)
    D = second_hit(c, r, A, B)
    E = second_hit(c, r, A, C)
    s = poly([E, G, C], fill='url(#dots)', sw=0) + circle(c, r, 1.1)
    s += poly([A, B, C], sw=1.2) + ln(A, G, 1.2) + ln(D, F, 1.2) + ln(E, G, 1.2)
    lab = lambda p, t, dx, dy: tx((p[0] + dx, p[1] + dy), t, 15)
    s += lab(A, 'A', 0, -9) + lab(D, 'D', -10, -1) + lab(E, 'E', 11, -1) + lab(B, 'B', -6, 13)
    s += lab(F, 'F', 0, 13) + lab(G, 'G', 1, 13) + lab(C, 'C', 7, 13)
    s += tx((648.6, 455), 'O', 15, italic=True)
    return fig(6, (565, 390, 990, 712), s)


# ================================================================ 쪽 내용
def bogi(pg, x0, y0, x1, y1, ty, rows):
    s = box(pg, x0, y0, x1, y1)
    s += L(pg, ty, (x0 + x1) / 2 - 30, '&lt;보기&gt;', cls='bt')
    for y, x, t in rows:
        s += L(pg, y, x, t)
    return s


def cont(pg, y, t):
    return f'<div class="ln cont" style="right:{210 - X(996):.2f}mm;top:{Y(pg, y):.2f}mm">{t}</div>'


def P1():
    s = L(1, 165, 85, '※ 아래 표와 같이 모든 문항은 차등배점입니다.', cls='b')
    s += table(1, [88, 168, 290, 410, 530], [187, 211, 235],
               [['번호', '1번 ~ 6번', '7번 ~ 10번', '11번 ~ 15번'], ['배점', '4.2점', '4.4점', '4.6점']], lambda r, c: False)
    s += table(1, [88, 168, 350, 530], [235, 259, 283],
               [['번호', '16번 ~ 19번', '20점 ~ 22번'], ['배점', '4.8점', '5점']], lambda r, c: False)
    s += Q(1, 'L', [304, 333], ['1. 아래 그림은 윗몸일으키기 횟수를 조사하여 나타낸', '막대그래프이다. 이 자료의 최빈값은? (4.2점)'])
    s += f1()
    s += CH(1, 'L', [603, 634, 665], ['$4$ 명', '$5$ 명', '$2$ 회', '$3$ 회', '$4$ 회'], xs=(90, 290))
    s += Q(1, 'L', [768, 797], ['2. 다음 중 음의 상관관계가 가장 강하게 나타나는', '것은? (4.2점)'])
    s += f2()
    s += Q(1, 'L', [1140, 1168], ['3. 다음 중 두 변량 사이의 관계가 나머지 넷과 <b><u>다른</u></b>', '것은? (4.2점)'])
    for i, (y, t) in enumerate(zip((1230, 1261, 1291, 1321, 1351),
                                   ('통학 시간과 수학 성적', '배추의 생산량과 배추 가격', '하루 중 낮의 길이와 밤의 길이',
                                    '겨울철 기온과 난방비', '해발 고도와 산소의 양'))):
        s += L(1, y, 92, f'<span class="cm">{MARK[i]}</span> {t}', cls='ch big')
    s += Q(1, 'R', [171, 201], ['4. 아래 원 O 에서 $[AD]$ ∥ $[BC]$ 일 때, 보기에서 옳은', '것을 모두 고르면? (4.2점)'])
    s += f4()
    s += bogi(1, 564, 483, 996, 607, 501, [(543, 572, '㉠ $^AB^=^CD^$'), (543, 788, '㉡ $[AB]=[CD]$'),
                                           (588, 572, '㉢ $^AD^=^BC^$'), (588, 788, '㉣ $[AD]=[BC]$')])
    s += CH(1, 'R', [651, 680], ['㉠, ㉡', '㉠, ㉢', '㉡, ㉣', '㉢, ㉣', '㉠, ㉡, ㉢, ㉣'])
    s += Q(1, 'R', [890, 920], ['5. 아래 보기의 사각형 중 항상 원에 내접하는 것의', '개수는? (4.2점)'])
    s += bogi(1, 565, 942, 997, 1080, 960, [(995, 573, '㉠ 평행사변형'), (995, 788, '㉡ 마름모'),
                                            (1029, 573, '㉢ 직사각형'), (1029, 788, '㉣ 정사각형'), (1062, 573, '㉤ 등변사다리꼴')])
    s += CH(1, 'R', [1128, 1160], ['$1$ 개', '$2$ 개', '$3$ 개', '$4$ 개', '$5$ 개'])
    return s + cont(1, 1427, '&lt; 다음 면에 계속... &gt;')


DIALOG = [(258, '재석 : 이거 얼마씩 받은 지 서로 모르는 거죠?', 0),
          (297, '제작진 : 네 제작진만 알고 있습니다. 여기 계신 네', 1), (323, '분이 각자 받으신 금액의 평균 금액만 알려드리겠', 1),
          (350, '습니다.', 0), (388, '왕코 : 아 뭐야 난 평균 금액보다 <b>2,000원이나 적잖아</b>', 1), (416, '좀 더 줘!!', 0),
          (456, '재석 : 형 그걸 말하면 어떡해요', 0), (495, '왕코 : 왜 말하면 안 돼?', 0),
          (521, '(제작진을 쳐다보며) 안되는거에...요?', 0), (557, '제작진 : 말씀하셔도 됩니다. 대신 거짓말하시면', 0),
          (584, '안 돼요', 0), (626, '히히 : 아 그래요? 전 말 안 할래요 근데 왕코형보다', 1),
          (653, '적어요 진심 맹세 하나님께 맹세', 0), (692, '재석 : 어? 나는 평균금액보다 <b>5,000원 더 받았는데</b>?', 1),
          (732, '국종 : (아 내가 제일 많이 받은 줄 알았는데 재석', 1),
          (758, '이형보다 <b>2,000원 덜 받았네</b>) 자자 일단 게임하러', 1), (783, '갑시다!', 0)]


def P2():
    s = Q(2, 'L', [134, 170, 201], ['6. 다음 그림과 같이 반지름 길이가 $6$cm 인 원에 내',
                                    '접하는 △ABC 에서 $[BC]=9$cm 일 때, sinA 의 값', '은? (4.2점)'])
    s += f6()
    s += CH(2, 'L', [544, 603], ['$' + fr('2', '3') + '$', '$' + fr(sq('7'), '4') + '$', '$' + fr('3', '4') + '$',
                                 '$' + fr(sq('6'), '2') + '$', '$' + fr(sq('7'), '3') + '$'])
    s += Q(2, 'L', [788, 817], ['7. 다음 그림에서 $~PT~$ 가 원의 접선일 때, ∠$x$ 의', '크기는? (4.4점)'])
    s += f7()
    s += CH(2, 'L', [1182, 1213], ['$38$˚', '$39$˚', '$40$˚', '$41$˚', '$42$˚'])
    s += Q(2, 'R', [132, 161, 190, 219], ["8. 다음은 인기 TV 프로그램 ‘워킹맨’에서 재석팀 4명이",
                                         '서로가 받은 미션 금액에 대해 나눈 대화이다. 미션',
                                         '금액이 가장 많은 사람과 가장 적은 사람의 차이는', '얼마인가? (4.4점)'])
    s += box(2, 563, 241, 998, 802)
    for y, t, j in DIALOG:
        s += L(2, y, 572, t, 990 if j else None, cls='dl')
    s += CH(2, 'R', [848, 879], ['$7,000$ 원', '$8,000$ 원', '$9,000$ 원', '$10,000$ 원', '$11,000$ 원'])
    s += Q(2, 'R', [1073], ['9. 다음 중 옳은 것은? (4.4점)'])
    s += CHL(2, 'R', [(1112, 0, '중앙값은 반드시 1개이다.'), (1143, 1, '최빈값은 항상 1개 존재한다.'),
                      (1174, 2, '대푯값을 통해 변량의 분포 상태를 알 수 있다.'), (1205, 3, '변량의 개수가 많을수록 산포도도 커진다.'),
                      (1236, 4, '편차의 합이 작을수록 자료가 고르게 분포되어|'), (1263, None, '있다고 할 수 있다.')])
    return s + cont(2, 1425, '&lt; 다음 장에 계속... &gt;')


def P3():
    s = Q(3, 'L', [143, 174, 205, 235], ['10. 다음은 학생 20명의 수행 평가 점수를 조사하여',
                                         '표로 나타낸 것이다. 평균을 $a$ 점, 중앙값을 $b$ 점, 최',
                                         '빈값을 $c$ 점이라고 할 때, $a, b, c$ 의 대소 관계로 옳', '은 것은? (4.4점)'])
    s += table(3, [114, 232, 284, 336, 388, 440, 491], [274, 314, 354],
               [['점수(점)', '$6$', '$7$', '$8$', '$9$', '$10$'], ['학생 수(명)', '$1$', '$2$', '$7$', '$6$', '$4$']],
               lambda r, c: c == 0)
    s += CH(3, 'L', [399, 430], ['$b&lt;c&lt;a$', '$c&lt;a=b$', '$c&lt;b&lt;a$', '$a=c&lt;b$', '$c&lt;a&lt;b$'])
    s += Q(3, 'L', [806, 842], ['11. 그림에서 직선 PA, PB 는 원 O 의 접선이고',
                                '$^AC^=^CD^=^BD^$ 일 때, ∠$x$ 의 크기는? (4.6점)'])
    s += f11()
    s += CH(3, 'L', [1182, 1213], ['$104$˚', '$105$˚', '$106$˚', '$107$˚', '$108$˚'])
    s += Q(3, 'R', [144, 176, 206], ['12. 아래 그림은 다음 변량에서 $x$ 의 값에 따른 중앙',
                                     '값 $y$ 를 나타낸 함수의 그래프이다. ㉠과 ㉡ 의 값',
                                     '을 각각 $a, b$ 라 할 때, $b-a$ 의 값은? (4.6점)'])
    s += box(3, 563, 248, 997, 292)
    s += L(3, 270, 632, '$34&nbsp;&nbsp; 5&nbsp;&nbsp; 9&nbsp;&nbsp; x&nbsp;&nbsp; 14&nbsp;&nbsp; 47&nbsp;&nbsp; 25&nbsp;&nbsp; 10&nbsp;&nbsp; 43$', cls='nums')
    s += f12()
    s += CH(3, 'R', [575, 606], ['$9$', '$11$', '$15$', '$18$', '$20$'])
    s += Q(3, 'R', [814, 842, 871], ['13. 다음 그림은 A, B, C 세 학급의 수학 수행평가',
                                     '성적을 그래프로 나타낸 것이다. 다음 설명 중 옳은', '것은? (4.6점)'])
    s += f13()
    s += CHL(3, 'R', [(1078, 0, '성적이 가장 우수한 반은 B 반이다.'), (1109, 1, 'B 반과 C 반의 성적의 표준편차는 같다.'),
                      (1140, 2, 'A 반이 B 반보다 성적이 고르게 분포되어 있다.'),
                      (1171, 3, 'A 반 성적의 평균이 C 반 성적의 평균보다 낮다.'),
                      (1200, 4, 'A 반 성적의 산포도가 C 반 성적의 산포도 보다|'), (1230, None, '작다.')])
    return s + cont(3, 1440, '&lt; 다음 면에 계속... &gt;')


def P4():
    s = Q(4, 'L', [150, 186, 224], ['14. 그림과 같이 반지름의 길이가 $6$cm 인 원 O 에서',
                                    '$[AB]$ 와 $[CD]$ 가 점 P 에서 만나고 ∠BPD$=40$˚ 일',
                                    '때, $^AD^$ 와 $^BC^$ 의 길이의 합은? (4.6점)'])
    s += f14()
    s += CH(4, 'L', [557, 611], ['$' + fr('4', '3') + 'π$cm', '$' + fr('8', '3') + 'π$cm', '$' + fr('16', '3') + 'π$cm',
                                 '$' + fr('22', '3') + 'π$cm', '$' + fr('28', '3') + 'π$cm'])
    s += Q(4, 'L', [837, 865], ['15. 아래 표는 어느 학급 남학생과 여학생의 한달 휴대', '폰 데이터 사용량을 조사하여 나타낸 것이다.'])
    s += table(4, [91, 232, 374, 515], [887, 911, 935, 959, 983],
               [['성별', '남학생', '여학생'], ['학생 수', '$12$명', '$8$명'], ['평균', '$10$G', '$10$G'],
                ['표준편차', '$2$', '$' + sq('2') + '$']], lambda r, c: c == 0 or r == 0)
    s += Q(4, 'L', [1004, 1033, 1062, 1092], ['이 학급에 $8$G, $12$G 를 사용하는 여학생 각각 1명,',
                                              '$10$G 를 사용하는 여학생 2명 총 4명의 여학생이 추',
                                              '가된다면 이 학급 전체 학생의 데이터 사용량의 표준', '편차는? (4.6점)'])
    s += CH(4, 'L', [1147, 1180], ['$1$', '$' + sq('2') + '$', '$' + sq('3') + '$', '$2$', '$3$'])
    s += Q(4, 'R', [147, 177, 208], ['16. 다음 그림은 윤아네 반 학생 20명의 음악 평가에',
                                     '서 받은 실기 점수와 필기 점수에 대한 산점도이다. 다', '음 중 옳은 것은? (4.8점)'])
    s += f16()
    s += CHL(4, 'R', [(500, 0, '실기 점수의 최빈값은 $80$ 점이다.'),
                      (531, 1, '실기 점수가 $80$ 점 이상인 학생들의 필기 점수의|'), (563, None, '평균은 $82.5$ 점이다.'),
                      (593, 2, '필기 점수와 실기 점수 중 적어도 하나가 $80$ 점|'), (624, None, '미만인 학생은 $5$ 명 이다.'),
                      (655, 3, '필기 점수가 $70$ 점 이상인 학생 중에서 실기 점|'),
                      (686, None, '수가 $90$ 점 이상인 학생은 전체의 $20$% 이다.'),
                      (717, 4, '필기 점수와 실기 점수가 모두 $75$ 점 이하인 학생|'),
                      (748, None, '은 재시험을 본다고 할 때, 재시험률은 $20$% 이다.')])
    return s + cont(4, 1438, '&lt; 다음 장에 계속... &gt;')


def P5():
    s = Q(5, 'L', [128, 161, 195, 227], ['17. 아래 5개의 수 의 평균과 표준편차를 각각 $m, s$',
                                         '라 하자. 이 5개의 수에 2개의 수 $m-ks, m+ks$',
                                         '를 추가한 7개의 수의 표준편차는 $' + sq('2') + 's$ 일 때,', '양수 $k$ 의 값은? (4.8점)'])
    s += box(5, 82, 268, 516, 305)
    s += L(5, 287, 230, '$2&nbsp;&nbsp; 3&nbsp;&nbsp; 4&nbsp;&nbsp; 5&nbsp;&nbsp; 6$', cls='nums')
    s += CH(5, 'L', [344, 393], ['$' + fr(sq('2'), '2') + '$', '$' + fr('3' + sq('2'), '2') + '$', '$' + sq('2') + '$',
                                 '$2' + sq('2') + '$', '$3' + sq('2') + '$'])
    s += Q(5, 'L', [755, 786, 816, 846, 876], ['18. 다음 그림과 같이 반지름의 길이가 $9$cm 인 원',
                                              'O 에서 호 AB 와 호 CD 의 길이는 각각 $4π$cm,',
                                              '$6π$cm 이고, 선분 AB 와 선분 CD 의 연장선이 만',
                                              '나서 이루는 예각의 크기가 $30$˚ 일 때, ∠BAD 의', '크기는? (4.8점)'])
    s += f18()
    s += CH(5, 'L', [1221, 1252], ['$10$˚', '$25$˚', '$40$˚', '$55$˚', '$65$˚'])
    s += Q(5, 'R', [127, 163, 195, 230], ['19. 한 변의 길이가 $8$ 인 정삼각형 ABC 에서 각 변의',
                                          '중점을 $D, E, F$ 라 하자. $[DF]$ 와 $[EF]$ 의 연장선이 삼',
                                          '각형 ABC 의 외접원과 만나는 점을 각각 $X, Y, Z, W$',
                                          '라 할 때, $[XY]+[ZW]$ 의 길이는? (4.8점)'])
    s += f19()
    s += CH(5, 'R', [641, 676], ['$2' + sq('5') + '$', '$4' + sq('5') + '$', '$6' + sq('5') + '$',
                                 '$8' + sq('5') + '$', '$10' + sq('5') + '$'], xs=(562, 695, 828))
    return s + cont(5, 1402, '&lt; 다음 면에 계속... &gt;')


def P6():
    s = Q(6, 'L', [136, 168, 200, 232], ['20. 다음 그림의 원 O 에서 $~PT~$는 접선이고 $[AB]$ 는',
                                         '지름이다. ∠ATC$=70$˚ 이고, 점 B 에서 그은 원의',
                                         '접선이 $~PT~$ 와 만나는 점을 Q 라 할 때, 보기의 내',
                                         '용 중 옳은 것의 개수는? (5점)'])
    s += f20()
    s += bogi(6, 89, 625, 520, 743, 643, [(681, 97, '㉠ $^BT^$ : $^TA^$ $=2:7$'), (681, 316, '㉡∠BQT$=2$∠ATC'),
                                          (722, 97, '㉢ $[OQ]$//$[AT]$'), (722, 316, '㉣ $[PT]$<sup>2</sup>$=[PB]$×$[PA]$')])
    s += CH(6, 'L', [787, 818], ['$1$ 개', '$2$ 개', '$3$ 개', '$4$ 개', '없다.'])
    s += Q(6, 'R', [131, 163, 192], ['21. 아래 그림이 보기의 조건을 만족하고 삼각형 EGC',
                                     '의 넓이를 $s$ 라 할 때, 삼각형 ABC 의 넓이를 $s$ 를 이', '용해 나타낸 값은? (5점)'])
    s += bogi(6, 563, 214, 993, 365, 233, [(272, 572, '㉠ $[AD]=3[EG]$'), (310, 572, '㉡ 호 DF 와 호 EG 의 길이는 같다.'),
                                           (347, 572, '㉢ △DBF 는 이등변 삼각형이다.')])
    s += f21()
    s += CH(6, 'R', [751, 782], ['$16s$', '$14s$', '$12s$', '$10s$', '$9s$'])
    return s + cont(6, 1421, '&lt; 다음 장에 계속... &gt;')


def P7():
    s = Q(7, 'L', [131, 162, 193, 224], ['22. 9개의 자연수로 이루어진 자료의 평균과 중앙값은',
                                         '$19$ 이고, 최빈값은 $17$ 이다. 이 자료에서 가장 큰',
                                         '변량을 $x$ 라고 할 때, $x$ 의 값이 될 수 있는 가장', '작은 수는? (5점)'])
    s += CH(7, 'L', [281, 313], ['$19$', '$20$', '$21$', '$22$', '$23$'])
    s += L(7, 1425, 662, '✿ &nbsp;수 고 하 셨 습 니 다&nbsp; ✿', cls='thx')
    return s


# ================================================================ 머리글·틀
def header(n):
    if n == 1:
        cells = ('<tr><td class="h" style="width:{w0}mm">2025학년도 2학기 기말고사</td>'
                 '<td class="h sch" style="width:{w1}mm">잠실여자중학교</td>'
                 '<td rowspan="2" style="width:{w2}mm">선택형</td><td rowspan="2" style="width:{w3}mm">22문항</td>'
                 '<td rowspan="2" style="width:{w4}mm">100점</td><td class="pg" style="width:{w5}mm">page</td></tr>'
                 '<tr><td class="h">11월 4일 화요일 1교시</td><td class="h">3학년 &nbsp;수학과</td><td class="pg">1/7</td></tr>')
        xs = [62, 385, 690, 773, 868, 955, 1021]
        hpx = 80
    else:
        cells = ('<tr><td class="h" style="width:{w0}mm">2025학년도 2학기 기말고사</td>'
                 '<td class="h" style="width:{w1}mm">11월 &nbsp;4일 &nbsp;화 요 일 &nbsp;1교시</td>'
                 '<td class="h" style="width:{w2}mm">3학년 &nbsp;수학과</td><td class="pg" style="width:{w3}mm">page</td>'
                 '<td class="pg" style="width:{w4}mm">' + f'{n}/7' + '</td></tr>')
        xs = [62, 385, 690, 890, 960, 1021]
        hpx = 44
    ws = {f'w{i}': f'{(xs[i + 1] - xs[i]) * K:.2f}' for i in range(len(xs) - 1)}
    return (f'<table class="hd" style="left:{FL:.2f}mm;top:{FT:.2f}mm;width:{(1021 - 62) * K - 0.4:.2f}mm;'
            f'height:{hpx * K:.2f}mm">{cells.format(**ws)}</table>'), hpx


def page(n, body):
    hd, hpx = header(n)
    div = (f'<div class="div" style="left:{X(542):.2f}mm;top:{FT + hpx * K:.2f}mm;'
           f'height:{FH - hpx * K:.2f}mm"></div>')
    foot = ('<div class="foot">이 시험문제의 저작권은 잠실여자중학교에 있습니다. 무단 전송 · 복제 · 배포시 '
            '저작권법에 의거 처벌 될 수 있습니다.</div>')
    return f'<section class="page"><div class="frame"></div>{hd}{div}{body}{foot}</section>'


CSS = r'''
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #fff; color: #111; }
body { font-family: "NanumGothic", "Noto Sans CJK KR", sans-serif; font-size: 10.4pt; }
.page { width: 210mm; height: 297mm; position: relative; page-break-after: always; overflow: hidden; }
.page:last-child { page-break-after: auto; }
.frame { position: absolute; left: 10.5mm; top: 7.5mm; width: 189mm; height: 278.1mm; border: 1.5px solid #111; }
.div { position: absolute; border-left: 1px solid #222; }
.ln { position: absolute; white-space: nowrap; transform: translateY(-50%); line-height: 1.3; letter-spacing: -0.1px; }
.jj { text-align: justify; text-align-last: justify; }
.b { font-weight: bold; }
.big { font-size: 11.3pt; }
.dl { font-size: 10.2pt; }
.m { font-family: "Liberation Serif", "Times New Roman", serif; font-size: 1.1em; font-weight: bold; }
.m i { font-style: italic; }
.ln sup { font-size: 0.65em; vertical-align: 0.6em; line-height: 0; }
.op { margin: 0 0.2em; }
.ov { display: inline-block; border-top: 1px solid #111; line-height: 1.02; padding-top: 0.5px; font-weight: normal; }
.arc, .lin { display: inline-block; line-height: 1.02; padding-top: 0.42em; background-repeat: no-repeat; font-weight: normal; }
.arc { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 20' preserveAspectRatio='none'%3E%3Cpath d='M2 18 Q50 -6 98 18' fill='none' stroke='black' stroke-width='5'/%3E%3C/svg%3E");
  background-size: 100% 0.36em; background-position: 0 0.05em; }
.lin { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 10 10'%3E%3Cpath d='M1 1 L9 5 L1 9 Z' fill='black'/%3E%3C/svg%3E"), url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 10 10'%3E%3Cpath d='M9 1 L1 5 L9 9 Z' fill='black'/%3E%3C/svg%3E"), linear-gradient(#000, #000);
  background-size: 0.33em 0.33em, 0.33em 0.33em, calc(100% - 0.1em) 1px; background-position: right 0.06em, left 0.06em, 0.05em 0.21em; }
.sq { white-space: nowrap; font-weight: bold; }
.sq .rc { border-top: 1px solid #111; padding: 0 1px; margin-left: -1px; }
.fr { display: inline-flex; flex-direction: column; vertical-align: middle; text-align: center; line-height: 1.12; margin: 0 2px; }
.fr .fn { border-bottom: 1px solid #111; padding: 0 2px; }
.cm { font-family: "NanumGothic", sans-serif; font-weight: normal; }
.ch { font-size: 10.8pt; }
.bx { position: absolute; border: 1px solid #222; }
.bt { font-size: 10.6pt; }
.nums { letter-spacing: 1px; }
table.tb { position: absolute; border-collapse: collapse; text-align: center; font-size: 10.4pt; }
table.tb td { border: 1px solid #222; padding: 0; line-height: 1; }
table.tb td.sh { background: #a9a9a9 url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='3' height='3'%3E%3Ccircle cx='1' cy='1' r='0.6' fill='%23666'/%3E%3C/svg%3E"); }
table.hd { position: absolute; border-collapse: collapse; table-layout: fixed; text-align: center;
  font-family: "NanumMyeongjo", serif; font-weight: bold; font-size: 12.2pt; }
table.hd td { border: 1.3px solid #111; padding: 0; white-space: nowrap; line-height: 1; }
table.hd td.pg { font-family: "Liberation Serif", serif; font-size: 12pt; }
table.hd td.sch { letter-spacing: 2px; }
.fig { position: absolute; overflow: visible; }
.fig text { font-family: "Liberation Serif", "Times New Roman", serif; fill: #111; }
.fig text.ko { font-family: "NanumGothic", sans-serif; }
.fig text.sf { font-family: "Liberation Sans", "NanumGothic", sans-serif; }
.fig text.bd { font-weight: bold; }
.fig text.bgw { paint-order: stroke; stroke: #fff; stroke-width: 6px; }
.cont { font-weight: bold; font-size: 10pt; letter-spacing: 0.5px; }
.thx { font-weight: bold; font-size: 11.5pt; letter-spacing: 4px; }
.foot { position: absolute; left: 0; right: 0; top: 288mm; text-align: center; font-size: 7.8pt; font-weight: bold; letter-spacing: 1.6px; }
'''

PAGES = [P1(), P2(), P3(), P4(), P5(), P6(), P7()]
HTML = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>2025 2학기 기말고사 3학년 수학</title>'
        f'<style>{CSS}</style></head><body>' + ''.join(page(i + 1, b) for i, b in enumerate(PAGES)) + '</body></html>')

if __name__ == '__main__':
    html_path = os.path.join(HERE, 'exam7.html')
    pdf_path = os.path.join(HERE, '2025_2학기_기말고사_3학년_수학_잠실여중.pdf')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(HTML)
    chrome = os.environ.get('CHROME', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    subprocess.run([chrome, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                    '--virtual-time-budget=5000', f'--print-to-pdf={pdf_path}', 'file://' + html_path], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(pdf_path)
