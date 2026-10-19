# -*- coding: utf-8 -*-
"""영동일고 2026학년도 2학기 중간고사 2학년 미적분Ⅰ 원본 시험지 복원.

원본 스캔(1415x2000px)의 줄 위치를 그대로 써서 배치하고, 수식은 KaTeX(katex/ 폴더,
오프라인)로 조판한 뒤 Chromium으로 A4 PDF를 만든다.
  python3 exam5/build_exam5.py
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
K = 297 / 2000  # 스캔 px → mm

# 단 위치(스캔 px)
LX, LX2, LR = 100, 142, 686     # 왼쪽 단: 번호, 본문, 오른쪽 끝
RX, RX2, RR = 716, 760, 1320    # 오른쪽 단
DIV = 705


def m(tex):
    tex = tex.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return f'${tex}$'


def L(y, x, html, right=None, cls=''):
    """스캔 좌표 (x, y=줄 가운데)에 한 줄을 놓는다. right가 있으면 양쪽 정렬."""
    w = f'width:{(right - x) * K:.2f}mm;' if right else ''
    c = 'ln' + (' jj' if right else '') + (' ' + cls if cls else '')
    return f'<div class="{c}" style="left:{x * K:.2f}mm;top:{y * K:.2f}mm;{w}">{html}</div>'


def RA(y, right, html):
    """오른쪽 끝 맞춤 한 줄"""
    return f'<div class="ln ra" style="right:{(1415 - right) * K:.2f}mm;top:{y * K:.2f}mm">{html}</div>'


def num(y, x, n):
    return L(y, x, f'{n}.', cls='qn')


def sd(n):
    return f'<b class="sd">서답형{n}.</b>'


def box(x0, y0, x1, y1):
    return (f'<div class="box" style="left:{x0 * K:.2f}mm;top:{y0 * K:.2f}mm;'
            f'width:{(x1 - x0) * K:.2f}mm;height:{(y1 - y0) * K:.2f}mm"></div>')


MARK = '①②③④⑤'


def ch(y, xs, items):
    return ''.join(L(y, x, f'{MARK[i]}&nbsp;{t}', cls='ch') for i, (x, t) in enumerate(zip(xs, items)))


def chs(rows):
    """[(y, [(번호, x, 내용), ...]), ...]"""
    out = ''
    for y, cells in rows:
        for k, x, t in cells:
            out += L(y, x, f'{MARK[k]}&nbsp;{t}', cls='ch')
    return out


def fr(a, b):
    return m(r'\dfrac{%s}{%s}' % (a, b))


def nfr(a, b):
    return m(r'-\dfrac{%s}{%s}' % (a, b))


LIM = r'\lim\limits'
XL5 = (135, 245, 357, 470, 577)
XR5 = (760, 870, 985, 1100, 1210)


# ------------------------------------------------------------------ 그림
def fig_q1():
    t = lambda x, y, s, it=True, sz=15: (f'<text x="{x}" y="{y}" font-size="{sz}" text-anchor="middle" '
                                         f'dominant-baseline="central"{" font-style=\"italic\"" if it else ""}>{s}</text>')
    ax = 'stroke="#555" stroke-width="0.9" stroke-dasharray="1.5,2"'
    gr = 'stroke="#222" stroke-width="1.5" fill="none"'
    s = ''
    # y = f(x)
    s += f'<line x1="172" y1="528" x2="352" y2="528" {ax}/><path d="M352,525 L358,528 L352,531" fill="#555"/>'
    s += f'<line x1="220" y1="570" x2="220" y2="392" {ax}/><path d="M217,394 L220,388 L223,394" fill="#555"/>'
    s += f'<line x1="172" y1="473" x2="274" y2="473" {gr}/>'
    s += f'<line x1="274" y1="476" x2="274" y2="524" stroke="#222" stroke-width="1.1" stroke-dasharray="3,2.5"/>'
    s += f'<line x1="276.5" y1="525.5" x2="358" y2="443" {gr}/>'
    s += '<circle cx="274" cy="473" r="3" fill="#333"/><circle cx="274" cy="528" r="3.3" fill="#fff" stroke="#222" stroke-width="1.1"/>'
    s += t(212, 392, 'y', sz=17) + t(211, 465, '1', False, 15) + t(228, 543, 'O', False, 15) + t(274, 544, '1', False, 15)
    s += t(352, 543, 'x', sz=16) + t(368, 427, 'y = f(x)', sz=18)
    # y = g(x)
    s += f'<line x1="415" y1="531" x2="602" y2="531" {ax}/><path d="M602,528 L608,531 L602,534" fill="#555"/>'
    s += f'<line x1="463" y1="572" x2="463" y2="385" {ax}/><path d="M460,387 L463,381 L466,387" fill="#555"/>'
    s += f'<line x1="463" y1="423" x2="612" y2="573" {gr}/>'
    s += f'<line x1="460.8" y1="533.1" x2="418" y2="572" {gr}/>'
    s += '<circle cx="463" cy="423" r="3" fill="#333"/><circle cx="463" cy="531" r="3.3" fill="#fff" stroke="#222" stroke-width="1.1"/>'
    s += t(455, 386, 'y', sz=17) + t(451, 423, '2', False, 15) + t(472, 544, 'O', False, 15) + t(566, 544, '2', False, 15)
    s += t(604, 543, 'x', sz=16) + t(558, 428, 'y = g(x)', sz=18)
    x0, y0, x1, y1 = 160, 375, 640, 585
    return (f'<svg class="fig" style="left:{x0 * K:.2f}mm;top:{y0 * K:.2f}mm;width:{(x1 - x0) * K:.2f}mm;'
            f'height:{(y1 - y0) * K:.2f}mm" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}">{s}</svg>')


# ------------------------------------------------------------------ 1쪽
def P1():
    s = ''
    s += num(297, LX, 1) + L(297, LX2, '두 함수 ' + m('y=f(x)') + ', ' + m('y=g(x)') + '의 그래프가 그림과 같을', LR)
    s += L(350, LX2, '때, ' + m(LIM + r'_{x\to1+}f(3x-2)+' + LIM + r'_{x\to2+}g(2-x)') + '의 값은? [3점]')
    s += fig_q1()
    s += ch(613, XL5, ['0', '1', '2', '3', '4'])
    s += num(760, LX, 2) + L(760, LX2, m(LIM + r'_{x\to\infty}\left(\sqrt{4x^2+x+2}-2x\right)') + '의 값은? [3점]')
    s += ch(835, XL5, [fr(1, 5), fr(1, 4), fr(1, 3), fr(1, 2), '1'])
    s += num(1097, LX, 3) + L(1097, LX2, '함수 ' + m(r'f(x)=\begin{cases}\dfrac{x^2+ax+b}{x-1} & (x\ne1)\\[2mm] \quad\ 4 & (x=1)\end{cases}')
                              + '이 실수 전체의')
    s += L(1195, LX2, '집합에서 연속일 때, ' + m('a^2+b^2') + '의 값은?')
    s += RA(1220, 680, '(단, ' + m('a') + ', ' + m('b') + '는 상수이다.) [3점]')
    s += ch(1262, (130, 240, 353, 465, 577), ['11', '12', '13', '14', '15'])
    s += num(1485, LX, 4) + L(1485, LX2, '함수 ' + m('f(x)=2x^3+ax^2+2') + '에 대하여 ' + m("f'(-1)=4") + '일', LR)
    s += L(1532, LX2, '때, 상수 ' + m('a') + '의 값은? [3점]')
    s += ch(1585, XL5, [fr(1, 2), '1', fr(3, 2), '2', fr(5, 2)])

    s += num(297, RX, 5) + L(297, RX2, '곡선 ' + m('y=x^3+4x-1') + '에 접하고 기울기가 7인 두', 1265)
    s += L(332, RX2, '직선의 ' + m('y') + '절편의 차는? [3.9점]')
    s += ch(382, XR5, ['1', '2', '3', '4', '5'])
    s += num(770, RX, 6) + L(770, RX2, '함수 ' + m('f(x)=(x^4+1)(ax-1)') + '에서 ' + m("f'(1)=8") + '일 때,', RR)
    s += L(825, RX2, '상수 ' + m('a') + '의 값은? [3.9점]')
    s += ch(865, XR5, [m('-4'), m('-2'), '0', '2', '4'])
    s += num(1262, RX, 7) + L(1262, RX2, '두 다항함수 ' + m('f(x)') + ', ' + m('g(x)') + '가')
    s += L(1320, 795, m(LIM + r'_{x\to2}\dfrac{f(x)+1}{x-2}=5') + ', ' + m(LIM + r'_{x\to2}\dfrac{x-2}{g(x)-1}=1'))
    s += L(1377, RX2, '을 만족시킨다. 함수 ' + m('h(x)=f(x)g(x)') + '에 대하여', 1258)
    s += L(1413, RX2, m("h'(2)") + '의 값은? [4점]')
    s += ch(1465, (760, 870, 985, 1095, 1210), ['4', fr(9, 2), '5', fr(11, 2), '6'])
    return s, '- 뒷면 계속'


# ------------------------------------------------------------------ 2쪽
def P2():
    s = ''
    s += num(292, LX, 8) + L(292, 150, '점 ' + m(r'(-2,\ 0)') + '에서 곡선 ' + m('y=2x^2+ax') + '에 그은 두 접선이', LR)
    s += L(325, 162, '곡선과 만나는 두 접점의 ' + m('x') + '좌표의 차가 3이 되도록', 670)
    s += L(353, 162, '하는 상수 ' + m('a') + '의 값은? (단, ' + m('a<4') + ') [4점]')
    s += ch(420, (132, 245, 357, 470, 580), [fr(5, 4), fr(3, 2), fr(7, 4), '2', fr(9, 4)])
    s += num(1020, LX, 9) + L(1020, 150, '최고차항의 계수가 양수인 다항함수 ' + m('f(x)') + '가 다음', 670)
    s += L(1067, 162, '조건을 만족시킬 때, ' + m('f(-2)') + '의 값은? [4점]')
    s += box(140, 1095, 690, 1250)
    s += L(1138, 150, '(가) ' + m(LIM + r'_{x\to\infty}\dfrac{x^4f(x)-f\left(x^2\right)}{\{f(x)\}^3}=\dfrac{1}{16}'))
    s += L(1212, 150, '(나) ' + m(LIM + r'_{x\to0}\dfrac{f(x)+5}{x}=4'))
    s += ch(1290, (145, 245, 370, 480, 600), ['1', fr(3, 2), '2', fr(5, 2), '3'])

    s += num(292, RX, 10) + L(292, 792, '일차함수 ' + m('f(x)') + '에 대하여 함수 '
                              + m(r'g(x)=\begin{cases}f(x) & (x<1)\\ \ \ x & (x\ge1)\end{cases}'))
    s += L(345, 792, '이 실수 전체의 집합에서 연속이다.')
    s += L(392, 815, m(LIM + r'_{h\to0}\dfrac{g(1+h)-g(1-h)}{h}=0'))
    s += L(465, 792, '일 때, ' + m(LIM + r'_{x\to0}\dfrac{g(x)-g(0)}{x^2+2x}') + '의 값은? [4점]')
    s += ch(530, (758, 870, 985, 1095, 1210), [m('-1'), nfr(1, 2), '0', fr(1, 2), '1'])
    s += num(1012, RX, 11) + L(1012, 792, '실수 전체의 집합에서 연속인 함수 ' + m('f(x)') + '가 다음')
    s += L(1082, 792, '조건을 만족시킬 때, ' + m(r'f\left(\dfrac{16}{3}\right)') + '의 값은?')
    s += RA(1122, 1328, '(단, ' + m('a') + ', ' + m('b') + '는 상수이다.) [4.1점]')
    s += box(765, 1147, 1328, 1330)
    s += L(1182, 775, '(가) 모든 실수 ' + m('x') + '에 대하여 ' + m('f(x+3)=f(x)+4') + '이다.')
    s += L(1207, 775, '(나) ' + m(r'0\le x\le3') + '일 때,')
    s += L(1250, 860, m(r'f(x)=\begin{cases}ax^2+x & (0\le x<2)\\ x+b & (2\le x\le3)\end{cases}'))
    s += L(1305, 830, '이다.')
    s += ch(1370, (778, 880, 992, 1110, 1235), ['6', fr(19, 3), fr(20, 3), '7', fr(22, 3)])
    return s, '- 다음 장 계속'


# ------------------------------------------------------------------ 3쪽
def P3():
    s = ''
    s += num(277, LX, 12) + L(277, 162, '양수 ' + m('k') + '에 대하여 두 함수')
    s += L(320, 198, m('f(x)=x^2-1') + ', ' + m('g(x)=kx+2'))
    s += L(358, 138, '가 다음 조건을 만족시킬 때, ' + m('g(1)') + '의 값은? [4.9점]')
    s += box(135, 407, 700, 535)
    s += L(450, 145, m(LIM + r'_{x\to a}\dfrac{f(x)+g(x)}{f(x)-g(x)}') + ' 의 값이 존재하지 <u>않도록</u> 하는')
    s += L(513, 145, '실수 ' + m('a') + '의 개수는 1이다.')
    s += ch(568, (135, 245, 357, 470, 585), ['4', '5', '6', '7', '8'])
    s += num(1032, LX, 13) + L(1032, 162, '함수 ' + m('f(x)=x^2+ax+b') + '가 다음 조건을 만족시킬', LR)
    s += L(1078, 162, '때, ' + m('f(3)') + '의 값은? (단, ' + m('a') + ', ' + m('b') + '는 정수이다.) [5점]')
    s += box(135, 1105, 695, 1278)
    s += L(1130, 145, '(가) ' + m('1<x<2') + '인 모든 실수 ' + m('x') + '에 대하여')
    s += L(1162, 210, m("4<f'(x)<6"))
    s += L(1190, 198, '이다.')
    s += L(1240, 145, '(나) ' + m(LIM + r'_{x\to1}\dfrac{xf(1)-f\left(x^2\right)}{x-1}=1'))
    s += ch(1312, (135, 245, 360, 473, 585), ['15', '17', '19', '21', '23'])

    s += num(277, RX, 14) + L(277, 792, '두 다항함수 ' + m('f(x)') + ', ' + m('g(x)') + '가 다음 조건을 만족시킨다.', RR)
    s += box(748, 325, 1320, 440)
    s += L(357, 758, '(가) ' + m('g(x)=(x^2-2)f(x)-3'))
    s += L(405, 758, '(나) ' + m(LIM + r'_{x\to2}\dfrac{xf(x)-2g(x)}{x-2}=9'))
    s += L(477, 758, '곡선 ' + m('y=f(x)') + ' 위의 점 ' + m(r'(2,\ f(2))') + '에서의 접선이 ' + m('y') + '축과', RR)
    s += L(507, 758, '만나는 점을 P라 하고, 곡선 ' + m('y=g(x)') + ' 위의 점')
    s += L(547, 758, m(r'(2,\ g(2))') + '에서의 접선이 ' + m('y') + '축과 만나는 점을 Q라 할', 1290)
    s += L(582, 758, '때, 선분 PQ의 길이는? [5점]')
    s += ch(635, (760, 875, 985, 1092, 1210), ['5', fr(11, 2), '6', fr(13, 2), '7'])
    s += num(1042, RX, 15) + L(1042, 792, '실수 ' + m('m') + '에 대하여 직선 ' + m('y=m(x+2)') + '가 함수')
    s += L(1105, 792, m(r'y=\begin{cases}\ \ x+4 & (x<-1)\\ x^2+5x+7 & (x\ge-1)\end{cases}'))
    s += L(1162, 758, '의 그래프와 만나는 점의 개수를 ' + m('f(m)') + '이라 하자.', 1258)
    s += L(1195, 758, '이차항의 계수가 1인 이차함수 ' + m('g(x)') + '에 대하여 함수', 1278)
    s += L(1232, 758, m('f(x)g(x)') + '가 실수 전체의 집합에서 연속일 때,')
    s += L(1268, 758, m('f(4)+g(4)') + '의 값은? [5점]')
    s += ch(1307, (760, 875, 990, 1102, 1215), ['1', '2', '3', '4', '5'])
    return s, '- 뒷면 계속'


# ------------------------------------------------------------------ 4쪽
def P4():
    s = ''
    s += num(277, LX, 16) + L(277, 162, '양수 ' + m('p') + '에 대하여 함수')
    s += L(345, 165, m(r'f(x)=\begin{cases}x^2+ax & (x\le p)\\ px+b & (x>p)\end{cases}'))
    s += L(405, 135, '는 실수 전체의 집합에서 미분가능하다. 함수 ' + m('f(x)') + '에', LR)
    s += L(442, 135, '대하여 닫힌구간 ' + m(r'[\,p-2,\ p+1\,]') + '에서 평균값 정리를', LR)
    s += L(483, 135, '만족시키는 ' + m('c') + '의 값이 ' + fr('p', 2) + '일 때, ' + m('a+b+p') + '의 값은?')
    s += RA(547, 690, '(단, ' + m('a') + ', ' + m('b') + '는 상수이다.) [5.1점]')
    s += chs([(590, [(0, 135, nfr(17, 9)), (1, 360, nfr(16, 9)), (2, 505, nfr(5, 3))]),
              (665, [(3, 135, nfr(14, 9)), (4, 360, nfr(13, 9))])])
    s += num(277, RX, 17) + L(277, 792, '함수 ' + m(r'f(x)=\begin{cases}x^2-1 & (x\le2)\\ ax+b & (x>2)\end{cases}') + '가 실수 전체의')
    s += L(350, 792, '집합에서 연속이고 ' + m('x=2') + '에서 미분가능하지 <u>않다.</u>')
    s += L(390, 792, '함수 ' + m('f(x)f(x+1)') + '이 실수 전체 집합에서')
    s += L(435, 792, '미분가능할 때, ' + m(r'\left|a\times b\right|') + '의 값은?')
    s += RA(472, 1318, '(단, ' + m('a') + ', ' + m('b') + '는 상수이다.)[5.1점]')
    s += ch(515, (760, 875, 990, 1102, 1215), ['27', '30', '33', '36', '39'])
    return s, '- 다음 장 계속'


# ------------------------------------------------------------------ 5쪽
def P5():
    s = ''
    s += L(310, LX, '※ 서답형 1번부터 서답형 4번까지는 답안지에 <u>답만</u> 쓰시오.')
    s += L(338, 122, '풀이 과정은 쓰지 않아도 됩니다.')
    s += L(390, LX, sd(1) + ' 실수 전체의 집합에서 연속인 함수 ' + m('f(x)') + '가 모든', LR)
    s += L(430, LX, '실수 ' + m('x') + '에 대하여')
    s += L(472, 130, m(r'4x^2f(x)=\left\{f(x)\right\}^3+2\left\{f(x)\right\}^2-8x^2'))
    s += L(515, LX, '을 만족시킨다. 함수 ' + m('f(x)') + '의 최댓값이 0이고 최솟값이 ' + m('-2') + '일', LR)
    s += L(560, LX, '때, ' + m(r'f\left(-\dfrac{1}{2}\right)+f\left(\dfrac{1}{4}\right)-f(2)') + '의 값을 구하시오. [3점]')
    s += L(1020, LX, sd(2) + ' 다음 조건을 만족시키는 모든 다항함수 ' + m('f(x)') + '에', 670)
    s += L(1060, LX, '대하여 ' + m('f(-2)') + '의 최댓값을 ' + m('M') + ', 최솟값을 ' + m('m') + '이라 할 때,', 670)
    s += L(1110, LX, fr('M', 'm') + ' 의 값을 구하시오. [4점]')
    s += box(95, 1152, 693, 1257)
    s += L(1187, 105, '(가) ' + m('f(3)=5'))
    s += L(1220, 105, '(나) 모든 실수 ' + m('x') + '에 대하여 ' + m(r"\left|\,f'(x)-2\,\right|\le3") + '이다.')

    s += L(277, 720, sd(3) + ' 다항함수 ' + m('f(x)') + '가 다음 조건을 만족시킬 때,', 1295)
    s += L(327, 720, m('f(2)') + '의 값을 구하시오. [4점]')
    s += box(720, 345, 1317, 583)
    s += L(383, 732, '(가) 모든 실수 ' + m('x') + '에 대하여 ' + m('f(-x)=f(x)') + '이다.')
    s += L(410, 732, '(나) 모든 실수 ' + m('x') + '에 대하여')
    s += L(450, 795, m(r"\left\{f'(x)\right\}^2=16x^2f(x)-48x^2"))
    s += L(482, 758, '이다.')
    s += L(530, 732, '(다) ' + m(LIM + r'_{x\to0}\dfrac{f(x)-4}{x^2}') + ' 의 값은 양의 상수이다.')
    s += L(1015, 720, sd(4) + ' 최고차항의 계수가 1인 삼차함수 ' + m('f(x)') + '가 다음', 1300)
    s += L(1055, 720, '조건을 만족시킬 때, ' + m('f(-2)') + '의 값을 구하시오. [5점]')
    s += box(718, 1095, 1320, 1245)
    s += L(1120, 730, '(가) ' + m(r'f(2)\ne0'))
    s += L(1147, 730, '(나) 모든 실수 ' + m('x') + '에 대하여 ' + m('f(-x)=-f(x)') + '이다.')
    s += L(1178, 730, '(다) 곡선 ' + m('y=f(x)') + ' 위의 점 ' + m(r'(2,\ f(2))') + '에서의 접선과')
    s += L(1208, 780, m('x') + '축, ' + m('y') + '축으로 둘러싸인 도형의 넓이는 16이다.')
    return s, '- 뒷면 계속'


# ------------------------------------------------------------------ 6쪽
def P6():
    s = ''
    s += L(278, LX, '※ 서답형 5번과 서답형 6번은 답안지에 <u>풀이 과정과 답</u>을 모두', LR, cls='tight')
    s += L(305, 122, '쓰시오. 답만 쓰면 0점 처리합니다.')
    s += L(357, LX, sd(5) + ' 다항식 ' + m('f(x)') + '를 ' + m('(x-2)^2') + '으로 나누었을 때의', 670)
    s += L(395, LX, '몫을 ' + m('Q(x)') + ', 나머지를 ' + m('R(x)') + '라 하자. ' + m('Q(2)=R(2)') + '이고,', LR)
    s += L(450, 128, m(LIM + r'_{x\to2}\dfrac{xf(x)-2x^3}{f(x)-R(x)}=k'))
    s += L(503, LX, '일 때, 상수 ' + m('k') + '의 값을 구하고, 그 과정을 서술하시오. [6점]')

    s += L(277, 720, sd(6) + ' 최고차항의 계수가 1인 이차함수 ' + m('f(x)') + '에 대하여', RR)
    s += L(310, 720, '함수 ' + m('g(x)') + '를')
    s += L(360, 748, m(r'g(x)=\begin{cases}f(x) & (f(x)<4x)\\ \ \ 4x & (f(x)\ge4x)\end{cases}'))
    s += L(417, 720, '라 하자. 실수 ' + m('t') + '에 대하여 함수 ' + m('y=g(x)') + '의 그래프와 직선', RR)
    s += L(445, 720, m('y=t') + '가 만나는 점의 개수를 ' + m('h(t)') + '라 하고, 집합 ' + m('A') + '를', 1300)
    s += L(477, 748, m(r'A=\left\{k\ \middle|\ g(k)\times g(-k)=0\right\}'))
    s += L(513, 720, '이라 할 때, 집합 ' + m('A') + '와 ' + m('h(t)') + '가 다음 조건을 만족시킨다.')
    s += box(717, 567, 1308, 750)
    s += L(607, 728, '(가) 집합 ' + m('A') + '의 원소의 개수는 3이다.')
    s += L(633, 728, '(나) 집합 ' + m('A') + '의 어떤 원소 ' + m('m') + '에 대하여,')
    s += L(672, 815, m(r'h(m)\times' + LIM + r'_{t\to m-}h(t)=h(0)\times' + LIM + r'_{t\to0+}h(t)'))
    s += L(710, 785, '를 만족시킨다.')
    s += L(782, 720, '실수 ' + m('m') + '의 값을 모두 구하고, 그 과정을 서술하시오. [8점]')
    return s, '- 끝'


# ------------------------------------------------------------------ 머리글·바닥글
def header(n):
    if n == 1:
        cols = [102, 377, 577, 817, 940, 1005, 1065, 1173, 1240, 1298]
        rows = [136, 172, 208, 245]
        w = [(cols[i + 1] - cols[i]) * K for i in range(len(cols) - 1)]
        h = [(rows[i + 1] - rows[i]) * K for i in range(3)]
        c = lambda i, t, rs=1, cls='': f'<td style="width:{w[i]:.2f}mm" rowspan="{rs}" class="{cls}">{t}</td>'
        body = (f'<tr style="height:{h[0]:.2f}mm">' + c(0, '2 학기 &nbsp; 중간 &nbsp; 고사') + c(1, '제 2 학년', 3)
                + c(2, '과 &nbsp; 목 &nbsp; 명') + c(3, '과목코드') + c(4, '교시') + c(5, '시간') + c(6, '문제유형')
                + c(7, '문항수') + c(8, '배점') + '</tr>'
                + f'<tr style="height:{h[1]:.2f}mm">' + c(0, '2026년 10월 14일 수요일') + c(2, '미적분 Ⅰ', 2, 'big')
                + c(3, '42', 2, 'code') + c(4, '1', 2) + c(5, '50분', 2) + c(6, '선택형') + c(7, '17') + c(8, '70') + '</tr>'
                + f'<tr style="height:{h[2]:.2f}mm">' + c(0, '영 &nbsp;동 &nbsp;일 &nbsp;고 &nbsp;등 &nbsp;학 &nbsp;교') + c(6, '서답형')
                + c(7, '6') + c(8, '30') + '</tr>')
        top = rows[0]
    else:
        cols = [102, 390, 610, 818, 938, 995, 1065, 1175, 1320]
        rows = [158, 190, 228]
        w = [(cols[i + 1] - cols[i]) * K for i in range(len(cols) - 1)]
        h = [(rows[i + 1] - rows[i]) * K for i in range(2)]
        c = lambda i, t, rs=1, cls='': f'<td style="width:{w[i]:.2f}mm" rowspan="{rs}" class="{cls}">{t}</td>'
        body = (f'<tr style="height:{h[0]:.2f}mm">' + c(0, '2 학기 &nbsp; 중간 고사') + c(1, '제 2 학년', 2)
                + c(2, '과 목 명') + c(3, '과목코드') + c(4, '교시') + c(5, '시간') + c(6, '쪽수', 2)
                + c(7, f'{n} / 6', 2, 'pg') + '</tr>'
                + f'<tr style="height:{h[1]:.2f}mm">' + c(0, '2026년 10월 14일 수요일') + c(2, '미적분 Ⅰ', 1, 'big')
                + c(3, '42', 1, 'code') + c(4, '1') + c(5, '50분') + '</tr>')
        top = rows[0]
    return (f'<table class="hd" style="left:{cols[0] * K:.2f}mm;top:{top * K:.2f}mm;width:{(cols[-1] - cols[0]) * K:.2f}mm">'
            f'{body}</table>'), rows[-1]


def page(n, body, cont):
    hd, hb = header(n)
    div = (f'<div class="div" style="left:{DIV * K:.2f}mm;top:{(hb + 8) * K:.2f}mm;'
           f'height:{(1882 - hb - 8) * K:.2f}mm"></div>')
    foot = (f'<div class="foot" style="top:{1917 * K:.2f}mm"><span class="pn">- {n} -</span>'
            '<img src="logo.png" class="logo"><span class="cp">본 시험문제의 저작권은 영동일고에 있습니다.</span></div>')
    return (f'<section class="page">{hd}{div}{body}{RA(1863, 1318, cont)}{foot}</section>')


CSS = r'''
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #fff; color: #000; }
body { font-family: "NanumMyeongjo", "Noto Serif CJK KR", serif; font-size: 9.9pt; }
.page { width: 210mm; height: 297mm; position: relative; page-break-after: always; overflow: hidden; }
.page:last-child { page-break-after: auto; }
.katex { font-size: 1.02em; }
.ln { position: absolute; white-space: nowrap; transform: translateY(-50%); line-height: 1.25; }
.tight { letter-spacing: -0.55px; word-spacing: -1px; }
.jj { text-align: justify; text-align-last: justify; }
.ra { text-align: right; }
.qn { font-family: "Liberation Serif", "Times New Roman", serif; font-size: 16.5pt; line-height: 1; transform: translateY(-58%); }
.sd { font-family: "NanumSquare", "NanumGothic", sans-serif; font-weight: 800; font-size: 12.2pt; letter-spacing: -0.3px; }
.ch .katex { font-size: 1.04em; }
.box { position: absolute; border: 1.2px solid #222; }
.div { position: absolute; border-left: 1.2px solid #222; }
.fig { position: absolute; overflow: visible; }
.fig text { font-family: "Liberation Serif", "Times New Roman", serif; fill: #222; }
table.hd { position: absolute; border-collapse: collapse; table-layout: fixed; border: 2px solid #111; text-align: center;
  font-family: "NanumGothic", sans-serif; font-weight: bold; font-size: 10pt; }
table.hd td { border: 1px solid #111; padding: 0; white-space: nowrap; line-height: 1; }
table.hd td.big { font-size: 15pt; letter-spacing: 0.5px; }
table.hd td.code { font-family: "Liberation Sans", sans-serif; font-weight: normal; font-size: 19pt; }
table.hd td.pg { font-size: 13pt; letter-spacing: 1px; }
.foot { position: absolute; right: 14.3mm; transform: translateY(-50%); display: flex; align-items: center;
  font-family: "NanumGothic", sans-serif; font-weight: bold; font-size: 11.6pt; letter-spacing: 0.6px; }
.foot .pn { font-weight: normal; font-size: 11pt; margin-right: 4.5mm; }
.foot .logo { width: 3.9mm; height: 4.2mm; margin-right: 2mm; }
'''

PAGES = [P1(), P2(), P3(), P4(), P5(), P6()]
HTML = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>2026 2학기 중간고사 2학년 미적분Ⅰ</title>'
        '<link rel="stylesheet" href="katex/katex.min.css">'
        f'<style>{CSS}</style></head><body>'
        + ''.join(page(i + 1, b, c) for i, (b, c) in enumerate(PAGES))
        + '<script src="katex/katex.min.js"></script><script src="katex/contrib/auto-render.min.js"></script>'
          '<script>renderMathInElement(document.body,{delimiters:[{left:"$",right:"$",display:false}],throwOnError:true});</script>'
          '</body></html>')

if __name__ == '__main__':
    html_path = os.path.join(HERE, 'exam5.html')
    pdf_path = os.path.join(HERE, '2026_2학기_중간고사_2학년_미적분I_영동일고.pdf')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(HTML)
    chrome = os.environ.get('CHROME', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    subprocess.run([chrome, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                    '--allow-file-access-from-files', '--virtual-time-budget=8000',
                    f'--print-to-pdf={pdf_path}', 'file://' + html_path], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(pdf_path)
