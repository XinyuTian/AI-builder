"""
Pi Day Challenge: Automate drawing a perfect circle on https://yage.ai/genai/pi.html
Uses Playwright to simulate mouse events that trace a mathematical circle on the canvas.
"""

import asyncio
import math
from playwright.async_api import async_playwright

URL = "https://yage.ai/genai/pi.html"
CANVAS_SELECTOR = "#drawingCanvas"
CALCULATE_BTN = "#calculateBtn"

# Circle parameters (canvas is 350x350)
CENTER_X = 175
CENTER_Y = 175
RADIUS = 130
NUM_POINTS = 360


async def draw_circle():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=5)
        page = await browser.new_page()
        await page.goto(URL, wait_until="networkidle")

        canvas = page.locator(CANVAS_SELECTOR)
        box = await canvas.bounding_box()
        if not box:
            print("ERROR: Could not find canvas element")
            await browser.close()
            return

        canvas_screen_x = box["x"]
        canvas_screen_y = box["y"]

        def canvas_to_screen(cx, cy):
            return canvas_screen_x + cx, canvas_screen_y + cy

        # Generate circle points using parametric equation
        points = []
        for i in range(NUM_POINTS + 1):
            angle = 2 * math.pi * i / NUM_POINTS
            x = CENTER_X + RADIUS * math.cos(angle)
            y = CENTER_Y + RADIUS * math.sin(angle)
            points.append((x, y))

        # Move to start and press mouse
        sx, sy = canvas_to_screen(*points[0])
        await page.mouse.move(sx, sy)
        await page.mouse.down()

        # Trace the circle
        for x, y in points[1:]:
            sx, sy = canvas_to_screen(x, y)
            await page.mouse.move(sx, sy)

        # Release mouse to finish
        await page.mouse.up()

        await page.wait_for_timeout(300)
        await page.click(CALCULATE_BTN)
        await page.wait_for_timeout(500)

        result_text = await page.locator("#result").inner_text()
        print("\n===== Pi Calculation Result =====")
        print(result_text)
        print("=================================\n")

        print("Press Enter to close the browser...")
        await asyncio.get_event_loop().run_in_executor(None, input)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(draw_circle())
