import xml.etree.ElementTree as ET
import re
import csv
from typing import Dict, List
import typer

def extract_abbreviations(text: str) -> List[str]:
    """
    Extracts abbreviations from the given text using predefined patterns.
    """
    patterns = [
        r'{{initialism (.*?)}}',
        r'{{abbreviation (.*?)}}',
        r'{{acronym (.*?)}}'
    ]
    results = []
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            result = match.group(1).split('|')[0]
            results.append(result.strip())
    return list(set(results))

def pos_and_map(text: str) -> str:
    """
    Identifies parts of speech (POS) in the input string based on a predefined mapping.
    """
    pos_mapping = {
        "===Adjective===": "adj",
        "===Adverb===": "adv",
        "===Noun===": "noun",
        "===Verb===": "verb",
    }
    found_pos = []
    for pos, abbr in pos_mapping.items():
        if pos in text:
            found_pos.append(abbr)
    return "|".join(found_pos)

def process_wiktionary_dump(input_file: str, output_file: str):
    """
    Processes a Wiktionary XML dump file and extracts relevant information.
    """
    wiktionary_dict: Dict[str, List] = {}
    
    for _, element in ET.iterparse(input_file, events=("end",)):
        if element.tag.endswith("}page"):
            title = element.find("./{*}title").text
            text = element.find("./{*}revision/{*}text").text
            
            if "==English==" in text:
                pos = pos_and_map(text)
                abbreviations = extract_abbreviations(text)
                
                wiktionary_dict[title] = [pos, abbreviations]
            
            element.clear()
    
    write_csv(output_file, wiktionary_dict)

def write_csv(csv_file_path: str, wiktionary_dict: Dict[str, List]):
    """
    Writes extracted data to a CSV file.
    """
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['word', 'pos', 'abbreviations'])
        for word, (pos, abbrs) in wiktionary_dict.items():
            csv_writer.writerow([word, pos, '|'.join(abbrs)])

app = typer.Typer()

@app.command()
def main(input_file: str, output_file: str):
    """
    Process a Wiktionary XML dump file and extract relevant information.
    """
    process_wiktionary_dump(input_file, output_file)

if __name__ == "__main__":
    app()