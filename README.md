# Crystal Ops

Helps maintain infrastructure.

### Requirements

* git-crypt is required to decrypt the keys and passwords. The git-crypt master key is in the safe.

### NOTES

* When pulling the repository please use ```bin/ops-update``` as this script will handle pulling in the galaxy repos
  as needed, as well as decrypting via git-crypt
* When adding a new repository from the galaxy please add it to requirements.yml

### Ansible

Ensure all hosts are in the inventory/hosts file. If they aren't in there then ansible won't work.
