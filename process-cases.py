import csv
from courtreader import readers
from datetime import datetime

def parse_datetime(date):
    return datetime.strptime(date, "%m/%d/%y")

def load_case_file(file_path):
    cases = []
    with open(file_path, 'r') as case_file:
        case_file_reader = csv.DictReader(case_file)
        for row in case_file_reader:
            row['FIPS'] = row['FIPS'].zfill(3)
            row['FILE_DATE'] = parse_datetime(row['FILE_DATE'])
            row['FINAL_DISP_DATE'] = parse_datetime(row['FINAL_DISP_DATE'])
            row['MATCHING_CASES'] = []
            cases.append(row)
    return cases

court_reader = readers.DistrictCourtReader()
court_reader.connect()

cases = load_case_file('cases/2014.csv')
case = cases[0]
print case

fips_code = case['FIPS']
search_date = case['FINAL_DISP_DATE']
cases_on_date = court_reader.get_cases_by_date(fips_code, search_date)
for case_on_date in cases_on_date:
    if case_on_date['status'] == 'Finalized':
        print case_on_date['details_url']

