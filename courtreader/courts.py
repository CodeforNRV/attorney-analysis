import captcha
import urllib2
from bs4 import BeautifulSoup
from opener import Opener

class DistrictCourt:
    url_root = 'https://eapps.courts.state.va.us/gdcourts/'
    
    def __init__(self):
        self.opener = Opener()
        
        # Open the case search page
        url = DistrictCourt.url_root
        url += 'caseSearch.do?welcomePage=welcomePage'
        page = self.opener.open(url)
        page_content = page.read()
        soup = BeautifulSoup(page_content)
        
        # See if we need to solve a captcha
        if 'By clicking Accept' in page_content:
            captcha_url = DistrictCourt.url_root
            captcha_url += 'captchaVerification.do'
            captcha.solve(self.opener, captcha_url)
            
            page = self.opener.open(url)
            soup = BeautifulSoup(page.read())
        
        # Load list of courts and fips codes
        fips = [tag['value'] for tag in soup.find_all('input', {'name':'courtFips'})]
        names = [tag['value'] for tag in soup.find_all('input', {'name':'courtName'})]
        self.court_names = {}
        for f, c in zip(fips, names):
            self.court_names[f] = c
