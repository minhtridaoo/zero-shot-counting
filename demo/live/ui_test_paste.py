"""Kiểm giao diện demo suy luận thật bằng trình duyệt Edge (Playwright): Ctrl+V thật, chạy, đổi ảnh/query, xóa.

Dùng: <python có playwright> demo/live/ui_test_paste.py --url http://127.0.0.1:7870 --img1 a.jpg --img2 b.jpg [--auth cs331:pass]
Ghi ảnh chụp vào --shots. In PASS/FAIL cho từng bước. Không đọc GT, không ghi vào kết quả nghiên cứu.
"""
import argparse
import base64
import io
import re
import sys
import time
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

STEPS = []


def check(name, cond, detail=""):
    STEPS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""), flush=True)


def png_b64(path):
    buf = io.BytesIO(); Image.open(path).convert("RGB").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def paste_image(page, path):
    """Đưa ảnh vào clipboard của trình duyệt rồi bấm Ctrl+V thật (không gọi thẳng vào ô upload)."""
    page.evaluate("""async (b64) => {
        const bin = atob(b64); const arr = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
        await navigator.clipboard.write([new ClipboardItem({'image/png': new Blob([arr], {type: 'image/png'})})]);
    }""", png_b64(path))
    page.locator("h1").first.click()          # focus vào trang, không phải ô chữ
    page.keyboard.press("Control+V")


def status(page):
    return page.locator("#live_status").inner_text()


def wait_status(page, pattern, timeout_s):
    t = time.time()
    while time.time() - t < timeout_s:
        s = status(page)
        if re.search(pattern, s):
            return s
        time.sleep(1)
    return status(page)


def visible_result_images(page):
    return page.evaluate("""() => [...document.querySelectorAll('img')].filter(i => i.offsetParent !== null
        && i.naturalWidth >= 700 && !i.closest('#live_image')).length""")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:7870")
    ap.add_argument("--img1", required=True); ap.add_argument("--img2", required=True)
    ap.add_argument("--q1", default="plates, bowls"); ap.add_argument("--q2", default="sheep, dogs")
    ap.add_argument("--auth", default=None, help="user:pass nếu app bật đăng nhập")
    ap.add_argument("--timeout", type=int, default=600, help="giây chờ mỗi lần chạy (CPU chậm)")
    ap.add_argument("--shots", default="demo/live/test_shots")
    a = ap.parse_args()
    shots = Path(a.shots); shots.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        br = p.chromium.launch(channel="msedge", headless=True)
        ctx = br.new_context(viewport={"width": 1366, "height": 900}, color_scheme="light",
                             permissions=["clipboard-read", "clipboard-write"])
        page = ctx.new_page()
        page.goto(a.url + "/?__theme=light")
        if a.auth:
            u, pw = a.auth.split(":", 1)
            page.get_by_label(re.compile("username", re.I)).fill(u); page.get_by_label(re.compile("password", re.I)).fill(pw)
            page.get_by_role("button", name=re.compile("login", re.I)).click()
        page.wait_for_selector("#live_image", timeout=60000)

        # 1. Ctrl+V ảnh 1
        paste_image(page, a.img1)
        page.wait_for_function("() => !!document.querySelector('#live_image img')", timeout=30000)
        check("Ctrl+V dán ảnh 1 vào ô ảnh", page.locator("#live_image img").count() > 0)
        page.locator("#live_queries textarea").fill(a.q1)
        page.screenshot(path=str(shots / "01_pasted.png"))
        # 2. Chạy
        page.locator("#live_run").click()
        s = wait_status(page, r"Đang chạy", 15)
        check("Hiện trạng thái đang xử lý", "Đang chạy" in s, s[:80])
        s = wait_status(page, r"Đã chạy model thật|❌", a.timeout)
        rid1 = (re.search(r"request (\S+)", s) or [None, None])[1]
        check("Chạy model thật xong cho ảnh 1", "Đã chạy model thật" in s, s[:160])
        n = visible_result_images(page)
        nq = len([q for q in a.q1.split(",") if q.strip()])
        check(f"Đủ 4 cách × {nq} tên vật có ảnh box", n == 4 * nq, f"{n} ảnh kết quả")
        body = page.inner_text("body")
        check("Có bảng đếm lẫn X/Y khi nhập 2 tên vật", "box dùng chung" in body.lower() if nq >= 2 else True)
        page.screenshot(path=str(shots / "02_result_img1.png"), full_page=True)
        # 3. Đổi query -> kết quả cũ bị xóa
        page.locator("#live_queries textarea").fill(a.q1.split(",")[0].strip())
        time.sleep(1.5)
        s = status(page)
        check("Đổi tên vật thì kết quả cũ bị xóa / đánh dấu", "đã thay đổi" in s and visible_result_images(page) == 0, s[:90])
        # 4. Ctrl+V ảnh 2 thay ảnh 1 (ô đang có ảnh)
        paste_image(page, a.img2)
        time.sleep(3)
        s = status(page)
        check("Dán ảnh 2 khi ô đã có ảnh: ảnh được thay, kết quả cũ không còn", visible_result_images(page) == 0 and page.locator("#live_image img").count() > 0, s[:90])
        page.locator("#live_queries textarea").fill(a.q2)
        page.locator("#live_run").click()
        s = wait_status(page, r"Đã chạy model thật|❌", a.timeout)
        rid2 = (re.search(r"request (\S+)", s) or [None, None])[1]
        check("Chạy model thật cho ảnh 2 + tên vật mới, request khác lần 1", "Đã chạy model thật" in s and rid2 and rid2 != rid1, f"{rid1} → {rid2}")
        page.screenshot(path=str(shots / "03_result_img2.png"), full_page=True)
        # 5. Thông báo lỗi dễ hiểu: tên vật có dấu chấm
        page.locator("#live_queries textarea").fill("cats. dogs")
        page.locator("#live_run").click()
        s = wait_status(page, r"❌", 30)
        check("Báo lỗi dễ hiểu khi tên vật không hợp lệ", "❌" in s and "dấu chấm" in s, s[:90])
        # 6. Xóa và bắt đầu lại
        page.locator("#live_clear").click(); time.sleep(1.5)
        check("Nút Xóa: ô ảnh và ô chữ trống, không còn kết quả",
              page.locator("#live_image img").count() == 0 and page.locator("#live_queries textarea").input_value() == ""
              and visible_result_images(page) == 0)
        # 7. Upload file (đường không dán)
        page.locator("#live_image input[type=file]").set_input_files(a.img1)
        page.wait_for_function("() => !!document.querySelector('#live_image img')", timeout=30000)
        check("Upload file vào ô ảnh", page.locator("#live_image img").count() > 0)
        page.screenshot(path=str(shots / "04_after_clear_upload.png"))
        br.close()
    print("TỔNG:", "PASS" if all(ok for _, ok in STEPS) else "FAIL", f"({sum(ok for _, ok in STEPS)}/{len(STEPS)})", flush=True)
    sys.exit(0 if all(ok for _, ok in STEPS) else 1)


if __name__ == "__main__":
    main()
