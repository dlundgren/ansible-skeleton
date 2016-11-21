# Ansible lookup plugin for getting the first available file
# (c) 2015,2016 David Lundgren <dlundgren@syberisle.net>

# For each item if the path exists along the regular paths then the first found entry will be returned.
# This operates differently from the file or found-file plugins as it is not an error if the file is not found.

from ansible import constants as C
from ansible import utils
import os

class LookupModule(object):
    def __init__(self, basedir=None, **kwargs):
        self.basedir = basedir

    def run(self, terms, inject=None, **kwargs):

        terms = utils.listify_lookup_plugin_terms(terms, self.basedir, inject)
        ret = []

        if not isinstance(terms, list):
            terms = [terms]

        paths = self.get_paths(inject)
        for term in terms:
            for path in paths:
                path = os.path.abspath(os.path.join(path, "vars", term))
                if os.path.exists(path):
                    ret.append(path)
                    break
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