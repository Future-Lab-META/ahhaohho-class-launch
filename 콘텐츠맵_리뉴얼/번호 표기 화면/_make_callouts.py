"""프로토타입에 번호 + 이름표 + 연결선을 얹어 기획서용 캡쳐를 만든다.

실행: python3 _make_callouts.py
     → callout.html 생성 후 헤드리스 크롬으로 프레임별 PNG 캡쳐

필터를 접은 기본 화면과 펼친 화면을 나눠 캡쳐하고, 각 캡쳐에는 그 화면의 번호만 표기함.
번호 위치는 레이아웃에서 자동 계산하므로 프로토타입을 수정한 뒤 다시 실행하면 됨.
"""
import json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
VIEWER = os.path.join(HERE, '..', '시안_콘텐츠맵_리뉴얼.html')
W, H = 1280, 800

CHROME = next((p for p in [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    shutil.which('google-chrome') or '', shutil.which('chromium') or '',
] if p and os.path.exists(p)), None)

# 시안 전용 안내 배너는 캡쳐에서 숨김 — 실제 화면 조건으로 찍기 위해
HIDE_NOTE = "document.querySelector('.demoNote').style.display='none';"

FRAMES = [
    dict(
        name='기본화면',
        setup=HIDE_NOTE + "if(!document.getElementById('fPanel').hidden) toggleFilter();",
        co={
            # 사이드바 항목은 폭이 264px 전체 — 밖으로 빼면 본문·이웃 항목을 덮으므로
            # 같은 행 안쪽 오른쪽(메뉴 텍스트 오른편 빈 공간)에 둠
            '1':  {'sel': '.navList li.now button', 'at': 'right', 'dx': -80, 'label': '사이드바 메뉴', 'tone': 'green',
                   # 배지가 메뉴 행 안에 들어가 있어 연결선·점이 오히려 지저분해짐
                   'noLine': True},
            '2':  {'sel': '.removedBtn', 'at': 'bottom', 'dy': 30, 'label': '기존 버튼 제거', 'tone': 'blue'},
            '3':  {'sel': '.pageHead h1', 'at': 'right', 'dx': 62, 'label': '화면 제목'},
            '4':  {'sel': '.headBtns', 'at': 'top', 'dy': -30, 'label': '수업 사례·큐레이션 만들기'},
            '5':  {'sel': '.searchBox', 'at': 'left', 'dx': -62, 'label': '검색창'},
            '6':  {'sel': '.filterBtn', 'at': 'left', 'dx': -64, 'label': '필터 버튼', 'tone': 'green'},
            '8':  {'sel': '.count', 'at': 'right', 'dx': 92, 'label': '챌린지 수'},
            '9':  {'sel': '.sortSel', 'at': 'right', 'dx': 58, 'label': '정렬', 'tone': 'green'},
            # 카드 폭이 141px로 좁아 카드 사이에 배지를 둘 수 없음 → 첫 카드 기준으로 왼쪽에 세로 배치
            '10-2': {'sel': '#grid .newTag', 'at': 'left', 'dx': -58, 'label': 'NEW 배지', 'tone': 'green'},
            '10-1': {'sel': '#grid .cCard:first-child .art', 'at': 'left', 'dx': -70, 'label': '썸네일'},
            '10-3': {'sel': '#grid .cCard:first-child .cat', 'at': 'left', 'dx': -70, 'label': '카테고리'},
            '10-4': {'sel': '#grid .cCard:first-child .tit', 'at': 'left', 'dx': -70, 'label': '챌린지명'},
        },
    ),
    dict(
        name='필터_펼침',
        setup=(HIDE_NOTE +
               "if(document.getElementById('fPanel').hidden) toggleFilter();"
               "document.querySelector('.fChip[data-k=\"cat\"][data-v=\"몸과 감각\"]').click();"
               "document.querySelector('.fChip[data-k=\"lv\"][data-v=\"2\"]').click();"),
        co={
            '6':   {'sel': '#fDot', 'at': 'top', 'dy': -30, 'label': '적용 표시(점)', 'tone': 'green'},
            '7-1': {'sel': '#fCat',   'at': 'left', 'dx': -66, 'label': '카테고리'},
            '7-2': {'sel': '#fGrade', 'at': 'left', 'dx': -66, 'label': '학년'},
            '7-3': {'sel': '#fSubj',  'at': 'left', 'dx': -66, 'label': '과목'},
            '7-4': {'sel': '#fLv',    'at': 'left', 'dx': -66, 'label': '난이도', 'tone': 'green'},
            '7-5': {'sel': '.fRow:last-child .fReset', 'at': 'right', 'dx': 60, 'label': '행별 초기화'},
        },
    ),
    dict(
        # 결과 0건 — '수와 생각' + 난이도 5는 교차하는 챌린지가 없는 조합
        name='필터_결과없음',
        setup=(HIDE_NOTE +
               "if(document.getElementById('fPanel').hidden) toggleFilter();"
               "document.querySelector('.fChip[data-k=\"cat\"][data-v=\"수와 생각\"]').click();"
               "document.querySelector('.fChip[data-k=\"lv\"][data-v=\"5\"]').click();"),
        co={
            '8':   {'sel': '.count', 'at': 'right', 'dx': 92, 'label': '챌린지 0개'},
            '7-6': {'sel': '#empty p', 'at': 'left', 'dx': -104, 'label': '결과 없음 안내'},
        },
    ),
    dict(
        name='카드클릭_모달',
        setup=(HIDE_NOTE +
               "if(!document.getElementById('fPanel').hidden) toggleFilter();"
               "document.querySelectorAll('#grid .cCard')[3].click();"),
        co={
            '11': {'sel': '.topbar', 'at': 'bottom', 'dy': 36, 'label': '챌린지 상세 보기 모달', 'tone': 'blue'},
        },
    ),
]

OVERLAY = r"""
<style>
  /* width/height를 명시하지 않으면 SVG가 기본 300×150으로만 그려져 선이 잘림 */
  #coSvg{position:fixed;left:0;top:0;width:100vw;height:100vh;z-index:899;pointer-events:none;overflow:visible}
  #coLayer{position:fixed;inset:0;z-index:900;pointer-events:none}
  .co{
    position:absolute;transform:translate(-50%,-50%);
    background:#E8380D;color:#fff;border-radius:999px;
    font-family:"Pretendard Variable",Pretendard,-apple-system,"Apple SD Gothic Neo",sans-serif;
    font-size:11.5px;font-weight:500;line-height:1;
    padding:5px 9px 5px 6px;white-space:nowrap;
    box-shadow:0 2px 8px rgba(0,0,0,.5);
    display:flex;align-items:center;gap:5px;
  }
  .co b{background:rgba(255,255,255,.22);border-radius:999px;padding:2px 5px;font-weight:700;font-size:11px}
  .co.blue{background:#1668D9}
  .co.green{background:#137A46}
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
      bx = it.ax; by = it.ay;
    } else {
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

  for (const it of items){
    const {ax, ay, bx, by, w, h, cfg} = it;
    if (!it.hasOffset || cfg.noLine) continue;
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
  window.__SETUP__();
  try { await document.fonts.ready; } catch(e){}
  /* 폰트·이미지 로드로 위치가 밀리므로 여러 번 다시 그림 */
  for (const w of [300, 400, 500, 600]){
    await new Promise(r=>setTimeout(r, w));
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
    for f in FRAMES:
        head = ('<script>window.__CO__=%s;window.__SETUP__=function(){%s};</script>'
                % (json.dumps(f['co'], ensure_ascii=False), f['setup']))
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
