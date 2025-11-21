#!/usr/bin/env python3
"""
Article Eater v18.4 - PDF Text Extraction
Converts uploaded PDFs to plain text for LLM processing
Uses pdfminer.six for robust extraction
"""

from pathlib import Path
from typing import Optional, Dict
import logging
import re

logger = logging.getLogger(__name__)


def extract_pdf_text(pdf_path: Path) -> Optional[str]:
    """
    Extract plain text from PDF file using pdfminer.six
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text or None if extraction fails
        
    Note:
        Requires: pip install pdfminer.six==20221105
    """
    try:
        from pdfminer.high_level import extract_text
        
        logger.info(f"Extracting text from {pdf_path}")
        text = extract_text(str(pdf_path))
        
        if not text or len(text) < 100:
            logger.warning(f"PDF extraction yielded minimal text: {len(text)} chars")
            return None
        
        logger.info(f"Extracted {len(text)} characters from {pdf_path.name}")
        return text
        
    except ImportError:
        logger.error(
            "pdfminer.six not installed. Install with: "
            "pip install pdfminer.six==20221105"
        )
        return None
    except Exception as e:
        logger.error(f"PDF extraction failed for {pdf_path}: {e}")
        return None


def section_paper_text(text: str) -> Dict[str, str]:
    """
    Heuristic sectioning of paper text into standard sections
    
    This is a STUB implementation using simple regex patterns.
    Production should use:
    - SciSpacy for sentence segmentation
    - Section header classification model (e.g., BERT fine-tuned)
    - Figure/table extraction and captioning
    - Reference extraction and parsing
    
    Args:
        text: Full paper text
        
    Returns:
        Dict mapping section names to text content:
        - abstract: Paper abstract
        - introduction: Introduction section
        - methods: Methods/Materials section  
        - results: Results/Findings section
        - discussion: Discussion section
        - conclusion: Conclusion section
        - references: References section
        - full_text: Complete text
    """
    sections = {
        'abstract': '',
        'introduction': '',
        'methods': '',
        'results': '',
        'discussion': '',
        'conclusion': '',
        'references': '',
        'full_text': text
    }
    
    # Simple regex-based sectioning
    # Note: This will miss many papers with non-standard headers
    
    # Find abstract
    abstract_pattern = re.compile(
        r'abstract[:\s]+(.*?)(?:introduction|keywords|1\.|methods)',
        re.IGNORECASE | re.DOTALL
    )
    match = abstract_pattern.search(text)
    if match:
        sections['abstract'] = match.group(1).strip()
    
    # Find introduction
    intro_pattern = re.compile(
        r'(?:introduction|1\.\s*introduction)[:\s]+(.*?)(?:2\.|methods?|materials?)',
        re.IGNORECASE | re.DOTALL
    )
    match = intro_pattern.search(text)
    if match:
        sections['introduction'] = match.group(1).strip()[:5000]  # Truncate if too long
    
    # Find methods
    methods_pattern = re.compile(
        r'(?:methods?|materials?\s+and\s+methods?|methodology)[:\s]+(.*?)(?:results?|findings?)',
        re.IGNORECASE | re.DOTALL
    )
    match = methods_pattern.search(text)
    if match:
        sections['methods'] = match.group(1).strip()[:5000]
    
    # Find results
    results_pattern = re.compile(
        r'results?[:\s]+(.*?)(?:discussion|conclusion)',
        re.IGNORECASE | re.DOTALL
    )
    match = results_pattern.search(text)
    if match:
        sections['results'] = match.group(1).strip()[:5000]
    
    # Find discussion
    discussion_pattern = re.compile(
        r'discussion[:\s]+(.*?)(?:conclusion|references|acknowledgments)',
        re.IGNORECASE | re.DOTALL
    )
    match = discussion_pattern.search(text)
    if match:
        sections['discussion'] = match.group(1).strip()[:5000]
    
    # Find conclusion
    conclusion_pattern = re.compile(
        r'conclusion[:\s]+(.*?)(?:references|acknowledgments|appendix)',
        re.IGNORECASE | re.DOTALL
    )
    match = conclusion_pattern.search(text)
    if match:
        sections['conclusion'] = match.group(1).strip()[:3000]
    
    # Find references
    references_pattern = re.compile(
        r'references[:\s]+(.*?)$',
        re.IGNORECASE | re.DOTALL
    )
    match = references_pattern.search(text)
    if match:
        sections['references'] = match.group(1).strip()[:10000]
    
    # Log extraction quality
    extracted_sections = sum(1 for s in sections.values() if s and s != text)
    logger.info(f"Extracted {extracted_sections}/7 sections from paper")
    
    return sections


def ingest_pdf(pdf_path: Path, article_id: str, db_path: str = "./ae.db") -> bool:
    """
    Full ingestion pipeline: PDF → text → sections → database
    
    Args:
        pdf_path: Path to PDF file
        article_id: Database article ID
        db_path: Database path (default: ./ae.db)
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Ingesting PDF for article {article_id}")
    
    # Extract text
    text = extract_pdf_text(pdf_path)
    if not text:
        logger.error(f"Text extraction failed for article {article_id}")
        return False
    
    # Section text
    sections = section_paper_text(text)
    
    # Store in database
    try:
        import sqlite3
        import json
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Store full text and sections
        # Note: In production, consider storing in filesystem with DB path reference
        # to avoid bloating database
        cursor.execute("""
            UPDATE articles
            SET 
                full_text = ?,
                sections = ?,
                text_length = ?,
                ingested_at = datetime('now')
            WHERE article_id = ?
        """, (
            text,
            json.dumps(sections),
            len(text),
            article_id
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(
            f"✓ Successfully ingested {len(text)} chars for article {article_id}"
        )
        return True
        
    except Exception as e:
        logger.error(f"Database storage failed for article {article_id}: {e}")
        return False


def clean_extracted_text(text: str) -> str:
    """
    Clean extracted PDF text
    - Remove excessive whitespace
    - Fix common OCR errors
    - Normalize line breaks
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text
    """
    # Remove page headers/footers (heuristic: single line with <10 words)
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        words = line.strip().split()
        # Keep lines with >10 words or lines that end with sentence punctuation
        if len(words) > 10 or (words and words[-1][-1] in '.!?'):
            cleaned_lines.append(line)
    
    text = '\n'.join(cleaned_lines)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r' +', ' ', text)
    
    # Fix common OCR errors
    text = text.replace('ﬁ', 'fi')
    text = text.replace('ﬂ', 'fl')
    text = text.replace('–', '-')
    text = text.replace('\u2019', "'")  # Right single quotation mark
    text = text.replace('\u201c', '"')   # Left double quotation mark
    text = text.replace('\u201d', '"')   # Right double quotation mark
    
    return text.strip()


if __name__ == '__main__':
    # Test extraction
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='PDF Text Extraction')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--article-id', default='test', help='Article ID')
    parser.add_argument('--db', default='./ae.db', help='Database path')
    parser.add_argument('--sections-only', action='store_true', 
                       help='Only show section breakdown')
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        sys.exit(1)
    
    if args.sections_only:
        text = extract_pdf_text(pdf_path)
        if text:
            sections = section_paper_text(text)
            print("\nExtracted Sections:")
            print("=" * 60)
            for section_name, section_text in sections.items():
                if section_text and section_name != 'full_text':
                    preview = section_text[:200] + "..." if len(section_text) > 200 else section_text
                    print(f"\n{section_name.upper()}:")
                    print(f"  Length: {len(section_text)} chars")
                    print(f"  Preview: {preview}")
    else:
        success = ingest_pdf(pdf_path, args.article_id, args.db)
        sys.exit(0 if success else 1)
