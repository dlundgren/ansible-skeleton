#!/bin/sh
#
# Since we allow vagrant-local.yml to specify the IP we need to reconfigure the hosts in ansible
#
#

CURDIR=$(dirname $0)

if [ ! -f "${CURDIR}/../../bin/common.sh" ]; then
  echo "Can't find the common script."
  exit 1
fi

. "${CURDIR}/../../bin/common.sh"

IP=$(grep ops_ip ${ROOTDIR}/../vagrant-defaults.yml | awk -F: '{print $2;}' | sed 's/ //g')
if [ -f "${ROOTDIR}/../vagrant-local.yml" ]; then
  IP=$(grep ops_ip ${ROOTDIR}/../vagrant-local.yml | awk -F: '{print $2;}' | sed 's/ //g')
fi

echo `cat <<EOF
{
  'vagrants': {
    'hosts':['vagrant','tester','box'],
    'vars':{'ansible_host': '$IP'}
  },
  '_meta': {
    'hostvars': {
      'vagrant' : {'ansible_host': '$IP'},
      'tester' : {'ansible_host': '$IP'},
      'box' : {'ansible_host': '$IP'}
    }
  }
}
EOF` | sed 's/ //g'
