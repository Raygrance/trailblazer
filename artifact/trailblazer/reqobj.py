
import random
import string

class RequestObject:
    def __init__(self):
        self.type = None
        self.values = [None]
        self.subtype = None
        self.required = True
        self.occur_in_sample = 1
        self.total_sample = 1
        self.examples = []
        self.seed_ids = [] # list of all ids seen in collected data
        self.seed_value_pairs = [] # list of seed ids with its associated data
    
    def __bool__(self):
        return self.type != None
    
    def initial_parse(self, object, seed_id=None):
        if type(object) == dict:
            self.type = dict
            self.values = {}
            for k in object:
                self.values[k] = RequestObject()
                self.values[k].parse(object[k], seed_id)
            self.seed_ids.append(seed_id)
            self.seed_value_pairs.append((object, seed_id))
        elif type(object) == list:
            self.type = list
            self.values = RequestObject()
            for i in object:
                self.values.parse(i, seed_id)
            self.seed_ids.append(seed_id)
        elif type(object) == bool:
            self.type = bool
            self.values = set()
            self.values.add(object)
            self.seed_ids.append(seed_id)
            self.seed_value_pairs.append((object, seed_id))
        elif type(object) == int:
            self.type = int
            self.values = set()
            self.values.add(object)
            self.seed_ids.append(seed_id)
            self.seed_value_pairs.append((object, seed_id))
        elif type(object) == float:
            self.type = float
            self.values = set()
            self.values.add(object)
            self.seed_ids.append(seed_id)
            self.seed_value_pairs.append((object, seed_id))
        elif type(object) == str:
            self.type = str
            self.values = set()
            self.values.add(object)
            self.seed_ids.append(seed_id)
            self.seed_value_pairs.append((object, seed_id))
        else:
            self.type = None
            self.values = [None]


    def add_example(self, object):
        self.examples.append(object)
        # if len(self.examples) > 1:
        #    1/0

    # generates ReqObj
    def parse(self, object, seed_id=None):
        if self.type == None:
            self.initial_parse(object, seed_id)
            return

        if type(object) != self.type:
            if type(object) is not type(None):
                print("Warning: type mismatch in RequestObject.parse()", self.type, type(object))
            return
        
        if type(object) == dict:
            for k in self.values:
                if k not in object:
                    self.values[k].required = False
                    self.values[k].total_sample += 1
            for k in object:
                if k not in self.values:
                    self.values[k] = RequestObject()
                    self.values[k].total_sample = 10
                    self.values[k].parse(object[k], seed_id)
                else:
                    self.values[k].occur_in_sample += 1
                    self.values[k].total_sample += 1
                    self.values[k].parse(object[k], seed_id)
            self.seed_ids.append(seed_id)
            self.seed_value_pairs.append((object, seed_id))
        elif type(object) == list:
            for i in object:
                self.values.parse(i, seed_id)
            self.seed_ids.append(seed_id)
        elif type(object) == bool:
            self.occur_in_sample += 1
            self.total_sample += 1
            self.values.add(object)
            self.seed_ids.append(seed_id)
            self.seed_value_pairs.append((object, seed_id))
        elif type(object) == int:
            self.occur_in_sample += 1
            self.total_sample += 1
            self.values.add(object)
            self.seed_ids.append(seed_id)
            self.seed_value_pairs.append((object, seed_id))
        elif type(object) == float:
            self.occur_in_sample += 1
            self.total_sample += 1
            self.values.add(object)
            self.seed_ids.append(seed_id)
            self.seed_value_pairs.append((object, seed_id))
        elif type(object) == str:
            self.occur_in_sample += 1
            self.total_sample += 1
            self.values.add(object)
            self.seed_ids.append(seed_id)
            self.seed_value_pairs.append((object, seed_id))
        else:
            self.type = None
            self.values = [None]
    
    #def add_sample(self, value):
    #    self.values.append(value)

    def to_requestbody(self, root=True, examples=0):
        if root:
            result = {}
            result["content"] = {"application/json": {"schema": {}}}
            result["content"]["application/json"]["schema"] = self.to_requestbody(False)
            if examples > 0:
                result["content"]["application/json"]["examples"] = {}
                if examples >= len(self.examples):
                    for i in range(len(self.examples)):
                        result["content"]["application/json"]["examples"]["example"+str(i)] = {"value": self.examples[i]}
                else:
                    temp = random.sample(self.examples, examples)
                    for i in range(len(temp)):
                        result["content"]["application/json"]["examples"]["example"+str(i)] = {"value": temp[i]}
            return result
        
        if self.type == dict:
            result = {"type": "object", "properties": {}}
            for k in self.values:
                result["properties"][k] = self.values[k].to_requestbody(False)
            return result
        elif self.type == list:
            result = {"type": "array", "items": {}}
            result["items"] = self.values.to_requestbody(False)
            return result
        elif self.type == bool:
            return {"type": "boolean"}
        elif self.type == int:
            return {"type": "integer"}
        elif self.type == float:
            return {"type": "number"}
        elif self.type == str:
            return {"type": "string"}
        else:
            return {}

    def generate(self, seed_id=None):
        return self.generate_combine(seed_id)

    def generate_combine(self, seed_id=None):
        
        if self.type == dict:
            result = {}
            # list of observed values with the same seed id
            seed_values = [obj for obj, sid in self.seed_value_pairs if sid == seed_id]

            keys = []
            seen = set()
            for obj in seed_values:
                for k in obj.keys():
                    if k not in seen:
                        seen.add(k)
                        keys.append(k)

            for k in keys:
                if k in self.values:  # Only if we have seen this key in the schema
                    # removed random chance to omit a value
                    # if random.random() < self.values[k].occur_in_sample / self.values[k].total_sample:
                    result[k] = self.values[k].generate(seed_id)
            return result
        elif self.type == list:
            result = []
            result.append(self.values.generate(seed_id))
            return result
        else:
            seed_values = [value for value, sid in self.seed_value_pairs if sid == seed_id]
            if not seed_values:
                return random.choice(tuple(self.values))
            return random.choice(tuple(seed_values))
    
    def generate_delete(self, delete_rate=0.1):
        if self.type == dict:
            result = {}
            for k in self.values:
                if random.random() < self.values[k].occur_in_sample / self.values[k].total_sample:
                    if random.random() < delete_rate:
                        continue
                    result[k] = self.values[k].generate_delete(delete_rate=1-(1-delete_rate)**2)
            return result
        elif self.type == list:
            result = []
            result.append(self.values.generate_delete(delete_rate=1-(1-delete_rate)**2))
            return result
        else:
            return random.choice(tuple(self.values))

    def generate_invalid(self, invalid_rate=0.2):
        if self.type == dict:
            if random.random() < invalid_rate:
                return ["random", 3.86, False]
            result = {}
            for k in self.values:
                if random.random() < self.values[k].occur_in_sample / self.values[k].total_sample:
                    result[k] = self.values[k].generate_invalid()
            return result
        elif self.type == list:
            if random.random() < invalid_rate:
                if random.random() < 0.5:
                    return "sample string"
                return {"key1": "value1", "key2": 4.93}
            result = []
            result.append(self.values.generate_invalid())
            return result
        else:
            if random.random() < invalid_rate:
                if self.type == str:
                    return random.choice([4294967296, True, 8.599, None])
                elif self.type == int:
                    return random.choice(["sample string", True, 4.206, None])
                elif self.type == float:
                    return random.choice([32768, True, "sample string", None])
                elif self.type == bool:
                    return random.choice(["sample string", 123456, 9.806, None])
                return -1
            return random.choice(tuple(self.values))


if __name__ == "__main__":
    #example = {"a": 5, "b": [7,8,9,10,11,45,89,130], "c": [{"ca": 123, "cb": "aaa"}, {"ca": 789, "cb": "idoarl", "cc": 0}]}

    ro = RequestObject()
    #ro.parse(example)

    for i in range(50):
        example = {
                "a": random.randint(1,50), 
                "b": list(set([random.randint(10,2000) for _ in range(random.randint(1,10))])), 
                "c": [
                        {
                            "ca": random.randint(1073741824, 4294967296), 
                            "cb": ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(6,20)))
                        }, 
                        {
                            "ca": random.randint(1073741824, 4294967296), 
                            "cb": ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(6,20))), 
                            "cc": 0
                        }]
                    }
        ro.parse(example, i)

    for i in range(10):
        print(ro.generate())
