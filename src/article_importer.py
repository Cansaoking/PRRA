"""
Módulo para importar artículos pre-seleccionados
"""
import re
from typing import List, Dict, Optional


class ArticleImporter:
    """Importa y parsea artículos pre-seleccionados desde texto"""
    
    @staticmethod
    def parse_citations(text: str) -> List[Dict]:
        """
        Parsea un texto con citas de artículos al formato usado por la aplicación
        
        Formato esperado:
        Autor, X. et al. (Año). "Título." Revista Volumen(Número).
            Abstract text...
        
        Args:
            text: Texto con citas y abstracts
            
        Returns:
            Lista de diccionarios con información de artículos
        """
        articles = []
        
        # Split by double newlines to separate articles
        article_blocks = re.split(r'\n\s*\n', text.strip())
        
        for block in article_blocks:
            if not block.strip():
                continue
                
            article = ArticleImporter._parse_single_citation(block)
            if article:
                articles.append(article)
        
        return articles
    
    @staticmethod
    def _parse_single_citation(block: str) -> Optional[Dict]:
        """
        Parsea una única cita con su abstract
        
        Args:
            block: Bloque de texto con una cita
            
        Returns:
            Diccionario con información del artículo o None
        """
        lines = block.split('\n')
        if not lines:
            return None
        
        # Primera línea contiene la cita
        citation_line = lines[0].strip()
        
        # Skip comment lines (starting with #)
        if citation_line.startswith('#'):
            return None
        
        # Must contain a year in parentheses to be valid
        year_match = re.search(r'\((\d{4})\)', citation_line)
        if not year_match:
            return None
        
        # El resto es el abstract (si existe)
        abstract_lines = [line.strip() for line in lines[1:] if line.strip()]
        abstract = ' '.join(abstract_lines) if abstract_lines else "No abstract available"
        
        # Parsear la cita
        # Patrón: Autor(es) (Año). "Título." Revista Info.
        
        # Extraer año
        year = year_match.group(1)
        
        # Extraer título (entre comillas)
        title_match = re.search(r'"([^"]+)"', citation_line)
        title = title_match.group(1) if title_match else "Unknown title"
        
        # Extraer autores (antes del año)
        authors_part = citation_line[:year_match.start()].strip()
        # Limpiar puntuación final
        authors = authors_part.rstrip('.,').strip()
        
        # Extraer revista (después del título y antes del punto final)
        journal = "Unknown journal"
        if title_match:
            after_title = citation_line[title_match.end():].strip()
            # Remover punto inicial si existe
            after_title = after_title.lstrip('.').strip()
            # Tomar hasta el final o hasta un punto
            journal_match = re.match(r'([^.]+)', after_title)
            if journal_match:
                journal = journal_match.group(1).strip()
        
        return {
            'pmid': 'imported',  # Marcar como importado
            'title': title,
            'authors': authors,
            'journal': journal,
            'year': year,
            'abstract': abstract
        }
    
    @staticmethod
    def convert_to_pubmed_format(articles: List[Dict], keyphrase: str = "imported_articles") -> Dict[str, List[Dict]]:
        """
        Convierte la lista de artículos al formato esperado por el sistema
        
        Args:
            articles: Lista de artículos parseados
            keyphrase: Frase clave para agrupar los artículos
            
        Returns:
            Diccionario en formato PubMed (keyphrase -> artículos)
        """
        return {keyphrase: articles}
