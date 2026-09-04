"""프로토타입에 번호(1-1~1-18) + 이름표 + 연결선을 얹어 기획서용 캡쳐 1장을 만든다.

실행: python3 make_callouts.py  → callout.html 생성 후 헤드리스 크롬으로 캡쳐
모든 번호가 한 화면에 나오도록, 캡쳐 전용 게시물(영상+이미지 2장 / 숨겨진 댓글 포함)을 추가해 사용.
"""
import base64, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def uri(p, m='image/jpeg'):
    return f"data:{m};base64," + base64.b64encode(open(p, 'rb').read()).decode()

html = open('gallery_template.html', encoding='utf-8').read()
for tok, f, m in [
    ('{{M_PORT}}', 'media_port.jpg', 'image/jpeg'),
    ('{{M_LAND}}', 'media_land.jpg', 'image/jpeg'),
    ('{{VID_MP4}}', 'ex_video.mp4', 'video/mp4'),
    ('{{VID_POSTER}}', 'ex_video_poster.jpg', 'image/jpeg'),
    ('{{EX_PLANE}}', 'ex_plane.jpg', 'image/jpeg'),
    ('{{EX_ROBOT}}', 'ex_robot.jpg', 'image/jpeg'),
    ('{{EX_ROBOT2}}', 'ex_robot2.jpg', 'image/jpeg'),
    ('{{EX_CAT}}', 'ex_cat.jpg', 'image/jpeg'),
    ('{{EX_RUN}}', 'ex_run.jpg', 'image/jpeg'),
    ('{{EX_DRAW}}', 'ex_draw.jpg', 'image/jpeg'),
]:
    html = html.replace(tok, uri(f, m))
assert '{{' not in html

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
/* 캡쳐 전용 게시물 — 모든 번호가 한 화면에 나오도록 조건을 모두 갖춤
   (영상 + 미디어 2장 + 관리자 숨김 댓글 + 작성자 숨김 댓글 + 고정 상태) */
projects.push({
  type:'curation', curation:'만들기 챌린지', challenge:'움직이는 로봇 만들기',
  maker:'초록발명가', avatar:'🤖', memberName:'이도윤', date:'9월 1일',
  media:[VID_MP4, EX_ROBOT2], video:true, poster:VID_POSTER, duration:'0:12', pinned:true,
  body:'내가 조립한 로봇 강아지! 다리 움직이게 하려고 기어를 두 개 넣었어요 🐶',
  comments:[
    {name:'지후', avatar:'🐳', memberName:'박지후', date:'9월 2일', text:'와 이거 어떻게 만든거야?? 나도 만들어보고 싶어!'},
    {name:'구름이', avatar:'☁️', date:'9월 2일', text:'(작성자가 앱에서 숨긴 댓글)', hiddenByAuthor:true},
    {name:'퓨야호', avatar:'🐻', date:'9월 2일', text:'(관리자가 숨긴 댓글 — 1-2로 복원)', hiddenByAdmin:true},
  ],
});

/* sel: 대상 · at: 기준점 · dx/dy: 배지 오프셋 · label: 이름표 */
const CO = {
  '1-1':  {sel:'#crumbCuration', at:'bottom', dy:30,  label:'큐레이션 정보'},
  '1-2':  {sel:'#unhideBtn',     at:'left', dx:-78, label:'댓글 숨김 해제'},
  '1-5':  {sel:'.topbar .tb-btn:last-child', at:'bottom', dy:30, label:'닫기'},

  '1-13': {sel:'#stageVid',   at:'center',      label:'게시물 이미지/영상', tone:'blue'},
  '1-14': {sel:'#durBadge',   at:'right', dx:78, label:'영상 길이', tone:'blue'},
  '1-17': {sel:'#stageVid',   at:'topright', dx:-72, dy:40, label:'확대(휠·핀치)', tone:'green'},
  '1-15': {sel:'.mediaCtrl .mBtn', at:'left', dx:-72, label:'미디어 이동'},
  '1-16': {sel:'#dots',       at:'bottom', dy:28,  label:'페이지 인디케이터'},
  '1-7':  {sel:'.pArrow.next',at:'bottom', dy:52,  label:'다음·이전 작품'},

  '1-18': {sel:'#hintBar',    at:'top',  dy:-26, label:'조작 안내', tone:'green'},

  '1-3':  {sel:'#pAvatar',    at:'left', dx:-70, label:'작성자 정보'},
  '1-4':  {sel:'.railHead .more', at:'bottom', dy:26, label:'더보기'},
  '1-6':  {sel:'#pBody',      at:'left', dx:-62, label:'게시물 내용'},
  '1-8':  {sel:'.cmt p',      at:'left', dx:-58, label:'댓글 내용'},
  '1-9':  {sel:'.cmt .cMore', at:'bottom', dy:26, label:'댓글 더보기'},
  '1-10': {sel:'#pinBtn',     at:'top',  dy:-30, label:'게시물 고정'},
  '1-11': {sel:'#challBtn',   at:'top',  dy:-30, label:'챌린지 상세 보기'},
};

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
      bx = it.ax; by = it.ay;                      // 대상 위에 겹치는 배지(1-13 등)
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
    /* 선의 시작점 = 배지 사각형 테두리에서 대상 방향 */
    const dx = ax - bx, dy = ay - by;
    const k = Math.min(1,
      Math.min((w/2 + 3) / Math.max(Math.abs(dx), 1e-6),
               (h/2 + 3) / Math.max(Math.abs(dy), 1e-6)));
    const sx = bx + dx * k;
    const sy = by + dy * k;

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
  openViewer(projects.length - 1);          // 캡쳐 전용 게시물
  await new Promise(r=>setTimeout(r, 700));
  try { await document.fonts.ready; } catch(e){}
  for (const w of [300, 400, 500, 600]){
    await new Promise(r=>setTimeout(r, w));
    drawCallouts();
  }
  addEventListener('resize', drawCallouts);
  document.title = 'ready';
})();
</script>
"""

open('callout.html', 'w', encoding='utf-8').write(html + OVERLAY)
print('callout.html built', len(html + OVERLAY) // 1024, 'KB')
