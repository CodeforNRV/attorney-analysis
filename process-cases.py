import csv
import sys
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

def find_complete_case(partial_case, cases):
    for i, case in enumerate(cases):
        if case['status'] == 'Finalized':
            print '\tGetting details for case ' + str(i+1) + \
                  ' of ' + str(len(cases)) + '\r',
            sys.stdout.flush()
            case_details = reader.get_case_details(case)
            if cases_match(partial_case, case_details):
                print '\nMATCH ' + case_details['case_number']
                partial_case['MATCHING_CASES'].append({
                    'CASE_NUMBER': case_details['case_number'],
                    'NAME': case_details['name']
                })

def cases_match(partial_case, case_details):
    return case_details['filed_date'] == partial_case['FILE_DATE'] and \
           case_details['case_type'] == 'Felony' and \
           case_details['offense_class'] == partial_case['OFFENSE_CLASS_CODE']

reader = readers.DistrictCourtReader()
reader.connect()

partial_cases = load_case_file('cases/2014.csv')
for i, partial_case in enumerate(partial_cases):
    print '\nPartial case ' + str(i+1) + ' of ' + str(len(partial_cases))
    fips_code = partial_case['FIPS']
    search_date = partial_case['FINAL_DISP_DATE']
    cases = reader.get_cases_by_date(fips_code, search_date)
    find_complete_case(partial_case, cases)

