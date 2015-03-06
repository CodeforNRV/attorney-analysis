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

for input_tag in soup.find_all('input'):
    print input_tag

# Choose the court we want to search
# https://eapps.courts.state.va.us/gdcourts/changeCourt.do
#POST
#selectedCourtsName:Accomack General District Court
#selectedCourtsFipCode:001
#sessionCourtsFipCode:

# Choose Hearing Date Search
# https://eapps.courts.state.va.us/gdcourts/caseSearch.do?fromSidebar=true&searchLanding=searchLanding&searchType=hearingDate&searchDivision=T&searchFipsCode=001&curentFipsCode=001

# Search for a date
# https://eapps.courts.state.va.us/gdcourts/caseSearch.do
#formAction:
#curentFipsCode:001
#searchTerm:03/06/2015
#searchHearingTime:
#searchCourtroom:
#lastName:
#firstName:
#middleName:
#suffix:
#searchHearingType:
#searchUnitNumber:
#caseSearch:Search
#searchFipsCode:001

# Find Finalized results

# Open result and check Filed Date
#https://eapps.courts.state.va.us/gdcourts/caseSearch.do?formAction=caseDetails&displayCaseNumber=GC15000299-00&localFipsCode=001&caseActive=true&clientSearchCounter=6

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

# Click next button
# https://eapps.courts.state.va.us/gdcourts/caseSearch.do
#formAction:caseDetails
#curentFipsCode:001
#searchTerm:03/04/2015
#searchHearingTime:
#searchCourtroom:
#lastName:
#firstName:
#middleName:
#suffix:
#searchHearingType:
#searchUnitNumber:
#searchFipsCode:001
#caseInfoScrollForward:Next
#unCheckedCases:
