"""
main.py - the entry point. Logs into email account, lists the folders, and counts the inbox. 
"""

import imaplib 

from config import EMAIL_ADDRESS, EMAIL_PASSWORD
from client import connect 
from scanner import scan_senders, print_top_senders
from blocklist import load_blocklist, find_blocked, report


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
    
    # Simple menu: pick what to do with the connection
    print("\nWhat do you want to do?")
    print("  1. Scan and rank senders")
    print("  2. Dry run the blocklist (see what would be removed)")
    choice = input("Enter 1 or 2: ").strip()    

    if choice == "1":
        counts = scan_senders(mail)
        print_top_senders(counts, top=25)
    elif choice == "2":
        blocked = load_blocklist()
        matches = find_blocked(mail, blocked)
        report(matches)
    else:
        print("No valid choice made.")

    mail.logout()
    print("\nDone - your connection works, Ready to build the scanner next.")


if __name__ == "__main__":
    main()