"""템플릿의 {{토큰}}에 base64 이미지를 치환해 시안 html을 만든다.

실행: python3 _시안_빌드.py
시안을 수정할 때는 이 폴더의 _시안_템플릿(이미지 삽입 전 소스).html을 고치고 다시 실행할 것.
이미지는 IMG 객체에 한 번만 임베드하고 마크업은 data-img로 참조 — 같은 이미지를
여러 곳의 src에 박으면 파일 크기가 배로 늘어남.
"""
import base64, mimetypes, pathlib

BASE = pathlib.Path("/Users/hakkim/Desktop/디지털창의환경팀/아하오호 클래스 정식 출시")
W    = BASE / "콘텐츠맵_리뉴얼"
C    = BASE / "챌린지_상세보기모달_전체화면_개선"
EX   = pathlib.Path("/Users/hakkim/Desktop/디지털창의환경팀/아트리소스/게시물 예시 이미지")

TOKENS = {
    "THUMB1":  C / "챌린지 썸네일 예시 이미지1.png",
    "THUMB2":  C / "챌린지 썸네일 예시 이미지2.png",
    "GUIDE_W": C / "가이드 자세히 보기 이미지 예시(가로가 긴 형태).jpeg",
    "GUIDE_T": C / "가이드 자세히 보기 이미지 예시(세로가 긴 형태).jpeg",
    "PICK1":   EX / "85bbe795-8bb2-4ddd-8280-0870f53ce146.jpeg",
    "PICK2":   EX / "64ccc559-996a-484e-8477-7fe5b6266657.jpeg",
    "PICK3":   EX / "775951d6-3f18-4aa6-8544-665b16cadcbc.jpeg",
    "AV1":     EX / "76da0b63-0439-40cc-9fa2-7ffc8851c2fc.jpeg",
    "AV2":     EX / "ff6548d9-73ce-4074-8124-e3a218e3dcdd.jpeg",
}
# 콘텐츠맵 카드 썸네일 — _리소스_준비.py로 아트리소스에서 축소해 둔 것
TOKENS.update({f"T{i:02d}": W / "썸네일(축소)" / f"T{i:02d}.jpg" for i in range(1, 21)})

src = (W / "_시안_템플릿(이미지 삽입 전 소스).html").read_text(encoding="utf-8")
for tok, path in TOKENS.items():
    assert path.exists(), path
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    uri = f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"
    n = src.count("{{%s}}" % tok)
    assert n == 1, f"{tok}은 IMG 객체에 1번만 있어야 함 (현재 {n}번)"
    src = src.replace("{{%s}}" % tok, uri)
    print(f"{tok:8s} {path.name}")

assert "{{" not in src, "치환되지 않은 토큰 있음"
out = W / "시안_콘텐츠맵_리뉴얼.html"
out.write_text(src, encoding="utf-8")
print("→", out.name, f"{out.stat().st_size/1024/1024:.2f} MB")
