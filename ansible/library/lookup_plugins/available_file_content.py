# Ansible lookup plugin for getting the content of the first available file
# (c) 2015,2016 David Lundgren <dlundgren@syberisle.net>

# For each item will find the first file and return it's content

from ansible import constants as C
from ansible import utils, errors
import os

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

        if isinstance(terms, basestring):
            terms = [terms]

        for term in terms:
            for path in self.get_paths(inject):
                path = os.path.join(path, 'files', term)
                if os.path.exists(path):
                    with open (path, "r") as myfile:
                        ret = myfile.read()
                    break


        return ret