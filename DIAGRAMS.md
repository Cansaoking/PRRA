# PRRA - Application Flow Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER                                  │
│                          ↕                                   │
│                    ┌──────────┐                              │
│                    │  PyQt5   │                              │
│                    │    UI    │                              │
│                    └─────┬────┘                              │
│                          ↓                                   │
│                    ┌──────────┐                              │
│                    │  Worker  │                              │
│                    │  Thread  │                              │
│                    └─────┬────┘                              │
│                          ↓                                   │
│         ┌────────────────┼────────────────┐                 │
│         ↓                ↓                ↓                  │
│    ┌─────────┐    ┌──────────┐    ┌──────────┐             │
│    │Document │    │    AI    │    │  PubMed  │             │
│    │Processor│    │ Analyzer │    │ Searcher │             │
│    └─────────┘    └──────────┘    └──────────┘             │
│         ↓                ↓                ↓                  │
│         └────────────────┼────────────────┘                 │
│                          ↓                                   │
│                    ┌──────────┐                              │
│                    │  Report  │                              │
│                    │Generator │                              │
│                    └──────────┘                              │
│                          ↓                                   │
│                  PDF & DOCX Reports                          │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Processing Flow

```
START
  │
  ▼
┌─────────────────────┐
│ User Selects File   │
│ (PDF/DOCX/DOC/      │
│  RTF/TXT)           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ DocumentProcessor   │
│ - Extract text      │
│ - Detect type       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ AIAnalyzer          │
│ - Load model        │
│ - Check GPU/CPU     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Extract Key Phrases │
│ - Parse text        │
│ - Generate prompts  │
│ - AI inference      │
│ OUTPUT: 3-10        │
│   phrases (2-4 wds) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ PubMed Search       │
│ For each phrase:    │
│ - Search recent     │
│ - Extend if needed  │
│ - Fetch metadata    │
│ OUTPUT: Articles    │
│   with abstracts    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Manuscript Analysis │
│ - Prepare abstracts │
│ - Build prompt      │
│ - AI inference      │
│ - Parse evaluation  │
│ OUTPUT: Structured  │
│   evaluation        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Generate Reports    │
│                     │
│ ┌─────────────────┐ │
│ │ Author Report   │ │
│ │ - Major points  │ │
│ │ - Minor points  │ │
│ │ - Other points  │ │
│ │ - Suggestions   │ │
│ └─────────────────┘ │
│                     │
│ ┌─────────────────┐ │
│ │ Auditor Report  │ │
│ │ - All above     │ │
│ │ - Key phrases   │ │
│ │ - PubMed data   │ │
│ │ - Article list  │ │
│ └─────────────────┘ │
└──────────┬──────────┘
           │
           ▼
         END
```

## Module Interactions

```
┌──────────────┐
│   config.py  │◄───────┐
│              │        │
│ - Constants  │        │ All modules
│ - Defaults   │        │ import config
│ - Prompts    │        │
└──────────────┘        │
                        │
┌──────────────────────────────────────┐
│                                      │
│  ┌────────────────┐                 │
│  │ ui_main.py     │                 │
│  │                │                 │
│  │ Creates ──────►│                 │
│  │                ▼                 │
│  │          ┌──────────┐            │
│  │          │worker.py │            │
│  │          │          │            │
│  │          │ Uses:    │            │
│  │          ├──────────┤            │
│  │          │          ▼            │
│  │     ┌────┼─document_processor   │
│  │     │    │                       │
│  │     ├────┼─ai_analyzer           │
│  │     │    │                       │
│  │     ├────┼─pubmed_searcher       │
│  │     │    │                       │
│  │     └────┼─report_generator      │
│  │          │                       │
│  │          └──────────┘            │
│  └────────────────┘                 │
│                                      │
└──────────────────────────────────────┘
```

## Data Flow

```
INPUT
  │
  ├─► Manuscript File
  │   (PDF/DOCX/...)
  │
  ▼
TEXT EXTRACTION
  │
  ├─► Raw Text String
  │   (5,000-50,000 chars)
  │
  ▼
ARTICLE TYPE DETECTION
  │
  ├─► Type String
  │   ("Research Article", 
  │    "Review", etc.)
  │
  ▼
AI MODEL LOADING
  │
  ├─► Model + Tokenizer
  │   (on GPU/CPU)
  │
  ▼
KEYPHRASE EXTRACTION
  │
  ├─► List[str]
  │   ["phrase 1",
  │    "phrase 2", ...]
  │
  ▼
PUBMED SEARCH
  │
  ├─► Dict[str, List[Dict]]
  │   {"phrase": [
  │     {"title": "...",
  │      "abstract": "...",
  │      ...}, ...]}
  │
  ▼
MANUSCRIPT ANALYSIS
  │
  ├─► Dict[str, List[str]]
  │   {"major": [...],
  │    "minor": [...],
  │    "other": [...],
  │    "suggestions": [...]}
  │
  ▼
REPORT GENERATION
  │
  ├─► Author Report
  │   (PDF/DOCX)
  │
  └─► Auditor Report
      (PDF/DOCX)
      │
      ▼
    OUTPUT
```

## Timeline (Typical Processing)

```
Time    Step                        Duration    Progress %
─────────────────────────────────────────────────────────
0:00    Start                       -           0%
0:01    Extract text                1s          10%
0:02    Detect article type         1s          15%
0:02    Load AI model (cached)      5-300s      25%
2:00    Extract keyphrases          20s         35%
2:20    Search PubMed               15s         55%
2:35    Analyze manuscript          90s         75%
4:05    Generate reports            10s         95%
4:15    Complete                    -           100%
─────────────────────────────────────────────────────────
Total: ~4-6 minutes (after first model download)
First time: +5-30 minutes for model download
```

## Error Handling Flow

```
┌──────────────┐
│  Try Block   │
└──────┬───────┘
       │
       ├─► Success ──────────────────┐
       │                             │
       └─► Exception                 │
           │                         │
           ▼                         │
       ┌──────────┐                 │
       │  Catch   │                 │
       └────┬─────┘                 │
            │                        │
            ├─► Log Error            │
            │                        │
            ├─► Show MessageBox      │
            │                        │
            └─► Emit error signal    │
                │                    │
                ▼                    ▼
            ┌──────────────────────────┐
            │   Clean up resources     │
            │   - Close handles        │
            │   - Free memory          │
            │   - Reset UI state       │
            └──────────────────────────┘
```

## PubMed Search Strategy

```
┌──────────────────────┐
│  Input: Key Phrase   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Search last 5 years  │
└──────────┬───────────┘
           │
           ├─► Results > 100 ────────┐
           │                         │
           ├─► Results 5-100 ────────┼──► Use these
           │                         │
           └─► Results < 5           │
               │                     │
               ▼                     │
         ┌──────────────┐           │
         │ Extend to    │           │
         │ 10 years     │           │
         └──────┬───────┘           │
                │                    │
                ├─► Results >= 5 ───┘
                │
                └─► Results < 5
                    │
                    ▼
              ┌──────────────┐
              │ Search all   │
              │ dates        │
              └──────┬───────┘
                     │
                     └─► Use these
```

## UI State Diagram

```
     ┌─────────┐
     │  Idle   │
     └────┬────┘
          │
   ┌──────▼──────┐
   │ File Loaded │
   └──────┬──────┘
          │
   ┌──────▼──────────┐
   │ Processing      │
   │ (button locked) │
   └──────┬──────────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌────────┐  ┌────────┐
│Success │  │ Error  │
└───┬────┘  └───┬────┘
    │           │
    └─────┬─────┘
          │
          ▼
     ┌─────────┐
     │ Idle    │
     └─────────┘
```

## Memory Management

```
┌──────────────────┐
│ Load AI Model    │  ← 4-16 GB RAM/VRAM
└────────┬─────────┘
         │
    ┌────▼────┐
    │ Process │
    └────┬────┘
         │
┌────────▼────────┐
│ Unload Model    │  ← Free memory
└─────────────────┘

GPU Memory:
Before: 0 GB used
During: 8-14 GB used
After:  0 GB used (cleaned)
```

## Prompt Flow

```
User Prompt Template (JSON)
         │
         ▼
Replace Placeholders
{num} → 5
{text} → manuscript excerpt
{abstracts} → PubMed abstracts
{type} → article type
         │
         ▼
Full Prompt String
         │
         ▼
Tokenize
         │
         ▼
AI Model
         │
         ▼
Generated Text
         │
         ▼
Parse Structure
(Major/Minor/Other/Suggestions)
         │
         ▼
Structured Output (Dict)
```
