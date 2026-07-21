import sys
import os
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt
from PySide6.QtNetwork import QLocalServer, QLocalSocket

# Ensure import paths include local folders
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ui.main_window import MainWindow
from ui.login_window import LoginWindow

def main():
    app = QApplication(sys.argv)
    
    # 중복 실행 방지 (QLocalServer/QLocalSocket 기반 창 복원)
    socket_name = "OHSUNG_Chatbot_SingleInstance_Socket"
    
    # 이미 실행 중인 서버 소켓에 접속을 시도
    socket = QLocalSocket()
    socket.connectToServer(socket_name)
    if socket.waitForConnected(200):
        # 연결 성공 시 기존 프로세스에 "SHOW" 신호를 전송하고 현재 인스턴스는 종료
        socket.write(b"SHOW")
        socket.waitForBytesWritten(1000)
        sys.exit(0)
        
    # 기존 서버가 없으므로 로컬 서버를 생성하고 수신 대기
    local_server = QLocalServer()
    local_server.removeServer(socket_name) # 소켓 찌꺼기 파일 정리
    local_server.listen(socket_name)

    app.setQuitOnLastWindowClosed(False)
    
    # Containers to reference dynamically
    app_state = {
        "login_window": None,
        "main_window": None
    }
    
    # 중복 실행 신호가 올 경우 기존 창 활성화
    def handle_new_connection():
        client_socket = local_server.nextPendingConnection()
        if client_socket:
            if client_socket.waitForReadyRead(1000):
                msg = client_socket.readAll().data().decode("utf-8")
                if msg == "SHOW":
                    if app_state["main_window"]:
                        app_state["main_window"].restore_from_tray()
                    elif app_state["login_window"]:
                        app_state["login_window"].show()
                        app_state["login_window"].raise_()
                        app_state["login_window"].activateWindow()
            client_socket.disconnectFromServer()
            
    local_server.newConnection.connect(handle_new_connection)
    
    login_window = LoginWindow()
    app_state["login_window"] = login_window
    
    # Handle login success
    def handle_login_success(fact, idno, lang):
        # Create and position MainWindow
        main_window = MainWindow(fact=fact, idno=idno, lang=lang)
        app_state["main_window"] = main_window
        
        screen = app.primaryScreen().geometry()
        window_geom = main_window.geometry()
        x = screen.width() - window_geom.width() - 50
        y = screen.height() - window_geom.height() - 100
        main_window.move(x, y)
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
    login_window.login_success.connect(handle_login_success)
    
    # Center the login window on primary screen
    screen_geom = app.primaryScreen().geometry()
    lx = (screen_geom.width() - login_window.width()) // 2
    ly = (screen_geom.height() - login_window.height()) // 2
    login_window.move(lx, ly)
    login_window.show()
    login_window.raise_()
    login_window.activateWindow()
    
    # Setup System Tray Icon
    tray_icon = QSystemTrayIcon(app)
    tray_icon.setToolTip("오성 Bot")
    
    # Try using ohsung_mark.png or other existing images as tray icon
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    icon_names = [
        "image/ohsung_mark_256.png",
        "image/mark_512.png",
        "ohsung_mark.png",
        "ohsung_mark_256.png",
        "mark.png",
        "mark.bmp"
    ]
    icon_loaded = False
    
    for name in icon_names:
        icon_path = os.path.join(project_root, name)
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            tray_icon.setIcon(icon)
            icon_loaded = True
            break
            
    if not icon_loaded:
        from PySide6.QtGui import QPixmap, QPainter, QColor, QBrush
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor("#D32F2F")))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(2, 2, 28, 28)
        painter.end()
        tray_icon.setIcon(QIcon(pixmap))
        
    # Setup Tray Right-Click Menu
    tray_menu = QMenu()
    
    show_action = QAction("보이기 / 숨기기", tray_menu)
    def toggle_window():
        mw = app_state["main_window"]
        lw = app_state["login_window"]
        if mw:
            if mw.isVisible():
                mw.minimize_to_tray()
            else:
                mw.restore_from_tray()
        elif lw:
            if lw.isVisible():
                lw.hide()
            else:
                lw.show()
                lw.raise_()
                lw.activateWindow()
                
    show_action.triggered.connect(toggle_window)
    tray_menu.addAction(show_action)
    
    # Exit action
    exit_action = QAction("종료", tray_menu)
    exit_action.triggered.connect(app.quit)
    tray_menu.addAction(exit_action)
    
    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()
    
    # Connect double click on tray icon to toggle visibility
    tray_icon.activated.connect(
        lambda reason: toggle_window() if reason == QSystemTrayIcon.Trigger else None
    )
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
