#!/usr/bin/env python

import os
import os.path

dmi_vendor_table = ["KVM",  "QEMU", "VMware", "VMW",
                    "innotek GmbH", "Xen", "Bochs", "Parallels", "BHYVE"]


def detect_vm_dmi():
    dmi_vendors = ['product_name', 'sys_vendor', 'board_vendor', 'bios_vendor']
    sysfs_dmi_path = "/sys/class/dmi/id/"
    for i in range(len(dmi_vendors)):
        dmi_file = os.path.join(sysfs_dmi_path, dmi_vendors[i])
        if obtainer(dmi_file):
            element = reader(dmi_file)
            if element in dmi_vendor_table:
                print "Virtualization found in DMI:", element
    return None


def obtainer(path):
    if os.path.exists(path):
        return True
    return False


def reader(file):
    try:
        with open(file) as f:
            return f.read().strip()
    except IOError as e:
        e.filename


def detect_vm_xen():
    xen_file = '/proc/xen/capabilitie'
    if obtainer(xen_file):
        print "Virtualization XEN found ({0} exists)".format(xen_file)
    return None


def detect_vm_hypervisor():
    hypervisor = "/sys/hypervisor/type"
    if obtainer(hypervisor):
        h = reader(hypervisor)
        print "Virtualization found in /sys/hypervisor/type"
        if h == 'xen':
            print 'VIRTUALIZATION_XEN'
        else:
            print 'VIRTUALIZATION_VM_OTHER'
    return None


def detect_vm_uml():
    proc = reader('/proc/cpuinfo')
    if 'vendor_id\t: User Mode Linux' in proc:
        print "UML virtualization found in /proc/cpuinfo"
    return None


def detect_vm_zvm():
    zvm = '/proc/sysinfo'
    if obtainer(zvm):
        z = reader(zvm)
        if 'z/VM' in z:
            print 'VIRTUALIZATION_ZVM'
        else:
            print 'VIRTUALIZATION_KVM'
    return None


def detect_vm_device_tree():
    tree = '/proc/device-tree/hypervisor/compatible'
    if obtainer(tree):
        print 'VIRTUALIZATION_QEMU'
    return None


if __name__ == '__main__':
    detect_vm_dmi()
    detect_vm_xen()
    detect_vm_hypervisor()
    detect_vm_device_tree()
    detect_vm_uml()
    detect_vm_zvm()
