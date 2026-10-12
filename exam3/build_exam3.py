# -*- coding: utf-8 -*-
"""수서중 2026학년도 2학기 중간고사 2학년 수학 원본 시험지 복원.

원본 스캔(1415x2000px)의 좌표를 그대로 써서 문항과 그림을 배치한다.
그림은 SVG로 새로 그리고(10번 삽화만 원본에서 채점 표시를 지운 이미지),
Chromium으로 A4 PDF를 만든다.
  python3 exam3/build_exam3.py
"""
import math
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------ 좌표 변환
# 각 스캔에서 바깥 테두리의 (왼쪽, 위, 오른쪽, 아래) 픽셀 위치
FRAMES = {1: (90, 98, 1360, 1866), 2: (71, 96, 1356, 1854), 3: (91, 99, 1362, 1868),
          4: (80, 89, 1368, 1846), 5: (107, 94, 1373, 1865), 6: (63, 99, 1357, 1851)}
FL, FT, FW, FH = 10.5, 14.5, 189.0, 262.0  # 출력 테두리(mm)


def X(pg, x):
    x0, _, x1, _ = FRAMES[pg]
    return FL + (x - x0) / (x1 - x0) * FW


def Y(pg, y):
    _, y0, _, y1 = FRAMES[pg]
    return FT + (y - y0) / (y1 - y0) * FH


def S(pg):
    x0, y0, x1, y1 = FRAMES[pg]
    return (FW / (x1 - x0) + FH / (y1 - y0)) / 2  # mm per px


COL = {'L': (FL + 4.5, FL + FW / 2 - 3.5), 'R': (FL + FW / 2 + 4.5, FL + FW - 3.5)}
LH = 6.9  # 본문 줄 높이(mm)


# ------------------------------------------------------------ 글자 표기
def fmt(s):
    """$...$ 안: 수식(세리프). [AB] 선분, {OX} 반직선, _x_ 기울임."""
    def math_run(mo):
        t = mo.group(1)
        t = t.replace('=', '\x01').replace('≡', '\x02')
        t = re.sub(r'\[([^\]]+)\]', r'<span class="ov">\1</span>', t)
        t = re.sub(r'\{([^}]+)\}', r'<span class="vec">\1</span>', t)
        t = re.sub(r'_([^_]+)_', r'<i>\1</i>', t)
        t = re.sub(r'\^(\w)', r'<sup>\1</sup>', t)
        t = t.replace('\x01', '<span class="op">=</span>').replace('\x02', '<span class="op">≡</span>')
        return f'<span class="m">{t}</span>'
    return re.sub(r'\$([^$]+)\$', math_run, s)


def place(pg, x_mm, y_mm, html, w=None, cls=''):
    ws = f'width:{w:.2f}mm;' if w else ''
    return f'<div class="abs {cls}" style="left:{x_mm:.2f}mm;top:{y_mm:.2f}mm;{ws}">{html}</div>'


def lines(pg, col, ys, texts, first_indent=0, cls='q', right=None):
    """원본 줄바꿈 그대로: 각 줄을 따로 두고 마지막 줄 외에는 양쪽 정렬."""
    l, r = COL[col]
    out = []
    for i, (yy, t) in enumerate(zip(ys, texts)):
        last = (i == len(texts) - 1)
        ind = first_indent if i == 0 else (5.2 if first_indent <= 5.2 else 6.6)
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
    out = place(pg, l, Y(pg, ys[0]) - LH / 2, f'{num}', cls='qn')
    return out + lines(pg, col, ys, [rest] + texts[1:], first_indent=5.2 if len(num) < 3 else 6.6)


MARK = '①②③④⑤'


def choices(pg, col, ys, items, ncol, xs=None, indent=1.2):
    """ys: 각 줄의 y(px). ncol 개씩 한 줄."""
    l, r = COL[col]
    w = r - l - indent
    out = []
    for i, t in enumerate(items):
        row, c = divmod(i, ncol)
        cx = l + indent + (xs[c] if xs else c * w / ncol)
        out.append(place(pg, cx, Y(pg, ys[row]) - LH / 2, f'<span class="cm">{MARK[i]}</span> {fmt(t)}', cls='ch'))
    return ''.join(out)


def choice_lines(pg, col, rows):
    """긴 선택지: rows = [(y, 번호 or None, 텍스트)]"""
    l, r = COL[col]
    out = []
    for yy, k, t in rows:
        if k is not None:
            out.append(place(pg, l + 1.2, Y(pg, yy) - LH / 2, MARK[k], cls='ch'))
            out.append(place(pg, l + 6.2, Y(pg, yy) - LH / 2, fmt(t), w=r - l - 6.2, cls='ch jj' if t.endswith('|') else 'ch'))
        else:
            out.append(place(pg, l + 6.2, Y(pg, yy) - LH / 2, fmt(t), cls='ch'))
    return ''.join(out).replace('|</div>', '</div>')


def bogi(pg, x0, y0, x1, y1, rows):
    """<보기> 상자. rows=[(y, [(x, text), ...])] (스캔 px)"""
    s = S(pg)
    body = ''
    for yy, cells in rows:
        for xx, t in cells:
            body += place(pg, (xx - x0) * s, (yy - y0) * s - LH / 2, fmt(t), cls='bg')
    title = '<div class="bogi-t"><span>&lt;보 &nbsp;기&gt;</span></div>'
    return (f'<div class="abs box" style="left:{X(pg, x0):.2f}mm;top:{Y(pg, y0):.2f}mm;'
            f'width:{(x1 - x0) * s:.2f}mm;height:{(y1 - y0) * s:.2f}mm">{title}{body}</div>')


def table(pg, x0, y0, colx, rowy, cells):
    """colx/rowy: 경계(px). cells: 행별 셀 내용. 첫 행/첫 열은 머리."""
    s = S(pg)
    ws = [(colx[i + 1] - colx[i]) * s for i in range(len(colx) - 1)]
    hs = [(rowy[i + 1] - rowy[i]) * s for i in range(len(rowy) - 1)]
    t = f'<table class="tb" style="left:{X(pg, colx[0]):.2f}mm;top:{Y(pg, rowy[0]):.2f}mm">'
    for r, row in enumerate(cells):
        t += f'<tr style="height:{hs[r]:.2f}mm">' + ''.join(
            f'<td style="width:{ws[c]:.2f}mm">{fmt(v)}</td>' for c, v in enumerate(row)) + '</tr>'
    return t + '</table>'


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


# ================================================================ 그림
def f1():  # 1번 (1쪽, 상자 안)
    A, B, C, M = (430, 655), (332, 860), (530, 860), (430, 860)
    s = pg_([A, B, C]) + ln(A, M) + ticks(A, B) + ticks(A, C)
    s += dot(polar(A, 34, bis_dir(A, B, M)), 2.6) + dot(polar(A, 34, bis_dir(A, M, C)), 2.6)
    s += tx((430, 638), 'A') + tx((318, 870), 'B') + tx((430, 878), 'M') + tx((544, 870), 'C')
    return fig(1, (300, 625, 560, 892), s)


def f2():
    B, C = (916, 638), (1075, 638)
    A = (995.5, 638 - 79.5 / math.tan(math.radians(23)))
    D = lerp(B, A, 2 * 159 * math.sin(math.radians(23)) / dist(A, B))
    s = pg_([A, B, C]) + ln(D, C) + ticks(D, C) + ticks(B, C)
    s += arc_at(A, B, C, 15) + ln((995.5, 498), (995.5, 470), 1.1) + arrowhead((995.5, 468), (0, -1), 7, False)
    s += tx((999, 511), '46°', 21) + tx((995, 437), 'A') + tx((900, 640), 'B') + tx((1092, 640), 'C') + tx((951, 518), 'D')
    return fig(1, (880, 420, 1110, 660), s)


def f3():
    O = (875, 1375)
    t = 46.6
    Xe, Xd = polar(O, 228, t), polar(O, 206, t)
    P = (1036, 1375 - 161 * math.tan(math.radians(t / 2)))
    A = polar(O, 161 / math.cos(math.radians(t / 2)) * math.cos(math.radians(t / 2)), t)
    A = foot(P, O, Xe)
    B = (1036, 1375)
    Pe = add(O, mul(unit(sub(P, O)), 214))
    s = ln(O, Xe) + ln(O, (1110, 1375), 2.2) + ln(O, Pe, 1.4) + ln(A, P, 1.4) + ln(P, B, 1.4)
    s += right(A, O, P) + right(B, O, P) + ticks(A, P) + ticks(P, B)
    s += dot(Xd, 3.6) + dot((1082, 1375), 3.6)
    s += tx((1002, 1210), 'X') + tx((970, 1249), 'A') + tx((1042, 1290), 'P') + tx((859, 1378), 'O')
    s += tx((1036, 1394), 'B') + tx((1082, 1394), 'Y')
    return fig(1, (845, 1195, 1118, 1408), s)


def f4():  # 4번 (2쪽, 상자 안)
    A, B, C, D, P = (412, 330), (330, 480), (495, 480), (412, 480), (412, 432)
    s = pg_([A, B, C]) + ln(A, D) + ln(B, P) + ln(C, P) + ticks(A, B) + ticks(A, C)
    s += dot(polar(A, 28, bis_dir(A, B, D)), 2.4) + dot(polar(A, 28, bis_dir(A, D, C)), 2.4)
    s += tx((412, 316), 'A') + tx((316, 486), 'B') + tx((509, 486), 'C') + tx((412, 500), 'D') + tx((401, 421), 'P')
    return fig(2, (300, 305, 525, 512), s)


def f5():
    B, C = (287.5, 1607.5), (455, 1607.5)
    A = (455, 1607.5 - 167.5 * math.tan(math.radians(40)))
    M = mid(A, B)
    s = pg_([A, B, C]) + ln(M, C) + ticks(A, M) + ticks(M, B) + right(C, A, B, 9) + arc_at(B, C, A, 20)
    s += tx((324, 1597), '40°', 20) + tx((455, 1451), 'A') + tx((356, 1522), 'M') + tx((272, 1610), 'B') + tx((470, 1612), 'C')
    return fig(2, (258, 1435, 485, 1625), s)


def f6():
    A, B, C = (1025, 272.5), (897.5, 445), (1080, 444)
    O = circumcenter(A, B, C)
    D, E, F = foot(O, A, B), foot(O, B, C), foot(O, A, C)
    s = pg_([A, B, C]) + ln(O, A, 1.3) + ln(O, B, 1.3) + ln(O, C, 1.3)
    s += ln(O, D, 1.3) + ln(O, E, 1.3) + ln(O, F, 1.3) + right(D, A, O, 8) + right(E, C, O, 8) + right(F, A, O, 8)
    s += dot(O, 3.2) + dash_bulge(A, F, 14)
    s += tx((1076, 314), '8 cm', 20) + tx((1036, 384), '6 cm', 20) + ln((1012, 384), (999, 381), 1) + arrowhead((997, 380.5), (-1, -0.2), 6, False)
    s += tx((1025, 258), 'A') + tx((883, 447), 'B') + tx((1096, 447), 'C') + tx((sub(D, (12, 8))), 'D')
    s += tx(add(E, (0, 19)), 'E') + tx(add(F, (14, 6)), 'F') + tx(add(O, (-4, -18)), 'O')
    return fig(2, (868, 245, 1110, 478), s)


def f7():
    A, B, C = (945, 1130), (879, 1273), (1120, 1273)
    I = incenter(A, B, C)
    D = inter(A, I, B, C)
    E = inter(B, I, A, C)
    s = pg_([A, B, C]) + ln(A, D) + ln(B, E) + dot(I, 3.6)
    s += dot(polar(A, 30, bis_dir(A, B, D) ), 2.2) + dot(polar(A, 30, bis_dir(A, D, C)), 2.2)
    s += arc_at(C, B, A, 22) + tx((1083, 1262), '40°', 20)
    s += arc_at(E, B, A, 13) + tx(add(E, (-27, -6)), 'x', 22, italic=True)
    s += arc_at(D, B, A, 13) + tx(add(D, (-24, -18)), 'y', 22, italic=True)
    s += tx((945, 1115), 'A') + tx((864, 1276), 'B') + tx((1135, 1276), 'C') + tx(add(D, (2, 19)), 'D')
    s += tx(add(E, (15, -11)), 'E') + tx(add(I, (16, 7)), 'I')
    return fig(2, (850, 1100, 1145, 1300), s)


def f8():
    A, B, C = (426, 248), (309, 400), (500, 400)
    I = incenter(A, B, C)
    D = inter(A, B, I, (I[0] + 10, I[1]))
    E = inter(A, C, I, (I[0] + 10, I[1]))
    s = pg_([A, B, C]) + ln(D, E) + ln(B, I) + ln(C, I) + dot(I, 3)
    s += mid_arrow(D, I, 0.5) + mid_arrow(B, C, 0.5)
    s += tx((426, 233), 'A') + tx(add(D, (-15, -3)), 'D') + tx(add(I, (0, -18)), 'I') + tx(add(E, (15, -1)), 'E')
    s += tx((295, 402), 'B') + tx((514, 402), 'C')
    return fig(3, (283, 222, 528, 415), s)


def f9():
    O, r = (384.3, 1349.3), 101
    A, B, C = polar(O, r, 90), polar(O, r, 220), polar(O, r, -20)
    s = (f'<path d="M{O[0]:.2f},{O[1]:.2f} L{B[0]:.2f},{B[1]:.2f} A{r},{r} 0 0 0 {C[0]:.2f},{C[1]:.2f} Z" '
         f'fill="url(#stip)" stroke="none"/>')
    s += f'<circle cx="{O[0]}" cy="{O[1]}" r="{r}" fill="none" stroke="#000" stroke-width="1.3"/>'
    s += ln(A, B) + ln(A, C) + ln(O, A) + ln(O, B) + ln(O, C) + dot(O, 3.2)
    s += tx((321, 1238), '6 cm', 21) + curve((338, 1251), (352, 1292), (382, 1302), 1)
    tb = polar(B, 22, bis_dir(B, A, O))
    s += tx((299, 1362), '25°', 20) + curve((310, 1373), (328, 1374), tb, 1) + arrowhead(tb, sub(tb, (322, 1378)), 6, False)
    tc = polar(C, 22, bis_dir(C, A, O))
    s += tx((457, 1316), '35°', 20) + curve((455, 1329), (448, 1350), tc, 1) + arrowhead(tc, sub(tc, (447, 1352)), 6, False)
    s += tx((384, 1235), 'A') + tx(add(O, (14, -8)), 'O') + tx((291, 1430), 'B') + tx((496, 1388), 'C')
    return fig(3, (268, 1222, 512, 1455), s, STIPPLE)


def f10():
    s = S(3)
    x0, y0 = 905, 380
    over = (f'<svg class="abs fig" style="left:{X(3, x0):.2f}mm;top:{Y(3, y0):.2f}mm;width:{250 * s:.2f}mm;'
            f'height:{265 * s:.2f}mm" viewBox="0 0 250 265" xmlns="http://www.w3.org/2000/svg">'
            f'<image href="q10_fig.png" x="0" y="0" width="250" height="265"/>'
            f'<rect x="50" y="104" width="22" height="20" fill="#fff"/>'
            f'<line x1="61.7" y1="99.5" x2="72" y2="106" stroke="#000" stroke-width="1.6"/>'
            f'<circle cx="61.7" cy="99.5" r="2.4" fill="#000"/>'
            f'<text x="59" y="117" font-size="15" font-family="Liberation Sans, sans-serif" text-anchor="middle" '
            f'dominant-baseline="central">A</text></svg>')
    return over


def f11():
    A, B, C = (976, 1189), (931.7, 1342.7), (1110.7, 1342.7)
    I = incenter(A, B, C)
    D, E, F = foot(I, A, B), foot(I, B, C), foot(I, A, C)
    s = pg_([A, B, C]) + ln(A, I, 1.3) + ln(B, I, 1.3) + ln(C, I, 1.3)
    s += ln(I, D, 1.3) + ln(I, E, 1.3) + ln(I, F, 1.3) + right(D, B, I, 7) + right(E, C, I, 8) + right(F, A, I, 8)
    s += dot(I, 3)
    s += tx((976, 1173), 'A') + tx((917, 1346), 'B') + tx((1127, 1346), 'C') + tx(add(D, (-14, -5)), 'D')
    s += tx(add(E, (0, 18)), 'E') + tx(add(F, (12, -12)), 'F') + tx(add(I, (-4, 22)), 'I')
    return fig(3, (902, 1158, 1140, 1375), s)


def f12():
    B, C = (305, 448), (457, 448)
    A = (381, 448 - 76 / math.tan(math.radians(22)))
    O, I = circumcenter(A, B, C), incenter(A, B, C)
    s = pg_([A, B, C]) + ln(B, O, 1.3) + ln(C, O, 1.3) + ln(B, I, 1.3) + ln(C, I, 1.3) + dot(O, 3.2) + dot(I, 3.2)
    s += ticks(A, B) + ticks(A, C) + arc_at(A, B, C, 17) + tx((418, 284), '44°', 19)
    s += tx((381, 244), 'A') + tx(add(O, (-1, -16)), 'O') + tx(add(I, (0, 21)), 'I') + tx((292, 451), 'B') + tx((471, 451), 'C')
    return fig(4, (282, 232, 485, 468), s)


def f13():
    k = 22
    c70, s70 = math.cos(math.radians(70)), math.sin(math.radians(70))
    B = (341, 1291.7)
    C = (B[0] + 7 * k, B[1])
    A = (B[0] + 5 * k * c70, B[1] - 5 * k * s70)
    D = (A[0] + 7 * k, A[1])
    E = (B[0] - 3 * k * c70, B[1] + 3 * k * s70)  # 원본 그림처럼 BE를 약 3cm로 (축척대로 그리면 답이 드러남)
    P = inter(D, E, B, C)
    s = pg_([A, B, C, D]) + ln(B, E) + ln(D, E)
    s += dot(polar(D, 26, bis_dir(D, A, E)), 2.2) + dot(polar(D, 26, bis_dir(D, E, C)), 2.2)
    s += arc_at(A, B, D, 12) + tx(add(A, (34, 22)), '110°', 21)
    s += arc_at(B, C, A, 16) + tx(add(B, (26, -30)), '<tspan font-style="italic">x</tspan>°', 20)
    s += arc_at(P, C, D, 17) + tx(add(P, (33, -14)), '<tspan font-style="italic">y</tspan>°', 20)
    s += dash_bulge(A, B, -20) + dash_bulge(B, C, -24) + dash_bulge(B, E, -14)
    s += tx((316, 1233), '5cm', 20) + tx((420, 1322), '7cm', 20) + tx((300, 1310), '<tspan font-style="italic">z</tspan> cm', 20)
    s += tx(add(A, (-8, -10)), 'A') + tx(add(D, (14, -4)), 'D') + tx(add(B, (-4, -6)), 'B') + tx(add(C, (14, 2)), 'C')
    s += tx(add(E, (-10, 10)), 'E')
    return fig(4, (283, 1170, 555, 1368), s)


def f14():
    A, D, B, C = (1146, 247), (1305, 247), (1105, 365), (1264, 365)
    s = pg_([A, B, C, D], sw=1.5) + ln(A, C, 1.3) + mid_arrow(A, D) + mid_arrow(B, C) + mid_arrow(A, B) + mid_arrow(D, C)
    s += tx((1132, 244), 'A') + tx((1320, 244), 'D') + tx((1092, 368), 'B') + tx((1279, 368), 'C')
    return fig(4, (1080, 228, 1335, 385), s)


def f15():
    A, D, B, C = (950, 1312), (1138, 1312), (907, 1446), (1095, 1446)
    M = mid(B, C)
    O = mid(A, C)
    N = inter(A, M, B, D)
    s = pg_([A, N, O], fill='url(#stip)', sw=0) + pg_([A, B, C, D]) + ln(A, C, 1.3) + ln(B, D, 1.3) + ln(A, M, 1.3)
    s += ticks(B, M) + ticks(M, C)
    s += tx((935, 1308), 'A') + tx((1153, 1308), 'D') + tx((892, 1451), 'B') + tx((1110, 1451), 'C') + tx(add(M, (0, 20)), 'M')
    s += tx(add(N, (-15, -6)), 'N') + tx(add(O, (10, 17)), 'O')
    return fig(4, (878, 1295, 1165, 1478), s, STIPPLE)


def f16():
    A, D, B, C = (357, 270), (509.5, 270), (325, 398), (477.5, 398)
    O = mid(A, C)
    E, F = lerp(B, D, 0.30), lerp(B, D, 0.70)
    s = pg_([A, B, C, D]) + ln(A, C, 1.3) + ln(B, D, 1.3)
    s += ln(A, E, 1.3) + ln(E, C, 1.3) + ln(A, F, 1.3) + ln(F, C, 1.3) + ticks(B, E) + ticks(F, D)
    s += arc_at(A, E, O, 16) + arc_at(C, E, O, 18)
    ta = polar(A, 16, bis_dir(A, E, O))
    s += tx((306, 315), '31 °', 21) + curve((323, 316), (345, 318), ta, 1, '3,2')
    tc = polar(C, 18, bis_dir(C, E, O))
    s += tx((431, 423), '24 °', 21) + curve((432, 410), (434, 393), tc, 1, '3,2')
    s += tx((344, 266), 'A') + tx((523, 266), 'D') + tx((311, 402), 'B') + tx((491, 404), 'C')
    s += tx(add(O, (-3, 18)), 'O') + tx(add(E, (2, 19)), 'E') + tx(add(F, (-2, -18)), 'F')
    return fig(5, (293, 250, 532, 438), s)


def f18():
    B = (278, 1595)
    C = (B[0] + 170, B[1])
    A = (B[0] + 146 * math.cos(math.radians(50)), B[1] - 146 * math.sin(math.radians(50)))
    D = (A[0] + 170, A[1])
    E = (A[0] + 146, A[1])
    F = foot(C, B, E)
    s = pg_([A, B, C, D], sw=1.4) + ln(B, E, 3.2) + ln(C, F, 1.5) + right(F, B, C, 9)
    s += dot(polar(B, 24, bis_dir(B, A, E)), 2.6) + dot(polar(B, 24, bis_dir(B, E, C)), 2.6)
    s += arc_at(D, A, C, 13) + tx(add(D, (-26, 28)), '50°', 21)
    s += tx(add(A, (-14, -8)), 'A') + tx(add(E, (-4, -16)), 'E') + tx(add(D, (13, -3)), 'D')
    s += tx(add(F, (-8, -18)), 'F') + tx(add(B, (-13, 4)), 'B') + tx(add(C, (12, 6)), 'C')
    return fig(5, (258, 1440, 556, 1612), s)


def para_diag(pg, A, D, B, C, box):
    O = mid(A, C)
    s = pg_([A, B, C, D], sw=1.5) + ln(A, C, 1.3) + ln(B, D, 1.3)
    s += tx(add(A, (-14, -9)), 'A') + tx(add(D, (14, -9)), 'D') + tx(add(B, (-14, 7)), 'B') + tx(add(C, (12, 8)), 'C')
    s += tx(add(O, (-3, 19)), 'O')
    return fig(pg, box, s)


def f22():
    A, C, B, D = (400, 324), (400, 446), (275, 385), (525, 385)
    E = foot(A, C, D)
    F = inter(A, E, B, D)
    s = pg_([A, B, C, D], sw=1.5) + ln(B, D, 1.3) + ln(A, E, 1.3) + right(E, A, D, 8)
    s += arc_at(C, B, D, 11) + arc_at(F, A, B, 11) + tx((383, 414), '128 °', 19)
    s += tx((400, 309), 'A') + tx((260, 388), 'B') + tx((400, 463), 'C') + tx((541, 388), 'D')
    s += tx(add(E, (2, 18)), 'E') + tx(add(F, (12, -12)), 'F')
    return fig(6, (250, 295, 555, 475), s)


def f23():
    a = 140
    A, D, B, C = (322, 995), (322 + a, 995), (322, 995 + a), (322 + a, 995 + a)
    f = 0.4
    F = (C[0], C[1] - f * a)
    th = 45 + math.degrees(math.atan(f)) / 2
    E = (B[0] + a / math.tan(math.radians(th)), A[1])
    G = (C[0], C[1] + (E[0] - A[0]))
    s = pg_([A, B, C, D], sw=1.3) + ln(B, E) + ln(B, F) + ln(B, G) + ln(C, G)
    s += dot(polar(B, 14, bis_dir(B, A, E)), 2.2) + dot(polar(B, 14, bis_dir(B, E, F)), 2.2)
    s += tx((309, 990), 'A', 19) + tx((E[0], 976), 'E') + tx((477, 990), 'D', 19) + tx((475, 1082), 'F', 18)
    s += tx((309, 1138), 'B', 19) + tx((477, 1137), 'C') + tx((G[0], G[1] + 18), 'G')
    return fig(6, (296, 965, 488, 1238), s)


def f24():
    O, r = (1013, 336), 92
    h = r / math.sqrt(2)
    s = f'<circle cx="{O[0]}" cy="{O[1]}" r="{r + 3}" fill="url(#stip)" stroke="#777" stroke-width="0.8" stroke-dasharray="1.5,2.5"/>'
    s += f'<rect x="{O[0] - h:.2f}" y="{O[1] - h:.2f}" width="{2 * h:.2f}" height="{2 * h:.2f}" fill="none" stroke="#000" stroke-width="1.8"/>'
    return fig(6, (910, 233, 1116, 439), s, STIPPLE)


# ================================================================ 페이지 내용
def box_html(pg, x0, y0, x1, y1, inner):
    s = S(pg)
    return (f'<div class="abs box" style="left:{X(pg, x0):.2f}mm;top:{Y(pg, y0):.2f}mm;'
            f'width:{(x1 - x0) * s:.2f}mm;height:{(y1 - y0) * s:.2f}mm">{inner}</div>')


def inbox(pg, x0, y0, rows):
    """상자 안 줄들: rows = [(x, y, text)] (스캔 px, 상자 원점 기준 변환)"""
    s = S(pg)
    return ''.join(place(pg, (x - x0) * s, (y - y0) * s - LH / 2, fmt(t), cls='bx') for x, y, t in rows)


BL = '<span class="blank">'  # 빈칸 상자


def blank(t):
    return f'<span class="blank">{t}</span>'


def P1():
    s = ''
    # 머리 상자
    s += box_html(1, 103, 112, 492, 258, '<div class="h-date"><div>날짜</div><div>10월 1일 (목) 2교시</div></div>')
    s += box_html(1, 507, 112, 946, 258, '<div class="h-title"><div class="h-big">2학년 &nbsp;수학</div>'
                  '<div class="h-sub">2026학년도 2학기 중간고사</div></div>')
    s += box_html(1, 960, 112, 1346, 258, '<table class="h-ratio"><tr><td>문항유형</td><td>반영비율</td></tr>'
                  '<tr><td>선택형 &nbsp; &nbsp; 총 (100)점</td><td>(30)%</td></tr></table>')
    s += box_html(1, 103, 290, 710, 437, '<div class="notice">문제를 풀기 전에 성명, 학년, 반, 번호를 답안지에 '
                  '정확하게 기재한 후, 선택형 문제에 대한 정확한 답을 골라 선택형 답란에 칠하시오.<br>'
                  '<b>※ 문제는 총 ( 24 )문항입니다.</b></div>')
    # 1번
    s += qlines(1, 'L', [497, 540, 580], ['1. “이등변삼각형의 두 밑각의 크기는 서로 같다”를 증명하는',
                                          '과정이다. (가)~(다)에 알맞은 것을 차례로 나열한', '것은? (3점)'])
    s += box_html(1, 156, 618, 700, 1241, inbox(1, 156, 618, [
        (168, 918, '$[AB]=[AC]$인 이등변삼각형 $ABC$에서 $∠A$의'),
        (168, 965, '이등분선과 $[BC]$의 교점을 $M$이라고 하자.'),
        (192, 1006, '$△ABM$과 $△ACM$에서'),
        (192, 1052, '$[AB]=$' + blank('(가)') + ','),
        (192, 1094, '$∠BAM=∠CAM$'),
        (190, 1133, blank('(나)') + '는 공통이므로'),
        (192, 1177, '$△ABM≡△ACM$ (' + blank('(다)') + ' 합동)'),
        (192, 1218, '따라서 $∠B=∠C$이다.')]))
    s += f1()
    s += table(1, 156, 1272, [156, 201, 352, 517, 696], [1272, 1309, 1349, 1389, 1430, 1470, 1511],
               [['', '(가)', '(나)', '(다)'], ['①', '$[AC]$', '$[AB]$', '$SAS$'], ['②', '$[AC]$', '$[AM]$', '$ASA$'],
                ['③', '$[AM]$', '$[BM]$', '$ASA$'], ['④', '$[AC]$', '$[AM]$', '$SAS$'], ['⑤', '$[AM]$', '$[AB]$', '$ASA$']])
    # 2번
    s += qlines(1, 'R', [302, 350, 392], ['2. 그림과 같이 $[AB]=[AC]$인 이등변삼각형 $ABC$에서',
                                          '$[BC]=[CD]$이고, $∠A=46°$일 때, $∠ACD$의 크기는?', '>>(4점)'])
    s += f2()
    s += choices(1, 'R', [680], ['$20°$', '$21°$', '$22°$', '$23°$', '$24°$'], 5)
    # 3번
    s += qlines(1, 'R', [1072, 1118, 1165], ['3. 그림과 같이 $∠XOY$의 내부의 한 점 $P$에서',
                                             '${OX}$, ${OY}$에 내린 수선의 발을 각각 $A$, $B$라 하자.',
                                             '$[PA]=[PB]$일 때, 옳지 <b class="bu">않은</b> 것은? (4점)'])
    s += f3()
    s += choices(1, 'R', [1433, 1480, 1527], ['$[OA]=[OB]$', '$∠AOP=∠BOP$', '$∠APO=∠BPO$', '$△AOP≡△BOP$',
                                              '$∠APO=2∠AOP$'], 2)
    return s, '[뒷면에 계속됩니다.]'


def P2():
    s = qlines(2, 'L', [125, 175, 220, 265], ['4. $[AB]=[AC]$인 이등변삼각형 $ABC$에서 $∠A$의 이등분선과',
                                             '밑변 $BC$의 교점을 $D$라 하자. 이때 $[AD]$ 위의 한 점을',
                                             '<<$P$라하고, $[BP]=[CP]$임을 증명하는 과정이다.',
                                             '(가)~(다)에 알맞은 것을 차례로 나열한 것은? (4점)'])
    s += box_html(2, 143, 300, 688, 861, inbox(2, 143, 300, [
        (153, 540, '$[AD]$는 이등변삼각형 $ABC$의 꼭지각 $A$의 이등'),
        (153, 580, '분선이므로'),
        (200, 625, '$[BD]=$' + blank('(가)') + ' ……㉠'),
        (200, 667, '$∠BDP=$' + blank('(나)') + '$=90°$ &nbsp;……㉡'),
        (200, 712, '$[PD]$는 공통 ……㉢'),
        (153, 752, '㉠, ㉡, ㉢에 의해'),
        (153, 795, '$△BPD≡△CPD$(' + blank('(다)') + '합동)'),
        (153, 840, '∴ $[BP]=[CP]$')]))
    s += f4()
    s += table(2, 145, 888, [145, 190, 352, 516, 686], [888, 927, 968, 1009, 1050, 1090, 1131],
               [['', '(가)', '(나)', '(다)'], ['①', '$[CD]$', '$∠CPD$', '$ASA$'], ['②', '$[CD]$', '$∠CDP$', '$RHS$'],
                ['③', '$[AD]$', '$∠CPD$', '$RHS$'], ['④', '$[PC]$', '$∠CDP$', '$SAS$'], ['⑤', '$[CD]$', '$∠CDP$', '$SAS$']])
    s += qlines(2, 'L', [1297, 1342, 1387], ['5. 그림과 같이 $∠C=90°$인 직각삼각형 $ABC$에서',
                                             '$[AB]$의 중점을 $M$이라 하자. $∠B=40°$일 때,', '$∠AMC$의 크기는? (4점)'])
    s += f5()
    s += choices(2, 'L', [1697, 1745], ['$75°$', '$80°$', '$85°$', '$90°$', '$95°$'], 3)
    s += qlines(2, 'R', [118, 163, 208], ['6. 그림에서 점 $O$는 $△ABC$의 외심이다. 사각형 $DBEO$의',
                                          '넓이는 $38 cm^2$이고 $[AF]=8 cm$, $[OF]=6 cm$일 때,',
                                          '$△ABC$의 넓이는? (4점)'])
    s += f6()
    s += choices(2, 'R', [508, 556], ['$62 cm^2$', '$81 cm^2$', '$102 cm^2$', '$124 cm^2$', '$162 cm^2$'], 3)
    s += qlines(2, 'R', [1022, 1067], ['7. 그림에서 점 $I$는 $△ABC$의 내심이다. $∠C=40°$일 때,',
                                       '$∠_x_+∠_y_$의 크기는? (5점)'])
    s += f7()
    s += choices(2, 'R', [1330, 1378], ['$140°$', '$145°$', '$150°$', '$155°$', '$160°$'], 3)
    return s, '[다음 장에 계속됩니다.]'


def P3():
    s = qlines(3, 'L', [132, 178], ['8. 그림에서 점 $I$가 $△ABC$의 내심이고 $[DE]$∥$[BC]$일 때,',
                                    '&lt;보기&gt; 중 옳은 것을 <b class="bu">있는 대로</b> 고른 것은? (5점)'])
    s += f8()
    s += bogi(3, 143, 458, 676, 597, [
        (498, [(150, 'ㄱ. $[DE]=[DB]+[EC]$'), (413, 'ㄴ. $∠DBI=∠DIB$')]),
        (538, [(150, 'ㄷ. $∠IBC=∠ICB$'), (413, 'ㄹ. $[DB]=[DI]$, $[EC]=[EI]$')]),
        (578, [(150, 'ㅁ. ($△ADE$의 둘레의 길이)$=[AB]+[AC]$')])])
    s += choices(3, 'L', [642, 690, 738], ['ㄴ, ㄷ', 'ㄱ, ㄹ, ㅁ', 'ㄴ, ㄷ, ㅁ', 'ㄱ, ㄴ, ㄹ, ㅁ', 'ㄱ, ㄴ, ㄷ, ㄹ, ㅁ'], 2)
    s += qlines(3, 'L', [1084, 1132, 1175], ['9. 그림과 같이 세 점 $A$, $B$, $C$는 원 $O$위에 있다.',
                                             '$∠ABO=25°$, $∠ACO=35°$, $[OA]=6 cm$일 때,', '부채꼴 $OBC$의 넓이는? (4점)'])
    s += f9()
    s += choices(3, 'L', [1527, 1575], ['$10π cm^2$', '$11π cm^2$', '$12π cm^2$', '$13π cm^2$', '$14π cm^2$'], 3)
    s += qlines(3, 'R', [128, 170, 214, 257, 300, 342], [
        '10. 학교 체육대회에서 세 학생이 동시에 출발하여', '가운데 깃발을 먼저 뽑는 학생이 이기는 게임을',
        '준비하고 있다. 세 학생이 출발할 위치를', '$A$, $B$, $C$라고 할 때, 세 학생의 출발 위치로부터',
        '같은 거리에 있도록 깃발의 위치를 정하는 방법으로', '옳은 것은? (4점)'])
    s += f10()
    s += choice_lines(3, 'R', [
        (693, 0, '점 $C$에서 $[AB]$에 내린 수선의 발을 찾는다.'),
        (740, 1, '$[AB]$, $[AC]$, $[BC]$의 수직이등분선의 교점을 찾는다.'),
        (785, 2, '$∠CAB$, $∠ABC$, $∠ACB$의 이등분선의 교점을|'), (827, None, '찾는다.'),
        (868, 3, '$△ABC$의 세 꼭짓점 $A$, $B$, $C$에서 각 대변에|'), (910, None, '내린 수선의 교점을 찾는다.'),
        (953, 4, '$△ABC$에서 세 꼭짓점 $A$, $B$, $C$와 각 대변의|'), (995, None, '중점을 이은 선분의 교점을 찾는다.')])
    s += qlines(3, 'R', [1080, 1120], ['11. 그림에서 점 $I$가 $△ABC$의 내심일 때, &lt;보기&gt; 중',
                                       '옳은 것을 <b class="bu">있는 대로</b> 고른 것은? (4점)'])
    s += f11()
    s += bogi(3, 773, 1428, 1310, 1555, [
        (1468, [(780, 'ㄱ. $△CIF≡△CIE$'), (1040, 'ㄴ. $∠AID=∠AIF$')]),
        (1503, [(780, 'ㄷ. $[ID]=[IE]=[IF]$'), (1040, 'ㄹ. $∠BIE=∠CIE$')]),
        (1538, [(780, 'ㅁ. $△AID≡△BID$')])])
    s += choices(3, 'R', [1597, 1645, 1693], ['ㄱ, ㄴ', 'ㄷ, ㄹ', 'ㄱ, ㄴ, ㄷ', 'ㄱ, ㄷ, ㅁ', 'ㄱ, ㄷ, ㄹ, ㅁ'], 2)
    return s, '[뒷면에 계속됩니다.]'


def P4():
    s = qlines(4, 'L', [118, 160, 202], ['12. 그림에서 두 점 $O$, $I$는 각각 $[AB]=[AC]$인 이등변',
                                         '삼각형 $ABC$의 외심과 내심이다. $∠A=44°$일 때,', '$∠OBI$의 크기는? (5점)'])
    s += f12()
    s += choices(4, 'L', [497], ['$10°$', '$11°$', '$12°$', '$13°$', '$14°$'], 5)
    s += qlines(4, 'L', [977, 1025, 1072, 1115], ['13. 평행사변형 $ABCD$에서 $[DE]$는 $∠D$의 이등분선이고',
                                                  '$∠A=110°$이다. $∠D$의 이등분선과 $[AB]$의 연장선의',
                                                  '교점을 $E$라고 할 때, $[BE]=_z_cm$라고 한다.', '$_x_+_y_+_z_$ 값은? (4점)'])
    s += f13()
    s += choices(4, 'L', [1405], ['104', '106', '107', '110', '112'], 5)
    s += qlines(4, 'R', [110, 152, 192], ['14. “평행사변형에서 두 쌍의 대변의 길이는 각각',
                                          '같다”를 확인하는 과정이다. (가)~(다)에 알맞은', '것을 차례로 나열한 것은? (4점)'])
    s += box_html(4, 735, 216, 1346, 652, inbox(4, 735, 216, [
        (757, 237, '평행사변형 $ABCD$에서'), (757, 280, '대각선 $AC$를 긋자.'),
        (772, 322, '$△ABC$와 $△CDA$에서'), (757, 368, '$[AB]$∥$[DC]$, $[AD]$∥$[BC]$이므로'),
        (797, 412, '$∠BAC=$' + blank('(가)') + ' (엇각) ……①'), (797, 455, '$∠ACB=∠CAD$ (엇각) ……②'),
        (808, 500, '$[AC]$는 공통 ……③ 이다.'),
        (770, 543, '①, ②, ③에서 $△ABC≡△CDA$(' + blank('(나)') + '합동)'),
        (757, 588, '이므로 ' + blank('(다)') + '이다. 따라서 평행사변형의 두 쌍의'),
        (757, 630, '대변의 길이는 각각 같다.')]))
    s += f14()
    s += table(4, 737, 680, [737, 780, 891, 1008, 1338], [680, 721, 762, 802, 842, 882, 922],
               [['', '(가)', '(나)', '(다)'],
                ['①', '$∠DCA$', '$ASA$', '$[AB]=[CD]$, $[BC]=[DA]$'], ['②', '$∠DCA$', '$SAS$', '$[AB]=[CD]$, $[BC]=[DA]$'],
                ['③', '$∠DCA$', '$ASA$', '$[AB]$∥$[DC]$, $[AD]$∥$[BC]$'], ['④', '$∠BCA$', '$SAS$', '$∠B=∠D$, $∠BAD=∠BCD$'],
                ['⑤', '$∠BCA$', '$ASA$', '$∠B=∠D$, $∠BAD=∠BCD$']])
    s += qlines(4, 'R', [1103, 1150, 1198, 1245], ['15. 평행사변형 $ABCD$에서 두 대각선의 교점을 $O$,',
                                                   '$[BC]$의 중점을 $M$, $[AM]$과 $[BD]$의 교점을 $N$이라',
                                                   '하자. $[AN]$ : $[NM]=2$ : $1$이고 □$ABCD$의 넓이가',
                                                   '$72 cm^2$일 때, $△ANO$의 넓이는? (5점)'])
    s += f15()
    s += choices(4, 'R', [1510, 1557], ['$6 cm^2$', '$7 cm^2$', '$8 cm^2$', '$9 cm^2$', '$10 cm^2$'], 3)
    return s, '[다음 장에 계속됩니다.]'


def P5():
    s = qlines(5, 'L', [125, 172, 217], ['16. 평행사변형 $ABCD$에서 점 $O$는 두 대각선의 교점이고,',
                                         '$[BE]=[DF]$이다. $∠EAO=31°$, $∠ECO=24°$일 때,', '$∠AFC$의 크기는? (4점)'])
    s += f16()
    s += choices(5, 'L', [463, 511], ['$121°$', '$122°$', '$123°$', '$124°$', '$125°$'], 3)
    s += qlines(5, 'L', [688], ['17. 다음 설명 중 옳지 <b class="bu">않은</b> 것은? (4점)'])
    s += choice_lines(5, 'L', [
        (730, 0, '한 내각의 크기가 $90°$인 마름모는 정사각형이다.'),
        (772, 1, '두 대각선이 서로 수직인 직사각형은 정사각형이다.'),
        (813, 2, '이웃하는 두 변의 길이가 같은 평행사변형은|'), (855, None, '마름모이다.'),
        (898, 3, '대각의 크기의 합이 $180°$인 평행사변형은 직|'), (938, None, '사각형이다.'),
        (982, 4, '두 대각선이 서로 다른 것을 수직이등분하는|'), (1022, None, '평행사변형은 정사각형이다.')])
    s += qlines(5, 'L', [1240, 1287, 1330, 1370], ['18. 평행사변형 $ABCD$에서 $∠B$의 이등분선과 $[AD]$의',
                                                   '교점을 $E$라 하고, 꼭짓점 $C$에서 $[BE]$에 내린 수선의',
                                                   '발을 $F$라 하자. $∠D=50°$일 때, $∠DCF$의 크기는?', '>>(5점)'])
    s += f18()
    s += choices(5, 'L', [1645], ['$64°$', '$65°$', '$66°$', '$67°$', '$68°$'], 5)
    s += qlines(5, 'R', [130, 175, 218], ['19. $[AB]$∥$[DC]$인 □$ABCD$가 평행사변형이 되기 위해',
                                          '필요한 조건을 &lt;보기&gt;에서 <b class="bu">있는 대로</b> 고른 것은?',
                                          '(단, 점 $O$는 두 대각선의 교점이다.) (4점)'])
    s += para_diag(5, (1017.5, 277.5), (1175, 277.5), (970, 405), (1127.5, 405), (945, 255, 1200, 425))
    s += bogi(5, 762, 462, 1352, 571, [
        (505, [(770, 'ㄱ. $[AB]=[DC]$'), (982, 'ㄴ. $[AD]$∥$[BC]$'), (1182, 'ㄷ. $[AC]=[BD]$')]),
        (550, [(770, 'ㄹ. $[AD]=[BC]$'), (982, 'ㅁ. $∠DAO=∠BCO$')])])
    s += choices(5, 'R', [613, 661, 709], ['ㄱ, ㄴ', 'ㄱ, ㄹ', 'ㄴ, ㄷ', 'ㄷ, ㅁ, ㄹ', 'ㄱ, ㄴ, ㅁ'], 2)
    s += qlines(5, 'R', [847, 890], ['20. <<□$ABCD$가 평행사변형이 되지 <b class="bu">않는</b> 것은?',
                                     '(단, 점 $O$는 두 대각선의 교점이다.) <span class="pt">(3점)</span>'])
    s += choice_lines(5, 'R', [
        (937, 0, '$[AB]=[BC]=5 cm$, $[AC]⊥[BD]$'),
        (985, 1, '$[AB]$∥$[DC]$, $[AB]=[DC]=5 cm$'),
        (1032, 2, '$[AB]=[DC]=4 cm$, $[AD]=[BC]=5 cm$'),
        (1080, 3, '$∠A=120°$, $∠B=60°$, $[AD]=[BC]=6 cm$'),
        (1128, 4, '$[OA]=7 cm$, $[OB]=4 cm$, $[OC]=7 cm$, $[OD]=4 cm$')])
    s += qlines(5, 'R', [1338, 1378], ['21. 평행사변형 $ABCD$가 직사각형이 되는 조건은?',
                                       '(단, 점 $O$는 두 대각선의 교점이다.) (4점)'])
    s += para_diag(5, (1000, 1427.5), (1150, 1427.5), (947.5, 1555), (1097.5, 1555), (925, 1403, 1175, 1570))
    s += choices(5, 'R', [1597, 1647], ['$[AB]=[BC]$', '$[OB]=[OC]$', '$[AD]=[BC]$', '$[BD]⊥[AC]$', '$[OB]=[OD]$'], 3)
    return s, '[뒷면에 계속됩니다.]'


def P6():
    s = qlines(6, 'L', [125, 170, 213], ['22. $∠C=128°$인 마름모 $ABCD$의 꼭짓점 $A$에서',
                                         '$[CD]$에 내린 수선의 발을 $E$라 하고, $[AE]$와 $[BD]$의',
                                         '교점을 $F$라고 할 때, $∠AFB$의 크기는? (4점)'])
    s += f22()
    s += choices(6, 'L', [502], ['$61°$', '$62°$', '$63°$', '$64°$', '$65°$'], 5)
    s += qlines(6, 'L', [840, 885, 928], ['23. 정사각형 $ABCD$에서 $[BE]$는 $∠ABF$의 이등분선',
                                          '이다. 점 $G$는 $[AE]=[CG]$를 만족하는 $[DC]$의 연장선',
                                          '위의 한 점일 때, 옳지 <b class="bu">않은</b> 것은? (5점)'])
    s += f23()
    s += choices(6, 'L', [1262, 1305, 1350, 1393, 1435],
                 ['$[BE]=[BF]$', '$[BF]=[FG]$', '$∠ABE=∠CBG$', '$∠CGB=∠FBG$', '$∠EBC=∠FBG$'], 1)
    s += qlines(6, 'R', [121, 164, 207], ['24. 원 모양의 풀밭 둘레의 네 지점을 꼭짓점으로 하는',
                                          '정사각형 모양의 목장을 만들려고 한다. 풀밭의',
                                          '넓이가 $144π m^2$일 때, 목장의 넓이는? (4점)'])
    s += f24()
    s += choices(6, 'R', [463, 510], ['$282 m^2$', '$284 m^2$', '$286 m^2$', '$288 m^2$', '$290 m^2$'], 3)
    s += place(6, COL['R'][0], Y(6, 722) - LH / 2, '[끝]', w=COL['R'][1] - COL['R'][0], cls='cont')
    return s, None


def page(n, body, cont):
    top_div = Y(1, 268) if n == 1 else FT
    c = ''
    if cont:
        c = place(n, COL['R'][0], FT + FH - 9.5, cont, w=COL['R'][1] - COL['R'][0], cls='cont')
    foot = (f'<div class="foot1"><span>수학 2학년</span><span>{n} / 6</span><span class="sch">수 서 중 학 교</span></div>'
            '<div class="foot2">※ 이 시험 문제의 저작권은 수서중학교에 있습니다. 무단 전송 · 복제 · 배포 시 저작권법에 의거 처벌될 수 있습니다.</div>')
    return (f'<section class="page"><div class="frame"></div>'
            f'<div class="divider" style="top:{top_div:.2f}mm"></div>{body}{c}{foot}</section>')


CSS = r'''
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #fff; color: #000; }
body { font-family: "NanumGothic", "Noto Sans CJK KR", sans-serif; font-size: 10.2pt; }
.page { width: 210mm; height: 297mm; position: relative; page-break-after: always; overflow: hidden; }
.page:last-child { page-break-after: auto; }
.frame { position: absolute; left: 10.5mm; top: 14.5mm; width: 189mm; height: 262mm; border: 1.6px solid #000; }
.divider { position: absolute; left: 105mm; bottom: 20.5mm; border-left: 1.2px solid #000; }
.abs { position: absolute; white-space: nowrap; line-height: 6.9mm; }
.q, .qn, .ch, .bx, .bg, .cont { height: 6.9mm; }
.jj { text-align: justify; text-align-last: justify; }
.jl { text-align: left; }
.jr { text-align: right; }
.qn { letter-spacing: 0; }
.q { letter-spacing: -0.25px; }
.m { font-family: "Liberation Serif", "Times New Roman", serif; font-size: 1.08em; }
.m i { font-style: italic; }
.m sup { font-size: 0.68em; vertical-align: 0.5em; line-height: 0; }
.op { margin: 0 0.12em; }
.ov { display: inline-block; border-top: 1px solid #000; line-height: 1.05; padding-top: 0.5px; }
.vec { display: inline-block; line-height: 1.05; padding-top: 0.42em;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 10 10'%3E%3Cpath d='M1 1 L9 5 L1 9' fill='none' stroke='black' stroke-width='1.6'/%3E%3C/svg%3E"), linear-gradient(#000, #000);
  background-repeat: no-repeat; background-size: 0.36em 0.36em, calc(100% - 0.1em) 1px; background-position: right 0.04em, left 0.21em; }
.bu { font-weight: bold; text-decoration: underline; text-underline-offset: 2px; }
.pt { position: absolute; right: 0; }
.cm { font-family: "NanumGothic", sans-serif; }
.blank { display: inline-block; border: 1px solid #000; padding: 0 0.35em; line-height: 1.25; margin: 0 1px; }
.box { border: 1.3px solid #000; white-space: normal; }
.bogi-t { position: absolute; top: -3.4mm; left: 0; right: 0; text-align: center; line-height: 6.9mm; }
.bogi-t span { background: #fff; padding: 0 1.5mm; }
table.tb { position: absolute; border-collapse: collapse; text-align: center; }
table.tb td { border: 1px solid #000; padding: 0; line-height: 1; }
.fig { overflow: visible; }
.fig text { font-family: "Liberation Serif", "Times New Roman", serif; fill: #000; }
.h-date { display: flex; height: 100%; align-items: center; font-size: 10.5pt; font-weight: bold; }
.h-date div:first-child { width: 27.5%; height: 100%; display: flex; align-items: center; justify-content: center; border-right: 1px solid #000; }
.h-date div:last-child { flex: 1; text-align: center; font-weight: normal; }
.h-title { text-align: center; padding-top: 2mm; }
.h-big { display: inline-block; font-size: 25pt; letter-spacing: 1.5mm; border-bottom: 1.3px solid #000; line-height: 1.2; padding: 0 2mm; }
.h-sub { font-size: 12pt; font-weight: bold; margin-top: 2.5mm; letter-spacing: 0.3px; }
table.h-ratio { width: 100%; height: 100%; border-collapse: collapse; text-align: center; font-size: 10.5pt; }
table.h-ratio td { border-left: 1px solid #000; }
table.h-ratio td:first-child { border-left: none; width: 64.5%; }
table.h-ratio tr:first-child td { border-bottom: 1px solid #000; height: 32%; }
.notice { padding: 1.2mm 2.2mm; line-height: 4.9mm; text-align: justify; font-size: 10.6pt; word-break: keep-all; }
.cont { font-weight: bold; text-align: right; }
.foot1 { position: absolute; left: 13.5mm; right: 21mm; top: 278mm; font-weight: bold; font-size: 9.5pt; display: flex; justify-content: space-between; letter-spacing: 0.5px; }
.foot1 .sch { letter-spacing: 2.5mm; }
.foot2 { position: absolute; left: 0; right: 0; top: 282.2mm; text-align: center; font-size: 8.6pt; letter-spacing: 1.3px; }
'''

PAGES = [P1(), P2(), P3(), P4(), P5(), P6()]
HTML = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>2026 2학기 중간고사 2학년 수학</title>'
        f'<style>{CSS}</style></head><body>'
        + ''.join(page(i + 1, b, c) for i, (b, c) in enumerate(PAGES)) + '</body></html>')

if __name__ == '__main__':
    html_path = os.path.join(HERE, 'exam3.html')
    pdf_path = os.path.join(HERE, '2026_2학기_중간고사_2학년_수학.pdf')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(HTML)
    chrome = os.environ.get('CHROME', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    subprocess.run([chrome, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                    '--allow-file-access-from-files', '--virtual-time-budget=5000',
                    f'--print-to-pdf={pdf_path}', 'file://' + html_path], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(pdf_path)
