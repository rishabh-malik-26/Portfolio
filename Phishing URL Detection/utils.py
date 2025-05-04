import re
from urllib.parse import urlparse
import pandas as pd
import numpy as np 



def url_length(url):
    length = len(url)
    return length

def domain_extractor(url):
    try:
        return urlparse(url).netloc if isinstance(url,str) else None
    except Exception:
        return None
    
def number_of_hyphens(url):
    number =url.count("-")
    return number

from urllib.parse import urlparse, parse_qs

def count_query_params(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return len(query_params)


def is_ip_address(x):
  ip =  bool(re.match(r'^(25[0-5]|2[0-4]\d|1\d{2}|\d{1,2})\.(25[0-5]|2[0-4]\d|1\d{2}|\d{1,2})\.(25[0-5]|2[0-4]\d|1\d{2}|\d{1,2})\.(25[0-5]|2[0-4]\d|1\d{2}|\d{1,2})$',x))
  if ip:
    return 1
  else:
    return 0


def has_a(domain):
    special_chars = ['@','_']
    for s in special_chars:
      if s in domain:
        return 1
    else:
        return 0
    

def domain_length(domain):
   return len(str(domain))

def has_numbers(domain):
  result = bool(re.search(r'\d',domain))
  if result:
     return 1
  else:
      return 0
  
def is_file_extension(url):
    extension = {'.exe','.php','.js','.dll','.html'}
    return int(any( url.endswith(e) for e in extension))


def number_of_dots(url):
    return url.count('.')


def count_subdomains(url):
    return len(url.split('.')) - 2


from collections import Counter
from scipy.stats import entropy

def calculate_entropy_url(url):
    # Count the frequency of each character
   freq = Counter(url)
   total_length = len(url)

    # Convert frequencies to probabilities
   probabilities = [count / total_length for count in freq.values()]

    # Calculate entropy using scipy
   return entropy(probabilities, base=2)


def suspicious_keywords(url):
    # List of suspicious keywords
    suspicious_keyword = [
    'secure', 'account', 'login', 'verify', 'update', 'password',
    'urgent', 'confirm', 'warning', 'alert', 'bank', 'payment','paypal'
    'activate', 'suspend', 'locked', 'fraud', 'refund']
    
    url = url.lower()
    
    for keyword in suspicious_keyword:
        if keyword in url:
            return 1  
    
    return 0


def main(url):
    domain = domain_extractor(url)
    all_data = [url_length(url), is_ip_address(domain), has_a(domain), has_numbers(domain),
       is_file_extension(url), suspicious_keywords(url), count_subdomains(url),
       calculate_entropy_url(url),count_query_params(url),domain_length(domain)]
    
    df = pd.DataFrame(all_data)
    return df



## Fuction to Manage Url and Domain Input ##

import re
from urllib.parse import urlparse

def validate_and_convert(user_input):
    """
    Validates if the input is a domain or a URL and converts domains to URLs.
    
    Args:
        user_input (str): The user-provided input (domain or URL).
    
    Returns:
        str: A valid URL if the input is a domain or already a URL.
    """
    # Regular expression to match a domain (e.g., example.com, sub.example.co.uk)
    domain_pattern = re.compile(
        r'^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$'
    )
    
    # Check if the input is already a valid URL
    parsed_url = urlparse(user_input)
    if parsed_url.scheme in ('http', 'https') and parsed_url.netloc:
        return user_input  # Input is already a valid URL
    
    # Check if the input is a domain
    if domain_pattern.match(user_input):
        # Convert domain to URL with https://
        return f"https://{user_input}"
    
    # If neither a domain nor a URL, raise an error or return None
    raise ValueError("Invalid input: Not a valid domain or URL.")



