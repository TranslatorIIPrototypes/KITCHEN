import requests
import sys
import json

def get_plater_openspecs(automat_url='http://automat.renci.org/'):
    plater_paths = requests.get(automat_url + 'registry').json()
    open_specs = {}
    for path in plater_paths:
        open_spec_path = f'{automat_url}{path}/openapi.json'
        open_spec = requests.get(open_spec_path).json()
        open_spec['info']['version'] = '2.0'
        paths = extract_paths(open_spec)
        patched_paths = patch_path(paths, path)
        open_spec['paths'] = patched_paths
        open_specs[path] = open_spec
    return open_specs

def extract_paths(open_spec):
    return open_spec['paths']

def patch_path(path, source):
    for index, key in enumerate(path):
        if key == 'tags':
            continue
        endpoint = path[key]
        patch_method(endpoint.get('get'), source, index)
        patch_method(endpoint.get('post'), source, index)
    return path

def patch_method(method, source, index):
    if method == None:
        return
    method['tags'] = [source]
    method['summary'] = method.get('summary', '')
    method['operationId'] = method.get('operationId', 'operation') + f'{index}' + source
    if 'requestBody' in method:
        if 'allowEmptyValue' in method['requestBody']:
            del method['requestBody']['allowEmptyValue']

def make_full(server_url='https://automat.renci.org/'):
    server_spec = requests.get(f'{server_url}openapi.yml').json()
    server_spec['info']['version'] = '1.0'
    server_spec['info']['termsOfService'] = ''
    server_spec['info']['contact'] = {'email': 'kebedey@renci.org'}
    server_spec['servers'] = [{'url': server_url}]
    plater_stuff = get_plater_openspecs(server_url)
    automat_paths = {}
    for plater_name in plater_stuff:
        spec = plater_stuff[plater_name]
        plater_paths = spec['paths']
        for p in plater_paths:
            automat_paths[f'/{plater_name}{p}'] = plater_paths[p]
    server_spec['paths'] = automat_paths
    return server_spec

if __name__ == '__main__':
    try:
        with open('openspec.json', 'w') as f:
            json.dump(make_full(), f)
    except:
        print('Please provide output file name')