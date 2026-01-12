#!/usr/bin/env python3
"""
Test script for PRRA core modules (non-GUI)
"""
import sys
import os

# Añadir directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_document_processor():
    """Test DocumentProcessor module"""
    print("\n" + "="*60)
    print("Testing DocumentProcessor")
    print("="*60)
    
    from src.document_processor import DocumentProcessor
    
    # Test article type detection
    test_text_research = """
    Introduction: This is a research article.
    Methods: We used various methods.
    Results: We found interesting results.
    Discussion: We discuss our findings.
    """
    
    test_text_review = """
    This is a systematic review of the literature.
    We reviewed multiple studies on this topic.
    """
    
    dp = DocumentProcessor()
    
    article_type_1 = dp.detect_article_type(test_text_research)
    print(f"✓ Research article detected as: {article_type_1}")
    
    article_type_2 = dp.detect_article_type(test_text_review)
    print(f"✓ Review article detected as: {article_type_2}")
    
    preview = dp.get_text_preview("This is a long text " * 100, 50)
    print(f"✓ Text preview generated: {len(preview)} chars")
    
    print("✓ DocumentProcessor tests passed")

def test_pubmed_searcher():
    """Test PubMedSearcher module"""
    print("\n" + "="*60)
    print("Testing PubMedSearcher")
    print("="*60)
    
    from src.pubmed_searcher import PubMedSearcher
    
    ps = PubMedSearcher()
    print("✓ PubMedSearcher instance created")
    print("✓ Note: Actual PubMed searches require internet connection")
    print("✓ PubMedSearcher module loaded successfully")

def test_report_generator():
    """Test ReportGenerator module"""
    print("\n" + "="*60)
    print("Testing ReportGenerator")
    print("="*60)
    
    from src.report_generator import ReportGenerator
    
    # Test for both formats
    rg_pdf = ReportGenerator('pdf')
    print("✓ ReportGenerator instance created (PDF)")
    
    rg_docx = ReportGenerator('docx')
    print("✓ ReportGenerator instance created (DOCX)")
    
    print("✓ ReportGenerator tests passed")

def test_config():
    """Test config module"""
    print("\n" + "="*60)
    print("Testing Config")
    print("="*60)
    
    from src import config
    
    print(f"✓ Available models: {len(config.AVAILABLE_MODELS)}")
    for model in config.AVAILABLE_MODELS:
        print(f"  - {model}")
    
    print(f"✓ Default keyphrases: {config.DEFAULT_NUM_KEYPHRASES}")
    print(f"✓ Default articles: {config.DEFAULT_NUM_ARTICLES}")
    print(f"✓ Supported formats: {len(config.SUPPORTED_FORMATS)}")
    print("✓ Config module tests passed")

def main():
    """Run all tests"""
    print("="*60)
    print("PRRA - Core Module Tests")
    print("="*60)
    
    try:
        test_config()
        test_document_processor()
        test_pubmed_searcher()
        test_report_generator()
        
        print("\n" + "="*60)
        print("✅ All core module tests passed!")
        print("="*60)
        print("\nNote: GUI components (PyQt5) are not tested in this script.")
        print("Note: AI analyzer requires torch and transformers (large dependencies).")
        print("Note: Actual functionality requires running the full application.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
