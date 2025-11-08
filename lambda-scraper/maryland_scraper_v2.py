"""
Maryland Government Document Scraper - Version 2.0
Updated for OPTIMIZED SCHEMA with content hashing, deduplication, and scraper run tracking

Scrapes meeting notes, agendas, and policy discussions from Maryland state and local government websites.
Configured sources in maryland_sources.json
"""

import json
import os
import hashlib
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from uuid import uuid4

from collections import Counter

import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

from text_utils import extract_and_summarize


def _format_list_for_sentence(items: List[str]) -> str:
    items = [item for item in items if item]
    if not items:
        return ''
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ', '.join(items[:-1]) + f", and {items[-1]}"


def generate_board_of_estimates_summary(full_text: str, date_label: str) -> Optional[Dict[str, Any]]:
    """Create a structured summary for Board of Estimates agendas."""
    if not full_text:
        return None

    agenda_keyword_map = {
        'audit': 'audits',
        'oversight': 'oversight reviews',
        'hearing': 'public hearings',
        'grant award': 'grant awards',
        'grant': 'grant awards',
        'lease': 'lease agreements',
        'loan': 'loan and financing requests',
        'insurance': 'insurance renewals',
        'transfer of funds': 'budget transfers',
        'transfer': 'budget transfers',
        'resolution': 'policy resolutions',
        'ordinance': 'policy ordinances',
        'contract': 'contract approvals',
        'procurement': 'procurement actions',
        'public comment': 'public engagement',
        'community': 'community investments',
        'infrastructure': 'infrastructure projects',
        'capital': 'capital projects',
        'water': 'water and sewer projects',
        'sewer': 'water and sewer projects',
        'budget': 'budget adjustments',
        'housing': 'housing initiatives',
        'economic development': 'economic development',
        'retirement': 'retirement system actions',
        'personnel': 'personnel actions',
        'employee travel': 'employee travel requests',
        'travel request': 'employee travel requests',
        'travel reimbursement': 'employee travel requests'
    }

    debate_keywords = {
        'audit', 'oversight', 'hearing', 'grant', 'lease', 'loan', 'resolution', 'ordinance',
        'contract', 'procurement', 'policy', 'public', 'community', 'budget', 'housing',
        'economic', 'infrastructure', 'capital', 'development', 'zoning', 'environment',
        'sustainability', 'transportation', 'education', 'safety', 'justice', 'equity'
    }

    operational_theme_exclusions = {
        'employee travel requests',
        'personnel actions',
        'retirement system actions',
        'insurance renewals'
    }

    lines = [line.strip() for line in full_text.splitlines() if line.strip()]
    agenda_lines: List[str] = []

    agenda_code_pattern = re.compile(r'^[A-Z]{2,4}-\d{2}-\d+')

    parsed_items: List[Dict[str, Any]] = []

    for raw_line in lines:
        cleaned_line = re.sub(r'^P\s*\d+(?:-\d+)?\s+', '', raw_line)
        cleaned_line = cleaned_line.strip(' -\u2022')
        if not cleaned_line:
            continue
        if agenda_code_pattern.match(cleaned_line):
            agenda_lines.append(cleaned_line)
            parts = [part.strip() for part in re.split(r'\s+-\s+', cleaned_line) if part.strip()]
            item = {
                'code': parts[0] if parts else '',
                'agency': parts[1] if len(parts) > 1 else '',
                'category': parts[2] if len(parts) > 2 else '',
                'description': parts[3] if len(parts) > 3 else '',
                'text': cleaned_line
            }
            parsed_items.append(item)

    if not agenda_lines:
        return None

    agency_counter: Counter = Counter()
    category_counter: Counter = Counter()
    keyword_hits: Counter = Counter()
    theme_counter: Counter = Counter()
    amount_highlights: List[Dict[str, Any]] = []
    debate_highlights: List[str] = []

    for item in parsed_items:
        agency = item['agency']
        category = item['category']
        description = item['description']
        full_line = item['text']

        if agency:
            agency_counter[agency] += 1
        if category:
            category_counter[category] += 1

        lowered = full_line.lower()
        for keyword, phrase in agenda_keyword_map.items():
            if keyword in lowered:
                if phrase not in operational_theme_exclusions:
                    keyword_hits[phrase] += 1
                    theme_counter[phrase] += 1
                else:
                    keyword_hits[phrase] += 1

        amount_match = re.search(r'\$[\d,]+(?:\.\d+)?(?:\s?(?:million|billion))?', full_line)
        if amount_match:
            amount_text = amount_match.group()
            raw_amount = amount_text.lower().replace('$', '').replace(',', '').strip()
            multiplier = 1
            if raw_amount.endswith('million'):
                multiplier = 1_000_000
                raw_amount = raw_amount.replace('million', '').strip()
            elif raw_amount.endswith('billion'):
                multiplier = 1_000_000_000
                raw_amount = raw_amount.replace('billion', '').strip()

            try:
                numeric_value = float(raw_amount) * multiplier
            except ValueError:
                numeric_value = 0

            descriptor = description or category or agency or item['code']
            amount_highlights.append({
                'label': descriptor,
                'agency': agency,
                'category': category,
                'amount_text': amount_text,
                'value': numeric_value,
                'code': item['code']
            })

        combined_descriptor = ' '.join(filter(None, [description, category, agency]))
        lowered_desc = combined_descriptor.lower()
        if any(term in lowered_desc for term in debate_keywords):
            focus_label = description or category or agency or item['code']
            if focus_label and focus_label not in debate_highlights:
                debate_highlights.append(focus_label)

    top_agencies = [agency for agency, _ in agency_counter.most_common(3)]
    top_themes = [theme for theme, _ in theme_counter.most_common(5) if theme not in operational_theme_exclusions]

    if not top_themes:
        top_themes = [category for category, _ in category_counter.most_common(5)
                      if category.lower() not in {'employee travel requests', 'personnel actions'}]

    def _normalize_theme_label(label: str) -> str:
        normalized = label.replace('/', ' and ').replace(' - ', ' ').strip()
        return normalized.lower()

    theme_display = [_normalize_theme_label(theme) for theme in top_themes if theme]
    theme_display = [theme for theme in theme_display if theme]

    item_count = len(agenda_lines)
    sentences: List[str] = []

    sentences.append(f"Board of Estimates meeting on {date_label} reviews {item_count} agenda items.")

    active_counter = theme_counter if theme_counter else category_counter

    if active_counter:
        theme_phrases: List[str] = []
        for theme, count in active_counter.most_common(4):
            display = _normalize_theme_label(theme)
            if display:
                label = display.rstrip('s') if count == 1 else display
                theme_phrases.append(f"{count} {label}")
        if theme_phrases:
            sentences.append(f"Key themes include {_format_list_for_sentence(theme_phrases)}.")

    if top_agencies:
        sentences.append(f"Frequent presenters: {_format_list_for_sentence(top_agencies)}.")

    if amount_highlights:
        amount_highlights = [entry for entry in amount_highlights
                             if (entry['category'] or '').lower() not in {'employee travel requests', 'personnel actions'}]
        if amount_highlights:
            amount_highlights.sort(key=lambda entry: entry['value'], reverse=True)
            top_amounts = []
            for entry in amount_highlights[:3]:
                agency_label = entry['agency'] or entry['category'] or ''
                context = entry['label'] or entry['category']
                snippet = context
                if agency_label and agency_label not in context:
                    snippet = f"{agency_label} - {context}"
                top_amounts.append(f"{snippet} ({entry['amount_text']})")
            if top_amounts:
                sentences.append(f"Largest funding items: {_format_list_for_sentence(top_amounts)}.")

    policy_highlights = []
    for descriptor in debate_highlights:
        lowered_desc = descriptor.lower()
        if any(token in lowered_desc for token in ('travel', 'personnel', 'retirement', 'employee')):
            continue
        policy_highlights.append(descriptor)
        if len(policy_highlights) >= 4:
            break

    if policy_highlights:
        sentences.append(f"Debate focuses on {_format_list_for_sentence(policy_highlights)}.")
    elif parsed_items:
        notable_descriptions = []
        for item in parsed_items[:3]:
            descriptor = item['description'] or item['category']
            if descriptor:
                if item['agency'] and item['agency'] not in descriptor:
                    descriptor = f"{item['agency']} - {descriptor}"
                notable_descriptions.append(descriptor)
        if notable_descriptions:
            sentences.append(f"Notable agenda items include {_format_list_for_sentence(notable_descriptions)}.")

    summary_text = ' '.join(sentences).strip()

    if len(sentences) > 1:
        lead = sentences[0]
        bullets = [f"- {detail}" for detail in sentences[1:]]
        summary_text = lead + '\n' + '\n'.join(bullets)

    topic_candidates: List[str] = []
    for theme in theme_display:
        topic_candidates.append(' '.join(word.capitalize() for word in theme.split()))
    topic_candidates.extend(top_agencies)

    deduped_topics = []
    for topic in topic_candidates:
        if topic and topic not in deduped_topics:
            deduped_topics.append(topic)

    return {
        'summary': summary_text,
        'topics': deduped_topics[:8]
    }

# Initialize Supabase client
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Scraper version for tracking
SCRAPER_VERSION = "2.0.0-maryland"

# Load Maryland sources configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(SCRIPT_DIR, 'maryland_sources.json'), 'r') as f:
        MD_SOURCES = json.load(f)
except FileNotFoundError:
    print("Warning: maryland_sources.json not found, using defaults")
    MD_SOURCES = {'metadata': {'total_sources': 0}}

# Cache for database lookups to reduce queries
_cache = {
    'countries': {},
    'states': {},
    'sources': {},
    'topics': {}
}


# ============================================================================
# DATABASE HELPER FUNCTIONS (Same as lambda_function.py)
# ============================================================================

def get_or_create_country(country_code: str, country_name: str) -> int:
    """Get country ID or create if doesn't exist"""
    if country_code in _cache['countries']:
        return _cache['countries'][country_code]

    try:
        result = supabase.table('countries').select('id').eq('code', country_code).execute()
        if result.data:
            country_id = result.data[0]['id']
            _cache['countries'][country_code] = country_id
            return country_id

        result = supabase.table('countries').insert({
            'code': country_code,
            'name': country_name
        }).execute()
        country_id = result.data[0]['id']
        _cache['countries'][country_code] = country_id
        return country_id
    except Exception as e:
        print(f"Error getting/creating country {country_code}: {e}")
        return 1


def get_or_create_state(country_id: int, state_code: str, state_name: str) -> int:
    """Get state ID or create if doesn't exist"""
    cache_key = f"{country_id}:{state_code}"

    if cache_key in _cache['states']:
        return _cache['states'][cache_key]

    try:
        result = supabase.table('states').select('id').eq('country_id', country_id).eq('code', state_code).execute()
        if result.data:
            state_id = result.data[0]['id']
            _cache['states'][cache_key] = state_id
            return state_id

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
        return 1


def get_or_create_source(name: str, source_type: str, state_id: int, website_url: Optional[str] = None) -> int:
    """Get source ID or create if doesn't exist"""
    cache_key = f"{name}:{state_id}"

    if cache_key in _cache['sources']:
        return _cache['sources'][cache_key]

    try:
        result = supabase.table('sources').select('id').eq('name', name).eq('state_id', state_id).execute()
        if result.data:
            source_id = result.data[0]['id']
            _cache['sources'][cache_key] = source_id
            return source_id

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
        return 1


def get_or_create_topic(topic_name: str) -> int:
    """Get topic ID or create if doesn't exist"""
    if topic_name in _cache['topics']:
        return _cache['topics'][topic_name]

    try:
        result = supabase.table('topics').select('id').ilike('name', topic_name).execute()
        if result.data:
            topic_id = result.data[0]['id']
            _cache['topics'][topic_name] = topic_id
            return topic_id

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
        return 1


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
# MARYLAND-SPECIFIC SCRAPERS
# ============================================================================

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

        meeting_cells = soup.find_all('td', class_='calendar-day')

        for cell in meeting_cells[:20]:
            try:
                date_link = cell.find('a')
                if not date_link:
                    continue

                href = date_link.get('href', '')
                if '/Day/' in href:
                    date_str = href.split('/Day/')[1].split('?')[0]
                    if len(date_str) == 8:
                        month = date_str[:2]
                        day = date_str[2:4]
                        year = date_str[4:]
                        meeting_date = f"{year}-{month}-{day}"
                    else:
                        meeting_date = datetime.now().strftime('%Y-%m-%d')
                else:
                    meeting_date = datetime.now().strftime('%Y-%m-%d')

                meeting_lists = cell.find_all('ul')
                for ul in meeting_lists:
                    chamber = "Unknown"
                    prev_sibling = ul.find_previous_sibling(text=True)
                    if prev_sibling:
                        chamber = prev_sibling.strip()

                    for li in ul.find_all('li'):
                        committee_name = li.get_text(strip=True)

                        document = {
                            'title': f"{chamber} - {committee_name}",
                            'content': f"Maryland General Assembly meeting scheduled for {chamber} {committee_name}. Check the official website for detailed agenda and updates.",
                            'date': meeting_date,
                            'source': 'Maryland General Assembly',
                            'source_type': 'legislature',
                            'state_code': 'MD',
                            'state_name': 'Maryland',
                            'country_code': 'US',
                            'country_name': 'United States',
                            'topics': detect_topics(f"{chamber} {committee_name}"),
                            'url': urljoin(base_url, href),
                            'document_type': 'agenda'
                        }
                        documents.append(document)

            except Exception as e:
                print(f"Error parsing meeting cell: {e}")
                continue

    except Exception as e:
        print(f"Error scraping MD General Assembly: {e}")

    return documents


def summarize_meeting_pdfs(agenda_url: Optional[str], memo_url: Optional[str], date_text: str,
                           fallback_topics: Optional[List[str]] = None) -> Dict[str, Any]:
    """Pull summary, full text, and topics from provided agenda/memo PDFs."""
    fallback_topics = fallback_topics or ['Budget', 'Contracts', 'Procurement', 'Finance']

    def sanitize_text(value: Optional[str]) -> Optional[str]:
        if not value:
            return value
        return value.replace('\x00', '').replace('\u0000', '').strip()

    summary_text: Optional[str] = None
    full_text: Optional[str] = None
    key_phrases: List[str] = []
    chosen_url: Optional[str] = None
    agenda_topics: List[str] = []

    for candidate in [agenda_url, memo_url]:
        if not candidate or not candidate.lower().endswith('.pdf'):
            continue

        try:
            result = extract_and_summarize(
                pdf_url=candidate,
                summary_length=6,
                method='huggingface',  # Use AI summarization for best quality
                pdf_max_pages=1000,
                pdf_max_chars=500000  # Handle large 400+ page documents
            )

            summary_text = sanitize_text(result.get('summary'))
            full_text = sanitize_text(result.get('full_text')) or ''
            key_phrases = result.get('key_phrases') or []
            chosen_url = candidate

            # HuggingFace AI handles all summarization now
            # Removed custom Board of Estimates logic for consistency

            if summary_text:
                break

        except Exception as exc:
            print(f"Error summarizing PDF {candidate}: {exc}")
            continue

    if not summary_text:
        summary_text = (
            f"Board of Estimates meeting held on {date_text}. Agenda and President's Memorandum "
            "available for review. Topics include budget, contracts, and city procurement matters."
        )
        full_text = ''

    # Use HuggingFace key phrases if available, otherwise detect from text
    if key_phrases:
        topics = key_phrases[:8]
    else:
        topic_seed = (full_text or summary_text or '')
        topics = detect_topics(topic_seed)

    if not topics:
        topics = fallback_topics

    topics = topics[:8]

    return {
        'summary': summary_text,
        'full_text': full_text,
        'topics': topics,
        'url': chosen_url or agenda_url or memo_url
    }


def scrape_baltimore_board_of_estimates() -> List[Dict[str, Any]]:
    """
    Scrape Baltimore Board of Estimates memos and agendas
    URL: https://www.baltimorecitycouncil.com/memos-agendas
    """
    documents = []
    url = "https://www.baltimorecitycouncil.com/memos-agendas"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        tables = soup.find_all('table')

        for table in tables[:1]:
            rows = table.find_all('tr')[1:]

            for row in rows[:10]:
                try:
                    cells = row.find_all('td')
                    if len(cells) < 3:
                        continue

                    date_text = cells[0].get_text(strip=True)
                    try:
                        meeting_date = datetime.strptime(date_text, '%B %d, %Y').strftime('%Y-%m-%d')
                    except:
                        meeting_date = datetime.now().strftime('%Y-%m-%d')

                    memo_link = cells[1].find('a') if len(cells) > 1 else None
                    memo_url = memo_link.get('href') if memo_link else None

                    agenda_link = cells[2].find('a') if len(cells) > 2 else None
                    agenda_url = agenda_link.get('href') if agenda_link else None

                    summary_details = summarize_meeting_pdfs(agenda_url, memo_url, date_text)
                    summary_text = summary_details['summary']
                    full_text = summary_details['full_text']
                    topics = summary_details['topics']
                    canonical_url = summary_details['url'] or agenda_url or memo_url or url

                    # Avoid storing extremely large blobs in content
                    trimmed_full_text = None
                    if full_text:
                        trimmed_full_text = full_text if len(full_text) <= 5000 else full_text[:5000] + '...'

                    document = {
                        'title': f"Baltimore Board of Estimates - {date_text}",
                        'content': summary_text,
                        'summary': summary_text,
                        'full_text': trimmed_full_text,
                        'date': meeting_date,
                        'source': 'Board of Estimates',
                        'source_type': 'board',
                        'state_code': 'MD',
                        'state_name': 'Maryland',
                        'country_code': 'US',
                        'country_name': 'United States',
                        'topics': topics if topics else ['General'],
                        'url': canonical_url,
                        'document_type': 'agenda'
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
    """
    documents = []
    url = "https://www.baltimorecitycouncil.com/complete-calendar"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        meeting_items = soup.find_all('div', class_='calendar-item')[:10]

        if not meeting_items:
            meeting_items = soup.find_all('article')[:10]

        for item in meeting_items:
            try:
                title_elem = item.find(['h2', 'h3', 'h4'])
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)

                content_elem = item.find('p') or item.find('div', class_='description')
                content = content_elem.get_text(strip=True) if content_elem else "City Council meeting"

                date_elem = item.find('time') or item.find('span', class_='date')
                if date_elem:
                    date_text = date_elem.get('datetime', date_elem.get_text(strip=True))
                    try:
                        meeting_date = datetime.strptime(date_text[:10], '%Y-%m-%d').strftime('%Y-%m-%d')
                    except:
                        meeting_date = datetime.now().strftime('%Y-%m-%d')
                else:
                    meeting_date = datetime.now().strftime('%Y-%m-%d')

                document = {
                    'title': title,
                    'content': content,
                    'date': meeting_date,
                    'source': 'City Council',
                    'source_type': 'council',
                    'state_code': 'MD',
                    'state_name': 'Maryland',
                    'country_code': 'US',
                    'country_name': 'United States',
                    'topics': detect_topics(title + " " + content),
                    'url': url,
                    'document_type': 'meeting'
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

        meeting_rows = soup.find_all('tr', class_='MeetingRow')[:10]

        for row in meeting_rows:
            try:
                name_cell = row.find('td', class_='MeetingName') or row.find('a', class_='MeetingLink')
                if name_cell:
                    title = name_cell.get_text(strip=True)
                    meeting_link = name_cell.find('a')
                    meeting_url = meeting_link.get('href') if meeting_link else url
                else:
                    continue

                date_cell = row.find('td', class_='MeetingDate')
                if date_cell:
                    date_text = date_cell.get_text(strip=True)
                    try:
                        meeting_date = datetime.strptime(date_text, '%m/%d/%Y').strftime('%Y-%m-%d')
                    except:
                        meeting_date = datetime.now().strftime('%Y-%m-%d')
                else:
                    meeting_date = datetime.now().strftime('%Y-%m-%d')

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
                    'source_type': 'council',
                    'state_code': 'MD',
                    'state_name': 'Maryland',
                    'country_code': 'US',
                    'country_name': 'United States',
                    'topics': detect_topics(title),
                    'url': meeting_url,
                    'document_type': 'meeting'
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


# ============================================================================
# STORAGE FUNCTION (Updated for optimized schema)
# ============================================================================

def store_documents(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Store scraped documents in Supabase using OPTIMIZED SCHEMA
    """
    stored_count = 0
    updated_count = 0
    duplicate_count = 0
    error_count = 0

    for doc in documents:
        try:
            title = doc.get('title')
            content = doc.get('content', '')
            document_date = doc.get('document_date') or doc.get('date')
            url = doc.get('url')
            topics = doc.get('topics', [])

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
                    'summary': doc.get('summary'),
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
                    'summary': doc.get('summary'),
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


# ============================================================================
# MAIN LAMBDA HANDLER
# ============================================================================

def lambda_handler(event, context):
    """
    AWS Lambda handler - scrapes all Maryland government sources with tracking
    """
    print(f"Starting Maryland government document scraping (version {SCRAPER_VERSION})...")
    print(f"Total sources configured: {MD_SOURCES.get('metadata', {}).get('total_sources', 'Unknown')}")

    # Initialize Maryland state (ensure it exists in DB)
    country_id = get_or_create_country('US', 'United States')
    state_id = get_or_create_state(country_id, 'MD', 'Maryland')

    # Define scrapers with metadata
    maryland_scrapers = [
        {
            'name': 'Maryland General Assembly',
            'type': 'legislature',
            'function': scrape_md_general_assembly
        },
        {
            'name': 'Board of Estimates',
            'type': 'board',
            'function': scrape_baltimore_board_of_estimates
        },
        {
            'name': 'Baltimore City Council',
            'type': 'council',
            'function': scrape_baltimore_city_council
        },
        {
            'name': 'Montgomery County Council',
            'type': 'council',
            'function': lambda: scrape_legistar_calendar(
                'https://montgomerycountymd.legistar.com/Calendar.aspx',
                'Montgomery County',
                'County Council'
            )
        },
        {
            'name': "Prince George's County Council",
            'type': 'council',
            'function': lambda: scrape_legistar_calendar(
                'https://princegeorgescountymd.legistar.com/Calendar.aspx',
                "Prince George's County",
                'County Council'
            )
        }
    ]

    all_documents = []
    scraper_runs = {}
    source_stats = {}

    # Scrape each source
    for scraper in maryland_scrapers:
        source_name = scraper['name']
        source_type = scraper['type']
        scraper_func = scraper['function']

        print(f"\nScraping {source_name}...")

        # Get/create source ID
        source_id = get_or_create_source(source_name, source_type, state_id)

        # Create scraper run record
        run_id = create_scraper_run(source_id)
        scraper_runs[source_name] = run_id

        try:
            docs = scraper_func()
            all_documents.extend(docs)
            source_stats[source_name] = len(docs)
            print(f"✓ {source_name}: {len(docs)} documents found")

            # Update run with success (will update again after storage)
            update_scraper_run(
                run_id=run_id,
                status='success',
                documents_found=len(docs)
            )

        except Exception as e:
            error_msg = str(e)
            print(f"✗ {source_name}: Failed with error: {error_msg}")
            source_stats[source_name] = 0

            # Update run with failure
            update_scraper_run(
                run_id=run_id,
                status='failed',
                documents_found=0,
                error_message=error_msg
            )

    # Store all documents
    print(f"\n{'='*60}")
    print(f"Storing {len(all_documents)} total documents in Supabase...")
    results = store_documents(all_documents)

    # Update scraper runs with final storage stats
    for source_name, run_id in scraper_runs.items():
        if source_stats.get(source_name, 0) > 0:
            update_scraper_run(
                run_id=run_id,
                status='success',
                documents_found=source_stats[source_name],
                documents_added=results['stored'],
                documents_updated=results['updated']
            )

    # Prepare response
    response = {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Maryland government scraping completed',
            'scraper_version': SCRAPER_VERSION,
            'sources_scraped': len(maryland_scrapers),
            'breakdown': source_stats,
            'total_documents_found': len(all_documents),
            'storage_results': results,
            'scraper_runs': len(scraper_runs)
        }, indent=2)
    }

    # Pretty print results
    print(f"\n{'='*60}")
    print(f"✅ Maryland Scraping Complete!")
    print(f"{'='*60}")
    print(f"Sources scraped:     {len(maryland_scrapers)}")
    print(f"Documents found:     {len(all_documents)}")
    print(f"New documents:       {results['stored']}")
    print(f"Updated documents:   {results['updated']}")
    print(f"Duplicates skipped:  {results['duplicates']}")
    print(f"Errors:              {results['errors']}")
    print(f"{'='*60}")
    print("\nBreakdown by source:")
    for source, count in source_stats.items():
        print(f"  {source}: {count}")
    print(f"{'='*60}\n")

    return response


# For local testing
if __name__ == '__main__':
    # Test with environment variables
    result = lambda_handler({}, None)
    print(json.dumps(json.loads(result['body']), indent=2))
