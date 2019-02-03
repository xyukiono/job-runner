import os.path as osp
import networkx as nx
import hashlib
import copy

class ParamGenerator(object):

    def __init__(self):
        self.start_name = '__START__'
        self.end_name = '__END__'
        self.graph = nx.DiGraph()
        self._add_to_graph(self.start_name, self.start_name)

    def add_params(self, name, values, in_series=False):
        from_nodes = self._find_leaf_nodes()
        self._add_to_graph(name, values, from_nodes=from_nodes, in_series=in_series)

    def add_params_if(self, name, values, cond_key, cond_val):
        all_tags = self._find_node_by_name(cond_key)

        from_nodes = []

        for tag in all_tags:
            node = self.graph.nodes[tag]
            if node['value'] == cond_val:
                if node['child'] is not None:
                    print('[warning] {} has already had a child'.format(tag))
                from_nodes.append(tag)

        self._add_to_graph(name, values, from_nodes=from_nodes)            

    def generate(self, param_dict, add_param_string=True):
        if len(self._find_node_by_name(self.end_name)) == 0:
            self._close()
        all_nodes = self.graph.nodes(data=True)
        start_node = self._find_node_by_name(self.start_name)[0]
        end_node = self._find_node_by_name(self.end_name)[0]
        
        param_dict_list = []
        
        for tags in nx.all_simple_paths(self.graph, start_node, end_node):
            param = copy.deepcopy(param_dict)
            param_string = ''
            for tag in tags[1:-1]: # remove start and end tags
                node = all_nodes[tag]
                param[node['name']] = node['value']
                param_string = osp.join(param_string, '{}-{}'.format(node['name'], node['value']))
            if add_param_string:
                param['__PARAM__'] = param_string
            param_dict_list.append(param)
        return param_dict_list

    def _add_to_graph(self, key, values, from_nodes=None, in_series=False):
        if not isinstance(values, (list, tuple)):
            values = [values]

        to_nodes = []
        
        for val in values:
            hashstr = hashlib.sha256('{}-{}'.format(key, val).encode('utf-8')).hexdigest()[:16]
            self.graph.add_node(hashstr, name=key, value=val, child=None)
            to_nodes.append(hashstr)
            
        if from_nodes is not None:
            if in_series:
                # connect from_nodes to to_nodes in series
                assert len(to_nodes) == len(from_nodes)
                for fn, tn in zip(from_nodes, to_nodes):
                    self.graph.add_edge(fn, tn)
                    self.graph.nodes[fn]['child'] = key
            else:
                # connect to_nodes in each from_nodes
                for fn in from_nodes:
                    for tn in to_nodes:
                        self.graph.add_edge(fn, tn)
                    self.graph.nodes[fn]['child'] = key

    def _find_specific_attribute_node(self, graph, attr, value):
        result = []
        d = nx.get_node_attributes(graph, attr)
        for key, v in d.items():
            if(v == value):
                result.append(key)
        return result

    def _find_leaf_nodes(self):
        d = nx.get_node_attributes(self.graph, 'child')
        result = []
        for key, v in d.items():
            if v is None:
                result.append(key)
        return result

    def _find_node_by_name(self, name):
        return self._find_specific_attribute_node(self.graph, 'name', name)

    def _close(self):
        from_nodes = self._find_leaf_nodes()
        self._add_to_graph(self.end_name, self.end_name, from_nodes=from_nodes)
