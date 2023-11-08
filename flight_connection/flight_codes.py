import json
import re
import requests
import os.path
from lxml import html

AIRLINE_CODES_LIST_URL = "https://en.wikipedia.org/wiki/List_of_airline_codes"
curr_dir = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(curr_dir, "airline_codes.json")


def get_airline_codes(write_to_file=False, airline_file_path=FILE_PATH):
    if os.path.exists(airline_file_path):
        return json.load(open(airline_file_path))
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


def strip_code(code: str) -> str:
    code = code.upper()
    # remove all whitespace
    code = "".join(code.split())
    return code


def is_iata_airline(airline_code: str) -> bool:
    if re.match("^[A-Z][\d]|[\d][A-Z]|[A-Z]{2}$", airline_code) is None:
        return False
    iata_codes = set([code["iata_code"] for code in get_airline_codes()])
    return (airline_code in iata_codes)


def is_icao_airline(airline_code: str) -> bool:
    if re.match("^[A-Z]{3}$", airline_code) is None:
        return False
    icao_codes = set([code["icao_code"] for code in get_airline_codes()])
    return (airline_code in icao_codes)


def iata_to_icao_airline(airline_code: str) -> bool:
    codes = get_airline_codes()
    for code in codes:
        if code["iata_code"] == airline_code.upper():
            return code["icao_code"]
    return None


def icao_to_iata_airline(airline_code: str) -> bool:
    codes = get_airline_codes()
    for code in codes:
        if code["icao_code"] == airline_code.upper():
            return code["iata_code"]
    return None


def iata_to_icao_flight(flight_code: str) -> str:
    flight_code = strip_code(flight_code)
    if re.match("^([A-Z][\d]|[\d][A-Z]|[A-Z]{2}|[A-Z]{3})([\d]{2,4})$", flight_code) is None:
        print("ERROR: invalid flight code {}".format(flight_code))
        return None
    if is_icao_airline(flight_code[:3]):
        # the airline code is ICAO
        return flight_code
    if is_iata_airline(flight_code[:2]):
        return iata_to_icao_airline(flight_code[:2]) + flight_code[2:]


if __name__ == "__main__":
    get_airline_codes(write_to_file=True)
    print(is_iata_airline("B6"))
    print(is_icao_airline("B6"))
    print(iata_to_icao_airline("B6"))
