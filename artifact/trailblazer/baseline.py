import psycopg2
import constants
import argparse
import requests
import time

def fetch_requests(host):
    conn = psycopg2.connect(
        database=constants.DB_NAME, 
        host=constants.DB_HOST, 
        user=constants.DB_USER, 
        password=constants.DB_PASS, 
        port=constants.DB_PORT
    )
    cursor = conn.cursor()
        
    cursor.execute(f"SELECT * FROM requests WHERE host='{host}';")
    rows = cursor.fetchall()

    return rows


def parse_headers(header_list):
    """
    Convert ['Key: Value', 'A: B'] into {'Key': 'Value', 'A': 'B'}
    """
    headers = {}
    if not header_list:
        return headers
    
    for h in header_list:
        if ':' not in h:
            raise ValueError(f"Invalid header format: {h}")
        key, value = h.split(':', 1)
        headers[key.strip()] = value.strip()

    return headers


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Relay all captured requests")
    parser.add_argument("host", help="Host to fetch requests from DB")
    parser.add_argument("host_to_send", nargs="?", help="Host to send requests to (default: host)")
    parser.add_argument(
        "-H", "--header",
        action="append",
        help='Optional HTTP header, e.g. -H "Authorization: Bearer xxx"'
    )

    args = parser.parse_args()

    host = args.host
    host_to_send = args.host_to_send if args.host_to_send else host
    headers = parse_headers(args.header)

    reqs = fetch_requests(host)

    t0 = time.time()

    for request in reqs:
        r_id, r_host, r_url, r_method, r_query, r_req, r_res, r_code, _ = request
        url = f"http://{host_to_send}{r_url}{r_query}"

        try:
            response = requests.request(
                r_method, 
                url, 
                data=r_req,
                headers=headers if headers else None
            )
        except Exception as e:
            print(f"Failed to send request to {url}: {e}")
            continue
    
    t1 = time.time()
    print(f"Finished in {t1 - t0} seconds")