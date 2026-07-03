import sys
import os
import time
import subprocess
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, Qt

# Ensure import paths include client and server folders
sys.path.append(r"c:\project\ERP_javis\client")
sys.path.append(r"c:\project\ERP_javis")

from ui.main_window import MainWindow

def run_gui_test():
    # 1. Kill any existing server/client processes to ensure port 8001 is clean
    print("Terminating existing server/client processes...")
    subprocess.run(["powershell", "-Command", "$p = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue; if ($p) { Stop-Process -Id $p.OwningProcess -Force -ErrorAction SilentlyContinue }"], capture_output=True)
    subprocess.run(["powershell", "-Command", "Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*server\\main.py*' -or $_.CommandLine -like '*client\\main.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"], capture_output=True)
    time.sleep(1)
    
    # 2. Start the FastAPI server in background (force Mock Mode)
    print("Starting API server in Mock Mode...")
    project_root = r"c:\project\ERP_javis"
    python_exe = os.path.join(project_root, ".venv", "Scripts", "python.exe")
    env = os.environ.copy()
    env["DB_SERVER"] = ""
    server_process = subprocess.Popen([python_exe, "server/main.py"], cwd=project_root, env=env)
    time.sleep(3) # Wait for server to bind to port 8001
    
    # 3. Initialize QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(400, 600)
    window.show()
    window.raise_()
    window.activateWindow()
    
    screenshot_dir = r"C:\Users\acon97.OSMAIL_SERVER\.gemini\antigravity\brain\2923908c-1f02-4e48-91fa-ce69b91d33d2"
    
    # We will orchestrate the test using a state machine via QTimer
    state = 0
    
    def next_step():
        nonlocal state
        if state == 0:
            print("Step 1: Testing Conditional Search Mode...")
            # Switch to Tab 1 (Selective Mode / 조건 선택)
            window.tab_widget.setCurrentIndex(1)
            # Select "📞 6. 내선번호 조회"
            window.cb_sql_list.setCurrentIndex(5)
            # Enter search keyword
            window.input_field_sel.setText("이민준")
            # Click send button
            window.btn_send_sel.click()
            
            # Wait 3 seconds for search to finish, then capture screenshot
            QTimer.singleShot(3000, next_step)
            state = 1
            
        elif state == 1:
            print("Step 1: Capturing Selective Mode screenshot...")
            p1 = os.path.join(screenshot_dir, "test_phone_selective.png")
            window.grab().save(p1)
            print(f"Saved: {p1}")
            
            # Switch back to General (Natural Language) Mode
            print("Step 2: Testing Natural Language Mode...")
            window.tab_widget.setCurrentIndex(0)
            window.input_field_gen.setText("Y6 공장 곽상기 내선번호 조회")
            window.btn_send_gen.click()
            
            # Wait 3 seconds for search to finish, then capture screenshot
            QTimer.singleShot(3000, next_step)
            state = 2
            
        elif state == 2:
            print("Step 2: Capturing Natural Language Mode screenshot...")
            p2 = os.path.join(screenshot_dir, "test_phone_natural.png")
            window.grab().save(p2)
            print(f"Saved: {p2}")
            
            # Done! Exit QApplication
            print("Exiting application...")
            app.quit()
            
    # Trigger first step after 1 second
    QTimer.singleShot(1000, next_step)
    
    # Start QApplication event loop
    app.exec()
    
    # Terminate the server
    print("Terminating server...")
    server_process.terminate()
    try:
        server_process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        server_process.kill()
        
    print("Cleanup done!")

if __name__ == "__main__":
    run_gui_test()
