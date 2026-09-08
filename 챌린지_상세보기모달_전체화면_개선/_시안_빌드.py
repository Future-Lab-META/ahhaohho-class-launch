import base64, mimetypes, pathlib

BASE = pathlib.Path("/Users/hakkim/Desktop/디지털창의환경팀/아하오호 클래스 정식 출시")
W    = BASE / "챌린지_상세보기모달_전체화면_개선"
EX   = pathlib.Path("/Users/hakkim/Desktop/디지털창의환경팀/아트리소스/게시물 예시 이미지")

TOKENS = {
    "THUMB1":  W / "챌린지 썸네일 예시 이미지1.png",
    "THUMB2":  W / "챌린지 썸네일 예시 이미지2.png",
    "GUIDE_W": W / "가이드 자세히 보기 이미지 예시(가로가 긴 형태).jpeg",
    "GUIDE_T": W / "가이드 자세히 보기 이미지 예시(세로가 긴 형태).jpeg",
    # 아하's Pick — 다른 아이 게시물 예시 이미지
    "PICK1":   EX / "85bbe795-8bb2-4ddd-8280-0870f53ce146.jpeg",
    "PICK2":   EX / "64ccc559-996a-484e-8477-7fe5b6266657.jpeg",
    "PICK3":   EX / "775951d6-3f18-4aa6-8544-665b16cadcbc.jpeg",
    # Pick 작성자 프로필 이미지 — Pick 사진과 겹치지 않게 다른 게시물 이미지 사용
    "AV1":     EX / "76da0b63-0439-40cc-9fa2-7ffc8851c2fc.jpeg",
    "AV2":     EX / "ff6548d9-73ce-4074-8124-e3a218e3dcdd.jpeg",
}

src = (W / "_시안_템플릿(이미지 삽입 전 소스).html").read_text(encoding="utf-8")
for tok, path in TOKENS.items():
    assert path.exists(), path
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    uri = f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"
    n = src.count("{{%s}}" % tok)
    src = src.replace("{{%s}}" % tok, uri)
    print(f"{tok:8s} x{n}  {path.name}")

assert "{{" not in src, "치환되지 않은 토큰 있음"
out = W / "시안_챌린지상세보기_전체화면.html"
out.write_text(src, encoding="utf-8")
print("→", out, f"{out.stat().st_size/1024/1024:.2f} MB")
