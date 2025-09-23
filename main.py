from fastapi import FastAPI, WebSocket, Request, Depends
from fastapi.responses import StreamingResponse, HTMLResponse
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

@app.get("/live")
async def live_feed(request: Request):
    sid = request.query_params.get("sid")
    page = await get_or_create_page(sid)

    print("Sessions object from live:", sessions)
    print("Session locks object from live:", session_locks)

    async def generate():
        while True:
            buf = await page.screenshot(type="jpeg", quality=LIVE_FEED_QUALITY)
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + buf + b"\r\n")
            await asyncio.sleep(1 / FPS)

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    sid = ws.query_params.get("sid")
    page = await get_or_create_page(sid)

    print("Sessions object from WS:", sessions)
    print("Session locks object from WS:", session_locks)

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
            await page.mouse.move(scaled_x, scaled_y)
        elif data["type"] == "click":
            scaled_x = data["x"] * (960 / data["img_width"])
            scaled_y = data["y"] * (540 / data["img_height"])
            await page.mouse.click(scaled_x, scaled_y)
        elif data["type"] == "keypress":
            await page.keyboard.press(data["key"])
        elif data["type"] == "wheel":
            await page.mouse.wheel(data["deltaX"], data["deltaY"])

    await page.close()
    sessions.pop(sid, None)
    session_locks.pop(sid, None)

@app.get("/")
def index():
    with open("index.html") as f:
        return HTMLResponse(f.read())
