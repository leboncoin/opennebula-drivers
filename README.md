# OpenNebula Driver

Some IPAM and AUTH driver for OpenNebula
Developped for @leboncoin

## Prerequisites

```bash
apt-get install python-pip
```

## Installation

```bash
su - oneadmin

# Put the driver in the right directory.
# IPAM : ~/remotes/ipam/
# AUTH : ~/remotes/auth/
# The owner should be oneadmin:oneadmin

cd ~/remotes/<driver_type>/<driver_name>/

# Install python libs
sudo pip install -r requirements.txt

# Enable it in opennebula
# Display the loaded drivers (Ex: ipam)
ps aux | grep one_ipam

```

Edit the `/etc/one/oned.conf` to enable the new driver
```
...
IPAM_MAD = [
    EXECUTABLE = "one_ipam",
    ARGUMENTS  = "-t 1 -i dummy,<driver_name>"
]
...
AUTH_MAD = [
    EXECUTABLE = "one_auth_mad",
    AUTHN = "ssh,x509,ldap,server_cipher,server_x509,<driver_name>"
]
```

```bash
# Restart opennebula
sudo systemctl restart opennebula.service

# Display the loaded drivers (Ex: ipam)
ps aux | grep one_ipam
```

## IPAM configuration

You need to create a new *Address Range* in a *Virtual Network*.

Add this driver during the create, it cannot be updated.

## AUTH configuration

To active this auth driver by default, add this line into `/etc/one/oned.conf` :

```
...
DEFAULT_AUTH = "<driver_name>"
...
```

