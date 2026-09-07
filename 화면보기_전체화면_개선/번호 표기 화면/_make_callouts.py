"""프로토타입에 번호 + 이름표 + 연결선을 얹어 기획서용 캡쳐를 만든다.

실행: python3 _make_callouts.py
     → callout.html 생성 후 헤드리스 크롬으로 프레임별 PNG 캡쳐

'아하오호 화면 보기'는 단계(개요·가이드·기록하기·돌아보기)와 탭(화면 보기·수업 정보)이
나뉘어 있어 한 화면에 모든 번호를 담을 수 없음 → 프레임을 나눠 캡쳐하고, 번호는
기존 기획서와 같이 화면별로 매김(같은 번호가 다른 화면에 다시 등장함).
번호 위치는 레이아웃에서 자동 계산하므로 프로토타입을 수정한 뒤 다시 실행하면 됨.
"""
import os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
VIEWER = os.path.join(HERE, '..', '시안_아하오호화면보기_전체화면.html')
W, H = 1280, 800

CHROME = next((p for p in [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    shutil.which('google-chrome') or '', shutil.which('chromium') or '',
] if p and os.path.exists(p)), None)

# ── 프레임 정의 ────────────────────────────────────────────────────────────
# setup : 프로토타입을 그 화면 상태로 만드는 JS
# co    : {번호: {sel 대상, at 기준점, dx/dy 배지 오프셋, label 이름표, tone 색}}
#         tone 없음=빨강(유지·변경), blue=핵심 변경, green=신규
FRAMES = [
    dict(
        name='개요',
        setup="setTab('view'); show(0); pickGo(1);",
        co={
            '공통 1':  {'sel': '#ovTitle', 'at': 'bottom', 'dx': 46, 'dy': 34, 'label': '챌린지명'},
            '공통 2':  {'sel': '.topbar .tb-btn:last-child', 'at': 'bottom', 'dy': 30, 'label': '모달 닫기'},
            '공통 3':  {'sel': '#tabInfo', 'at': 'bottom', 'dy': 32, 'label': '구분탭'},
            '공통 4':  {'sel': '#stepList', 'at': 'left', 'dx': -74, 'label': '진행 단계', 'tone': 'blue'},
            '공통 5':  {'sel': '.device', 'at': 'left', 'dx': -70, 'label': '앱 화면 카드', 'tone': 'blue'},
            '공통 7':  {'sel': '#hintView', 'at': 'top', 'dy': -26, 'label': '조작 안내', 'tone': 'green'},
            '1':      {'sel': '#s0Slides', 'at': 'right', 'dx': 76, 'dy': 130, 'label': '썸네일·Pick 이미지 영역'},
            '2-1':    {'sel': '#pickNext', 'at': 'right', 'dx': 60, 'label': '슬라이드 이동 화살표', 'tone': 'green'},
            '2-2':    {'sel': '#pickDots', 'at': 'left', 'dx': -64, 'label': '인디케이터', 'tone': 'green'},
            '2-3':    {'sel': '#s0 .pickTag', 'at': 'top', 'dy': -28, 'label': 'Pick 작성자', 'tone': 'green'},
            '3':      {'sel': '#s0Cat', 'at': 'right', 'dx': 66, 'label': '카테고리'},
            '4':      {'sel': '#s0Title', 'at': 'right', 'dx': 66, 'label': '챌린지 제목'},
            '6':      {'sel': '#s0Bubble', 'at': 'left', 'dx': -64, 'label': '소개 문구(아하 설명글)'},
            '7':      {'sel': '#s0 .char', 'at': 'right', 'dx': 60, 'label': '캐릭터'},
            '8':      {'sel': '#s0 .actions .btn.dark', 'at': 'bottom', 'dy': 34, 'label': '시작하기'},
            '9':      {'sel': '#s0 .actions .btn.ghost', 'at': 'bottom', 'dy': 34, 'label': '활동재료(앱 전용)'},
        },
    ),
    dict(
        name='가이드_자세히보기',
        setup="setTab('view'); show(1); gCur=1; renderGuide();",
        co={
            '1':      {'sel': '#gStep', 'at': 'left', 'dx': -66, 'label': '페이지네이션'},
            '2':      {'sel': '#gImgPane', 'at': 'center', 'label': '가이드 이미지/영상', 'tone': 'blue'},
            '4':      {'sel': '#gCap', 'at': 'left', 'dx': -60, 'label': '가이드 설명', 'tone': 'blue'},
            '8':      {'sel': '#guideCtrl', 'at': 'left', 'dx': -74, 'label': '페이지 이동(카드 밖)', 'tone': 'green'},
            '공통 6':  {'sel': '#gImgPane', 'at': 'topright', 'dx': -70, 'dy': 40, 'label': '확대(휠·핀치)', 'tone': 'green'},
            '공통 4':  {'sel': '#stepList', 'at': 'left', 'dx': -74, 'label': '진행 단계', 'tone': 'blue'},
        },
    ),
    dict(
        name='가이드_마무리',
        setup="setTab('view'); show(1); gCur=gSteps.length-1; renderGuide();",
        co={
            '1': {'sel': '#gStep', 'at': 'left', 'dx': -66, 'label': '페이지네이션'},
            '5': {'sel': '#gOutroText', 'at': 'left', 'dx': -58, 'label': '업로드 안내 문구'},
            '6': {'sel': '#s1 .ohho', 'at': 'right', 'dx': 60, 'label': '오호 캐릭터'},
            '7': {'sel': '#s1 .outro .btn.dark', 'at': 'top', 'dy': -30, 'label': '기록하기'},
        },
    ),
    dict(
        name='기록하기',
        setup="setTab('view'); show(2);",
        co={
            '1': {'sel': '#s2 .thumbImg', 'at': 'left', 'dx': -70, 'label': '첨부 이미지 예시'},
            '2': {'sel': '#s2 .ask', 'at': 'left', 'dx': -58, 'label': '작성 안내 문구'},
            '3': {'sel': '#s2 .ta', 'at': 'left', 'dx': -58, 'label': '텍스트 작성란 예시'},
            '4': {'sel': '#s2 .btn.dark', 'at': 'left', 'dx': -70, 'label': '기록하기'},
        },
    ),
    dict(
        name='프로젝트_돌아보기',
        setup="setTab('view'); show(3); pickOpt(document.querySelectorAll('#s3 .opt')[1]);",
        co={
            '1': {'sel': '#s3 .bubble', 'at': 'top', 'dy': -28, 'label': '느낀점 선택 안내'},
            '2': {'sel': '#s3 .opt.on', 'at': 'left', 'dx': -62, 'label': '돌아보기 데이터(선택 상태)'},
            '3': {'sel': '#s3 .foot .btn', 'at': 'top', 'dy': -30, 'label': '완료'},
        },
    ),
    dict(
        # 좌측 열이 268px로 좁아 배지가 겹치므로, 우측 본문을 visibility로만 감춰
        # (레이아웃·위치는 실제 그대로 유지) 배지가 오른쪽으로 나갈 공간을 확보
        name='수업정보_좌측고정영역',
        setup=("setTab('info');"
               "document.querySelector('.ciMain').style.visibility='hidden';"),
        co={
            '공통 3':  {'sel': '#tabInfo', 'at': 'right', 'dx': 70, 'label': '구분탭'},
            '1':      {'sel': '#ci-keyword h5', 'at': 'right', 'dx': 74, 'label': '활동 키워드'},
            '2':      {'sel': '#ci-comp h5',    'at': 'right', 'dx': 74, 'label': '성취 역량'},
            '3':      {'sel': '#ci-cat h5',     'at': 'right', 'dx': 74, 'label': '카테고리'},
            '4':      {'sel': '#ci-level .stars i:nth-child(3)', 'at': 'right', 'dx': 74, 'label': '난이도'},
            '5':      {'sel': '#ci-mat .ciMat', 'at': 'right', 'dx': 74, 'label': '준비물'},
            '공통 7':  {'sel': '#hintInfo', 'at': 'top', 'dy': -26, 'label': '조작 안내(ESC만)', 'tone': 'green'},
        },
    ),
    dict(
        name='수업정보_본문',
        setup=("setTab('info');"
               "document.querySelector('.ciMeta').style.visibility='hidden';"),
        co={
            '6': {'sel': '#ci-desc h5',      'at': 'left', 'dx': -74, 'label': '챌린지 설명'},
            '7': {'sel': '#ci-goal .ciGoal', 'at': 'left', 'dx': -74, 'label': '활동 목표'},
            '8': {'sel': '#ci-std .ciTbl',   'at': 'left', 'dx': -74, 'label': '교과 성취 기준', 'tone': 'blue'},
            '공통 8': {'sel': '.ciMain', 'at': 'topright', 'dx': -110, 'dy': 34,
                      'label': '좌측 고정 · 우측만 스크롤', 'tone': 'blue'},
        },
    ),
    dict(
        name='수업정보_참고자료_추천',
        setup=("setTab('info');"
               "document.querySelector('.ciMeta').style.visibility='hidden';"
               "const m=document.querySelector('.ciMain'), t=document.getElementById('ci-ref');"
               "m.scrollTop += t.getBoundingClientRect().top - m.getBoundingClientRect().top - 20;"),
        co={
            '9':  {'sel': '#ci-ref .ciFiles', 'at': 'left', 'dx': -74, 'label': '교육자 참고 자료(파일)'},
            '10': {'sel': '#ci-ref .ciLinks', 'at': 'left', 'dx': -74, 'label': '참고 자료(링크)'},
            '11': {'sel': '#ci-etc .ciText',  'at': 'left', 'dx': -74, 'label': '기타 참고 사항'},
            '12': {'sel': '.ciRecCard',       'at': 'left', 'dx': -74, 'label': '추천 챌린지', 'tone': 'blue'},
        },
    ),
]

# ── 오버레이 (배지 + 연결선) ──────────────────────────────────────────────
OVERLAY = r"""
<style>
  /* width/height를 명시하지 않으면 SVG가 기본 300×150으로만 그려져 선이 잘림 */
  #coSvg{position:fixed;left:0;top:0;width:100vw;height:100vh;z-index:899;pointer-events:none;overflow:visible}
  #coLayer{position:fixed;inset:0;z-index:900;pointer-events:none}
  .co{
    position:absolute;transform:translate(-50%,-50%);
    background:#E8380D;color:#fff;border-radius:999px;
    font-family:"IBM Plex Sans KR",-apple-system,"Apple SD Gothic Neo",sans-serif;
    font-size:11.5px;font-weight:500;line-height:1;
    padding:5px 9px 5px 6px;white-space:nowrap;
    box-shadow:0 2px 8px rgba(0,0,0,.5);
    display:flex;align-items:center;gap:5px;
  }
  .co b{background:rgba(255,255,255,.22);border-radius:999px;padding:2px 5px;font-weight:700;font-size:11px}
  .co.blue{background:#1668D9}
  .co.green{background:#137A46}
  .wrap{display:none}
  body{background:var(--stage)}
</style>
<script>
const CO = window.__CO__;

function anchorOf(r, at){
  switch (at){
    case 'left':     return [r.left, r.top + r.height/2];
    case 'right':    return [r.right, r.top + r.height/2];
    case 'top':      return [r.left + r.width/2, r.top];
    case 'bottom':   return [r.left + r.width/2, r.bottom];
    case 'topleft':  return [r.left, r.top];
    case 'topright': return [r.right, r.top];
    default:         return [r.left + r.width/2, r.top + r.height/2];
  }
}

function drawCallouts(){
  document.getElementById('coLayer')?.remove();
  document.getElementById('coSvg')?.remove();

  const svg = document.createElementNS('http://www.w3.org/2000/svg','svg');
  svg.id = 'coSvg';
  document.body.appendChild(svg);

  const layer = document.createElement('div');
  layer.id = 'coLayer';
  document.body.appendChild(layer);

  const PAD = 10;
  const items = [];

  /* 1단계 — 배지 생성 후 실제 폭을 재서 화면 안으로 밀어넣음 */
  for (const [num, cfg] of Object.entries(CO)){
    const el = document.querySelector(cfg.sel);
    if (!el) continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;

    const [ax, ay] = anchorOf(r, cfg.at);
    const b = document.createElement('div');
    b.className = 'co ' + (cfg.tone || '');
    b.innerHTML = `<b>${num}</b>${cfg.label}`;
    b.style.left = (ax + (cfg.dx || 0)) + 'px';
    b.style.top  = (ay + (cfg.dy || 0)) + 'px';
    layer.appendChild(b);
    items.push({b, ax, ay, cfg});
  }

  const GAP = 22;   // 배지 테두리와 대상 사이 최소 여백 → 연결선이 보이도록
  for (const it of items){
    const w = it.b.offsetWidth, h = it.b.offsetHeight;
    const ox = it.cfg.dx || 0, oy = it.cfg.dy || 0;
    let bx, by;
    if (ox === 0 && oy === 0){
      bx = it.ax; by = it.ay;                      // 대상 위에 겹치는 배지
    } else {
      /* 오프셋 방향으로, 배지가 대상을 덮지 않을 거리까지 밀어냄 */
      const len = Math.hypot(ox, oy);
      const ux = ox / len, uy = oy / len;
      const half = Math.min(
        Math.abs(ux) > 1e-6 ? (w / 2) / Math.abs(ux) : Infinity,
        Math.abs(uy) > 1e-6 ? (h / 2) / Math.abs(uy) : Infinity);
      const dist = Math.max(len, half + GAP);
      bx = it.ax + ux * dist;
      by = it.ay + uy * dist;
    }
    bx = Math.min(Math.max(bx, PAD + w/2), innerWidth  - PAD - w/2);
    by = Math.min(Math.max(by, PAD + h/2), innerHeight - PAD - h/2);
    it.b.style.left = bx + 'px';
    it.b.style.top  = by + 'px';
    it.bx = bx; it.by = by; it.w = w; it.h = h;
    it.hasOffset = !(ox === 0 && oy === 0);
  }

  /* 2단계 — 확정된 배지 위치에서 대상까지 연결선 */
  for (const it of items){
    const {ax, ay, bx, by, w, h, cfg} = it;
    if (!it.hasOffset) continue;
    const color = cfg.tone === 'blue' ? '#1668D9' : cfg.tone === 'green' ? '#137A46' : '#E8380D';
    const dx = ax - bx, dy = ay - by;
    const k = Math.min(1,
      Math.min((w/2 + 3) / Math.max(Math.abs(dx), 1e-6),
               (h/2 + 3) / Math.max(Math.abs(dy), 1e-6)));
    const sx = bx + dx * k, sy = by + dy * k;

    for (const [col, wid] of [['rgba(0,0,0,.55)', 4], [color, 2]]){
      const line = document.createElementNS('http://www.w3.org/2000/svg','line');
      line.setAttribute('x1', sx); line.setAttribute('y1', sy);
      line.setAttribute('x2', ax); line.setAttribute('y2', ay);
      line.setAttribute('stroke', col);
      line.setAttribute('stroke-width', String(wid));
      line.setAttribute('stroke-linecap', 'round');
      svg.appendChild(line);
    }
    const dot = document.createElementNS('http://www.w3.org/2000/svg','circle');
    dot.setAttribute('cx', ax); dot.setAttribute('cy', ay); dot.setAttribute('r', '4');
    dot.setAttribute('fill', color);
    dot.setAttribute('stroke', 'rgba(0,0,0,.55)');
    dot.setAttribute('stroke-width', '1.5');
    svg.appendChild(dot);
  }
}

(async function(){
  openViewer(document.querySelector('.thumb'));
  window.__SETUP__();
  try { await document.fonts.ready; } catch(e){}
  /* 폰트·이미지 로드로 위치가 밀리므로 여러 번 다시 그림 */
  for (const w of [300, 400, 500, 600]){
    await new Promise(r=>setTimeout(r, w));
    window.__SETUP__();
    drawCallouts();
  }
  addEventListener('resize', drawCallouts);
  document.title = 'ready';
})();
</script>
"""


def main():
    if CHROME is None:
        sys.exit('크롬을 찾을 수 없음 — CHROME 경로를 확인할 것')
    base = open(VIEWER, encoding='utf-8').read()
    import json
    for f in FRAMES:
        head = ('<script>window.__CO__=%s;window.__NAME__=%s;'
                'window.__SETUP__=function(){%s};</script>'
                % (json.dumps(f['co'], ensure_ascii=False),
                   json.dumps(f['name'].replace('_', ' '), ensure_ascii=False),
                   f['setup']))
        open('callout.html', 'w', encoding='utf-8').write(base + head + OVERLAY)
        out = 'callout_%s.png' % f['name']
        subprocess.run([
            CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
            '--force-device-scale-factor=2', f'--window-size={W},{H}',
            '--virtual-time-budget=6000', f'--screenshot={out}',
            'file://' + os.path.join(HERE, 'callout.html'),
        ], check=True, capture_output=True)
        print(f'{out}  ({os.path.getsize(out)//1024} KB)')
    os.remove('callout.html')


if __name__ == '__main__':
    main()
