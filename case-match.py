import csv
from datetime import datetime

fips = {}
with open('st51_va_cou.txt', 'r') as fips_file:
    fips_reader = csv.reader(fips_file)
    for line in fips_reader:
        fips[int(line[2])] = line[3]

no_attorney_cases = []
bad_fips_codes = []
with open('2014.csv', 'r') as no_attorney_file:
    no_attorney_reader = csv.DictReader(no_attorney_file)
    for row in no_attorney_reader:
        if int(row['FIPS']) in fips:
            row['FILE_DATE'] = datetime.strptime(row['FILE_DATE'], "%m/%d/%y")
            row['FINAL_DISP_DATE'] = datetime.strptime(row['FINAL_DISP_DATE'], "%m/%d/%y")
            row['LOCALITY'] = fips[int(row['FIPS'])]
            if 'Roanoke' not in row['LOCALITY']:
                row['LOCALITY'] = row['LOCALITY'].replace('County', '')
            if 'Roanoke' not in row['LOCALITY']:
                row['LOCALITY'] = row['LOCALITY'].replace('city', '')
            else:
                row['LOCALITY'] = row['LOCALITY'].replace('city', 'City')
            row['LOCALITY'] = row['LOCALITY'].replace(' ', '')
            no_attorney_cases.append(row)
        elif int(row['FIPS']) not in bad_fips_codes:
            bad_fips_codes.append(int(row['FIPS']))
print 'Bad FIPS Codes', str(bad_fips_codes)

cases = {}
with open('va_criminal_cases_14.csv', 'r') as cases_file:
    cases_reader = csv.DictReader(cases_file)
    for row in cases_reader:
        if row['DispositionDate'] != '':
            if row['Court'] not in cases:
                cases[row['Court']] = []
            cases[row['Court']].append({
                'case_number': row['CaseNumber'],
                'name': row['Defendant'], 
                'file_date': row['Filed'][:10], 
                'deposition_date': row['DispositionDate'][:10]
            })

for no_attorney_case in no_attorney_cases:
    no_attorney_case['names'] = []
    no_attorney_case['case_numbers'] = []
    file_date = str(no_attorney_case['FILE_DATE'])[:10]
    depo_date = str(no_attorney_case['FINAL_DISP_DATE'])[:10]
    matching_locality = []
    for locality in cases:
        if no_attorney_case['LOCALITY'] + 'Circuit' in locality:
            matching_locality.append(locality)
    if len(matching_locality) != 1:
        print no_attorney_case['LOCALITY'], str(matching_locality)
    else:
        for case in cases[matching_locality[0]]:
            if case['file_date'] == file_date and case['deposition_date'] == depo_date:
                print 'MATCH!'
                no_attorney_case['names'].append(case['name'])
                no_attorney_case['case_numbers'].append(case['case_number'])
                print no_attorney_case