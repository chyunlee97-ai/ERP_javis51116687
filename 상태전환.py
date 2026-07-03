from PySide6.QtGui import QPixmap

# 상태 전환 예시
IMAGES = {
    "idle":     QPixmap("character_idle.png"),
    "thinking": QPixmap("character_thinking.png"),
    "talking":  QPixmap("character_talking.png"),
}

def set_state(self, state: str):
    self.char_label.setPixmap(IMAGES[state])