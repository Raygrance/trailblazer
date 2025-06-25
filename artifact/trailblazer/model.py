
# REF: https://swagger.io/specification/v3/

class OpenAPISpec():
    def __init__(self, basePath="/"):
        self.openapi = "3.0.0"
        self.servers = [{"url": "http://" + basePath}]
        self.info = {"title": "example", "version": "1.0.0"}
        self.paths = {}
    
    def set_basePath(self, basePath):
        self.servers = [{"url": basePath}]
        
    def set_paths(self, paths):
        self.paths = paths
    
    def to_dict(self):
        result = {}
        result["openapi"] = self.openapi
        result["servers"] = self.servers
        #result["resourcePath"] = self.resourcePath
        result["info"] = self.info
        #result["produces"] = self.produces
        result["paths"] = self.paths.to_dict()  # {k: self.paths[k].to_dict() for k in self.paths}
        return result
        

class OpenAPI_Paths():
    def __init__(self):
        self.paths = {}
    
    def __contains__(self, path):
        return path in self.paths

    def __getitem__(self, path):
        return self.paths[path]
        
    def add_pathItem(self, path, PathItem):
        self.paths[path] = PathItem
    
    def to_dict(self):
        return {k: self.paths[k].to_dict() for k in self.paths}
    

class OpenAPI_PathItem():
    def __init__(self):
        self.methods = {}  # get / post / put / delete / patch / head / options / trace
        self.parameters = []
    
    # TODO
    def add_parameter(self, parameter):
        self.parameters.append(parameter)
    
    def to_dict(self):
        result = {}
        if "get" in self.methods:
            result["get"] = self.methods["get"].to_dict()
        if "post" in self.methods:
            result["post"] = self.methods["post"].to_dict()
        if "put" in self.methods:
            result["put"] = self.methods["put"].to_dict()
        if "delete" in self.methods:
            result["delete"] = self.methods["delete"].to_dict()
        if "patch" in self.methods:
            result["patch"] = self.methods["patch"].to_dict()
        if "head" in self.methods:
            result["head"] = self.methods["head"].to_dict()
        if "options" in self.methods:
            result["options"] = self.methods["options"].to_dict()
        if "trace" in self.methods:
            result["trace"] = self.methods["trace"].to_dict()
        if self.parameters:
            result["parameters"] = [i.to_dict() for i in self.parameters]
        return result


class OpenAPI_Operation():
    def __init__(self):
        self.parameters = []
        self.requestBody = None
        self.responses = {}
    
    # TODO
    def add_parameter(self, parameter):
        self.parameters.append(parameter)

    def set_requestBody(self, requestBody):
        self.requestBody = requestBody
    
    def add_response(self, code, response):
        self.responses[code] = response
    
    def to_dict(self):
        result = {}
        if self.parameters:
            result["parameters"] = self.parameters
        if self.requestBody:
            result["requestBody"] = self.requestBody
        result["responses"] = self.responses
        return result


class OpenAPI_RequestBody():
    def __init__(self, description=""):
        self.description = description
        self.required = False
        self.content = {}  # media type to request body object
    
    def add_content(self, media_type, schema):
        self.content[media_type] = schema
    
    def to_dict(self):
        result = {}
        result["description"] = self.description
        result["required"] = self.required
        result["content"] = self.content
        return result


class OpenAPI_Responses():
    def __init__(self):
        self.responses = {}
    
    def add_response(self, status_code, response):
        self.responses[status_code] = response
    
    def to_dict(self):
        return self.responses


class OpenAPI_Response():
    def __init__(self, description=""):
        self.description = description
        self.content = {}  # media type to response body object
    
    def add_content(self, media_type, schema):
        self.content[media_type] = schema
    
    def to_dict(self):
        result = {}
        result["description"] = self.description
        result["content"] = self.content
        return result
        

class OpenAPI_Schema():
    def __init__(self, type="object"):
        self.type = type
        self.required = []
        self.properties = {}
    
    def add_property(self, name, type, format=None, additional=None, listobject=None):
        self.properties[name] = {"type": type}
        if format:
            self.properties[name]["format"] = format
        if additional:
            self.properties[name]["additionalProperties"] = additional
        if listobject:
            self.properties[name]["items"] = listobject
    
    # TODO
    def set_required(self, key, required):
        if key in self.required:
            if not required:
                self.required.remove(key)
        else:
            if required:
                self.required.append(key)
        
    def to_dict(self):
        result = {}
        result["type"] = self.type
        if self.required:
            result["required"] = self.required
        if self.properties:
            result["properties"] = self.properties
        return result

        
class OpenAPI_Parameter():
    def __init__(self, name, in_, required=False, schema=None):
        self.name = name
        self.in_ = in_
        self.required = required
        if in_ == "path":
            self.required = True
        self.schema = schema
    
    def to_dict(self):
        result = {}
        result["name"] = self.name
        result["in"] = self.in_
        if self.required:
            result["required"] = self.required
        result["schema"] = self.schema.to_dict()
        return result
    