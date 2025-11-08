#!/usr/bin/env python3
"""
Inspect current Supabase schema

Checks what columns and structure currently exist in the documents table.
"""

import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

def inspect_schema():
    """Inspect the current schema"""
    print("\n" + "="*80)
    print("INSPECTING CURRENT SUPABASE SCHEMA")
    print("="*80)

    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Get all columns by selecting all fields from one document
        print("\n🔄 Fetching sample document...")
        result = supabase.table('documents').select('*').limit(1).execute()

        if result.data and len(result.data) > 0:
            doc = result.data[0]

            print("\n✅ Found document!")
            print("\n📋 Current schema (columns):")
            for key in doc.keys():
                value = doc[key]
                value_type = type(value).__name__
                value_preview = str(value)[:50] if value else "NULL"
                print(f"   • {key:20} ({value_type:10}) = {value_preview}...")

            print("\n📄 Full sample document:")
            print(json.dumps(doc, indent=2, default=str))

            # Count documents
            count_result = supabase.table('documents').select('id', count='exact').execute()
            doc_count = count_result.count if hasattr(count_result, 'count') else len(count_result.data)
            print(f"\n📊 Total documents in database: {doc_count}")

        else:
            print("\n⚠️ No documents found in table")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_schema()
