import time
import json
import csv
import unittest
from MRTD import decodeMRZ
import os
print("Current working directory:", os.getcwd())

# Dynamically get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct file paths
encoded_file = os.path.join(script_dir, "records_encoded.json")
decoded_file = os.path.join(script_dir, "records_decoded.json")
output_csv = os.path.join(script_dir, "execution_times.csv")

with open(encoded_file, "r") as ef, open(decoded_file, "r") as df:
    encoded_records = json.load(ef)["records_encoded"]
    decoded_records = json.load(df)["records_decoded"]

def measure_time(func, *args):
    start_time = time.time()
    func(*args)
    end_time = time.time()
    return end_time - start_time

def process_records_no_tests(records):
    for record in records:
        line1, line2 = record.split(";")
        decodeMRZ(line1, line2)

def process_records_with_tests(records):
    for record in records:
        line1, line2 = record.split(";")
        
        # Create a temporary test case for dynamic decoding
        class DynamicDecodeTestCase(unittest.TestCase):
            def test_dynamic_decode(self):
                result = decodeMRZ(line1, line2)
                self.assertTrue("passport-number" in result)
        
        unittest.TextTestRunner().run(
            unittest.TestLoader().loadTestsFromTestCase(DynamicDecodeTestCase)
        )

k_values = [100] + [i for i in range(1000, 10001, 1000)]
results = []

for k in k_values:
    subset_records = encoded_records[:k]

    time_no_tests = measure_time(process_records_no_tests, subset_records)
    time_with_tests = measure_time(process_records_with_tests, subset_records)

    results.append([k, time_no_tests, time_with_tests])

with open(output_csv, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Lines_Read", "Exec_Time_No_Tests", "Exec_Time_With_Tests"])
    writer.writerows(results)

print(f"Results written to {output_csv}")

