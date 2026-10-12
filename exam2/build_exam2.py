# -*- coding: utf-8 -*-
"""배명고 2026학년도 제2학기 (중간) 정기시험 2학년 미적분Ⅰ 원본 시험지 복원.

수식은 KaTeX(katex/ 폴더, 오프라인)로 렌더링하고 Chromium으로 PDF를 만든다.
  python3 exam2/build_exam2.py
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
PX = 297 / 2000  # 원본 스캔(2000px 높이) → mm


def mm(px):
    return f'{px * PX:.1f}mm'


def block(col, y, html, cls=''):
    """col: 'L' | 'R', y: 원본 스캔 기준 px 위치"""
    return f'<div class="blk {col} {cls}" style="top:{mm(y)}">{html}</div>'


def qhead(num, body):
    return f'<div class="qt"><b class="qn">{num}.</b><div class="qb">{body}</div></div>'


def choices(items, cols, cls=''):
    marks = '①②③④⑤'
    cells = ''.join(f'<div class="ch"><span class="cm">{marks[i]}</span>&nbsp;{t}</div>' for i, t in enumerate(items))
    return f'<div class="choices c{cols} {cls}">{cells}</div>'


def box(title, inner):
    return f'<div class="cbox"><div class="cbox-t"><span>&lt; {title} &gt;</span></div>{inner}</div>'


def m(tex):
    tex = tex.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return f'${tex}$'


L = r'\lim\limits'

# ---------------------------------------------------------------- 1쪽
P1 = []
P1.append('''<div class="hbox">
  <div class="h-title">2026학년도 &nbsp; 제 2학기 &nbsp; (중간) 정기시험</div>
  <div class="h-mid">
    <div class="h-grade"><span class="circ">2</span><span class="h-hak">학년</span></div>
    <div class="h-subj">미적분 <span class="bar">Ⅰ</span></div>
    <div class="h-code"><div class="h-code-l">코드<br>번호</div><div class="h-code-n">73</div></div>
  </div>
  <table class="h-tab"><tr>
    <td>실시일자</td><td>9월 &nbsp;30일 &nbsp;1교시</td><td>구분</td><td>일반</td><td>출제자</td>
    <td>구회진(인), 이수진(인), 문혜인(인)</td></tr></table>
</div>''')
P1.append(block('L', 515, '<div class="notice">※ 다음 물음에 대한 가장 옳은 답을 골라, <b class="sans">OMR</b> 카드 답안지에 정확히 표기하시오.</div>'))
P1.append(block('L', 615, qhead(1, '다음 중 옳지 <u>않은</u> 것은? [3.4점]') + choices([
    m(L + r'_{x\to\infty}\dfrac{5x}{2x^2+3x}=0'),
    m(L + r'_{x\to 3}\dfrac{x^2-9}{x-3}=6'),
    m(L + r'_{x\to\infty}\dfrac{8x^3+2x^2}{-2x^3-4}=-4'),
    m(L + r'_{x\to -\infty}\dfrac{2x+1}{4x+5}=-\dfrac{1}{2}'),
    m(L + r'_{x\to 1}\dfrac{x-1}{x^2-1}=\dfrac{1}{2}'),
], 2, 'tall')))
P1.append(block('L', 1090, qhead(2, '함수 ' + m(r'f(x)=\begin{cases} \ \ x^2-4 & (x\ge 1)\\ -2x+a & (x<1)\end{cases}')
                                 + '에서 <u>극한값 ' + m(L + r'_{x\to1}f(x)') + '</u>가 존재할 때, 실수 ' + m('a') + '의 값은? [3.4점]')
                + choices([m('-2'), m('-1'), m('0'), m('1'), m('2')], 5)))
P1.append(block('L', 1480, qhead(3, '다음 중 주어진 함수의 도함수 중 <u>옳지 않은</u> 것을 모두 고르면? (정답 2개) [3.4점]')
                + '<table class="deriv">' + ''.join(
                    f'<tr><td>{n}</td><td>{m(a)}</td><td>{m(r"\Longrightarrow")}</td><td>{m(b)}</td></tr>' for n, a, b in [
                        ('①', 'y=2x+1', "y'=2"),
                        ('②', 'y=-4x^2+2x+1', "y'=-8x+2"),
                        ('③', 'y=3x^3+3x^2+3x+3', "y'=27x^2+9x+3"),
                        ('④', 'y=4', "y'=4"),
                        ('⑤', 'y=(x-1)(x^2+x)', "y'=3x^2-1"),
                    ]) + '</table>'))
P1.append(block('R', 560, qhead(4, '다음 중 옳지 <u>않은</u> 것은? [3.4점]') + choices([
    '함수 ' + m(r'f(x)=\dfrac{2}{x+1}') + '은 ' + m('x=3') + '에서 연속이다.',
    '함수 ' + m(r'f(x)=\begin{cases} x+1 & (x\ne 3)\\ \ \ \ 4 & (x=3)\end{cases}') + ' 는 ' + m('x=3') + '에서 연속이다.',
    '함수 ' + m('f(x)=x^2+x') + ' 가 연속인 구간은 ' + m(r'(-\infty,\,\infty)') + '이다.',
    '함수 ' + m(r'f(x)=\sqrt{2x-4}') + ' 의 정의역을 구간의 기호로 나타내면 ' + m(r'(2,\,\infty)') + '이다.',
    '함수 ' + m(r'f(x)=\dfrac{1}{x^2+1}') + ' 의 정의역을 구간의 기호로 나타내면 ' + m(r'(-\infty,\,\infty)') + '이다.',
], 1, 'tall')))
P1.append(block('R', 1360, qhead(5, '곡선 ' + m('y=x^3-2x^2+3') + ' 위의 점 ' + m(r'(1,\,2)') + '에서의 접선의 방정식은? [3.4점]')
                + choices([m('y=-2x+1'), m('y=-x+3'), m('y=-x-3'), m('y=x+3'), m('y=x-3')], 3)))

# ---------------------------------------------------------------- 2쪽
P2 = []
P2.append(block('L', 175, qhead(6, '다음 &lt;보기&gt;에서 함수 ' + m(r'f(x)=\dfrac{|x^2-9|}{|x|-3}') + '에 대한 설명 중 옳은 것을 모두 고른 것은? [3.8점]')
                + box('보 &nbsp; 기', ''.join(f'<div class="bi"><span class="bl">{k}.</span>&nbsp;{v}</div>' for k, v in [
                    ('ㄱ', m(L + r'_{x\to3+}f(x)=' + L + r'_{x\to3+}\dfrac{x^2-9}{x-3}=' + L + r'_{x\to3+}(x+3)=6')),
                    ('ㄴ', m(L + r'_{x\to3-}f(x)=' + L + r'_{x\to3-}\dfrac{-x^2+9}{-x-3}=' + L + r'_{x\to3-}(x-3)=0')),
                    ('ㄷ', m(L + r'_{x\to3+}f(x)=' + L + r'_{x\to3-}f(x)=6')),
                    ('ㄹ', m(L + r'_{x\to3}f(x)') + '가 존재한다.'),
                ]), ) + choices(['ㄱ', 'ㄱ, ㄴ', 'ㄱ, ㄷ', 'ㄱ, ㄹ', 'ㄱ, ㄷ, ㄹ'], 3)))
P2.append(block('L', 1080, qhead(7, '함수 ' + m(r'f(x)=\begin{cases} x^2+1 & (|x|<1)\\ \ \ \ a & (|x|=1)\\ x+b & (|x|>1)\end{cases}')
                                 + ' 에 대하여 함수 ' + m('f(x)f(-x)') + '가 ' + m('x=-1') + '에서 연속일 때, ' + m('ab^2')
                                 + '의 값은? (단, ' + m('a') + ', ' + m('b') + '는 상수이고, ' + m('a>0') + ', ' + m('b>0') + '이다.) [4.4점]')
                + choices(['2', '4', '8', '10', '20'], 5)))
P2.append(block('R', 180, qhead(8, '실수 ' + m('k') + '에 대하여 두 함수 ' + m('y=x^2-3x+24') + ', ' + m('y=5x+k') + '의 그래프가 만나는 서로 다른 점의 개수를 '
                                 + m('f(k)') + '라 하자. 함수 ' + m('f(k)') + '가 닫힌구간 ' + m(r'[0,\,n]') + '에서 연속이 되도록 하는 자연수 '
                                 + m('n') + '의 최댓값은? [4.4점]')
                + choices(['5', '6', '7', '8', '9'], 5)))
P2.append(block('R', 840, qhead(9, '함수 ' + m('f(x)=-x^3+ax^2+3x-2') + '에 대하여<br>'
                                 + m(L + r'_{h\to0}\dfrac{f(1+h^2)-f(1-3h)}{h}=12') + '일 때, 상수 ' + m('a') + '의 값은? [3.8점]')
                + choices([m('-6'), m('-4'), m('-2'), m('0'), m('2')], 5)))
P2.append(block('R', 1425, qhead(10, '함수 ' + m('f(x)=x^3-ax^2+2ax-7') + '가 극값을 갖지 않도록 하는 모든 정수 ' + m('a') + '의 값의 합은? [3.8점]')
                + choices(['19', '21', '22', '23', '24'], 3)))

# ---------------------------------------------------------------- 3쪽
P3 = []
P3.append(block('L', 180, qhead(11, '함수 ' + m('f(x)=x^2') + '에 대하여 닫힌구간 ' + m(r'[n,\ n+1]') + '에서 평균값 정리를 만족시키는 상수 '
                                  + m('c') + '의 값을 ' + m('a_n') + '이라 할 때, ' + m(r'\displaystyle\sum_{k=1}^{100}a_k') + '의 값은? (단, '
                                  + m('n') + '은 자연수이다.) [4.4점]')
                + choices(['5000', '5050', '5100', '5150', '5200'], 3)))
P3.append(block('L', 835, qhead(12, '이차함수 ' + m('f(x)') + '에 대하여 ' + m(L + r'_{x\to1}\dfrac{f(x^2)}{x-1}=2') + '일 때,<br>'
                                  + '<span class="ind">' + m(L + r'_{x\to-1}\dfrac{f(x)+xf(-1)}{x+1}') + '의 값은? [4.4점]</span>')
                + choices([m('-1'), m('0'), m('1'), m('2'), m('4')], 5)))
P3.append(block('L', 1405, qhead(13, '다항식 ' + m('f(x)') + '가 모든 실수 ' + m('x') + '에 대하여 ' + m("f(x)=g'(x)") + '이고 '
                                  + m(r"\{f(x)+g(x)\}'=8x^3+12x^2-18x+5") + '을 만족할 때, ' + m('f(x)') + '를 구하면? [4.4점]')
                + choices([m('f(x)=8x^3-12x^2+6x-1'), m('f(x)=8x^3-12x^2-6x+1'), m('f(x)=8x^3+12x^2+6x-1'),
                           m('f(x)=8x^3+12x^2-6x+1'), m('f(x)=8x^3+12x^2+6x+1')], 1, 'ind1')))
P3.append(block('R', 180, qhead(14, '삼차함수 ' + m('f(x)') + ' 가 다음 조건을 만족시킬 때,<br>' + m('f(2)-f(-2)') + '의 값은? [4.4점]')
                + box('조 &nbsp; 건', '<div class="ci">(가) 함수 ' + m('f(x)') + '는 ' + m('x=-3') + ' 에서 극값을 갖는다.</div>'
                      + '<div class="ci">(나) 모든 실수 ' + m('x') + '에 대하여 ' + m("f'(x)-f'(-x)=0") + ' 이고,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + m("f'(0)>0") + ' 이다.</div>'
                      + '<div class="ci">(다) 함수 ' + m('f(x)') + ' 의 극댓값과 극솟값의 차는 18 이다.</div>')
                + choices([m(r'\dfrac{43}{3}'), m(r'\dfrac{44}{3}'), m(r'\dfrac{46}{3}'), m(r'\dfrac{47}{3}'), m(r'\dfrac{49}{3}')], 3, 'tall')))
P3.append(block('R', 975, qhead(15, '실수 전체의 집합에서 연속인 함수 ' + m('f(x)') + '가 다음 조건을 만족시킨다.')
                + box('조 &nbsp; 건', '<div class="ci">(가) 모든 실수 ' + m('x') + '에 대하여 ' + m(r'f(x+2)=\dfrac{1}{2}f(x)') + '이다.</div>'
                      + '<div class="ci">(나) ' + m(r'0\le x\le 2') + '일 때,<br>'
                      + '<span class="pw">' + m(r'f(x)=\begin{cases} -2x+a & (0\le x\le 1)\\ \ \ \ x+b & (1<x\le 2)\end{cases}') + '</span><br>'
                      + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;이다. (단, ' + m('a') + ', ' + m('b') + '는 상수이다.)</div>')
                + '<div class="qb2">자연수 ' + m('n') + '에 대하여 방정식 ' + m(r'f(x)=\dfrac{1}{n}x') + '를 만족시키는 실수 ' + m('x') + '의 개수를 '
                + m('a_n') + '이라 할 때, ' + m(r'\displaystyle\sum_{k=1}^{15}a_k') + '의 값은? [5.1점]</div>'
                + choices(['53', '54', '55', '56', '57'], 3)))

# ---------------------------------------------------------------- 4쪽
P4 = []
P4.append(block('L', 180, qhead(16, '최고차항의 계수가 1 인 이차함수 ' + m('f(x)') + '가 있다. 실수 ' + m('t') + '에 대하여 함수 ' + m('f(|x|+t)')
                                  + ' 가 ' + m('x=a') + ' 에서 극값을 갖는 모든 실수 ' + m('a') + ' 의 개수를 ' + m('g(t)') + ' 라 할 때,<br>'
                                  + m(L + r'_{t\to1-}g(t)\ne' + L + r'_{t\to1+}g(t)') + ' 이다. &nbsp;함수 &nbsp;' + m('h(x)=(x-3)f(x)')
                                  + ' 가 다음 조건을 만족시킬 때, ' + m("h'(5)") + ' 의 값은? [5.1점]')
                + box('조 &nbsp; 건', '<div class="ci">(가) 방정식 ' + m('h(x)=0') + '의 모든 근은 정수이다.</div>'
                      + '<div class="ci">(나) ' + m(r"h'(1)\times h'(3)<0") + '</div>')
                + choices(['27', '28', '29', '30', '31'], 3)))
P4.append(block('L', 1080, '<div class="sd">【서답형 1.】</div><div class="sp">다음 함수의 극한값을 구하시오. [6점]</div>'
                + '<div class="sub">(1) ' + m(L + r'_{x\to\infty}\dfrac{6x^2-4x+1}{-3x^2+4x}') + '</div>'
                + '<div class="sub2">(<u>풀이과정과 답을 쓰시오.</u>) [3점]</div>'))
P4.append(block('L', 1430, '<div class="sub">(2) ' + m(L + r'_{x\to4}\dfrac{\sqrt{x}-2}{x-4}') + '</div>'
                + '<div class="sub2">(<u>풀이과정과 답을 쓰시오.</u>) [3점]</div>'))
P4.append(block('R', 180, '<div class="sd">【서답형 2.】</div><div class="sp">다항식 ' + m('f(x)') + '를 ' + m('(x-2)^2') + '로 나누었을때의 몫을 '
                + m('Q(x)') + ', 나머지를 ' + m('R(x)') + '라 하면 ' + m('Q(2)=R(-2)') + '이다.</div>'
                + '<div class="sp0">' + m(L + r'_{x\to2}\dfrac{f(x)+x^2-2x+2}{f(x)-R(x)}') + '의 값이 ' + m('k') + '로 존재할 때, '
                + m('k') + '의 값을 구하시오. <u>(풀이과정과 답을 쓰시오.)</u> [7점]</div>'))
P4.append(block('R', 1010, '<div class="sd">【서답형 3.】</div><div class="sp">함수 ' + m('f(x)=x^3+ax^2-24x+12') + '가 &nbsp;' + m('x=-4')
                + '에서 극댓값을 가질 때, 극댓값과 극솟값을 다음의 순서대로 구하시오.</div><div class="pts">[7점]</div>'
                + '<div class="sub">(1) ' + m('a') + '의 값을 구하시오. [3점] <u>(풀이과정과 답을 쓰시오.)</u></div>'))
P4.append(block('R', 1405, '<div class="sub">(2) 아래의 증감표를 완성하시오. [2.4점]</div>'
                + '<table class="inc"><tr><td>' + m('x') + '</td><td>' + m(r'\cdots') + '</td><td></td><td>' + m(r'\cdots')
                + '</td><td></td><td>' + m(r'\cdots') + '</td></tr>'
                + "<tr><td>" + m("f'(x)") + '</td><td></td><td></td><td></td><td></td><td></td></tr>'
                + '<tr><td>' + m('f(x)') + '</td><td></td><td></td><td></td><td></td><td></td></tr></table>'))
P4.append(block('R', 1675, '<div class="sub">(3) 극댓값과 극솟값을 구하시오. [1.6점]</div>'
                + '<div class="ans">극댓값: ( &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; ), &nbsp; 극솟값: ( &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; )</div>'))

# ---------------------------------------------------------------- 5쪽
P5 = []
P5.append(block('L', 170, '<div class="sd">【서답형 4.】</div><div class="sp">다항함수 ' + m('f(x)') + '에 대하여 함수 ' + m('f(x)=(x^2+3x-1)g(x)')
                + '이고, ' + m(L + r'_{x\to1}\dfrac{f(x)-1}{3g(x)-1}=11') + '일 때, ' + m("f'(1)") + '의 값을 구하시오.</div>'
                + '<div class="sp0"><u>(풀이과정과 답을 쓰시오.)</u> [7점]</div>'))
P5.append(block('R', 170, '<div class="sd">【서답형 5.】</div><div class="sp">최고차항의 계수가 1인 삼차함수 ' + m('f(x)') + '에 대하여 함수 '
                + m('y=f(x)') + '의 그래프를 ' + m('x') + '축의 방향으로 3만큼 ' + m('y') + '축의 방향으로 1만큼 평행이동한 그래프를 나타내는 함수를 '
                + m('y=g(x)') + '라 하자.</div>'
                + '<div class="sp0">' + m(L + r'_{x\to1}\dfrac{f(x)}{(x-1)\{g(x)-1\}}=\dfrac{1}{2}') + ', '
                + m(L + r'_{x\to4}\dfrac{f(x)}{(x-1)\{g(x)-1\}}=k') + ' 일 때, 상수 ' + m('k') + '의 값을 구하시오. (풀이과정과 답을 쓰시오.) [8점]</div>'))
P5.append(block('R', 1570, '<div class="chk"><div>※ 확인 사항</div>'
                + '<div class="ck">◦답안지의 해당란에 필요한 내용을 정확히 기입(표기)했는지 확인하시오.</div>'
                + '<div class="ck">◦서답형 답안지 작성은 반드시 검정 또는 청색의 지워지지 않는 볼펜을 사용하여 작성하며, 그 외의 연필(샤프 등) 등 지워지는 펜을 사용하여 작성한 해당 문항은 채점하지 않고, 0점으로 처리하니 주의하시오.</div></div>'))


# ---------------------------------------------------------------- 페이지 틀
def footer(n):
    return f'''<div class="foot">
  <div class="f-school"><div class="f-name">배 &nbsp;명 &nbsp;고 &nbsp;등 &nbsp;학 &nbsp;교</div><div class="f-url">https://bm.sen.hs.kr</div></div>
  <div class="f-pg"><svg width="44" height="22" viewBox="0 0 44 22"><rect x="0.5" y="0.5" width="43" height="21" fill="none" stroke="#000"/>
    <line x1="0.5" y1="21.5" x2="43.5" y2="0.5" stroke="#000"/><text x="6" y="10" font-size="10">{n}</text><text x="31" y="19" font-size="10">5</text></svg></div>
  <div class="f-copy">※ 본 시험문제의 저작권은 배명고등학교에 있습니다. 무단 전송·복제·배포 시 저작권법에 의거하여 처벌될 수 있습니다.</div>
</div>'''


def page(n, blocks):
    if n == 1:
        head = '<div class="pno1">1</div>'
        divider_top = mm(515)
    else:
        head = f'<div class="phead"><div class="ptitle">미 &nbsp;적 &nbsp;분 &nbsp;<span class="bar">Ⅰ</span></div><div class="pno">{n}</div></div>'
        divider_top = mm(160)
    return (f'<section class="page">{head}<div class="divider" style="top:{divider_top}"></div>'
            f'{"".join(blocks)}{footer(n)}</section>')


CSS = r'''
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #fff; color: #000; }
body { font-family: "NanumMyeongjo", "Noto Serif CJK KR", serif; font-size: 10.4pt; line-height: 1.75; }
.katex { font-size: 1.04em; display: inline-block; white-space: nowrap; text-indent: 0; margin: 0.4mm 0; }
.page { width: 210mm; height: 297mm; position: relative; page-break-after: always; overflow: hidden; }
.page:last-child { page-break-after: auto; }
.bar { font-family: "Liberation Sans", sans-serif; font-weight: 300; }
.sans { font-family: "NanumGothic", "Noto Sans CJK KR", sans-serif; }
/* 머리글 */
.pno1 { position: absolute; top: 9mm; right: 21mm; font-size: 13pt; font-family: "Liberation Sans", sans-serif; }
.phead { position: absolute; top: 11mm; left: 14mm; right: 14mm; height: 11mm; border-bottom: 1px solid #555; }
.ptitle { text-align: center; font-size: 17pt; letter-spacing: 1mm; line-height: 11mm; }
.pno { position: absolute; right: 2mm; top: 0; font-size: 19pt; line-height: 11mm; font-family: "Liberation Sans", sans-serif; }
.hbox { position: absolute; top: 23mm; left: 15.5mm; right: 13mm; height: 50.5mm; border: 2px solid #000; }
.h-title { text-align: center; font-size: 18pt; font-weight: bold; margin-top: 3mm; letter-spacing: 0.3mm; font-family: "NanumGothic", "Noto Sans CJK KR", sans-serif; }
.h-mid { position: relative; height: 22mm; }
.h-grade { position: absolute; left: 3mm; top: 1mm; display: flex; align-items: center; gap: 6mm; }
.circ { display: inline-block; width: 14mm; height: 14mm; border: 1.3px solid #000; border-radius: 50%; text-align: center; line-height: 14mm; font-size: 22pt; }
.h-hak { font-size: 22pt; }
.h-subj { position: absolute; left: 0; right: 0; text-align: center; top: -2mm; font-size: 40pt; letter-spacing: 1.5mm; }
.h-code { position: absolute; right: 4mm; top: 0; display: flex; align-items: center; gap: 3mm; }
.h-code-l { font-size: 13pt; line-height: 1.35; text-align: center; }
.h-code-n { width: 38mm; height: 17mm; border: 1.3px solid #000; border-radius: 50%; text-align: center; line-height: 17mm; font-size: 30pt; font-family: "Liberation Sans", sans-serif; }
.h-tab { position: absolute; left: 0; right: 0; bottom: 0; width: 100%; border-collapse: collapse; border-top: 2px solid #000; font-size: 14pt; height: 15mm; }
.h-tab td { border-left: 1px solid #000; text-align: center; white-space: nowrap; padding: 0 1.5mm; }
.h-tab td:first-child { border-left: none; }
/* 단 */
.divider { position: absolute; left: 106.5mm; bottom: 19.5mm; border-left: 1.3px solid #000; }
.blk { position: absolute; }
.blk.L { left: 15mm; width: 88.5mm; }
.blk.R { left: 109.5mm; width: 88.5mm; }
.notice { border: 1px solid #000; padding: 0.5mm 2mm 0.5mm 2mm; text-indent: -1.2em; padding-left: calc(2mm + 1.2em); font-size: 10.6pt; }
.qt { display: flex; align-items: baseline; }
.qn { font-weight: bold; min-width: 1.6em; font-family: "NanumGothic", "Noto Sans CJK KR", sans-serif; font-size: 11pt; }
.qb { flex: 1; text-align: left; word-break: keep-all; padding-left: 0.2em; }
.qb2 { margin: 2mm 0 0 1.8em; text-align: left; word-break: keep-all; }
.ind { display: inline-block; margin-left: 0.6em; margin-top: 1mm; }
.choices { display: grid; column-gap: 3mm; row-gap: 1mm; margin: 2.5mm 0 0 1.8em; align-items: center; }
.choices.c1 { grid-template-columns: 1fr; row-gap: 0.6mm; }
.choices.c2 { grid-template-columns: 1fr 1fr; column-gap: 5mm; }
.choices.c3 { grid-template-columns: 1fr 1fr 1fr; }
.choices.c5 { grid-template-columns: repeat(5, 1fr); }
.choices.tall { row-gap: 3mm; }
.choices.ind1 { margin-left: 2.2em; }
.ch { word-break: keep-all; padding-left: 1.3em; text-indent: -1.3em; }
.ch * { text-indent: 0; }
.cbox { border: 1px solid #000; margin: 6mm 0 2mm 0; padding: 4mm 2.5mm 2mm; position: relative; }
.cbox-t { position: absolute; top: -0.9em; left: 0; right: 0; text-align: center; line-height: 1.6; }
.cbox-t span { background: #fff; padding: 0 1.5mm; }
.ci { margin-bottom: 0.6mm; }
.pw { display: inline-block; margin-left: 9mm; }
.bi { margin: 1.5mm 0; }
.bl { display: inline-block; width: 1em; }
table.deriv { margin: 2mm 0 0 1.2em; border-collapse: collapse; }
table.deriv td { padding: 0 1mm; line-height: 1.6; white-space: nowrap; }
table.deriv td:nth-child(2) { width: 34mm; }
table.deriv td:nth-child(3) { width: 9mm; text-align: center; }
.sd { font-family: "NanumGothic", "Noto Sans CJK KR", sans-serif; font-weight: bold; font-size: 11.5pt; }
.sp { text-indent: 0.6em; text-align: left; word-break: keep-all; margin-top: 1mm; }
.sp0 { text-align: left; word-break: keep-all; margin-top: 1.5mm; }
.pts { text-align: right; }
.sub { margin-top: 1.2mm; }
.sub2 { }
table.inc { width: 100%; border-collapse: collapse; margin-top: 2mm; }
table.inc td { border: 1px solid #000; height: 8.3mm; text-align: center; width: 15%; }
table.inc td:first-child { width: 12%; }
.ans { margin: 6mm 0 0 8mm; }
.chk { border: 1px solid #000; padding: 1mm 2.5mm; font-size: 9.6pt; line-height: 1.6; text-align: justify; word-break: keep-all; }
.ck { padding-left: 1em; text-indent: -1em; }
/* 바닥글 */
.foot { position: absolute; left: 14mm; right: 12mm; bottom: 6mm; height: 13mm; }
.f-school { position: absolute; left: 3mm; top: 0; }
.f-name { font-family: "NanumGothic", sans-serif; font-weight: bold; font-size: 10.5pt; letter-spacing: 0.5mm; }
.f-url { font-family: "Liberation Sans", sans-serif; font-size: 7.5pt; margin-left: 9mm; line-height: 1.2; }
.f-pg { position: absolute; left: 50%; transform: translateX(-50%); top: 1mm; }
.f-pg text { font-family: "Liberation Sans", sans-serif; }
.f-copy { position: absolute; right: 2mm; top: 0; width: 49mm; border: 1px solid #000; font-size: 7pt; line-height: 1.45; padding: 1mm 1.5mm; font-family: "NanumGothic", sans-serif; }
'''

PAGES = [page(1, P1), page(2, P2), page(3, P3), page(4, P4), page(5, P5)]

HTML = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>2026 2학기 중간 미적분Ⅰ</title>'
        '<link rel="stylesheet" href="katex/katex.min.css">'
        f'<style>{CSS}</style></head><body>{"".join(PAGES)}'
        '<script src="katex/katex.min.js"></script><script src="katex/contrib/auto-render.min.js"></script>'
        '<script>renderMathInElement(document.body,{delimiters:[{left:"$",right:"$",display:false}],throwOnError:true});</script>'
        '</body></html>')

if __name__ == '__main__':
    html_path = os.path.join(HERE, 'exam2.html')
    pdf_path = os.path.join(HERE, '2026_2학기_중간_2학년_미적분I.pdf')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(HTML)
    chrome = os.environ.get('CHROME', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    subprocess.run([chrome, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                    '--allow-file-access-from-files', '--virtual-time-budget=8000',
                    f'--print-to-pdf={pdf_path}', 'file://' + html_path], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(pdf_path)
