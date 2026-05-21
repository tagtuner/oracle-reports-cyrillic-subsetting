# -*- coding: utf-8 -*-
"""
Oracle Reports uifont.ali Duplicate Headers Cleaner & Arial TrueType Subsetting Injector
Developed by tagtuner (GitHub Release)

This Python script solves the 'Duplicate [ PDF:Subset ] headers' trap in Oracle Reports configuration.
It comments out all occurrences of [ PDF:Subset ] and appends a single, clean, unified block at the
end of uifont.ali in both 'admin' and 'mesg' folders.
"""

import os
import re
import io

def clean_uifont(filepath, admin_path):
    print("Cleaning file: {0}".format(filepath))
    if not os.path.exists(filepath):
        print("Error: File not found: {0}".format(filepath))
        return

    with io.open(filepath, 'r', encoding='latin-1') as f:
        content = f.read()

    # 1. Comment out ALL occurrences of [ PDF:Subset ] (case-insensitive)
    content = re.sub(r'\[\s*PDF\s*:\s*Subset\s*\]', '# [ PDF:Subset ]', content, flags=re.IGNORECASE)

    # 2. Ensure Arial is mapped to courier in [ Global ]
    if '[ Global ]' in content:
        global_sec = re.search(r'(\[\s*Global\s*\])(.*?)(?=\[\s*\w+\s*\]|\Z)', content, re.DOTALL)
        if global_sec:
            sec_header = global_sec.group(1)
            sec_body = global_sec.group(2)
            
            if re.search(r'Arial\s*=\s*\w+', sec_body, re.IGNORECASE):
                new_sec_body = re.sub(r'Arial\s*=\s*\w+', 'Arial = courier', sec_body, flags=re.IGNORECASE)
                content = content.replace(global_sec.group(0), sec_header + new_sec_body)
                print("  -> Arial = courier set in [ Global ]")
            else:
                new_sec_body = sec_body + "\nArial = courier\n"
                content = content.replace(global_sec.group(0), sec_header + new_sec_body)
                print("  -> Arial = courier injected in [ Global ]")
    else:
        content = "[ Global ]\nArial = courier\n\n" + content
        print("  -> Created [ Global ] section at top")

    # 3. Append the single, clean [ PDF:Subset ] section at the very end of the file
    # Directs all Courier mappings to the physical arial TrueType files located in the admin folder
    subset_rules = """

[ PDF:Subset ]
Courier..Italic.Bold.. = "{admin}/arialbi.ttf"
Courier...Bold..       = "{admin}/arialbd.ttf"
Courier..Italic...     = "{admin}/ariali.ttf"
Courier.....           = "{admin}/arial.ttf"

courier..Italic.Bold.. = "{admin}/arialbi.ttf"
courier...Bold..       = "{admin}/arialbd.ttf"
courier..Italic...     = "{admin}/ariali.ttf"
courier.....           = "{admin}/arial.ttf"
""".format(admin=admin_path)

    content = content.strip() + "\n" + subset_rules + "\n"
    print("  -> Appended single, clean [ PDF:Subset ] to end of file")

    with io.open(filepath, 'w', encoding='latin-1') as f:
        f.write(content)

if __name__ == "__main__":
    # Specify your ORACLE_HOME absolute path here
    # Example: "/u01/oracle/PROD/fs2/EBSapps/10.1.2"
    oracle_home = os.environ.get("ORACLE_HOME", "/u01/oracle/PROD/fs2/EBSapps/10.1.2")
    
    admin_ali = os.path.join(oracle_home, "guicommon/tk/admin/uifont.ali")
    mesg_ali = os.path.join(oracle_home, "guicommon/tk/mesg/uifont.ali")
    admin_path = os.path.join(oracle_home, "guicommon/tk/admin")
    
    print("Detected ORACLE_HOME: {0}".format(oracle_home))
    clean_uifont(admin_ali, admin_path)
    clean_uifont(mesg_ali, admin_path)
    print("=== uifont.ali CLEANING COMPLETED SUCCESSFULLY ===")
