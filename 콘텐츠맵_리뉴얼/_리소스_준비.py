"""아트리소스의 실제 챌린지 썸네일을 시안용으로 축소해 `썸네일(축소)/`에 저장한다.

실행: python3 _리소스_준비.py

원본은 `디지털창의환경팀/아트리소스/챌린지 썸네일/`에 있고 한 장이 최대 15MB라
그대로 임베드할 수 없음. 카드 썸네일은 171px(2배 캡쳐 시 342px)로 렌더되므로
560px / JPEG q78로 줄여도 충분함.

썸네일 63개 중 44개가 mp4임 — 영상 썸네일은 ffmpeg로 첫 프레임을 뽑아
정지 이미지로 쓰고, 시안 카드에는 '영상 썸네일'임을 배지로 표시함.
"""
import pathlib, subprocess, sys, unicodedata
from PIL import Image

SRC = pathlib.Path("/Users/hakkim/Desktop/디지털창의환경팀/아트리소스/챌린지 썸네일")
OUT = pathlib.Path(__file__).parent / "썸네일(축소)"
SIZE, QUALITY = 560, 78

# (파일 이름 앞부분, 시안에서 쓸 키) — 영상 썸네일은 첫 프레임을 추출
PICK = [
    ("쭉잡아당겨그리기",           "T01"),
    ("수다스러운말렛만들기",        "T02"),
    ("연필뽑기게임",              "T03"),
    ("물방울돋보기만들기",          "T04"),
    ("블라인드컨투어드로잉",        "T05"),
    ("도전패턴콜렉터",             "T06"),
    ("콜라주팝업카드",             "T07"),
    ("거울반전그리기",             "T08"),
    ("모든것에눈이있다면",          "T09"),
    ("아슬아슬물건쌓기",           "T10"),
    ("가상벽화",                  "T11"),
    ("감정연기연습",               "T12"),
    ("기생생물을찾아라",           "T13"),
    ("고마운밥상으로그린밥그림",     "T14"),
    ("가려운등을시원하게긁기챌린지",  "T15"),
    ("변신마술쇼쇼쇼",             "T16"),
    ("토스트4컷만화",              "T17"),
    ("틀린그림찾기",               "T18"),
    ("삐도둑아사라져라",           "T19"),
    ("잠망경으로보는세상",          "T20"),
]


def shrink(img, dest):
    img = img.convert("RGB")
    w, h = img.size
    s = SIZE / min(w, h)
    if s < 1:
        img = img.resize((round(w * s), round(h * s)), Image.LANCZOS)
    img.save(dest, "JPEG", quality=QUALITY, optimize=True)


def nfc(x):
    return unicodedata.normalize("NFC", x)


def main():
    OUT.mkdir(exist_ok=True)
    # macOS는 파일명을 NFD로 저장하므로 정규화해서 대조해야 함
    files = {nfc(f.name): f for f in SRC.iterdir() if f.is_file()}
    rows = []
    for stem, key in PICK:
        matches = [v for k, v in files.items() if nfc(k).startswith(nfc(stem) + "_thumb.")]
        if not matches:
            sys.exit(f"원본을 찾을 수 없음: {stem}")
        src = sorted(matches)[0]
        dest = OUT / f"{key}.jpg"
        if src.suffix.lower() == ".mp4":
            tmp = OUT / f"_{key}_frame.png"
            # 첫 프레임은 페이드인·백지인 경우가 많아 1초 지점을 뽑고, 짧으면 첫 프레임으로
            for ss in ("00:00:01", "00:00:00"):
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", ss,
                                "-i", str(src), "-vframes", "1", str(tmp)], check=True)
                if tmp.exists() and tmp.stat().st_size > 0:
                    break
            with Image.open(tmp) as im:
                shrink(im, dest)
            tmp.unlink()
        else:
            with Image.open(src) as im:
                shrink(im, dest)
        rows.append((key, src.suffix.lstrip("."), dest.stat().st_size // 1024))

    for key, ext, kb in rows:
        print(f"{key}  {ext:4s} → {kb:4d}KB")
    print(f"\n총 {len(rows)}장 / {sum(r[2] for r in rows)}KB → {OUT.name}/")


if __name__ == "__main__":
    main()
