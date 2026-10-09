# -*- coding: utf-8 -*-
"""2026학년도 2학기 1차 정기시험 (3학년 수학) 원본 시험지 복원.

HTML(+SVG 그림)을 생성한 뒤 Chromium으로 PDF를 만든다.
  python3 exam/build_exam.py
"""
import math
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- 수식 도우미
def frac(n, d):
    return f'<span class="frac"><span class="num">{n}</span><span class="den">{d}</span></span>'


def sq(x):
    return f'<span class="sqrt"><span class="rad">√</span><span class="rc">{x}</span></span>'


def ov(x):
    return f'<span class="ov">{x}</span>'


def v(x):
    return f'<i class="var">{x}</i>'


DEG = '°'
ANG = '∠'
TRI = '△'


def choices(items, cols):
    """items: 보기 5개, cols: 한 줄당 개수"""
    marks = '①②③④⑤'
    cells = ''.join(f'<div class="ch"><span class="cm">{marks[i]}</span> {t}</div>' for i, t in enumerate(items))
    return f'<div class="choices c{cols}">{cells}</div>'


def q(num, body, pts):
    return f'<div class="q"><div class="qt"><b class="qn">{num}.</b> {body} ({pts}점)</div>'


# ---------------------------------------------------------------- SVG 도우미
def svg(w, h, inner, cls='fig'):
    return (f'<svg class="{cls}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'xmlns="http://www.w3.org/2000/svg">{inner}</svg>')


def line(p, q_, sw=1.6, dash=None, color='#000'):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<line x1="{p[0]:.2f}" y1="{p[1]:.2f}" x2="{q_[0]:.2f}" y2="{q_[1]:.2f}" '
            f'stroke="{color}" stroke-width="{sw}"{d} stroke-linecap="round"/>')


def poly(pts, fill='none', sw=1.6, close=True, dash=None):
    d = ' '.join(f'{x:.2f},{y:.2f}' for x, y in pts)
    tag = 'polygon' if close else 'polyline'
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<{tag} points="{d}" fill="{fill}" stroke="#000" stroke-width="{sw}"{da} stroke-linejoin="round"/>'


def text(x, y, s, size=13, anchor='middle', italic=False, cls=''):
    st = ' font-style="italic"' if italic else ''
    return (f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}"'
            f'{st} class="{cls}" dominant-baseline="central">{s}</text>')


def rtext(x, y, coef, rad, size=13):
    """SVG 안의 근호 표기(예: 4√3). 근호 위 가로선을 직접 그린다."""
    cw, rw = len(coef) * 0.5 * size, 0.62 * size
    w = cw + rw + len(rad) * 0.5 * size
    x0 = x - w / 2
    out = (f'<text x="{x0:.2f}" y="{y:.2f}" font-size="{size}" dominant-baseline="central">{coef}√</text>'
           f'<text x="{x0+cw+rw:.2f}" y="{y:.2f}" font-size="{size}" dominant-baseline="central">{rad}</text>')
    out += line((x0 + cw + rw - 0.08 * size, y - 0.52 * size), (x0 + w + 0.05 * size, y - 0.52 * size), 0.8)
    return out


def arc(c, r, a1, a2, sw=1.0, dash=None):
    """수학 좌표계 각도(도, 반시계)로 c 중심 원호. SVG y축은 아래 방향."""
    x1 = c[0] + r * math.cos(math.radians(a1)); y1 = c[1] - r * math.sin(math.radians(a1))
    x2 = c[0] + r * math.cos(math.radians(a2)); y2 = c[1] - r * math.sin(math.radians(a2))
    large = 1 if abs(a2 - a1) > 180 else 0
    sweep = 0 if a2 > a1 else 1
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<path d="M{x1:.2f},{y1:.2f} A{r},{r} 0 {large} {sweep} {x2:.2f},{y2:.2f}" '
            f'fill="none" stroke="#000" stroke-width="{sw}"{da}/>')


def bulge(p, q_, k, dash='3,3', sw=0.9):
    """p→q 를 잇는 점선 곡선(길이 표시용). k>0 이면 진행방향 왼쪽(화면 기준)으로 볼록."""
    mx, my = (p[0] + q_[0]) / 2, (p[1] + q_[1]) / 2
    dx, dy = q_[0] - p[0], q_[1] - p[1]
    L = math.hypot(dx, dy)
    nx, ny = dy / L, -dx / L
    cx, cy = mx + nx * k, my + ny * k
    return (f'<path d="M{p[0]:.2f},{p[1]:.2f} Q{cx:.2f},{cy:.2f} {q_[0]:.2f},{q_[1]:.2f}" fill="none" '
            f'stroke="#000" stroke-width="{sw}" stroke-dasharray="{dash}"/>'), (mx + nx * k * 0.62, my + ny * k * 0.62)


def ang(p):
    return math.degrees(math.atan2(-p[1], p[0]))


def angle_at(c, p):
    return ang((p[0] - c[0], p[1] - c[1]))


def arrow_head(tip, direction, size=7):
    dx, dy = direction
    L = math.hypot(dx, dy); dx /= L; dy /= L
    bx, by = tip[0] - dx * size, tip[1] - dy * size
    px, py = -dy * size * 0.45, dx * size * 0.45
    return f'<polygon points="{tip[0]:.2f},{tip[1]:.2f} {bx+px:.2f},{by+py:.2f} {bx-px:.2f},{by-py:.2f}" fill="#000"/>'


def right_mark(c, p1, p2, s=8):
    u = ((p1[0] - c[0]), (p1[1] - c[1])); L = math.hypot(*u); u = (u[0] / L * s, u[1] / L * s)
    w = ((p2[0] - c[0]), (p2[1] - c[1])); L = math.hypot(*w); w = (w[0] / L * s, w[1] / L * s)
    pts = [(c[0] + u[0], c[1] + u[1]), (c[0] + u[0] + w[0], c[1] + u[1] + w[1]), (c[0] + w[0], c[1] + w[1])]
    return poly(pts, close=False, sw=1)


# ================================================================= 그림
def fig_q1():
    ox, oy, cw, rh = 42, 150, 36, 26
    s = ''
    for i in range(0, 8):
        s += line((ox + i * cw, oy - 5 * rh), (ox + i * cw, oy), 0.6)
    for j in range(0, 6):
        s += line((ox, oy - j * rh), (ox + 7 * cw, oy), 0.6) if False else line((ox, oy - j * rh), (ox + 7 * cw, oy - j * rh), 0.6)
    s += line((ox, oy), (ox + 7 * cw, oy), 1.2) + line((ox, oy), (ox, oy - 5 * rh), 1.2)
    for val, h in ((7, 3), (8, 4), (9, 3)):
        col = val - 3  # 5→2번째 칸
        cx = ox + (col - 0.5) * cw
        s += f'<rect x="{cx-9:.1f}" y="{oy-h*rh:.1f}" width="18" height="{h*rh:.1f}" fill="#555" stroke="#333" stroke-width="0.6"/>'
    for j in range(0, 5):
        s += text(ox - 10, oy - j * rh, str(j), 12, cls='b')
    s += text(ox - 6, oy - 4.62 * rh, '(도수)', 11, 'end', cls='b')
    for k, val in enumerate(range(5, 11)):
        s += text(ox + (k + 1.5) * cw, oy + 15, str(val), 12, cls='b')
    s += text(ox + 7 * cw + 20, oy + 13, '(개)', 11, cls='b')
    s += text(ox + 11, oy, '≈', 12)
    return svg(330, 175, s)


SCATTER = [(26, 22), (40, 27), (42.5, 28), (44.5, 29), (50, 27), (51.5, 29), (55.5, 26),
           (67.5, 29), (67.5, 28), (69.5, 27), (75, 26), (87, 31), (87, 25), (94, 30), (95, 31),
           (99, 30), (100, 29), (104.5, 31), (106, 32), (110, 26), (114, 25), (119, 25),
           (120, 31), (120, 29), (126, 27), (131, 25), (140, 28), (150, 28), (153, 26),
           (174, 26), (180, 30), (200, 27.4), (209, 37)]


def fig_q4():
    ox, oy = 58, 210  # (0, 20) 위치
    kx, ky = 1.12, 10.3  # px per km, px per 시간
    X = lambda x: ox + x * kx
    Y = lambda y: oy - (y - 20) * ky
    s = ''
    for x in range(10, 251, 10):
        s += line((X(x), Y(20)), (X(x), Y(38)), 0.6)
    for y in range(22, 39, 2):
        s += line((X(0), Y(y)), (X(250), Y(y)), 0.6)
    s += line((X(0), Y(20)), (X(250) + 12, Y(20)), 1.3) + arrow_head((X(250) + 14, Y(20)), (1, 0))
    s += line((X(0), Y(20)), (X(0), Y(38) - 10), 1.3) + arrow_head((X(0), Y(38) - 12), (0, -1))
    for y in range(22, 37, 2):
        s += text(X(0) - 13, Y(y), str(y), 12, cls='b')
    for x in (50, 100, 150, 200):
        s += text(X(x), Y(20) + 15, str(x), 12, cls='b')
    s += text(X(0) - 10, Y(20) + 15, 'O', 12)
    s += text(X(250) + 16, Y(20) + 15, 'x', 13, italic=True)
    s += text(X(0) - 9, Y(38) - 12, 'y', 13, italic=True)
    s += text(X(0) - 3, Y(21), '≈', 12)
    s += (f'<text x="{X(0)-38}" y="{(Y(26)+Y(36))/2}" font-size="12.5" text-anchor="middle" class="b" '
          f'style="writing-mode: vertical-rl; letter-spacing:1px">배송 시간(시간)</text>')
    s += text(X(250) - 30, Y(20) + 33, '배송 거리(km)', 12.5, cls='b')
    for x, y in SCATTER:
        s += f'<circle cx="{X(x):.2f}" cy="{Y(y):.2f}" r="2.9" fill="#000"/>'
    s += text(X(106), Y(32) - 12, 'A', 13)
    s += text(X(180), Y(30) - 12, 'B', 13)
    return svg(380, 255, s)


def fig_q9():
    A, B, C = (40, 25), (40, 125), (195, 125)
    s = poly([A, B, C], sw=1.8) + right_mark(B, A, C, 9)
    p, lp = bulge(A, B, -16); s += p
    s += text(lp[0] - 9, lp[1], '4', 15, cls='b')
    p, lp = bulge(B, C, -18); s += p
    s += text(lp[0], lp[1] + 9, '5', 15, cls='b')
    s += text(A[0], A[1] - 12, 'A', 15, cls='b') + text(B[0] - 10, B[1] + 12, 'B', 15, cls='b')
    s += text(C[0] + 12, C[1] + 4, 'C', 15, cls='b')
    return svg(230, 165, s)


def fig_q12():
    u = 140
    ox, oy = 50, 222
    P = lambda x, y: (ox + x * u, oy - y * u)
    c50, s50, t50 = math.cos(math.radians(50)), math.sin(math.radians(50)), math.tan(math.radians(50))
    s = ''
    O, A, B, C, D = P(0, 0), P(c50, 0), P(c50, s50), P(1, 0), P(1, t50)
    s += poly([O, D, C], fill='#c9c9c9', sw=0)
    for i in range(1, 13):
        s += line(P(i / 10, 0), P(i / 10, 1.4), 0.5, color='#444')
    for j in range(1, 15):
        s += line(P(0, j / 10), P(1.2, j / 10), 0.5, color='#444')
    s += line(P(0, 0), P(1.2, 0), 1.2) + arrow_head((P(1.2, 0)[0] + 10, oy), (1, 0)) + line(P(1.2, 0), (P(1.2, 0)[0] + 6, oy), 1.2)
    s += line(P(0, 0), P(0, 1.4), 1.2) + arrow_head((ox, P(0, 1.4)[1] - 10), (0, -1)) + line(P(0, 1.4), (ox, P(0, 1.4)[1] - 6), 1.2)
    # 사분원
    s += (f'<path d="M{P(0,1)[0]:.2f},{P(0,1)[1]:.2f} A{u},{u} 0 0 1 {C[0]:.2f},{C[1]:.2f}" '
          f'fill="none" stroke="#000" stroke-width="1.2"/>')
    s += line(O, D, 1.6) + line(D, C, 1.6) + line(B, A, 1.6)
    s += line(P(0, s50), B, 1.4, dash='6,3') + line(P(0, t50), D, 1.4, dash='6,3')
    s += right_mark(A, B, C, 6) + right_mark(C, D, (C[0] + 10, C[1]), 6)
    s += arc(O, 18, 0, 50, 1)
    s += text(O[0] + 30, O[1] - 10, '50°', 12, cls='b')
    s += text(O[0] - 10, O[1] + 12, 'O', 13)
    s += text(A[0] + 8, A[1] - 9, 'A', 13) + text(C[0] + 9, C[1] - 9, 'C', 13)
    s += text(B[0] - 4, B[1] - 13, 'B', 13) + text(D[0] + 5, D[1] - 10, 'D', 13)
    s += text(A[0], oy + 13, '0.64', 12) + text(C[0], oy + 13, '1', 12)
    s += text(ox - 6, P(0, t50)[1], '1.19', 12, 'end') + text(ox - 6, P(0, 1)[1], '1', 12, 'end')
    s += text(ox - 6, P(0, s50)[1], '0.77', 12, 'end')
    s += text(P(1.2, 0)[0] + 16, oy + 10, 'x', 13, italic=True) + text(ox - 8, P(0, 1.4)[1] - 10, 'y', 13, italic=True)
    return svg(255, 252, s)


def fig_q13():
    k = 40
    th2 = math.atan(math.sqrt(3) / 2); th1 = th2 + math.radians(60)
    Bm = (0, 0); Am = (4 * math.cos(th1), 4 * math.sin(th1)); Cm = (6 * math.cos(th2), 6 * math.sin(th2))
    ox, oy = 70, 190
    T = lambda p: (ox + p[0] * k, oy - p[1] * k)
    A, B, C = T(Am), T(Bm), T(Cm)
    s = poly([A, B, C], sw=1.8)
    p, lp = bulge(A, B, -16); s += p; s += text(lp[0] - 9, lp[1], '4', 15, cls='b')
    p, lp = bulge(B, C, -20); s += p; s += text(lp[0] + 9, lp[1] + 6, '6', 15, cls='b')
    s += arc(B, 15, angle_at(B, C), angle_at(B, A), 1)
    s += text(B[0] + 8, B[1] - 30, '60°', 13, cls='b')
    s += text(A[0] - 8, A[1] - 10, 'A', 15, cls='b') + text(C[0] + 12, C[1] - 2, 'C', 15, cls='b')
    s += text(B[0], B[1] + 15, 'B', 15, cls='b')
    return svg(300, 215, s)


def fig_q14():
    k = 25
    Bm = (0, 0); Cm = (4 * math.sqrt(3), 0); Am = (-2 * math.sqrt(3), 2); Dm = (-math.sqrt(3) / 2, 1.5)
    ox, oy = 125, 105
    T = lambda p: (ox + p[0] * k, oy - p[1] * k)
    A, B, C, D = T(Am), T(Bm), T(Cm), T(Dm)
    s = poly([A, B, C], sw=1.6) + line(B, D, 1.6)
    s += arc(B, 13, angle_at(B, D), angle_at(B, A), 1) + arc(B, 19, 0, angle_at(B, D), 1)
    s += text(B[0] - 40, B[1] - 26, '30°', 12, cls='b')
    s += text(B[0] + 30, B[1] - 13, '120°', 12, cls='b')
    p, lp = bulge(A, B, -14); s += p; s += text(lp[0] - 6, lp[1] + 8, '4', 14, cls='b')
    p, lp = bulge(B, C, -14); s += p; s += rtext(lp[0], lp[1] + 10, '4', '3', 14)
    s += text(A[0] - 10, A[1] - 6, 'A', 15, cls='b') + text(C[0] + 12, C[1] - 2, 'C', 15, cls='b')
    s += text(B[0], B[1] + 15, 'B', 15, cls='b') + text(D[0] - 2, D[1] - 13, 'D', 15, cls='b')
    return svg(330, 150, s)


def fig_q15():
    s4 = 4 * math.sqrt(3); k = 26
    ox, oy = 40, 215
    T = lambda p: (ox + p[0] * k, oy - p[1] * k)
    Bm, Cm, Am, Dm = (0, 0), (s4, 0), (0, s4), (s4, s4)
    Fm = (s4 / 2, 6); Em = (s4 - 4, s4); Gm = (Em[0] + 2, Em[1] - 2 * math.sqrt(3))
    A, B, C, D, E, F, G = map(T, (Am, Bm, Cm, Dm, Em, Fm, Gm))
    s = poly([A, B, C, D], sw=1.8) + line(B, F, 1.6) + line(E, C, 1.6) + line(G, D, 1.6)
    s += text(A[0] - 10, A[1] - 6, 'A', 15, cls='b') + text(D[0] + 11, D[1] - 6, 'D', 15, cls='b')
    s += text(B[0] - 10, B[1] + 10, 'B', 15, cls='b') + text(C[0] + 11, C[1] + 10, 'C', 15, cls='b')
    s += text(E[0] - 3, E[1] - 11, 'E', 15, cls='b') + text(F[0] - 11, F[1] + 4, 'F', 15, cls='b')
    s += text(G[0] - 9, G[1] + 12, 'G', 15, cls='b')
    return svg(260, 240, s)


def fig_q16():
    a = math.radians(53); W = 46
    y1, y2 = 95, 95 + W
    x0, x1 = 60, 320
    s = ''
    # 기울어진 띠: 단위벡터 d (아래-오른쪽 방향), 법선 n
    d = (math.cos(a), math.sin(a)); n = (math.sin(a), -math.cos(a))
    pb = (175, y2)  # 왼쪽 모서리가 아래 변과 만나는 점
    L1, L2 = -112, 150
    e1 = [(pb[0] + d[0] * t, pb[1] + d[1] * t) for t in (L1, L2)]
    e2 = [(p[0] + n[0] * W, p[1] + n[1] * W) for p in e1]
    # 겹친 부분(평행사변형)
    h = W / math.sin(a)
    tl = pb[0] - W / math.tan(a)
    para = [(tl, y1), (tl + h, y1), (pb[0] + h, y2), pb]
    s += poly(para, fill='#bdbdbd', sw=0)
    s += f'<rect x="{x0}" y="{y1}" width="{x1-x0}" height="{W}" fill="none" stroke="#000" stroke-width="1.6"/>'
    s += poly([e1[0], e1[1], e2[1], e2[0]], sw=1.6)
    p, lp = bulge((x0 - 3, y1), (x0 - 3, y2), -7, dash='2,2'); s += p
    s += text(x0 - 30, (y1 + y2) / 2, '2cm', 13, cls='b')
    s += arc(pb, 16, 180 - 53, 180, 1)
    s += text(pb[0] - 24, pb[1] - 12, 'a', 14, italic=True, cls='b')
    return svg(340, 260, s)


def fig_q17():
    O = (175, 25); R = 150
    P = lambda deg: (O[0] + R * math.sin(math.radians(deg)), O[1] + R * math.cos(math.radians(deg)))
    A, B, L = P(0), P(30), P(-30)
    s = line(O, L, 1.3, dash='2,3') + line(L, P(-34), 1.3, dash='2,3')
    s += line(O, A, 1.3, dash='2,3') + line(O, B, 1.6)
    s += (f'<path d="M{L[0]:.2f},{L[1]:.2f} A{R},{R} 0 0 0 {B[0]:.2f},{B[1]:.2f}" fill="none" stroke="#000" stroke-width="1.6"/>')
    E1 = P(36); E0 = P(-36)
    s += (f'<path d="M{B[0]:.2f},{B[1]:.2f} A{R},{R} 0 0 0 {E1[0]:.2f},{E1[1]:.2f}" fill="none" stroke="#000" stroke-width="1.3" stroke-dasharray="2,3"/>')
    s += (f'<path d="M{E0[0]:.2f},{E0[1]:.2f} A{R},{R} 0 0 0 {L[0]:.2f},{L[1]:.2f}" fill="none" stroke="#000" stroke-width="1.3" stroke-dasharray="2,3"/>')
    s += arc(O, 18, -90, -60, 1)
    s += text(O[0] + 12, O[1] + 42, '30°', 12.5, cls='b')
    s += text(O[0] + 62, O[1] + 70, '10 cm', 13, cls='b')
    for p in (A, B, L):
        s += f'<circle cx="{p[0]:.2f}" cy="{p[1]:.2f}" r="7.5" fill="#fff" stroke="#000" stroke-width="1.2"/>'
        s += f'<circle cx="{p[0]:.2f}" cy="{p[1]:.2f}" r="4" fill="#000"/>'
    s += line((B[0] + 9, B[1]), (325, B[1]), 0.7, dash='1.5,2') + line((A[0] + 9, A[1]), (325, A[1]), 0.7, dash='1.5,2')
    s += line((292, B[1] + 3), (292, A[1] - 3), 0.9) + arrow_head((292, B[1] + 1), (0, -1), 4) + arrow_head((292, A[1] - 1), (0, 1), 4)
    s += text(304, (A[1] + B[1]) / 2, 'h', 13, italic=True)
    s += text(O[0], O[1] - 13, 'O', 14) + text(A[0], A[1] + 20, 'A', 14) + text(B[0] + 12, B[1] + 16, 'B', 14)
    return svg(335, 205, s)


def fig_q19():
    sc = 0.36; ox, oy = -20, -22
    raw = dict(D=(130, 145), E=(345, 290), F=(630, 88), A=(125, 490), B=(345, 645), C=(640, 435))
    p = {k: (ox + x * sc, oy + y * sc) for k, (x, y) in raw.items()}
    D, E, F, A, B, C = (p[k] for k in 'DEFABC')
    defs = ('<defs>'
            '<linearGradient id="g19a" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#e6e6e6"/><stop offset="1" stop-color="#a9a9a9"/></linearGradient>'
            '<linearGradient id="g19b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#b0b0b0"/><stop offset="1" stop-color="#d8d8d8"/></linearGradient>'
            '<linearGradient id="g19c" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d0d0d0"/><stop offset="1" stop-color="#a8a8a8"/></linearGradient>'
            '</defs>')
    s = defs
    s += poly([D, E, F], fill='url(#g19c)', sw=0) + poly([A, B, E, D], fill='url(#g19a)', sw=0) + poly([B, C, F, E], fill='url(#g19b)', sw=0)
    s += line(A, C, 1.3, dash='4,3')
    for a_, b_ in ((D, E), (E, F), (D, F), (D, A), (E, B), (F, C), (A, B), (B, C)):
        s += line(a_, b_, 2.0)
    s += line(D, B, 1.3)
    s += arc(B, 15, angle_at(B, D), angle_at(B, A), 1)
    s += text(B[0] - 17, B[1] - 20, 'a', 14, italic=True, cls='b')
    s += arc(B, 10, angle_at(B, C), angle_at(B, A), 1)
    s += text(B[0] + 32, B[1] + 9, '105°', 13, cls='b')
    s += arc(C, 16, angle_at(C, A) + 360, angle_at(C, B) + 360, 1)
    s += text(C[0] - 30, C[1] + 11, '30°', 13, cls='b')
    pth, lp = bulge(B, C, -14); s += pth
    s += rtext(lp[0] + 26, lp[1] + 10, '10', '2', 13)
    s += text(D[0] - 12, D[1] - 3, 'D', 14, cls='b') + text(E[0] + 10, E[1] + 13, 'E', 14, cls='b')
    s += text(F[0] + 10, F[1] - 5, 'F', 14, cls='b') + text(A[0] - 11, A[1] + 7, 'A', 14, cls='b')
    s += text(B[0], B[1] + 14, 'B', 14, cls='b') + text(C[0] + 12, C[1] + 2, 'C', 14, cls='b')
    return svg(260, 235, s)


def fig_q20():
    k = 95; ox, oy = 150, 212
    T = lambda p: (ox + p[0] * k, oy - p[1] * k)
    r3 = math.sqrt(3)
    H1 = dict(A=(0, 0), B=(1, 0), C=(1.5, r3 / 2), D=(1, r3), E=(0, r3), F=(-0.5, r3 / 2))
    pts2 = [(0, 0)]; dirs = [45, 105, 165, 225, 285]
    for dd in dirs:
        x, y = pts2[-1]
        pts2.append((x + math.cos(math.radians(dd)), y + math.sin(math.radians(dd))))
    H2 = dict(zip('AGHIJK', pts2))
    s = poly([T(H1[c]) for c in 'ABCDEF'], sw=1.6) + poly([T(H2[c]) for c in 'AGHIJK'], sw=1.6)
    A, E, G = T(H1['A']), T(H1['E']), T(H2['G'])
    s += line(A, E, 1.6) + line(E, G, 1.6)
    s += arc(A, 16, 0, 45, 1)
    s += text(A[0] + 37, A[1] - 15, '45°', 13, cls='b')
    off = dict(A=(0, 16), B=(4, 16), C=(13, 0), D=(10, -12), E=(-7, -11), F=(-12, 0),
               G=(14, 6), H=(8, 12), I=(-2, -13), J=(-12, 2), K=(-10, 8))
    for c, pt in list(H1.items()) + list(H2.items())[1:]:
        P_ = T(pt); dx, dy = off[c]
        s += text(P_[0] + dx, P_[1] + dy, c, 14, cls='b')
    return svg(330, 236, s)


def fig_q22():
    k = 150; ox, oy = 165, 30
    T = lambda p: (ox + p[0] * k, oy - p[1] * k)
    t = math.radians(60)
    Am, Bm, Cm, Dm = (0, 0), (0, -1), (1, -1), (1, 0)
    B2 = (-math.sin(t), -math.cos(t)); D2 = (math.cos(t), -math.sin(t)); C2 = (B2[0] + D2[0], B2[1] + D2[1])
    Pm = (0, -0.5 - 0.5 * (math.sin(t) / (1 + math.sin(t))))
    A, B, C, D, B_, C_, D_, P = map(T, (Am, Bm, Cm, Dm, B2, C2, D2, Pm))
    s = poly([A, B, C, D], sw=1.6) + poly([A, B_, C_, D_], sw=1.6) + line(B_, C, 1.6)
    s += text(A[0], A[1] - 13, 'A', 15, cls='b') + text(D[0] + 12, D[1] - 8, 'D', 15, cls='b')
    s += text(B[0] - 12, B[1] + 8, 'B', 15, cls='b') + text(C[0] + 14, C[1] + 4, 'C', 15, cls='b')
    s += text(B_[0] - 14, B_[1] + 2, "B′", 15, cls='b') + text(C_[0] - 8, C_[1] + 18, "C′", 15, cls='b')
    s += text(D_[0] + 14, D_[1] - 12, "D′", 15, cls='b') + text(P[0] + 11, P[1] - 14, 'P', 15, cls='b')
    return svg(345, 275, s)


# ================================================================= 문항
def bogi(items):
    rows = ''.join(f'<div class="bg">{t}</div>' for t in items)
    return f'<div class="bogi"><div class="bogi-t"><span>&nbsp;&lt;보기&gt;&nbsp;</span></div>{rows}</div>'


def table(rows, cls='tb'):
    out = f'<table class="{cls}">'
    for r in rows:
        out += '<tr>' + ''.join(f'<th>{c[1:]}</th>' if c.startswith('#') else f'<td>{c}</td>' for c in r) + '</tr>'
    return out + '</table>'


Q = {}
Q[1] = (q(1, '다음은 농구팀이 최근 10경기에서 성공한 3점 슛의 수를 나타낸 것이다. 자료의 중앙값, 최빈값을 차례로 구한 것은?', 4)
        + f'<div class="figc">{fig_q1()}</div>'
        + choices(['7, 7', '7, 8', '7.5, 8', '8, 8', '8, 8.5'], 3) + '</div>')
Q[2] = (q(2, '다음은 어느 중학교 체육대회에 입을 옷을 선택하기 위해 반 학생 20명이 선호하는 옷의 색을 조사하여 나타낸 것이다. &lt;보기&gt;에서 옳은 것만을 있는 대로 고른 것은?', 4)
        + table([['#선호하는 색', '검정색', '파란색', '노란색', '흰색'], ['#학생 수(명)', '4', '2', '1', '13']])
        + bogi(['ㄱ. 평균은 4이다.', 'ㄴ. 최빈값은 흰색이다.', 'ㄷ. 중앙값은 흰색이다.', 'ㄹ. 이 자료의 대푯값으로 평균이 적합하다.'])
        + choices(['ㄱ', 'ㄴ', 'ㄷ', 'ㄱ, ㄷ', 'ㄴ, ㄹ'], 3) + '</div>')
Q[3] = (q(3, '중간고사 전과목 성적의 표준편차가 민주는 5.1점, 도윤이는 3.5점일 때, 설명 중 옳은 것은?', 4)
        + choices(['도윤이가 민주보다 시험 성적이 더 높다.', '도윤이가 민주보다 시험 성적이 더 낮다.',
                   '민주의 과목별 점수가 도윤이보다 고르다.', '도윤이의 과목별 점수가 민주보다 고르다.',
                   '민주와 도윤이의 시험 성적은 고르기 정도가 같다.'], 1) + '</div>')
Q[4] = (q(4, '다음은 어느 택배 회사 차량들의 배송 거리와 배송 시간 사이의 관계를 나타낸 산점도이다. 이에 대한 설명으로 옳은 것은?', 4)
        + f'<div class="figc">{fig_q4()}</div>'
        + choices(['B는 A 보다 배송시간이 더 걸린다.', '배송 거리가 60km미만인 차량의 수는 7대이다.',
                   '배송 거리와 배송 시간 사이에 음의 상관관계이다.',
                   '배송 거리가 멀면 대체로 배송 시간이 적게 걸린다고 할 수 있다.',
                   '배송 거리가 200km 이상이고, 배송 시간이 26시간 이상인 택배 차는 1대 이다.'], 1) + '</div>')
Q[5] = (q(5, '삼각비의 대소 관계 중 옳은 것은?', 4)
        + choices([f'sin 30{DEG} = cos 30{DEG}', f'sin 40{DEG} = cos 50{DEG}', f'sin 20{DEG} &gt; tan 46{DEG}',
                   f'sin 45{DEG} × cos 45{DEG} &lt; {frac(1, 2)}', f'sin 0{DEG} + cos 90{DEG} + tan 0{DEG} &gt; 1'], 1) + '</div>')
Q[6] = (q(6, '다음 식의 값은?', 4.3)
        + f'<div class="box center">cos 30{DEG} ÷ tan 30{DEG} − sin 30{DEG} × tan 45{DEG}</div>'
        + choices(['0', frac(sq('2'), '2'), '1', sq('3'), '2'], 5) + '</div>')

Q[7] = (q(7, '대푯값과 산포도에 대한 설명으로 &lt;보기&gt;에서 옳은 것만을 있는 대로 고른 것은?', 4.3)
        + bogi(['ㄱ. 편차의 평균은 항상 0이다.', 'ㄴ. 표준편차가 0이 되는 경우는 없다.', 'ㄷ. 변량이 짝수 개이면 중앙값은 두 개다.',
                'ㄹ. 자료의 분산은 표준편차보다 항상 크다.', 'ㅁ. 대푯값에는 평균, 중앙값, 최빈값, 분산, 표준편차 등이 있다.'])
        + choices(['ㄱ', 'ㄱ, ㄹ', 'ㄴ, ㄷ', 'ㄹ, ㅁ', 'ㄴ, ㄷ, ㅁ'], 3) + '</div>')
Q[8] = (q(8, '자료 A, B의 평균이 같을 때, 설명 중 옳은 것은?', 4.3)
        + table([['#자료 A', '15', '10', '6', '9'], ['#자료 B', '7', '10', v('x'), '18']])
        + choices([f'{v("x")}는 10이다.', '자료 A, 자료 B는 분산이 같다.', '자료 B의 편차는 차례로 3, 0, 5, 10이다.',
                   '자료 A가 자료 B 보다 편차의 합이 더 크다.', '자료 B가 자료 A 보다 편차의 제곱의 평균 값이 더 크다.'], 1) + '</div>')
Q[9] = (q(9, '그림의 직각삼각형 ABC에서 삼각비의 값이 옳은 것은?', 4.3)
        + f'<div class="figc">{fig_q9()}</div>'
        + choices([f'sin {v("A")} = {frac("4" + sq("41"), "41")}', f'cos {v("A")} = {frac(4, 5)}',
                   f'sin {v("C")} = {frac(4, 3)}', f'cos {v("C")} = {frac("5" + sq("41"), "41")}',
                   f'tan {v("C")} = {frac(5, 4)}'], 2) + '</div>')
Q[10] = (q(10, '다음은 어느 지역의 최근 5년 동안 연중 최대 적설량을 조사하여 나타낸 것이다. 평균이 20cm일 때, 표준편차는?', 4.5)
         + '<div class="unit">(단위: cm)</div><div class="box center wide">23 &nbsp;&nbsp; 24 &nbsp;&nbsp; 15 &nbsp;&nbsp; 17 &nbsp;&nbsp; 21</div>'
         + choices(['3cm', sq('10') + ' cm', '2' + sq('3') + ' cm', '12cm', '15cm'], 3) + '</div>')
Q[11] = (q(11, '중학교 3학년 학생 10명의 체중을 측정하였더니 평균은 52kg이고 표준편차는 6kg이었다. 그런데 체중계의 오류로 실제 체중보다 3kg씩 작게 측정되었다는 사실을 알게 되었다. 10명의 학생의 실제 체중의 평균과 표준편차는?', 4.5)
         + '<table class="opt"><tr><td></td><td><u>평균(kg)</u></td><td><u>표준편차(kg)</u></td></tr>'
         + ''.join(f'<tr><td>{m}</td><td>{a}</td><td>{b}</td></tr>' for m, a, b in
                   zip('①②③④⑤', (49, 49, 52, 55, 55), (3, 6, 6, 3, 6)))
         + '</table></div>')
Q[12] = (q(12, '그림과 같이 점 O를 중심으로 하고 반지름의 길이가 1인 사분원에 대하여 옳은 것은?', 4.5)
         + f'<div class="figc">{fig_q12()}</div>'
         + choices([f'sin 40{DEG} = {ov("OA")}', f'sin 50{DEG} = 1.19', f'cos 50{DEG} = 0.77',
                    f'tan 50{DEG} = 0.64', f'tan 50{DEG} = {ov("AB")}'], 1) + '</div>')

Q[13] = (q(13, f'{TRI}ABC에서 {ov("AB")} = 4, {ov("BC")} = 6, {ANG}ABC = 60{DEG} 일 때, {ov("AC")}의 길이는?', 4.5)
         + f'<div class="figc">{fig_q13()}</div>'
         + choices([sq('7'), '2' + sq('6'), '5', '3' + sq('3'), '2' + sq('7')], 3) + '</div>')
Q[14] = (q(14, f'그림에서 {ANG}ABD = 30{DEG}, {ANG}DBC = 120{DEG} 이고, {ov("AB")} = 4, {ov("BC")} = 4{sq("3")} 일 때, {ov("AD")}의 길이는?', 4.8)
         + f'<div class="figc">{fig_q14()}</div>'
         + choices([sq('5'), sq('6'), sq('7'), '2' + sq('2'), '3'], 3) + '</div>')
Q[15] = (q(15, f'그림과 같이 정사각형 ABCD에서 점 E, F, G, C는 한 직선 위에 있고, {TRI}BCF, {TRI}EGD는 정삼각형이다. {TRI}BCF의 넓이가 12{sq("3")} 일 때, {ov("ED")}의 길이는?', 4.8)
         + f'<div class="figc">{fig_q15()}</div>'
         + choices(['2', '2' + sq('3'), sq('14'), '4', '4' + sq('3')], 5) + '</div>')
Q[16] = (q(16, f'그림과 같이 폭이 2cm인 직사각형 모양의 띠 두 개가 비스듬히 겹쳐져 있다. 두 띠가 이루는 예각의 크기가 {v("a")}일 때, 겹쳐진 부분의 넓이는?', 4.8)
         + f'<div class="figc">{fig_q16()}</div>'
         + choices([frac(4, 'sin ' + v('a')), frac(4, 'cos ' + v('a')), frac(4, 'tan ' + v('a')),
                    '3 sin ' + v('a'), '4'], 3) + '</div>')

Q[17] = (q(17, f'그림과 같이 길이가 10cm인 줄의 한쪽 끝을 점 O에 고정하고 다른 쪽 끝에 추를 매달았다. 추를 가장 낮은 위치인 A에서 {ANG}AOB = 30{DEG} 가 되는 B 지점까지 움직였다. 이때 A 지점과 B 지점에서의 추의 높이의 차가 {v("h")}cm일 때, {v("h")}의 값은? (단, 추의 크기와 줄의 굵기는 무시한다.)', 4.8)
         + f'<div class="figc">{fig_q17()}</div>'
         + choices([f'5(2 − {sq("3")})', f'10(2 − {sq("3")})', f'1 + {sq("3")}', '5', '5' + sq('3')], 3) + '</div>')
Q[18] = (q(18, f'다음 표는 A반 학생 2명과 B반 학생 2명의 주말 동안 공부 시간의 평균과 분산을 나타낸 것이다. 전체 학생 4명의 주말 동안 공부한 시간의 평균을 {v("x")}시간, 분산을 {v("y")}라 할 때, {v("x")}, {v("y")}의 값은?', 5)
         + table([['#', '#평균(시간)', '#분산'], ['#A 반', '6', '4'], ['#B 반', '4', '2']], 'tb t18')
         + '<table class="opt"><tr><td></td><td><u>평균(시간)</u></td><td><u>분산</u></td></tr>'
         + ''.join(f'<tr><td>{m}</td><td>{a}</td><td>{b}</td></tr>' for m, a, b in
                   zip('①②③④⑤', (5, 5, 5, 6, 6), (3, 4, 5, 3, 4)))
         + '</table></div>')
Q[19] = (q(19, f'그림과 같은 삼각기둥에서 {ov("BC")} = 10{sq("2")}, {ANG}ABC = 105{DEG}, {ANG}BCA = 30{DEG} 이고, {ANG}ABD = {ANG}{v("a")}라 할 때, tan {v("a")} = {sq("2")}이다. 이 삼각기둥의 높이는?', 5)
         + f'<div class="figc">{fig_q19()}</div>'
         + choices(['5', '10', '5' + sq('2'), '8' + sq('2'), '10' + sq('2')], 3) + '</div>')
Q[20] = (q(20, f'그림과 같이 한 변의 길이가 1인 두 정육각형 ABCDEF, AGHIJK가 있다. 점 G가 정육각형 ABCDEF의 내부에 있고 {ANG}BAG = 45{DEG} 일 때, {TRI}AEG의 넓이는?', 5)
         + f'<div class="figc">{fig_q20()}</div>'
         + choices([frac(sq('2'), 4), frac(sq('3'), 4), frac(sq('6'), 4), frac(sq('2'), 2), frac('3' + sq('2'), 4)], 3) + '</div>')

Q[21] = (q(21, f'두 자료 A, B에 대하여 자료 A의 중앙값이 25이고, 두 자료 A, B를 섞은 전체 자료의 중앙값도 25일 때, {v("b")} − {v("a")}의 값은? (단, {v("a")}, {v("b")}는 자연수이고, {v("a")} &lt; {v("b")})', 5.3)
         + table([['#자료 A', '9', '14', '32', '48', v('a'), v('b')], ['#자료 B', '3', '12', '18', '31', v('a') + ' + 3', v('b')]])
         + choices(['1', '2', '3', '4', '5'], 5) + '</div>')
Q[22] = (q(22, f"정사각형 ABCD를 점 A를 중심으로 회전하여 정사각형 AB′C′D′를 만들었다. 세 점 B′, D′, C가 한 직선 위에 있고, {ov('AB')}와 {ov('B′C')}의 교점을 P라 할 때, {ANG}BPC + {ANG}BAD′의 크기는?", 5.3)
         + f'<div class="figc">{fig_q22()}</div>'
         + choices([f'75{DEG}', f'90{DEG}', f'105{DEG}', f'120{DEG}', f'135{DEG}'], 5) + '</div>')

# ================================================================= 페이지
HEAD1 = '''<table class="hd"><tr>
<td class="h1">2026학년도 2학기 1차 정기시험</td><td class="h2">잠실여자중학교</td>
<td rowspan="2" class="h3">선택형</td><td rowspan="2" class="h3">22문항</td><td rowspan="2" class="h3">100점</td>
<td class="pg">page</td></tr>
<tr><td class="h1">10월 2일 금요일 1교시</td><td class="h2">3학년 수학과</td><td class="pg">1/5</td></tr></table>'''


def head(n):
    return (f'<table class="hd"><tr><td class="h1">2026학년도 2학기 1차 정기시험</td>'
            f'<td class="h2">10월 2일 금요일 1교시</td><td class="h2">3학년 수학과</td>'
            f'<td class="pg">page</td><td class="pg">{n}/5</td></tr></table>')


NOTICE = '<div class="notice">※ 선택형 22문항입니다. 각 문항별 배점이 다르니 물음의 끝에 표시된 배점을 참고하시오.</div>'
FOOT = '이 시험문제의 저작권은 잠실여자중학교에 있습니다. 무단 전송·복제·배포 시 저작권법에 의거 처벌 될 수 있습니다.'


def page(n, left, right, cont=None, end=False):
    hd = HEAD1 if n == 1 else head(n)
    c = f'<div class="cont">{cont}</div>' if cont else ''
    e = '<div class="end">&lt;끝&gt;</div>' if end else ''
    return (f'<section class="page"><div class="frame">{hd}<div class="cols">'
            f'<div class="col left">{left}{e}</div><div class="col right">{right}{c}</div>'
            f'</div></div><div class="foot">{FOOT}</div></section>')


PAGES = [
    page(1, NOTICE + Q[1] + Q[2] + Q[3], Q[4] + Q[5] + Q[6], '다음 면에 계속'),
    page(2, Q[7] + Q[8] + Q[9], Q[10] + Q[11] + Q[12], '다음 장에 계속'),
    page(3, Q[13] + Q[14], Q[15] + Q[16], '다음 면에 계속'),
    page(4, Q[17] + Q[18], Q[19] + Q[20], '다음 장에 계속'),
    page(5, Q[21] + Q[22], '', end=True),
]

CSS = r'''
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #fff; color: #000; }
body { font-family: "Liberation Serif", "NanumMyeongjo", "Noto Serif CJK KR", serif; font-size: 10.2pt; line-height: 1.55; }
.page { width: 210mm; height: 297mm; padding: 9mm 9mm 0; page-break-after: always; overflow: hidden; }
.page:last-child { page-break-after: auto; }
.frame { border: 1.6px solid #000; height: 276mm; display: flex; flex-direction: column; }
.hd { width: 100%; border-collapse: collapse; font-weight: bold; font-size: 11pt; }
.hd td { border-bottom: 1.6px solid #000; border-left: 1.2px solid #000; padding: 3px 6px; text-align: center; white-space: nowrap; }
.hd td:first-child { border-left: none; }
.hd tr:first-child td[rowspan], .hd tr:first-child td.h1, .hd tr:first-child td.h2 { }
.hd .pg { width: 1%; }
.cols { flex: 1; display: flex; min-height: 0; }
.col { width: 50%; padding: 5mm 4.5mm 3mm; position: relative; }
.col.left { border-right: 1.2px solid #000; }
.notice { font-weight: bold; margin-bottom: 4mm; }
.q { margin-bottom: 6mm; }
.qt { text-align: justify; word-break: keep-all; }
.qn { font-weight: normal; }
.var, i { font-family: "Liberation Serif", serif; font-style: italic; }
.ch * { text-indent: 0; }
.frac { display: inline-flex; flex-direction: column; vertical-align: middle; text-align: center; margin: 0 2px; line-height: 1.15; }
.frac .num { border-bottom: 1px solid #000; padding: 0 2px; }
.frac .den { padding: 0 2px; }
.sqrt { white-space: nowrap; }
.sqrt .rad { margin-right: -1px; }
.sqrt .rc { border-top: 1px solid #000; padding: 0 1px; }
.ov { border-top: 1px solid #000; padding-top: 0; line-height: 1.1; display: inline-block; }
.choices { display: grid; column-gap: 6px; row-gap: 3px; margin-top: 2mm; align-items: center; }
.choices.c1 { grid-template-columns: 1fr; }
.choices.c2 { grid-template-columns: 1fr 1fr; }
.choices.c3 { grid-template-columns: 1fr 1fr 1fr; }
.choices.c5 { grid-template-columns: repeat(5, auto); justify-content: space-between; }
.ch { word-break: keep-all; padding-left: 1.3em; text-indent: -1.3em; }
.choices.c2 .ch, .choices.c3 .ch, .choices.c5 .ch { padding-left: 0; text-indent: 0; }
.figc { text-align: center; margin: 2mm 0; }
.fig { max-width: 100%; height: auto; }
.fig text { font-family: "Liberation Serif", "NanumMyeongjo", serif; fill: #000; }
.fig text.b { }
.tb { border-collapse: collapse; width: 100%; margin: 2mm 0; text-align: center; border-top: 1.5px solid #000; border-bottom: 1.5px solid #000; }
.tb th, .tb td { border-bottom: 1px solid #000; padding: 2px 4px; }
.tb tr th + td, .tb td + td { border-left: 1px solid #000; }
.tb th { background: #c8c8c8; font-weight: normal; white-space: nowrap; }
.t18 th + th { border-left: 1px solid #000; }
.t18 td, .t18 th { width: 33%; }
.bogi { border: 1px solid #000; padding: 3mm 3mm 2mm; margin: 4mm 0 2mm; position: relative; }
.bogi-t { position: absolute; top: -0.85em; left: 0; right: 0; text-align: center; line-height: 1.5; }
.bogi-t::before { content: ""; }
.bogi-t { background: transparent; }
.bogi-t span { background: #fff; }
.bg { padding-left: 1.4em; text-indent: -1.4em; word-break: keep-all; }
.box { border: 1px solid #000; padding: 2mm 3mm; margin: 2mm 0; }
.box.wide { padding: 3mm; }
.center { text-align: center; }
.unit { text-align: right; font-size: 9.5pt; margin-top: 1mm; }
table.opt { border-collapse: collapse; margin: 2mm auto 0; text-align: center; }
table.opt td { padding: 0 9mm; line-height: 1.6; }
table.opt td:first-child { padding: 0 4mm 0 0; }
.cont { position: absolute; right: 4.5mm; bottom: 3mm; font-weight: bold; }
.end { position: absolute; left: 0; right: 0; bottom: 3mm; text-align: center; font-weight: bold; }
.foot { text-align: center; font-size: 9.5pt; font-weight: bold; padding-top: 1.5mm; letter-spacing: 0.2px; }
'''

HTML = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>2026 2학기 1차 정기시험 3학년 수학</title>'
        f'<style>{CSS}</style></head><body>{"".join(PAGES)}</body></html>')

if __name__ == '__main__':
    html_path = os.path.join(HERE, 'exam.html')
    pdf_path = os.path.join(HERE, '2026_2학기_1차_정기시험_3학년_수학.pdf')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(HTML.replace('&lt;보기&gt;</div>', '&lt;보기&gt;</div>'))
    chrome = os.environ.get('CHROME', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    subprocess.run([chrome, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                    f'--print-to-pdf={pdf_path}', 'file://' + html_path], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(pdf_path)
