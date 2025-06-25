from reqobj import RequestObject
import path
import psycopg2
import json
import model
import pickle
import constants


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

def process(requests, rules):
    result = {}
    for request in requests:
        method = request[3]
        rule = path.url_to_rule(request[2])
        if (rule, method) not in rules:
            result[(rule, method)] = RequestObject()
        result[(rule, method)].parse(json.loads(request[5]))
    return result

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

def rule_to_parameters(rule):
    result = []
    i = 1
    for segment in rule:
        if type(segment) == int:
            parameter = model.OpenAPI_Parameter("id" + str(i), "path", True, model.OpenAPI_Schema("integer" if segment == 1 else "string"))
            result.append(parameter)
            i += 1
    return result

def to_spec(base_url, requests, rules, examples=0, mutants=0):
    ReqObjs = {}
    for request in requests:
        method = request[3].lower()
        rule = path.url_to_rule(request[2])
        if (rule, method) not in ReqObjs:
            ReqObjs[(rule, method)] = [RequestObject(), set()]
            #print(json.loads(request[5]))
        obj = json.loads(request[5])
        ReqObjs[(rule, method)][0].parse(obj)
        ReqObjs[(rule, method)][0].add_example(obj)
        ReqObjs[(rule, method)][1].add(request[7])

    with open('spec.pkl', 'wb') as file:
        pickle.dump(ReqObjs, file)

    result = model.OpenAPISpec(base_url)
    paths = model.OpenAPI_Paths()
    result.set_paths(paths)

    for rule, method in ReqObjs:
        rule_str = rule_to_path(rule)
        if rule_str not in paths:
            paths.add_pathItem(rule_str, model.OpenAPI_PathItem())
            for parameter in rule_to_parameters(rule):
                paths[rule_str].add_parameter(parameter)
        if method not in paths[rule_str].methods:
            paths[rule_str].methods[method] = model.OpenAPI_Operation()
        if ReqObjs[(rule, method)][0]:
            paths[rule_str].methods[method].set_requestBody(ReqObjs[(rule, method)][0].to_requestbody(examples=examples, mutants=mutants))
        for response_code in ReqObjs[(rule, method)][1]:
            paths[rule_str].methods[method].add_response(response_code, {"description": "Auto generated response object"})
    
    return result

def print_model(model):
    for rule in model:
        print(rule)
        print(json.dumps(model[rule].generate()))
        print(json.dumps(model[rule].generate()))
        print()

if __name__ == "__main__":
    hosts = path.step1()
    print()
    print("Select a web app from the above list: ")
    s = int(input()) - 1

    rules = path.step2(hosts[s])

    # path.print_rules(rules)

    print("====================================")

    requests = fetch_requests(hosts[s])

    #model = process(requests, rules)
    #print_model(model)

    spec = to_spec(hosts[s], requests, rules, examples=5, mutants=0)

    temp = spec.to_dict()

    #print(temp)

    f = open("to_spec_test.json", "w")
    json.dump(temp, f, indent=4)
    f.close()
