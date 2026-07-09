# MISP Integration Workshop — CIRCL - Importing the lab `.ova`

> This document covers importing the **pre-configured `.ova` image** for the workshop and
> lists the IP addresses and default credentials of each VM. The four VMs (`misp`,
> `wazuh-manager`, `wazuh-agent-01` and `flowintel`) come already installed, networked and
> ready to start.
>
> If you'd rather build the lab from scratch (base VM import, host-only network, static
> IPs, installing MISP and Wazuh), see [INSTALLATION.md](INSTALLATION.md). Once the VMs are
> up, continue with the main walkthrough in [TUTORIAL.md](TUTORIAL.md).

## Requirements

* [Oracle VirtualBox](https://www.virtualbox.org/) (with the `VBoxManage` CLI, which ships
  with it).
* Enough free resources for four VMs running at once — roughly **16 GB RAM** and
  **~60 GB disk** are comfortable.

## 1 - Download the `.ova`

Download the pre-configured lab image, `wazuh-misp-lab.ova`, which bundles all four VMs:

* **<TODO_INSERT_OVA_LINK>**

## 2 - Create the host-only network

The VMs use a host-only network (`vboxnet0`, `192.168.56.0/24`) for lab traffic. Create it
once **before** importing, and disable VirtualBox's host-only DHCP so it doesn't fight the
VMs' static IPs:

```bash
# Create the host-only network (gives you vboxnet0) and set the host's IP
VBoxManage hostonlyif create
VBoxManage hostonlyif ipconfig vboxnet0 --ip 192.168.56.1 --netmask 255.255.255.0

# Disable VirtualBox's host-only DHCP so it doesn't fight the static IPs
VBoxManage dhcpserver remove --ifname vboxnet0 2>/dev/null || true
```

## 3 - Import the appliance

Import all four VMs from the single `.ova`:

```bash
VBoxManage import wazuh-misp-lab.ova
```

Alternatively, use the VirtualBox GUI: `File` -> `Import Appliance`, select
`wazuh-misp-lab.ova`, and click `Finish`.

## 4 - Start the VMs

Open Oracle VirtualBox and power on the four VMs, or start them from the CLI:

```bash
VBoxManage startvm misp
VBoxManage startvm wazuh-manager
VBoxManage startvm wazuh-agent-01
VBoxManage startvm flowintel
```

> Give the `misp` and `wazuh-manager` VMs a minute or two after boot to bring their
> services (Docker stack / Wazuh indexer + dashboard) fully up before connecting.

## Lab layout — VM IP addresses

All VMs sit on the host-only network `192.168.56.0/24`:

```
192.168.56.1    the host itself (VirtualBox assigns this to vboxnet0)
192.168.56.10   wazuh-manager VM
192.168.56.20   wazuh-agent-01 VM
192.168.56.30   misp docker
192.168.56.50   flowintel VM
```

## Default credentials

> ⚠️ These are lab defaults for an isolated, offline environment. **Never** reuse them on
> anything exposed to a real network.

### SSH / VM console login

| VM | Address | User | Password |
|----|---------|------|----------|
| `misp` | `192.168.56.30` | `root` | `root` |
| `wazuh-manager` | `192.168.56.10` | `wazuh-user` | `wazuh` |
| `wazuh-agent-01` | `192.168.56.20` | `root` | `root` |
| `flowintel` | `192.168.56.50` | `root` | `root` |

### Web interfaces

| Service | URL | User | Password |
|---------|-----|------|----------|
| MISP | `https://192.168.56.30` | `admin@admin.test` | `admin` |
| Wazuh Dashboard | `https://192.168.56.10` | `admin` | `admin` |
| Flowintel | `http://192.168.56.50` | `admin@admin.admin` | `admin` |

> The MISP and Wazuh web UIs use self-signed TLS certificates — your browser will warn
> about them. This is expected for a local lab; accept the exception and continue.

## Next steps

With the VMs running and reachable, head to [TUTORIAL.md](TUTORIAL.md) to start the
walkthrough.
