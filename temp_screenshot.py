import os
from PIL import ImageGrab

screenshot_dir = r"C:\Users\acon97.OSMAIL_SERVER\.gemini\antigravity\brain\0687c67d-d1cf-4e81-90cf-6ed2e39f81b6"
screenshot_path = os.path.join(screenshot_dir, "temp_ui_preview.png")
img = ImageGrab.grab()
img.save(screenshot_path)
print(f"Screenshot saved to {screenshot_path}")
