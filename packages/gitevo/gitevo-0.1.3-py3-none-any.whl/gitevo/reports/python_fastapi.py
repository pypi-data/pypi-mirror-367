from gitevo import GitEvo, ParsedCommit


extension = '.py'
    
def metrics(evo: GitEvo):

    @evo.metric('Number of endpoints', show_version_chart=False)
    def endpoints(commit: ParsedCommit):
        fastapi = FastAPICommit(commit)
        return len(fastapi.endpoints())

    @evo.metric('Endpoints: mean LOC', show_version_chart=False)
    def mean_parameters(commit: ParsedCommit):
        fastapi = FastAPICommit(commit)
        
        endpoints = fastapi.endpoints()
        number_of_endpoints = len(endpoints)
        if number_of_endpoints == 0:
            return 0
        
        sum_loc = sum([endpoint.function.loc for endpoint in endpoints])
        return round(sum_loc/number_of_endpoints, 2)

    @evo.metric('Endpoints: HTTP methods', categorical=True, top_n=5)
    def http_method(commit: ParsedCommit):
        fastapi = FastAPICommit(commit)
        return [endpoint.decorator.http_method for endpoint in fastapi.endpoints()]

    @evo.metric('Endpoints: sync vs. async', categorical=True)
    def sync_async(commit: ParsedCommit):
        fastapi = FastAPICommit(commit)
        return [endpoint.function.sync_async() for endpoint in fastapi.endpoints()]

    @evo.metric('Endpoints: return type in function?', categorical=True)
    def has_return_type(commit: ParsedCommit):
        fastapi = FastAPICommit(commit)
        return [str(endpoint.function.has_return_type()) for endpoint in fastapi.endpoints()]

    @evo.metric('Endpoints: typed vs. untyped parameters', categorical=True, show_version_chart=False)
    def typed_untyped(commit: ParsedCommit):
        fastapi = FastAPICommit(commit)
        return [typed_untyped for endpoint in fastapi.endpoints() for typed_untyped in endpoint.function.typed_untyped()]

    @evo.metric('Endpoints: default parameters?', categorical=True)
    def defaults(commit: ParsedCommit):
        fastapi = FastAPICommit(commit)
        return [str(has_default) for endpoint in fastapi.endpoints() for has_default in endpoint.function.defaults()]

    @evo.metric('Endpoints: common parameter names', categorical=True, version_chart_type='hbar', top_n=5)
    def parameter_names(commit: ParsedCommit):
        fastapi = FastAPICommit(commit)
        return [param_name for endpoint in fastapi.endpoints() for param_name in endpoint.function.parameter_names()]

    @evo.metric('Endpoints: common parameter types', categorical=True, version_chart_type='hbar', top_n=5)
    def parameter_types(commit: ParsedCommit):
        fastapi = FastAPICommit(commit)
        return [param_type for endpoint in fastapi.endpoints() for param_type in endpoint.function.parameter_types()]

    @evo.metric('Endpoints: mean number of parameters', show_version_chart=False)
    def mean_parameters(commit: ParsedCommit):
        fastapi = FastAPICommit(commit)

        endpoints = fastapi.endpoints()
        number_of_endpoints = len(endpoints)
        if number_of_endpoints == 0:
            return 0
        
        sum_of_parameters = sum([len(endpoint.function.parameters) for endpoint in endpoints])
        return round(sum_of_parameters/number_of_endpoints, 2)

    @evo.metric('Security imports', categorical=True, version_chart_type='hbar', top_n=5)
    def security_imports(commit: ParsedCommit):
        fastapi = FastAPICommit(commit)
        return fastapi.security_imports()

    @evo.metric('Response imports', categorical=True, version_chart_type='hbar', show_version_chart=False, top_n=5)
    def response_imports(commit: ParsedCommit):
        fastapi = FastAPICommit(commit)
        return fastapi.response_imports()

    @evo.metric('FastAPI imports', show_version_chart=False)
    def fastapi_imports(commit: ParsedCommit):
        fastapi = FastAPICommit(commit)
        return len(fastapi.fastapi_imports())

    @evo.metric('APIRouter imports', show_version_chart=False)
    def apirouter_imports(commit: ParsedCommit):
        fastapi = FastAPICommit(commit)
        return len(fastapi.apirouter_imports())

    @evo.metric('UploadFile imports', show_version_chart=False)
    def upload_file_imports(commit: ParsedCommit):
        fastapi = FastAPICommit(commit)
        return len(fastapi.upload_file_imports())

    @evo.metric('BackgroundTasks imports', show_version_chart=False)
    def background_tasks_imports(commit: ParsedCommit):
        fastapi = FastAPICommit(commit)
        return len(fastapi.background_tasks_imports())

    @evo.metric('WebSocket imports', show_version_chart=False)
    def websocket_imports(commit: ParsedCommit):
        fastapi = FastAPICommit(commit)
        return len(fastapi.websocket_imports())
    

from tree_sitter import Node
from gitevo import ParsedCommit
from gitevo.utils import as_str


class FastAPIEndpoint:

    def __init__(self, decorator, function):
        self.decorator: EndpointDecorator = decorator
        self.function: EndpointFunction = function

class EndpointDecorator:
    
    def __init__(self, object, http_method, arguments):
        self.object = object
        self.http_method = http_method
        self.arguments = arguments

    def argument_names(self):
        return [arg[0] for arg in self.arguments if arg[0] != '']

    def argument_values(self):
        return [arg[1] for arg in self.arguments]

    def __str__(self):
        return f'{self.http_method} {self.arguments[0][1]}'

class EndpointFunction:
    
    def __init__(self, name, parameters, return_type, is_async, loc):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.is_async = is_async
        self.loc = loc

    def sync_async(self):
        if self.is_async: return 'async'
        return 'sync'
    
    def parameter_names(self):
        return [param[0] for param in self.parameters if param[0] is not None]
    
    def parameter_types(self):
        return [param[1] for param in self.parameters if param[1] is not None]
    
    def typed_untyped(self):
        return ['typed' if param[2] else 'untyped' for param in self.parameters if param[2] is not None]
    
    def defaults(self):
        return ['with default' if param[3] else 'without default' for param in self.parameters if param[3] is not None]
    
    def param_node_types(self):
        return [param[4] for param in self.parameters if param[4] is not None]

    def has_return_type(self):
        if self.return_type: return 'with return type'
        return 'without return type'

    def __str__(self):
        return f'{self.name}'
    
class FastAPICommit:
    
    def __init__(self, parsed_commit: ParsedCommit):
        self.parsed_commit = parsed_commit
  
    def endpoints(self) -> list[FastAPIEndpoint]:
        result = []
        for decorated_definition_node in self.parsed_commit.find_nodes_by_type(['decorated_definition']):
            for node in decorated_definition_node.children:

                if self._is_fastapi_decorator(node):
                    endpoint_decorator = self._create_endpoint_decorator(node)
                    endpoint_function = None
                    
                    function_definition_node = decorated_definition_node.child_by_field_name('definition')
                    if function_definition_node:
                        endpoint_function = self._create_endpoint_function(function_definition_node)

                    if endpoint_decorator and endpoint_function:
                        endpoint = FastAPIEndpoint(endpoint_decorator, endpoint_function)
                        result.append(endpoint)
        return result
    
    def fastapi_imports(self):
        return self._find_imports(['FastAPI'])

    def apirouter_imports(self):
        return self._find_imports(['APIRouter'])
    
    def websocket_imports(self):
        return self._find_imports(['WebSocket'])
    
    def background_tasks_imports(self):
        return self._find_imports(['BackgroundTasks'])
    
    def upload_file_imports(self):
        return self._find_imports(['UploadFile'])
    
    def security_imports(self):

        # https://github.com/fastapi/fastapi/blob/master/fastapi/security/__init__.py
        security_classes = ['APIKeyCookie', 'APIKeyHeader', 'APIKeyQuery', 'HTTPAuthorizationCredentials', 
                            'HTTPBasic', 'HTTPBasicCredentials', 'HTTPBearer', 'HTTPDigest', 'OAuth2',
                            'OAuth2AuthorizationCodeBearer', 'OAuth2PasswordBearer', 'OAuth2PasswordRequestForm',
                            'OAuth2PasswordRequestFormStrict', 'SecurityScopes', 'OpenIdConnect']

        return self._find_imports(security_classes)
    
    def response_imports(self):
        response_classes = ['FileResponse', 'HTMLResponse', 'JSONResponse', 'PlainTextResponse', 'RedirectResponse', 'Response', 'StreamingResponse']
        return self._find_imports(response_classes)
    
    def _create_endpoint_decorator(self, decorator_node: Node) -> EndpointDecorator:

        object = as_str(self.parsed_commit.descendant_node_by_field_name(decorator_node, 'object').text)
        http_method = as_str(self.parsed_commit.descendant_node_by_field_name(decorator_node, 'attribute').text)
        argumemnts_node = self.parsed_commit.descendant_node_by_field_name(decorator_node, 'arguments')

        if argumemnts_node:
            args = []
            for arg_node in self.parsed_commit.named_children_for(argumemnts_node):

                if arg_node.type == 'keyword_argument':
                    name = as_str(arg_node.child_by_field_name('name').text)
                    value = as_str(arg_node.child_by_field_name('value').text)
                else:
                    name = ''
                    value = as_str(arg_node.text)
                args.append((name, value))
        
        return EndpointDecorator(object, http_method, args)
    
    def _create_endpoint_function(self, function_definition: Node) -> EndpointFunction:

        is_async = as_str(function_definition.child(0).text) == 'async'
        name = as_str(function_definition.child_by_field_name('name').text)
        loc = self._loc(function_definition)
        
        return_type = ''
        return_type_node = function_definition.child_by_field_name('return_type')
        if return_type_node:
            return_type = as_str(return_type_node.text)

        parameters_node = function_definition.child_by_field_name('parameters')

        if parameters_node:
            params = []
            for param_node in self.parsed_commit.named_children_for(parameters_node):
                
                param_name = None
                param_type = None
                is_typed = None
                has_default = None
                node_type = None

                if param_node.type == 'identifier':
                    param_name = as_str(param_node.text)
                    is_typed = False
                    has_default = False
                    node_type = 'only_name'

                if param_node.type == 'default_parameter':
                    param_name = as_str(param_node.child_by_field_name('name').text)
                    is_typed = False
                    has_default = True
                    node_type = 'default_parameter'
                
                if param_node.type == 'typed_parameter':
                    param_name = as_str(param_node.children[0].text)
                    param_type = as_str(param_node.child_by_field_name('type').text)
                    is_typed = True
                    has_default = False
                    node_type = 'typed_parameter'
                
                if param_node.type == 'typed_default_parameter':
                    param_name = as_str(param_node.child_by_field_name('name').text)
                    param_type = as_str(param_node.child_by_field_name('type').text)
                    is_typed = True
                    has_default = True
                    node_type = 'typed_default_parameter'

                params.append((param_name, param_type, is_typed, has_default, node_type))
        
        return EndpointFunction(name, params, return_type, is_async, loc)
    
    def _loc(self, node: Node) -> int:
        return len(as_str(node.text).split('\n'))
    
    def _is_fastapi_decorator(self, node: Node):

        fastapi_objects = ['app', 'router']
        http_methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace', 'connect']

        if node.type != 'decorator':
            return False

        decorator_obj = self.parsed_commit.descendant_node_by_field_name(node, 'object')
        decorator_att = self.parsed_commit.descendant_node_by_field_name(node, 'attribute')
        
        if decorator_obj:
            for fastapi_obj in fastapi_objects:
                if fastapi_obj in as_str(decorator_obj.text):
                    if decorator_att and as_str(decorator_att.text) in http_methods:
                        return True
        return False
    
    def _find_imports(self, import_classes):
        imports = []
        for imp in self._imports():
            for imp_element in imp.children_by_field_name('name'):
                for import_class in import_classes:
                    if import_class == as_str(imp_element.text):
                        imports.append(import_class)
        return imports
    
    def _imports(self) -> list[Node]:
        nodes = ['import_statement', 'import_from_statement', 'future_import_statement']
        return self.parsed_commit.find_nodes_by_type(nodes)