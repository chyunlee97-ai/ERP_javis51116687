import os
from PIL import ImageGrab

screenshot_dir = r"C:\Users\acon97.OSMAIL_SERVER\.gemini\antigravity\brain\2923908c-1f02-4e48-91fa-ce69b91d33d2"
screenshot_path = os.path.join(screenshot_dir, "chatbot_preview_final.png")
img = ImageGrab.grab()
img.save(screenshot_path)
print(f"Screenshot saved to {screenshot_path}")
