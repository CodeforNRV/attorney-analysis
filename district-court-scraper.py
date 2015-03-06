import cookielib
import os
import re
import sys
import urllib
import urllib2
import webbrowser
from bs4 import BeautifulSoup
from time import sleep

user_agent = u"Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; " + \
    u"rv:1.9.2.11) Gecko/20101012 Firefox/3.6.11"

# Get cookie and list of courts
cookieJar = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
opener.addheaders = [('User-Agent', user_agent)]

home = opener.open('https://eapps.courts.state.va.us/gdcourts/captchaVerification.do?landing=landing')
html = BeautifulSoup(home.read())

captcha_script_url = None
for script_tag in html.find_all('script', {'src':True}):
    if script_tag['src'].startswith('https://www.google.com/recaptcha/api/challenge'):
        captcha_url = script_tag['src']
captcha_image_url = 'https://www.google.com/recaptcha/api/image?c='
captcha_challenge = None
for line in urllib2.urlopen(captcha_url):
    if line.strip().startswith('challenge'):
        captcha_challenge = line.split(':')[1].strip()[1:-2]

webbrowser.open(captcha_image_url + captcha_challenge)
captcha_response = raw_input('Enter CAPTCHA: ')

data = urllib.urlencode({
    'recaptcha_challenge_field': captcha_challenge,
    'recaptcha_response_field': captcha_response,
    'accept': 'Accept',
    'pageName': 'landingCaptchaVerificationPage',
    'showCaptcha': True})
capthca_verification_url = u"https://eapps.courts.state.va.us/gdcourts/captchaVerification.do"
html = opener.open(capthca_verification_url, data)
print html.read()

raw_input('PAUSE')

case_search_url = u"https://eapps.courts.state.va.us/gdcourts/caseSearch.do?welcomePage=welcomePage"
html = opener.open(case_search_url)
print html.read()
#html = BeautifulSoup(home.read())
