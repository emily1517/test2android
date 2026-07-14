#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET
import re

def parse_dump(xml_path):
    tree = ET.parse(xml_path)
    return tree.getroot()

def get_bounds_center(node):
    bounds = node.get('bounds')
    if not bounds:
        return None
    m = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
    if m:
        x = (int(m.group(1)) + int(m.group(3))) // 2
        y = (int(m.group(2)) + int(m.group(4))) // 2
        return f"{x} {y}"
    return None

def find_node(root, **kwargs):
    for node in root.iter():
        match = True
        for k, v in kwargs.items():
            if k == 'text' and v.lower() not in (node.get('text') or '').lower():
                match = False
            elif k == 'resource_id' and node.get('resource-id') != v:
                match = False
            elif k == 'class' and node.get('class') != v:
                match = False
        if match:
            center = get_bounds_center(node)
            if center:
                return center
    return None

def find_profile_button(root):
    return find_node(root, text="already have") or find_node(root, text="I already have a profile")

def find_email_field(root):
    return (find_node(root, resource_id="com.facebook.katana:id/login_username") or
            find_node(root, class_="android.widget.EditText"))

def find_password_field(root):
    edits = [get_bounds_center(n) for n in root.iter() if n.get('class') == 'android.widget.EditText']
    return edits[1] if len(edits) >= 2 else (edits[0] if edits else None)

def get_editcount(root):
    return str(sum(1 for n in root.iter() if n.get('class') == 'android.widget.EditText'))

def get_field_value(root, idx=0):
    texts = [n.get('text') or '' for n in root.iter() if n.get('class') == 'android.widget.EditText']
    return texts[idx] if len(texts) > idx else ''

def find_login_button(root):
    for t in ["Log in", "Login", "Sign in", "Continue"]:
        c = find_node(root, text=t)
        if c:
            return c
    return find_node(root, class_="android.widget.Button")

def main():
    xml_path = sys.argv[1]
    cmd = sys.argv[2]
    root = parse_dump(xml_path)

    if cmd == "editcount":
        print(get_editcount(root))
    elif cmd == "email_field":
        print(find_email_field(root) or "")
    elif cmd == "password_field":
        print(find_password_field(root) or "")
    elif cmd == "login_button":
        print(find_login_button(root) or "")
    elif cmd == "profile_button":
        print(find_profile_button(root) or "")
    elif cmd == "field_value":
        print(get_field_value(root, int(sys.argv[3]) if len(sys.argv) > 3 else 0))
    elif cmd == "dump_text_summary":
        texts = [n.get('text') or n.get('content-desc') or '' for n in root.iter() if n.get('text') or n.get('content-desc')]
        print("\n".join(texts[:100]))
    else:
        print("Unknown command")

if __name__ == "__main__":
    main()
