# (c) 2018 David Lundgren
# MIT
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = """
    lookup: vars_dict_starts_with
    author: David Lundgren
    version_added: "2.5"
    short_description: Lookup templated value of variables that start with a prefix
    description:
      - Retrieves the value of an Ansible variable.
    options:
      _terms:
        description: The variable names to look up.
        required: True
      default:
        description:
            - What to return if a variable is undefined.
            - If no default is set, it will result in an error if any of the variables is undefined.
"""

EXAMPLES = """
- name: find several related variables
  debug: msg="{{ lookup('vars_starts_with', 'ansible_play') }}"
- name: alternate way to find some 'prefixed vars' in loop
  debug: msg="{{ lookup('vars', 'ansible_play_' + item) }}"
  loop:
    - hosts
    - batch
    - hosts_all
"""

RETURN = """
_value:
  description:
    - value of the variables requested.
"""

from ansible.errors import AnsibleError, AnsibleUndefinedVariable
from ansible.module_utils.six import string_types
from ansible.plugins.lookup import LookupBase


class LookupModule(LookupBase):

	def run(self, terms, variables=None, **kwargs):
		if variables is not None:
			self._templar.set_available_variables(variables)
		myvars = getattr(self._templar, '_available_variables', {})

		self.set_options(direct=kwargs)
		default = self.get_option('default')

		ret = {}
		for term in terms:
			if not isinstance(term, string_types):
				raise AnsibleError('Invalid setting identifier, "%s" is not a string, its a %s' % (term, type(term)))

			try:
				for key in myvars:
					if key.startswith(term):
						# print(self._templar.template(myvars[key], fail_on_undefined=True))
						ret.update(self._templar.template(myvars[key], fail_on_undefined=True))
						# ret.extend(self._templar.template(myvars[key], fail_on_undefined=True))
				for key in myvars['hostvars'][myvars['inventory_hostname']]:
					if key.startswith(term):
						ret.update(self._templar.template(myvars['hostvars'][myvars['inventory_hostname']][key], fail_on_undefined=True))
			except AnsibleUndefinedVariable:
				if default is not None:
					ret.update(default)
				else:
					raise

		return ret
