"""
Dialog for editing reports before saving
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTextEdit, QLabel, QTabWidget, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from typing import Dict, List

# Constants
BULLET_AND_NUMBER_CHARS = '•-*) '  # Characters to strip for bullet formatting (excluding digits to preserve content)


class ReportEditorDialog(QDialog):
    """Dialog para editar informes antes de guardarlos"""
    
    def __init__(self, evaluation: Dict[str, List[str]], parent=None):
        super().__init__(parent)
        self.evaluation = evaluation.copy()
        self.modified = False
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz del diálogo"""
        self.setWindowTitle("Edit Reports - Manual Verification")
        self.setGeometry(150, 150, 900, 700)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Título y descripción
        title_label = QLabel("Review and Edit Report Content")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        desc_label = QLabel("Edit the evaluation content below. Changes will be reflected in both Author and Auditor reports.")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: gray; margin-bottom: 10px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Tabs para cada sección
        tabs = QTabWidget()
        
        # Crear editores para cada sección
        self.editors = {}
        sections = {
            'major': 'Major Points (Critical issues)',
            'minor': 'Minor Points (Improvements)',
            'other': 'Other Points (Observations)',
            'suggestions': 'Suggestions for Improvement'
        }
        
        for key, title in sections.items():
            tab = QWidget()
            tab_layout = QVBoxLayout()
            
            info = QLabel(f"Edit {title.split('(')[0].strip()}")
            info.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
            tab_layout.addWidget(info)
            
            editor = QTextEdit()
            editor.setFont(QFont("Arial", 10))
            
            # Cargar contenido actual (uno por línea)
            content = '\n'.join(f"• {point}" for point in self.evaluation.get(key, []))
            editor.setPlainText(content)
            
            tab_layout.addWidget(editor)
            tab.setLayout(tab_layout)
            
            tabs.addTab(tab, title.split('(')[0].strip())
            self.editors[key] = editor
        
        layout.addWidget(tabs)
        
        # Botones
        button_layout = QHBoxLayout()
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)
        
        btn_reset = QPushButton("Reset All")
        btn_reset.clicked.connect(self.reset_content)
        btn_reset.setToolTip("Restore original content")
        button_layout.addWidget(btn_reset)
        
        btn_save = QPushButton("Save and Continue")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        btn_save.clicked.connect(self.save_and_accept)
        button_layout.addWidget(btn_save)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def save_and_accept(self):
        """Guarda los cambios y cierra el diálogo"""
        # Parsear el contenido de cada editor
        for key, editor in self.editors.items():
            text = editor.toPlainText()
            lines = text.strip().split('\n')
            
            # Limpiar y extraer puntos
            points = []
            for line in lines:
                line = line.strip()
                
                # Remover bullets y numeración al inicio de línea usando regex
                # Patrón: números opcionales seguidos de punto/paréntesis, espacios, y bullets
                import re
                line = re.sub(r'^[\d]+[.)]\s*', '', line)  # Remove "1. " or "1) "
                line = line.lstrip(BULLET_AND_NUMBER_CHARS)  # Remove bullets
                
                if line:
                    points.append(line)
            
            self.evaluation[key] = points
        
        self.modified = True
        self.accept()
    
    def reset_content(self):
        """Restaura el contenido original"""
        reply = QMessageBox.question(
            self,
            "Reset Content",
            "Are you sure you want to reset all sections to their original content?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Recargar contenido original
            for key, editor in self.editors.items():
                content = '\n'.join(f"• {point}" for point in self.evaluation.get(key, []))
                editor.setPlainText(content)
    
    def get_evaluation(self) -> Dict[str, List[str]]:
        """Retorna la evaluación editada"""
        return self.evaluation
    
    def was_modified(self) -> bool:
        """Retorna si el contenido fue modificado"""
        return self.modified
