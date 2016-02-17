#!/bin/sh
# Common utilities for shell scripts

# find root directory
CURDIR=$(dirname $0)
ROOTDIR=$(cd ${CURDIR}/.. && pwd)

if [ -z $(which ansible-playbook) ]; then
  echo "Can't find ansible-playbook in the path."
  exit 1
fi

#
# Runs the given play
#
runplay() {
  local play
  local args
  play=$1
  shift
  args=$*

  local playbook="${ROOTDIR}/ansible/playbooks/${play}.yml"
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

  echo ansible-playbook -i ${ROOTDIR}/etc/ansible/hosts "${playbook}" --limit "$group" $args

  # Allow the user to change the location of the ansible configuration
  # This allows a bastion host to be used
  if [ -z "${ALT_ANSIBLE_CONFIG}" ]; then
    CONFIG_FILE="${ROOTDIR}/etc/ansible/ansible.cfg"
  else
    CONFIG_FILE=$ALT_ANSIBLE_CONFIG
  fi

  if [ -z "${OPS_ENV}" ]; then
    HOSTS_FILE=${ROOTDIR}/etc/ansible/hosts
  else
    HOSTS_FILE=${ROOTDIR}/etc/local/hosts
  fi

  # add --ask-vault-pass once we are ready to really begin using the vault
  env ANSIBLE_CONFIG="${CONFIG_FILE}" ansible-playbook -i "${HOSTS_FILE}" "${playbook}" --limit "$group" $args
}

runwithoutlimit() {
  local play
  local group
  local args

  play=$1
  shift
  args=$*

  local playbook="${ROOTDIR}/ansible/playbooks/${play}.yml"
  if [ ! -f "$playbook" ]; then
    echo "playbook file for ${playbook} is missing."
    exit 1
  fi


  # Allow the user to change the location of the ansible configuration
  # This allows a bastion host to be used
  if [ -z "${ALT_ANSIBLE_CONFIG}" ]; then
    CONFIG_FILE="${ROOTDIR}/etc/ansible/ansible.cfg"
  else
    CONFIG_FILE=$ALT_ANSIBLE_CONFIG
  fi

  if [ -z "${OPS_ENV}" ]; then
    HOSTS_FILE=${ROOTDIR}/etc/ansible/hosts
  else
    HOSTS_FILE=${ROOTDIR}/etc/local/hosts
  fi

  echo ansible-playbook -i "${HOSTS_FILE}" "${playbook}"  $args

  # add --ask-vault-pass once we are ready to really begin using the vault
  env ANSIBLE_CONFIG="${CONFIG_FILE}" ansible-playbook -i "${HOSTS_FILE}" "${playbook}" $args
}