"""
Módulo para análisis de manuscritos con modelos de IA
"""
from typing import List, Dict, Tuple, Optional
from src.config import MAX_INPUT_TOKENS, MAX_OUTPUT_TOKENS_KEYPHRASES, MAX_OUTPUT_TOKENS_ANALYSIS


class AIAnalyzer:
    """Gestiona el análisis de manuscritos usando modelos de IA locales"""
    
    def __init__(self, model_name: str):
        """
        Inicializa el analizador de IA
        
        Args:
            model_name: Nombre del modelo de HuggingFace a usar
        """
        self.model_name = model_name
        # Lazy import: defer torch/transformers import until model is loaded
        self.device = None
        self.model = None
        self.tokenizer = None
    
    def load_model(self) -> Tuple:
        """
        Carga el modelo y tokenizador
        
        Returns:
            Tupla con (modelo, tokenizador)
        """
        if self.model is None or self.tokenizer is None:
            # Import torch and transformers only when actually loading the model
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            # Initialize device on first load
            if self.device is None:
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            ).to(self.device)
            
            # Asegurar que tiene pad_token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
        
        return self.model, self.tokenizer
    
    def extract_keyphrases(self, text: str, prompt_template: str, num_keyphrases: int = 5) -> List[str]:
        """
        Extrae frases clave del manuscrito usando IA
        
        Args:
            text: Texto del manuscrito
            prompt_template: Template del prompt con placeholders {num} y {text}
            num_keyphrases: Número de frases clave a extraer
            
        Returns:
            Lista de frases clave
        """
        import torch
        model, tokenizer = self.load_model()
        
        # Limitar texto de entrada
        text_excerpt = text[:MAX_INPUT_TOKENS * 4]  # Aproximadamente 4 chars por token
        
        # Preparar prompt
        prompt = prompt_template.format(num=num_keyphrases, text=text_excerpt)
        
        # Generar
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=MAX_INPUT_TOKENS).to(self.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=MAX_OUTPUT_TOKENS_KEYPHRASES,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                pad_token_id=tokenizer.pad_token_id
            )
        
        # Decodificar respuesta
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extraer solo la parte generada (después del prompt)
        if prompt in generated_text:
            generated_text = generated_text.split(prompt)[-1]
        
        # Parsear frases clave
        keyphrases = self._parse_keyphrases(generated_text, num_keyphrases)
        
        return keyphrases
    
    def _parse_keyphrases(self, text: str, num_keyphrases: int) -> List[str]:
        """
        Parsea frases clave del texto generado
        
        Args:
            text: Texto generado por la IA
            num_keyphrases: Número esperado de frases
            
        Returns:
            Lista de frases clave limpias
        """
        lines = text.strip().split('\n')
        keyphrases = []
        
        for line in lines:
            # Limpiar línea
            line = line.strip()
            
            # Eliminar numeración y guiones
            line = line.lstrip('0123456789.-) ')
            
            # Eliminar comillas
            line = line.strip('"\'')
            
            # Validar que sea una frase válida (2-6 palabras)
            if line and 2 <= len(line.split()) <= 6:
                keyphrases.append(line)
            
            if len(keyphrases) >= num_keyphrases:
                break
        
        # Si no se encontraron suficientes, extraer de cualquier línea
        if len(keyphrases) < num_keyphrases:
            for line in lines:
                words = line.strip().split()
                if 2 <= len(words) <= 6 and line.strip() not in keyphrases:
                    keyphrases.append(line.strip())
                    if len(keyphrases) >= num_keyphrases:
                        break
        
        return keyphrases[:num_keyphrases]
    
    def analyze_manuscript(
        self,
        manuscript_text: str,
        pubmed_data: Dict[str, List[Dict]],
        prompt_template: str,
        article_type: str
    ) -> Dict[str, List[str]]:
        """
        Analiza el manuscrito usando abstracts de PubMed como referencia
        
        Args:
            manuscript_text: Texto completo del manuscrito
            pubmed_data: Datos de artículos de PubMed
            prompt_template: Template del prompt
            article_type: Tipo de artículo detectado
            
        Returns:
            Diccionario con secciones de evaluación: major, minor, other, suggestions
        """
        import torch
        model, tokenizer = self.load_model()
        
        # Preparar abstracts
        abstracts = self._prepare_abstracts(pubmed_data)
        
        # Limitar texto del manuscrito
        text_excerpt = manuscript_text[:MAX_INPUT_TOKENS * 3]
        
        # Preparar prompt
        prompt = prompt_template.format(
            text=text_excerpt,
            abstracts=abstracts,
            type=article_type
        )
        
        # Generar análisis
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=MAX_INPUT_TOKENS).to(self.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=MAX_OUTPUT_TOKENS_ANALYSIS,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                pad_token_id=tokenizer.pad_token_id
            )
        
        # Decodificar
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extraer solo la respuesta generada
        if prompt in generated_text:
            generated_text = generated_text.split(prompt)[-1]
        
        # Parsear evaluación
        evaluation = self._parse_evaluation(generated_text)
        
        return evaluation
    
    def _prepare_abstracts(self, pubmed_data: Dict[str, List[Dict]], max_abstracts: int = 10) -> str:
        """
        Prepara abstracts de PubMed para el prompt
        
        Args:
            pubmed_data: Datos de PubMed
            max_abstracts: Número máximo de abstracts a incluir
            
        Returns:
            String con abstracts formateados
        """
        abstracts = []
        count = 0
        
        for keyphrase, articles in pubmed_data.items():
            for article in articles:
                if count >= max_abstracts:
                    break
                
                abstract = article.get('abstract', 'No abstract available')
                if abstract and abstract != "No abstract available":
                    abstracts.append(f"[{article.get('year', 'N/A')}] {abstract}")
                    count += 1
            
            if count >= max_abstracts:
                break
        
        return '\n\n'.join(abstracts) if abstracts else "No abstracts available"
    
    def _parse_evaluation(self, text: str) -> Dict[str, List[str]]:
        """
        Parsea el texto de evaluación en secciones estructuradas
        
        Args:
            text: Texto generado por la IA
            
        Returns:
            Diccionario con secciones: major, minor, other, suggestions
        """
        sections = {
            'major': [],
            'minor': [],
            'other': [],
            'suggestions': []
        }
        
        current_section = None
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Detectar encabezados de sección
            line_upper = line.upper()
            if 'MAJOR POINT' in line_upper:
                current_section = 'major'
                continue
            elif 'MINOR POINT' in line_upper:
                current_section = 'minor'
                continue
            elif 'OTHER POINT' in line_upper:
                current_section = 'other'
                continue
            elif 'SUGGESTION' in line_upper or 'IMPROVEMENT' in line_upper:
                current_section = 'suggestions'
                continue
            
            # Agregar contenido a la sección actual
            if current_section and line:
                # Limpiar línea (remover guiones, asteriscos, numeración)
                line = line.lstrip('-*•0123456789.) ')
                if line:
                    sections[current_section].append(line)
        
        # Si no se encontró estructura, intentar extracción libre
        if not any(sections.values()):
            sections = self._parse_evaluation_fallback(text)
        
        return sections
    
    def _parse_evaluation_fallback(self, text: str) -> Dict[str, List[str]]:
        """
        Método de respaldo para parsear evaluación sin estructura clara
        
        Args:
            text: Texto de evaluación
            
        Returns:
            Diccionario con secciones
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Dividir en partes iguales
        mid = len(lines) // 2
        
        return {
            'major': lines[:mid//2] if lines else ['No major points identified'],
            'minor': lines[mid//2:mid] if len(lines) > mid//2 else ['No minor points identified'],
            'other': lines[mid:mid+mid//2] if len(lines) > mid else [],
            'suggestions': lines[mid+mid//2:] if len(lines) > mid+mid//2 else []
        }
    
    def unload_model(self):
        """Libera memoria descargando el modelo"""
        if self.model is not None:
            del self.model
            del self.tokenizer
            self.model = None
            self.tokenizer = None
            
            # Only import torch if needed to clear cache
            if self.device == "cuda":
                import torch
                torch.cuda.empty_cache()
