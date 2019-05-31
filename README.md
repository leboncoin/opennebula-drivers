
# OpenNebula Driver

Some IPAM and AUTH driver for OpenNebula
Developed for @leboncoin

## Prerequisites

```bash
apt-get install python-pip
```

## Installation

```bash
su - oneadmin

# Put the driver in the right directory.
# IPAM : ~/remotes/ipam/
# IPAM HOOK : ~/remotes/hooks/ft/
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
...
VM_HOOK = [
   name      = "hook_powerdns",
   on        = "CREATE",
   command   = "/var/lib/one/remotes/hooks/ft/hook_powerdns.py",
   arguments = "$TEMPLATE" ]
```

```bash
# Restart opennebula
sudo systemctl restart opennebula.service

# Display the loaded drivers (Ex: ipam)
ps aux | grep one_ipam
```

## IPAM configuration

You need to create a new *Address Range* in a *Virtual Network*.

The IPAM works in two steps :
 - The instance is created, Opennebula is asking a new IP to the IPAM driver **powerdns**
     - The driver doesn't know the final name of the instance, it creates an *A entry* in the DNS relative to the encoded IP
 - When the instance is in the state **CREATE**, it triggers the **hook_powerdns** which is updating the *A entry* in the DNS (replacing the encoded IP value to the final name)


## AUTH configuration

To active this auth driver by default, add this line into `/etc/one/oned.conf` :

```
...
DEFAULT_AUTH = "<driver_name>"
...
```
