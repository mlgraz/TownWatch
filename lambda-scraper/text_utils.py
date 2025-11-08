"""
Text Extraction and Summarization Utilities for TownWatch Scraper

Provides functions for:
- PDF text extraction (handles 400+ page documents)
- Webpage text extraction
- Extractive summarization (spaCy)
- AI-powered summarization (HuggingFace BART/T5)
- Intelligent chunking for large documents
- Key topic/phrase extraction
"""

import re
from io import BytesIO
from typing import List, Optional, Dict, Any, Tuple

import requests
import pdfplumber
from bs4 import BeautifulSoup

# HuggingFace model cache (loaded once, reused)
_hf_summarizer = None
_hf_model_name = "facebook/bart-large-cnn"  # Best free summarization model


# ============================================================================
# PDF EXTRACTION
# ============================================================================

def extract_pdf_text(pdf_url: str, max_pages: int = 1000, max_chars: int = 500000) -> str:
    """
    Extract text content from a PDF URL (handles large 400+ page documents)

    Args:
        pdf_url: URL to the PDF file
        max_pages: Maximum number of pages to extract (default: 1000 - handles large docs)
        max_chars: Maximum characters to return (default: 500000 - ~200 pages)

    Returns:
        Extracted text content, limited to max_chars
    """
    try:
        print(f"Extracting PDF from: {pdf_url}")

        # Download PDF
        response = requests.get(pdf_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; TownWatch/1.0)'
        })
        response.raise_for_status()

        # Open PDF from bytes
        pdf_file = BytesIO(response.content)

        text_parts = []
        total_chars = 0

        with pdfplumber.open(pdf_file) as pdf:
            num_pages = min(len(pdf.pages), max_pages)
            print(f"Processing {num_pages} pages from PDF")

            for page_num, page in enumerate(pdf.pages[:max_pages], 1):
                # Extract text from page
                page_text = page.extract_text()

                if page_text:
                    # Clean up text
                    page_text = clean_extracted_text(page_text)
                    text_parts.append(page_text)
                    total_chars += len(page_text)

                    # Stop if we've extracted enough
                    if total_chars >= max_chars:
                        break

        # Join all pages
        full_text = '\n\n'.join(text_parts)

        # Limit to max_chars
        if len(full_text) > max_chars:
            full_text = full_text[:max_chars] + "..."

        print(f"✓ Extracted {len(full_text)} characters from PDF")
        return full_text

    except Exception as e:
        print(f"Error extracting PDF text from {pdf_url}: {e}")
        return ""


def extract_pdf_tables(pdf_url: str, max_pages: int = 5) -> List[List[List[str]]]:
    """
    Extract tables from a PDF (useful for agendas)

    Args:
        pdf_url: URL to the PDF file
        max_pages: Maximum number of pages to process

    Returns:
        List of tables, where each table is a list of rows
    """
    try:
        response = requests.get(pdf_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; TownWatch/1.0)'
        })
        response.raise_for_status()

        pdf_file = BytesIO(response.content)
        all_tables = []

        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages[:max_pages]:
                tables = page.extract_tables()
                if tables:
                    all_tables.extend(tables)

        print(f"✓ Extracted {len(all_tables)} tables from PDF")
        return all_tables

    except Exception as e:
        print(f"Error extracting PDF tables from {pdf_url}: {e}")
        return []


def parse_agenda_table(table: List[List[str]]) -> List[Dict[str, str]]:
    """
    Parse an agenda table into structured items

    Args:
        table: A table extracted from PDF (list of rows)

    Returns:
        List of agenda items as dictionaries
    """
    agenda_items = []

    if not table or len(table) < 2:
        return agenda_items

    # Skip header row
    for row in table[1:]:
        if not row or not row[0]:
            continue

        item = {
            'item_number': row[0].strip() if row[0] else '',
            'description': row[1].strip() if len(row) > 1 and row[1] else '',
            'presenter': row[2].strip() if len(row) > 2 and row[2] else '',
            'time': row[3].strip() if len(row) > 3 and row[3] else ''
        }

        # Only add if has description
        if item['description']:
            agenda_items.append(item)

    return agenda_items


# ============================================================================
# WEBPAGE TEXT EXTRACTION
# ============================================================================

def extract_webpage_text(url: str, max_chars: int = 5000) -> str:
    """
    Extract clean text content from a webpage

    Args:
        url: URL of the webpage
        max_chars: Maximum characters to return

    Returns:
        Cleaned text content
    """
    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; TownWatch/1.0)'
        })
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Get text
        text = soup.get_text(separator=' ', strip=True)

        # Clean up
        text = clean_extracted_text(text)

        # Limit length
        if len(text) > max_chars:
            text = text[:max_chars] + "..."

        return text

    except Exception as e:
        print(f"Error extracting webpage text from {url}: {e}")
        return ""


# ============================================================================
# TEXT CLEANING
# ============================================================================

def clean_extracted_text(text: str) -> str:
    """
    Clean up extracted text (remove excessive whitespace, etc.)

    Args:
        text: Raw extracted text

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)

    # Replace multiple newlines with double newline
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    # Remove excessive whitespace
    text = text.strip()

    return text


# ============================================================================
# EXTRACTIVE SUMMARIZATION
# ============================================================================

def summarize_text_simple(text: str, num_sentences: int = 5) -> str:
    """
    Simple extractive summarization - extracts first N sentences

    This is a fallback method that doesn't require spaCy.
    For better results, use summarize_text_smart() when spaCy is available.

    Args:
        text: Input text to summarize
        num_sentences: Number of sentences to extract

    Returns:
        Summary text
    """
    if not text:
        return ""

    # Split into sentences (simple approach)
    sentences = re.split(r'[.!?]+', text)

    # Clean sentences
    sentences = [s.strip() for s in sentences if s.strip()]

    # Take first N sentences
    summary_sentences = sentences[:num_sentences]

    # Join with periods
    summary = '. '.join(summary_sentences)

    # Add final period if missing
    if summary and not summary.endswith('.'):
        summary += '.'

    return summary


def summarize_text_smart(text: str, num_sentences: int = 5, max_chars: int = 2000) -> str:
    """
    Smart extractive summarization using spaCy

    Extracts the most important sentences based on keyword frequency
    and position in text.

    Args:
        text: Input text to summarize
        num_sentences: Number of sentences to extract
        max_chars: Maximum characters in summary

    Returns:
        Summary text
    """
    try:
        import spacy

        # Try to load spaCy model
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found, falling back to simple summarization")
            return summarize_text_simple(text, num_sentences)

        # Limit input text to avoid processing too much
        if len(text) > 50000:
            text = text[:50000]

        # Process text
        doc = nlp(text)

        # Score sentences based on word frequency and position
        sentence_scores = {}
        word_frequencies = {}

        # Calculate word frequencies
        for token in doc:
            if not token.is_stop and not token.is_punct and token.text.strip():
                word = token.text.lower()
                word_frequencies[word] = word_frequencies.get(word, 0) + 1

        # Normalize frequencies
        if word_frequencies:
            max_freq = max(word_frequencies.values())
            word_frequencies = {k: v/max_freq for k, v in word_frequencies.items()}

        # Score sentences
        for sent_idx, sent in enumerate(doc.sents):
            score = 0
            word_count = 0

            for token in sent:
                if token.text.lower() in word_frequencies:
                    score += word_frequencies[token.text.lower()]
                    word_count += 1

            # Average score per word
            if word_count > 0:
                score = score / word_count

            # Boost score for sentences near beginning (important context)
            if sent_idx < 3:
                score *= 1.5

            sentence_scores[sent.text] = score

        # Get top N sentences
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        top_sentences = top_sentences[:num_sentences]

        # Re-order sentences by their original position in text
        sentences_in_order = []
        for sent in doc.sents:
            for selected_sent, score in top_sentences:
                if sent.text == selected_sent:
                    sentences_in_order.append(sent.text)
                    break

        # Join sentences
        summary = ' '.join(sentences_in_order)

        # Limit to max_chars
        if len(summary) > max_chars:
            summary = summary[:max_chars] + "..."

        return summary

    except ImportError:
        print("Warning: spaCy not available, using simple summarization")
        return summarize_text_simple(text, num_sentences)
    except Exception as e:
        print(f"Error in smart summarization: {e}, falling back to simple")
        return summarize_text_simple(text, num_sentences)


def extract_key_phrases(text: str, top_n: int = 10) -> List[str]:
    """
    Extract key phrases/topics from text using frequency analysis

    Args:
        text: Input text
        top_n: Number of key phrases to return

    Returns:
        List of key phrases
    """
    try:
        import spacy

        # Try to load spaCy model
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found, using simple keyword extraction")
            return extract_keywords_simple(text, top_n)

        # Limit text
        if len(text) > 10000:
            text = text[:10000]

        doc = nlp(text)

        # Extract noun chunks and named entities
        key_phrases = []

        # Add noun chunks
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 3:  # Max 3 words
                key_phrases.append(chunk.text.lower())

        # Add named entities
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'GPE', 'LOC', 'PERSON', 'EVENT', 'LAW']:
                key_phrases.append(ent.text.lower())

        # Count frequencies
        phrase_freq = {}
        for phrase in key_phrases:
            phrase = phrase.strip()
            if len(phrase) > 3:  # Minimum length
                phrase_freq[phrase] = phrase_freq.get(phrase, 0) + 1

        # Sort by frequency
        top_phrases = sorted(phrase_freq.items(), key=lambda x: x[1], reverse=True)

        # Return top N unique phrases
        return [phrase for phrase, count in top_phrases[:top_n]]

    except Exception as e:
        print(f"Error extracting key phrases: {e}")
        return extract_keywords_simple(text, top_n)


def extract_keywords_simple(text: str, top_n: int = 10) -> List[str]:
    """
    Simple keyword extraction (fallback when spaCy not available)

    Args:
        text: Input text
        top_n: Number of keywords to return

    Returns:
        List of keywords
    """
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                  'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'be', 'been',
                  'this', 'that', 'these', 'those', 'will', 'would', 'should', 'could'}

    # Extract words
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())

    # Filter stop words
    words = [w for w in words if w not in stop_words]

    # Count frequencies
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1

    # Sort by frequency
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

    return [word for word, count in top_words[:top_n]]


# ============================================================================
# HUGGINGFACE AI SUMMARIZATION (FREE, HIGH QUALITY)
# ============================================================================

def get_huggingface_summarizer():
    """
    Load HuggingFace summarization model (cached for reuse)
    Uses BART-large-CNN - best free summarization model

    Returns:
        Summarization pipeline
    """
    global _hf_summarizer

    if _hf_summarizer is not None:
        return _hf_summarizer

    try:
        from transformers import pipeline
        print(f"Loading HuggingFace model: {_hf_model_name}")

        # Load model with optimizations for Lambda
        _hf_summarizer = pipeline(
            "summarization",
            model=_hf_model_name,
            device=-1,  # Use CPU (Lambda doesn't have GPU)
            framework="pt"  # PyTorch
        )

        print("✓ HuggingFace model loaded successfully")
        return _hf_summarizer

    except Exception as e:
        print(f"Error loading HuggingFace model: {e}")
        print("Falling back to spaCy summarization")
        return None


def chunk_text_intelligently(text: str, max_chunk_size: int = 1024) -> List[str]:
    """
    Split large text into intelligent chunks for processing

    Tries to split on:
    1. Section headers (all caps lines, numbered sections)
    2. Paragraph breaks
    3. Sentence boundaries

    Args:
        text: Input text to chunk
        max_chunk_size: Maximum tokens per chunk (BART limit is 1024)

    Returns:
        List of text chunks
    """
    if not text:
        return []

    # Rough estimate: 1 token ≈ 4 characters
    max_chars = max_chunk_size * 4

    chunks = []

    # Split on major section headers first (all caps lines)
    section_pattern = r'\n([A-Z][A-Z\s]{10,})\n'
    sections = re.split(section_pattern, text)

    current_chunk = ""

    for section in sections:
        # If adding this section would exceed limit, save current chunk
        if len(current_chunk) + len(section) > max_chars and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = ""

        current_chunk += section + "\n"

    # Add final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    # If no good section splits found, split on paragraphs
    if len(chunks) <= 1:
        chunks = []
        paragraphs = text.split('\n\n')
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) > max_chars and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            current_chunk += para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

    return chunks


def extract_interesting_sections(text: str, top_n: int = 5) -> str:
    """
    Extract the most "interesting" sections from a large document

    Interesting = Contains:
    - Dollar amounts (budget discussions)
    - Votes/decisions ("approved", "voted", "passed")
    - Action items ("will", "shall", "must")
    - Controversy indicators ("opposed", "objection", "concern")
    - Policy changes ("amend", "revise", "new policy")

    Args:
        text: Full document text
        top_n: Number of top sections to return

    Returns:
        Filtered text with most interesting content
    """
    # Split into chunks
    chunks = chunk_text_intelligently(text, max_chunk_size=1024)

    # Score each chunk
    scored_chunks = []

    for chunk in chunks:
        score = 0
        chunk_lower = chunk.lower()

        # High-value indicators
        if re.search(r'\$[\d,]+(?:\.\d+)?(?:\s?(?:million|billion|thousand))?', chunk):
            score += 10  # Budget/money mentions

        if re.search(r'\b(vote|voted|approved|passed|rejected|opposed)\b', chunk_lower):
            score += 8  # Decisions/votes

        if re.search(r'\b(resolution|ordinance|bill|legislation|policy)\b', chunk_lower):
            score += 7  # Policy items

        if re.search(r'\b(concern|objection|oppose|controversial|debate)\b', chunk_lower):
            score += 6  # Controversy

        if re.search(r'\b(will|shall|must|require)\b', chunk_lower):
            score += 5  # Action items

        if re.search(r'\b(amend|revise|change|new|establish)\b', chunk_lower):
            score += 5  # Changes

        # Penalty for procedural text
        if re.search(r'\b(call to order|pledge of allegiance|roll call|minutes approved)\b', chunk_lower):
            score -= 5  # Boring procedural stuff

        # Bonus for being near the beginning (often has key items)
        if chunks.index(chunk) < 3:
            score += 3

        scored_chunks.append((score, chunk))

    # Sort by score and take top N
    scored_chunks.sort(reverse=True, key=lambda x: x[0])
    top_chunks = [chunk for score, chunk in scored_chunks[:top_n]]

    return "\n\n".join(top_chunks)


def summarize_with_huggingface(text: str, max_length: int = 500, min_length: int = 100,
                                filter_interesting: bool = True) -> str:
    """
    Summarize text using HuggingFace BART model (FREE, high quality)

    Args:
        text: Input text to summarize
        max_length: Maximum length of summary (in tokens)
        min_length: Minimum length of summary (in tokens)
        filter_interesting: If True, pre-filter text to most interesting sections

    Returns:
        AI-generated summary
    """
    try:
        # Load model
        summarizer = get_huggingface_summarizer()

        if summarizer is None:
            # Fallback to spaCy if HuggingFace fails
            print("HuggingFace not available, using spaCy")
            return summarize_text_smart(text, num_sentences=5)

        # For very large documents, extract interesting sections first
        if filter_interesting and len(text) > 10000:
            print(f"Large document detected ({len(text)} chars), filtering to interesting sections...")
            text = extract_interesting_sections(text, top_n=5)
            print(f"Filtered to {len(text)} chars of interesting content")

        # Chunk text if still too large
        chunks = chunk_text_intelligently(text, max_chunk_size=1024)

        if len(chunks) == 0:
            return "No content to summarize."

        print(f"Summarizing {len(chunks)} chunks with HuggingFace BART...")

        summaries = []

        for i, chunk in enumerate(chunks[:10], 1):  # Limit to 10 chunks for performance
            try:
                # BART can handle up to 1024 tokens input
                result = summarizer(
                    chunk,
                    max_length=max_length // len(chunks[:10]),  # Split summary length across chunks
                    min_length=min(min_length, max_length // len(chunks[:10]) - 10),
                    do_sample=False,  # Deterministic output
                    truncation=True
                )

                if result and len(result) > 0:
                    summary_text = result[0]['summary_text']
                    summaries.append(summary_text)
                    print(f"  ✓ Chunk {i}/{len(chunks[:10])} summarized")

            except Exception as e:
                print(f"  ✗ Error summarizing chunk {i}: {e}")
                continue

        # Combine summaries
        final_summary = " ".join(summaries)

        # If combined summary is still too long, summarize again
        if len(final_summary) > max_length * 4:  # Rough char estimate
            print("Combined summary too long, doing second-pass summarization...")
            result = summarizer(
                final_summary,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
                truncation=True
            )
            final_summary = result[0]['summary_text']

        print(f"✓ Final summary: {len(final_summary)} characters")
        return final_summary

    except Exception as e:
        print(f"Error in HuggingFace summarization: {e}")
        print("Falling back to spaCy summarization")
        return summarize_text_smart(text, num_sentences=5)


# ============================================================================
# COMBINED EXTRACTION & SUMMARIZATION
# ============================================================================

def extract_and_summarize(pdf_url: Optional[str] = None,
                         webpage_url: Optional[str] = None,
                         summary_length: int = 5,
                         method: str = 'huggingface',
                         pdf_max_pages: int = 1000,
                         pdf_max_chars: int = 500000,
                         webpage_max_chars: int = 8000) -> Dict[str, Any]:
    """
    Extract content from PDF/webpage and create a summary

    Args:
        pdf_url: URL to PDF file (optional)
        webpage_url: URL to webpage (optional)
        summary_length: Number of sentences in summary (for spaCy) or tokens (for HuggingFace)
        method: 'huggingface' (AI, best quality), 'smart' (spaCy), or 'simple' (basic)
        pdf_max_pages: Max pages to extract (default: 1000 for large docs)
        pdf_max_chars: Max characters to extract (default: 500000)
        webpage_max_chars: Max characters from webpage

    Returns:
        Dictionary with 'full_text', 'summary', and 'key_phrases'
    """
    full_text_parts = []

    # Extract from PDF
    if pdf_url:
        pdf_text = extract_pdf_text(pdf_url, max_pages=pdf_max_pages, max_chars=pdf_max_chars)
        if pdf_text:
            full_text_parts.append(pdf_text)

    # Extract from webpage
    if webpage_url:
        web_text = extract_webpage_text(webpage_url, max_chars=webpage_max_chars)
        if web_text:
            full_text_parts.append(web_text)

    # Combine text
    full_text = '\n\n'.join(full_text_parts)

    if not full_text:
        return {
            'full_text': '',
            'summary': '',
            'key_phrases': []
        }

    # Create summary based on method
    if method == 'huggingface':
        # Use AI summarization (best quality)
        summary = summarize_with_huggingface(
            full_text,
            max_length=summary_length * 30 if summary_length > 10 else 500,  # Convert sentences to tokens estimate
            min_length=100,
            filter_interesting=True
        )
    elif method == 'smart':
        # Use spaCy (good quality, no AI needed)
        summary = summarize_text_smart(full_text, num_sentences=summary_length)
    else:
        # Use simple extraction (basic, always works)
        summary = summarize_text_simple(full_text, num_sentences=summary_length)

    # Extract key phrases
    key_phrases = extract_key_phrases(full_text, top_n=10)

    return {
        'full_text': full_text,
        'summary': summary,
        'key_phrases': key_phrases
    }
