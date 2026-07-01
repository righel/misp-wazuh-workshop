# MISP Integration Workshop — CIRCL - Installation & Network Setup

> This document describes how to build the lab environment **from scratch**: importing
> the base VMs, configuring the host-only network, and installing MISP and Wazuh.
>
> The resulting VMs are distributed as pre-configured `.ova` images for the workshop.
> If you already have those images, you can skip this document and go straight to
> [TUTORIAL.md](TUTORIAL.md).

## Lab layout

```
192.168.56.1    the host itself (VirtualBox assigns this to vboxnet0)
192.168.56.10   wazuh-manager VM
192.168.56.20   wazuh-agent-01 VM
192.168.56.30   misp docker
```

## 0 - Host-only network (do this once)

```
# Create the host-only network (gives you vboxnet0) and set the host's IP
VBoxManage hostonlyif create
VBoxManage hostonlyif ipconfig vboxnet0 --ip 192.168.56.1 --netmask 255.255.255.0

# Disable VirtualBox's host-only DHCP so it doesn't fight your static IPs
VBoxManage dhcpserver remove --ifname vboxnet0
```

---

## 1 - MISP VM

### 1.1 - Importing the base VM

You can download an Ubuntu Server 24.04 `.ova` from here:
* https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.ova

1. Import the appliance into Oracle Virtual Box by going to `File` -> `Import Appliance`.

    ![Import OVA Appliance](images/misp-import-ova-appliance.png)


2. Go to _Settings_ and change the name of the VM to `misp` and set the RAM to 4096 MB:
    ![](images/misp-vm-settings.png)

3. Click on _Finish_.

### 1.2 - Networking

Attach the two adapters to the `misp` VM (powered off):
```
$ VBoxManage modifyvm "misp" --nic1 nat --nic2 hostonly --hostonlyadapter2 vboxnet0
```

Set `root` password:
```
sudo virt-customize -a /home/lucho/VirtualBox\ VMs/misp/ubuntu-noble-24.04-cloudimg.vdi \
      --root-password password:root \
      --run-command 'usermod -U root'
```

Configure ssh:

```
# vim /etc/ssh/sshd_config.d/99-enable-pw.conf
```
Add:
```
PasswordAuthentication yes
PermitRootLogin yes
```

Restart ssh:
```
systemctl restart ssh
```

Change hostname to `misp`:
```
echo "misp" > /etc/hostname
```

Cofigure static IP address:

```
root@ubuntu:~# vim /etc/netplan/99-lab.yaml
```

Write the following configuration:
```
network:
  version: 2
  ethernets:
    enp0s3:                 # NAT — internet
      dhcp4: true
    enp0s8:                 # host-only — lab traffic
      dhcp4: false
      addresses:
        - 192.168.56.30/24
```

Apply configuration:
```
chmod 600 /etc/netplan/99-lab.yaml
netplan apply
ip a show enp0s8            # confirm 192.168.56.30
```

### 1.3 - Installing `misp-docker`

0. Install `docker engine` and docker compose`:
    * https://docs.docker.com/engine/install/ubuntu/ 
    * https://docs.docker.com/compose/install/linux/

1. Grab just the compose file
```
mkdir misp && cd misp

curl -O https://raw.githubusercontent.com/MISP/misp-docker/refs/heads/master/docker-compose.yml
```
2. Create your .env 
```
curl -o .env https://raw.githubusercontent.com/MISP/misp-docker/refs/heads/master/template.env
```

3. Edit .env (see below)
```
vim .env

BASE_URL=https://192.168.56.30
ADMIN_EMAIL=admin@admin.test
ADMIN_PASSWORD=...                 # or use the generated default
```

4. PUll images and Start MISP
```
docker compose pull
docker compose up -d
```

Once the stack is up, MISP is reachable at `https://192.168.56.30`.

---

## 2 - Wazuh Manager VM

### 2.1 - Import Wazuh `.ova`

1. Download the `.ova` Wazuh virtual machine from:
    * https://documentation.wazuh.com/current/deployment-options/virtual-machine/virtual-machine.html

2. Import the appliance into Oracle Virtual Box by going to `File` -> `Import Appliance`.

    ![Import OVA appliance](images/wazuh-import-ova-appliance.png)

3. Go to _Settings_ and change the name of the VM to `wazuh-manager`:
    ![](images/wazuh-manager-vm-settings.png)

4. Click on _Finish_.

### 2.2 - Networking

Attach the two adapters to the `wazuh-manager` VM (powered off):
```
$ VBoxManage modifyvm "wazuh-manager" --nic1 nat --nic2 hostonly --hostonlyadapter2 vboxnet0
```

Get interfaces mac addresses:
```
$ VBoxManage showvminfo "wazuh-manager" | grep -i "host-only\|nic"
NIC 1:                       MAC: 0800272778B9, Attachment: NAT, Cable connected: on, Trace: off (file: none), Type: 82545EM, Reported speed: 0 Mbps, Boot priority: 0, Promisc Policy: deny, Bandwidth group: none
NIC 1 Settings:
NIC 2:                       MAC: 080027CE133C, Attachment: Host-only Interface 'vboxnet0', Cable connected: on, Trace: off (file: none), Type: 82540EM, Reported speed: 0 Mbps, Boot priority: 0, Promisc Policy: deny, Bandwidth group: none
```


Delete exisiting eth0 conf:
```
rm /etc/systemd/network/20-eth0.network
```

Modify `nat` config to match the mac address of the NAT interface:

`/etc/systemd/network/20-nat.network`: 
```
[Match]
MACAddress=08:00:27:27:78:B9

[Network]
DHCP=yes
```

Modify `hostonly` config to match the mac address of the Host-only interface:

`/etc/systemd/network/20-hostonly.network`: 
```
[Match]
MACAddress=08:00:27:CE:13:3C

[Network]
Address=192.168.56.10/24
```


Restart the network service:
```
sudo networkctl reload
sudo networkctl reconfigure eth0 eth1     # or just: systemctl restart systemd-networkd
ip -br addr                          # confirm 192.168.56.10 is now on the 08:00:27:ce:13:3c interface
```

---

## 3 - Wazuh Agent host (Ubuntu Server)

You can download an Ubuntu Server 24.04 `.ova` from here:
* https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.ova

Impor the appliance in Oracle Virtual Box following the same steps as before.

### 3.1 - Networking

1. Set Ubuntu Server root password:
    ```
    $ sudo apt install libguestfs-tools -y
    ...
    $ sudo virt-customize -a /home/lucho/VirtualBox\ VMs/wazuh-agent-01/ubuntu-noble-24.04-cloudimg.vdi \
      --root-password password:root \
      --run-command 'usermod -U root'
    [   0.0] Examining the guest ...
    [  24.0] Setting a random seed
    [  24.1] Running: usermod -U root
    [  24.2] Setting passwords
    [  24.9] SELinux relabelling
    [  25.0] Finishing off
    ```
2. Configure ssh:

```
# vim /etc/ssh/sshd_config.d/99-enable-pw.conf
```
Add:
```
PasswordAuthentication yes
PermitRootLogin yes
```

Restart ssh:
```
systemctl restart ssh
```

Change hostname to `wazuh-agent-01`:
```
echo "wazuh-agent-01" > /etc/hostname
```

Cofigure static IP address:

```
root@ubuntu:~# vim /etc/netplan/99-lab.yaml
```

Attach Host-only interface:
```
$ VBoxManage modifyvm "wazuh-agent-01" --nic2 hostonly --hostonlyadapter2 vboxnet0
```

Write the following configuration:
```
network:
  version: 2
  ethernets:
    enp0s3:                 # NAT — internet
      dhcp4: true
    enp0s8:                 # host-only — lab traffic
      dhcp4: false
      addresses:
        - 192.168.56.20/24
```

Apply configuration:
```
chmod 600 /etc/netplan/99-lab.yaml
netplan apply
ip a show enp0s8            # confirm 192.168.56.20
```

### 3.2 - Install the Wazuh Agent

1. Login via ssh:
```
# ssh root@192.168.56.20
...
root@wazuh-agent-01:~#
```
2. Install _Wazuh Agent_:
```
apt-get install gnupg apt-transport-https
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import && chmod 644 /usr/share/keyrings/wazuh.gpg
echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | tee -a /etc/apt/sources.list.d/wazuh.list
apt-get update
```

```
WAZUH_MANAGER="192.168.56.10" apt-get install wazuh-agent
```

> Replace `192.168.56.10` with your _Wazuh Manager_ IP.

> To change the IP address of the _Wazuh Manager_ after the agent installation, edit the `/var/ossec/etc/ossec.conf` configuration file.

More info:
* https://documentation.wazuh.com/current/installation-guide/wazuh-agent/wazuh-agent-package-linux.html

---

## 4 - Wazuh <-> MISP integration script installation

1. Pull the integration script into the Wazuh integrations directory
```
sudo curl -fsSL https://raw.githubusercontent.com/wazuh/integrations/refs/heads/main/integrations/misp/custom-misp.py \
  -o /var/ossec/integrations/custom-misp.py
```
2. Set ownership and permissions on the script
```
sudo chown root:wazuh /var/ossec/integrations/custom-misp.py
sudo chmod 750 /var/ossec/integrations/custom-misp.py
```
3. Create the log directory the script writes to and hand it to wazuh
```
sudo mkdir -p /var/log/wazuh-misp
sudo chown wazuh:wazuh /var/log/wazuh-misp
```
