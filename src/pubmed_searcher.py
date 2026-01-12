"""
Módulo para búsqueda de artículos en PubMed
"""
import datetime
from typing import List, Dict, Optional
from Bio import Entrez
from src.config import (
    ENTREZ_EMAIL,
    ENTREZ_TOOL,
    PUBMED_INITIAL_YEARS,
    PUBMED_MAX_RESULTS_THRESHOLD,
    PUBMED_MIN_RESULTS_THRESHOLD
)


class PubMedSearcher:
    """Gestiona búsquedas en la base de datos PubMed"""
    
    def __init__(self, email: str = ENTREZ_EMAIL):
        """
        Inicializa el buscador de PubMed
        
        Args:
            email: Email para identificación en Entrez
        """
        Entrez.email = email
        Entrez.tool = ENTREZ_TOOL
    
    def search_articles(self, keyphrases: List[str], num_articles: int = 20) -> Dict[str, List[Dict]]:
        """
        Busca artículos en PubMed usando frases clave
        
        Args:
            keyphrases: Lista de frases clave para buscar
            num_articles: Número máximo de artículos a recuperar por frase
            
        Returns:
            Diccionario con frases clave como keys y listas de artículos como values
        """
        pubmed_data = {}
        current_year = datetime.datetime.now().year
        
        for kp in keyphrases:
            articles = self._search_single_keyphrase(kp, num_articles, current_year)
            if articles:
                pubmed_data[kp] = articles
        
        return pubmed_data
    
    def _search_single_keyphrase(self, keyphrase: str, num_articles: int, current_year: int) -> List[Dict]:
        """
        Busca artículos para una única frase clave
        
        Args:
            keyphrase: Frase clave a buscar
            num_articles: Número de artículos deseados
            current_year: Año actual
            
        Returns:
            Lista de artículos encontrados
        """
        try:
            # Búsqueda inicial con años recientes
            ids = self._search_with_date_range(
                keyphrase,
                current_year - PUBMED_INITIAL_YEARS,
                current_year,
                num_articles
            )
            
            # Si hay demasiados resultados, no hacer nada (ya limitado por retmax)
            # Si hay pocos resultados, extender búsqueda
            if len(ids) < PUBMED_MIN_RESULTS_THRESHOLD:
                ids = self._search_with_date_range(
                    keyphrase,
                    current_year - 10,  # Extender a 10 años
                    current_year,
                    num_articles
                )
            
            # Si aún no hay suficientes, búsqueda sin límite de fecha
            if len(ids) < PUBMED_MIN_RESULTS_THRESHOLD:
                ids = self._search_without_date(keyphrase, num_articles)
            
            # Obtener detalles de los artículos
            if ids:
                return self._fetch_article_details(ids[:num_articles])
            
            return []
            
        except Exception as e:
            print(f"Error buscando '{keyphrase}': {str(e)}")
            return []
    
    def _search_with_date_range(self, query: str, start_year: int, end_year: int, max_results: int) -> List[str]:
        """
        Realiza búsqueda en PubMed con rango de fechas
        
        Args:
            query: Término de búsqueda
            start_year: Año de inicio
            end_year: Año de fin
            max_results: Número máximo de resultados
            
        Returns:
            Lista de PMIDs
        """
        try:
            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                sort="pub date",
                retmax=max_results,
                datetype="pdat",
                mindate=f"{start_year}/01/01",
                maxdate=f"{end_year}/12/31"
            )
            record = Entrez.read(handle)
            handle.close()
            return record['IdList']
        except Exception as e:
            print(f"Error en búsqueda con fechas: {str(e)}")
            return []
    
    def _search_without_date(self, query: str, max_results: int) -> List[str]:
        """
        Realiza búsqueda en PubMed sin restricción de fechas
        
        Args:
            query: Término de búsqueda
            max_results: Número máximo de resultados
            
        Returns:
            Lista de PMIDs
        """
        try:
            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                sort="pub date",
                retmax=max_results
            )
            record = Entrez.read(handle)
            handle.close()
            return record['IdList']
        except Exception as e:
            print(f"Error en búsqueda sin fechas: {str(e)}")
            return []
    
    def _fetch_article_details(self, pmids: List[str]) -> List[Dict]:
        """
        Obtiene detalles completos de artículos por sus PMIDs
        
        Args:
            pmids: Lista de PMIDs
            
        Returns:
            Lista de diccionarios con información de artículos
        """
        try:
            fetch_handle = Entrez.efetch(db="pubmed", id=pmids, retmode="xml")
            articles_xml = Entrez.read(fetch_handle)
            fetch_handle.close()
            
            articles = []
            for art in articles_xml.get('PubmedArticle', []):
                try:
                    article_info = self._parse_article(art)
                    if article_info:
                        articles.append(article_info)
                except Exception as e:
                    print(f"Error parseando artículo: {str(e)}")
                    continue
            
            return articles
            
        except Exception as e:
            print(f"Error obteniendo detalles: {str(e)}")
            return []
    
    def _parse_article(self, article_xml) -> Optional[Dict]:
        """
        Parsea XML de un artículo de PubMed
        
        Args:
            article_xml: XML del artículo
            
        Returns:
            Diccionario con información del artículo o None
        """
        try:
            medline = article_xml['MedlineCitation']
            article = medline['Article']
            
            # Extraer autores
            authors = []
            if 'AuthorList' in article:
                for author in article['AuthorList']:
                    if 'ForeName' in author and 'LastName' in author:
                        authors.append(f"{author['ForeName']} {author['LastName']}")
                    elif 'CollectiveName' in author:
                        authors.append(author['CollectiveName'])
            
            # Extraer abstract
            abstract_text = "No abstract available"
            if 'Abstract' in article and 'AbstractText' in article['Abstract']:
                abstract_parts = article['Abstract']['AbstractText']
                if isinstance(abstract_parts, list):
                    abstract_text = ' '.join(str(part) for part in abstract_parts)
                else:
                    abstract_text = str(abstract_parts)
            
            # Extraer año
            year = "N/A"
            if 'Journal' in article and 'JournalIssue' in article['Journal']:
                pub_date = article['Journal']['JournalIssue'].get('PubDate', {})
                year = pub_date.get('Year', pub_date.get('MedlineDate', 'N/A'))
            
            return {
                'pmid': medline.get('PMID', 'N/A'),
                'title': article.get('ArticleTitle', 'No title'),
                'authors': ', '.join(authors) if authors else 'No authors listed',
                'journal': article.get('Journal', {}).get('Title', 'Unknown journal'),
                'year': str(year),
                'abstract': abstract_text
            }
            
        except Exception as e:
            print(f"Error parseando artículo: {str(e)}")
            return None
    
    def search_with_progressive_and(self, keyphrases: List[str], num_articles: int) -> Dict[str, List[Dict]]:
        """
        Búsqueda progresiva: empieza con términos individuales, 
        luego combina con AND si hay demasiados resultados
        
        Args:
            keyphrases: Lista de frases clave
            num_articles: Número de artículos deseados
            
        Returns:
            Diccionario con resultados de búsqueda
        """
        current_year = datetime.datetime.now().year
        
        # Probar búsqueda con todas las frases combinadas
        combined_query = ' AND '.join(f'"{kp}"' for kp in keyphrases)
        
        ids = self._search_with_date_range(combined_query, current_year - PUBMED_INITIAL_YEARS, current_year, 100)
        
        if len(ids) > PUBMED_MAX_RESULTS_THRESHOLD:
            # Demasiados resultados, mantener combinación AND
            articles = self._fetch_article_details(ids[:num_articles])
            return {'combined_search': articles}
        elif len(ids) < PUBMED_MIN_RESULTS_THRESHOLD:
            # Pocos resultados, buscar individualmente
            return self.search_articles(keyphrases, num_articles)
        else:
            # Cantidad razonable
            articles = self._fetch_article_details(ids[:num_articles])
            return {'combined_search': articles}
