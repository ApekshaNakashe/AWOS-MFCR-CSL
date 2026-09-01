
import win32security
import ntsecuritycon as con

import subprocess
import os

def unlock_file(path):
    
    if not os.path.isfile(path):
        return

    print("UNLOCK:", path)

    sd = win32security.GetFileSecurity(
        path,
        win32security.DACL_SECURITY_INFORMATION
    )

    win32security.SetFileSecurity(
        path,
        win32security.DACL_SECURITY_INFORMATION |
        win32security.UNPROTECTED_DACL_SECURITY_INFORMATION,
        sd
    )

    print("UNLOCKED")
def lock_file(path):
    if not os.path.isfile(path):
        return

    print("LOCK:", path)

    # Security descriptor
    sd = win32security.SECURITY_DESCRIPTOR()

    # SIDs
    system_sid, _, _ = win32security.LookupAccountName("", "SYSTEM")
    admin_sid, _, _ = win32security.LookupAccountName("", "Administrators")
    everyone_sid, _, _ = win32security.LookupAccountName("", "Everyone")

    # New ACL
    dacl = win32security.ACL()

    # SYSTEM - Full Control
    dacl.AddAccessAllowedAceEx(
        win32security.ACL_REVISION_DS,
        0,
        con.FILE_ALL_ACCESS,
        system_sid
    )

    # Administrators - Full Control
    dacl.AddAccessAllowedAceEx(
        win32security.ACL_REVISION_DS,
        0,
        con.FILE_ALL_ACCESS,
        admin_sid
    )

    # Everyone - Read Only
    dacl.AddAccessAllowedAceEx(
        win32security.ACL_REVISION_DS,
        0,
        con.FILE_GENERIC_READ |
        con.FILE_READ_ATTRIBUTES |
        con.FILE_READ_EA |
        con.SYNCHRONIZE,
        everyone_sid
    )

    sd.SetSecurityDescriptorDacl(True, dacl, False)

    win32security.SetFileSecurity(
        path,
        win32security.DACL_SECURITY_INFORMATION |
        win32security.PROTECTED_DACL_SECURITY_INFORMATION,
        sd
    )

    print("LOCKED")