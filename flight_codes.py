import json
import requests
import os.path
from lxml import html

AIRLINE_CODES_LIST_URL = "https://en.wikipedia.org/wiki/List_of_airline_codes"
curr_dir = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(curr_dir, "airline_codes.json")


def get_airline_codes(read_from_file=False, write_to_file=False):
    if read_from_file:
        return json.load(open(FILE_PATH))
    page = requests.get(AIRLINE_CODES_LIST_URL)
    if page.status_code != 200:
        print("ERROR: failed to get airline code list")
        exit(1)
    tree = html.fromstring(page.text)
    airline_codes_table = tree.cssselect(".wikitable")[0]
    data_rows = airline_codes_table.cssselect("tr")[1:]
    data = [{
        "iata_code": row[0].text_content().strip(),
        "icao_code": row[1].text_content().strip(),
        "airline": row[2].text_content().strip(),
    } for row in data_rows]
    if write_to_file:
        f = open(FILE_PATH, "w")
        json.dump(data, f, indent=4)
    return data

if __name__ == "__main__":
    get_airline_codes(write_to_file=True)
