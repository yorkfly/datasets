from __future__ import print_function
import json
import sys, os
from pprint import pprint
try:
    from itertools import izip
except ImportError:
    izip = zip
from auxiliary import flat_case
from collections import OrderedDict, defaultdict

try:
    unicode
except NameError:
    unicode = str
    
def average(a_list):
    return sum(a_list) / len(a_list) if a_list else 0
    
def _byteify(input):
    """
    Force the given input to only use `str` instead of `bytes` or `unicode`.
    This works even if the input is a dict, list,
    """
    if isinstance(input, dict):
        return {_byteify(key): _byteify(value) for key, value in input.items()}
    elif isinstance(input, list):
        return [_byteify(element) for element in input]
    elif isinstance(input, unicode):
        return str(input.encode('ascii', 'replace').decode('ascii'))
    else:
        return input
    
def json_path(path, data):
    entries = path.split(".")
    for entry in entries:
        if entry.startswith("["):
            entry = int(entry[1:-1])
        data = data[entry]
    return data
    
def _guess_schema(input):
    if isinstance(input, dict):
        return {str(key.encode('ascii', 'replace').decode('ascii')): 
                _guess_schema(value) for key, value in input.items()}
    elif isinstance(input, list):
        return [_guess_schema(input[0])] if input else []
    else:
        return type(input)

class JsonMetrics(object):
    def __init__(self, structures, data, parent_name):
        self.values= {}
        self.headers = {}
        self.last_id = {}
        self.path = []
        self.name = parent_name
        self.union_types = defaultdict(set)
        self.structures = structures
        self.report = {
            'locals': 0,
            'heights': [],
            'lists': {
                'count': 0,
                'lengths': [],
                'complex': 0
            },
            'dicts': {
                'count': 0,
                'widths': [],
            },
            'unions': {
                'count': 0,
                'sizes': []
            },
            'atomics': {
                'strings': 0,
                'ints': 0,
                'floats': 0,
                'longs': 0,
                'nones': 0,
                'booleans': 0,
                'count': 0
            }
        }
        self.walk(data, parent_name)
        self.countUnions()
        self.aggregateLists()
        
    @property
    def json_path(self):
        return ".".join([self.name]+self.path)
        
    def walk(self, chunk, parent_name):
        if isinstance(chunk, dict):
            self.walk_dict(chunk, parent_name)
        elif isinstance(chunk, list):
            self.walk_list(chunk, parent_name)
        else:
            self.walk_atomic(chunk, parent_name)
        return self
        
    def walk_dict(self, a_dict, parent_name):
        self.report['dicts']['widths'].append(len(a_dict))
        self.report['dicts']['count'] += 1
        for key, value in a_dict.items():
            self.path.append(key)
            self.walk(value, key)
            self.path.pop()
    def walk_list(self, a_list, parent_name):
        self.report['lists']['count'] += 1
        self.report['lists']['lengths'].append(len(a_list))
        if a_list:
            self.path.append("[0]")
            value = a_list[0]
            if (isinstance(value, dict) or isinstance(value, list)):
                self.report['lists']['complex'] += 1
            self.walk(value, parent_name)
            self.path.pop()
    def walk_atomic(self, an_atomic, parent_name):
        self.union_types[self.json_path].add(type(an_atomic))
        self.report['heights'].append(len(self.path))
        self.report['atomics']['count'] += 1
    def countUnions(self):
        for types in self.union_types.values():
            if len(types) > 1:
                self.report['unions']['count'] += 1
                self.report['unions']['sizes'].append(len(types))
            for an_atomic in types:
                if an_atomic == int:
                    self.report['atomics']['ints'] += 1
                elif an_atomic == float:
                    self.report['atomics']['floats'] += 1
                elif an_atomic == str:
                    self.report['atomics']['strings'] += 1
                elif an_atomic == unicode:
                    self.report['atomics']['strings'] += 1
                elif an_atomic is None:
                    self.report['atomics']['nones'] += 1
                elif an_atomic == bool:
                    self.report['atomics']['booleans'] += 1
    def aggregateLists(self):
        if self.report['heights']:
            self.report['heights'] = max(self.report['heights'])
        else:
            self.report['heights'] = 0        
        if self.report['lists']['lengths']:
            self.report['lists']['lengths'] = max(self.report['lists']['lengths'])
        else:
            self.report['lists']['lengths'] = 0
        if self.report['dicts']['widths']:
            self.report['dicts']['average branching factor'] = average(self.report['dicts']['widths'])
            del self.report['dicts']['widths']
        else:
            self.report['dicts']['widths'] = 0
        if self.report['unions']['sizes']:
            self.report['unions']['sizes'] = max(self.report['unions']['sizes'])
        else:
            self.report['unions']['sizes'] = 0

def build_report(model):
    locals = model["locals"]
    hardware = model['metadata']['hardware']
    module_name = flat_case(model['metadata']['name'])
    json_reports = {}
    for local in locals:
        name = flat_case(local["name"])
        file = local["file"]
        type = local["type"]
        row = local["row"]
        with open(file, "r") as local_file:
            if type == "json":
                data_list = json.load(local_file)
                metrics = JsonMetrics({}, data_list, row)
                json_reports[name] = metrics.report
            elif type == "csv":
                pass
    return json.dumps(json_reports, indent=2)
        

def build_metrics(model, fast):
    module_name = flat_case(model['metadata']['name'])    
    files = {'metrics/' + module_name + '/' + module_name + '.json': build_report(model)}
    
    return files, {}
    