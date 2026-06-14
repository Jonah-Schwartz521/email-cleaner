""""
config.py - settings and credentials. 
Everything that might change (which servers to use, login details) 
lives here, separate from the logic. Loads email address and password 
from .env file.
"""

import os 
from dotenv import load_dotenv

# Read EMAIL_ADDRESS and EMAIL_PASSWORD from .env file 
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# IMAP server addresses per provider
# To support a new provider later, just add a line here
IMAP_SERVERS = {
    "comcast.net": "imap.comcast.net",
    "gmail.com": "imap.gmail.com",
}

# Secure IMAP port (SSL)
IMAP_PORT = 993

def get_server(email_address):
    """"Pick the right IMAP server based on the part after the @."""
    domain = email_address.split("@")[-1].lower()
    if domain not in IMAP_SERVERS:
        raise ValueError(f"No IMAP server configured for '{domain}'")
    return IMAP_SERVERS[domain]
   