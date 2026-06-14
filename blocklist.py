"""
blocklist.py — find which inbox messages match blocklist.

The list of blocked domains lives in data/blocklist.txt (one per line).
This file loads that list and finds matching messages. It does NOT move
or delete anything yet — that's the safe "dry run" stage.
"""

import os 
import email 

from scanner import domain_of # reuse the same domain extractor

def load_blocklist(path="data/blocklist.txt"):
    """
    Read blocked domains from the text file into a set.
    Skips blank lines and comment lines (starting with #).
    A set makes 'is this domain blocked?' checks instant.
    """
    if not os.path.exists(path):
        print(f"No blocklist file found at {path}. Create it and add domains.")
        return set()
    
    blocked = set()
    with open(path) as f:
        for line in f:
            line = line.strip().lower()
            if line and not line.startswith("#"):
                blocked.add(line)
    return blocked

def find_blocked(mail, blocked_domains, batch_size=500):
    """
    Scan the inbox and collect the message IDs whose sender domain 
    is on the blocklist. Returns a dict: domain -> list of message IDs.
    """
    mail.select("INBOX")
    status, data = mail.search(None, "ALL")
    ids = data[0].split()
    total = len(ids)

    matches = {} # domain -> [messsage ids]

    for start in range(0, total, batch_size):
        batch = ids[start:start + batch_size]
        id_set = b",".join(batch)
        status, fetched = mail.fetch(id_set, "(BODY.PEEK[HEADER.FIELDS (FROM)])")

        for item in fetched:
            if isinstance(item, tuple):
                # item[0] holds the message's ID at the start, like
                # b'1234 (BODY[HEADER.FIELDS (FROM)] {38}'. Grab that ID.
                msg_id = item[0].split()[0]

                # item[1] is the raw header; parse out the From domain
                msg = email.message_from_bytes(item[1])
                domain = domain_of(msg['From']) 

                if domain in blocked_domains:
                    # setdefault: get this domain's list or make a new
                    # empty one, then add message ID to it
                    matches.setdefault(domain, []).append(msg_id)
        
        done = min(start + batch_size, total)
        print(f" {done}/{total} checked")

    return  matches


def report(matches):
    """"Dry-run output: show me what WOULD be removed, without actually removing anything."""
    if not matches:
        print("\nNo blocked senders found in the inbox.")
        return 

    total = sum(len(ids) for ids in matches.values())
    print(f"\nDRY RUN - these would be removed: ({total} messages):\n")

    # Sort domains by how many messages each has, biggest first
    for domain, ids in sorted(matches.items(), key=lambda kv: len(kv[1]), reverse=True):
        print(f" {len(ids):>6} {domain}")
 

