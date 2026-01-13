"""
Módulo para extracción de texto de diferentes formatos de documento
"""
import os
import re
from typing import Optional, List
from docx import Document
from PyPDF2 import PdfReader
from striprtf.striprtf import rtf_to_text


class DocumentProcessor:
    """Procesa documentos en múltiples formatos y extrae texto"""
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Extrae texto de un archivo según su extensión
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Texto extraído del documento
            
        Raises:
            ValueError: Si el formato no es soportado
            FileNotFoundError: Si el archivo no existe
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == '.pdf':
                return DocumentProcessor._extract_from_pdf(file_path)
            elif ext in ['.doc', '.docx']:
                return DocumentProcessor._extract_from_docx(file_path)
            elif ext == '.rtf':
                return DocumentProcessor._extract_from_rtf(file_path)
            elif ext == '.txt':
                return DocumentProcessor._extract_from_txt(file_path)
            else:
                raise ValueError(f"Formato no soportado: {ext}")
        except Exception as e:
            raise Exception(f"Error al extraer texto del archivo {file_path}: {str(e)}")
    
    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """Extrae texto de un archivo PDF"""
        reader = PdfReader(file_path)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return ' '.join(text_parts)
    
    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        """Extrae texto de un archivo DOCX o DOC"""
        doc = Document(file_path)
        return '\n'.join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())
    
    @staticmethod
    def _extract_from_rtf(file_path: str) -> str:
        """Extrae texto de un archivo RTF"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            rtf_content = f.read()
        return rtf_to_text(rtf_content)
    
    @staticmethod
    def _extract_from_txt(file_path: str) -> str:
        """Extrae texto de un archivo TXT"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    @staticmethod
    def detect_article_type(text: str) -> str:
        """
        Detecta el tipo de artículo basándose en su contenido
        
        Args:
            text: Texto del manuscrito
            
        Returns:
            Tipo de artículo: "Research Article", "Review", "Case Report", u "Other"
        """
        text_lower = text.lower()
        
        # Palabras clave para artículos de investigación
        research_keywords = ['methods', 'methodology', 'materials', 'results', 'discussion']
        research_count = sum(1 for keyword in research_keywords if keyword in text_lower)
        
        # Palabras clave para revisiones
        review_keywords = ['review', 'systematic review', 'meta-analysis', 'literature']
        review_count = sum(1 for keyword in review_keywords if keyword in text_lower)
        
        # Palabras clave para casos clínicos
        case_keywords = ['case report', 'case study', 'patient', 'diagnosis', 'treatment']
        case_count = sum(1 for keyword in case_keywords if keyword in text_lower)
        
        # Determinar tipo basándose en las coincidencias
        if research_count >= 4:
            return "Research Article"
        elif review_count >= 2:
            return "Review"
        elif case_count >= 3:
            return "Case Report"
        else:
            return "Other"
    
    @staticmethod
    def get_text_preview(text: str, max_chars: int = 1000) -> str:
        """
        Obtiene una vista previa del texto
        
        Args:
            text: Texto completo
            max_chars: Número máximo de caracteres
            
        Returns:
            Vista previa del texto
        """
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "..."
    
    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """
        Extrae palabras clave (keywords) del manuscrito si están presentes
        
        Args:
            text: Texto completo del manuscrito
            
        Returns:
            Lista de keywords extraídas del manuscrito, vacía si no se encuentran
        """
        keywords = []
        
        # Patrones para encontrar secciones de keywords en diferentes formatos
        patterns = [
            r'(?i)keywords?\s*[:;]\s*([^\n]+)',  # Keywords: palabra1, palabra2
            r'(?i)key\s+words?\s*[:;]\s*([^\n]+)',  # Key words: palabra1, palabra2
            r'(?i)index\s+terms?\s*[:;]\s*([^\n]+)',  # Index terms: palabra1, palabra2
            r'(?i)palabras?\s+clave\s*[:;]\s*([^\n]+)',  # Palabras clave: (Spanish)
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Tomar el primer match
                keywords_text = matches[0].strip()
                # Dividir por delimitadores comunes
                keywords = re.split(r'[;,•·]+', keywords_text)
                keywords = [kw.strip() for kw in keywords if kw.strip()]
                break
        
        # Filtrar keywords vacías o muy cortas
        keywords = [kw for kw in keywords if len(kw) > 2]
        
        # Limitar a 10 keywords máximo (lo más común)
        if len(keywords) > 10:
            keywords = keywords[:10]
        
        return keywords
