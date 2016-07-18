# Ansible lookup plugin for getting the first available file
# (c) 2015,2016 David Lundgren <dlundgren@syberisle.net>

# For each item if the path exists along the regular paths then the first found entry will used.
#
# This will put the content of the found file into the items data
#

from ansible import constants as C
from ansible import utils, errors
from ansible.utils import template

import os
import codecs

class LookupModule(object):
    def __init__(self, basedir=None, **kwargs):
        self.basedir = basedir

    def get_paths(self, inject):
        paths = []

        paths.append(utils.path_dwim(self.basedir, ''))

        if '_original_file' in inject:
            paths.append(utils.path_dwim_relative(inject['_original_file'], '', '', self.basedir, check=False))

        if 'playbook_dir' in inject:
            paths.append(inject['playbook_dir'])

        for path in C.get_config(C.p, C.DEFAULTS, 'lookup_file_paths', None, [], islist=True):
            path = utils.unfrackpath(path)
            if os.path.exists(path):
                paths.append(path)

        return paths

    def run(self, terms, inject=None, **kwargs):
        ret = []
        for item in terms['items']:
            content = self.load_file_content(template.template_from_string('', terms['name'], {'item':item}), inject)
            if content:
                item[terms['key']] = content;
                ret.append(item)

        return ret

    def load_file_content(self, file, inject):
        ret = None
        for path in self.get_paths(inject):
            path = os.path.join(path, 'files', file)
            if os.path.exists(path):
                with open (path, "r") as myfile:
                    ret = myfile.read()
                break

        return ret