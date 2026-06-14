"""
main.py - the entry point. Logs into email account, lists the folders, and counts the inbox. 
"""

import imaplib 

from config import EMAIL_ADDRESS, EMAIL_PASSWORD
from client import connect 

def main():
    # Make sure the credentials actually loaded from .env
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("Missing EMAIL_ADDRESS or EMAIL_PASSWORD in your .env file")
        return
    
    # Try to connect 
    try:
        mail = connect(EMAIL_ADDRESS, EMAIL_PASSWORD)
    except imaplib.IMAP4.error as e:
        print(f"    Login Failed: {e}")
        print("    -> Check your app password and that third-party access")
        print("     is enabled on the account.")
        return
    except Exception as e:
        print(f"  Connection error: {e}")
        return
    
    # List the mail folders 
    status, folders = mail.list()
    print(f"\nFound {len(folders)} folders:")
    for f in folders:
        print(" ", f.decode())

    # Count messages in inbox 
    mail.select("INBOX")
    status, data = mail.search(None, "ALL")
    count = len(data[0].split()) if data[0] else 0
    print(f"\nINBOX contains {count} messages.")

    mail.logout()
    print("\nDone - your connection works, Ready to build the scanner next.")


if __name__ == "__main__":
    main()