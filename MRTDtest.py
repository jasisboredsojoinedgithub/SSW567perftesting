import unittest
from unittest.mock import patch
from MRTD import scanMRZ, decodeMRZ, encodeMRZ, mismatch, calculate_check_digit

class TestMRZFunctions(unittest.TestCase):
    def setUp(self):
        # Default test data for validation
        self.line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<"
        self.line2 = "L898902C36UTO7408122F1204159ZE184226B<<<<<1"
        self.decoded_fields = {
            "document-type": "P",
            "issuing-country": "UTO",
            "last-name": "ERIKSSON",
            "first-name": "ANNA MARIA",
            "passport-number": "L898902C3",
            "passport-check-digit": "6",
            "country-code": "UTO",
            "birth-date": "740812",
            "birth-date-check-digit": "2",
            "sex": "F",
            "expiration-date": "120415",
            "expiration-date-check-digit": "9",
            "personal-number": "ZE184226B<<<<<",
            "personal-number-check-digit": "1",
        }

    @patch("MRTD.scanMRZ")
    def test_scan(self, mock_scan):
        """Test designed to verify scanMRZ function returns None"""
        mock_scan.return_value = None
        self.assertIsNone(scanMRZ(), "scanMRZ should return None")

    def test_decode_valid(self):
        """Test valid decoding of MRZ strings"""
        result = decodeMRZ(self.line1, self.line2)
        self.assertEqual(result, self.decoded_fields)

    def test_decode_invalid_lengths(self):
        """Test that decodeMRZ raises an error for invalid input lengths"""
        invalid_line1 = "P<UTO"
        invalid_line2 = "L898902"
        with self.assertRaises(IndexError, msg="decodeMRZ should raise IndexError for invalid lengths."):
            decodeMRZ(invalid_line1, invalid_line2)

    def test_encode(self):
        """Test valid encoding of fields into MRZ strings"""
        expected_line1 = f"P<{self.decoded_fields['issuing-country']}{self.decoded_fields['last-name']}<<{self.decoded_fields['first-name'].replace(' ', '<')}".ljust(44, "<")
        expected_line2 = self.line2
        result_line1, result_line2 = encodeMRZ(self.decoded_fields)
        self.assertEqual(result_line1, expected_line1)
        self.assertEqual(result_line2, expected_line2)

    def test_encode_invalid_field(self):
        """Test encodeMRZ raises a KeyError for missing fields"""
        invalid_fields = self.decoded_fields.copy()
        invalid_fields.pop("passport-number")  # Remove a required field
        with self.assertRaises(KeyError, msg="encodeMRZ should raise KeyError for missing fields."):
            encodeMRZ(invalid_fields)

    def test_mismatch_no_mismatches(self):
        """Test no mismatches are found in valid data"""
        result = mismatch(self.decoded_fields)
        self.assertEqual(result, [])

    def test_mismatch_with_errors(self):
        """Test mismatch detection for incorrect check digits"""
        modified_fields = self.decoded_fields.copy()
        modified_fields["passport-check-digit"] = "7"  # Incorrect check digit
        modified_fields["birth-date-check-digit"] = "3"  # Incorrect check digit
        result = mismatch(modified_fields)
        self.assertIn("Passport Number there is a mismatch in the digit check", result)
        self.assertIn("Birth Date there is a mismatch in the digit check", result)

    def test_calculate_check_digit_numeric(self):
        """Test check digit calculation for numeric fields"""
        test_field = "123456789"
        result = calculate_check_digit(test_field)
        expected = (1 * 7 + 2 * 3 + 3 * 1 + 4 * 7 + 5 * 3 + 6 * 1 + 7 * 7 + 8 * 3 + 9 * 1) % 10
        self.assertEqual(result, expected)

    def test_calculate_check_digit_alphanumeric(self):
        """Test check digit calculation for alphanumeric fields"""
        test_field = "ABC123"
        result = calculate_check_digit(test_field)
        expected = ((10 * 7) + (11 * 3) + (12 * 1) + (1 * 7) + (2 * 3) + (3 * 1)) % 10
        self.assertEqual(result, expected)

    def test_calculate_check_digit_special_chars(self):
        """Test check digit calculation with special characters"""
        test_field = "A<B<C"
        result = calculate_check_digit(test_field)
        expected = ((10 * 7) + (0 * 3) + (11 * 1) + (0 * 7) + (12 * 3)) % 10
        self.assertEqual(result, expected)

    def test_calculate_check_digit_all_zeros(self):
        """Test check digit calculation with all zeros"""
        test_field = "000000000"
        result = calculate_check_digit(test_field)
        self.assertEqual(result, 0)

    def test_calculate_check_digit_empty_field(self):
        """Test check digit calculation with an empty field"""
        test_field = ""
        result = calculate_check_digit(test_field)
        self.assertEqual(result, 0, "Check digit for an empty field should be 0.")

    def test_dynamic_decode(self):
        """Dynamic decoding test for integration with performance scripts"""
        test_record = "P<CIVLYNN<<NEVEAH<BRAM<<<<<<<<<<<<<<<<<<<<<<;W620126G54CIV5910106F9707302AJ010215I<<<<<<6"
        line1, line2 = test_record.split(";")
        result = decodeMRZ(line1, line2)
        self.assertIn("passport-number", result)
        self.assertEqual(result["passport-number"], "W620126G5")


if __name__ == "__main__":
    unittest.main()

