# @todo COMMENT THIS MO ^ dlundgren
from ansible import constants as C
from ansible import utils, errors
from ansible.utils import template

import os

class LookupModule(object):
    def __init__(self, basedir=None, **kwargs):
        self.basedir = basedir

    def run(self, terms, inject=None, **kwargs):
        ret = []

        for item in terms['items']:
            content = self.resolveAvailableFilePath(template.template_from_string('', terms['name'], {'item':item}), inject)
            if content:
                item[terms['key']] = content
                ret.append(item)

        return ret

    def __getPaths(self, inject):
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

    def resolveAvailableFilePath(self, file, inject):
        ret = None

        for path in self.__getPaths(inject):
            path = os.path.join(path, 'files', file)
            if os.path.exists(path):
                ret = path
                break

        return ret