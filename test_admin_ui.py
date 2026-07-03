import sys
import os
import time
import subprocess
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

sys.path.append(r"c:\project\ERP_javis\client")
sys.path.append(r"c:\project\ERP_javis")

from ui.main_window import MainWindow

def run_test():
    # Force SHOW_DEVELOPER_PANELS=True for testing
    import config
    config.SHOW_DEVELOPER_PANELS = True
    
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Wait for layout to settle
    window.show()
    window.raise_()
    window.activateWindow()
    app.processEvents()
    time.sleep(1)
    
    # Take screenshot
    pixmap = window.grab()
    pixmap.save("admin_panels_test.png")
    print("Screenshot saved to admin_panels_test.png")
    
    # Close
    window.close()
    app.quit()

if __name__ == "__main__":
    run_test()
