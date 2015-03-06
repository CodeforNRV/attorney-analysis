import csv
import cookielib
import os
import os.path
import pickle
import re
import sys
import urllib
import urllib2
import webbrowser
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep

def solve_captcha(opener):
    # Get this party started
    page = opener.open('https://eapps.courts.state.va.us/gdcourts/captchaVerification.do?landing=landing')
    soup = BeautifulSoup(page.read())

    with open('cookie', 'w') as f:
        f.write(pickle.dumps(list(cookieJar)))

    # Get the captcha image
    captcha_script_url = None
    for script_tag in soup.find_all('script', {'src':True}):
        if script_tag['src'].startswith('https://www.google.com/recaptcha/api/challenge'):
            captcha_url = script_tag['src']
    captcha_image_url = 'https://www.google.com/recaptcha/api/image?c='
    captcha_challenge = None
    page = urllib2.urlopen(captcha_url)
    for line in page:
        if line.strip().startswith('challenge'):
            captcha_challenge = line.split(':')[1].strip()[1:-2]

    # Show the captcha image to the user and ask them to solve it
    webbrowser.open(captcha_image_url + captcha_challenge)
    captcha_response = raw_input('Enter CAPTCHA: ')

    # Submit our captcha solution
    data = urllib.urlencode({
        'recaptcha_challenge_field': captcha_challenge,
        'recaptcha_response_field': captcha_response,
        'accept': 'Accept',
        'pageName': 'landingCaptchaVerificationPage',
        'showCaptcha': True})
    url = u"https://eapps.courts.state.va.us/gdcourts/captchaVerification.do"
    page = opener.open(url, data)

    # Did we pass the captcha?
    if 'The reCAPTCHA challenge failed' in page.read():
        print 'Captcha Failed'
        sys.exit(0)


user_agent = u"Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; " + \
    u"rv:1.9.2.11) Gecko/20101012 Firefox/3.6.11"

# Create page opener that stores cookie
cookieJar = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
opener.addheaders = [('User-Agent', user_agent)]

# Try to load cookie
if os.path.isfile('cookie'):
    with open('cookie', 'r') as f:
        for cookie in pickle.loads(f.read()):
            cookieJar.set_cookie(cookie)

# Open the case search page
url = u"https://eapps.courts.state.va.us/gdcourts/caseSearch.do?welcomePage=welcomePage"
page = opener.open(url)
page_content = page.read()
soup = BeautifulSoup(page_content)

# See if we need to solve a captcha
if 'By clicking Accept' in page_content:
    solve_captcha(opener)
    page = opener.open(url)
    soup = BeautifulSoup(page.read())

# Load list of courts and fips codes
fips = [tag['value'] for tag in soup.find_all('input', {'name':'courtFips'})]
names = [tag['value'] for tag in soup.find_all('input', {'name':'courtName'})]
court_names = {}
for f, c in zip(fips, names):
    court_names[f] = c

# load cases
cases = []
with open('cases/2014.csv', 'r') as case_file:
    case_file_reader = csv.DictReader(case_file)
    for row in case_file_reader:
        row['FIPS'] = row['FIPS'].zfill(3)
        row['COURT_NAME'] = court_names[row['FIPS']]
        row['FILE_DATE'] = datetime.strptime(row['FILE_DATE'], "%m/%d/%y")
        row['FINAL_DISP_DATE'] = datetime.strptime(row['FINAL_DISP_DATE'], "%m/%d/%y")
        cases.append(row)

case = cases[0]
print case
search_date = case['FINAL_DISP_DATE'].strftime('%m/%d/%Y')

# Choose the court we want to search
data = urllib.urlencode({
    'selectedCourtsName': case['COURT_NAME'],
    'selectedCourtsFipCode': case['FIPS'],
    'sessionCourtsFipCode': ''
})
url = u"https://eapps.courts.state.va.us/gdcourts/changeCourt.do"
opener.open(url, data)

# Choose Hearing Date Search
url = u"https://eapps.courts.state.va.us/gdcourts/caseSearch.do"
url += u"?fromSidebar=true&searchLanding=searchLanding"
url += u"&searchType=hearingDate&searchDivision=T&"
url += u"&searchFipsCode=" + case['FIPS']
url += u"&curentFipsCode=" + case['FIPS']
opener.open(url)

# Search for a date
data = urllib.urlencode({
    'formAction':'',
    'curentFipsCode':case['FIPS'],
    'searchTerm':search_date,
    'searchHearingTime':'',
    'searchCourtroom':'',
    'lastName':'',
    'firstName':'',
    'middleName':'',
    'suffix':'',
    'searchHearingType':'',
    'searchUnitNumber':'',
    'caseSearch':'Search',
    'searchFipsCode':case['FIPS']
})
url = u"https://eapps.courts.state.va.us/gdcourts/caseSearch.do"
page = opener.open(url, data)
soup = BeautifulSoup(page.read())

# Find Finalized results
finalized_case_urls = []
while True:
    rows = soup.find('table', {'class':'tableborder'}).find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if cells[0]['class'][0] == 'gridheader':
            continue
        case_detail_url = cells[1].a['href']
        case_status = list(cells[6].stripped_strings)[0]
        if case_status == 'Finalized':
            finalized_case_urls.append(case_detail_url)

    # Click next button, if its there
    if soup.find('input', {'name': 'caseInfoScrollForward'}) is None:
        break
    
    data = urllib.urlencode({
        'formAction':'',
        'curentFipsCode':case['FIPS'],
        'searchTerm':search_date,
        'searchHearingTime':'',
        'searchCourtroom':'',
        'lastName':'',
        'firstName':'',
        'middleName':'',
        'suffix':'',
        'searchHearingType':'',
        'searchUnitNumber':'',
        'searchFipsCode':case['FIPS'],
        'caseInfoScrollForward':'Next',
        'unCheckedCases':''
    })
    url = u"https://eapps.courts.state.va.us/gdcourts/caseSearch.do"
    page = opener.open(url, data)
    soup = BeautifulSoup(page.read())

print case['COURT_NAME']
for url in finalized_case_urls:
    url = 'https://eapps.courts.state.va.us/gdcourts/' + url
    page = opener.open(url)
    soup = BeautifulSoup(page.read())
    content = list(soup.find('td', text=re.compile('Case Number')) \
                       .parent.stripped_strings)
    case_number = content[1]
    filed_date = datetime.strptime(content[3], "%m/%d/%Y")
    content = list(soup.find('td', text=re.compile('Name')) \
                       .parent.stripped_strings)
    name = content[1]
    print case_number, name, filed_date
    if filed_date == case['FILE_DATE']:
        print 'MATCH'

# Go back to search results
# https://eapps.courts.state.va.us/gdcourts/criminalDetail.do
#formAction:backButton
#searchFipsCode:001
#localFipsCode:001
#searchDivision:
#searchType:caseNumber
#currentIndex:0
#maxSize:0
#className:content clearfix
#localLastName:
#forward:caseInfoScrollForwardButton
#back:
#button:Back to Search Results
#clientSearchCounter:6

