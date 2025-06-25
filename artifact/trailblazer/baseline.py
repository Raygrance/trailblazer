import psycopg2
import constants
import sys
import requests
import time

def fetch_requests(host):
    conn = psycopg2.connect(database=constants.DB_NAME, host=constants.DB_HOST, user=constants.DB_USER, password=constants.DB_PASS, port=constants.DB_PORT)
    cursor = conn.cursor()
        
    cursor.execute(f"SELECT * FROM requests WHERE host='{host}';")
    rows = cursor.fetchall()

    requests = []

    for row in rows:
        r_id, r_host, r_url, r_method, r_query, r_req, r_res, r_code, _ = row
        
        requests.append(row)

    # filename = 'strapi_data.csv'
    # import csv
    # # Writing to a CSV file
    # with open(filename, 'w', newline='') as file:
    #     writer = csv.writer(file)
        
    #     # Writing the data rows
    #     writer.writerows(rows)
        
    return requests


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 baseline.py <host> [host_to_send]")
        exit(1)

    host = sys.argv[1]
    host_to_send = sys.argv[2] if len(sys.argv) == 3 else host
    reqs = fetch_requests(host)

    t0 = time.time()

    for request in reqs:
        r_id, r_host, r_url, r_method, r_query, r_req, r_res, r_code, _ = request
        url = f"http://{host_to_send}{r_url}{r_query}"
        #print(f"Sending request to {url}")
        try:
            response = requests.request(r_method, url, data=r_req)
        except:
            print(f"Failed to send request to {url}")
            continue
        #print(f"Response: {response.text}")
        #print(f"Status code: {response.status_code}")
        #print(f"Expected status code: {r_code}")
    
    t1 = time.time()
    print(f"Finished in {t1 - t0} seconds")

