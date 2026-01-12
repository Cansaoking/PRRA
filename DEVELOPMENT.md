# PRRA - Development Guide

## Architecture Overview

PRRA follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                     UI Layer (PyQt5)                     │
│                   src/ui_main.py                         │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│                  Worker Thread Layer                     │
│                    src/worker.py                         │
└─┬──────┬──────┬──────┬──────┬───────────────────────────┘
  │      │      │      │      │
  ▼      ▼      ▼      ▼      ▼
┌───┐  ┌───┐  ┌───┐  ┌───┐  ┌───┐
│Doc│  │AI │  │Pub│  │Rep│  │Cfg│
│Proc│ │Ana│  │Med│  │Gen│  │   │
└───┘  └───┘  └───┘  └───┘  └───┘
```

## Module Descriptions

### 1. config.py
**Purpose**: Central configuration and constants
- Model definitions
- Default parameters
- Prompt templates
- File format definitions

**Key Classes/Functions**: None (constants only)

### 2. document_processor.py
**Purpose**: Document text extraction and analysis
- Extract text from PDF, DOCX, DOC, RTF, TXT
- Detect article type (research/review/case report)
- Generate text previews

**Key Classes**:
- `DocumentProcessor`: Main class with static methods

**Key Methods**:
- `extract_text(file_path)`: Extract text from any supported format
- `detect_article_type(text)`: Heuristic-based type detection
- `get_text_preview(text, max_chars)`: Generate preview

### 3. pubmed_searcher.py
**Purpose**: Search and retrieve articles from PubMed
- Progressive search strategy (individual → AND combinations)
- Date-based filtering
- Article metadata extraction

**Key Classes**:
- `PubMedSearcher`: Manages PubMed interactions

**Key Methods**:
- `search_articles(keyphrases, num_articles)`: Main search method
- `search_with_progressive_and(keyphrases, num_articles)`: Advanced search
- `_fetch_article_details(pmids)`: Retrieve full article data

**Search Strategy**:
1. Search each keyphrase individually with recent dates (5 years)
2. If too few results: extend date range (10 years)
3. If still too few: search without date limits
4. If too many results: combine with AND

### 4. ai_analyzer.py
**Purpose**: AI-based manuscript analysis
- Load and manage HuggingFace models
- Extract key phrases from manuscripts
- Analyze manuscripts using reference abstracts
- GPU/CPU detection and usage

**Key Classes**:
- `AIAnalyzer`: Manages AI models and inference

**Key Methods**:
- `load_model()`: Load HuggingFace model
- `extract_keyphrases(text, prompt, num)`: Extract key phrases
- `analyze_manuscript(text, pubmed_data, prompt, type)`: Full analysis
- `unload_model()`: Free GPU/CPU memory

**Analysis Structure**:
- Major Points: Critical issues
- Minor Points: Smaller improvements
- Other Points: Optional observations
- Suggestions: Actionable recommendations

### 5. report_generator.py
**Purpose**: Generate evaluation reports
- Create PDF and DOCX reports
- Two report types: Author and Auditor
- Professional formatting

**Key Classes**:
- `ReportGenerator`: Manages report creation

**Key Methods**:
- `generate_author_report()`: Simple evaluation report for authors
- `generate_auditor_report()`: Detailed report with all metadata

**Report Types**:

**Author Report**:
- Evaluation only (major/minor/other/suggestions)
- Clean, professional format
- No internal details

**Auditor Report**:
- Complete manuscript information
- Key phrases extracted
- PubMed search results
- Full evaluation
- Article metadata
- For internal review and verification

### 6. worker.py
**Purpose**: Background processing thread
- Asynchronous manuscript processing
- Progress reporting
- Error handling
- Logging

**Key Classes**:
- `WorkerThread`: QThread subclass for background work

**Key Signals**:
- `progress`: Update progress bar (0-100)
- `log_message`: Send log messages to UI
- `result`: Emit final results
- `error`: Report errors

**Processing Pipeline**:
1. Extract text (5-10%)
2. Detect article type (10-15%)
3. Load AI model (15-25%)
4. Extract keyphrases (25-35%)
5. Search PubMed (35-55%)
6. Analyze manuscript (55-75%)
7. Generate reports (75-95%)
8. Cleanup (95-100%)

### 7. ui_main.py
**Purpose**: PyQt5 graphical user interface
- File selection
- Configuration
- Prompt editing
- Progress monitoring

**Key Classes**:
- `MainWindow`: Main application window

**UI Tabs**:
1. **Manuscript**: File selection and preview
2. **Configuration**: Settings (keyphrases, articles, model, format)
3. **Prompts**: Edit AI prompts (JSON)
4. **Progress**: Real-time logs and progress bar

## Data Flow

```
User selects manuscript
        ↓
Document processor extracts text
        ↓
AI analyzer loads model
        ↓
AI extracts key phrases
        ↓
PubMed searcher finds articles
        ↓
AI analyzes manuscript using abstracts
        ↓
Report generator creates two reports
        ↓
User receives both reports
```

## Key Design Decisions

### 1. Modular Architecture
- **Why**: Separation of concerns, testability, maintainability
- **Benefit**: Easy to update individual components

### 2. Two Separate Reports
- **Why**: Different audiences need different information
- **Author Report**: Clean evaluation for manuscript improvement
- **Auditor Report**: Complete details for verification and auditing

### 3. Progressive PubMed Search
- **Why**: Balance between too many and too few results
- **Strategy**: Start specific, broaden if needed

### 4. Local AI Processing
- **Why**: Privacy and copyright concerns
- **Requirement**: No manuscripts sent to external servers

### 5. GPU Detection
- **Why**: Significant performance improvement when available
- **Fallback**: CPU mode for systems without GPU

### 6. Editable Prompts
- **Why**: Flexibility for different use cases
- **Format**: JSON for easy editing and sharing

## Extension Points

### Adding New Models
1. Add model name to `config.py` → `AVAILABLE_MODELS`
2. Ensure model is compatible with HuggingFace `transformers`
3. Test with various manuscript types

### Adding New File Formats
1. Add format to `config.py` → `SUPPORTED_FORMATS`
2. Implement extraction method in `document_processor.py`
3. Follow pattern of existing extractors

### Customizing Evaluation Criteria
1. Edit prompts in `config.py` → `DEFAULT_PROMPTS`
2. Update parsing logic in `ai_analyzer.py` → `_parse_evaluation()`
3. Adjust report generation if needed

### Adding New Report Formats
1. Extend `report_generator.py`
2. Add new format to `config.py`
3. Implement generation methods for both report types

## Testing

### Unit Tests
- Test individual modules with `test_modules.py`
- Mock external dependencies (PubMed, AI models)

### Integration Tests
- Test complete pipeline with sample manuscripts
- Verify report generation
- Check error handling

### Manual Tests
1. Test all file formats (PDF, DOCX, DOC, RTF, TXT)
2. Test with different manuscript types
3. Test with various AI models
4. Test error scenarios (no internet, corrupted file, etc.)

## Performance Considerations

### Memory Management
- AI models can use 4-16 GB RAM/VRAM
- Unload models after use with `unload_model()`
- Consider smaller models for limited resources

### Processing Time
- First model load: 1-5 minutes (download + load)
- Text extraction: < 1 second
- Keyphrase extraction: 10-30 seconds
- PubMed search: 5-20 seconds
- Manuscript analysis: 30-120 seconds
- Report generation: < 5 seconds

**Total**: 1-6 minutes per manuscript (after initial setup)

### Optimization Tips
1. Use GPU when available (10-50x faster)
2. Use smaller models for faster processing
3. Limit manuscript text length in prompts
4. Cache model between analyses
5. Reduce number of PubMed articles if needed

## Troubleshooting

### Common Issues

**Issue**: Out of memory
- **Solution**: Use smaller model, reduce text length, close other apps

**Issue**: Model download fails
- **Solution**: Check internet, use mirror, download manually

**Issue**: PubMed search returns no results
- **Solution**: Check internet, verify email in config, broaden search

**Issue**: Report generation fails
- **Solution**: Check write permissions, verify output directory exists

**Issue**: GUI doesn't start
- **Solution**: Install PyQt5, check display settings

## Contributing

1. Follow existing code style
2. Add docstrings to new functions
3. Update this guide for major changes
4. Test thoroughly before committing
5. Use meaningful commit messages

## License

[Specify license here]
