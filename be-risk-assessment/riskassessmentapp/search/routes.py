import os
import random
import time
import asyncio
import aiohttp
from aiohttp import ClientSession, ClientTimeout
from googlesearch import search
from bs4 import BeautifulSoup
import spacy
import re
import json
from spacy.matcher import Matcher
from flask import Flask, jsonify, request, Blueprint
from math import exp
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from sentence_transformers import SentenceTransformer, util  # Import SBERT and cosine similarity
from transformers import pipeline, BertTokenizer, BertForTokenClassification  # New imports for advanced gender detection
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from openai import OpenAI
from dotenv import load_dotenv
import ast

risksearch = Blueprint('search', __name__, template_folder='templates')

nlp = spacy.load("en_core_web_sm")
sbert_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # Load SBERT model
load_dotenv()

OpenAI.api_key = os.getenv("OPENAI_API_KEY")
api_key = os.getenv("OPENAI_API_KEY")
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

def extract_pii_with_gpt(data_into_list, attributes, model="gpt-4o-mini"):
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

    # Define system and user prompts
    system_prompt = (
        "You are an advanced NLP assistant specializing in extracting Personally Identifiable Information (PII). "
        "When you cannot find any information for an attribute, explicitly return an empty list `[]` for that attribute."
    )
           # Construct the prompt
    prompt = (
            "Extract PII information from the following text document:\n"
            f"{input_data}\n\n"
            "Return results in dictionary format with these attributes:\n"
            "{'Name': '', 'Location': '', 'Email': '', 'Phone': '', 'DOB': '', 'Address': '', 'Gender': '', "
            "'Employer': '', 'Education': '', 'Birth Place': '', 'Personal Cell': '', 'Business Phone': '', "
            "'Facebook Account': '', 'Twitter Account': '', 'Instagram Account': '', 'DDL': '', "
            "'Passport': '', 'Credit Card': '', 'SSN': ''}. If no value exists for an attribute, return an empty string."
        )
    extracted_pii = None  # Initialize the variable to avoid reference errors

    try:
        # Make a request to GPT
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for consistent output
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

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(aiohttp.ClientError))
async def fetch_url(session, url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'}
    timeout = ClientTimeout(total=10)
    async with session.get(url, headers=headers, timeout=timeout) as response:
        response.raise_for_status()
        return await response.text()

async def scrape_google_results(query):
    tasks = []
    #urls = [url for url in search(query, num=21, stop=10, pause=2)]
    urls = []
    for url in search(query, num_results=21, safe=None):
        urls.append(url)
        print("Inside search delay")
        print(urls)
        time.sleep(random.uniform(0, 1)) 

    print("URLs being scraped:")
    for idx, url in enumerate(urls, 1):
        print(f"{idx}. {url}")

    print(f"\nTotal URLs to be scraped: {len(urls)}")
    async with ClientSession() as session:
        for url in urls:
            if not (url.endswith('.pdf') or '-image?' in url):
                tasks.append(fetch_url(session, url))
        responses = await asyncio.gather(*tasks, return_exceptions=True)
    return responses, urls

@risksearch.route('/', methods=["GET"])
async def risk_search():
    execution_start = time.time()
    query = request.args.get('searchName', '')
    if not query:
        return jsonify({"error": "No search query provided"}), 400

    data_into_list = []

    try:
        responses, urls = await scrape_google_results(query)
        for idx, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"Error fetching URL {urls[idx]}: {response}")
                continue
            soup = BeautifulSoup(response, 'html.parser')

            cleaned_data = clean_scraped_data(soup, query)


            parsed_text = soup.get_text()
            text = parsed_text.split('\n')
            text = list(filter(lambda x: x not in ('', '\r'), text))


            for line in text:
                if not line.isspace():
                    if idx == 20 and 'https://' in line:
                        line = line.replace('https://', ' https://')
                    aligned_line = align_sentence(line.strip())
                    #print(aligned_line)
                    data_into_list.append(aligned_line)
                    splitted_lines_list = re.split(r'\. |\.\[', aligned_line)
                    #data_into_list.extend(splitted_lines_list)
        #extracted_addresses = address_pattern(data_into_list, query)

        # Print relevant sentences
        '''print("\n=== Relevant Sentences ===")
        for line in data_into_list:
            print(line)'''

        output_match_term = []
        output_word = []
        output_line = []
        output_list_span_start = []
        output_list_span_end = []
        output_list_search = []
        output_list_url_no = []
        output_list_line_no = []
        output_list_match_count = []

        name_split = query.lower().split()
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

        attributes = extract_pii_with_gpt(data_into_list, attributes)

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

        '''for line_no, line in enumerate(data_into_list):
            email_matches = re.finditer(r'\S+@\S+', line)
            for m in email_matches:
                attributes['Email'].add(m.group(0))
                match_count = sum(1 for name in name_split if m.group(0).lower().find(name) >= 0)
                inp_list = ['Email', m.group(0), line, m.start(), m.end(), query, 0, line_no, match_count]
                append_list(output_match_term, output_word, output_line, output_list_span_start, output_list_span_end,
                            output_list_search, output_list_url_no, output_list_line_no, output_list_match_count,
                            inp_list)

            for pattern in phone_pattern:
                for m in re.finditer(pattern, line):
                    attributes['Phone'].add(m.group(0))
                    match_count = sum(1 for name in name_split if line.lower().find(name) >= 0)
                    inp_list = ['Phone', m.group(0), line, m.start(), m.end(), query, 0, line_no, match_count]
                    append_list(output_match_term, output_word, output_line, output_list_span_start,
                                output_list_span_end, output_list_search, output_list_url_no, output_list_line_no,
                                output_list_match_count, inp_list)

            pattern_values = dob_pattern(line)
            if pattern_values:
                attributes['DoB'].add(pattern_values[1])
                match_count = sum(1 for name in name_split if line.lower().find(name) >= 0)
                inp_list = [pattern_values[0], pattern_values[1], line, pattern_values[2], pattern_values[3], query, 0,
                            line_no, match_count]
                append_list(output_match_term, output_word, output_line, output_list_span_start, output_list_span_end,
                            output_list_search, output_list_url_no, output_list_line_no, output_list_match_count,
                            inp_list)

            pattern_values = address_pattern(line)
            if pattern_values:
                attributes['Address'].add(pattern_values[1])
                match_count = sum(1 for name in name_split if line.lower().find(name) >= 0)
                inp_list = [pattern_values[0], pattern_values[1], line, pattern_values[2], pattern_values[3], query, 0,
                            line_no, match_count]
                append_list(output_match_term, output_word, output_line, output_list_span_start, output_list_span_end,
                            output_list_search, output_list_url_no, output_list_line_no, output_list_match_count,
                            inp_list)
            # Call the modified address_pattern function to extract all relevant addresses
            extracted_addresses = address_pattern(data_into_list, query)

            # Process each extracted address
            for address in extracted_addresses:
                # Add the address directly to attributes['Address']
                attributes['Address'].add(address)

                # Create an input list (inp_list) for this address with relevant data
                inp_list = ["Address", address, " ".join(data_into_list), 0, 0, query, 0, 0, 0]

                # Append details of each address found to output lists
                append_list(output_match_term, output_word, output_line, output_list_span_start, output_list_span_end,
                            output_list_search, output_list_url_no, output_list_line_no, output_list_match_count,
                            inp_list)

            gender = gender_pattern(line)
            if gender:
                attributes['Gender'].add(gender)

            education = education_pattern(line)
            if education:
                attributes['Education'].add(education)

            birth_place = birth_place_pattern(line)
            if birth_place:
                attributes['Birth Place'].add(birth_place)

            ssn = ssn_pattern(line)
            if ssn:
                attributes['SSN'].add(ssn)

            passport = passport_pattern(line)
            if passport:
                attributes['Passport #'].add(passport)

            credit_card = credit_card_pattern(line)
            if credit_card:
                attributes['Credit Card'].add(credit_card)

            ddl = ddl_pattern(line)
            if ddl:
                attributes['DDL'].add(ddl)

            business_phone = business_phone_pattern(line)
            if business_phone:
                attributes['Business Phone'].add(business_phone)

            if idx == 20:
                social_media_list = []
                if '.linkedin.com' in line:
                    social_media_list.append('.linkedin.com')
                if 'https://www.instagram.com' in line:
                    social_media_list.append('https://www.instagram.com')
                if 'https://www.facebook.com' in line:
                    social_media_list.append('https://www.facebook.com')
                if 'twitter.com' in line:
                    social_media_list.append('twitter.com')

                if social_media_list:
                    out_social_med_list = find_social_media_acnt(social_media_list, line)
                    match_count = sum(1 for name in name_split if out_social_med_list[0][0].lower().find(name) >= 0)
                    inp_list = [out_social_med_list[0][1], out_social_med_list[0][0], line, '', '', query, 0, line_no,
                                match_count]
                    append_list(output_match_term, output_word, output_line, output_list_span_start,
                                output_list_span_end, output_list_search, output_list_url_no, output_list_line_no,
                                output_list_match_count, inp_list)

            doc = nlp(line.strip())
            for ent in doc.ents:
                if ent.label_ == 'PERSON':
                    attributes['Name'].add(ent.text.strip())
                elif ent.label_ == 'ORG':
                    attributes['Employer'].add(ent.text.strip())
                elif ent.label_ == 'GPE':
                    location = ent.text.strip()
                    if ',' in location:
                        city, country = [part.strip() for part in location.split(',', 1)]
                    else:
                        city, country = location, None
                    if country:
                        if country not in attributes['Location']:
                            attributes['Location'][country] = set()
                        attributes['Location'][country].add(city)

        attributes['Location'] = {country: list(cities) for country, cities in attributes['Location'].items()}'''

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