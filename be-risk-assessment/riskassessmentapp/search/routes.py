import os
import random
import time
import asyncio
import aiohttp
from aiohttp import ClientSession, ClientTimeout
from googlesearch import search
from bs4 import BeautifulSoup
import json
from flask import Flask, jsonify, request, Blueprint
from math import exp
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from openai import OpenAI
from dotenv import load_dotenv
import ast

risksearch = Blueprint('search', __name__, template_folder='templates')

load_dotenv()

OpenAI.api_key = os.getenv("OPENAI_API_KEY")
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()


def extract_pii_with_gpt(data_into_list, attributes, target_name, model="gpt-4o-mini"):
    """
        Modified version to extract PII attributes using GPT from structured, meaningful paragraphs
        rather than just lines of text.

        Args:
        - data_into_list (list): List of structured paragraphs with meaningful context about target person
        - attributes (dict): Dictionary containing sets for each PII attribute
        - target_name (str): Name of the target person
        - model (str): OpenAI model to use for the extraction

        Returns:
        - dict: Updated attributes dictionary with extracted PII values
    """
    # Combine the data into a single input for GPT
    # Include separator lines to help GPT understand the structure
    input_data = "\n\n".join(data_into_list)

    print(f"Extracting PII attributes for: {target_name}")
    print(f"Input data length: {len(input_data)} characters")

    # Define system and user prompts optimized for contextual extraction
    system_prompt = (
        f"You are an advanced NLP system specialized in extracting Personally Identifiable Information (PII) "
        f"from contextual, multi-paragraph text about a person. You excel at finding both explicit and implicit "
        f"personal details while ensuring high accuracy and proper attribution."
    )

    user_prompt = (
        "Extract all possible Personally Identifiable Information (PII) from the following structured text about "
        f"{target_name}:\n\n"
        f"{input_data}\n\n"
        "Guidelines for extraction:\n"
        "1. Extract the following attributes (provide empty string if not found):\n"
        "   - Name: Full name, including variations or nicknames\n"
        "   - Location: Current city/state/country of residence\n"
        "   - Email: Any email addresses\n"
        "   - Phone: Any phone numbers (personal or unspecified)\n"
        "   - DOB: Date of birth in MM-DD-YYYY format when possible\n"
        "   - Address: Full or partial physical addresses\n"
        "   - Gender: Gender information\n"
        "   - Employer: Current employer or business affiliation\n"
        "   - Education: Schools attended, degrees earned\n"
        "   - Birth Place: City/state/country of birth\n"
        "   - Personal Cell: Mobile phone numbers specifically\n"
        "   - Business Phone: Work-related phone numbers\n"
        "   - Facebook Account: Facebook username or profile info\n"
        "   - Twitter Account: Twitter handle or profile info\n"
        "   - Instagram Account: Instagram username or profile info\n"
        "   - DDL: Driver's license information\n"
        "   - Passport: Passport information\n"
        "   - Credit Card: Credit card details\n"
        "   - SSN: Social Security Number\n\n"

        "2. PAY SPECIAL ATTENTION to URL patterns, page titles, and metadata that might contain PII.\n"
        "3. For multiple values of the same attribute, use comma-separated strings.\n"
        "4. ONLY extract information about the target person, not others mentioned in the text.\n"
        "5. Use exactly these field names in your response.\n"
        "6. Return a valid JSON dictionary with the field names listed above.\n"
        "7. Do **not** include extra text, explanations, or additional details outside of the requested attributes.\n\n"
        "Format the final response as a **valid JSON dictionary**:\n"
        "{\n"
        "  'Name': '',\n"
        "  'Location': '',\n"
        "  'Email': '',\n"
        "  'Phone': '',\n"
        "  'DOB': '',\n"
        "  'Address': '',\n"
        "  'Gender': '',\n"
        "  'Employer': '',\n"
        "  'Education': '',\n"
        "  'Birth Place': '',\n"
        "  'Personal Cell': '',\n"
        "  'Business Phone': '',\n"
        "  'Facebook Account': '',\n"
        "  'Twitter Account': '',\n"
        "  'Instagram Account': '',\n"
        "  'DDL': '',\n"
        "  'Passport': '',\n"
        "  'Credit Card': '',\n"
        "  'SSN': ''\n"
        "}\n"
        "Ensure the response is **valid JSON** without extra text or explanations."
    )

    extracted_pii = None  # Initialize the variable to avoid reference errors

    try:
        # Make a request to GPT
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,  # Lower temperature for consistent output
            max_tokens=15000   # Adjust based on expected input/output size
        )

        # Log raw GPT response
        extracted_pii = response.choices[0].message.content.strip()
        print("[DEBUG] Raw GPT Response:\n", extracted_pii)

        if not extracted_pii:
            print("[ERROR] GPT response is None or empty.")
            return attributes  # Return the original attributes unchanged

    except Exception as e:
        print(f"[ERROR] Error processing GPT response:\n{e}")
        return attributes  # Return the original attributes unchanged

    # Attempt to parse the GPT response
    try:
        # Fix invalid JSON if necessary
        print("[DEBUG] Attempting to parse GPT response...")
        extracted_pii = extracted_pii.strip("```json").strip("```").strip()  # Remove markdown formatting
        print("[DEBUG] Cleaned GPT response:\n", extracted_pii)

        # Attempt JSON parsing
        pii_data = json.loads(extracted_pii)  # Parse as JSON
        print("[DEBUG] Parsed PII Data as JSON:\n", pii_data)

    except json.JSONDecodeError as e:
        print(f"[WARNING] JSON parsing failed. Trying ast.literal_eval...\nError: {e}")
        try:
            # Try evaluating as a Python dictionary
            pii_data = ast.literal_eval(extracted_pii)
            print("[DEBUG] Parsed PII Data using ast.literal_eval:\n", pii_data)
        except (ValueError, SyntaxError) as e:
            print(f"[ERROR] Failed to parse GPT result as dictionary:\n{extracted_pii}\nError: {e}")
            return attributes  # Return the original attributes unchanged

    # Update the attributes dictionary
    print("[DEBUG] Updating attributes dictionary...")
    for key, value in pii_data.items():
        if key in attributes:
            # Ensure attributes[key] is a set
            if not isinstance(attributes[key], set):
                attributes[key] = set()

            if value:  # Only add non-empty values
                attributes[key].add(value)
                print(f"[DEBUG] Added value for key '{key}': {value}")
            else:
                print(f"[DEBUG] Skipping empty value for key '{key}'.")

    print("[DEBUG] Final attributes dictionary:\n", attributes)
    return attributes

def calculate_privacy_score(willingness_measure, resolution_power, beta_coefficient):
    privacy_score = 1 / exp(beta_coefficient * (1 - willingness_measure) * resolution_power)
    return privacy_score


def calculate_overall_risk_score(pii_attributes, weights, willingness_measures, resolution_powers, beta_coefficients):
    overall_risk_score = 0
    if not any(pii_attributes.values()):
        return 0  # No personal information found
    for attribute in pii_attributes:
        if pii_attributes[attribute]:  # Only calculate for attributes that have values
            weight = weights.get(attribute, 0)
            willingness_measure = willingness_measures.get(attribute, 0)
            resolution_power = resolution_powers.get(attribute, 0)
            beta_coefficient = beta_coefficients.get(attribute, 1)
            privacy_score = calculate_privacy_score(willingness_measure, resolution_power, beta_coefficient)
            overall_risk_score += weight * privacy_score
    return overall_risk_score


async def extract_page_metadata(html_content, url):
    """
    Extract comprehensive metadata from a webpage.

    Args:
        html_content (str): The HTML content of the webpage
        url (str): The URL of the webpage

    Returns:
        dict: A dictionary containing detailed webpage metadata
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Basic URL analysis for domain and path
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path

    # Extract title
    title = soup.title.string if soup.title else "No title available"

    # Extract meta description
    description_tag = soup.find("meta", {"name": "description"})
    description = description_tag.get("content", "") if description_tag else ""

    # Extract meta keywords
    keywords_tag = soup.find("meta", {"name": "keywords"})
    keywords = keywords_tag.get("content", "") if keywords_tag else ""

    # Extract Open Graph metadata
    og_title = soup.find("meta", {"property": "og:title"})
    og_title = og_title.get("content", "") if og_title else ""

    og_description = soup.find("meta", {"property": "og:description"})
    og_description = og_description.get("content", "") if og_description else ""

    og_site_name = soup.find("meta", {"property": "og:site_name"})
    og_site_name = og_site_name.get("content", "") if og_site_name else ""

    # Extract a snippet of text (first paragraph or visible text)
    snippet = ""
    for p in soup.find_all('p'):
        if p.text and len(p.text.strip()) > 50:  # Find a paragraph with reasonable content
            snippet = p.text.strip()[:200] + "..." if len(p.text.strip()) > 200 else p.text.strip()
            break

    if not snippet:
        # If no good paragraph found, just get some visible text
        visible_text = soup.get_text().strip()
        snippet = visible_text[:200] + "..." if len(visible_text) > 200 else visible_text

    # Extract heading content as it's often very relevant
    h1_content = [h.text.strip() for h in soup.find_all('h1') if h.text.strip()]
    h2_content = [h.text.strip() for h in soup.find_all('h2') if h.text.strip()]

    h1_text = h1_content[0] if h1_content else ""
    h2_text = "; ".join(h2_content[:3]) if h2_content else ""  # Just include first few h2s

    # Create webpage info object with enhanced metadata
    webpage_info = {
        "url": url,
        "domain": domain,
        "title": title,
        "h1": h1_text,
        "h2_summary": h2_text,
        "description": description if description else og_description if og_description else snippet,
        "site_name": og_site_name if og_site_name else domain,
        "keywords": keywords,
        "snippet": snippet
    }

    return webpage_info


@retry(stop=stop_after_attempt(2), wait=wait_fixed(1),
       retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)))
async def fetch_url(session, url):
    """
    Fetch URL content with improved error handling and timeout management.

    Args:
        session (ClientSession): The aiohttp session to use
        url (str): The URL to fetch

    Returns:
        str: The HTML content of the URL

    Raises:
        Exception: If the URL cannot be fetched after retries
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }

    # Use a shorter timeout to fail faster on problematic URLs
    timeout = ClientTimeout(total=15, connect=5, sock_connect=5, sock_read=15)

    try:
        async with session.get(url, headers=headers, timeout=timeout, allow_redirects=True) as response:
            # Check for HTTP errors
            if response.status >= 400:
                raise aiohttp.ClientResponseError(
                    response.request_info,
                    response.history,
                    status=response.status,
                    message=f"HTTP Error {response.status}",
                    headers=response.headers
                )

            # Check content type to ensure it's HTML
            content_type = response.headers.get('Content-Type', '')
            if not ('text/html' in content_type.lower() or 'application/xhtml+xml' in content_type.lower()):
                raise ValueError(f"Unsupported content type: {content_type}")

            # Get the content
            html_content = await response.text()

            # Basic validation of the content
            if not html_content or len(html_content) < 500:  # Very small responses are likely errors
                raise ValueError("Response too small or empty")

            return html_content

    except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as e:
        print(f"Error fetching {url}: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error fetching {url}: {str(e)}")
        raise


async def get_search_results_metadata(query):
    """
    Search for query on Google and return comprehensive metadata for each result.
    This improved version filters out URLs that can't be fetched and includes enhanced metadata.

    Args:
        query (str): The search query (person's name)

    Returns:
        list: A list of dictionaries containing detailed metadata for each successfully fetched search result
    """
    # Try different approaches based on which package might be installed
    try:
        # For google package
        from googlesearch import search
        urls = [url for url in search(query, num=25, stop=25, pause=2)]
    except TypeError:
        try:
            # Alternative approach for older/different versions
            from googlesearch import search
            urls = [url for url in search(query, num_results=25, sleep_interval=2)]
        except (TypeError, AttributeError):
            try:
                # For google-search-results package (serpapi)
                from serpapi import GoogleSearch

                # You'll need an API key for this
                serpapi_key = os.getenv("SERPAPI_API_KEY")
                if not serpapi_key:
                    raise ValueError("SERPAPI_API_KEY environment variable not set")

                search_params = {
                    "q": query,
                    "num": 25,
                    "api_key": serpapi_key
                }
                search_results = GoogleSearch(search_params).get_dict()
                urls = [result.get('link') for result in search_results.get('organic_results', [])]
            except (ImportError, ValueError):
                # Fallback to a simple list of dummy URLs for testing
                print("WARNING: No suitable search package found. Using test URLs.")
                urls = [
                    f"https://example.com/profile/{query.replace(' ', '-').lower()}",
                    f"https://linkedin.com/in/{query.replace(' ', '-').lower()}",
                    f"https://twitter.com/{query.replace(' ', '').lower()}",
                    f"https://facebook.com/{query.replace(' ', '.').lower()}",
                    f"https://example.org/about/{query.replace(' ', '_').lower()}"
                ]

    print(f"Found {len(urls)} URLs for query: {query}")

    webpages_metadata = []
    successful_urls = 0

    async with ClientSession() as session:
        for url in urls:
            # Skip certain file types that we can't process
            if url.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx')) or '-image?' in url:
                print(f"Skipping unsupported file type: {url}")
                continue

            try:
                # Try to fetch the URL with a reasonable timeout
                html_content = await fetch_url(session, url)

                # Extract comprehensive metadata
                metadata = await extract_page_metadata(html_content, url)

                # Look for simple indicators that this page might be relevant to our search
                # This helps prioritize more relevant pages in the results
                relevance_score = 0
                query_terms = query.lower().split()

                # Check title, description, headings for query terms
                for term in query_terms:
                    if term in metadata["title"].lower():
                        relevance_score += 3  # Title matches are highly relevant
                    if term in metadata["description"].lower():
                        relevance_score += 2  # Description matches are relevant
                    if term in metadata["h1"].lower():
                        relevance_score += 2  # H1 matches are relevant
                    if term in metadata["h2_summary"].lower():
                        relevance_score += 1  # H2 matches are somewhat relevant

                # Add relevance score to metadata
                metadata["relevance_score"] = relevance_score

                webpages_metadata.append(metadata)
                successful_urls += 1
                print(f"Successfully extracted metadata from: {url} (relevance: {relevance_score})")

                # If we have enough successful URLs, we can stop
                if successful_urls >= 15:  # Set a reasonable limit for the number of results
                    break

            except Exception as e:
                # If URL can't be fetched, don't include it in the results
                print(f"Error fetching or processing URL {url}: {e}")
                # We don't add anything to webpages_metadata for failed URLs

    # Sort results by relevance score (most relevant first)
    webpages_metadata = sorted(webpages_metadata, key=lambda x: x["relevance_score"], reverse=True)

    print(f"Returning {len(webpages_metadata)} successfully fetched URLs")
    return webpages_metadata

async def clean_webpage_with_gpt(html_content, url, target_name, model="gpt-4o-mini"):
    """
    Use GPT to analyze a webpage and its metadata to extract structured information relevant to the target person.
    This enhanced version includes page metadata (title, description, URL) in the analysis.

    Args:
        html_content (str): The HTML content of the webpage
        url (str): The URL of the webpage
        target_name (str): The name of the person we're looking for information about
        model (str): OpenAI model to use for analysis

    Returns:
        list: A list containing meaningful paragraphs about the target person with PII information
    """
    try:
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract metadata
        page_title = soup.title.string if soup.title else "Untitled Page"

        # Extract meta description
        description_tag = soup.find("meta", {"name": "description"})
        meta_description = description_tag.get("content", "") if description_tag else ""

        # Extract meta keywords
        keywords_tag = soup.find("meta", {"name": "keywords"})
        meta_keywords = keywords_tag.get("content", "") if keywords_tag else ""

        # Get any OpenGraph metadata which often contains rich information
        og_title = soup.find("meta", {"property": "og:title"})
        og_title = og_title.get("content", "") if og_title else ""

        og_description = soup.find("meta", {"property": "og:description"})
        og_description = og_description.get("content", "") if og_description else ""

        # Extract the text content
        parsed_text = soup.get_text()

        # Basic preprocessing to make the text more manageable
        text = parsed_text.split('\n')
        text = list(filter(lambda x: x not in ('', '\r') and not x.isspace(), text))

        # Join a reasonable amount of text to send to GPT
        combined_text = "\n".join(text)
        truncated_text = combined_text[:20000]  # Limit to 20K chars to avoid token limits

        # Define system and user prompts for a more structured analysis
        system_prompt = (
            f"You are an expert analyst specializing in identifying and organizing personal information "
            f"from web content and metadata. Your expertise is in finding, contextualizing, and "
            f"structuring personal information in a meaningful way."
        )

        user_prompt = (
            f"I'm looking for information about {target_name}. Please analyze both the webpage content and its metadata.\n\n"
            f"METADATA:\n"
            f"URL: {url}\n"
            f"Page Title: {page_title}\n"
            f"Meta Description: {meta_description}\n"
            f"Meta Keywords: {meta_keywords}\n"
            f"OG Title: {og_title}\n"
            f"OG Description: {og_description}\n\n"
            f"WEBPAGE CONTENT:\n{truncated_text}\n\n"

            f"Please create a comprehensive summary of ALL information about {target_name}. "
            f"Focus on extracting personal identifiable information (PII) and organizing it into a meaningful narrative.\n\n"

            f"Instructions:\n"
            f"1. First, analyze the URL, title, and metadata for any information about {target_name}.\n"
            f"2. Then, analyze the webpage content and create a thorough summary of all information found.\n"
            f"3. Specifically look for and include ANY of these personal attributes if found:\n"
            f"   - Full name (including variations, nicknames, or formal names)\n"
            f"   - Location information (current location, hometown, places lived)\n"
            f"   - Contact details (email addresses, phone numbers)\n"
            f"   - Birth information (date of birth, age, birthplace)\n"
            f"   - Addresses (current or past residences, work addresses)\n"
            f"   - Gender information\n"
            f"   - Employment details (current employer, job title, work history)\n"
            f"   - Educational background (schools, degrees, graduation years)\n"
            f"   - Social media accounts (Facebook, Twitter, Instagram, etc.)\n"
            f"   - Any sensitive information (driver's license, passport numbers, financial info, etc.)\n\n"

            f"4. IMPORTANT: Format your response as a collection of detailed paragraphs that provide CONTEXT for the information. "
            f"   Don't just list facts - explain how they relate to the person and where/how they were mentioned.\n"
            f"5. If information seems contradictory, include all versions and note the contradiction.\n"
            f"6. Include ONLY information about {target_name}. Ignore information about other people.\n"
            f"7. If absolutely no information about {target_name} is found, respond with: 'NO_RELEVANT_INFORMATION'\n\n"

            f"Your goal is to create a comprehensive profile that captures ALL possible PII about {target_name} from this webpage "
            f"and its metadata in a way that preserves context and meaning."
        )

        # Make a request to GPT
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # Very low temperature for consistency
            max_tokens=15000  # Allow for detailed response
        )

        # Get the GPT response
        gpt_response = response.choices[0].message.content.strip()

        # If no information was found, return empty list
        if gpt_response == "NO_RELEVANT_INFORMATION":
            print(f"No relevant information found about {target_name} on this webpage and its metadata.")
            return []

        # Split into paragraphs for easier processing later
        paragraphs = gpt_response.split('\n\n')
        cleaned_paragraphs = [p.strip() for p in paragraphs if p.strip()]

        # Log the extracted information for debugging
        print(f"Extracted {len(cleaned_paragraphs)} meaningful paragraphs about {target_name} from {url}")

        return cleaned_paragraphs

    except Exception as e:
        print(f"Error in clean_webpage_with_gpt: {e}")
        # Return an empty list if there's an error
        return []


async def scrape_selected_urls(urls, target_name):
    """
    Scrape content from user-selected URLs and clean it using GPT.
    This updated version passes URL information to the cleaning function to include metadata analysis.

    Args:
        urls (list): List of URLs to scrape
        target_name (str): Name of the person we're looking for

    Returns:
        tuple: (list of structured content about the target person, boolean indicating if no data was found)
    """
    if not urls:
        return [], True

    all_cleaned_data = []
    url_count = 0
    success_count = 0

    async with ClientSession() as session:
        for url in urls:
            url_count += 1
            if url.endswith('.pdf') or '-image?' in url:
                print(f"Skipping unsupported file type: {url}")
                continue

            try:
                print(f"Fetching URL {url_count}/{len(urls)}: {url}")
                response = await fetch_url(session, url)

                # Check if the response is an exception
                if isinstance(response, Exception):
                    print(f"Error fetching URL {url}: {response}")
                    continue

                # Use enhanced GPT function to extract meaningful information from this webpage and its metadata
                print(f"Processing content from {url}...")
                # Pass the URL to the clean_webpage_with_gpt function
                cleaned_data = await clean_webpage_with_gpt(response, url, target_name)

                if cleaned_data:
                    success_count += 1
                    # Add source information as the first element
                    source_info = f"The following information was found on: {url}"
                    all_cleaned_data.append(source_info)

                    # Add the structured paragraphs
                    all_cleaned_data.extend(cleaned_data)

                    # Add a separator between different URLs
                    all_cleaned_data.append("---")

                    print(f"Successfully extracted information from {url} ({len(cleaned_data)} paragraphs)")
                else:
                    print(f"No relevant information found on {url}")

            except Exception as e:
                print(f"Error processing URL {url}: {e}")

    # Remove the last separator if it exists
    if all_cleaned_data and all_cleaned_data[-1] == "---":
        all_cleaned_data.pop()

    print(f"Processed {url_count} URLs, found relevant information on {success_count} URLs")
    print(f"Total paragraphs of information: {len(all_cleaned_data)}")

    if not all_cleaned_data:
        return [], True

    return all_cleaned_data, False


@risksearch.route('/', methods=["GET"])
async def risk_search():
    """Endpoint to search for a person and return webpage metadata for disambiguation"""
    query = request.args.get('searchName', '')
    if not query:
        return jsonify({"error": "No search query provided"}), 400

    try:
        # Get enhanced metadata with relevance scoring
        webpages_metadata = await get_search_results_metadata(query)

        if not webpages_metadata:
            return jsonify(
                {"message": "No relevant web results found for this name. Try a different search term."}), 404

        return jsonify({"webpages": webpages_metadata})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@risksearch.route('/extract', methods=["POST"])
async def extract_pii():
    """Endpoint to extract PII from selected URLs"""
    execution_start = time.time()
    print("Request Content-Type:", request.headers.get('Content-Type'))
    print("Request method:", request.method)
    print("Request JSON:", request.json)

    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    target_name = data.get('searchName', '')
    selected_urls = data.get('selectedUrls', [])
    print(f"Target name: {target_name}")
    print(f"Selected URLs: {selected_urls}")

    if not target_name:
        return jsonify({"error": "No search name provided"}), 400
    if not selected_urls:
        return jsonify({"error": "No URLs selected"}), 400

    try:
        print("About to scrape selected URLs")

        # Get cleaned data from selected URLs
        cleaned_data, no_relevant_data = await scrape_selected_urls(selected_urls, target_name)

        print(f"Cleaned data length: {len(cleaned_data)}")
        print(f"Sample cleaned data: {cleaned_data[:5] if cleaned_data else 'No data'}")

        if no_relevant_data:
            return jsonify({"message": "No relevant data found about this person."})

        attributes = {
            'Name': set(),
            'Location': {},
            'Email': set(),
            'Phone': set(),
            'DoB': set(),
            'Address': set(),
            'Gender': set(),
            'Employer': set(),
            'Education': set(),
            'Birth Place': set(),
            'Personal Cell': set(),
            'Business Phone': set(),
            'Facebook Account': set(),
            'Twitter Account': set(),
            'Instagram Account': set(),
            'DDL': set(),
            'Passport #': set(),
            'Credit Card': set(),
            'SSN': set()
        }

        print("This is Cleaned Data")
        for line in cleaned_data:
            print(line)

        attributes = extract_pii_with_gpt(cleaned_data, attributes, target_name)

        def print_attributes(attributes):
            """
            Helper function to pretty print the extracted PII attributes
            """
            print("\n=== Extracted PII Attributes ===")
            for key, value in attributes.items():
                if isinstance(value, set):
                    print(f"{key}:", list(value) if value else "[]")
                else:
                    print(f"{key}:", value if value else "[]")
            print("==============================\n")

        print_attributes(attributes)

        dictionary = {key: list(value) for key, value in attributes.items()}

        def print_attributes(attributes):
            """
            Helper function to pretty print the extracted PII attributes
            """
            print("\n=== Extracted PII Attributes ===")
            for key, value in attributes.items():
                if isinstance(value, set):
                    print(f"{key}:", list(value) if value else "[]")
                else:
                    print(f"{key}:", value if value else "[]")
            print("==============================\n")

        print_attributes(attributes)

        pii_attributes = list(dictionary.keys())

        weights = {'Name': 1, 'Address': 1, 'Location': 1, 'Gender': 1, 'Employer': 2, 'DoB': 2, 'Education': 1,
                   'Birth Place': 2, 'Personal Cell': 0.5, 'Email': 0.1, 'Business Phone': 0.1, 'Facebook Account': 1,
                   'Twitter Account': 0.1, 'Instagram Account': 0.1, 'DDL': 2, 'Passport #': 2, 'Credit Card': 2,
                   'SSN': 10}

        willingness_measures = {'Name': 1.0, 'Address': 0.1, 'Location': 0.1, 'Birth Place': 0.2, 'DoB': 0.83,
                                'Personal Cell': 0.16, 'Gender': 0.98, 'Employer': 0.5, 'Education': 0.8, 'Email': 0.7,
                                'Business Phone': 0.4, 'Facebook Account': 0.9, 'Twitter Account': 0.9,
                                'Instagram Account': 0.9, 'DDL': 0.2, 'Passport #': 0.05, 'Credit Card': 0.02,
                                'SSN': 0.01}

        resolution_powers = {'Name': 0.1, 'Address': 0.3, 'Location': 0.1, 'DoB': 0.7, 'Personal Cell': 0.9, 'Email': 0.95,
                             'Business Phone': 0.4, 'Facebook Account': 0.8, 'Twitter Account': 0.8, 'Instagram Account': 0.8,
                             'DDL': 1.0, 'Passport #': 1.0, 'Credit Card': 1.0, 'SSN': 1.0, 'Gender': 0.1, 'Employer': 0.2,
                             'Education': 0.3, 'Birth Place': 0.5}

        beta_coefficients = {'Name': 1, 'Address': 1, 'Location': 1, 'DoB': 1, 'Personal Cell': 1, 'Email': 1,
                             'Business Phone': 1, 'Facebook Account': 1, 'Twitter Account': 1, 'Instagram Account': 1,
                             'DDL': 1, 'Passport #': 1, 'Credit Card': 1, 'SSN': 1, 'Gender': 1, 'Employer': 1,
                             'Education': 1, 'Birth Place': 1}

        overall_risk_score = calculate_overall_risk_score(dictionary, weights, willingness_measures, resolution_powers,
                                                          beta_coefficients)

        if overall_risk_score == 0:
            risk_level = 'Low'
        elif overall_risk_score <= 2.74:
            risk_level = 'Very Low'
        elif 2.74 < overall_risk_score <= 5.48:
            risk_level = 'Low'
        elif 5.48 < overall_risk_score <= 6.87:
            risk_level = 'Medium'
        elif 6.87 < overall_risk_score <= 12.25:
            risk_level = 'High'
        else:
            risk_level = 'Very High'

        dictionary['risk_score'] = overall_risk_score
        dictionary['risk_level'] = risk_level

        execution_time = time.time() - execution_start
        print(f"Program Ended, Time: {execution_time} seconds")

        return jsonify(dictionary)

    except Exception as e:
        return jsonify({"error": str(e)}), 400
