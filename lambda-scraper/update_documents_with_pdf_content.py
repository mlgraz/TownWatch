#!/usr/bin/env python3
"""
Update existing Supabase documents with real PDF-extracted content

This script:
1. Loads existing documents from Supabase
2. Loads our scraped documents with PDF extraction (from JSON)
3. Updates the Supabase documents with the real content
"""

import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

def update_documents():
    """Update documents with PDF-extracted content"""
    print("\n" + "="*80)
    print("UPDATING SUPABASE DOCUMENTS WITH PDF-EXTRACTED CONTENT")
    print("="*80)

    try:
        # Connect to Supabase
        print("\n🔄 Connecting to Supabase...")
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected!")

        # Load our scraped documents with PDF content
        print("\n🔄 Loading scraped documents with PDF content...")
        with open('test_output/baltimore_board_of_estimates.json', 'r') as f:
            scraped_docs = json.load(f)
        print(f"✅ Loaded {len(scraped_docs)} documents with PDF content")

        # Get existing documents from Supabase
        print("\n🔄 Fetching existing documents from Supabase...")
        result = supabase.table('documents').select('*').execute()
        existing_docs = result.data
        print(f"✅ Found {len(existing_docs)} existing documents")

        # Match and update
        print("\n🔄 Matching and updating documents...")
        updated_count = 0
        not_found_count = 0

        for scraped in scraped_docs:
            # Find matching document by title and date
            title = scraped['title']
            date = scraped['date']

            # Find in existing
            matching = [d for d in existing_docs if d['title'] == title and d['document_date'] == date]

            if matching:
                existing_id = matching[0]['id']
                old_content = matching[0]['content'][:100] + "..." if matching[0]['content'] else "No content"
                new_content = scraped['content'][:100] + "..."

                print(f"\n  📝 Updating: {title}")
                print(f"     Old content ({len(matching[0]['content'])} chars): {old_content}")
                print(f"     New content ({len(scraped['content'])} chars): {new_content}")

                # Clean content - remove null bytes and other problematic characters
                clean_content = scraped['content'].replace('\x00', '').replace('\u0000', '')

                # Update the document
                update_result = supabase.table('documents').update({
                    'content': clean_content,
                    'updated_at': 'now()'
                }).eq('id', existing_id).execute()

                if update_result.data:
                    updated_count += 1
                    print(f"     ✅ Updated!")
                else:
                    print(f"     ❌ Update failed")

            else:
                not_found_count += 1
                print(f"\n  ⚠️  No match found for: {title} ({date})")

        # Summary
        print("\n" + "="*80)
        print("UPDATE COMPLETE!")
        print("="*80)
        print(f"\n✅ Updated: {updated_count} documents")
        print(f"⚠️  Not found: {not_found_count} documents")
        print(f"\nDocuments now have real PDF-extracted content!")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    update_documents()
