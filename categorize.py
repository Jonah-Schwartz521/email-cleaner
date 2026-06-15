"""
categorize.py — sort kept mail into folders by sender domain.

Reads domain -> folder rules from data/categories.txt, finds matching
messages, and (after a dry run + confirmation) moves them in batches.
Reuses the same domain logic as the scanner.
"""

import os
import email

from scanner import domain_of


def load_categories(path="data/categories.txt"):
    """
    Read 'domain = Folder' rules into a dict: {domain: folder}.
    Skips blanks and comment lines.
    """
    rules = {}
    if not os.path.exists(path):
        print(f"No categories file found at {path}.")
        return rules

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            domain, folder = line.split("=", 1)
            rules[domain.strip().lower()] = folder.strip()
    return rules


def find_categorized(mail, rules, batch_size=500):
    """
    Scan the inbox; for each message whose domain is in the rules,
    record it under its target folder.
    Returns: {folder: [message ids]}
    """
    mail.select("INBOX")
    status, data = mail.search(None, "ALL")
    ids = data[0].split()
    total = len(ids)

    matches = {}  # folder -> [ids]

    for start in range(0, total, batch_size):
        batch = ids[start:start + batch_size]
        id_set = b",".join(batch)
        status, fetched = mail.fetch(id_set, "(BODY.PEEK[HEADER.FIELDS (FROM)])")

        for item in fetched:
            if isinstance(item, tuple):
                msg_id = item[0].split()[0]
                msg = email.message_from_bytes(item[1])
                domain = domain_of(msg.get("From", ""))
                if domain in rules:
                    folder = rules[domain]
                    matches.setdefault(folder, []).append(msg_id)

        done = min(start + batch_size, total)
        print(f"  {done}/{total} checked")

    return matches


def report(matches):
    """Dry run: show how many would go to each folder."""
    if not matches:
        print("\nNothing matched your category rules.")
        return
    total = sum(len(ids) for ids in matches.values())
    print(f"\nDRY RUN — these would be sorted ({total} messages):\n")
    for folder, ids in sorted(matches.items(), key=lambda kv: len(kv[1]), reverse=True):
        print(f"  {len(ids):>6}  -> {folder}")


def sort_mail(mail, matches):
    """Move each group of messages into its folder, in batches. Asks first."""
    total = sum(len(ids) for ids in matches.values())
    if total == 0:
        print("Nothing to sort.")
        return

    confirm = input(f"\nSort {total} messages into folders? Type yes: ")
    if confirm.strip().lower() != "yes":
        print("Cancelled — nothing moved.")
        return

    mail.select("INBOX")
    moved = 0
    for folder, ids in matches.items():
        mail.create(folder)  # make the folder if needed (ok if it exists)
        batch_size = 200
        for start in range(0, len(ids), batch_size):
            batch = [mid for mid in ids[start:start + batch_size] if mid]
            if not batch:
                continue
            id_set = b",".join(batch)
            mail.copy(id_set, folder)
            mail.store(id_set, "+FLAGS", "\\Deleted")
            moved += len(batch)
            print(f"  moved {moved}/{total}")

    mail.expunge()
    print(f"Sorted {moved} messages into folders.")