#!/usr/bin/env python3
#
# This script gets the RDS/Elasticache information and puts it in the vars
#

from __future__ import unicode_literals, print_function
import argparse
import json
import os

def nested_set(dic, keys, value):
    _keys = keys[:-1]
    for idx, key in enumerate(_keys):
        if len(_keys) > (idx+1) and _keys[idx+1].isdigit() and int(_keys[idx+1]) < 50:
            dic = dic.setdefault(key, [])
            i = int(_keys[idx+1])
            if i not in dic:
                dic.append({})
            dic = dic[i]
            break
        else:
            dic = dic.setdefault(key, {})

    dic[keys[-1]] = value

PARSERS = {}
def parses(prefix):
    def inner(func):
        PARSERS[prefix] = func
        return func

    return inner

def iterresources(file):
    with open(file, 'r') as f:
        try:
            state = json.load(f)
            for resource in state['resources']:
                yield resource
        except Exception:
            yield '', 'no.type', ''

def parse_tags(attrs):
    tags = []
    for key in attrs.keys():
        if key.startswith('tags'):
            if '.' in key:
                a, name = key.split('.')
            else:
                name = key
            if name == '%':
                continue
            tags.append(("%s_%s" % (name, attrs[key])).lower())
    return tags

@parses('aws_instance')
def parse_aws_instance(instance, vars=None):
    return (
	    'aws_instance',
	    instance['attributes']['id'],
	    instance['attributes']['private_ip'],
        instance['attributes']['tags']
    )

@parses('aws_lb')
def parse_lb_instance(resource, vars=None):
    if 'primary' in resource:
        instance = resource['primary']
    elif 'instances' in resource:
        instance = resource['instances'][0]
    else:
        return ['','','', []]

    for group in parse_tags(instance['attributes']):
        if group.startswith('name_'):
            name = '_'.join(group.split('_')[1:])

    return (
        'aws_lb_instance',
        name,
        instance['attributes']['dns_name'],
        []
    )

@parses('aws_db_instance')
def parse_db_instance(instance, vars=None):
    return (
        'aws_db_instance',
        instance['attributes']['id'],
        instance['attributes']['address'],
        instance['attributes']['tags']
    )

@parses('aws_efs_file_system')
def parse_efs(instance, vars=None):
    name = instance['attributes']['id']
    if 'Name' in instance['attributes']['tags']:
        name = instance['attributes']['tags']['Name']

    return (
        'aws_efs',
        name,
        instance['attributes']['dns_name'],
        instance['attributes']['tags']
    )

@parses('aws_s3_bucket')
def parse_s3_bucket(instance, vars=None):
    name = instance['attributes']['id']
    if 'Name' in instance['attributes']['tags']:
        name = instance['attributes']['tags']['Name']

    return (
        'aws_s3_bucket',
        name,
        instance['attributes']['bucket_domain_name'],
        instance['attributes']['tags'],
        {
            'regional_name': instance['attributes']['bucket_regional_domain_name'],
            'region': instance['attributes']['region']
        }
    )

@parses('aws_elasticache_cluster')
def parse_elasticache_cluster(instance, vars=None):
    if 'cluster_address' in instance['attributes']:
        address = instance['attributes']['cluster_address']
    else:
        # grab the first node as the address
        address = instance['attributes']['cache_nodes'][0]['address']

    nodes = []
    for node in instance['attributes']['cache_nodes']:
        if 'address' in node:
            nodes.append(node['address'])

    if len(nodes) == 1:
        address = nodes[0]

    return (
        'aws_elasticache_cluster',
        instance['attributes']['cluster_id'],
        address,
        instance['attributes']['tags'],
        nodes
    )

def main():
    parser = argparse.ArgumentParser(
        __file__, __doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--list',
                       action='store_true',
                       help='list all variables')
    modes.add_argument('--host',
                       help='list variables for a single host')
    parser.add_argument('--file',
                        help="tfstate file to parse")
    parser.add_argument('--env',
                        default='all',
                        help="Environment the hosts belong to")
    parser.add_argument('--vars-only',
                        dest='vars_only',
                        default=False,
                        action='store_true',
                        help="only the vars, no hosts")
    parser.add_argument('--pretty',
                        action='store_true',
                        help='pretty-print output JSON')

    args = parser.parse_args()

    if args.file:
        file = args.file
    else:
        file = '%s/.tfstate' % os.path.dirname(__file__)

    if args.list:
        vars = {}
        groups = {}
        hosts = []
        hostvars = {}
        for resource in iterresources(file):
            if 'type' not in resource:
                continue

            if resource['type'] not in PARSERS:
                continue

            if 'instances' not in resource or len(resource['instances']) == 0:
                continue

            module_name = None
            if 'module' in resource:
                resource_type, module_name = resource['module'].split('.', 1)
                if '.' in module_name:
                    module_name = module_name.split('.',1)[0]

            try:
                parser = PARSERS[resource['type']]
            except KeyError as e:
                continue

            for instance in resource['instances']:
                if 'attributes_flat' in instance:
                    instance['attributes'] = {}
                    for i in instance['attributes_flat']:
                        if i[-1] is '#' or i[-1] is '%':
                            continue
                        nested_set(instance['attributes'], i.split('.'), instance['attributes_flat'][i])

                data = parser(instance)
                if len(data) == 4:
                    type, name, address, tags = data
                else:
                    type, name, address, tags, extra = data
                if type == "":
                    continue
                if not module_name:
                    module_name = type

                if len(tags) > 0:
                    tags = dict((k.lower(), v) for k, v in tags.items())

                if type == "aws_instance":
                    if 'name' in tags:
                        name = tags['name']
                    hosts.append(name)
                    hostvars[name] = {'ansible_host': address}
                    if 'server' in tags:
                        # Terraform use to have tags be `name_value`, but now they are arrays
                        server = 'server_%s' % tags['server']
                        if server not in groups:
                            groups[server] = {'hosts':[]}
                        groups[server]['hosts'].append(name)
                        if module_name not in hostvars:
                            if module_name not in groups:
                                groups[module_name] = {'hosts': []}
                            groups[module_name]['hosts'].append(name)

                if not type in vars:
                    vars[type] = {}
                vars[type][name] = address

                # aws_s3_buckets override the vars by pushing the extra data
                if type == "aws_s3_bucket" and extra is not None:
                    vars[type][name] = extra
                    vars[type][name]['id'] = name

                if type == "aws_elasticache_cluster":
                    extra_name = "%s_nodes" % module_name
                    if extra_name not in vars:
                        vars[extra_name] = {}
                    vars[extra_name][name] = extra

        if args.vars_only:
            output = {
                'all': {
                    'vars': {
                        args.env: vars
                    }
                },
                '_meta': {'hostvars':{}}
            }
        else:
            output = {
                'all': {
                    'vars': vars,
                    'children': list(groups.keys())
                },
                '_meta': {'hostvars': hostvars}
            }
            output.update(groups)

        print(json.dumps(output, indent=4 if args.pretty else None))

if __name__ == '__main__':
    main()