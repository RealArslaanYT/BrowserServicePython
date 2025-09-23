from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from playwright.async_api import async_playwright, ViewportSize, Page, Browser
import asyncio
import json
import uuid

app = FastAPI()
browser: Browser = None
sessions: dict[str, Page] = {}
session_locks: dict[str, asyncio.Lock] = {}

FPS = 15  # VERY LOW so Render doesn't commit die when tryna run this
LIVE_FEED_QUALITY = 35  # Also quite low (less than half!) to satisfy Render's bad VM

@app.on_event("startup")
async def startup():
    global browser
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=True,
        chromium_sandbox=False,
        args=[
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-extensions",
            "--disable-infobars",
            "--disable-accelerated-2d-canvas",
            "--disable-software-rasterizer"
        ]
    )

async def get_or_create_page(sid: str):
    lock = session_locks.setdefault(sid, asyncio.Lock())
    async with lock:
        if sid not in sessions:
            page = await browser.new_page(viewport=ViewportSize(width=960, height=540))
            await page.goto("https://www.google.com")
            await page.wait_for_load_state("networkidle")
            sessions[sid] = page
    return sessions[sid]

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    sid = ws.query_params.get("sid")
    page = await get_or_create_page(sid)

    async def send_frames():
        try:
            while True:
                buf = await page.screenshot(type="jpeg", quality=LIVE_FEED_QUALITY)
                await ws.send_bytes(buf)  # send as binary
                await asyncio.sleep(1 / FPS)
        except Exception as e:
            print(f"Frame sender stopped: {e}")

    # run frame sender in background
    frame_task = asyncio.create_task(send_frames())

    try:
        async for message in ws.iter_text():
            data = json.loads(message)
            if data["type"] == "navigate":
                url = data["url"]
                if ":/" not in url:
                    url = f"http://{url}"
                await page.goto(url)
                await page.wait_for_load_state("networkidle")
            elif data["type"] == "mousemove":
                scaled_x = data["x"] * (960 / data["img_width"])
                scaled_y = data["y"] * (540 / data["img_height"])
                await page.mouse.move(x=scaled_x, y=scaled_y)
            elif data["type"] == "click":
                scaled_x = data["x"] * (960 / data["img_width"])
                scaled_y = data["y"] * (540 / data["img_height"])
                await page.mouse.click(x=scaled_x, y=scaled_y)
            elif data["type"] == "rightClick":
                scaled_x = data["x"] * (960 / data["img_width"])
                scaled_y = data["y"] * (540 / data["img_height"])
                await page.mouse.click(x=scaled_x, y=scaled_y, button="right")
            elif data["type"] == "keypress":
                await page.keyboard.press(data["key"])
            elif data["type"] == "wheel":
                await page.mouse.wheel(data["deltaX"], data["deltaY"])
    finally:
        frame_task.cancel()
        await page.close()
        sessions.pop(sid, None)
        session_locks.pop(sid, None)

@app.get("/")
def index():
    with open("index.html") as f:
        return HTMLResponse(f.read())
