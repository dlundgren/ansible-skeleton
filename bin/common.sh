#!/bin/sh
# Common utilities for shell scripts

# find root directory
CURDIR=$(dirname $0)
ROOTDIR=$(cd ${CURDIR}/.. && pwd)
PLAYDIR=$ROOTDIR/plays
VARDIR=$ROOTDIR/inventory

if [ -z $(which ansible-playbook) ]; then
  echo "Can't find ansible-playbook in the path."
  exit 1
fi

RESET="\033[0m"
ARROW="\033[32m==>\033[0m"
ERROR="\033[31m-->"

# Allow the user to change the location of the ansible configuration
# This allows a bastion host to be used
if [ -z "${ALT_ANSIBLE_CONFIG}" ]; then
    CONFIG_FILE="${ROOTDIR}/ansible.cfg"
else
    CONFIG_FILE=$ALT_ANSIBLE_CONFIG
fi

if [ -z "${HOSTS_FILE}" ]; then
    if [ "${OPS_ENV}" != "dev" ]; then
        HOSTS_FILE=${VARDIR}/hosts
    else
        HOSTS_FILE=${VARDIR}/hosts-dev
    fi
fi

buildcommand() {
  CMD="env ANSIBLE_CONFIG=${CONFIG_FILE} ansible-playbook"
}

#
# Runs the given play
#
runplay() {
  local play
  local args
  play=$1
  shift
  args=$*

  local playbook="${PLAYDIR}/${play}.yml"
  if [ ! -f "$playbook" ]; then
    echo "playbook file for ${playbook} is missing."
    exit 1
  fi

  runit $playbook $args
}

# Quick function to run the ansible playbook (since we use it multiple times above
runit() {
  local playbook
  local group
  local args

  playbook=$1
  shift
  group=$1
  shift
  args=$*

#  echo ANSIBLE_CONFIG="${CONFIG_FILE}" ansible-playbook -i "${HOSTS_FILE}" "${playbook}" --limit "$group" $args
  #env ANSIBLE_CONFIG="${CONFIG_FILE}"
  ansible-playbook "${playbook}" --limit "$group" $args
}

runwithoutlimit() {
  local play
  local group
  local args

  play=$1
  shift
  args=$*

  local playbook="${PLAYDIR}/${play}.yml"
  if [ ! -f "$playbook" ]; then
    echo "playbook file for ${playbook} is missing."
    exit 1
  fi

  # add --ask-vault-pass once we are ready to really begin using the vault
  env ANSIBLE_CONFIG="${CONFIG_FILE}" ansible-playbook  "${playbook}" --extra-vars "${extravars}" $args
}