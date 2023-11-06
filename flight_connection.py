import argparse
import json
from pprint import pprint
import re
import functools
from typing import List
from flight_types import *

import requests


BASE_URL = "https://flightaware.com"


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Check if you can make a tight layover")
    parser.add_argument(
        "flight_code_leg_1",
        type=str,
        help="flight code of the first leg of the journey",
        metavar="flight_code_leg_1",
        nargs=1,
    )
    parser.add_argument(
        "flight_code_leg_2",
        type=str,
        help="flight code of the second leg of the journey",
        metavar="flight_code_leg_2",
        nargs=1,
    )
    return parser


def get_flight_info(flight_code: str):
    # TEMPORARY
    # if flight_code == "ETD102":
    #     return json.load(open("ETD102.json"))
    # if flight_code == "ETD270":
    #     return json.load(open("ETD270.json"))
    # if flight_code == "JBU217":
    #     return json.load(open("JBU217.json"))
    # if re.match(r"([A-Z]{2}|[A-Z]\d|\d[A-Z])\s?\d{3,4}", flight_code) is None:
    #     print("ERROR: {} is not a flight code".format(flight_code))
    #     exit(1)
    flight_page_url = BASE_URL + "/live/flight/" + flight_code
    flight_page = requests.get(flight_page_url)
    if flight_page.status_code != 200:
        print("ERROR: there was an error fetching the flight page for {}".format(
            flight_code))
        print(flight_page.text)
        exit(1)
    match = re.search(
        r"<script>var trackpollBootstrap = (.*);</script>", flight_page.text)
    if match is None:
        print("ERROR: could not find flight data in HTML page")
        exit(1)
    flight_data = json.loads(match.group(1))
    return list(flight_data["flights"].values())[0]


def print_flight_info(flight_info):
    print("Flight {} from {} to {}".format(
        flight_info["codeShare"]["iataIdent"],
        flight_info["origin"]["friendlyName"],
        flight_info["destination"]["friendlyName"]))


def get_flight_history(flight_info) -> List[Flight]:
    return [Flight(
        origin=get_airport_info(flight_info, "origin"),
        destination=get_airport_info(flight_info, "destination"),
        start=Time(
            scheduled_sec=flight["gateDepartureTimes"]["scheduled"],
            actual_sec=flight["gateDepartureTimes"]["actual"]
        ),
        end=Time(
            scheduled_sec=flight["gateArrivalTimes"]["scheduled"],
            actual_sec=flight["gateArrivalTimes"]["actual"]
        )
    ) for flight in flight_info["activityLog"]["flights"] if
        (flight["gateDepartureTimes"]["actual"]) is not None and
        (flight["gateArrivalTimes"]["actual"] is not None)]


def get_connection_times(leg_1_info, leg_2_info) -> List[Connection]:
    leg_1_dest = leg_1_info["destination"]["iata"]
    leg_2_orig = leg_2_info["origin"]["iata"]
    if not leg_1_dest == leg_2_orig:
        print("ERROR: the two flights are not connected")
        print("       flight 1 arrives in {}, flight 2 departs from {}",
              leg_1_dest, leg_2_orig)
        exit(1)
    leg_1_history = get_flight_history(leg_1_info)
    leg_2_history = get_flight_history(leg_2_info)
    connection_times = []
    for leg_1 in leg_1_history:
        closest_leg_2 = min(leg_2_history, key=lambda l: abs(
            l.start.actual_sec - leg_1.end.actual_sec))
        connection_time = closest_leg_2.start.actual_sec - leg_1.end.actual_sec
        if connection_time < 0 or connection_time > 24 * 60 * 60:
            continue
        connection_times.append(Connection(
            start=leg_1.end,
            end=closest_leg_2.start,
        ))
        leg_2_history.remove(closest_leg_2)
    return connection_times


def get_airport_info(flight_info, arr_or_dest="destination") -> Airport:
    return Airport(
        iata_code=flight_info[arr_or_dest]["iata"],
        timezone=flight_info[arr_or_dest]["TZ"],
        name=flight_info[arr_or_dest]["friendlyName"],
        location_name=flight_info[arr_or_dest]["friendlyLocation"],
        location=tuple(flight_info[arr_or_dest]["coord"]),
    )


if __name__ == '__main__':
    parser = setup_parser()
    args = parser.parse_args()
    FLIGHT_CODE_LEG_1 = args.flight_code_leg_1[0]
    FLIGHT_CODE_LEG_2 = args.flight_code_leg_2[0]

    leg_1_info = get_flight_info(FLIGHT_CODE_LEG_1)
    leg_2_info = get_flight_info(FLIGHT_CODE_LEG_2)

    print("Leg 1:")
    print_flight_info(leg_1_info)
    print("Leg 2:")
    print_flight_info(leg_2_info)

    # with open(FLIGHT_CODE_LEG_1 + ".json", "w") as f:
    #     json.dump(leg_1_info, f, indent=4, sort_keys=True)

    # with open(FLIGHT_CODE_LEG_2 + ".json", "w") as f:
    #     json.dump(leg_2_info, f, indent=4, sort_keys=True)

    connection_times = get_connection_times(leg_1_info, leg_2_info)
    print("Connection stats over the last {} flights:".format(len(connection_times)))
    print("Avg. connection time: {:.2f} hours".format(
        functools.reduce(lambda acc, x: acc + x.length_sec(), connection_times, 0) / len(connection_times) / (60 * 60)))
    # for connection in connection_times:
    #     print(connection.length_sec())
    print("Avg. delay of leg 1: {:.2f} hours".format(
        functools.reduce(lambda acc, x: acc + x.start.delay_sec(), connection_times, 0) / len(connection_times) / (60 * 60)))
    # for connection in connection_times:
    #     print(connection.start.delay_sec())
    print("Avg. delay of leg 2: {:.2f} hours".format(
        functools.reduce(lambda acc, x: acc + x.end.delay_sec(), connection_times, 0) / len(connection_times) / (60 * 60)))
    # for connection in connection_times:
    #     print(connection.end.delay_sec())
