#!/usr/bin/env python3
"""
Test script for new keyword extraction feature
"""
import sys
import os
import re
from typing import List

# Add root directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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


def test_keyword_extraction():
    """Test keyword extraction functionality"""
    print("\n" + "="*60)
    print("Testing Keyword Extraction")
    print("="*60)
    
    # Test 1: CGRP receptors (the issue topic)
    test1 = """
    Title: CGRP Receptor Antagonists for Migraine Prevention
    
    Abstract: Calcitonin gene-related peptide (CGRP) plays a key role in migraine pathophysiology...
    
    Keywords: CGRP receptor, migraine, calcitonin gene-related peptide, therapeutic target, monoclonal antibodies
    
    Introduction: ...
    """
    result1 = extract_keywords(test1)
    print(f"✓ Test 1 (CGRP receptors): Found {len(result1)} keywords")
    for kw in result1:
        print(f"  • {kw}")
    assert 'CGRP receptor' in result1, "Should find 'CGRP receptor'"
    assert 'migraine' in result1, "Should find 'migraine'"
    
    # Test 2: Diabetes (should not be confused with CGRP)
    test2 = """
    Keywords: diabetes mellitus; insulin resistance; type 2 diabetes; glucose metabolism
    """
    result2 = extract_keywords(test2)
    print(f"\n✓ Test 2 (Diabetes): Found {len(result2)} keywords")
    for kw in result2:
        print(f"  • {kw}")
    assert 'diabetes mellitus' in result2
    assert 'CGRP' not in ' '.join(result2), "Should not find CGRP in diabetes paper"
    
    # Test 3: Different formats
    test3 = """
    Key words: neuropeptide, receptor pharmacology, pain management
    """
    result3 = extract_keywords(test3)
    print(f"\n✓ Test 3 (Key words format): Found {len(result3)} keywords")
    for kw in result3:
        print(f"  • {kw}")
    assert len(result3) == 3
    
    # Test 4: Spanish keywords
    test4 = """
    Palabras clave: receptor CGRP, migraña, péptido relacionado
    """
    result4 = extract_keywords(test4)
    print(f"\n✓ Test 4 (Spanish): Found {len(result4)} keywords")
    for kw in result4:
        print(f"  • {kw}")
    assert len(result4) > 0
    
    # Test 5: No keywords
    test5 = """
    Title: Some paper without keywords
    Abstract: This paper has no keyword section
    """
    result5 = extract_keywords(test5)
    print(f"\n✓ Test 5 (No keywords): Found {len(result5)} keywords")
    assert len(result5) == 0, "Should find no keywords"
    
    # Test 6: Multiple separators
    test6 = """
    Keywords: receptor • ligand • binding • activation • signaling
    """
    result6 = extract_keywords(test6)
    print(f"\n✓ Test 6 (Bullet separator): Found {len(result6)} keywords")
    for kw in result6:
        print(f"  • {kw}")
    assert len(result6) == 5
    
    print("\n" + "="*60)
    print("✅ All keyword extraction tests passed!")
    print("="*60)


def test_prompt_improvement():
    """Test that prompts are improved"""
    print("\n" + "="*60)
    print("Testing Prompt Improvements")
    print("="*60)
    
    from src.config import DEFAULT_PROMPTS
    
    keyphrases_prompt = DEFAULT_PROMPTS['keyphrases']
    
    # Check for medical/scientific focus
    assert 'medical/scientific' in keyphrases_prompt.lower(), "Prompt should mention medical/scientific"
    print("✓ Keyphrases prompt mentions medical/scientific focus")
    
    # Check it discourages general terms
    assert 'do not' in keyphrases_prompt.lower() or 'only' in keyphrases_prompt.lower(), \
        "Prompt should discourage general terms"
    print("✓ Prompt discourages general methodology terms")
    
    # Check for specificity
    assert any(term in keyphrases_prompt.lower() for term in ['specific', 'main', 'topics']), \
        "Prompt should encourage specificity"
    print("✓ Prompt encourages specific medical concepts")
    
    print("\n" + "="*60)
    print("✅ All prompt improvement tests passed!")
    print("="*60)


def main():
    """Run all tests"""
    print("="*60)
    print("PRRA - Keyword Extraction and Improvements Tests")
    print("="*60)
    
    try:
        test_keyword_extraction()
        test_prompt_improvement()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nSummary of improvements:")
        print("1. ✓ Keyword extraction from manuscripts")
        print("2. ✓ Improved AI prompt for medical/scientific focus")
        print("3. ✓ Support for multiple keyword formats")
        print("4. ✓ Bilingual support (English/Spanish)")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
