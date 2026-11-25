"""Chụp giao diện demo đang chạy (Edge có sẵn trên máy, qua Playwright) để chèn vào slide.

Dùng: .venv-demo\\Scripts\\python demo\\capture_screens.py [--url http://127.0.0.1:7860]
Ra: final/shared/figures/demo_tab1.png, demo_tab2.png, demo_tab3.png
"""
import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parents[1] / "final/shared/figures"


def wait_images(page, n):
    page.wait_for_function(
        f"[...document.querySelectorAll('img')].filter(i => i.complete && i.naturalWidth > 300).length >= {n}",
        timeout=30000)
    page.wait_for_timeout(800)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--url", default="http://127.0.0.1:7860")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        br = p.chromium.launch(channel="msedge", headless=True)
        page = br.new_page(viewport={"width": 1280, "height": 820}, device_scale_factor=1.5,
                           color_scheme="light")
        page.goto(a.url + "/?__theme=light")
        wait_images(page, 4)
        page.screenshot(path=str(OUT / "demo_tab1.png"), full_page=False)

        page.get_by_role("tab", name="2 · Lỗi X/Y (box dùng chung)").click()
        wait_images(page, 5)
        page.screenshot(path=str(OUT / "demo_tab2.png"), full_page=False)

        page.get_by_role("tab", name="3 · Bộ lọc F").click()
        wait_images(page, 6)
        page.screenshot(path=str(OUT / "demo_tab3.png"), full_page=False)
        br.close()
    print("Đã lưu:", *(OUT / f"demo_tab{i}.png" for i in (1, 2, 3)))


if __name__ == "__main__":
    main()
