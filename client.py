"""
client.py - talking to the mail server. 
"""

import imaplib
from config import get_server, IMAP_PORT 

def connect(email_address, password):
    """Open a secure IMAP connection and log in. Returns the connection"""
    server = get_server(email_address)
    print(f"Connecting to {server} as {email_address} ...")
    mail = imaplib.IMAP4_SSL(server, IMAP_PORT)
    mail.login(email_address, password)
    print(" Login successful.")
    return mail 
