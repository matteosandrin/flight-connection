import unittest
from unittest.mock import patch
from unittest import TestCase
from flight_connection import flight_codes

MOCK_AIRLINE_CODES = [{
    "iata_code": "B6",
    "icao_code": "JBU",
    "airline": "JetBlue Airways"
}]


class StripCodeTest(TestCase):

    def test_lower_code(self):
        result = flight_codes.strip_code("jbu217")
        self.assertEqual("JBU217", result)

    def test_whitespace_code(self):
        result = flight_codes.strip_code("\tJBU 217\n")
        self.assertEqual("JBU217", result)


@patch('flight_connection.flight_codes.get_airline_codes')
class IsIataAirlineTest(TestCase):

    def test_valid_code(self, mock_get_airline_codes):
        mock_get_airline_codes.return_value = MOCK_AIRLINE_CODES
        self.assertEqual(flight_codes.is_iata_airline("B6"), True)

    def test_invalid_code_regex(self, mock_get_airline_codes):
        mock_get_airline_codes.return_value = MOCK_AIRLINE_CODES
        self.assertEqual(flight_codes.is_iata_airline("XXXX"), False)

    def test_invalid_code_not_in_list(self, mock_get_airline_codes):
        mock_get_airline_codes.return_value = MOCK_AIRLINE_CODES
        self.assertEqual(flight_codes.is_iata_airline("XY"), False)


@patch('flight_connection.flight_codes.get_airline_codes')
class IsIcaoAirlineTest(TestCase):

    def test_valid_code(self, mock_get_airline_codes):
        mock_get_airline_codes.return_value = MOCK_AIRLINE_CODES
        self.assertEqual(flight_codes.is_icao_airline("JBU"), True)

    def test_invalid_code_regex(self, mock_get_airline_codes):
        mock_get_airline_codes.return_value = MOCK_AIRLINE_CODES
        self.assertEqual(flight_codes.is_icao_airline("XXXX"), False)

    def test_invalid_code_not_in_list(self, mock_get_airline_codes):
        mock_get_airline_codes.return_value = MOCK_AIRLINE_CODES
        self.assertEqual(flight_codes.is_icao_airline("XYZ"), False)


@patch('flight_connection.flight_codes.get_airline_codes')
class IataToIcaoAirlineTest(TestCase):

    def test_valid_code(self, mock_get_airline_codes):
        mock_get_airline_codes.return_value = MOCK_AIRLINE_CODES
        self.assertEqual(flight_codes.iata_to_icao_airline("B6"), "JBU")

    def test_invalid_code_not_in_list(self, mock_get_airline_codes):
        mock_get_airline_codes.return_value = MOCK_AIRLINE_CODES
        self.assertIsNone(flight_codes.iata_to_icao_airline("XY"))


@patch('flight_connection.flight_codes.get_airline_codes')
class IcaoToIataAirlineTest(TestCase):

    def test_valid_code(self, mock_get_airline_codes):
        mock_get_airline_codes.return_value = MOCK_AIRLINE_CODES
        self.assertEqual(flight_codes.icao_to_iata_airline("JBU"), "B6")

    def test_invalid_code_not_in_list(self, mock_get_airline_codes):
        mock_get_airline_codes.return_value = MOCK_AIRLINE_CODES
        self.assertIsNone(flight_codes.icao_to_iata_airline("XYZ"))


@patch('flight_connection.flight_codes.get_airline_codes')
class IataToIcaoFlightTest(TestCase):

    def test_valid_iata_code(self, mock_get_airline_codes):
        mock_get_airline_codes.return_value = MOCK_AIRLINE_CODES
        self.assertEqual(flight_codes.iata_to_icao_flight("B61234"), "JBU1234")

    def test_valid_icao_code(self, mock_get_airline_codes):
        mock_get_airline_codes.return_value = MOCK_AIRLINE_CODES
        self.assertEqual(flight_codes.iata_to_icao_flight("JBU1234"), "JBU1234")

    def test_invalid_code_regex(self, mock_get_airline_codes):
        mock_get_airline_codes.return_value = MOCK_AIRLINE_CODES
        self.assertIsNone(flight_codes.iata_to_icao_flight("XXXX12"))
