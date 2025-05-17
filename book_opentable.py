from playwright.sync_api import sync_playwright
import time
from datetime import datetime
import re

def book_reservation(data: dict) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)  # Set headless=True when ready
        page = browser.new_page()

        try:
            # 1. Go to OpenTable
            page.goto("https://www.opentable.com/")
            time.sleep(2)

            # 2. Search for restaurant
            print(f"🔍 Searching for: {data['restaurant']}")
            page.locator('input[placeholder="Location, Restaurant, or Cuisine"]').fill(data["restaurant"])
            page.keyboard.press("Enter")

            # 3. Wait for results to load
            page.wait_for_selector('a[data-test="es-card-name"]', timeout=10000)
            page.screenshot(path="search_results.png", full_page=True)

            # 4. Click the matching restaurant
            page.locator('a[data-test="es-card-name"]', has_text=data["restaurant"]).first.click()

             # 5. Set date
            date_obj = datetime.strptime(data["date"], "%Y-%m-%d")
            formatted_date = date_obj.strftime("%B %-d, %Y")  # Example: "May 17, 2025"
            page.locator('button[data-test="date-button"]').click()
            page.locator(f'td[aria-label="{formatted_date}"]').click()
            time.sleep(1)

            # 6. Set time
            page.locator('button[data-test="time-button"]').click()
            time_text = datetime.strptime(data["time"], "%H:%M").strftime("%-I:%M %p")  # "7:00 PM"
            page.locator(f'ul[role="listbox"] >> text="{time_text}"').click()
            time.sleep(1)

            # 7. Click Find Table
            page.locator('button[data-test="find-table-button"]').click()
            page.wait_for_load_state("networkidle")
            time.sleep(3)

            # 8. Click available reservation time
            time_buttons = page.locator('button >> text="' + time_text + '"')
            if time_buttons.count() > 0:
                time_buttons.first.click()
                time.sleep(2)
            else:
                browser.close()
                return {"success": False, "error": f"No available time slots for {time_text}"}

            # 9. Optional: fill in guest email/phone if prompted
            if "email" in data:
                email_field = page.locator('input[type="email"]')
                if email_field.count() > 0:
                    email_field.first.fill(data["email"])
                    time.sleep(1)

            if "phone" in data:
                phone_field = page.locator('input[type="tel"]')
                if phone_field.count() > 0:
                    # Remove any formatting just in case
                    digits_only = re.sub(r"\D", "", data["phone"])
                    phone_field.first.fill(digits_only)
                    time.sleep(1)

            # 10. Stop here for MVP - simulate success
            # Optionally, click page.locator('button >> text="Complete Reservation"').click()

            browser.close()
            return {"success": True, "message": f"Reservation flow completed for {data['restaurant']} at {time_text}"}

        except Exception as e:
            browser.close()
            return {"success": False, "error": str(e)}
