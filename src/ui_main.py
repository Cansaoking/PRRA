"""
PRRA main graphical interface
"""
import sys
import os
import json
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QCheckBox,
    QFileDialog, QProgressBar, QTabWidget, QMessageBox, QPlainTextEdit,
    QGroupBox, QSpinBox, QSplitter, QDialog
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
from src.report_editor_dialog import ReportEditorDialog


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación PRRA"""
    
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.prompts = DEFAULT_PROMPTS.copy()
        self.worker = None
        self.output_directory = None  # Custom output directory
        self.imported_articles_file = None  # Path to imported articles file
        
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
        
        # Opción para importar artículos
        import_layout = QHBoxLayout()
        self.import_articles_checkbox = QCheckBox("Import pre-selected articles (skip PubMed search)")
        self.import_articles_checkbox.setToolTip("Load articles from a text file with citations and abstracts")
        self.import_articles_checkbox.stateChanged.connect(self.on_import_articles_changed)
        import_layout.addWidget(self.import_articles_checkbox)
        pubmed_layout.addLayout(import_layout)
        
        self.import_file_label = QLabel("No file selected")
        self.import_file_label.setStyleSheet("padding: 3px; background-color: #f0f0f0; border-radius: 3px; margin-left: 20px;")
        self.import_file_label.setVisible(False)
        pubmed_layout.addWidget(self.import_file_label)
        
        btn_import_layout = QHBoxLayout()
        btn_import_layout.addSpacing(20)
        self.btn_import_file = QPushButton("📄 Load Articles File...")
        self.btn_import_file.clicked.connect(self.load_articles_file)
        self.btn_import_file.setVisible(False)
        btn_import_layout.addWidget(self.btn_import_file)
        btn_import_layout.addStretch()
        pubmed_layout.addLayout(btn_import_layout)
        
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
        
        # Output directory selection
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Output directory:"))
        self.output_dir_label = QLabel("Same as manuscript")
        self.output_dir_label.setStyleSheet("padding: 3px; background-color: #f0f0f0; border-radius: 3px;")
        dir_layout.addWidget(self.output_dir_label)
        
        btn_choose_dir = QPushButton("📁 Choose...")
        btn_choose_dir.clicked.connect(self.choose_output_directory)
        dir_layout.addWidget(btn_choose_dir)
        output_layout.addLayout(dir_layout)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Opciones adicionales
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        
        self.manual_checkbox = QCheckBox("Manual mode (confirm intermediate steps)")
        self.manual_checkbox.setToolTip("Enable to review and confirm each processing step")
        options_layout.addWidget(self.manual_checkbox)
        
        self.edit_reports_checkbox = QCheckBox("Allow manual editing of reports before saving")
        self.edit_reports_checkbox.setToolTip("Enable to review and edit reports before they are saved")
        self.edit_reports_checkbox.setChecked(False)
        options_layout.addWidget(self.edit_reports_checkbox)
        
        self.clean_cache_checkbox = QCheckBox("Clean cache on exit (models, temporary files)")
        self.clean_cache_checkbox.setToolTip("Automatically remove downloaded models and temporary files when closing the application")
        self.clean_cache_checkbox.setChecked(False)
        options_layout.addWidget(self.clean_cache_checkbox)
        
        # Botón de limpieza manual de cache
        cache_button_layout = QHBoxLayout()
        cache_button_layout.addSpacing(20)
        btn_clean_cache = QPushButton("🗑️ Clean Cache Now...")
        btn_clean_cache.setToolTip("Manually clean cache and temporary files without closing the application")
        btn_clean_cache.clicked.connect(self.clean_cache_now)
        cache_button_layout.addWidget(btn_clean_cache)
        
        btn_view_cache = QPushButton("📊 View Cache Info")
        btn_view_cache.setToolTip("View information about current cache usage")
        btn_view_cache.clicked.connect(self.view_cache_info)
        cache_button_layout.addWidget(btn_view_cache)
        cache_button_layout.addStretch()
        options_layout.addLayout(cache_button_layout)
        
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
    
    def choose_output_directory(self):
        """Permite al usuario elegir directorio de salida personalizado"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Choose Output Directory",
            os.path.dirname(self.file_path) if self.file_path else ""
        )
        
        if directory:
            self.output_directory = directory
            self.output_dir_label.setText(f"📁 {os.path.basename(directory)}")
            self.log_message(f"Output directory set to: {directory}")
        else:
            # User cancelled, reset to default
            self.output_directory = None
            self.output_dir_label.setText("Same as manuscript")
    
    def on_import_articles_changed(self, state):
        """Maneja el cambio en el checkbox de importación de artículos"""
        is_checked = state == Qt.Checked
        self.import_file_label.setVisible(is_checked)
        self.btn_import_file.setVisible(is_checked)
        
        if not is_checked:
            self.imported_articles_file = None
            self.import_file_label.setText("No file selected")
    
    def load_articles_file(self):
        """Carga un archivo con artículos pre-seleccionados"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Articles File",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Validar que tiene contenido
                if not content.strip():
                    QMessageBox.warning(self, "Error", "The file is empty")
                    return
                
                # Quick validation: check if it looks like citations
                if not re.search(r'\(\d{4}\)', content):
                    reply = QMessageBox.question(
                        self,
                        "Confirm",
                        "The file doesn't appear to contain citations with years in (YYYY) format.\nDo you want to continue anyway?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return
                
                self.imported_articles_file = file_path
                self.import_file_label.setText(f"📄 {os.path.basename(file_path)}")
                self.log_message(f"Loaded articles file: {file_path}")
                
                # Try to parse and show count
                from src.article_importer import ArticleImporter
                articles = ArticleImporter.parse_citations(content)
                self.log_message(f"✓ Parsed {len(articles)} article(s) from file")
                
                if len(articles) == 0:
                    QMessageBox.warning(
                        self,
                        "Warning",
                        "No articles could be parsed from the file. Please check the format."
                    )
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not read file: {str(e)}")
                self.imported_articles_file = None
    
    def view_cache_info(self):
        """Muestra información sobre el cache actual"""
        try:
            from src.cache_manager import CacheManager
            from pathlib import Path
            
            base_path = Path(__file__).parent.parent
            info = CacheManager.get_cache_info(base_path)
            
            # Construir mensaje con información
            msg = f"Total Cache Size: {info['total_size_str']}\n\n"
            
            if info['model_cache']:
                msg += "AI Models Cache:\n"
                for cache_item in info['model_cache']:
                    msg += f"  • {cache_item['path']}\n    Size: {cache_item['size_str']}\n"
                msg += "\n"
            
            if info['pycache']:
                total_pycache = sum(item['size'] for item in info['pycache'])
                msg += f"Python Cache (__pycache__):\n"
                msg += f"  • {len(info['pycache'])} directories\n"
                msg += f"  • Total size: {CacheManager.format_size(total_pycache)}\n"
            
            if info['total_size'] == 0:
                msg = "No cache files found."
            
            QMessageBox.information(self, "Cache Information", msg)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not retrieve cache info: {str(e)}")
    
    def clean_cache_now(self):
        """Limpia el cache manualmente"""
        try:
            from src.cache_manager import CacheManager
            from pathlib import Path
            
            # Obtener información primero
            base_path = Path(__file__).parent.parent
            info = CacheManager.get_cache_info(base_path)
            
            if info['total_size'] == 0:
                QMessageBox.information(
                    self,
                    "Cache Clean",
                    "No cache files found to clean."
                )
                return
            
            # Confirmar limpieza
            reply = QMessageBox.question(
                self,
                'Confirm Cache Cleaning',
                f'This will remove all cache and temporary files.\n\n'
                f'Current cache size: {info["total_size_str"]}\n\n'
                f'Items to clean:\n'
                f'- AI models (HuggingFace/Torch): {len(info["model_cache"])} directories\n'
                f'- Python cache files: {len(info["pycache"])} directories\n\n'
                f'Warning: Downloaded AI models will need to be re-downloaded.\n\n'
                f'Continue?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Mostrar progreso
                progress = QMessageBox(self)
                progress.setWindowTitle('Cleaning Cache')
                progress.setText('Cleaning cache and temporary files...')
                progress.setStandardButtons(QMessageBox.NoButton)
                progress.show()
                QApplication.processEvents()
                
                # Limpiar cache
                results = CacheManager.clean_cache(
                    clean_models=True,
                    clean_pycache=True,
                    base_path=base_path
                )
                
                progress.close()
                
                # Mostrar resultados
                if results['success'] or len(results['cleaned']) > 0:
                    size_freed = CacheManager.format_size(results['size_freed'])
                    msg = f'Successfully cleaned cache!\n\n'
                    msg += f'Space freed: {size_freed}\n'
                    msg += f'Items cleaned: {len(results["cleaned"])}'
                    
                    if results['errors']:
                        msg += f'\n\nWarnings:\n' + '\n'.join(results['errors'])
                    
                    self.log_message(f"✓ Cache cleaned: {size_freed} freed")
                    QMessageBox.information(self, 'Cache Cleaned', msg)
                else:
                    error_msg = '\n'.join(results['errors'])
                    QMessageBox.warning(
                        self,
                        'Cleanup Failed',
                        f'Could not clean cache:\n\n{error_msg}'
                    )
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error cleaning cache: {str(e)}")
    
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
        
        # Validar que si está marcado importar, tenga un archivo
        if self.import_articles_checkbox.isChecked() and not self.imported_articles_file:
            QMessageBox.warning(self, "Error", "Please load an articles file or uncheck the import option")
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
            output_format=self.output_combo.currentText(),
            output_directory=self.output_directory,
            allow_edit_reports=self.edit_reports_checkbox.isChecked(),
            imported_articles_file=self.imported_articles_file if self.import_articles_checkbox.isChecked() else None
        )
        
        # Conectar señales
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.log_message.connect(self.log_message)
        self.worker.result.connect(self.on_review_complete)
        self.worker.error.connect(self.on_review_error)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.request_report_edit.connect(self.on_report_edit_request)
        
        # Iniciar
        self.worker.start()
        self.log_message("=" * 60)
        self.log_message("Starting automated peer review process...")
        self.log_message("=" * 60)
    
    def on_report_edit_request(self, data: dict):
        """Maneja la solicitud de edición de reportes"""
        self.log_message("📝 Opening report editor for manual verification...")
        
        # Mostrar diálogo de edición
        dialog = ReportEditorDialog(data['evaluation'], self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            if dialog.was_modified():
                self.log_message("✓ Reports modified by user")
            else:
                self.log_message("✓ Reports confirmed without changes")
            
            # Pasar la evaluación editada de vuelta al worker
            self.worker.edited_reports = dialog.get_evaluation()
        else:
            self.log_message("⚠ Report editing cancelled, using original content")
            self.worker.edited_reports = data['evaluation']
        
        # Notificar al worker que la edición está completa
        self.worker.notify_edit_complete()
    
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
    
    def closeEvent(self, event):
        """Maneja el evento de cierre de la aplicación"""
        # Verificar si hay un worker en ejecución
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                'Confirm Exit',
                'A review is currently in progress. Are you sure you want to exit?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
            else:
                # Detener el worker
                self.worker.stop()
                self.worker.wait(2000)  # Esperar máximo 2 segundos
        
        # Limpiar cache si está habilitado
        if self.clean_cache_checkbox.isChecked():
            reply = QMessageBox.question(
                self,
                'Clean Cache',
                'Do you want to clean all cache and temporary files?\n\n'
                'This will remove:\n'
                '- Downloaded AI models (will need to re-download next time)\n'
                '- Python cache files (__pycache__)\n'
                '- Torch/HuggingFace cache\n\n'
                'This may free up several GB of disk space.',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                try:
                    from src.cache_manager import CacheManager
                    from pathlib import Path
                    
                    # Mostrar progreso
                    progress = QMessageBox(self)
                    progress.setWindowTitle('Cleaning Cache')
                    progress.setText('Cleaning cache and temporary files...')
                    progress.setStandardButtons(QMessageBox.NoButton)
                    progress.show()
                    QApplication.processEvents()
                    
                    # Limpiar cache
                    base_path = Path(__file__).parent.parent
                    results = CacheManager.clean_cache(
                        clean_models=True,
                        clean_pycache=True,
                        base_path=base_path
                    )
                    
                    progress.close()
                    
                    # Mostrar resultados
                    if results['success']:
                        size_freed = CacheManager.format_size(results['size_freed'])
                        QMessageBox.information(
                            self,
                            'Cache Cleaned',
                            f'Successfully cleaned cache!\n\n'
                            f'Space freed: {size_freed}\n'
                            f'Items cleaned: {len(results["cleaned"])}'
                        )
                    else:
                        error_msg = '\n'.join(results['errors'])
                        QMessageBox.warning(
                            self,
                            'Partial Cleanup',
                            f'Cache cleaning completed with some errors:\n\n{error_msg}'
                        )
                        
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        'Error',
                        f'Error cleaning cache: {str(e)}'
                    )
        
        # Aceptar el evento de cierre
        event.accept()


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
