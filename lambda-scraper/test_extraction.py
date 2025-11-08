#!/usr/bin/env python3
"""
Test script for PDF extraction and text summarization

This script tests the new text extraction and summarization features
without needing to run the full scraper or deploy to Lambda.

Usage:
    python test_extraction.py
"""

from text_utils import (
    extract_pdf_text,
    extract_webpage_text,
    extract_and_summarize,
    summarize_text_smart,
    summarize_text_simple
)

def test_pdf_extraction():
    """Test PDF text extraction with a sample government PDF"""
    print("\n" + "="*70)
    print("TEST 1: PDF Text Extraction")
    print("="*70)

    # Example: Baltimore Board of Estimates agenda (replace with actual URL)
    sample_pdf_url = "https://example.gov/agenda.pdf"

    print(f"\nExtracting text from: {sample_pdf_url}")
    print("(This will fail if the URL is not accessible - that's expected for testing)")

    try:
        pdf_text = extract_pdf_text(sample_pdf_url, max_pages=3, max_chars=2000)

        if pdf_text:
            print(f"\n✓ Successfully extracted {len(pdf_text)} characters")
            print(f"\nFirst 500 characters:")
            print("-" * 70)
            print(pdf_text[:500])
            print("-" * 70)
        else:
            print("\n✗ No text extracted (PDF may not be accessible)")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("(This is expected if the sample URL is not a real PDF)")


def test_webpage_extraction():
    """Test webpage text extraction"""
    print("\n" + "="*70)
    print("TEST 2: Webpage Text Extraction")
    print("="*70)

    # Use a real government website for testing
    sample_url = "https://mgaleg.maryland.gov"

    print(f"\nExtracting text from: {sample_url}")

    try:
        webpage_text = extract_webpage_text(sample_url, max_chars=2000)

        if webpage_text:
            print(f"\n✓ Successfully extracted {len(webpage_text)} characters")
            print(f"\nFirst 500 characters:")
            print("-" * 70)
            print(webpage_text[:500])
            print("-" * 70)
        else:
            print("\n✗ No text extracted")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def test_simple_summarization():
    """Test simple summarization (no spaCy required)"""
    print("\n" + "="*70)
    print("TEST 3: Simple Extractive Summarization")
    print("="*70)

    sample_text = """
    The Baltimore City Council met on Tuesday to discuss the proposed housing development
    project in East Baltimore. The project includes 500 new affordable housing units and
    a community center. Council members raised concerns about parking availability and
    impact on local traffic patterns. The developer presented updated traffic studies
    showing minimal impact during peak hours. A vote on the project is scheduled for
    next month. The planning commission recommended approval with conditions including
    additional green space and increased parking. Community members testified both for
    and against the proposal during the public comment period.
    """

    print("\nOriginal text length:", len(sample_text), "characters")

    summary = summarize_text_simple(sample_text, num_sentences=3)

    print(f"\n✓ Summary created ({len(summary)} characters):")
    print("-" * 70)
    print(summary)
    print("-" * 70)


def test_smart_summarization():
    """Test smart summarization with spaCy (if available)"""
    print("\n" + "="*70)
    print("TEST 4: Smart Extractive Summarization (requires spaCy)")
    print("="*70)

    sample_text = """
    The Maryland General Assembly convened today to debate House Bill 1234, which proposes
    significant changes to the state's education funding formula. The bill would increase
    per-pupil funding by 15% over the next three years, with additional allocations for
    schools in economically disadvantaged areas. Supporters argue the measure is necessary
    to address longstanding inequities in school funding across the state. Critics worry
    about the fiscal impact and whether existing tax revenues can support the increase.
    The Ways and Means Committee heard testimony from educators, parents, and budget analysts.
    Committee Chair Delegate Smith indicated the committee would likely approve the bill with
    amendments to phase in the funding increases more gradually. A floor vote is expected
    within two weeks. Governor Johnson has indicated support for increased education funding
    but has not yet committed to signing this specific proposal.
    """

    print("\nOriginal text length:", len(sample_text), "characters")

    try:
        summary = summarize_text_smart(sample_text, num_sentences=3)

        print(f"\n✓ Smart summary created ({len(summary)} characters):")
        print("-" * 70)
        print(summary)
        print("-" * 70)

    except Exception as e:
        print(f"\n✗ Smart summarization failed (spaCy may not be installed): {e}")
        print("Falling back to simple summarization...")
        summary = summarize_text_simple(sample_text, num_sentences=3)
        print(f"\n✓ Simple summary ({len(summary)} characters):")
        print("-" * 70)
        print(summary)
        print("-" * 70)


def test_combined_extraction():
    """Test the combined extract_and_summarize function"""
    print("\n" + "="*70)
    print("TEST 5: Combined Extraction & Summarization")
    print("="*70)

    print("\nThis test combines PDF extraction, webpage extraction, and summarization")
    print("(Will use webpage only since PDF URL is a placeholder)")

    # Use real webpage for testing
    webpage_url = "https://mgaleg.maryland.gov"

    try:
        result = extract_and_summarize(
            pdf_url=None,  # No PDF for this test
            webpage_url=webpage_url,
            summary_length=3,
            method='smart'
        )

        print(f"\n✓ Full text extracted: {len(result['full_text'])} characters")
        print(f"✓ Summary created: {len(result['summary'])} characters")
        print(f"✓ Key phrases found: {len(result['key_phrases'])}")

        print("\nSummary:")
        print("-" * 70)
        print(result['summary'])
        print("-" * 70)

        print("\nKey Phrases:")
        print(", ".join(result['key_phrases'][:5]))

    except Exception as e:
        print(f"\n✗ Error: {e}")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("POLLYVIEW TEXT EXTRACTION & SUMMARIZATION TESTS")
    print("="*70)

    print("\nThese tests demonstrate the new PDF extraction and summarization features.")
    print("Some tests may fail if dependencies are not installed or URLs are inaccessible.")
    print("That's expected for local testing.")

    # Run tests
    test_simple_summarization()  # Always works
    test_smart_summarization()   # Requires spaCy
    test_webpage_extraction()    # Requires internet
    test_pdf_extraction()        # May fail with placeholder URL
    test_combined_extraction()   # Requires internet

    print("\n" + "="*70)
    print("TESTS COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Download spaCy model: python -m spacy download en_core_web_sm")
    print("3. Run the scraper: python maryland_scraper.py")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
