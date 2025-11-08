#!/usr/bin/env python3
"""
Check Supabase Connection and Schema

Tests connection to Supabase and checks if the database schema is set up.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

def check_connection():
    """Check if we can connect to Supabase"""
    print("\n" + "="*80)
    print("CHECKING SUPABASE CONNECTION")
    print("="*80)

    print(f"\nSupabase URL: {SUPABASE_URL}")
    print(f"API Key: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "API Key: Not found")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("\n❌ ERROR: Supabase credentials not found in .env file")
        return False

    try:
        print("\n🔄 Connecting to Supabase...")
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connection successful!")
        return supabase
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        return False


def check_schema(supabase: Client):
    """Check if the documents table exists and has the correct schema"""
    print("\n" + "="*80)
    print("CHECKING DATABASE SCHEMA")
    print("="*80)

    try:
        print("\n🔄 Checking if 'documents' table exists...")

        # Try to query the documents table
        result = supabase.table('documents').select('*').limit(1).execute()

        print("✅ Table 'documents' exists!")

        # Check how many documents are already there
        count_result = supabase.table('documents').select('id', count='exact').execute()
        doc_count = count_result.count if hasattr(count_result, 'count') else len(count_result.data)

        print(f"📊 Current documents in database: {doc_count}")

        if doc_count > 0:
            print("\n📄 Sample document:")
            sample = supabase.table('documents').select('title, date, source, jurisdiction').limit(1).execute()
            if sample.data:
                doc = sample.data[0]
                print(f"   Title: {doc.get('title', 'N/A')}")
                print(f"   Date: {doc.get('date', 'N/A')}")
                print(f"   Source: {doc.get('source', 'N/A')}")
                print(f"   Jurisdiction: {doc.get('jurisdiction', 'N/A')}")

        return True

    except Exception as e:
        print(f"❌ Schema check failed: {e}")
        print("\n📋 The database schema may not be set up yet.")
        print("\nTo set up the schema:")
        print("1. Go to your Supabase dashboard: https://app.supabase.com")
        print(f"2. Open your project: {SUPABASE_URL}")
        print("3. Go to SQL Editor (left sidebar)")
        print("4. Run the SQL from: lambda-scraper/setup_supabase.sql")
        return False


def main():
    """Run all checks"""
    print("\n" + "="*80)
    print("POLLYVIEW SUPABASE CONNECTION CHECK")
    print("="*80)

    # Check connection
    supabase = check_connection()
    if not supabase:
        print("\n❌ Cannot proceed - fix connection issues first")
        return False

    # Check schema
    schema_ok = check_schema(supabase)

    # Final summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    if schema_ok:
        print("\n✅ Everything is ready!")
        print("\nNext step: Run the scraper to store data")
        print("Command: python maryland_scraper.py")
    else:
        print("\n⚠️  Schema needs to be set up")
        print("\nNext step: Run the SQL schema in Supabase")
        print("File: lambda-scraper/setup_supabase.sql")

    print("="*80 + "\n")

    return schema_ok


if __name__ == "__main__":
    main()
