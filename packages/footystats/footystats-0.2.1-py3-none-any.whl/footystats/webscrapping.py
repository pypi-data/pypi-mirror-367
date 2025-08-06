import asyncio
import random
import math

from playwright.async_api import async_playwright
from playwright.async_api import Page
from playwright.async_api import TimeoutError
from footystats.leagues import leagues
from footystats.leagues import teams_to_exclude
from footystats.utils import sortURLbyDate, verifyRoundWithRightSeason
from footystats.utils import incrementDate

from bs4 import BeautifulSoup
from urllib.parse import urljoin

rooturl:str = "https://www.worldfootball.net"

LOCATIONS = {
    "London":    {"latitude": 51.5074, "longitude": -0.1278, "locale": "en-GB"},
    "New York":  {"latitude": 40.7128, "longitude": -74.0060, "locale": "en-US"},
    "Los Angeles": {"latitude": 34.0522, "longitude": -118.2437, "locale": "en-US"},
    "Dublin":    {"latitude": 53.3498, "longitude": -6.2603, "locale": "en-IE"},
    "Berlin":    {"latitude": 52.5200, "longitude": 13.4050, "locale": "de-DE"},
    "Paris":     {"latitude": 48.8566, "longitude": 2.3522, "locale": "fr-FR"},
    "Tokyo":     {"latitude": 35.6895, "longitude": 139.6917, "locale": "ja-JP"},
    "Sydney":    {"latitude": -33.8688, "longitude": 151.2093, "locale": "en-AU"},
    "Toronto":   {"latitude": 43.651070, "longitude": -79.347015, "locale": "en-CA"},
    "São Paulo": {"latitude": -23.5505, "longitude": -46.6333, "locale": "pt-BR"},
}


async def rotate_locations(context, page, delay=60):
    """Cycle randomly through cities, changing geolocation every `delay` seconds."""
    while True:
        cities = list(LOCATIONS.items())
        random.shuffle(cities)  # Randomize order each cycle

        for city, location in cities:
            print(f"[+] Switching location to: {city}")

            # Update context geolocation
            await context.set_geolocation({
                "latitude": location["latitude"],
                "longitude": location["longitude"]
            })
            await context.set_extra_http_headers({"Accept-Language": location["locale"]})

            # Reload page to apply new location
            await page.reload()
            print(f"    -> Reloaded page with locale {location['locale']}")

            await asyncio.sleep(delay)  # wait before next switch

async def block_ads(page):
    """
    block requests related to common advertising networks 
    on the given page to reduce clutter and speed up loading.
    this is done by intercepting all network requests and 
    aborting those that match known ad-related URL patterns.

    custom patterns like "googlevignette" are also included 
    to catch additional ad elements that may bypass standard 
    filters.

    this function should be called before page navigation 
    to ensure ads are blocked from the start.

    :param page: the Playwright page instance on which to 
    block ad-related network requests
    :type page: playwright.async_api.Page
    """
    ad_patterns = [
        "googlesyndication.com",
        "doubleclick.net",
        "googleads.g.doubleclick.net",
        "adservice.google",
        "googlevignette"  # include custom indicators
    ]

    async def handle_route(route, request):
        if any(pattern in request.url for pattern in ad_patterns):
            await route.abort()
        else:
            await route.continue_()

    await page.route("**/*", handle_route)

def valid_url(url:str)->bool:
    """
    this function is used in getURLfromForm
    It checks if a url contains a forbidden keyword
    This elimintates non-standard seasons
    Sometimes, some seasons have playoff, relegation matches, etc
    The goal is to have ony standard seasons, with no particular situations
    that do not reflect "normal" season
    
    A list of forbidden keywords is established inside the func.
    Cautious, a feature far to be optimal is there:
    to exclude url concerning relegation matches, the word "sued"
    is present in the list of the forbidden keywords.
    The problem is that in SerieB, its excludes the urls
    dealing with fc-suedtirol club.
    Hence, even if its shitty, a specific condition is hardcoded
    
    :param url: url coming from a form (when listing seasons)
    :type url: str
    :return: True or False
    :rtype: bool
    """
    exclude_url_with:list=["playoff","playout","aufstieg","abstieg",
    "uefa-cup","relegation","vorrunde","finale","match-des-champions",
    "groupe","sued","nord"]

    for kw in exclude_url_with:
        if url.find("fc-suedtirol")!=-1:
            return True
        if url.find(kw)!=-1:
            return False
    return True

async def move_mouse_human_like(page, selector, steps=None):
    """
    move the mouse cursor to the center of a given element 
    on the page using a human-like pattern.
    the movement may follow either a straight line or a 
    curved path with randomized steps to mimic human behavior.
    this function is asynchronous and can be used with 
    Playwright's async API.

    it assumes the mouse starts at position (0, 0) since 
    Playwright does not track the current mouse location.
    at the end of the movement, a short random pause is 
    applied to simulate natural user hesitation.

    :param page: the Playwright page instance to operate on
    :type page: playwright.async_api.Page
    :param selector: the CSS selector of the element to 
    which the mouse will move
    :type selector: str
    :param steps: optional number of movement steps; 
    if not provided, a random value between 30 and 80 
    is selected
    :type steps: int or None
    """
    element = await page.query_selector(selector)
    if not element:
        raise ValueError(f"Element not found for selector: {selector}")

    box = await element.bounding_box()
    print("*****************************************")
    print(box)
    print("*****************************************")
    if not box:
        raise ValueError("Unable to retrieve bounding box.")

    # Target is the center of the element
    target_x = box['x'] + box['width'] / 2
    target_y = box['y'] + box['height'] / 2

    # Start at (0, 0) for simplicity (Playwright doesn't track current mouse position)
    start_x, start_y = 0, 0

    if steps is None:
        steps = random.randint(30, 80)

    # Randomly choose movement type
    use_curve = random.choice([True, False])

    if use_curve:
        await _move_mouse_curve(page, start_x, start_y, target_x, target_y, steps)
    else:
        await _move_mouse_straight(page, start_x, start_y, target_x, target_y, steps)

    # Optionally click
    await asyncio.sleep(random.uniform(0.1, 0.3))
    # await page.mouse.click(target_x, target_y)

async def _move_mouse_curve(page, x1, y1, x2, y2, steps):
    """
    move the mouse cursor from (x1, y1) to (x2, y2) using a 
    curved, human-like trajectory. the motion simulates a 
    bezier-like arc based on sinusoidal offsets, giving a 
    natural imperfection in the path.

    this technique adds randomness to the movement to avoid 
    detection by anti-bot mechanisms. each intermediate point 
    is visited with a small delay to simulate human hand motion.

    :param page: the Playwright page instance to operate on
    :type page: playwright.async_api.Page
    :param x1: starting x-coordinate of the mouse
    :type x1: float
    :param y1: starting y-coordinate of the mouse
    :type y1: float
    :param x2: target x-coordinate of the mouse
    :type x2: float
    :param y2: target y-coordinate of the mouse
    :type y2: float
    :param steps: number of intermediate steps in the path
    :type steps: int
    """
    radius = random.uniform(0.3, 0.7)
    angle = math.atan2(y2 - y1, x2 - x1)

    for i in range(steps):
        t = i / steps
        # Create a Bezier-like arc using sinusoidal offset
        offset = math.sin(t * math.pi) * radius * 100
        dx = (x2 - x1) * t
        dy = (y2 - y1) * t
        cx = x1 + dx + offset * math.cos(angle + math.pi / 2)
        cy = y1 + dy + offset * math.sin(angle + math.pi / 2)

        await page.mouse.move(cx, cy)
        await asyncio.sleep(random.uniform(0.004, 0.02))

async def _move_mouse_straight(page, x1, y1, x2, y2, steps):
    """
    move the mouse cursor from (x1, y1) to (x2, y2) in a 
    straight-line path. the motion is divided into evenly 
    spaced steps to approximate continuous human motion.

    short random delays between movements are added to 
    mimic human hand movement. this method is simpler 
    than the curved path, and appears more mechanical, 
    but still more natural than a direct jump.

    :param page: the Playwright page instance to operate on
    :type page: playwright.async_api.Page
    :param x1: starting x-coordinate of the mouse
    :type x1: float
    :param y1: starting y-coordinate of the mouse
    :type y1: float
    :param x2: target x-coordinate of the mouse
    :type x2: float
    :param y2: target y-coordinate of the mouse
    :type y2: float
    :param steps: number of intermediate steps in the path
    :type steps: int
    """
    for i in range(steps):
        t = i / steps
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        await page.mouse.move(x, y)
        await asyncio.sleep(random.uniform(0.004, 0.02))

async def accept_cookies_if_present(page):
    # Try common button texts and selectors
    selectors = [
        "button:has-text('Accept')",
        "button:has-text('Accept all')",
        "button:has-text('I agree')",
        "text='Accepter et continuer'",
        "text='Accept Cookies'",
        "text='Got it'",
        "[id*='cookie'][id*='accept']",
        "[class*='cookie'][class*='accept']",
    ]

    for selector in selectors:
        try:
            button = await page.query_selector(selector)
            if button:
                await button.click()
                print(f"[✓] Clicked cookie accept button with selector: {selector}")
                break
        except Exception as e:
            continue

async def move_mouse_to_button_and_click(page: Page, button_text: str = "Accepter et continuer", steps_range=(30, 80)):
    """
    move the mouse cursor in a human-like manner toward a 
    button containing the specified text and perform a click. 
    the button is identified by its visible label, and the 
    motion includes randomized interpolation and noise to 
    simulate realistic user behavior.

    the mouse movement begins from a random point located 
    above and to the left of the button and progresses 
    through a series of intermediate positions before 
    clicking the center of the button.

    :param page: the Playwright page instance to operate on
    :type page: playwright.async_api.Page
    :param button_text: the exact visible text of the button 
    to click; defaults to "Accepter et continuer"
    :type button_text: str
    :param steps_range: a tuple indicating the range of steps 
    used in the interpolated mouse movement; the actual 
    number is randomly chosen within this range
    :type steps_range: tuple[int, int]
    """
    # Find the button with exact text
    locator = page.locator(f"button:has-text('{button_text}')")
    if not await locator.is_visible():
        raise Exception(f"Button with text '{button_text}' not found or not visible")

    box = await locator.bounding_box()
    if not box:
        raise Exception("Could not determine bounding box of button")

    # Center of the button
    target_x = box["x"] + box["width"] / 2
    target_y = box["y"] + box["height"] / 2

    # Get current mouse position
    # NOTE: Playwright does not expose current mouse position, so we start from a random point
    current_x = random.randint(0, int(box["x"]))
    current_y = random.randint(0, int(box["y"]))
    await page.mouse.move(current_x, current_y)

    # Simulate human-like movement
    steps = random.randint(*steps_range)
    for i in range(steps):
        t = i / steps
        # Linear interpolation
        intermediate_x = current_x + t * (target_x - current_x)
        intermediate_y = current_y + t * (target_y - current_y)

        # Slight randomness to make it more human
        intermediate_x += random.uniform(-1, 1)
        intermediate_y += random.uniform(-1, 1)

        await page.mouse.move(intermediate_x, intermediate_y)

    # Final move to center
    await page.mouse.move(target_x, target_y)

    # Click the button
    await locator.click()



async def accept_cookies(page):
    try:
        # Wait up to 5 seconds for the button with the exact label text to appear
        await page.wait_for_selector('button:has-text("Accepter et continuer")', timeout=5000)
        await page.click('button:has-text("Accepter et continuer")')
        print("Cookies accepted.")
        await asyncio.sleep(1)  # Give some time for UI to settle after click
    except TimeoutError:
        # Button didn't appear within timeout — maybe cookies already accepted or not present
        print("No cookie consent button found, or already accepted.")
