"""
Configuración y constantes de la aplicación PRRA
"""

# Configuración de PubMed
ENTREZ_EMAIL = "prra@example.com"
ENTREZ_TOOL = "PRRA"

# Modelos de IA disponibles
AVAILABLE_MODELS = [
    "Qwen/Qwen2.5-7B-Instruct",
    "deepseek-ai/deepseek-coder-7b-instruct-v1.5",
    "microsoft/Phi-3-mini-4k-instruct",
    "meta-llama/Llama-2-7b-chat-hf"
]

# Formatos de archivo soportados
SUPPORTED_FORMATS = {
    'pdf': 'PDF Documents (*.pdf)',
    'docx': 'Word Documents (*.docx)',
    'doc': 'Word Documents (*.doc)',
    'rtf': 'Rich Text Format (*.rtf)',
    'txt': 'Text Files (*.txt)'
}

# Configuración por defecto
DEFAULT_NUM_KEYPHRASES = 5
DEFAULT_NUM_ARTICLES = 20
DEFAULT_OUTPUT_FORMAT = "pdf"

# Prompts por defecto
DEFAULT_PROMPTS = {
    'keyphrases': """Extract {num} key phrases (2-4 words each) from the following scientific manuscript text.
Focus on the main topics, methods, and findings. Return only the phrases, one per line.

Text:
{text}

Key phrases:""",
    
    'analysis': """You are an expert scientific peer reviewer. Analyze the following manuscript and provide a detailed evaluation.

Manuscript Type: {type}
Manuscript Text (excerpt):
{text}

Reference Abstracts from recent PubMed articles:
{abstracts}

Evaluate the manuscript on these aspects:
1. English language quality (grammar, clarity, academic style)
2. Structure and organization (logical flow, section organization)
3. Content currency (are references and methods up-to-date?)
4. Methodology (appropriate methods, clear description)
5. Originality and contribution
6. Data presentation and interpretation
7. Conclusions supported by results

Provide your evaluation in this exact format:

MAJOR POINTS:
- [List critical issues that must be addressed]

MINOR POINTS:
- [List smaller issues that should be improved]

OTHER POINTS:
- [List optional suggestions or observations]

SUGGESTIONS FOR IMPROVEMENT:
- [List specific actionable suggestions]

Evaluation:"""
}

# Configuración de búsqueda en PubMed
PUBMED_INITIAL_YEARS = 5  # Años hacia atrás para búsqueda inicial
PUBMED_MAX_RESULTS_THRESHOLD = 100  # Umbral para considerar "demasiados resultados"
PUBMED_MIN_RESULTS_THRESHOLD = 5   # Umbral para considerar "pocos resultados"

# Configuración de generación de texto con IA
MAX_INPUT_TOKENS = 2000
MAX_OUTPUT_TOKENS_KEYPHRASES = 300
MAX_OUTPUT_TOKENS_ANALYSIS = 2000

# Configuración de interfaz
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
