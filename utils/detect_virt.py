#!/usr/bin/env python

import os

dmi_vendor_table = [
    "KVM",
    "QEMU",
    "VMware",
    "VMW",
    "innotek GmbH",
    "Xen",
    "Bochs",
    "Parallels",
    "BHYVE"
]


def detect_vm_dmi():
    dmi_vendors = ['product_name', 'sys_vendor', 'board_vendor', 'bios_vendor']
    for dmi_vendor in dmi_vendors:
        dmi_file = os.path.join("/sys/class/dmi/id/", dmi_vendor)
        if not os.path.exists(dmi_file):
            continue
        with open(dmi_file) as dmi_fd:
            dmi_data = dmi_fd.read()
            if dmi_data in dmi_vendor_table:
                return dmi_data


def detect_vm_hypervisor():
    hypervisor = "/sys/hypervisor/type"
    if os.path.exists(hypervisor):
        with open(hypervisor) as hypervisor_fd:
            return hypervisor_fd.read()


def detect_vm_uml():
    with open('/proc/cpuinfo') as cpuinfo:
        if 'vendor_id\t: User Mode Linux' in cpuinfo.read():
            return "UML"


def detect_vm_zvm():
    zvm = '/proc/sysinfo'
    if os.path.exists(zvm):
        with open(zvm) as zvm_fd:
            return "ZVM" if 'z/VM' in zvm_fd.read() else "KVM"


def detect_by_file(filename, vm):
    if os.path.exists(filename):
        return vm


def main():
    checks = (
        detect_by_file('/proc/xen/capabilitie', "XEN"),
        detect_by_file('/proc/device-tree/hypervisor/compatible', 'QEMU'),
        detect_vm_zvm(),
        detect_vm_uml(),
        detect_vm_hypervisor(),
        detect_vm_dmi()
    )
    if any(checks):
        print checks
        return 1

if __name__ == '__main__':
    main()
