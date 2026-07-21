import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPlainTextEdit, QFrame

class AdminPanelsWidget(QWidget):
    def __init__(self, parent=None, project_root=""):
        super().__init__(parent)
        self.project_root = project_root
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # 1. Factory Selection Panel (추가 1번창)
        self.fact_frame = QFrame(self)
        self.fact_frame.setObjectName("FactFrame")
        self.fact_frame.setStyleSheet("""
            QFrame#FactFrame {
                background-color: #1e1e1e;
                border: 2px solid #D32F2F;
                border-radius: 12px;
            }
        """)
        fact_layout = QHBoxLayout(self.fact_frame)
        fact_layout.setContentsMargins(15, 10, 15, 10)
        
        lbl_title = QLabel("🔧 [관리자] 기본 공장 설정 (fallback @fact):", self.fact_frame)
        lbl_title.setStyleSheet("color: #FFCDD2; font-weight: bold; font-size: 12px;")
        
        self.cb_fact = QComboBox(self.fact_frame)
        self.cb_fact.setStyleSheet("""
            QComboBox {
                border: 1px solid #D32F2F;
                border-radius: 6px;
                padding: 4px 10px;
                background-color: #2b2b2b;
                color: #ffffff;
                font-size: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #2b2b2b;
                color: #ffffff;
                selection-background-color: #D32F2F;
            }
        """)
        
        fact_layout.addWidget(lbl_title)
        fact_layout.addWidget(self.cb_fact, 1)
        
        layout.addWidget(self.fact_frame)
        
        # 2. SQL Script Viewer Panel (추가 2번창)
        self.sql_frame = QFrame(self)
        self.sql_frame.setObjectName("SqlFrame")
        self.sql_frame.setStyleSheet("""
            QFrame#SqlFrame {
                background-color: #1e1e1e;
                border: 2px solid #D32F2F;
                border-radius: 12px;
            }
        """)
        sql_layout = QVBoxLayout(self.sql_frame)
        sql_layout.setContentsMargins(15, 10, 15, 10)
        sql_layout.setSpacing(6)
        
        lbl_sql_title = QLabel("📝 [관리자] 실행된 SQL 스크립트:", self.sql_frame)
        lbl_sql_title.setStyleSheet("color: #FFCDD2; font-weight: bold; font-size: 12px;")
        
        self.txt_sql = QPlainTextEdit(self.sql_frame)
        self.txt_sql.setReadOnly(True)
        self.txt_sql.setStyleSheet("""
            QPlainTextEdit {
                background-color: #2b2b2b;
                color: #00ff00;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                border: 1px solid #555555;
                border-radius: 6px;
            }
        """)
        self.txt_sql.setPlaceholderText("질문을 입력하여 쿼리가 실행되면 여기에 생성된 SQL 스크립트가 표시됩니다.")
        self.txt_sql.setMinimumHeight(200)
        
        sql_layout.addWidget(lbl_sql_title)
        sql_layout.addWidget(self.txt_sql)
        
        layout.addWidget(self.sql_frame)
        
        # Load factories
        self.load_factories()
        
    def load_factories(self):
        md_path = os.path.join(self.project_root, "[자연어로 공장 구분 기준].md")
        factories = []
        if os.path.exists(md_path):
            try:
                with open(md_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line.startswith("|"):
                            continue
                        cols = [c.strip() for c in line.split("|")][1:-1]
                        if not cols or cols[0] == "code_fact" or cols[0].startswith("---"):
                            continue
                        code = cols[0]
                        name1 = cols[1] if len(cols) > 1 else ""
                        name2 = cols[2] if len(cols) > 2 else ""
                        
                        label = f"{code}"
                        if name1:
                            label += f" ({name1}"
                            if name2:
                                label += f"/{name2}"
                            label += ")"
                        factories.append((code, label))
            except Exception as e:
                print(f"Error parsing factories in admin panel: {e}")
                
        if not factories:
            factories = [("K1", "K1 (김해/김해공장)")]
            
        for code, label in factories:
            self.cb_fact.addItem(label, code)
            
        # Default select K1 if available
        index = self.cb_fact.findData("K1")
        if index >= 0:
            self.cb_fact.setCurrentIndex(index)
            
    def set_sql_script(self, sql_script, input_text="", intent_found=True):
        if sql_script:
            self.txt_sql.setPlainText(sql_script)
        elif not intent_found:
            msg = "[SQL 생성 없음] 입력된 질문의 의도를 파악하지 못해 SQL이 생성되지 않았습니다."
            if input_text:
                msg += f"\n\n입력 내용: {input_text}"
            self.txt_sql.setPlainText(msg)
        else:
            self.txt_sql.setPlainText("[SQL 없음] SQL 실행 정보가 반환되지 않았습니다.")
