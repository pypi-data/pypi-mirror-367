import json
import re
import unicodedata

import requests
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import ChatOpenAI

from core.utils.app_config import AppConfig

import logging
import time

logger = logging.getLogger(__name__)
config = AppConfig()
model = ChatOpenAI(openai_api_key=config.get("OPENAI_API_KEY"),
    temperature=0,
    top_p=1.0,
    frequency_penalty=0,
    presence_penalty=0,
    max_tokens=None)
logger.info("Initialized ChatOpenAI model")

from typing import List, Dict


def clean_text(text: str) -> str:
    logger.info("Cleaning text of non-ASCII characters and extra spaces")
    # Remove non-ASCII characters (non-English)
    text = ''.join([char for char in text if char.isascii()])
    # Remove escape sequences like \x03
    text = re.sub(r'\\x[0-9A-Fa-f]{2}', '', text)
    # Normalize Unicode text (NFKD form)
    text = unicodedata.normalize('NFKD', text)
    # Remove extra spaces
    return re.sub(r'\s+', ' ', text).strip()


def ingest_document(source: str) -> str:
    """
    Ingest document text from a URL or a local file.
    Supports .pdf (via PyPDF2) or plain text files.
    """
    logger.debug("Ingesting document from source: %s", source)
    if source.startswith("http"):
        logger.debug("Fetching remote URL: %s", source)
        response = requests.get(source)
        response.raise_for_status()
        raw_text = response.text
        logger.debug("Fetched URL %s [status=%d], raw content length=%d",
            source, response.status_code, len(raw_text))
        cleaned = clean_text(raw_text)
        logger.debug("Cleaned text length: %d", len(cleaned))
        return cleaned

    if source.lower().endswith(".pdf"):
        logger.debug("Reading PDF file: %s", source)
        raw_text = ""
        reader = PdfReader(source)
        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            raw_text += page_text + "\n"
            logger.debug("Extracted page %d text length: %d", idx + 1, len(page_text))
        logger.debug("Total raw PDF text length before cleaning: %d", len(raw_text))
        cleaned = clean_text(raw_text)
        logger.debug("Cleaned PDF text length: %d", len(cleaned))
        return cleaned

    logger.debug("Reading plain-text file: %s", source)
    with open(source, "r", encoding="utf-8") as f:
        raw_text = f.read()
    logger.debug("Read plain-text file %s, raw length %d", source, len(raw_text))
    cleaned = clean_text(raw_text)
    logger.debug("Cleaned text length: %d", len(cleaned))
    return cleaned


example_dict = {
    "rule": "Offerors are required to demonstrate their ability to perform in a minimum of Task Area 1 plus 5 other Task Areas",
    "description": "(Task Area 1 plus 3 other Task Areas for HUBZone; Task Area 1 plus 5 other Task Areas for SDVOSB; and Task Area 1 plus 5 other Task Areas",
    "value": "6"
}


def extract_compliance_rules(text: str, regulation: str, text_input: str = "") -> list:
    """
    Extract compliance rules for a given regulation using the local LLaMA model.
    The LLM is prompted to output a JSON array of rules (each rule being an object with keys like 'rule', 'description', and optionally 'value').
    """
    logger.info("Extracting compliance rules for regulation '%s'", regulation)
    if text_input:
        logger.debug("Additional rules input: %s", text_input)
    additional_rules = ""
    if text_input:
        additional_rules = f"Additionally, please follow the following rules: {text_input}."
    full_prompt = f"""
    You are an expert in {regulation} compliance. Extract solicitation requirements from the following text and return them exclusively as a valid JSON array. 
    
    {additional_rules}

    Each JSON object in the array MUST include these keys:
    - "requirements": (string) A short, concise title of the solicitation requirement.
    - "description": (string) A clear, detailed explanation of the solicitation requirement.
    - "value": (optional string) A specific numerical value or threshold explicitly mentioned in the requirement.

    JSON Example:
    [
    {json.dumps(example_dict)}
    ]

    STRICT REQUIREMENTS:
    - You MUST respond ONLY with a valid JSON array.
    - You MUST NOT include any summaries, commentary, explanations, or additional text outside the JSON structure.
    - Your response MUST start with '[' and end with ']' with no additional text before or after.
    - The description should be an actionable issue that can be used to CHECK if a requirement is being enforced. For example, instead of "name a security officer", use something like "verify there is a named security officer"

    Text for requirement extraction:
    <<<
    {text}
    >>>
    """
    logger.debug("Constructed full LLM prompt (length %d)", len(full_prompt))
    user_message = [{
        'role': 'user',
        'content': full_prompt,
    }]
    try:
        start_time = time.time()
        response = model.invoke(user_message)
        elapsed = time.time() - start_time
        logger.debug("LLM invocation completed in %.2fs", elapsed)
        string = response.content
        logger.debug("Raw LLM output: %s", string)
    except Exception:
        logger.exception("LLM invocation failed for regulation '%s'", regulation)
        return []
    try:
        match = re.search(r"```(?:json)?\s*(\[[\s\S]*?\])\s*```", string)
        if match:
            payload = match.group(1)
        else:
            payload = string.strip()
        rules = json.loads(payload)
        logger.debug(
            "Parsed %d rules from LLM output for regulation '%s'",
            len(rules), regulation
        )
    except Exception:
        logger.exception(
            "Failed to decode JSON from LLM output for regulation '%s'",
            regulation
        )
        logger.debug("LLM output for decoding: %s", string)
        rules = []
    return rules


def extract_requirements_by_sections(
        text: str,
        sections: List[str],
        regulation: str
) -> Dict[str, List[Dict[str, str]]]:
    """Extract solicitation requirements for each evaluation section listed in `sections`.

    For each section heading, find the corresponding text segment in the document,
    invoke the compliance rule extractor focusing on that section, and
    return a mapping from section heading to its extracted requirements.
    """
    logger.info("Extracting requirements by sections for regulation '%s'", regulation)
    requirements_map: Dict[str, List[Dict[str, str]]] = {}
    for idx, heading in enumerate(sections):
        logger.debug("Searching for section heading: '%s'", heading)
        match = re.search(re.escape(heading), text)
        if not match:
            logger.warning("Section heading '%s' not found in document.", heading)
            continue
        start = match.start()
        if idx + 1 < len(sections):
            next_heading = sections[idx + 1]
            next_match = re.search(re.escape(next_heading), text[start + len(heading):])
            end = start + len(heading) + (next_match.start() if next_match else len(text))
            logger.debug("Section '%s' spans chars %d to %d (until next heading '%s')",
                heading, start, end, next_heading)
        else:
            end = len(text)
            logger.debug("Section '%s' spans chars %d to %d (till end of text)", heading, start, end)
        section_text = text[start:end]
        logger.debug("Section '%s' text length: %d", heading, len(section_text))
        prompt = f"Please extract solicitation requirements specifically for the evaluation section titled '{heading}'."
        logger.debug("Prompting extract_compliance_rules for section '%s'", heading)
        reqs = extract_compliance_rules(section_text, regulation, text_input=prompt)
        logger.info("Extracted %d requirements for section '%s'", len(reqs), heading)
        requirements_map[heading] = reqs
    logger.info("Completed requirements extraction for %d sections", len(requirements_map))
    return requirements_map


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    logger.info("Starting solicitation ingestion pipeline")
    base_dir = r"./data/RFx/requests"
    sources = {
        "Solicitations": [
            f"{base_dir}/HIPAA_Privacy.pdf",
            f"{base_dir}/HIPAA_2.pdf",
        ],
        # add other regs here...
    }

    regulation_rules = {}
    all_text_chunks = []
    regulation = "HIPAA"
    logger.debug("Initial ingestion for regulation 'HIPAA' from %s", sources["HIPAA"][0])
    text = ingest_document(sources["HIPAA"][0])
    for regulation, docs in sources.items():
        regulation_rules[regulation] = []
        logger.info("Processing regulation '%s' with %d source(s)", regulation, len(docs))
        for source in docs:
            logger.info("Loading document: %s", source)
            try:
                text = ingest_document(source)
                logger.debug("Ingested text length for %s: %d", source, len(text))
            except Exception:
                logger.exception("Error ingesting document %s", source)
                continue

            splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_text(text)
            logger.info("Split text into %d chunks (chunk_size=%d, overlap=%d)", len(chunks), splitter.chunk_size, splitter.chunk_overlap)
            all_text_chunks.extend(chunks)

            try:
                rules = extract_compliance_rules(text, regulation)
                logger.info("Extracted %d rules from document %s", len(rules), source)
            except Exception:
                logger.exception("Error extracting compliance rules for regulation '%s' from document %s", regulation, source)
                rules = []
            regulation_rules[regulation].extend(rules)

        logger.info("Extraction complete for regulation '%s'; total rules: %d", regulation, len(regulation_rules[regulation]))
        logger.debug("Rules for regulation '%s': %s", regulation, json.dumps(regulation_rules[regulation], indent=2))

    logger.info("Solicitation ingestion pipeline finished; processed %d regulation(s), total text chunks: %d", len(regulation_rules), len(all_text_chunks))
