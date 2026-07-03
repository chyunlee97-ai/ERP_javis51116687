import sys
import os
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt
from PySide6.QtNetwork import QLocalServer, QLocalSocket

# Ensure import paths include local folders
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ui.main_window import MainWindow

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
    
    # Initialize main window
    window = MainWindow()
    
    # 중복 실행 신호가 올 경우 기존 창 활성화
    def handle_new_connection():
        client_socket = local_server.nextPendingConnection()
        if client_socket:
            if client_socket.waitForReadyRead(1000):
                msg = client_socket.readAll().data().decode("utf-8")
                if msg == "SHOW":
                    window.restore_from_tray()
            client_socket.disconnectFromServer()
            
    local_server.newConnection.connect(handle_new_connection)
    
    # Position the window in the bottom right corner of the desktop
    screen = app.primaryScreen().geometry()
    window_geom = window.geometry()
    x = screen.width() - window_geom.width() - 50
    y = screen.height() - window_geom.height() - 100
    window.move(x, y)
    window.show()
    window.raise_()
    window.activateWindow()
    
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
        # Fallback to programmatically drawing a beautiful red circle icon
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
        if window.isVisible():
            window.minimize_to_tray()
        else:
            window.restore_from_tray()
            
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
