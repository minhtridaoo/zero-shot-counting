"""Sinh demo/live/kaggle_live_demo.ipynb: notebook Kaggle T4 chạy demo suy luận thật (Gradio, link https).

- Ô môi trường lấy NGUYÊN VĂN ô 3 của experiments/countgdpp/kaggle_p1_test.ipynb (môi trường đã chạy test 11/11).
- Code demo (live_engine.py, app_live.py, check_against_test.py) được nhúng vào notebook kèm sha256,
  vì chưa push lên GitHub. Repo được clone ở commit cố định để có code CountGD++, freeze, audit đã khóa.
Chạy lại script này mỗi khi sửa code demo:  python demo/live/build_kaggle_notebook.py
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
W8 = ROOT / "experiments/countgdpp/kaggle_p1_test.ipynb"
OUT = HERE / "kaggle_live_demo.ipynb"
PIN = "974048f"  # main ngày 24/11, có freeze v2, audit, code runner đã khóa
FILES = ["live_engine.py", "app_live.py", "check_against_test.py"]


def code(src):
    return dict(cell_type="code", metadata={}, execution_count=None, outputs=[], source=src.strip("\n").splitlines(True))


def md(src):
    return dict(cell_type="markdown", metadata={}, source=src.strip("\n").splitlines(True))


def main():
    w8 = json.loads(W8.read_text(encoding="utf-8"))
    env_cell = "".join(w8["cells"][3]["source"])
    assert env_cell.startswith("# Ô 3 — môi trường /tmp/venv310"), "Ô 3 của notebook W8 đã đổi; xem lại"
    files = {n: (HERE / n).read_text(encoding="utf-8") for n in FILES}
    digests = {n: hashlib.sha256(s.encode("utf-8")).hexdigest() for n, s in files.items()}
    cells = [
        md(f"""
# Demo suy luận THẬT — CountGD++ trên ảnh mới (CS331), Kaggle T4

Notebook này chạy model trên GPU của Kaggle rồi mở giao diện web qua link **https://….gradio.live** để mở trên trình duyệt.
Bạn dán ảnh bằng Ctrl+V, nhập tên vật, bấm **Chạy**. Model chạy thật trên ảnh đó cho cả bốn cách: B0, B2, P+F, C6.

**Cài đặt phiên (bên phải màn hình, mục Session options):**
- **Accelerator: GPU T4 x2**.
- **Internet: On**. Kaggle yêu cầu tài khoản đã xác minh số điện thoại.
- (Nếu gdown báo quá lượt tải) **Add Input** → dataset riêng chứa `countgd_plusplus.pth`. Đây chính là dataset đã gắn khi chạy test 11/11.

**Chạy:** dùng **Run All** trong chế độ chỉnh sửa (phiên tương tác), **không** dùng "Save & Run All". Cách sau chạy nền, không mở được link.
- Lần đầu khoảng 10–15 phút: cài môi trường và build CUDA ops.
- Ô cuối in **link** và **mật khẩu** (user `cs331`). Giữ ô đó chạy và giữ tab Kaggle mở trong lúc demo.

**Giới hạn:**
- Link gradio.live sống tối đa 72 giờ nhưng chết ngay khi phiên Kaggle tắt.
- Phiên tương tác tắt sau khoảng 12 giờ, hoặc sớm hơn nếu bỏ tab lâu không thao tác.
- GPU miễn phí khoảng 30 giờ/tuần.
- Mỗi lần mở phiên mới thì link mới.

**Không đổi điều kiện so với lần test 11/11:**
- Cùng checkpoint (sha256 kiểm theo audit 14/10), cùng `process_folder.py` đã pin.
- Cùng môi trường: ô 3 chép nguyên văn từ notebook W8.
- Seed 42; τ_sample 0.23; P(τ 0.20, M 5); F với bounds/threshold **riêng** của P+F và C6 từ `freeze_v2_20261111.json`.
- Ô 6 chạy lại 3 query test đã có kết quả để xác nhận wrapper khớp số đếm chính thức. Đây chỉ là kiểm wrapper, **không** phải chạy lại test.

Ảnh dùng trong demo **không** đưa vào bảng kết quả nghiên cứu. Log từng lần chạy: `/kaggle/working/demo_logs/requests.jsonl`.
"""),
        code(f"""
# Ô 1 — thiết lập chung (cùng tên biến với notebook W8 để ô 3 chạy nguyên văn)
import datetime, glob, hashlib, json, os, pathlib, re, secrets, shlex, shutil, subprocess, sys, time
REPO_URL = "https://github.com/minhtridaoo/zero-shot-counting.git"
REPO_REF = "{PIN}"
FREEZE_SHA = "64e89ef53eab306fdbb33cfc39797749ff17cc8635f46ae381d96e45c4f6736d"
ROOT = pathlib.Path("/tmp/CS331")
PY = "/tmp/venv310/bin/python"
OUT = pathlib.Path("/kaggle/working/demo_out"); OUT.mkdir(parents=True, exist_ok=True)
LOGS = pathlib.Path("/kaggle/working/demo_logs"); LOGS.mkdir(parents=True, exist_ok=True)
DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD") or secrets.token_urlsafe(6)   # đổi ở đây nếu muốn mật khẩu cố định
ENV = os.environ.copy()
ENV.update(CUDA_VISIBLE_DEVICES="0", MPLBACKEND="Agg", PYTHONUNBUFFERED="1", GRADIO_ANALYTICS_ENABLED="False")
def sh(cmd, cwd=None):
    print("$", cmd, flush=True)
    p = subprocess.Popen(cmd, shell=True, cwd=cwd, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in p.stdout:
        print(line, end="", flush=True)
    if p.wait():
        raise RuntimeError(f"Lệnh lỗi (mã {{p.returncode}}), xem các dòng ngay phía trên. Dừng.")
def file_hash(path, algo="sha256"):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()
gpu = subprocess.check_output("nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader", shell=True, text=True)
print(gpu)
assert "T4" in gpu.splitlines()[0], "Cần GPU T4 (Session options > Accelerator > GPU T4 x2). Dừng."
"""),
        code("""
# Ô 2 — lấy code ở commit cố định; kiểm freeze v2
if not ROOT.exists():
    sh(f"git clone -q {REPO_URL} {ROOT}")
sh(f"git fetch -q origin && git checkout -q {REPO_REF}", cwd=ROOT)
COMMIT = subprocess.check_output("git rev-parse HEAD", shell=True, cwd=ROOT, text=True).strip()
print("commit", COMMIT)
assert file_hash(ROOT / "results/countgdpp/freeze_v2_20261111.json") == FREEZE_SHA, "freeze v2 khác sha256. Dừng."
print("freeze v2 khớp sha256")
"""),
        code(env_cell + """

# Thêm cho demo: Gradio, giữ nguyên các bản đã pin của môi trường test (không nâng cấp torch/transformers/numpy/pillow)
sh(f'uv pip install -q -p {PY} "gradio==5.50.0" "huggingface_hub<1.0" transformers==4.44.2 numpy==2.2.6 pillow==10.4.0')
sh(f"{PY} -c " + shlex.quote("import torch, transformers, numpy, PIL, gradio; print('sau khi cài gradio: torch', torch.__version__, '| transformers', transformers.__version__, '| numpy', numpy.__version__, '| pillow', PIL.__version__, '| gradio', gradio.__version__)"))
"""),
        code("""
# Ô 4 — checkpoint CountGD++ (kiểm sha256 đã audit 14/10), BERT, và ảnh MUCCA (chỉ để ô 6 kiểm wrapper)
CKPT = ROOT / "CountGDPlusPlus/checkpoints/countgd_plusplus.pth"
EXPECTED = json.loads((ROOT / "results/countgdpp/checkpoint_audit_2026-10-14.json").read_text())["checkpoint_sha256"]
if not CKPT.exists():
    local = glob.glob("/kaggle/input/**/countgd_plusplus.pth", recursive=True)
    if local:
        shutil.copy(local[0], CKPT)
    else:
        sh(f"uv pip install -q -p {PY} gdown")
        sh(f'/tmp/venv310/bin/gdown "https://drive.google.com/uc?id=1j6N22TtKu2NVcKpgfrf-sJHGeLDqs9hs" -O {CKPT}')
assert file_hash(CKPT) == EXPECTED, "checkpoint sha256 sai"
print("Checkpoint đúng bản đã audit 14/10.")
BERT = ROOT / "CountGDPlusPlus/checkpoints/bert-base-uncased"
if not any((BERT / n).exists() for n in ("model.safetensors", "pytorch_model.bin")):
    sh(f"{PY} download_bert.py", cwd=ROOT / "CountGDPlusPlus")
print("BERT:", sorted(p.name for p in BERT.iterdir()))
MUCCA = ROOT / "data_external/mucca_zenodo_19231375/MUCCA_1.0"
if not (MUCCA / "images/mcac_12.jpg").exists():
    sh('wget -q -O /tmp/MUCCA_1.0.zip "https://zenodo.org/api/records/19231375/files/MUCCA_1.0.zip/content"')
    assert file_hash("/tmp/MUCCA_1.0.zip", "md5") == "b182e445445dad017493ffb35803f816", "md5 MUCCA sai"
    MUCCA.mkdir(parents=True, exist_ok=True)
    sh(f"unzip -q -o /tmp/MUCCA_1.0.zip -d {MUCCA}")
print("Ảnh MUCCA:", len(list((MUCCA / "images").glob("*.jpg"))))
"""),
        code("# Ô 5 — ghi code demo (nhúng từ máy Trí, kiểm sha256)\nDEMO_FILES = " + json.dumps(files, ensure_ascii=False)
             + "\nDEMO_SHA = " + json.dumps(digests) + """
live = ROOT / "demo/live"; live.mkdir(parents=True, exist_ok=True)
for name, src in DEMO_FILES.items():
    (live / name).write_text(src, encoding="utf-8")
    assert hashlib.sha256(src.encode("utf-8")).hexdigest() == DEMO_SHA[name], name
    print(f"{name}: sha256 {DEMO_SHA[name][:12]}…")
"""),
        code("""
# Ô 6 — kiểm wrapper trên GPU: 3 query test đã có kết quả chính thức phải ra đúng số đếm của cả 4 cách.
# Đây KHÔNG phải chạy lại test (không chấm, không ghi vào kết quả); dừng nếu lệch.
sh(f"{PY} demo/live/check_against_test.py --device cuda --data-root {ROOT} --queries t01_1 t01_2 t05_1 --log-dir {LOGS}/check", cwd=ROOT)
"""),
        code("""
# Ô 7 — MỞ DEMO. Giữ ô này chạy trong lúc demo; bấm Stop (■) để tắt.
proc = subprocess.Popen([PY, "demo/live/app_live.py", "--device", "cuda", "--share", "--host", "0.0.0.0", "--port", "7860",
                         "--password", DEMO_PASSWORD, "--log-dir", str(LOGS)], cwd=ROOT, env=ENV,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
url = None
try:
    for line in proc.stdout:
        if "Warning" in line or "warn(" in line:
            continue
        print(line, end="", flush=True)
        m = re.search(r"https://[\\w.-]+\\.gradio\\.live", line)
        if m and not url:
            url = m.group(0)
            print("\\n" + "=" * 70 + f"\\nLINK DEMO: {url}\\nĐăng nhập: user = cs331 · mật khẩu = {DEMO_PASSWORD}\\n" + "=" * 70, flush=True)
except KeyboardInterrupt:
    pass
finally:
    proc.terminate()
    print("Đã tắt demo. Log:", LOGS / "requests.jsonl")
"""),
        md("""
## Sau khi demo

- Log mọi lần bấm Chạy: `/kaggle/working/demo_logs/requests.jsonl`. Tải ở tab Output nếu muốn lưu.
- Mỗi dòng log ghi: request id, sha256 ảnh, tên vật, thiết bị GPU, checkpoint, freeze, cấu hình, số đếm và thời gian từng cách.
- Ảnh demo **không** phải dữ liệu nghiên cứu; không đưa vào bảng kết quả.
"""),
    ]
    nb = dict(cells=cells, metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                     "language_info": {"name": "python"}}, nbformat=4, nbformat_minor=5)
    OUT.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("Đã ghi", OUT, "| code demo:", {k: v[:12] for k, v in digests.items()})


if __name__ == "__main__":
    main()
