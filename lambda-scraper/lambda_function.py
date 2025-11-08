"""
AWS Lambda function for scraping government websites and storing in Supabase

This script scrapes meeting notes from local government websites and stores them
in the TownWatch Supabase database using the OPTIMIZED SCHEMA.

Requirements (add to requirements.txt):
- requests
- beautifulsoup4
- supabase
- python-dateutil
"""

import json
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import uuid4

import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

# Initialize Supabase client
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Scraper version for tracking
SCRAPER_VERSION = "2.0.0"

# Cache for database lookups to reduce queries
_cache = {
    'countries': {},
    'states': {},
    'sources': {},
    'topics': {}
}


# ============================================================================
# DATABASE HELPER FUNCTIONS (for optimized schema)
# ============================================================================

def get_or_create_country(country_code: str, country_name: str) -> int:
    """Get country ID or create if doesn't exist"""
    # Check cache
    if country_code in _cache['countries']:
        return _cache['countries'][country_code]

    try:
        # Try to fetch existing
        result = supabase.table('countries').select('id').eq('code', country_code).execute()
        if result.data:
            country_id = result.data[0]['id']
            _cache['countries'][country_code] = country_id
            return country_id

        # Create new country
        result = supabase.table('countries').insert({
            'code': country_code,
            'name': country_name
        }).execute()
        country_id = result.data[0]['id']
        _cache['countries'][country_code] = country_id
        return country_id
    except Exception as e:
        print(f"Error getting/creating country {country_code}: {e}")
        return 1  # Default to US


def get_or_create_state(country_id: int, state_code: str, state_name: str) -> int:
    """Get state ID or create if doesn't exist"""
    cache_key = f"{country_id}:{state_code}"

    # Check cache
    if cache_key in _cache['states']:
        return _cache['states'][cache_key]

    try:
        # Try to fetch existing
        result = supabase.table('states').select('id').eq('country_id', country_id).eq('code', state_code).execute()
        if result.data:
            state_id = result.data[0]['id']
            _cache['states'][cache_key] = state_id
            return state_id

        # Create new state
        result = supabase.table('states').insert({
            'country_id': country_id,
            'code': state_code,
            'name': state_name
        }).execute()
        state_id = result.data[0]['id']
        _cache['states'][cache_key] = state_id
        return state_id
    except Exception as e:
        print(f"Error getting/creating state {state_code}: {e}")
        return 1  # Default to first state


def get_or_create_source(name: str, source_type: str, state_id: int, website_url: Optional[str] = None) -> int:
    """Get source ID or create if doesn't exist"""
    cache_key = f"{name}:{state_id}"

    # Check cache
    if cache_key in _cache['sources']:
        return _cache['sources'][cache_key]

    try:
        # Try to fetch existing
        result = supabase.table('sources').select('id').eq('name', name).eq('state_id', state_id).execute()
        if result.data:
            source_id = result.data[0]['id']
            _cache['sources'][cache_key] = source_id
            return source_id

        # Create new source
        result = supabase.table('sources').insert({
            'name': name,
            'source_type': source_type,
            'state_id': state_id,
            'website_url': website_url,
            'is_active': True
        }).execute()
        source_id = result.data[0]['id']
        _cache['sources'][cache_key] = source_id
        return source_id
    except Exception as e:
        print(f"Error getting/creating source {name}: {e}")
        return 1  # Default to first source


def get_or_create_topic(topic_name: str) -> int:
    """Get topic ID or create if doesn't exist"""
    # Check cache
    if topic_name in _cache['topics']:
        return _cache['topics'][topic_name]

    try:
        # Try to fetch existing (case-insensitive)
        result = supabase.table('topics').select('id').ilike('name', topic_name).execute()
        if result.data:
            topic_id = result.data[0]['id']
            _cache['topics'][topic_name] = topic_id
            return topic_id

        # Create new topic with slug
        slug = topic_name.lower().replace(' ', '-').replace('&', 'and')
        result = supabase.table('topics').insert({
            'name': topic_name,
            'slug': slug,
            'description': f'Auto-generated topic for {topic_name}'
        }).execute()
        topic_id = result.data[0]['id']
        _cache['topics'][topic_name] = topic_id
        return topic_id
    except Exception as e:
        print(f"Error getting/creating topic {topic_name}: {e}")
        return 1  # Default to first topic


def calculate_content_hash(content: str) -> str:
    """Calculate SHA-256 hash of content for deduplication"""
    if not content:
        return hashlib.sha256(b'').hexdigest()
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def find_duplicate_by_hash(content_hash: str) -> Optional[str]:
    """Check if document with this content hash already exists"""
    try:
        result = supabase.table('documents').select('id').eq('content_hash', content_hash).limit(1).execute()
        if result.data:
            return result.data[0]['id']
        return None
    except Exception as e:
        print(f"Error checking for duplicate: {e}")
        return None


def create_scraper_run(source_id: int) -> str:
    """Create a new scraper run record and return the run ID"""
    try:
        result = supabase.table('scraper_runs').insert({
            'source_id': source_id,
            'status': 'running',
            'started_at': datetime.utcnow().isoformat(),
            'scraper_version': SCRAPER_VERSION
        }).execute()
        return result.data[0]['id']
    except Exception as e:
        print(f"Error creating scraper run: {e}")
        return str(uuid4())


def update_scraper_run(run_id: str, status: str, documents_found: int = 0, documents_added: int = 0,
                       documents_updated: int = 0, error_message: Optional[str] = None):
    """Update scraper run with results"""
    try:
        supabase.table('scraper_runs').update({
            'status': status,
            'completed_at': datetime.utcnow().isoformat(),
            'documents_found': documents_found,
            'documents_added': documents_added,
            'documents_updated': documents_updated,
            'error_message': error_message
        }).eq('id', run_id).execute()
    except Exception as e:
        print(f"Error updating scraper run: {e}")


# ============================================================================
# SCRAPER FUNCTIONS (updated for new schema)
# ============================================================================

def scrape_sf_city_council() -> List[Dict[str, Any]]:
    """
    Example scraper for San Francisco City Council

    NOTE: This is a template - you'll need to customize the selectors
    based on the actual structure of the government website you're scraping.
    """
    documents = []

    # Example URL - replace with actual government website
    url = "https://sfgov.org/meetings"  # REPLACE THIS

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Example: Find all meeting items
        # CUSTOMIZE these selectors based on the actual website structure
        meetings = soup.find_all('div', class_='meeting-item')

        for meeting in meetings[:10]:  # Limit to 10 most recent
            try:
                # Extract data - CUSTOMIZE based on actual HTML structure
                title_elem = meeting.find('h2', class_='meeting-title')
                date_elem = meeting.find('time', class_='meeting-date')
                content_elem = meeting.find('div', class_='meeting-summary')
                link_elem = meeting.find('a', class_='meeting-link')

                if not title_elem or not date_elem:
                    continue

                # Parse data
                title = title_elem.get_text(strip=True)
                date_str = date_elem.get('datetime', date_elem.get_text(strip=True))
                content = content_elem.get_text(strip=True) if content_elem else ""
                url_link = link_elem.get('href') if link_elem else None

                # Auto-detect topics based on keywords
                topics = detect_topics(title + " " + content)

                document = {
                    'title': title,
                    'content': content,
                    'date': parse_date(date_str),
                    'source': 'City Council',
                    'source_type': 'council',
                    # New schema requires state/country codes
                    'state_code': 'CA',
                    'state_name': 'California',
                    'country_code': 'US',
                    'country_name': 'United States',
                    'topics': topics,
                    'url': url_link,
                    'document_type': 'agenda'
                }

                documents.append(document)

            except Exception as e:
                print(f"Error parsing meeting item: {e}")
                continue

    except Exception as e:
        print(f"Error scraping SF City Council: {e}")

    return documents


def scrape_oakland_planning_commission() -> List[Dict[str, Any]]:
    """
    Example scraper for Oakland Planning Commission

    NOTE: Customize this based on the actual website structure
    """
    documents = []

    url = "https://oakland.gov/planning/meetings"  # REPLACE THIS

    # Similar structure to above - customize for Oakland's website
    # ... implementation here ...

    return documents


def detect_topics(text: str) -> List[str]:
    """
    Auto-detect topics based on keywords in the text

    This is a simple keyword-based approach. For production, consider:
    - Using NLP libraries like spaCy
    - Training a topic classification model
    - Using OpenAI API for topic extraction
    """
    text_lower = text.lower()
    topics = []

    # Define topic keywords
    topic_keywords = {
        'Budget': ['budget', 'funding', 'fiscal', 'revenue', 'expenditure'],
        'Housing': ['housing', 'affordable housing', 'development', 'zoning', 'residential'],
        'Transportation': ['transportation', 'transit', 'traffic', 'parking', 'bike lane'],
        'Environment': ['environment', 'climate', 'sustainability', 'green', 'pollution'],
        'Public Safety': ['public safety', 'police', 'fire', 'emergency', 'crime'],
        'Education': ['education', 'school', 'student', 'teacher', 'curriculum'],
        'Parks': ['park', 'recreation', 'playground', 'open space'],
        'Infrastructure': ['infrastructure', 'road', 'bridge', 'water', 'sewer'],
        'Health': ['health', 'healthcare', 'medical', 'hospital', 'clinic'],
        'Economic Development': ['economic', 'business', 'jobs', 'employment', 'commerce'],
    }

    for topic, keywords in topic_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            topics.append(topic)

    return topics if topics else ['General']


def parse_date(date_str: str) -> str:
    """
    Parse date string to ISO format (YYYY-MM-DD)

    Handles various date formats commonly found on government websites
    """
    try:
        from dateutil import parser
        dt = parser.parse(date_str)
        return dt.strftime('%Y-%m-%d')
    except Exception:
        # Fallback to current date if parsing fails
        return datetime.now().strftime('%Y-%m-%d')


def store_documents(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Store scraped documents in Supabase using OPTIMIZED SCHEMA

    Handles:
    - Foreign key lookups (country, state, source)
    - Content hash deduplication
    - Topic many-to-many relationships
    - Document updates vs inserts
    """
    stored_count = 0
    updated_count = 0
    duplicate_count = 0
    error_count = 0

    for doc in documents:
        try:
            # Extract old schema fields
            title = doc.get('title')
            content = doc.get('content', '')
            document_date = doc.get('date')
            url = doc.get('url')
            topics = doc.get('topics', [])

            # New schema requires these lookups
            country_code = doc.get('country_code', 'US')
            country_name = doc.get('country_name', 'United States')
            state_code = doc.get('state_code')
            state_name = doc.get('state_name')
            source_name = doc.get('source')
            source_type = doc.get('source_type', 'council')

            if not all([title, document_date, state_code, state_name, source_name]):
                print(f"Skipping document with missing required fields: {title}")
                error_count += 1
                continue

            # Get/create foreign key IDs
            country_id = get_or_create_country(country_code, country_name)
            state_id = get_or_create_state(country_id, state_code, state_name)
            source_id = get_or_create_source(source_name, source_type, state_id, url)

            # Calculate content hash for deduplication
            content_hash = calculate_content_hash(content)

            # Check for duplicate by hash
            existing_id = find_duplicate_by_hash(content_hash)

            if existing_id:
                # Update existing document
                supabase.table('documents').update({
                    'title': title,
                    'content': content,
                    'url': url,
                    'updated_at': datetime.utcnow().isoformat(),
                    'last_verified_at': datetime.utcnow().isoformat()
                }).eq('id', existing_id).execute()
                duplicate_count += 1
                updated_count += 1
                document_id = existing_id
            else:
                # Insert new document
                result = supabase.table('documents').insert({
                    'title': title,
                    'content': content,
                    'content_hash': content_hash,
                    'document_date': document_date,
                    'source_id': source_id,
                    'state_id': state_id,
                    'country_id': country_id,
                    'url': url,
                    'document_type': doc.get('document_type', 'meeting'),
                    'status': 'published',
                    'scraped_at': datetime.utcnow().isoformat(),
                    'scraper_version': SCRAPER_VERSION
                }).execute()
                document_id = result.data[0]['id']
                stored_count += 1

            # Handle topics (many-to-many relationship)
            if topics:
                for topic_name in topics:
                    try:
                        topic_id = get_or_create_topic(topic_name)
                        # Insert document-topic relationship (ignore if exists)
                        supabase.table('document_topics').upsert({
                            'document_id': document_id,
                            'document_date': document_date,  # Required for partitioned table
                            'topic_id': topic_id,
                            'confidence': 1.0
                        }, on_conflict='document_id,document_date,topic_id').execute()
                    except Exception as e:
                        print(f"Error adding topic '{topic_name}' to document: {e}")

        except Exception as e:
            print(f"Error storing document '{doc.get('title', 'unknown')}': {e}")
            error_count += 1

    return {
        'stored': stored_count,
        'updated': updated_count,
        'duplicates': duplicate_count,
        'errors': error_count,
        'total_processed': len(documents)
    }


def lambda_handler(event, context):
    """
    Main Lambda handler function with scraper run tracking

    This function is triggered by:
    - AWS EventBridge (scheduled)
    - Manual invocation
    - API Gateway (optional)

    To use Maryland-specific scraping, import maryland_scraper:
    from maryland_scraper import lambda_handler as md_handler
    return md_handler(event, context)
    """
    print(f"Starting government website scraping (version {SCRAPER_VERSION})...")

    all_documents = []
    scraper_runs = {}

    # Scrape multiple sources
    scrapers = [
        ('SF City Council', 'CA', 'California', 'council', scrape_sf_city_council),
        # Add more scrapers here
        # Format: (source_name, state_code, state_name, source_type, scraper_function)
    ]

    for source_name, state_code, state_name, source_type, scraper_func in scrapers:
        print(f"Scraping {source_name}...")

        # Get/create source ID for tracking
        country_id = get_or_create_country('US', 'United States')
        state_id = get_or_create_state(country_id, state_code, state_name)
        source_id = get_or_create_source(source_name, source_type, state_id)

        # Create scraper run record
        run_id = create_scraper_run(source_id)
        scraper_runs[source_name] = {
            'run_id': run_id,
            'source_id': source_id
        }

        try:
            docs = scraper_func()
            all_documents.extend(docs)
            print(f"✓ Scraped {len(docs)} documents from {source_name}")

            # Update scraper run with success
            update_scraper_run(
                run_id=run_id,
                status='success',
                documents_found=len(docs),
                documents_added=0,  # Will be updated after storage
                documents_updated=0
            )

        except Exception as e:
            error_msg = str(e)
            print(f"✗ Error scraping {source_name}: {error_msg}")

            # Update scraper run with failure
            update_scraper_run(
                run_id=run_id,
                status='failed',
                documents_found=0,
                error_message=error_msg
            )

    # Store in Supabase
    print(f"\nStoring {len(all_documents)} documents in Supabase...")
    results = store_documents(all_documents)

    # Update scraper runs with storage results
    for source_name, run_info in scraper_runs.items():
        # Note: This is a simplified update. In production, you'd track per-source stats
        update_scraper_run(
            run_id=run_info['run_id'],
            status='success',
            documents_found=len(all_documents),
            documents_added=results['stored'],
            documents_updated=results['updated']
        )

    # Prepare response
    response = {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Scraping completed',
            'scraper_version': SCRAPER_VERSION,
            'sources_scraped': len(scrapers),
            'total_documents_found': len(all_documents),
            'storage_results': results,
            'scraper_runs': len(scraper_runs)
        })
    }

    print(f"\n✅ Scraping complete!")
    print(f"   Documents found: {len(all_documents)}")
    print(f"   Stored: {results['stored']}")
    print(f"   Updated: {results['updated']}")
    print(f"   Duplicates: {results['duplicates']}")
    print(f"   Errors: {results['errors']}")

    return response


# For local testing
if __name__ == '__main__':
    # Test locally with fake event/context
    result = lambda_handler({}, None)
    print(json.dumps(result, indent=2))
