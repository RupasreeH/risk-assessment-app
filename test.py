import os
import time
import asyncio
import aiohttp
from aiohttp import ClientSession, ClientTimeout
from googlesearch import search
from bs4 import BeautifulSoup
import spacy
import random
import re
import json
from spacy.matcher import Matcher
from flask import Flask, jsonify, request
from math import exp
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from sentence_transformers import SentenceTransformer, util  # Import SBERT and cosine similarity
from openai import OpenAI
from dotenv import load_dotenv
import ast



app = Flask(__name__)


nlp = spacy.load("en_core_web_sm")
sbert_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # Load SBERT model
load_dotenv()

OpenAI.api_key = os.getenv("OPENAI_API_KEY")
api_key = os.getenv("OPENAI_API_KEY")
GOOGLE_KG_API_KEY = os.getenv("GOOGLE_KG_API_KEY")
client = OpenAI()


def align_sentence(sent):
    sent_split = sent.split()
    result_sent_list = []
    for string in sent_split:
        if string.isupper():
            result_sent_list.append(string)
        else:
            y = ''
            for idx, i in enumerate(string):
                if i.isupper() and idx != 0:
                    i = ' ' + i
                y += i
            result_sent_list.append(y)
    return ' '.join(result_sent_list)






def is_noise_line(line):
    """Heuristics to detect if the line is part of navigation, ads, or common footer/header."""
    noise_keywords = [
        "menu", "navigation", "privacy policy", "terms of service", "login", "subscribe",
        "more", "about", "footer", "contact us", "©", "cookie", "follow us", "back to top"
    ]
    return any(keyword in line.lower() for keyword in noise_keywords)


def clean_scraped_data(soup, query_name):
    """Advanced cleaning to filter irrelevant data and focus on person-related information."""
    data_into_list = []

    for element in soup.find_all(['div', 'p']):
        text_content = element.get_text().strip()
        if text_content and not text_content.isspace():
            data_into_list.append(text_content)

    cleaned_data = []
    for line in data_into_list:
        if not is_noise_line(line):
            cleaned_data.append(line)

    final_cleaned_data = []
    for line in cleaned_data:
        doc = nlp(line)
        entities = [ent.text for ent in doc.ents]
        if any(query_name.lower() in ent.lower() for ent in entities) or entities:
            final_cleaned_data.append(line)

    final_cleaned_data = list(set(final_cleaned_data))  # Remove duplicates

    return final_cleaned_data


def extract_pii_with_gpt(data_into_list, attributes, target_name, model="gpt-4o"):
    """
    Extract PII attributes using GPT and store results in the existing attributes dictionary.

    Args:
    - data_into_list (list): List of strings containing web-scraped data.
    - attributes (dict): Dictionary containing sets for each PII attribute.
    - model (str): OpenAI model to use for the extraction.

    Returns:
    - dict: Updated attributes dictionary with extracted PII values or empty sets where no values are found.
    """
    # Combine the data into a single input for GPT
    input_data = "\n".join(data_into_list)
    print(target_name)

    # Define system and user prompts
    system_prompt = (
        f"You are an advanced NLP assistant specializing in extracting Personally Identifiable Information (PII) from unstructured text. "
        f"Extract PII only for the individual named: {target_name}. Ignore any PII that does not belong to this person. "
        f"If certain attributes are missing, explicitly return an empty string for those fields. "
        f"Ensure extracted data follows the correct structure and is free from formatting errors."
    )

    user_prompt = (
        "Extract all possible Personally Identifiable Information (PII) from the following unstructured document:\n\n"
        f"{input_data}\n\n"
        "Follow these strict guidelines while extracting PII:\n"
        "1. Extract Name, Location, Email, Phone, DOB, Address, Gender, Employer, Education, Birth Place, Personal Cell, "
        "Business Phone, Social Media Accounts (Facebook, Twitter, Instagram), Driver’s License (DDL), Passport, Credit Card, and SSN.\n"
        "2. If a field is missing or unidentifiable, return an empty string `''` for that attribute.\n"
        "3. Preserve full names, emails, and phone numbers without modifying their structure.\n"
        "4. Extract dates (such as DOB) in `MM-DD-YYYY` format where possible.\n"
        "5. If the document is unstructured and includes multiple individuals, locate {target_name} and extract only their PII.\n"
        "6. If multiple values exist for an attribute (e.g., multiple emails), return them as a **comma-separated string**.\n"
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
def dob_pattern(text):
    doc = nlp(text)
    list_return = []

    pattern_dob_year = [{'LOWER': 'born', 'POS': 'VERB'}, {'POS': 'NUM', 'LENGTH': 4}]
    pattern_dob = [{'LOWER': 'born', 'POS': 'VERB'}, {'POS': 'NUM'}, {'POS': 'PROPN'}, {'POS': 'NUM'}]

    matcher = Matcher(nlp.vocab, validate=True)
    matcher.add('Year_of_Birth', [pattern_dob_year])
    matcher.add('Date_of_Birth', [pattern_dob])

    found_matches = matcher(doc)

    if found_matches:
        for match_id, start_pos, end_pos in found_matches:
            string_id = nlp.vocab.strings[match_id]
            span = doc[start_pos:end_pos]
            list_return = [string_id, span.text[5:], start_pos, end_pos]
    else:
        pattern_born = [{'LOWER': 'born', 'POS': 'VERB'}]
        matcher = Matcher(nlp.vocab, validate=True)
        matcher.add('born', [pattern_born])
        first_match = matcher(doc)

        if first_match:
            pattern_dob1 = [{'POS': 'NUM'}, {'POS': 'PROPN'}, {'POS': 'NUM', 'LENGTH': 4}]
            matcher1 = Matcher(nlp.vocab, validate=True)
            matcher1.add('Date_of_Birth1', [pattern_dob1])
            found_matches = matcher1(doc)
            for match_id, start_pos, end_pos in found_matches:
                string_id = nlp.vocab.strings[match_id]
                span = doc[start_pos:end_pos]
                list_return = [string_id, span.text, start_pos, end_pos]

    return list_return




def find_social_media_acnt(inp_list, line):
    id_name_type = []
    dictSocialMedia = {"https://www.instagram.com": "Instagram ID", ".linkedin.com": "LinkedIn Profile",
                       "https://www.facebook.com": "Facebook ID", "twitter.com": "Twitter ID"}
    for soc_med_type in inp_list:
        li = list(line.split(' '))
        for idx, i in enumerate(li):
            if soc_med_type in i and soc_med_type != 'https://www.facebook.com':
                id_name_type.append([li[idx + 2], dictSocialMedia[soc_med_type]])
                break
            if soc_med_type in i and soc_med_type == 'https://www.facebook.com':
                if li[idx + 2] in ('public', 'people'):
                    if str(li[idx + 4])[-1]:
                        id_name_type.append([li[idx + 4] + li[idx + 5], dictSocialMedia[soc_med_type]])
                    else:
                        id_name_type.append([li[idx + 4], dictSocialMedia[soc_med_type]])
                    break
                id_name_type.append([li[idx + 2], dictSocialMedia[soc_med_type]])
    return id_name_type


def gender_pattern(text):
    gender_keywords = ['he', 'she', 'his', 'her', 'male', 'female', 'gender']
    doc = nlp(text.lower())
    for token in doc:
        if token.text in gender_keywords:
            return token.text.capitalize()
    return None


def education_pattern(text):
    education_keywords = ['university', 'college', 'degree', 'bachelor', 'master', 'phd']
    doc = nlp(text.lower())
    for token in doc:
        if any(keyword in token.text for keyword in education_keywords):
            return token.text.capitalize()
    return None


def birth_place_pattern(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "GPE":  # GPE refers to geographical locations
            return ent.text
    return None


def ssn_pattern(text):
    match = re.search(r'\b\d{3}-\d{2}-\d{4}\b', text)
    return match.group(0) if match else None


def passport_pattern(text):
    match = re.search(r'\b[A-PR-WYa-pr-wy][1-9]\d\s?\d{4}[1-9]\b', text)
    return match.group(0) if match else None


def credit_card_pattern(text):
    match = re.search(r'\b(?:\d[ -]*?){13,16}\b', text)
    return match.group(0) if match else None


def ddl_pattern(text):
    match = re.search(r'\b[A-Za-z]\d{7}\b', text)  # Common pattern for driver's license numbers
    return match.group(0) if match else None


def business_phone_pattern(text):
    match = re.search(r'\b[\+]{0,1}[\d]{1,4}[\s-]{0,1}[\d]{1,4}[\s-]{0,1}[\d]{2,4}[\s-]{0,1}[\d]{2,4}\b',
                      text)  # Generic business phone pattern
    return match.group(0) if match else None


def append_list(output_match_term, output_word, output_line, output_list_span_start, output_list_span_end,
                output_list_search, output_list_url_no, output_list_line_no, output_list_match_count, inp_list):
    output_match_term.append(inp_list[0])
    output_word.append(inp_list[1])
    output_line.append(inp_list[2])
    output_list_span_start.append(inp_list[3])
    output_list_span_end.append(inp_list[4])
    output_list_search.append(inp_list[5])
    output_list_url_no.append(inp_list[6])
    output_list_line_no.append(inp_list[7])
    output_list_match_count.append(inp_list[8])


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
    Extract metadata from a webpage including title, description, and keywords.

    Args:
        html_content (str): The HTML content of the webpage
        url (str): The URL of the webpage

    Returns:
        dict: A dictionary containing the webpage metadata
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract title
    title = soup.title.string if soup.title else "No title available"

    # Extract meta description
    description_tag = soup.find("meta", {"name": "description"})
    description = description_tag.get("content", "") if description_tag else ""

    # Extract meta keywords
    keywords_tag = soup.find("meta", {"name": "keywords"})
    keywords = keywords_tag.get("content", "") if keywords_tag else ""

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

    # Create webpage info object
    webpage_info = {
        "url": url,
        "title": title,
        "description": description if description else snippet,
        "keywords": keywords
    }

    return webpage_info






@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(aiohttp.ClientError))
async def fetch_url(session, url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'}
    timeout = ClientTimeout(total=10)
    async with session.get(url, headers=headers, timeout=timeout) as response:
        response.raise_for_status()
        return await response.text()


async def get_search_results_metadata(query):
    """
    Search for query on Google and return metadata for each result.

    Args:
        query (str): The search query (person's name)

    Returns:
        list: A list of dictionaries containing metadata for each search result
    """
    urls = [url for url in search(query, tld="com", num=21, stop=21, pause=2)]
    print(f"Found {len(urls)} URLs for query: {query}")

    webpages_metadata = []

    async with ClientSession() as session:
        for url in urls:
            if url.endswith('.pdf') or '-image?' in url:
                continue

            try:
                html_content = await fetch_url(session, url)
                metadata = await extract_page_metadata(html_content, url)
                webpages_metadata.append(metadata)
                print(f"Extracted metadata from: {url}")
            except Exception as e:
                print(f"Error fetching or processing URL {url}: {e}")
                # Add a basic entry even if we couldn't fetch the full metadata
                webpages_metadata.append({
                    "url": url,
                    "title": "Could not fetch title",
                    "description": "Failed to load page",
                    "keywords": ""
                })

    return webpages_metadata


async def scrape_selected_urls(urls):
    """
    Scrape content from user-selected URLs.

    Args:
        urls (list): List of URLs to scrape

    Returns:
        tuple: (list of raw responses, list of URLs, boolean indicating if no data was found)
    """

    if not urls:
        return [], [], True

    relevant_responses = []
    relevant_urls = []

    async with ClientSession() as session:
        for url in urls:
            if url.endswith('.pdf') or '-image?' in url:
                continue

            try:
                response = await fetch_url(session, url)

                # Check if the response is an exception
                if isinstance(response, Exception):
                    print(f"Error fetching URL {url}: {response}")
                    continue

                relevant_responses.append(response)
                relevant_urls.append(url)

            except Exception as e:
                print(f"Error fetching or processing URL {url}: {e}")

        if not relevant_responses:
            return [], [], True



    return relevant_responses, relevant_urls, False

@app.route('/search', methods=["GET"])
async def search_person():
    """Endpoint to search for a person and return webpage metadata for disambiguation"""
    query = request.args.get('searchName', '')
    if not query:
        return jsonify({"error": "No search query provided"}), 400

    try:
        webpages_metadata = await get_search_results_metadata(query)
        return jsonify({"webpages": webpages_metadata})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/extract', methods=["POST"])
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



        responses, urls, no_relevant_data = await scrape_selected_urls(selected_urls)

        print(f"Responses type: {type(responses)}, length: {len(responses)}")
        print(f"First response sample (truncated): {str(responses[0])[:100] if responses else 'No response'}")
        print(f"URLs returned: {urls}")
        print(f"No relevant data flag: {no_relevant_data}")
        if no_relevant_data:
            return jsonify({"message": "No Data Found."})
        data_into_list = []


        for idx, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"Error fetching URL {urls[idx]}: {response}")
                continue
            soup = BeautifulSoup(response, 'html.parser')



            #cleaned_data = clean_scraped_data(soup, query)


            parsed_text = soup.get_text()
            text = parsed_text.split('\n')
            text = list(filter(lambda x: x not in ('', '\r'), text))



            for line in text:
                if not line.isspace():
                    if idx == 20 and 'https://' in line:
                        line = line.replace('https://', ' https://')
                    aligned_line = align_sentence(line.strip())
                    data_into_list.append(aligned_line)
                    splitted_lines_list = re.split(r'\. |\.\[', aligned_line)
                    #data_into_list.extend(splitted_lines_list)
        #extracted_addresses = address_pattern(data_into_list, query)




        # Print relevant sentences
        print("\n=== Relevant Sentences ===")
        for line in data_into_list:
            print(line)

        if not data_into_list:
            return jsonify({"message": "No Data Found."})

        output_match_term = []
        output_word = []
        output_line = []
        output_list_span_start = []
        output_list_span_end = []
        output_list_search = []
        output_list_url_no = []
        output_list_line_no = []
        output_list_match_count = []

        name_split = target_name.lower().split()
        phone_pattern = [
            r'[\d]?[(]{1}[\d]{3}[)]{1}[\s]?[\d]{3}[-\s]{1}[\d]{4}',
            r'[+]{1}[\d]{2}[\s]{1}[(]?[\+]?[)]?[\d]{2}[\s]{1}[\d]{4}[\s]{1}[\d]{4}',
            r'[+]{1}[\d]{2}[\s]{1}[(]?[\d]?[)]?[\d]{3}[\s]{1}[\d]{3}[\s]{1}[\d]{3}',
            r'[\d]{3}[-\s]{1}[\d]{3}[-\s]{1}[\d]{4}'
        ]

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

        if not data_into_list:
            return jsonify({"message": "No Data Found."})

        attributes = extract_pii_with_gpt(data_into_list, attributes,target_name)

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
        return jsonify({"error": str(e)}), 500

# Root route for backward compatibility
@app.route('/', methods=["GET"])
async def api_root():
    return jsonify({"message": "Please use /search and /extract endpoints for the enhanced API."})



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
