#!/usr/bin/env python3
"""
Local Test Scraper - Full Workflow Testing

This script runs the Maryland scraper locally and saves results to JSON files
so you can review the quality of extraction and summarization before deploying.

No Supabase required - saves to local files.

Usage:
    python test_scraper_local.py
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any

# Import scraper functions from optimized pipeline
from maryland_scraper_v2 import (
    scrape_md_general_assembly,
    scrape_baltimore_board_of_estimates,
    scrape_baltimore_city_council,
    scrape_legistar_calendar,
    detect_topics
)

OUTPUT_DIR = "test_output"


def setup_output_directory():
    """Create output directory if it doesn't exist"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"✓ Created output directory: {OUTPUT_DIR}/")
    else:
        print(f"✓ Using output directory: {OUTPUT_DIR}/")


def save_to_json(data: Any, filename: str):
    """Save data to JSON file"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  💾 Saved to: {filepath}")


def print_document_preview(doc: Dict[str, Any], index: int):
    """Print a preview of a scraped document"""
    print(f"\n  📄 Document {index}:")
    print(f"     Title: {doc.get('title', 'N/A')[:80]}")
    print(f"     Date: {doc.get('date', 'N/A')}")
    print(f"     Source: {doc.get('source', 'N/A')}")
    print(f"     Jurisdiction: {doc.get('jurisdiction', 'N/A')}")
    print(f"     Topics: {', '.join(doc.get('topics', []))}")
    print(f"     Content length: {len(doc.get('content', ''))} characters")

    # Show content preview
    content = doc.get('content', '')
    if content:
        preview = content[:150].replace('\n', ' ')
        print(f"     Preview: {preview}...")


def generate_summary_report(all_results: Dict[str, List[Dict[str, Any]]]):
    """Generate a summary report of scraping results"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_sources_scraped': len(all_results),
        'sources': {}
    }

    total_docs = 0
    total_with_content = 0
    total_content_length = 0

    for source_name, docs in all_results.items():
        docs_with_real_content = [d for d in docs if len(d.get('content', '')) > 100]
        avg_content_length = sum(len(d.get('content', '')) for d in docs) / len(docs) if docs else 0

        report['sources'][source_name] = {
            'documents_found': len(docs),
            'documents_with_content': len(docs_with_real_content),
            'average_content_length': int(avg_content_length),
            'topics_found': list(set(topic for doc in docs for topic in doc.get('topics', [])))
        }

        total_docs += len(docs)
        total_with_content += len(docs_with_real_content)
        total_content_length += sum(len(d.get('content', '')) for d in docs)

    report['totals'] = {
        'total_documents': total_docs,
        'documents_with_real_content': total_with_content,
        'average_content_length': int(total_content_length / total_docs) if total_docs else 0,
        'extraction_success_rate': f"{(total_with_content/total_docs*100) if total_docs else 0:.1f}%"
    }

    return report


def test_single_scraper(scraper_name: str, scraper_func, *args):
    """Test a single scraper function"""
    print(f"\n{'='*80}")
    print(f"Testing: {scraper_name}")
    print(f"{'='*80}")

    try:
        print(f"🔄 Scraping {scraper_name}...")
        documents = scraper_func(*args)

        print(f"✅ Success! Found {len(documents)} documents")

        # Show previews of first 3 documents
        for i, doc in enumerate(documents[:3], 1):
            print_document_preview(doc, i)

        if len(documents) > 3:
            print(f"\n  ... and {len(documents) - 3} more documents")

        # Save to JSON
        filename = f"{scraper_name.lower().replace(' ', '_')}.json"
        save_to_json(documents, filename)

        return documents

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def main():
    """Run local scraper tests"""
    print("\n" + "="*80)
    print("POLLYVIEW LOCAL SCRAPER TEST - FULL WORKFLOW")
    print("="*80)
    print("\nThis will:")
    print("  1. Scrape real Maryland government websites")
    print("  2. Extract PDF content and create summaries")
    print("  3. Detect topics from actual content")
    print("  4. Save results to local JSON files for review")
    print("\n⚠️  Note: This may take 1-2 minutes as it downloads and processes PDFs")
    print("="*80)

    # Setup
    setup_output_directory()

    # Store all results
    all_results = {}

    # Test 1: Baltimore Board of Estimates (has PDFs to extract!)
    docs = test_single_scraper(
        "Baltimore Board of Estimates",
        scrape_baltimore_board_of_estimates
    )
    all_results['Baltimore BOE'] = docs

    # Test 2: Baltimore City Council
    docs = test_single_scraper(
        "Baltimore City Council",
        scrape_baltimore_city_council
    )
    all_results['Baltimore City Council'] = docs

    # Test 3: Maryland General Assembly
    docs = test_single_scraper(
        "Maryland General Assembly",
        scrape_md_general_assembly
    )
    all_results['MD General Assembly'] = docs

    # Test 4: Montgomery County (Legistar)
    docs = test_single_scraper(
        "Montgomery County Council",
        scrape_legistar_calendar,
        'https://montgomerycountymd.legistar.com/Calendar.aspx',
        'Montgomery County',
        'County Council'
    )
    all_results['Montgomery County'] = docs

    # Test 5: Prince George's County (Legistar)
    docs = test_single_scraper(
        "Prince Georges County Council",
        scrape_legistar_calendar,
        'https://princegeorgescountymd.legistar.com/Calendar.aspx',
        "Prince George's County",
        'County Council'
    )
    all_results['Prince Georges County'] = docs

    # Generate summary report
    print(f"\n{'='*80}")
    print("GENERATING SUMMARY REPORT")
    print(f"{'='*80}")

    report = generate_summary_report(all_results)
    save_to_json(report, 'scraping_summary_report.json')

    # Save all documents together
    all_docs_combined = []
    for source, docs in all_results.items():
        all_docs_combined.extend(docs)
    save_to_json(all_docs_combined, 'all_documents_combined.json')

    # Print final summary
    print(f"\n{'='*80}")
    print("SCRAPING COMPLETE! 🎉")
    print(f"{'='*80}")
    print(f"\n📊 Summary:")
    print(f"   Total sources scraped: {report['total_sources_scraped']}")
    print(f"   Total documents found: {report['totals']['total_documents']}")
    print(f"   Documents with real content: {report['totals']['documents_with_real_content']}")
    print(f"   Average content length: {report['totals']['average_content_length']} chars")
    print(f"   Extraction success rate: {report['totals']['extraction_success_rate']}")

    print(f"\n📁 Output files in {OUTPUT_DIR}/:")
    print(f"   • all_documents_combined.json - All {len(all_docs_combined)} documents")
    print(f"   • scraping_summary_report.json - Detailed statistics")
    for source_name in all_results.keys():
        filename = f"{source_name.lower().replace(' ', '_')}.json"
        print(f"   • {filename} - {source_name} documents")

    print(f"\n🔍 Review the files to see:")
    print(f"   • Quality of PDF extraction")
    print(f"   • Summary accuracy")
    print(f"   • Topic detection from real content")
    print(f"   • Searchable document text")

    print(f"\n✅ Next steps:")
    print(f"   1. Review the JSON files in {OUTPUT_DIR}/")
    print(f"   2. Check scraping_summary_report.json for statistics")
    print(f"   3. Look at specific source files to see extraction quality")
    print(f"   4. If satisfied, deploy to Lambda and connect to Supabase!")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
