# Ansible lookup plugin for getting the first available file given a list of items and a template
# (c) 2015,2016 David Lundgren <dlundgren@syberisle.net>
#
# Given a list of items it will attempt to find a file in the regular list of paths that is similar to the name
#
# - name: Add SSH keys
#  authorized_key:
#    user: "{{ item.username }}"
#    state: present
#    key: "{{ lookup('file', item.pubkey) }} }}"
#    manage_dir: yes
#    path: '/home/{{ item.username }}/.ssh/authorized_keys'
#  with_available_file_from_items:
#    items: "{{ users }}"
#    name: files/ssh/keys/{{ item.username }}.pubkeys
#    key: pubkey
#
# This will look in the {role}/files/ssh/keys/, {playbook}/files/ssh/keys/ folders for the {username}.pubkeys file.
# If the file is not found then the user is not returned in the list of items to be used.

import os

from ansible import constants as C
from ansible import utils, errors
from ansible.utils import template

class LookupModule(object):
    def __init__(self, basedir=None, **kwargs):
        self.basedir = basedir

    def run(self, terms, inject=None, **kwargs):
        ret = []

        for item in terms['items']:
            content = self.resolve_available_file_path(template.template_from_string('', terms['name'], {'item':item}), inject)
            if content:
                item[terms['key']] = content
                ret.append(item)

        return ret

    def get_paths(self, inject):
        paths = []

        for path in C.get_config(C.p, C.DEFAULTS, 'lookup_file_paths', None, [], islist=True):
            path = utils.unfrackpath(path)
            if os.path.exists(path):
                paths.append(path)

        if '_original_file' in inject:
            paths.append(utils.path_dwim_relative(inject['_original_file'], '', '', self.basedir, check=False))

        if 'playbook_dir' in inject:
            paths.append(inject['playbook_dir'])

        paths.append(utils.path_dwim(self.basedir, ''))

        unq = []
        [unq.append(i) for i in paths if not unq.count(i)]

        return unq

    def resolve_available_file_path(self, file, inject):
        ret = None

        for path in self.get_paths(inject):
            path = os.path.join(path, 'files', file)
            if os.path.exists(path):
                ret = path
                break

        return ret