import random
import string
from reqobj import RequestObject

# with open('spec.pkl', 'rb') as file:
#     ReqObjs = pickle.load(file)


def get_mutation(ReqObj: RequestObject, schema={}, delete=True, invalid_type=True, combine=True):
    
    # chooses a random seed from observed instances to act as baseline mutation payload
    if ReqObj.seed_ids:
        seed = random.choice(ReqObj.seed_ids)
    else:
        seed = None

    random.seed()
    if random.random() < -1:  
        return ReqObj.generate_combine(seed) # return original test instance
    else:
        result = ReqObj.generate_combine(seed)

        # perform schema aware mutations 50% of the time
        if random.random() <= 2:
            mutate_by_schema(result, schema)
        else:
            res = random.random()
            if res <= 0.25:
                delete_random_element(result)
            elif res > 0.25 and res <= 0.5:
                invalid_random_element(result)
            elif res > 0.5 and res <= 0.75:
                swap_random_elements(result)
            else:
                overflow_random_element(result)

        return result 

def get_all_paths(json_obj, parent_path=""):
    """
    Recursively collect all paths in the JSON object.
    Each path corresponds to a leaf node or a subtree.
    """
    paths = []
    
    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            full_path = parent_path + [key] if parent_path else [key]
            paths.append(full_path)
            if isinstance(value, dict):
                # Recursively collect paths from the nested dict
                paths.extend(get_all_paths(value, full_path))
    
    return paths

#############################################################################################################################

def delete_by_path(json_obj, path):
    """
    Delete the element at the specified path in the JSON object.
    """
    keys = path
    current = json_obj
    for key in keys[:-1]:
        current = current[key]  # Navigate to the parent of the node to be deleted
    del current[keys[-1]]  # Delete the targeted node

def delete_random_element(json_obj):
    """
    Randomly delete a leaf node or subtree from the JSON object with equal probability.
    """
    # Get a list of all paths (to both leaf nodes and subtrees)
    all_paths = get_all_paths(json_obj)
    
    if not all_paths:
        return json_obj  # If there are no elements to delete, return the original object
    
    # Randomly choose one path to delete
    path_to_delete = random.choice(all_paths)
    
    # Delete the selected path
    delete_by_path(json_obj, path_to_delete)
    
    return json_obj

#############################################################################################################################

def invalid_by_path(json_obj, path):
    """
    Make the datatype invalid at the specified path in the JSON object.
    """
    keys = path
    current = json_obj
    for key in keys[:-1]:
        current = current[key]  # Navigate to the parent of the node to be deleted
    
    if isinstance(current, dict):
        current[keys[-1]] = random.choice([["random", 1.23, False], "invalid", 65536, 123.0, True, None])
    elif isinstance(current, list):
        current[keys[-1]] = random.choice([{"key1": "value1", "key2": 3.14}, "invalid", 65536, 123.0, True, None])
    elif isinstance(current, str):
        current[keys[-1]] = random.choice([{"key1": "value1", "key2": 3.14}, ["random", 1.23, False], 65536, 123.0, True, None])
    elif isinstance(current, int):
        current[keys[-1]] = random.choice([{"key1": "value1", "key2": 3.14}, ["random", 1.23, False], "invalid", True, None])
    elif isinstance(current, float):
        current[keys[-1]] = random.choice([{"key1": "value1", "key2": 3.14}, ["random", 1.23, False], "invalid", True, None])
    elif isinstance(current, bool):
        current[keys[-1]] = random.choice([{"key1": "value1", "key2": 3.14}, ["random", 1.23, False], "invalid", 65536, 123.0, None])
    else: # NoneType
        current[keys[-1]] = random.choice([{"key1": "value1", "key2": 3.14}, ["random", 1.23, False], "invalid", 65536, 123.0, True])

def invalid_random_element(json_obj):
    """
    Randomly give a leaf node or subtree invalid datatype from the JSON object with equal probability.
    """
    # Get a list of all paths (to both leaf nodes and subtrees)
    all_paths = get_all_paths(json_obj)
    
    if not all_paths:
        return json_obj  # If there are no elements to delete, return the original object
    
    # Randomly choose one path to delete
    path_to_invalid = random.choice(all_paths)
    
    # Delete the selected path
    invalid_by_path(json_obj, path_to_invalid)
    
    return json_obj

#############################################################################################################################

# Additional Mutation Methods by Ray Zhang

def swap_random_elements(json_obj):
    """
    Randomly swap two leaf nodes from the JSON object with equal probability
    """

    # Get a list of all paths (to both leaf nodes and subtrees)
    all_paths = get_all_paths(json_obj)
    
    if len(all_paths) < 2:
        return json_obj # If there are no elements to swap, return the original object
    
    # randomly choose two paths to swap
    paths_to_swap = random.sample(all_paths, 2)

    # swap the selected paths
    swap_by_path(json_obj, paths_to_swap)

    return json_obj

def swap_by_path(json_obj, paths_to_swap):
    """
    swap the two nodes at the end of the path
    """

    keys1 = paths_to_swap[0]
    keys2 = paths_to_swap[1]
    node1 = json_obj
    node2 = json_obj
    
    for key in keys1[:-1]:
        node1 = node1[key] 
    for key in keys2[:-1]:
        node2 = node2[key]

    # swap two nodes
    tmp = node1[keys1[-1]]
    node1[keys1[-1]] = node2[keys2[-1]]
    node2[keys2[-1]] = tmp

#############################################################################################################################

def overflow_random_element(json_obj):
    """
    Randomly selects a path to apply integer overflow/underflow
    """
    all_paths = get_all_paths(json_obj)

    if not all_paths:
        return json_obj # return original json object if nothing to mutate
    
    # randomly choose a path to overflow
    path_to_overflow = random.choice(all_paths)

    overflow_by_path(json_obj, path_to_overflow)

    return json_obj

def overflow_by_path(json_obj, path_to_overflow):
    """
    mutates ints or floats to very large or very small values
    to trigger integer over/underflow
    """
    keys = path_to_overflow
    current = json_obj
    for key in keys[:-1]:
        current = current[key]

    if isinstance(current, int) or isinstance(current, float):
        current[keys[-1]] = random.choice([2**31, 2**63, 10**100, -2**31, -2**63, -10**100]) # append numeric values to common numerical limits

#############################################################################################################################

def mutate_by_schema(json_obj, schema):
    """
    traverses through the given schema for the object and
    the payload, mutating primitive types. Recursively
    traverses nested objects/arrays, generates missing data
    """
    schema_type = schema.get("type")

    # surface item is an array, iterate nested items and mutate
    if schema_type == "array":
        item_schema = schema.get("items", {})
        
        # if data type is incorrect, prevent crash by returning
        if not isinstance(json_obj, list):
            return  
        
        # enumerate to save item index for mutation access
        for i, item in enumerate(json_obj):
            item_type = item_schema.get("type")
            if item_type == "object" and isinstance(item, dict):
                mutate_by_schema(item, item_schema)
            elif item_type == "array" and isinstance(item, list):
                mutate_array_recursive(item, item_schema)
            elif item_type:
                mutate_by_type(json_obj, i, item_type)

    # surface item is an object, recurse through nested items and mutate
    if schema_type == "object":
        properties = schema.get("properties", {})
        
        # if data type is incorrect, prevent crash  by returning
        if not isinstance(json_obj, dict):
            return  

        for key, object_schema in properties.items():
            expected_type = object_schema.get("type")

            # recurse nested object
            if expected_type == "object" and isinstance(json_obj.get(key), dict):
                mutate_by_schema(json_obj[key], object_schema)
            
            # iterate through nested array and mutate recursively
            elif expected_type == "array" and isinstance(json_obj.get(key), list):
                item_schema = object_schema.get("items", {})
                
                for i, item in enumerate(json_obj[key]):
                    item_type = item_schema.get("type")
                    if item_type == "object" and isinstance(item, dict):
                        mutate_by_schema(item, item_schema)
                    elif item_type == "array" and isinstance(item, list):
                        mutate_array_recursive(item, item_schema)
                    elif item_type:
                        mutate_by_type(json_obj[key], i, item_type)
            
            # mutate primitive type
            elif expected_type:
                mutate_by_type(json_obj, key, expected_type)


def mutate_array_recursive(arr, schema):
    """
    helper function to iterate through nested array items and mutate
    """
    
    # defensive check of item type
    if not isinstance(arr, list):
        return
    item_schema = schema.get("items", {})
    item_type = item_schema.get("type")

    # enumerate to get index for mutation access
    for i, item in enumerate(arr):
        if item_type == "object" and isinstance(item, dict):
            mutate_by_schema(item, item_schema)
        elif item_type == "array" and isinstance(item, list):
            mutate_array_recursive(item, item_schema)
        elif item_type:
            mutate_by_type(arr, i, item_type)


def mutate_by_type(json_obj, key, expected_type):
    """
    mutate a value depending on its type
    """
    if expected_type == "string":
        choices = ["", "\n", "\t", "\"", generate_random_string, generate_random_string, generate_random_string,
                   random.randint(-1000, 1000), random.uniform(-1000, 1000), {"key1": "value1", "key2": 3.14}, True, None]
    elif expected_type == "integer":
        choices = [0, -1, 1, random.randint(-1000000, 1000000), random.randint(-1000000, 1000000),
                   random.randint(-1000000, 1000000), 2**31 - 1, -2**31, random.uniform(-100, 100), generate_random_string, None, True, {"key1": "value1", "key2": 3.14}]
    elif expected_type == "number":
        choices = [0.0, -1.0, 1.0, random.uniform(-1000, 1000), random.uniform(-1000, 1000),
                   random.uniform(-1000, 1000), random.randint(-1000, 1000), generate_random_string, None, True, {"key1": "value1", "key2": 3.14}]
    elif expected_type == "boolean":
        choices = [True, False, None, random.randint(-1000, 1000), random.uniform(-1000, 1000),
                   generate_random_string, {"key1": "value1", "key2": 3.14}, [True, False, True, False]]
    else:
        choices = ["", generate_random_string, random.randint(-1000, 1000), random.uniform(-1000, 1000),
                   {"key1": "value1", "key2": 3.14}, True, False, None]

    # randomly select from valid choices given data type
    val = random.choice(choices)
    # generate random string
    if callable(val):
        val = val()
    json_obj[key] = val

def generate_random_string():
    """
    generates a random string of random length
    """
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(random.randint(1, 100)))

######################################################################################################################################################

if __name__ == "__main__":
    obj = {
    "name": "John",
    "age": 30,
    "address": {
        "street": "123 Main St",
        "city": "New York",
        "postal_code": {
            "zip": "10001",
            "extension": "1234"
        }
    },
    "phone": "555-5555"
}
    print(get_all_paths(obj))
    print(delete_random_element(obj))