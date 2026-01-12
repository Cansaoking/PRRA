"""
Interfaz gráfica principal de PRRA
"""
import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QCheckBox,
    QFileDialog, QProgressBar, QTabWidget, QMessageBox, QPlainTextEdit,
    QGroupBox, QSpinBox, QSplitter
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon

from src.config import (
    AVAILABLE_MODELS, SUPPORTED_FORMATS, DEFAULT_NUM_KEYPHRASES,
    DEFAULT_NUM_ARTICLES, DEFAULT_OUTPUT_FORMAT, DEFAULT_PROMPTS,
    WINDOW_WIDTH, WINDOW_HEIGHT
)
from src.document_processor import DocumentProcessor
from src.worker import WorkerThread


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación PRRA"""
    
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.prompts = DEFAULT_PROMPTS.copy()
        self.worker = None
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("PRRA - Peer Review Automated Application")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Widget central
        central = QWidget()
        main_layout = QVBoxLayout()
        
        # Título y descripción
        title_label = QLabel("PRRA - Automated Peer Review System")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        desc_label = QLabel("Automated scientific manuscript evaluation using AI and PubMed reference data")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: gray; margin-bottom: 10px;")
        main_layout.addWidget(desc_label)
        
        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self.create_input_tab(), "📄 Manuscript")
        tabs.addTab(self.create_config_tab(), "⚙️ Configuration")
        tabs.addTab(self.create_prompts_tab(), "💬 Prompts")
        tabs.addTab(self.create_progress_tab(), "📊 Progress")
        
        main_layout.addWidget(tabs)
        
        # Botones de control
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ Start Review")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.start_btn.clicked.connect(self.start_review)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_review)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        
        main_layout.addLayout(button_layout)
        
        central.setLayout(main_layout)
        self.setCentralWidget(central)
    
    def create_input_tab(self) -> QWidget:
        """Crea la pestaña de entrada de manuscrito"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Grupo de selección de archivo
        file_group = QGroupBox("Manuscript Selection")
        file_layout = QVBoxLayout()
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 3px;")
        file_layout.addWidget(self.file_label)
        
        btn_open = QPushButton("📂 Open Manuscript")
        btn_open.clicked.connect(self.open_file)
        file_layout.addWidget(btn_open)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Grupo de vista previa
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("File content will appear here...")
        preview_layout.addWidget(self.preview)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_config_tab(self) -> QWidget:
        """Crea la pestaña de configuración"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Grupo de extracción
        extraction_group = QGroupBox("Key Phrase Extraction")
        extraction_layout = QVBoxLayout()
        
        kp_layout = QHBoxLayout()
        kp_layout.addWidget(QLabel("Number of key phrases:"))
        self.num_keys_spin = QSpinBox()
        self.num_keys_spin.setMinimum(3)
        self.num_keys_spin.setMaximum(10)
        self.num_keys_spin.setValue(DEFAULT_NUM_KEYPHRASES)
        kp_layout.addWidget(self.num_keys_spin)
        kp_layout.addStretch()
        extraction_layout.addLayout(kp_layout)
        
        extraction_group.setLayout(extraction_layout)
        layout.addWidget(extraction_group)
        
        # Grupo de PubMed
        pubmed_group = QGroupBox("PubMed Search")
        pubmed_layout = QVBoxLayout()
        
        art_layout = QHBoxLayout()
        art_layout.addWidget(QLabel("Articles per search:"))
        self.num_articles_spin = QSpinBox()
        self.num_articles_spin.setMinimum(5)
        self.num_articles_spin.setMaximum(50)
        self.num_articles_spin.setValue(DEFAULT_NUM_ARTICLES)
        art_layout.addWidget(self.num_articles_spin)
        art_layout.addStretch()
        pubmed_layout.addLayout(art_layout)
        
        pubmed_group.setLayout(pubmed_layout)
        layout.addWidget(pubmed_group)
        
        # Grupo de modelo IA
        ai_group = QGroupBox("AI Model")
        ai_layout = QVBoxLayout()
        
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(AVAILABLE_MODELS)
        model_layout.addWidget(self.model_combo)
        ai_layout.addLayout(model_layout)
        
        # Información sobre CUDA
        import torch
        cuda_available = torch.cuda.is_available()
        cuda_label = QLabel(f"GPU (CUDA): {'✓ Available' if cuda_available else '✗ Not available (CPU mode)'}")
        cuda_label.setStyleSheet(f"color: {'green' if cuda_available else 'orange'}; font-style: italic;")
        ai_layout.addWidget(cuda_label)
        
        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)
        
        # Grupo de salida
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout()
        
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Report format:"))
        self.output_combo = QComboBox()
        self.output_combo.addItems(["pdf", "docx"])
        self.output_combo.setCurrentText(DEFAULT_OUTPUT_FORMAT)
        format_layout.addWidget(self.output_combo)
        format_layout.addStretch()
        output_layout.addLayout(format_layout)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Opciones adicionales
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        
        self.manual_checkbox = QCheckBox("Manual mode (confirm intermediate steps)")
        self.manual_checkbox.setToolTip("Enable to review and confirm each processing step")
        options_layout.addWidget(self.manual_checkbox)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_prompts_tab(self) -> QWidget:
        """Crea la pestaña de edición de prompts"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        info_label = QLabel("Edit AI prompts (JSON format). Use {num}, {text}, {abstracts}, {type} as placeholders.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 5px; background-color: #f9f9f9; border-radius: 3px;")
        layout.addWidget(info_label)
        
        self.prompt_editor = QPlainTextEdit()
        self.prompt_editor.setPlainText(json.dumps(self.prompts, indent=4))
        self.prompt_editor.setFont(QFont("Courier", 10))
        layout.addWidget(self.prompt_editor)
        
        # Botones
        button_layout = QHBoxLayout()
        
        btn_reset = QPushButton("Reset to Default")
        btn_reset.clicked.connect(self.reset_prompts)
        button_layout.addWidget(btn_reset)
        
        btn_save = QPushButton("💾 Save to File")
        btn_save.clicked.connect(self.save_prompts)
        button_layout.addWidget(btn_save)
        
        btn_load = QPushButton("📂 Load from File")
        btn_load.clicked.connect(self.load_prompts)
        button_layout.addWidget(btn_load)
        
        layout.addLayout(button_layout)
        
        tab.setLayout(layout)
        return tab
    
    def create_progress_tab(self) -> QWidget:
        """Crea la pestaña de progreso"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #28a745;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Log de mensajes
        log_label = QLabel("Processing Log:")
        log_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 9))
        layout.addWidget(self.log_text)
        
        # Botón para limpiar log
        btn_clear_log = QPushButton("Clear Log")
        btn_clear_log.clicked.connect(lambda: self.log_text.clear())
        layout.addWidget(btn_clear_log)
        
        tab.setLayout(layout)
        return tab
    
    def open_file(self):
        """Abre un archivo de manuscrito"""
        # Construir filtro de archivos
        file_filter = "All Supported (*.pdf *.docx *.doc *.rtf *.txt);;PDF (*.pdf);;Word (*.docx *.doc);;RTF (*.rtf);;Text (*.txt)"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Manuscript",
            "",
            file_filter
        )
        
        if file_path:
            self.file_path = file_path
            self.file_label.setText(f"📄 {os.path.basename(file_path)}")
            
            # Vista previa
            try:
                doc_processor = DocumentProcessor()
                text = doc_processor.extract_text(file_path)
                preview = doc_processor.get_text_preview(text, 2000)
                self.preview.setText(preview)
                
                # Log
                self.log_message(f"Loaded file: {file_path}")
                self.log_message(f"File size: {len(text)} characters")
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not read file: {str(e)}")
                self.file_path = None
    
    def save_prompts(self):
        """Guarda prompts a archivo JSON"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Prompts",
            "prompts.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                prompts = json.loads(self.prompt_editor.toPlainText())
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(prompts, f, indent=4)
                QMessageBox.information(self, "Success", "Prompts saved successfully")
            except json.JSONDecodeError:
                QMessageBox.warning(self, "Error", "Invalid JSON format")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not save file: {str(e)}")
    
    def load_prompts(self):
        """Carga prompts desde archivo JSON"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Prompts",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    prompts = json.load(f)
                self.prompts = prompts
                self.prompt_editor.setPlainText(json.dumps(prompts, indent=4))
                QMessageBox.information(self, "Success", "Prompts loaded successfully")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not load file: {str(e)}")
    
    def reset_prompts(self):
        """Resetea prompts a valores por defecto"""
        self.prompts = DEFAULT_PROMPTS.copy()
        self.prompt_editor.setPlainText(json.dumps(self.prompts, indent=4))
        QMessageBox.information(self, "Success", "Prompts reset to default")
    
    def start_review(self):
        """Inicia el proceso de revisión"""
        # Validaciones
        if not self.file_path:
            QMessageBox.warning(self, "Error", "Please select a manuscript file first")
            return
        
        # Validar prompts
        try:
            self.prompts = json.loads(self.prompt_editor.toPlainText())
            if 'keyphrases' not in self.prompts or 'analysis' not in self.prompts:
                raise ValueError("Prompts must contain 'keyphrases' and 'analysis' keys")
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Error", "Invalid JSON format in prompts")
            return
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            return
        
        # Limpiar log y progreso
        self.log_text.clear()
        self.progress_bar.setValue(0)
        
        # Deshabilitar botón de inicio
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Crear y iniciar worker
        self.worker = WorkerThread(
            file_path=self.file_path,
            num_keyphrases=self.num_keys_spin.value(),
            num_articles=self.num_articles_spin.value(),
            model_name=self.model_combo.currentText(),
            prompts=self.prompts,
            manual_mode=self.manual_checkbox.isChecked(),
            output_format=self.output_combo.currentText()
        )
        
        # Conectar señales
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.log_message.connect(self.log_message)
        self.worker.result.connect(self.on_review_complete)
        self.worker.error.connect(self.on_review_error)
        self.worker.finished.connect(self.on_worker_finished)
        
        # Iniciar
        self.worker.start()
        self.log_message("=" * 60)
        self.log_message("Starting automated peer review process...")
        self.log_message("=" * 60)
    
    def stop_review(self):
        """Detiene el proceso de revisión"""
        if self.worker and self.worker.isRunning():
            self.log_message("⏹ Stopping process...")
            self.worker.stop()
            self.worker.wait()
    
    def on_review_complete(self, result: dict):
        """Maneja la finalización exitosa de la revisión"""
        self.log_message("=" * 60)
        self.log_message("REVIEW SUMMARY")
        self.log_message("=" * 60)
        self.log_message(f"Article type: {result.get('article_type', 'Unknown')}")
        self.log_message(f"Key phrases extracted: {len(result.get('keyphrases', []))}")
        self.log_message(f"PubMed articles found: {result.get('total_articles', 0)}")
        self.log_message(f"Author report: {result.get('author_report', 'N/A')}")
        self.log_message(f"Auditor report: {result.get('auditor_report', 'N/A')}")
        self.log_message("=" * 60)
        
        QMessageBox.information(
            self,
            "Success",
            f"Review completed successfully!\n\n"
            f"Reports generated:\n"
            f"• {result.get('author_report', 'N/A')}\n"
            f"• {result.get('auditor_report', 'N/A')}"
        )
    
    def on_review_error(self, error_msg: str):
        """Maneja errores durante la revisión"""
        QMessageBox.critical(self, "Error", f"An error occurred:\n\n{error_msg}")
    
    def on_worker_finished(self):
        """Maneja la finalización del worker (éxito o error)"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def log_message(self, message: str):
        """Añade un mensaje al log"""
        self.log_text.append(message)
        # Scroll al final
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


def main():
    """Función principal"""
    app = QApplication(sys.argv)
    
    # Estilo de la aplicación
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
