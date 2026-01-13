"""
Worker thread for background processing
"""
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
from typing import Dict, Optional
import traceback
import os

from src.document_processor import DocumentProcessor
from src.ai_analyzer import AIAnalyzer
from src.pubmed_searcher import PubMedSearcher
from src.report_generator import ReportGenerator

# Constants
MAX_EDIT_TIMEOUT_SECONDS = 600  # 10 minutes maximum wait for user editing


class WorkerThread(QThread):
    """Thread de trabajo para procesamiento asíncrono"""
    
    # Señales
    progress = pyqtSignal(int)
    log_message = pyqtSignal(str)
    result = pyqtSignal(dict)
    error = pyqtSignal(str)
    request_confirmation = pyqtSignal(str, dict)  # Para modo manual
    request_report_edit = pyqtSignal(dict)  # Para edición de reportes
    
    def __init__(
        self,
        file_path: str,
        num_keyphrases: int,
        num_articles: int,
        model_name: str,
        prompts: Dict[str, str],
        manual_mode: bool,
        output_format: str,
        output_directory: Optional[str] = None,
        allow_edit_reports: bool = False
    ):
        super().__init__()
        self.file_path = file_path
        self.num_keyphrases = num_keyphrases
        self.num_articles = num_articles
        self.model_name = model_name
        self.prompts = prompts
        self.manual_mode = manual_mode
        self.output_format = output_format
        self.output_directory = output_directory
        self.allow_edit_reports = allow_edit_reports
        
        # Estado
        self.should_continue = True
        self.confirmation_data = None
        self.edited_reports = None  # Para almacenar reportes editados
        
        # Sincronización para edición de reportes
        self.edit_mutex = QMutex()
        self.edit_condition = QWaitCondition()
        self.edit_ready = False
    
    def run(self):
        """Ejecuta el proceso completo de revisión"""
        try:
            # Paso 1: Extraer texto del manuscrito
            self.log_message.emit("📄 Extracting text from manuscript...")
            self.progress.emit(5)
            
            doc_processor = DocumentProcessor()
            manuscript_text = doc_processor.extract_text(self.file_path)
            
            if not manuscript_text.strip():
                raise ValueError("The manuscript appears to be empty or unreadable")
            
            self.log_message.emit(f"✓ Extracted {len(manuscript_text)} characters")
            self.progress.emit(10)
            
            # Paso 2: Detectar tipo de artículo
            self.log_message.emit("🔍 Detecting article type...")
            article_type = doc_processor.detect_article_type(manuscript_text)
            self.log_message.emit(f"✓ Article type: {article_type}")
            self.progress.emit(15)
            
            # Paso 2b: Extraer keywords del manuscrito (si existen)
            self.log_message.emit("🔍 Looking for author-provided keywords...")
            manuscript_keywords = doc_processor.extract_keywords(manuscript_text)
            
            if manuscript_keywords:
                self.log_message.emit(f"✓ Found {len(manuscript_keywords)} keywords in manuscript:")
                for kw in manuscript_keywords:
                    self.log_message.emit(f"  • {kw}")
            else:
                self.log_message.emit("⚠ No keywords found in manuscript, will use AI extraction")
            self.progress.emit(18)
            
            # Paso 3: Inicializar y cargar modelo de IA
            self.log_message.emit(f"🤖 Loading AI model: {self.model_name}...")
            self.log_message.emit("⏳ This may take a few minutes the first time...")
            ai_analyzer = AIAnalyzer(self.model_name)
            ai_analyzer.load_model()
            self.log_message.emit("✓ Model loaded successfully")
            self.progress.emit(25)
            
            # Paso 4: Extraer frases clave (combinar keywords + AI)
            keyphrases = []
            
            # Usar keywords del manuscrito si existen
            if manuscript_keywords:
                keyphrases.extend(manuscript_keywords[:self.num_keyphrases])
                self.log_message.emit(f"✓ Using {len(keyphrases)} author keywords")
            
            # Si faltan keyphrases, completar con IA
            if len(keyphrases) < self.num_keyphrases:
                remaining = self.num_keyphrases - len(keyphrases)
                self.log_message.emit(f"🔑 Extracting {remaining} additional key phrases with AI...")
                ai_keyphrases = ai_analyzer.extract_keyphrases(
                    manuscript_text,
                    self.prompts.get('keyphrases', ''),
                    remaining
                )
                keyphrases.extend(ai_keyphrases)
            
            if not keyphrases:
                raise ValueError("Could not extract key phrases from the manuscript")
            
            self.log_message.emit(f"✓ Final key phrases for PubMed search:")
            for kp in keyphrases:
                self.log_message.emit(f"  • {kp}")
            self.progress.emit(35)
            
            # Confirmación manual si está activado
            if self.manual_mode:
                self.log_message.emit("⏸ Waiting for user confirmation...")
                # Aquí se podría emitir señal para confirmación
                # Por ahora continuamos automáticamente
            
            # Paso 5: Buscar en PubMed
            self.log_message.emit("🔬 Searching PubMed database...")
            pubmed_searcher = PubMedSearcher()
            pubmed_data = pubmed_searcher.search_articles(keyphrases, self.num_articles)
            
            if not pubmed_data:
                self.log_message.emit("⚠ Warning: No articles found in PubMed")
                self.log_message.emit("⚠ The evaluation will proceed with limited reference data")
            else:
                total_articles = sum(len(articles) for articles in pubmed_data.values())
                self.log_message.emit(f"✓ Found {total_articles} articles:")
                for kp, articles in pubmed_data.items():
                    self.log_message.emit(f"  • '{kp}': {len(articles)} articles")
            
            self.progress.emit(55)
            
            # Confirmación manual si está activado
            if self.manual_mode:
                self.log_message.emit("⏸ Waiting for user confirmation...")
            
            # Paso 6: Analizar manuscrito con IA
            self.log_message.emit("📊 Analyzing manuscript with AI...")
            self.log_message.emit("⏳ This may take several minutes...")
            
            evaluation = ai_analyzer.analyze_manuscript(
                manuscript_text,
                pubmed_data,
                self.prompts.get('analysis', ''),
                article_type
            )
            
            self.log_message.emit("✓ Analysis completed")
            self.log_message.emit(f"  • Major points: {len(evaluation.get('major', []))}")
            self.log_message.emit(f"  • Minor points: {len(evaluation.get('minor', []))}")
            self.log_message.emit(f"  • Other points: {len(evaluation.get('other', []))}")
            self.log_message.emit(f"  • Suggestions: {len(evaluation.get('suggestions', []))}")
            self.progress.emit(75)
            
            # Paso 6.5: Permitir edición manual si está habilitado
            if self.allow_edit_reports:
                self.log_message.emit("⏸ Requesting manual verification of reports...")
                
                # Reset edit state
                self.edit_mutex.lock()
                self.edit_ready = False
                self.edited_reports = None
                self.edit_mutex.unlock()
                
                # Emitir señal para edición en el hilo principal
                self.request_report_edit.emit({'evaluation': evaluation})
                
                # Esperar a que el usuario edite usando wait condition (más eficiente que polling)
                self.edit_mutex.lock()
                if not self.edit_ready:
                    # Esperar con timeout (en milisegundos)
                    self.edit_condition.wait(self.edit_mutex, MAX_EDIT_TIMEOUT_SECONDS * 1000)
                self.edit_mutex.unlock()
                
                if self.edited_reports is not None:
                    evaluation = self.edited_reports
                    self.log_message.emit("✓ Using edited evaluation")
                else:
                    self.log_message.emit("⚠ Edit timeout, using original evaluation")
            
            # Paso 7: Generar informes
            self.log_message.emit("📝 Generating reports...")
            
            # Determinar ruta de salida
            output_path = self.file_path
            if self.output_directory:
                # Usar directorio personalizado con el nombre base del archivo
                base_name = os.path.basename(self.file_path)
                output_path = os.path.join(self.output_directory, base_name)
                self.log_message.emit(f"✓ Using custom output directory: {self.output_directory}")
            
            report_generator = ReportGenerator(self.output_format)
            
            # Informe para autor
            author_report = report_generator.generate_author_report(
                output_path,
                evaluation
            )
            self.log_message.emit(f"✓ Author report: {author_report}")
            
            self.progress.emit(85)
            
            # Informe para auditoría
            auditor_report = report_generator.generate_auditor_report(
                output_path,
                evaluation,
                pubmed_data,
                keyphrases,
                manuscript_text,
                article_type
            )
            self.log_message.emit(f"✓ Auditor report: {auditor_report}")
            
            self.progress.emit(95)
            
            # Liberar memoria del modelo
            ai_analyzer.unload_model()
            
            self.progress.emit(100)
            self.log_message.emit("✅ Review completed successfully!")
            
            # Emitir resultado
            self.result.emit({
                'success': True,
                'author_report': author_report,
                'auditor_report': auditor_report,
                'evaluation': evaluation,
                'keyphrases': keyphrases,
                'article_type': article_type,
                'total_articles': sum(len(articles) for articles in pubmed_data.values()) if pubmed_data else 0
            })
            
        except Exception as e:
            error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
            self.log_message.emit(f"❌ {error_msg}")
            self.error.emit(error_msg)
    
    def notify_edit_complete(self):
        """Notifica que la edición de reportes ha sido completada"""
        self.edit_mutex.lock()
        self.edit_ready = True
        self.edit_condition.wakeAll()
        self.edit_mutex.unlock()
    
    def stop(self):
        """Detiene el procesamiento"""
        self.should_continue = False
        self.quit()
