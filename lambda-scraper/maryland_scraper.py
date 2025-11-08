"""
Maryland Government Document Scraper

Scrapes meeting notes, agendas, and policy discussions from Maryland state and local government websites.
Configured sources in maryland_sources.json

Features:
- PDF text extraction from meeting agendas
- Extractive summarization for readable content
- Auto-topic detection from real content
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from urllib.parse import urljoin
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# Import text extraction and summarization utilities
from text_utils import (
    extract_pdf_text,
    extract_webpage_text,
    extract_and_summarize,
    summarize_text_smart,
    summarize_text_simple
)

# Initialize Supabase client (optional for local testing)
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

# Only create client if credentials are provided
if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None
    print("⚠️  Supabase credentials not found - running in local test mode")

# Load Maryland sources configuration (optional)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MD_SOURCES_FILE = os.path.join(SCRIPT_DIR, 'maryland_sources.json')
if os.path.exists(MD_SOURCES_FILE):
    with open(MD_SOURCES_FILE, 'r') as f:
        MD_SOURCES = json.load(f)
else:
    MD_SOURCES = {'metadata': {'total_sources': 0}}
    print("⚠️  maryland_sources.json not found - using defaults")


def scrape_md_general_assembly() -> List[Dict[str, Any]]:
    """
    Scrape Maryland General Assembly meetings
    URL: https://mgaleg.maryland.gov/mgawebsite/Meetings/Month
    """
    documents = []
    base_url = "https://mgaleg.maryland.gov"
    url = "https://mgaleg.maryland.gov/mgawebsite/Meetings/Month"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find calendar table cells with meetings
        meeting_cells = soup.find_all('td', class_='calendar-day')

        for cell in meeting_cells[:20]:  # Limit to 20 most recent
            try:
                # Get date from the cell
                date_link = cell.find('a')
                if not date_link:
                    continue

                date_text = date_link.get_text(strip=True)
                # Parse date from href like /mgawebsite/Meetings/Day/11052025
                href = date_link.get('href', '')
                if '/Day/' in href:
                    date_str = href.split('/Day/')[1].split('?')[0]
                    # Convert MMDDYYYY to YYYY-MM-DD
                    if len(date_str) == 8:
                        month = date_str[:2]
                        day = date_str[2:4]
                        year = date_str[4:]
                        meeting_date = f"{year}-{month}-{day}"
                    else:
                        meeting_date = datetime.now().strftime('%Y-%m-%d')
                else:
                    meeting_date = datetime.now().strftime('%Y-%m-%d')

                # Get all meetings listed in this cell
                meeting_lists = cell.find_all('ul')
                for ul in meeting_lists:
                    chamber = "Unknown"
                    # Find chamber header (Senate, House, Other)
                    prev_sibling = ul.find_previous_sibling(text=True)
                    if prev_sibling:
                        chamber = prev_sibling.strip()

                    # Get committee meetings
                    for li in ul.find_all('li'):
                        committee_name = li.get_text(strip=True)
                        committee_link = li.find('a')

                        # Try to extract meeting details if there's a link
                        content = ""
                        topics = []
                        meeting_url = urljoin(base_url, href)

                        if committee_link:
                            committee_detail_url = urljoin(base_url, committee_link.get('href', ''))
                            if committee_detail_url and committee_detail_url != meeting_url:
                                print(f"Extracting details for: {committee_name}")
                                detail_text = extract_webpage_text(committee_detail_url, max_chars=3000)
                                if detail_text and len(detail_text) > 100:
                                    content = summarize_text_smart(detail_text, num_sentences=4)
                                    topics = detect_topics(detail_text)
                                    meeting_url = committee_detail_url

                        # Fallback to generic description
                        if not content:
                            content = f"Maryland General Assembly meeting scheduled for {chamber} {committee_name}."
                            topics = detect_topics(f"{chamber} {committee_name}")

                        document = {
                            'title': f"{chamber} - {committee_name}",
                            'content': content,
                            'date': meeting_date,
                            'source': 'Maryland General Assembly',
                            'jurisdiction': 'Maryland State',
                            'topics': topics if topics else ['Legislation'],
                            'url': meeting_url,
                            'is_favorite': False
                        }
                        documents.append(document)

            except Exception as e:
                print(f"Error parsing meeting cell: {e}")
                continue

    except Exception as e:
        print(f"Error scraping MD General Assembly: {e}")

    return documents


def scrape_baltimore_board_of_estimates() -> List[Dict[str, Any]]:
    """
    Scrape Baltimore Board of Estimates memos and agendas
    URL: https://www.baltimorecitycouncil.com/memos-agendas

    Now with PDF extraction and summarization!
    """
    documents = []
    url = "https://www.baltimorecitycouncil.com/memos-agendas"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find table with meeting documents
        tables = soup.find_all('table')

        for table in tables[:1]:  # Usually first table has the data
            rows = table.find_all('tr')[1:]  # Skip header

            for row in rows[:10]:  # Limit to 10 most recent
                try:
                    cells = row.find_all('td')
                    if len(cells) < 3:
                        continue

                    # Parse date
                    date_text = cells[0].get_text(strip=True)
                    try:
                        meeting_date = datetime.strptime(date_text, '%B %d, %Y').strftime('%Y-%m-%d')
                    except:
                        meeting_date = datetime.now().strftime('%Y-%m-%d')

                    # Get memo and agenda links
                    memo_link = cells[1].find('a')
                    agenda_link = cells[2].find('a')

                    memo_url = memo_link.get('href') if memo_link else None
                    agenda_url = agenda_link.get('href') if agenda_link else None

                    # Extract and summarize PDF content
                    content = ""
                    topics = []

                    # Try to extract from agenda PDF first
                    if agenda_url and agenda_url.endswith('.pdf'):
                        print(f"Extracting agenda PDF for {date_text}")
                        result = extract_and_summarize(
                            pdf_url=agenda_url,
                            webpage_url=None,
                            summary_length=5,
                            method='smart'
                        )
                        content = result['summary']

                        # Detect topics from actual content
                        full_text = result['full_text']
                        if full_text:
                            topics = detect_topics(full_text)

                    # Fallback: try memo PDF
                    if not content and memo_url and memo_url.endswith('.pdf'):
                        print(f"Extracting memo PDF for {date_text}")
                        result = extract_and_summarize(
                            pdf_url=memo_url,
                            webpage_url=None,
                            summary_length=5,
                            method='smart'
                        )
                        content = result['summary']

                        full_text = result['full_text']
                        if full_text:
                            topics = detect_topics(full_text)

                    # Final fallback: generic description
                    if not content:
                        content = f"Board of Estimates meeting held on {date_text}. Agenda and President's Memorandum available for review."
                        topics = ['Budget', 'Contracts', 'Procurement', 'Finance']

                    # Create document for this meeting
                    document = {
                        'title': f"Baltimore Board of Estimates - {date_text}",
                        'content': content,
                        'date': meeting_date,
                        'source': 'Board of Estimates',
                        'jurisdiction': 'Baltimore City',
                        'topics': topics if topics else ['General'],
                        'url': agenda_url if agenda_url else memo_url if memo_url else url,
                        'is_favorite': False
                    }
                    documents.append(document)

                except Exception as e:
                    print(f"Error parsing BOE row: {e}")
                    continue

    except Exception as e:
        print(f"Error scraping Baltimore BOE: {e}")

    return documents


def scrape_baltimore_city_council() -> List[Dict[str, Any]]:
    """
    Scrape Baltimore City Council meetings
    URL: https://www.baltimorecitycouncil.com/complete-calendar

    Now extracts and summarizes actual meeting content!
    """
    documents = []
    url = "https://www.baltimorecitycouncil.com/complete-calendar"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find meeting items - adjust selectors based on actual page structure
        meeting_items = soup.find_all('div', class_='calendar-item')[:10]

        if not meeting_items:
            # Try alternative selector
            meeting_items = soup.find_all('article')[:10]

        for item in meeting_items:
            try:
                title_elem = item.find(['h2', 'h3', 'h4'])
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)

                # Get meeting content/description
                content_elem = item.find('p') or item.find('div', class_='description')
                raw_content = content_elem.get_text(strip=True) if content_elem else ""

                # Check if there's a link to meeting details
                link_elem = item.find('a')
                meeting_detail_url = link_elem.get('href') if link_elem else None

                # Try to find date
                date_elem = item.find('time') or item.find('span', class_='date')
                if date_elem:
                    date_text = date_elem.get('datetime', date_elem.get_text(strip=True))
                    try:
                        meeting_date = datetime.strptime(date_text[:10], '%Y-%m-%d').strftime('%Y-%m-%d')
                    except:
                        meeting_date = datetime.now().strftime('%Y-%m-%d')
                else:
                    meeting_date = datetime.now().strftime('%Y-%m-%d')

                # Extract more content if there's a detail page
                content = raw_content
                if meeting_detail_url and len(raw_content) < 200:
                    print(f"Extracting detail page for: {title}")
                    detail_text = extract_webpage_text(meeting_detail_url, max_chars=3000)
                    if detail_text and len(detail_text) > len(raw_content):
                        # Summarize the detailed content
                        content = summarize_text_smart(detail_text, num_sentences=5)
                    else:
                        content = raw_content if raw_content else "City Council meeting"
                elif not content:
                    content = "City Council meeting"

                # Detect topics from title and content
                topics = detect_topics(title + " " + content)

                document = {
                    'title': title,
                    'content': content,
                    'date': meeting_date,
                    'source': 'City Council',
                    'jurisdiction': 'Baltimore City',
                    'topics': topics if topics else ['General'],
                    'url': meeting_detail_url if meeting_detail_url else url,
                    'is_favorite': False
                }
                documents.append(document)

            except Exception as e:
                print(f"Error parsing city council item: {e}")
                continue

    except Exception as e:
        print(f"Error scraping Baltimore City Council: {e}")

    return documents


def scrape_legistar_calendar(url: str, jurisdiction: str, source_name: str) -> List[Dict[str, Any]]:
    """
    Generic scraper for Legistar-based calendar systems
    Used by: Montgomery County, Prince George's County
    """
    documents = []

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Legistar typically uses a table structure
        meeting_rows = soup.find_all('tr', class_='MeetingRow')[:10]

        for row in meeting_rows:
            try:
                # Get meeting name
                name_cell = row.find('td', class_='MeetingName') or row.find('a', class_='MeetingLink')
                if name_cell:
                    title = name_cell.get_text(strip=True)
                    meeting_link = name_cell.find('a')
                    meeting_url = meeting_link.get('href') if meeting_link else url
                else:
                    continue

                # Get meeting date
                date_cell = row.find('td', class_='MeetingDate')
                if date_cell:
                    date_text = date_cell.get_text(strip=True)
                    try:
                        meeting_date = datetime.strptime(date_text, '%m/%d/%Y').strftime('%Y-%m-%d')
                    except:
                        meeting_date = datetime.now().strftime('%Y-%m-%d')
                else:
                    meeting_date = datetime.now().strftime('%Y-%m-%d')

                # Get meeting time/location
                time_cell = row.find('td', class_='MeetingTime')
                location_cell = row.find('td', class_='MeetingLocation')

                content = f"Meeting scheduled for {date_text}"
                if time_cell:
                    content += f" at {time_cell.get_text(strip=True)}"
                if location_cell:
                    content += f". Location: {location_cell.get_text(strip=True)}"

                document = {
                    'title': title,
                    'content': content,
                    'date': meeting_date,
                    'source': source_name,
                    'jurisdiction': jurisdiction,
                    'topics': detect_topics(title),
                    'url': meeting_url,
                    'is_favorite': False
                }
                documents.append(document)

            except Exception as e:
                print(f"Error parsing Legistar row: {e}")
                continue

    except Exception as e:
        print(f"Error scraping Legistar calendar for {jurisdiction}: {e}")

    return documents


def detect_topics(text: str) -> List[str]:
    """
    Auto-detect topics based on keywords in the text
    """
    text_lower = text.lower()
    topics = []

    topic_keywords = {
        'Budget': ['budget', 'funding', 'fiscal', 'revenue', 'expenditure', 'appropriation'],
        'Housing': ['housing', 'affordable housing', 'development', 'zoning', 'residential'],
        'Transportation': ['transportation', 'transit', 'traffic', 'parking', 'bike lane', 'road'],
        'Environment': ['environment', 'climate', 'sustainability', 'green', 'pollution', 'energy'],
        'Public Safety': ['public safety', 'police', 'fire', 'emergency', 'crime', '911'],
        'Education': ['education', 'school', 'student', 'teacher', 'curriculum', 'university'],
        'Health': ['health', 'healthcare', 'medical', 'hospital', 'clinic', 'pandemic'],
        'Economic Development': ['economic', 'business', 'jobs', 'employment', 'commerce', 'development'],
        'Planning': ['planning', 'zoning', 'land use', 'urban', 'development'],
        'Legislation': ['bill', 'legislation', 'law', 'ordinance', 'resolution', 'amendment'],
        'Contracts': ['contract', 'procurement', 'vendor', 'rfp', 'bid'],
        'Finance': ['finance', 'financial', 'treasury', 'bonds', 'debt'],
    }

    for topic, keywords in topic_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            topics.append(topic)

    return topics if topics else ['General']


def scrape_all_maryland_sources() -> Dict[str, List[Dict[str, Any]]]:
    """
    Scrape all configured Maryland government sources
    Returns a dictionary with source names as keys and documents as values
    """
    all_documents = {}

    # Maryland General Assembly
    print("Scraping Maryland General Assembly...")
    all_documents['MD General Assembly'] = scrape_md_general_assembly()

    # Baltimore Board of Estimates
    print("Scraping Baltimore Board of Estimates...")
    all_documents['Baltimore BOE'] = scrape_baltimore_board_of_estimates()

    # Baltimore City Council
    print("Scraping Baltimore City Council...")
    all_documents['Baltimore City Council'] = scrape_baltimore_city_council()

    # Montgomery County (Legistar)
    print("Scraping Montgomery County Council...")
    all_documents['Montgomery County'] = scrape_legistar_calendar(
        'https://montgomerycountymd.legistar.com/Calendar.aspx',
        'Montgomery County',
        'County Council'
    )

    # Prince George's County (Legistar)
    print("Scraping Prince George's County Council...")
    all_documents['Prince Georges County'] = scrape_legistar_calendar(
        'https://princegeorgescountymd.legistar.com/Calendar.aspx',
        "Prince George's County",
        'County Council'
    )

    return all_documents


def store_documents(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Store scraped documents in Supabase
    Checks for duplicates before inserting
    """
    stored_count = 0
    duplicate_count = 0
    error_count = 0

    for doc in documents:
        try:
            # Check if document already exists (based on title and date)
            existing = supabase.table('documents').select('id').eq(
                'title', doc['title']
            ).eq('date', doc['date']).execute()

            if existing.data:
                duplicate_count += 1
                continue

            # Insert new document
            result = supabase.table('documents').insert(doc).execute()
            stored_count += 1

        except Exception as e:
            print(f"Error storing document '{doc.get('title', 'unknown')}': {e}")
            error_count += 1

    return {
        'stored': stored_count,
        'duplicates': duplicate_count,
        'errors': error_count,
        'total_processed': len(documents)
    }


def lambda_handler(event, context):
    """
    AWS Lambda handler - scrapes all Maryland government sources
    """
    print("Starting Maryland government document scraping...")
    print(f"Total sources configured: {MD_SOURCES['metadata']['total_sources']}")

    # Scrape all sources
    all_documents_by_source = scrape_all_maryland_sources()

    # Flatten all documents into a single list
    all_documents = []
    for source_name, docs in all_documents_by_source.items():
        print(f"✓ {source_name}: {len(docs)} documents")
        all_documents.extend(docs)

    # Store in Supabase
    print(f"\nStoring {len(all_documents)} total documents in Supabase...")
    results = store_documents(all_documents)

    # Prepare response
    response = {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Maryland government scraping completed',
            'sources_scraped': len(all_documents_by_source),
            'breakdown': {k: len(v) for k, v in all_documents_by_source.items()},
            'total_documents_found': len(all_documents),
            'storage_results': results
        }, indent=2)
    }

    print(f"\n✅ Scraping complete!")
    print(f"   Stored: {results['stored']}")
    print(f"   Duplicates: {results['duplicates']}")
    print(f"   Errors: {results['errors']}")

    return response


# For local testing
if __name__ == '__main__':
    # Test with environment variables
    result = lambda_handler({}, None)
    print(json.dumps(json.loads(result['body']), indent=2))
