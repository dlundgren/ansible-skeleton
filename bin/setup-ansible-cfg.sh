#!/bin/sh
CURDIR=$(dirname $0)

if [ ! -f "${CURDIR}/common.sh" ]; then
  echo "Can't find the common script."
  exit 1
fi

. "${CURDIR}/common.sh"

rm -rf "${ROOTDIR}/ansible.cfg"
sed "s|##PWD##|${ROOTDIR}|g" "${ROOTDIR}/ansible.cfg.dist" > "${ROOTDIR}/ansible.cfg"

rm -rf "${ROOTDIR}/bootstrap.cfg"
sed "s|##PWD##|${ROOTDIR}|g" "${ROOTDIR}/bootstrap.cfg.dist" > "${ROOTDIR}/bootstrap.cfg"