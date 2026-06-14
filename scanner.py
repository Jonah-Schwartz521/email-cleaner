import email
from collections import Counter
from email.utils import parseaddr
 
 
def domain_of(from_header):
    """
    Pull the domain out of a 'From' header.
 
    A From header looks like:  "Target Deals" <deals@e.target.com>
    parseaddr() splits that into a name and the bare address, then we
    take the part after the @ as the domain. Falls back to "(unknown)"
    if the header is missing or malformed.
    """
    name, address = parseaddr(from_header)
    address = address.lower()
    if "@" in address:
        return address.split("@")[-1]
    return "(unknown)"
 
 
def scan_senders(mail, batch_size=500):
    """
    Scan the whole inbox and count messages per sender domain.
 
    'mail' is an already-connected IMAP connection (from client.connect).
    Returns a Counter mapping domain -> number of messages.
    """
    mail.select("INBOX")
 
    # Get the IDs of every message in the inbox.
    status, data = mail.search(None, "ALL")
    ids = data[0].split()
    total = len(ids)
 
    if total == 0:
        print("No messages found in the inbox.")
        return Counter()
 
    print(f"Scanning {total} messages (in batches of {batch_size})...")
    counts = Counter()
 
    # Work through the IDs in chunks. Fetching 500 headers in one request
    # is far faster than 500 separate requests. range(0, total, batch_size)
    # gives us the starting index of each chunk: 0, 500, 1000, ...
    for start in range(0, total, batch_size):
        batch = ids[start:start + batch_size]
 
        # Join this batch's IDs into one comma-separated set like b"1,2,3".
        id_set = b",".join(batch)
 
        # BODY.PEEK[HEADER.FIELDS (FROM)] = "give me only the From header,
        # and don't mark anything as read."
        status, fetched = mail.fetch(id_set, "(BODY.PEEK[HEADER.FIELDS (FROM)])")
 
        # The fetch response is a list. Each message we want comes back as
        # a tuple; there are also stray bytes items between them we skip.
        for item in fetched:
            if isinstance(item, tuple):
                # item[1] is the raw header bytes. Let the email module
                # parse it, then read the From value out.
                msg = email.message_from_bytes(item[1])
                from_header = msg.get("From", "")
                counts[domain_of(from_header)] += 1
 
        # Show progress so it doesn't look frozen on a big inbox.
        done = min(start + batch_size, total)
        print(f"  {done}/{total} scanned")
 
    return counts
 
def print_top_senders(counts, top=25):
    """Print the biggest sendes as a ranked table"""
    print(f"\nTop {top} senders by volume:\n")
    print(f"{'COUNT':>7}  DOMAIN")
    print(f"{'-----':>7}  ------")


    # most_common(top) returns the highest-count domains, already sorted
    for domain, count in counts.most_common(top):
        # :>7 right-aligns the number in a 7-wide column so it lines up.
        print(f"{count:>7}  {domain}")

    print(f"\n({len(counts)} distinct sender domains in total.)")
