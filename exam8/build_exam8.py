# -*- coding: utf-8 -*-
"""잠실여자중학교 2026학년도 2학기 2차 정기시험 3학년 수학 원본 시험지 복원.

첫 번째 잠실여중 시험지(exam/build_exam.py)와 같은 틀을 쓰고, 문항은 원본 위치(단 위에서의 mm)에
놓는다. 그림은 모두 SVG로 새로 그리고 Chromium으로 A4 PDF를 만든다.
  python3 exam8/build_exam8.py
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



def P(c, r, deg):
    return (c[0] + r * math.cos(math.radians(deg)), c[1] - r * math.sin(math.radians(deg)))


def sub(p, q): return (p[0] - q[0], p[1] - q[1])
def add(p, q): return (p[0] + q[0], p[1] + q[1])
def mul(p, k): return (p[0] * k, p[1] * k)
def mid(p, q): return ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
def dist(p, q): return math.hypot(p[0] - q[0], p[1] - q[1])


def unit(v):
    n = math.hypot(*v)
    return (v[0] / n, v[1] / n)


def inter(p1, p2, p3, p4):
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def foot(p, a, b):
    d = sub(b, a)
    t = ((p[0] - a[0]) * d[0] + (p[1] - a[1]) * d[1]) / (d[0] ** 2 + d[1] ** 2)
    return (a[0] + d[0] * t, a[1] + d[1] * t)


def circ(c, r, sw=1.6, fill='none'):
    return f'<circle cx="{c[0]:.2f}" cy="{c[1]:.2f}" r="{r:.2f}" fill="{fill}" stroke="#000" stroke-width="{sw}"/>'


def dot(p, r=2.6):
    return f'<circle cx="{p[0]:.2f}" cy="{p[1]:.2f}" r="{r}" fill="#000"/>'


def angarc(c, p1, p2, r, sw=1.0, fill=None):
    """c에서 p1, p2 방향 사이의 작은 각 호(채우기 선택)"""
    a1, a2 = angle_at(c, p1), angle_at(c, p2)
    if (a2 - a1) % 360 > 180:
        a1, a2 = a2, a1
    sw_ = (a2 - a1) % 360
    q1, q2 = P(c, r, a1), P(c, r, a1 + sw_)
    out = ''
    if fill:
        out += (f'<path d="M{c[0]:.2f},{c[1]:.2f} L{q1[0]:.2f},{q1[1]:.2f} A{r},{r} 0 0 0 {q2[0]:.2f},{q2[1]:.2f} Z" '
                f'fill="{fill}" stroke="none"/>')
    return out + (f'<path d="M{q1[0]:.2f},{q1[1]:.2f} A{r},{r} 0 0 0 {q2[0]:.2f},{q2[1]:.2f}" fill="none" '
                  f'stroke="#000" stroke-width="{sw}"/>')


def bis(c, p1, p2):
    a1, a2 = angle_at(c, p1), angle_at(c, p2)
    if (a2 - a1) % 360 > 180:
        a1, a2 = a2, a1
    return a1 + ((a2 - a1) % 360) / 2


def ticks(p, q, n=2, L=4.5, gap=2.6):
    m_, u = mid(p, q), unit(sub(q, p))
    nr = (-u[1], u[0])
    out = ''
    for i in range(n):
        c = add(m_, mul(u, (i - (n - 1) / 2) * gap))
        out += line(add(c, mul(nr, L)), sub(c, mul(nr, L)), 1.0)
    return out


def dcurve(p, q, k):
    """p→q 점선 곡선(길이 표시). k>0이면 진행 방향 왼쪽으로 볼록. 라벨 위치도 돌려준다."""
    p_, l = bulge(p, q, k, dash='2.5,2.5', sw=0.9)
    return p_, l


def T(p, s, dx=0, dy=0, size=15, italic=False):
    return text(p[0] + dx, p[1] + dy, s, size, italic=italic, cls='b')


# ================================================================= 그림
def f1():
    c, R = (150, 92), 82
    k = R / 10
    y = c[1] + 8 * k
    L, Rr = (c[0] - 6 * k, y), (c[0] + 6 * k, y)
    H = (c[0], y)
    s = circ(c, R) + line(L, Rr, 1.5) + line(c, H, 1.3) + line(c, L, 1.3) + dot(c) + right_mark(H, c, Rr, 6)
    p, lp = dcurve(c, L, 14); s += p + T(lp, '10 cm', -20, -6, 14)
    s += T((c[0] + 22, (c[1] + y) / 2), '8 cm', 0, 0, 14)
    p, lp = dcurve(L, Rr, -12); s += p
    s += line((Rr[0] - 10, y + 10), (Rr[0] + 14, y + 20), 0.8) + text(Rr[0] + 34, y + 22, 'x', 15, italic=True) + T((Rr[0] + 53, y + 22), 'cm', 0, 0, 14)
    s += T(c, 'O', 0, -13)
    return svg(300, 195, s)


def f2():
    c, R = (150, 98), 82
    A, B, C = P(c, R, 90), P(c, R, 190), P(c, R, -10)
    Pf, Qf = foot(c, A, B), foot(c, A, C)
    s = circ(c, R) + poly([A, B, C], sw=1.5) + line(c, Pf, 1.2) + line(c, Qf, 1.2) + dot(c)
    s += right_mark(Pf, A, c, 6) + right_mark(Qf, A, c, 6) + ticks(c, Pf) + ticks(c, Qf)
    s += angarc(A, B, C, 13) + angarc(B, C, A, 16) + angarc(C, A, B, 16)
    s += T(A, 'x', 0, 23, 15, True) + T(B, 'y', 24, -8, 15, True) + T(C, '50°', -30, -9, 13)
    p, lp = dcurve(A, C, 14); s += p
    s += line(P(c, R + 6, 47), (c[0] + 104, 22), 0.8) + T((c[0] + 130, 20), '6 cm', 0, 0, 14)
    s += T(A, 'A', 0, -12) + T(B, 'B', -12, 4) + T(C, 'C', 13, 4) + T(Pf, 'P', -11, -6) + T(Qf, 'Q', 11, -6)
    s += T(c, 'O', 0, -13)
    return svg(300, 190, s)


def f3():
    c, r = (95, 88), 62
    Pp = P(c, 2 * r, -30)
    A, B = P(c, r, 30), P(c, r, -90)
    s = circ(c, r) + line(Pp, A, 1.5) + line(Pp, B, 1.5) + dot(c, 2.2)
    p, lp = dcurve(A, Pp, 14); s += p
    s += T(add(lp, (44, -4)), '(<tspan font-style="italic">x</tspan>+4) cm', 0, 0, 15)
    p, lp = dcurve(B, Pp, -12); s += p + T(lp, '10 cm', 0, 10, 15)
    s += T(c, 'O', -11, 0) + T(A, 'A', 2, -12) + T(B, 'B', -2, 14) + T(Pp, 'P', 13, 4)
    return svg(300, 175, s)


def f4():
    c, R = (150, 82), 70
    A, B, Pp = P(c, R, 190), P(c, R, -10), P(c, R, 270)
    s = circ(c, R) + line(Pp, A, 1.5) + line(Pp, B, 1.5) + line(c, A, 1.3) + line(c, B, 1.3) + dot(c)
    s += angarc(Pp, A, B, 13) + T(Pp, '100°', 0, -22, 13)
    q1, q2 = P(c, 10, -10), P(c, 10, 190)
    s += f'<path d="M{q1[0]:.2f},{q1[1]:.2f} A10,10 0 1 0 {q2[0]:.2f},{q2[1]:.2f}" fill="none" stroke="#000" stroke-width="1"/>'
    s += text(c[0], c[1] - 20, '<tspan font-style="italic">x</tspan>°', 13, cls='b')
    s += T(c, 'O', 0, 13, 14) + T(A, 'A', -12, 0) + T(B, 'B', 12, 2) + T(Pp, 'P', 0, 13)
    return svg(300, 172, s)


def f5():
    c, R = (130, 92), 75
    A, B, C, D = P(c, R, 130), P(c, R, 225), P(c, R, -50), P(c, R, 35)
    E = add(C, mul(unit(sub(C, B)), 55))
    s = circ(c, R) + poly([A, B, C, D], sw=1.5) + line(C, add(E, mul(unit(sub(C, B)), 22)), 1.3) + dot(E, 2.2)
    s += angarc(A, B, D, 14) + T(A, '85°', 12, 18, 13)
    s += angarc(C, D, E, 11) + T(C, '<tspan font-style="italic">x</tspan>°', 18, -10, 13)
    s += T(A, 'A', -8, -12) + T(B, 'B', -12, 6) + T(C, 'C', -2, 14) + T(D, 'D', 12, -4) + T(E, 'E', 0, 13)
    return svg(300, 180, s)


def f6():
    c, R = (140, 98), 82
    A, D, B, C = P(c, R, 160), P(c, R, 70), P(c, R, 207), P(c, R, -63)
    F1, F2 = foot(c, A, D), foot(c, B, C)
    s = circ(c, R) + line(A, D, 1.5) + line(B, C, 1.5)
    for p_ in (A, D, B, C):
        s += line(c, p_, 1.3)
    s += line(c, F1, 1.2) + line(c, F2, 1.2) + right_mark(F1, D, c, 6) + right_mark(F2, C, c, 6)
    s += ticks(c, F1) + ticks(c, F2) + dot(c)
    p, lp = dcurve(B, C, -12); s += p + T(lp, '4cm', 0, 8, 14)
    s += T(A, 'A', -13, -2) + T(D, 'D', 6, -12) + T(B, 'B', -12, 6) + T(C, 'C', 10, 10) + T(c, 'O', 14, 4)
    return svg(290, 196, s)


def tangent_polygon(c, r, normals):
    lines_ = [(P(c, r, a), P(add(P(c, r, a), (0, 0)), 10, a + 90)) for a in normals]
    n = len(lines_)
    return [inter(*lines_[i - 1], *lines_[i]) for i in range(n)]


def f7():
    c, r = (145, 92), 58
    B, A, D, C = tangent_polygon(c, r, [190, 95, -8, -90])
    s = circ(c, r) + poly([A, D, C, B], sw=1.5) + dot(c)
    p, lp = dcurve(A, D, 12); s += p + text(lp[0] - 8, lp[1] - 8, 'x', 15, italic=True) + T(lp, 'cm', 12, -8, 14)
    p, lp = dcurve(D, C, 12); s += p + T(lp, '10 cm', 26, 0, 14)
    p, lp = dcurve(C, B, 12); s += p + T(lp, '10 cm', 0, 10, 14)
    p, lp = dcurve(B, A, 12); s += p + T(lp, '8 cm', -24, 0, 14)
    s += T(A, 'A', -10, -8) + T(D, 'D', 8, -10) + T(C, 'C', 12, 6) + T(B, 'B', -8, 12) + T(c, 'O', 0, 14)
    return svg(300, 190, s)


def f8():
    c, R = (150, 92), 75
    A, B, C, E, D = P(c, R, 180), P(c, R, 0), P(c, R, 128), P(c, R, 75), P(c, R, 300)
    s = circ(c, R) + line(A, B, 1.5) + line(A, C, 1.5) + line(C, D, 1.5) + line(E, D, 1.5) + line(E, B, 1.5) + dot(c, 3)
    s += angarc(C, A, D, 13) + T(C, '60°', 4, 22, 14)
    s += angarc(E, D, B, 13) + text(E[0] - 14, E[1] + 26, '<tspan font-style="italic">x</tspan>°', 15, cls='b')
    s += T(A, 'A', -13, 0) + T(B, 'B', 13, 0) + T(C, 'C', -8, -12) + T(E, 'E', 2, -13) + T(D, 'D', 4, 14)
    s += T(c, 'O', 0, -14)
    return svg(300, 184, s)


def f9():
    c, R = (140, 85), 70
    A, C, B = P(c, R, 270), P(c, R, 190), P(c, R, 70)
    Tt = (A[0] + 110, A[1])
    s = circ(c, R) + line((A[0] - 95, A[1]), (A[0] + 130, A[1]), 1.4) + dot(Tt, 2.6)
    s += poly([A, B, C], sw=1.5) + dot(c, 2.4)
    s += angarc(A, (A[0] - 50, A[1]), C, 16) + T(A, '40°', -38, -10, 13)
    s += angarc(A, C, B, 20) + T(A, '60°', -8, -30, 13)
    s += angarc(C, A, B, 10)
    s += T(A, 'A', 0, 14) + T(B, 'B', 4, -12) + T(C, 'C', -12, 2) + T(Tt, 'T', 0, 14) + T(c, 'O', 0, -13)
    return svg(300, 180, s)


def f10():
    c, R, r = (150, 98), 92, 58
    h = math.sqrt(R * R - r * r)
    Pp, Q = (c[0] - h, c[1] + r), (c[0] + h, c[1] + r)
    s = (f'<path d="M{c[0] - R},{c[1]} a{R},{R} 0 1 0 {2 * R},0 a{R},{R} 0 1 0 {-2 * R},0 Z '
         f'M{c[0] - r},{c[1]} a{r},{r} 0 1 0 {2 * r},0 a{r},{r} 0 1 0 {-2 * r},0 Z" fill="#8a8a8a" fill-rule="evenodd" '
         f'stroke="#000" stroke-width="1.4"/>')
    s += line(Pp, Q, 1.5) + dot(c, 2.8)
    p, lp = dcurve(Pp, Q, -8); s += p.replace('#000', '#000') + T(lp, '10', 0, 4, 14)
    s += T(c, 'O', 0, -13) + T(Pp, 'P', -12, 4) + T(Q, 'Q', 12, 4)
    return svg(300, 200, s)


def f11():
    c, r = (200, 90), 70
    Pp = (c[0] - r * 10 / 6, c[1])
    d = dist(c, Pp)
    al = math.degrees(math.acos(r / d))
    A, B = P(c, r, 180 - al), P(c, r, 180 + al)
    s = circ(c, r) + line(Pp, A, 1.5) + line(Pp, B, 1.5) + line(c, A, 1.5) + line(c, B, 1.5) + line(Pp, c, 1.5) + dot(c, 3)
    s += right_mark(B, Pp, c, 6)
    p, lp = dcurve(Pp, c, -10); s += p + T(lp, '10', 0, 6, 15)
    p, lp = dcurve(Pp, B, -12); s += p + T(lp, '8', -6, 4, 15)
    s += T(A, 'A', 0, -12) + T(B, 'B', 2, 14) + T(Pp, 'P', -13, 0) + T(c, 'O', 14, 0)
    return svg(300, 185, s)


def f12():
    c, r = (130, 124), 44
    E, D, F = P(c, r, 270), P(c, r, 170), P(c, r, 38)
    tl = lambda p_, a: (p_, P(p_, 10, a + 90))
    LE, LD, LF = tl(E, 270), tl(D, 170), tl(F, 38)
    A, B, C = inter(*LD, *LF), inter(*LD, *LE), inter(*LE, *LF)
    s = poly([A, B, C], sw=1.5) + circ(c, r, 1.4) + poly([D, E, F], sw=1.3) + dot(c, 2.4)
    s += angarc(A, B, C, 14) + T(A, '48°', 0, 24, 13)
    s += angarc(F, D, E, 14) + T(F, '50°', -28, -10, 13)
    s += angarc(C, A, B, 14) + T(C, 'x', -24, -8, 15, True)
    s += T(A, 'A', 0, -12) + T(B, 'B', -12, 4) + T(C, 'C', 12, 4) + T(D, 'D', -12, -4) + T(E, 'E', 0, 14)
    s += T(F, 'F', 10, -8) + T(c, 'O', 0, 13)
    return svg(270, 214, s)


def f13():
    c, R = (140, 95), 82
    A, B, C, D = P(c, R, 125), P(c, R, 55), P(c, R, 200), P(c, R, -20)
    s = circ(c, R) + line(A, B, 1.5) + line(C, D, 1.5) + line(A, D, 1.5) + line(B, C, 1.5) + dot(c, 2.6)
    s += arrow_head(add(mid(A, B), (6, 0)), (1, 0), 7) + arrow_head(add(mid(C, D), (6, 0)), (1, 0), 7)
    s += T(A, 'A', -8, -11) + T(B, 'B', 10, -10) + T(C, 'C', -12, 2) + T(D, 'D', 12, 4) + T(c, 'O', -12, 2)
    return svg(290, 192, s)


def f15():
    c, R = (140, 100), 88
    A, B, C = P(c, R, 90), P(c, R, 210), P(c, R, -30)
    Pm, Qm, Rm = mid(A, B), mid(B, C), mid(A, C)
    s = circ(c, R) + poly([A, B, C], sw=1.5) + line(A, Qm, 1.2) + line(B, Rm, 1.2) + line(C, Pm, 1.2)
    s += dot(Pm, 2.6) + dot(Qm, 2.6) + dot(Rm, 2.6) + dot(c, 2.4)
    s += T(A, 'A', 0, -12) + T(B, 'B', -12, 6) + T(C, 'C', 13, 6) + T(Pm, 'P', -13, -6) + T(Rm, 'R', 13, -6)
    s += T(Qm, 'Q', 0, 14)
    return svg(280, 200, s)


def f16():
    c, r = (200, 72), 50
    Pp = (c[0] - 150, c[1] + 18)
    d = dist(c, Pp)
    base = angle_at(c, Pp)
    al = math.degrees(math.acos(r / d))
    A, B = P(c, r, base - al), P(c, r, base + al)
    s = circ(c, r) + line(Pp, add(A, mul(unit(sub(A, Pp)), 45)), 1.4) + line(Pp, add(B, mul(unit(sub(B, Pp)), 45)), 1.4)
    s += line(Pp, c, 1.4) + line(c, A, 1.3) + line(c, B, 1.3) + dot(c, 2.6)
    s += right_mark(A, Pp, c, 6) + right_mark(B, Pp, c, 6) + ticks(c, A, 1) + ticks(c, B, 1)
    s += T(A, 'A', -4, -12) + T(B, 'B', -4, 14) + T(Pp, 'P', -12, 0) + T(c, 'O', 12, 2)
    return svg(300, 150, s)


def f17():
    c, R = (110, 175), 64
    B, C, D, A = P(c, R, 200), P(c, R, 350 - 360), P(c, R, 24), P(c, R, 94)
    Pp = inter(B, A, C, D)
    Q = inter(A, D, B, C)
    s = circ(c, R) + line(B, Pp, 1.5) + line(C, Pp, 1.5) + line(B, Q, 1.5) + line(A, Q, 1.5)
    s += angarc(B, Pp, Q, 16) + T(B, 'x', 22, -9, 15, True)
    s += angarc(Pp, B, C, 18) + T(Pp, '40°', -2, 34, 13)
    s += angarc(Q, B, A, 20) + T(Q, '36°', -34, -8, 13)
    s += T(A, 'A', -12, -2) + T(B, 'B', -12, 6) + T(C, 'C', 6, 14) + T(D, 'D', 13, -4) + T(Pp, 'P', 0, -12)
    s += T(Q, 'Q', 12, 4)
    return svg(300, 262, s), (Pp, Q)


def f18():
    k = 19
    A, D, B, C = (20, 85), (20 + 12 * k, 85), (20, 85 + 5 * k), (20 + 12 * k, 85 + 5 * k)
    f_ = foot(B, A, C)
    E = (2 * f_[0] - B[0], 2 * f_[1] - B[1])
    F = inter(A, D, E, C)
    r = 35 / 24 * k
    O = (D[0] - r, D[1] + r)
    G, I = (O[0], D[1]), (D[0], O[1])
    H = foot(O, F, C)
    s = line(A, B, 1.3, '4,3') + line(B, C, 1.3, '4,3')
    s += line(A, E, 1.5) + line(E, C, 1.5) + line(A, C, 1.5) + line(A, D, 1.5) + line(D, C, 1.5)
    s += circ(O, r, 1.4) + dot(O, 2.2)
    for p_ in (G, H, I):
        s += dot(p_, 1.8)
    s += T(mid(A, B), '5', -10, 0, 14) + T(mid(B, C), '12', 0, 12, 14)
    s += T(A, 'A', -12, 0) + T(B, 'B', -10, 8) + T(C, 'C', 12, 6) + T(D, 'D', 10, -10) + T(E, 'E', 0, -12)
    s += T(F, 'F', 0, -12) + T(G, 'G', -2, -11, 13) + T(H, 'H', -9, 10, 13) + T(I, 'I', 10, 0, 13) + T(O, 'O', 0, -10, 13)
    return svg(285, 205, s)


def solve19():
    # BC = CD = R - 2, AD = 8 (반지름 R)
    lo, hi = 4.01, 30.0
    def g(R):
        th = 2 * math.asin((R - 2) / (2 * R))
        return 2 * R * math.cos(th) - 8
    for _ in range(200):
        m_ = (lo + hi) / 2
        if g(lo) * g(m_) <= 0:
            hi = m_
        else:
            lo = m_
    return (lo + hi) / 2


def f19():
    Rr = solve19()
    k = 108 / Rr
    c = (140, 140)
    R = Rr * k
    th = math.degrees(2 * math.asin((Rr - 2) / (2 * Rr)))
    A, B = P(c, R, 180), P(c, R, 0)
    C, D = P(c, R, th), P(c, R, 2 * th)
    s = (f'<path d="M{A[0]:.2f},{A[1]:.2f} A{R:.2f},{R:.2f} 0 0 1 {B[0]:.2f},{B[1]:.2f}" fill="none" stroke="#000" '
         f'stroke-width="1.6"/>')
    for a, b in ((A, B), (A, D), (A, C), (D, B), (D, C), (C, B)):
        s += line(a, b, 1.4)
    p, lp = dcurve(A, D, 12); s += p + T(lp, '8', -2, 0, 15)
    p, lp = dcurve(A, B, -14); s += p + text(lp[0], lp[1] + 6, '2<tspan font-style="italic">r</tspan>', 15, cls='b')
    s += T(A, 'A', -12, 4) + T(B, 'B', 12, 4) + T(C, 'C', 10, -8) + T(D, 'D', 2, -12)
    return svg(285, 175, s), Rr


def f20():
    k = 30
    O = (150, 140)
    A, B, M = (O[0] - 4 * k, O[1]), (O[0] + 4 * k, O[1]), (O[0] - 2 * k, O[1])

    def hit(deg):
        u = (math.cos(math.radians(deg)), -math.sin(math.radians(deg)))
        f_ = sub(M, O)
        b = f_[0] * u[0] + f_[1] * u[1]
        t = -b + math.sqrt(b * b - (f_[0] ** 2 + f_[1] ** 2 - (4 * k) ** 2))
        return add(M, mul(u, t))
    Pp, Q = hit(120), hit(60)
    s = (f'<path d="M{A[0]},{A[1]} A{4 * k},{4 * k} 0 0 1 {B[0]},{B[1]}" fill="none" stroke="#000" stroke-width="1.6"/>')
    s += line(A, B, 1.5) + line(M, Pp, 1.5) + line(M, Q, 1.5) + line(Pp, Q, 1.5) + dot(O, 2.6)
    s += angarc(M, A, Pp, 12) + T(M, '60°', -28, -10, 14) + angarc(M, O, Q, 12) + T(M, '60°', 28, -10, 14)
    p, lp = dcurve(A, B, -46); s += p + T(lp, '8', 0, 10, 14)
    s += T(A, 'A', -12, 4) + T(B, 'B', 12, 4) + T(M, 'M', 0, 14) + T(O, 'O', 0, 14) + T(Pp, 'P', -11, -6)
    s += T(Q, 'Q', 6, -12)
    return svg(300, 205, s), dist(Pp, Q) / k


def f21():
    k = 26
    A = (110, 178)
    O, Tt = (A[0], A[1] - 3 * k), (A[0] + 6 * k, A[1])
    r = 3 * k
    u = unit(sub(Tt, O))
    f_ = sub(O, O)
    B = add(O, mul(u, r))
    phi = angle_at(A, B)
    Pp = add(A, mul((math.cos(math.radians(2 * phi)), -math.sin(math.radians(2 * phi))), 2 * r * math.sin(math.radians(2 * phi))))
    s = circ(O, r) + line((A[0] - 95, A[1]), (Tt[0] + 60, A[1]), 1.4) + line(A, O, 1.4) + line(O, Tt, 1.4)
    s += line(A, Pp, 1.4) + line(A, B, 1.4) + dot(O, 2.4) + dot(Tt, 2.6) + dot(Pp, 2.4) + dot(B, 2.4)
    s += dot(P(A, 15, phi * 1.5), 1.8) + dot(P(A, 18, phi / 2), 1.8)
    p, lp = dcurve(A, O, -10); s += p + T(lp, '3', -6, 0, 15)
    p, lp = dcurve(A, Tt, -10); s += p + T(lp, '6', 0, 6, 15)
    s += T(A, 'A', 0, 14) + T(Tt, 'T', 2, 14) + T(O, 'O', 2, -12) + T(B, 'B', 10, -10) + T(Pp, 'P', 4, -12)
    return svg(300, 205, s), 2 * phi


def f22():
    c, R = (140, 85), 70
    s = circ(c, R)
    for i in range(12):
        s += dot(P(c, R, 90 - 30 * i), 2.8)
    return svg(280, 170, s)
# ================================================================= 문항
def bogi(items):
    rows = ''.join(f'<div class="bg">{t}</div>' for t in items)
    return f'<div class="bogi"><div class="bogi-t"><span>&nbsp;&lt;보기&gt;&nbsp;</span></div>{rows}</div>'


def table(rows, cls='tb'):
    out = f'<table class="{cls}">'
    for r in rows:
        out += '<tr>' + ''.join(f'<th>{c[1:]}</th>' if c.startswith('#') else f'<td>{c}</td>' for c in r) + '</tr>'
    return out + '</table>'



def qa(top, body):
    """원본처럼 단 안의 정해진 위치(mm)에 문항을 놓는다."""
    return f'<div class="qa" style="top:{top}mm">{body}</div>'


def I(x):
    return v(x)


SQ2 = sq('2')
Q = {}
Q[1] = q(1, f'다음 그림에서 {v("x")}의 값은?', '4.0') + f'<div class="figc">{f1()}</div>' + choices(['6', '8', '10', '12', '14'], 5) + '</div>'
Q[2] = (q(2, f'다음 그림에서 {ANG}{v("x")} − {ANG}{v("y")}는?', '4.0') + f'<div class="figc">{f2()}</div>'
        + choices([f'30{DEG}', f'40{DEG}', f'50{DEG}', f'60{DEG}', f'70{DEG}'], 5) + '</div>')
Q[3] = (q(3, f'다음 그림에서 두 점 A, B는 원 O의 외부의 한 점 P에서 원 O에 그은 두 접선의 접점일 때, {v("x")}의 값은?', '4.0')
        + f'<div class="figc">{f3()}</div>' + choices(['4', '6', '10', '14', '16'], 5) + '</div>')
Q[4] = q(4, f'다음 그림에서 {v("x")}의 값은?', '4.0') + f'<div class="figc">{f4()}</div>' + choices(['190', '200', '230', '260', '280'], 5) + '</div>'
Q[5] = q(5, f'다음 그림에서 {v("x")}의 값은?', '4.0') + f'<div class="figc">{f5()}</div>' + choices(['45', '55', '65', '75', '85'], 5) + '</div>'
Q[6] = (q(6, f'그림과 같이 원 O의 중심으로부터 두 현 AD와 BC에 이르는 거리가 서로 같고 {ANG}AOD = 90{DEG}, {ov("BC")} = 4㎝일 때, 원 O의 둘레의 길이는?', '4.3')
        + f'<div class="figc">{f6()}</div>'
        + choices([f'2{SQ2}π㎝', '4π㎝', f'4{SQ2}π㎝', '8π㎝', f'8{SQ2}π㎝'], 3) + '</div>')
Q[7] = (q(7, f'다음 그림에서 원 O가 □ABCD의 내접원일 때, {v("x")}의 값은?', '4.3') + f'<div class="figc">{f7()}</div>'
        + choices(['8', '9', '10', '11', '12'], 5) + '</div>')
Q[8] = (q(8, f'다음 그림에서 {ov("AB")}는 원 O의 지름이고 {ANG}ACD = 60{DEG} 일 때, {v("x")}의 값은?', '4.3')
        + f'<div class="figc">{f8()}</div>' + choices(['10', '15', '20', '25', '30'], 5) + '</div>')
Q[9] = (q(9, f'다음 그림에서 직선 AT가 원 O의 접선일 때, {ANG}ACB의 크기는?', '4.3') + f'<div class="figc">{f9()}</div>'
        + choices([f'20{DEG}', f'40{DEG}', f'60{DEG}', f'80{DEG}', f'100{DEG}'], 5) + '</div>')
Q[10] = (q(10, f'그림과 같이 점 O를 중심으로 하는 두 원에서 작은 원의 접선과 큰 원의 교점을 P, Q라 하자. {ov("PQ")} = 10일 때, 색칠한 부분의 넓이는?', '4.5')
         + f'<div class="figc">{f10()}</div>' + choices(['25π', '50π', '100π', '200π', '400π'], 3) + '</div>')
Q[11] = (q(11, '다음 그림에서 두 점 A, B는 원 O의 외부의 한 점 P에서 원 O에 그은 두 접선의 접점이라고 할 때, □APBO의 넓이는?', '4.5')
         + f'<div class="figc">{f11()}</div>' + choices(['24', '30', '48', '60', '80'], 5) + '</div>')
Q[12] = (q(12, f'그림과 같이 원 O는 {TRI}ABC의 내접원이면서 {TRI}DEF의 외접원이다. {ANG}BAC = 48{DEG}, {ANG}DFE = 50{DEG} 일 때, {ANG}{v("x")}의 크기는?', '4.5')
         + f'<div class="figc">{f12()}</div>' + choices([f'46{DEG}', f'48{DEG}', f'50{DEG}', f'52{DEG}', f'54{DEG}'], 5) + '</div>')
Q[13] = (q(13, '그림과 같이 원 O 위의 네 점 A, B, C, D에서 현 AB와 현 CD가 서로 평행할 때, 호 AC와 호 BD의 길이가 같음을 설명하는 데에 필요한 성질로 &lt;보기&gt;에서 적절한 것만을 있는 대로 고른 것은?', '4.5')
         + f'<div class="figc">{f13()}</div>'
         + bogi(['ㄱ. 두 직선이 평행하면 엇각의 크기는 서로 같다.', 'ㄴ. 현의 수직이등분선은 그 원의 중심을 지난다.',
                 'ㄷ. 한 원에서 같은 크기의 원주각에 대한 호의 길이는 서로 같다.'])
         + choices(['ㄱ', 'ㄴ', 'ㄱ, ㄷ', 'ㄴ, ㄷ', 'ㄱ, ㄴ, ㄷ'], 3) + '</div>')
DLG = [('유라', '① 원에 현 AB를 하나 그려서 그 현의 수직이등분선 ' + v('l') + '을 그려보면 좋겠어.'),
       ('승훈', '② ' + v('l') + '이 원의 중심을 지나기는 하지만, 아직 원의 중심은 하나로 결정되지 않는데?'),
       ('유라', '③ 원에 또 다른 현 CD를 하나 더 그려서 수직이등분선 ' + v('m') + '을 하나 더 그려보자.'),
       ('승훈', '④ 이때 현 CD의 길이는 현 AB의 길이와 같아야 해.')]
Q[14] = (q(14, '다음은 천장에 매달 모빌을 만들기 위해 구입한 플라스틱 원판의 중심을 찾기 위한 유라와 승훈이의 대화이다. 원의 중심을 찾는 방법으로 밑줄 친 ① ~ ⑤ 중 가장 적절하지 <u>않은</u> 것은?', '4.8')
         + '<div class="dlg">' + ''.join(f'<div class="dr"><span class="who">{w}:</span><span><u>{t}</u></span></div>' for w, t in DLG)
         + f'<div class="dr"><span class="who">유라:</span><span>그러면 <u>⑤ 두 수직이등분선 {v("l")}과 {v("m")}의 교점이 바로 원의 중심이야.</u></span></div></div></div>')
Q[15] = (q(15, '원 O에 내접하는 삼각형 ABC에서 세 현 AB, BC, CA의 중점을 각각 P, Q, R라 할 때, 삼각형 ABC가 이등변삼각형이 되기 위해 필요한 조건이 될 수 있는 것을 &lt;보기&gt;에서 있는 대로 고른 것은?', '4.8')
         + f'<div class="figc">{f15()}</div>'
         + bogi([f'ㄱ. {ov("OP")} = {ov("OQ")}', f'ㄴ. {ANG}OAB = 30{DEG}', f'ㄷ. {ANG}AOP = {ANG}AOR', 'ㄹ. 점 P가 반직선 CO 위의 점이다.'])
         + choices(['ㄱ, ㄷ', 'ㄱ, ㄹ', 'ㄱ, ㄷ, ㄹ', 'ㄴ, ㄷ, ㄹ', 'ㄱ, ㄴ, ㄷ, ㄹ'], 3) + '</div>')
U = '<span class="ul">{}</span>'
Q[16] = (q(16, '다음은 원 O의 외부에 있는 한 점 P에서 원 O에 그은 두 접선의 길이에 대한 설명이다. (ㄱ) ~ (ㅁ)에 들어갈 말로 알맞지 <u>않은</u> 것은?', '4.8')
         + f'<div class="figc">{f16()}</div>'
         + '<div class="box pf">'
         + f'<div>그림의 {TRI}PAO, {TRI}PBO에서</div>'
         + f'<div>{U.format("(ㄱ)")} ⋯ (가)</div><div>{U.format("(ㄴ)")}(반지름) ⋯ (나)</div>'
         + f'<div>{U.format("(ㄷ)")}는 공통인 변 ⋯ (다)</div><div>(가) ~ (다)에서 삼각형의 합동 조건에 의하여</div>'
         + f'<div>{U.format("(ㄹ)")}이다. 따라서 {U.format("(ㅁ)")} 이다.</div></div>'
         + choices([f'(ㄱ): {ANG}AOP = {ANG}BOP', f'(ㄴ): {ov("OA")} = {ov("OB")}', f'(ㄷ): {ov("OP")}',
                    f'(ㄹ): {TRI}PAO ≡ {TRI}PBO', f'(ㅁ): {ov("PA")} = {ov("PB")}'], 2) + '</div>')
F17, _ = f17()
Q[17] = (q(17, f'그림과 같이 원에 내접하는 사각형 ABCD의 두 변 BA, CD의 연장선의 교점을 P, 두 변 AD, BC의 연장선의 교점을 Q라 하자. {ANG}BPC = 40{DEG}, {ANG}AQB = 36{DEG} 일 때, {ANG}{v("x")}의 크기는?', '4.8')
         + f'<div class="figc">{F17}</div>' + choices([f'50{DEG}', f'52{DEG}', f'54{DEG}', f'56{DEG}', f'58{DEG}'], 5) + '</div>')
Q[18] = (q(18, f'그림과 같이 {ov("AB")} = 5, {ov("BC")} = 12인 직사각형 ABCD를 꼭짓점 B가 점 E에 오도록 {ov("AC")}를 접는 선으로 하여 접었다. 원 O가 {TRI}CDF의 내접원이고 세 점 G, H, I는 접점일 때, 원 O의 반지름의 길이 {frac(v("q"), v("p"))}에 대하여 {v("p")} + {v("q")}의 값은? (단, {v("p")}, {v("q")}는 서로소이다.)', '5.0')
         + f'<div class="figc">{f18()}</div>' + choices(['55', '56', '57', '58', '59'], 5) + '</div>')
F19, _ = f19()
Q[19] = (q(19, f'그림과 같이 길이가 2{v("r")}인 선분 AB를 지름으로 하는 반원에 대하여 호 AB 위의 두 점 C, D가 {ov("BC")} = {ov("CD")} = {v("r")} − 2, {ov("AD")} = 8을 만족하면, {v("r")} = {v("p")} + {sq(v("q"))}이다. 이때 두 자연수 {v("p")}, {v("q")}에 대하여 {v("p")} + {v("q")}의 값은? (단, {v("r")} &gt; 4인 상수)', '5.0')
         + f'<div class="figc">{F19}</div>' + choices(['6', '7', '8', '9', '10'], 5) + '</div>')
F20, _ = f20()
Q[20] = (q(20, f'그림과 같이 길이가 8인 선분 AB를 지름으로 하는 반원이 있다. 반지름 {ov("OA")}의 중점 M에 대하여 반원 위의 두 점 P, Q가 {ANG}AMP = {ANG}OMQ = 60{DEG}를 만족할 때, {ov("PQ")}의 길이는?', '5.0')
         + f'<div class="figc">{F20}</div>'
         + choices(['2', f'2{SQ2}', f'2{sq("3")}', '4', f'2{sq("5")}'], 5) + '</div>')
F21, _ = f21()
ARC = '<span class="arcx">{}</span>'
Q[21] = (q(21, f'그림과 같이 직선 AT는 반지름의 길이가 3인 원 O의 접선이고, {ov("AT")} = 6이다. 원 O 위의 점 P에 대하여 {ANG}PAT의 이등분선이 원 O와 만나는 점 중에서 A가 아닌 점을 B라 할 때, &lt;보기&gt;에서 옳은 것만을 있는 대로 고른 것은?', '5.3')
         + f'<div class="figc">{F21}</div>'
         + bogi([f'ㄱ. {ANG}PAT = 45{DEG} 이면 {ARC.format("BP")} = {frac(3, 4)}π이다.',
                 f'ㄴ. {ANG}PAT = 90{DEG} 이면 직선 AB와 BT는 직교한다.',
                 f'ㄷ. {ANG}PAT = 120{DEG} 이면 직선 AP와 BT는 평행이다.'])
         + choices(['ㄱ', 'ㄱ, ㄴ', 'ㄱ, ㄷ', 'ㄴ, ㄷ', 'ㄱ, ㄴ, ㄷ'], 3) + '</div>')
Q[22] = (q(22, '원의 둘레를 십이등분하는 12개의 점 중에서 서로 다른 네 점을 택하여 이를 꼭짓점으로 하는 사각형을 만들 때, 사각형의 두 대각선이 서로 수직이 되는 서로 다른 사각형의 개수는? (단, 합동인 사각형은 서로 같은 것으로 본다.)', '5.3')
         + f'<div class="figc">{f22()}</div>' + choices(['6개', '9개', '12개', '15개', '18개'], 5) + '</div>')

# ================================================================= 페이지
HEAD1 = '''<table class="hd"><tr>
<td class="h1">2026학년도 2학기 2차 정기시험</td><td class="h2">잠실여자중학교</td>
<td rowspan="2" class="h3">선택형</td><td rowspan="2" class="h3">22문항</td><td rowspan="2" class="h3">100점</td>
<td class="pg">page</td></tr>
<tr><td class="h1">11월 4일 수요일 1교시</td><td class="h2">3학년 수학과</td><td class="pg">1/5</td></tr></table>'''


def head(n):
    return (f'<table class="hd"><tr><td class="h1">2026학년도 2학기 2차 정기시험</td>'
            f'<td class="h2">11월 4일 수요일 1교시</td><td class="h2">3학년 수학과</td>'
            f'<td class="pg">page</td><td class="pg">{n}/5</td></tr></table>')


NOTICE = '<div class="notice">※ 선택형 22문항입니다. 각 문항별 배점이 다르니 물음의 끝에 표시된 배점을 참고하시오.</div>'
FOOT = '이 시험문제의 저작권은 잠실여자중학교에 있습니다. 무단 전송·복제·배포 시 저작권법에 의거 처벌 될 수 있습니다.'


def page(n, left, right, cont=None, end=None):
    hd = HEAD1 if n == 1 else head(n)
    c = f'<div class="cont">{cont}</div>' if cont else ''
    e = f'<div class="end">{end}</div>' if end else ''
    L = ''.join(qa(t, b) for t, b in left)
    R = ''.join(qa(t, b) for t, b in right)
    return (f'<section class="page"><div class="frame">{hd}<div class="cols">'
            f'<div class="col left">{L}</div><div class="col right">{R}{c}{e}</div>'
            f'</div></div><div class="foot">{FOOT}</div></section>')


PAGES = [
    page(1, [(0, NOTICE), (11, Q[1]), (86, Q[2]), (178, Q[3])], [(0, Q[4]), (68, Q[5]), (150, Q[6])], '다음 면에 계속'),
    page(2, [(2, Q[7]), (80, Q[8]), (168, Q[9])], [(0, Q[10]), (108, Q[11])], '다음 장에 계속'),
    page(3, [(2, Q[12]), (102, Q[13])], [(2, Q[14]), (106, Q[15])], '다음 면에 계속'),
    page(4, [(2, Q[16]), (138, Q[17])], [(0, Q[18]), (124, Q[19])], '다음 장에 계속'),
    page(5, [(0, Q[20]), (96, Q[21])], [(0, Q[22])], end='수 고 하 셨 습 니 다 ♥'),
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
.bg * { text-indent: 0; }
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
.col { position: relative; }
.qa { position: absolute; left: 4.5mm; right: 4.5mm; }
.q { margin-bottom: 0; }
.dlg { border: 1px solid #000; padding: 2mm 3mm; margin-top: 3mm; }
.dr { display: flex; line-height: 1.75; margin-bottom: 1.2mm; word-break: keep-all; }
.who { flex: none; width: 3em; }
.dr u { text-underline-offset: 3px; }
.box.pf div { line-height: 1.9; }
.ul { display: inline-block; min-width: 25mm; border-bottom: 1px solid #000; text-align: center; font-size: 9pt; line-height: 1.2; }
.arcx { display: inline-block; line-height: 1.0; padding-top: 0.42em; background-repeat: no-repeat;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 20' preserveAspectRatio='none'%3E%3Cpath d='M2 18 Q50 -6 98 18' fill='none' stroke='black' stroke-width='5'/%3E%3C/svg%3E");
  background-size: 100% 0.36em; background-position: 0 0.05em; font-family: "Liberation Serif", serif; font-style: italic; }
.end { position: absolute; right: 8mm; bottom: 12mm; font-weight: bold; font-size: 12pt; letter-spacing: 1px; }
'''

HTML = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>2026 2학기 2차 정기시험 3학년 수학</title>'
        f'<style>{CSS}</style></head><body>{"".join(PAGES)}</body></html>')

if __name__ == '__main__':
    html_path = os.path.join(HERE, 'exam8.html')
    pdf_path = os.path.join(HERE, '2026_2학기_2차_정기시험_3학년_수학_잠실여중.pdf')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(HTML)
    chrome = os.environ.get('CHROME', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    subprocess.run([chrome, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                    f'--print-to-pdf={pdf_path}', 'file://' + html_path], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(pdf_path)
