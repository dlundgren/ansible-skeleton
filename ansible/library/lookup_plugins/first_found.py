# Ansible lookup plugin for getting the content of the first available file
# (c) 2015, David Lundgren <dlundgren@syberisle.net>
#
# MIT License

# For each item will find the first file and return the path

from ansible import constants as C
from ansible import utils, errors
import os
import codecs


class LookupModule(object):
    def __init__(self, basedir=None, **kwargs):
        self.basedir = basedir

    def run(self, terms, inject=None, **kwargs):

        terms = utils.listify_lookup_plugin_terms(terms, self.basedir, inject)
        anydict = False
        skip = False

        for term in terms:
            if isinstance(term, dict):
                anydict = True

                total_search = []

        if anydict:
            for term in terms:
                if isinstance(term, dict):
                    files = term.get('files', [])
                    paths = term.get('paths', [])
                    skip = utils.boolean(term.get('skip', False))

                    filelist = files
                    if isinstance(files, basestring):
                        files = files.replace(',', ' ')
                        files = files.replace(';', ' ')
                        filelist = files.split(' ')

                    pathlist = paths
                    if paths:
                        if isinstance(paths, basestring):
                            paths = paths.replace(',', ' ')
                            paths = paths.replace(':', ' ')
                            paths = paths.replace(';', ' ')
                            pathlist = paths.split(' ')

                    if not pathlist:
                        total_search = filelist
                    else:
                        for path in pathlist:
                            for fn in filelist:
                                f = os.path.join(path, fn)
                                total_search.append(f)
                else:
                    total_search.append(term)
        else:
            total_search = terms

        paths = self.__getPaths(inject)
        for fn in total_search:
            for path in paths:
                path = os.path.join(path, fn)
                if os.path.exists(path):
                    return [path]
        else:
            if skip:
                return []
            else:
                return [None]

    def __getPaths(self, inject):
        paths = []

        for path in C.get_config(C.p, C.DEFAULTS, 'lookup_file_paths', None, [], islist=True):
            path = utils.unfrackpath(path)
            if os.path.exists(path):
                paths.append(path)

        if '_original_file' in inject:
            # check the templates and vars directories too,
            # if they exist
            for roledir in ('templates', 'vars'):
                path = utils.path_dwim(self.basedir, os.path.join(self.basedir, '..', roledir))
                if os.path.exists(path):
                    paths.append(path)

        if 'playbook_dir' in inject:
            paths.append(inject['playbook_dir'])

        paths.append(utils.path_dwim(self.basedir, ''))

        unq = []
        [unq.append(i) for i in paths if not unq.count(i)]

        return unq
