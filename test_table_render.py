import sys
import os
from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView
from PySide6.QtCore import QTimer

def run():
    app = QApplication(sys.argv)
    w = QWidget()
    lay = QVBoxLayout(w)
    
    table = QTableWidget()
    table.setFixedHeight(165)
    table.verticalHeader().setDefaultSectionSize(24)
    table.verticalHeader().setVisible(False)
    
    table.setColumnCount(3)
    table.setHorizontalHeaderLabels(["NO.", "Col 1", "Col 2"])
    
    table.setRowCount(2)
    for r in range(2):
        table.setItem(r, 0, QTableWidgetItem(str(r+1)))
        table.setItem(r, 1, QTableWidgetItem("Val 1"))
        table.setItem(r, 2, QTableWidgetItem("Val 2"))
        
    lay.addWidget(table)
    w.resize(400, 300)
    w.show()
    
    def capture():
        w.grab().save("test_table_render.png")
        print("Captured test_table_render.png")
        app.quit()
        
    QTimer.singleShot(1000, capture)
    app.exec()

if __name__ == '__main__':
    run()
