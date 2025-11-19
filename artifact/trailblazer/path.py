from urllib.parse import urlparse
import psycopg2
import re
import random
import math
from collections import Counter

import csv
import constants

# host = "192.168.205.112:1337"

ID_NUMERIC = 1
ID_UUID = 2
ID_MD5 = 3
ID_SHA1 = 4
ID_SHA256 = 5
ID_HEX = 6
ID_HASH = 7
ID_STRING = 8  # for other strings identified as ID (not following above form, but have high entropy)
SHANNON_ENTROPY_THRESHOLD = 3.5 # threshold to identify high-entropy strings (as dynamic IDs)

# Define regex patterns for UUIDs and common hashes
uuid_pattern = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
md5_pattern = re.compile(r"[0-9a-fA-F]{32}")
sha1_pattern = re.compile(r"[0-9a-fA-F]{40}")
sha256_pattern = re.compile(r"[0-9a-fA-F]{64}")
hex_pattern = re.compile(r"[0-9a-fA-F]{16,40}")
hash_pattern = re.compile(r"[0-9a-zA-Z]{16,40}")


def identify_id(token):
    # print(token + "\t", shannon_entropy(token))
    if token.isdigit():  # Heuristic: token is purely numeric
        return ID_NUMERIC
    if uuid_pattern.fullmatch(token):
        return ID_UUID
    elif md5_pattern.fullmatch(token):
        return ID_MD5
    elif sha1_pattern.fullmatch(token):
        return ID_SHA1
    elif sha256_pattern.fullmatch(token):
        return ID_SHA256
    elif hex_pattern.fullmatch(token):
        return ID_HEX
    elif hash_pattern.fullmatch(token):
        return ID_HASH
    elif shannon_entropy(token) > SHANNON_ENTROPY_THRESHOLD:
        return ID_STRING
    return False


def shannon_entropy(s):
    if not s:
        return 0.0
    freq = Counter(s)
    total = len(s)
    return -sum((count / total) * math.log2(count / total) for count in freq.values())

# Convert URL to a rule, e.g. /api/v1/users/123 -> ('api', 'v1', 'users', 1)
def url_to_rule(url):
    segments = url.strip("/").split("/")
    rule = []
    for segment in segments:
        t = identify_id(segment)
        if t:
            rule.append(t)
        else:
            rule.append(segment)
    return tuple(rule)

# Convert rule to a path string, e.g. ('api', 'v1', 'users', 1) -> "/api/v1/users/{id1}"
def rule_to_path(rule):
    result = ""
    i = 1
    for segment in rule:
        if type(segment) == int:
            result += "/{id" + str(i) + "}"
            i += 1
        else:
            result += "/" + segment
    return result

# categorise APIs into endpoints
def categorise(urls):
    url_by_length = {} # by number of segments in path
    for url in urls:
        segments = url.strip("/").split("/")
        if len(segments) not in url_by_length:
            url_by_length[len(segments)] = []
        url_by_length[len(segments)].append(segments)
    
    rules = {}

    for k in url_by_length:
        for url in url_by_length[k]:   # url example: ['api', 'v1', 'users', '1']
            rule = []
            for segment in url:
                t = identify_id(segment)
                if t:
                    rule.append(t)
                else:
                    rule.append(segment)
            rule = tuple(rule)
            if rule in rules:
                rules[rule].append("/" + "/".join(url))
            else:
                rules[rule] = ["/" + "/".join(url)]
    return rules

            
def print_rules(rules):
    for rule in rules:
        print(rule)
        for url in rules[rule]:
            print("\t" + url)
        print()


# retrieve all API traffic for a certain host
def step2(host):
    conn = psycopg2.connect(database=constants.DB_NAME, host=constants.DB_HOST, user=constants.DB_USER, password=constants.DB_PASS, port=constants.DB_PORT)
    cursor = conn.cursor()
        
    cursor.execute(f"SELECT * FROM requests WHERE host='{host}';")
    rows = cursor.fetchall()

    # f = open("rr.txt", "w")

    urls = set()

    requests = []

    filename = 'directus_data.csv'
    f = open(filename, "w", newline='')
    writer = csv.writer(f)

    # Print out the data
    for row in rows:
        r_id, r_host, r_url, r_method, r_query, r_req, r_res, r_code, _ = row
        
        #requests.append(row)
        urls.add(r_url)
        # f.write("https://" + r_host + r_url + r_query + "\n")
        # f.write(r_method + "\n")
        # f.write(r_req + "\n")
        # f.write(r_res + "\n")
        # f.write(str(r_code) + "\n")
        # print("one record processed")
        writer.writerow(row)
    
    f.close()

    #f.close()

    print("Extracted " + str(len(urls)) + " unique API requests")

    rules = categorise(urls)

    #print_rules(rules)
    return rules


def step1():
    conn = psycopg2.connect(database=constants.DB_NAME, host=constants.DB_HOST, user=constants.DB_USER, password=constants.DB_PASS, port=constants.DB_PORT)
    cursor = conn.cursor()
        
    cursor.execute(f"SELECT DISTINCT host FROM requests;")
    rows = cursor.fetchall()
    

    result = []
    for row in rows:
        result.append(row[0])
    
    result.sort()
    i = 0
    for r in result:
        i += 1
        print(str(i) + "\t" + r)
    
    return result


if __name__ == "__main__":
    hosts = step1()
    print()
    print("Select a web app from the above list: ")
    s = int(input()) - 1

    rules = step2(hosts[s])
    print_rules(rules)
    print("Extracted all API requests for " + hosts[s])

    # os.chdir(os.getcwd())
    # os.system("java -jar APIDiscoverer.jar")
    # print()