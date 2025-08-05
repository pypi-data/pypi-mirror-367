#!/usr/bin/env python3
# File: LP-LoginParser.py

#In The Name of God

import re
import requests
import argparse
import json
from http import HTTPStatus
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin
import colorama
from colorama import Back as bg, Fore, Style, init
init(autoreset=True)

print(f"\n{bg.BLACK}{Fore.GREEN}LP-LoginParser{Style.RESET_ALL}\n\n")

def extract_login_payload(session, a):
    def vprint(msg):
        if a.verbose:
            print(msg)
    
    def dump_form_like(tag: Tag, index: int):
        """Pretty‐print a form-like container"""
        tag_name = tag.name
        action = tag.get("action", "").strip()
        method = tag.get("method", "GET").upper()

        heading = f"[*] {Fore.CYAN}Container{Style.RESET_ALL} #{index}: <{tag_name}"
        if tag_name == "form":
            heading += f" action='{bg.BLACK}{Fore.GREEN}{action}{Style.RESET_ALL}' method='{bg.BLACK}{Fore.GREEN}{method}{Style.RESET_ALL}'"
        print(f"\n{heading}")
        
        for inp in tag.find_all("input"):
            itype = inp.get("type", "").strip().lower()
            name  = inp.get("name", "").strip()
            value = inp.get("value", "")
            print(f"{bg.BLACK}{Fore.WHITE}<input type='{itype}' name='{name}' value='{value}'>")

    def verbose_dump_all(soup: BeautifulSoup):
        """Find all forms and pseudo-forms"""
        forms = soup.find_all("form")
        containers = []

        # Real forms
        for form in forms:
            containers.append(form)

        # Pseudo-forms
        pw_inputs = soup.find_all("input", {"type":"password"})
        seen = set()
        for pw in pw_inputs:
            parent = pw.find_parent()
            while parent and parent.name != "form":
                if len(parent.find_all("input")) >= 2:
                    if parent not in seen:
                        seen.add(parent)
                        containers.append(parent)
                    break
                parent = parent.find_parent()

        if not containers:
            vprint(f"\n[!] {Fore.YELLOW}No <form> tags or password‐based containers found.")
            return

        vprint(f"[*] {Fore.CYAN}[verbose] Dumping form‐like containers:")
        for i, container in enumerate(containers, 1):
            dump_form_like(container, i)

    # Fetch login page
    try:
        r = session.get(a.url, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"\n[!] {bg.RED}{Fore.WHITE}Error fetching URL: {e}")
        return None, None

    soup = BeautifulSoup(r.text, "html.parser")
    
    if a.verbose:
        verbose_dump_all(soup)

    # Form detection logic
    formtype = "Not Detected"
    login_forms = []
    forms = soup.find_all("form")

    for form in forms:
        input_tags = form.find_all("input")
        input_types = [inp.get("type", "").lower() for inp in input_tags]
        if "password" in input_types and any(t in input_types for t in ["text", "email", "hidden", "number"]):
            login_forms.append(form)
            formtype = "<Form>"



    
    # Fallback detection
    if not login_forms:
        pw_input = soup.find("input", {"type": "password"})
        if pw_input:
            container = pw_input.find_parent(["form", "div", "section", "dialog", "article", "aside", "main"])
            if container and len(container.find_all("input")) < 2:
                container = container.find_parent(["form", "div", "section", "dialog", "article", "aside", "main"])
            if container and len(container.find_all("input")) >= 2:
                vprint(f"\n[*] {Fore.YELLOW}Fallback: Using container with password input")
                formtype = "<div>/<section>/<main>"
                login_forms = [container]

    # Sibling fallback
    if not login_forms:
        pw_input = soup.find("input", {"type": "password"})
        user_input = soup.find("input", {"type": lambda x: x in ["text", "email", "number"]})
        if pw_input and user_input:
            pw_parent = pw_input.find_parent(["div", "section", "dialog", "article", "aside", "main"])
            user_parent = user_input.find_parent(["div", "section", "dialog", "article", "aside", "main"])

            # Find common ancestor
            common = None
            if pw_parent and user_parent:
                current = pw_parent
                while current:
                    if current == user_parent or current.find(user_parent.name):
                        common = current
                        break
                    current = current.find_parent(["div", "section", "dialog", "article", "aside", "main"])
            if common:
                vprint(f"\n[*] {Fore.YELLOW}Split-input fallback: Using common ancestor")
                formtype = "split inputs (merged ancestor)"
                login_forms = [common]

    # Sibling containers fallback
    if not login_forms:
        pw_input = soup.find("input", {"type": "password"})
        if pw_input:
            pw_parent = pw_input.find_parent(["div", "section", "article", "aside", "main"])
            if pw_parent:
                sibling_candidates = [pw_parent]
                prev_siblings = pw_parent.find_previous_siblings()
                next_siblings = pw_parent.find_next_siblings()

                for sibling in list(prev_siblings) + list(next_siblings):
                    if sibling and sibling.find("input", {"type": lambda x: x in ["text", "email", "number"]}):
                        sibling_candidates.append(sibling)

                if len(sibling_candidates) > 1:
                    synthetic_html = ''.join(str(tag) for tag in sibling_candidates)
                    synthetic_soup = BeautifulSoup(synthetic_html, "html.parser")
                    vprint(f"\n[*] {Fore.YELLOW}Sibling fallback: Inputs in sibling containers")
                    formtype = "split layout (inputs in sibling blocks)"
                    login_forms = [synthetic_soup]

    if not login_forms:
        print(f"[!] {bg.RED}{Fore.WHITE}Login form not detected")
        return None, None

    # Process first valid form
    form = login_forms[0]
    action = form.get("action") if form.name == "form" else None
    actionurl = urljoin(a.url, action) if action else a.url

    if not action:
        print(f"\n[-] {Fore.YELLOW}Warning: No form action - using -> {bg.BLACK}{Fore.WHITE}[{a.url}]")
    elif not actionurl.startswith("http"):
        print(f"\n[-] {Fore.YELLOW}Warning: Suspicious action URL -> {bg.BLACK}{Fore.WHITE}[{actionurl}]")

    # Build payload
    payload = {}
    for input_tag in form.find_all("input"):
        name = input_tag.get("name")
        if not name: continue
        
        t = input_tag.get("type", "").lower()
        if t in ["text", "email", "number"]:
            payload[name] = a.username
        elif t == "password":
            payload[name] = a.password
        elif t == "submit":
            payload[name] = input_tag.get("value", "Login")
        elif t == "hidden" or "csrf" in name.lower():
            payload[name] = input_tag.get("value", "")
    if a.verbose:
        print(f"\n\n[+] {Fore.CYAN}Detected{Style.RESET_ALL} login form action URL: {bg.BLACK}{Fore.WHITE}[{actionurl}]")
        print(f"\n\n[+] {Fore.CYAN}Detected{Style.RESET_ALL} login fields: {bg.BLACK}{Fore.WHITE}{payload}")
        print(f"\n\n[+] {Fore.CYAN}Detected{Style.RESET_ALL} login form structure: {bg.BLACK}{Fore.WHITE}{formtype}{Style.RESET_ALL}\n")
    
    return payload, actionurl

def main(a):
    
    session = requests.Session()
    
    # Set headers and cookies
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    cookies = {}
    
    if a.header:
        for h in a.header:
            k, v = h.split(":", 1)
            headers[k.strip()] = v.strip()
    if a.cookie:
        for c in a.cookie:
            k, v = c.split("=", 1)
            cookies[k.strip()] = v.strip()
    
    session.headers.update(headers)
    session.cookies.update(cookies)

    # Extract and submit login form
    payload, actionurl = extract_login_payload(session, a)
    if not payload:
        return

    try:
        r = session.post(actionurl, data=payload)
        print(f"\nLogin status: {bg.BLACK}{Fore.WHITE}{r.status_code} {HTTPStatus(r.status_code).phrase}{Style.RESET_ALL}")
        
        # Check login success
        failed_keywords = ["invalid", "incorrect", "try again", "sign in", "login failed"]
        success_keywords = ["sign off", "account summary", "welcome", "recent transactions"]
        page_content = r.text.lower()
        
        if any(kw in page_content for kw in failed_keywords):
            print(f"[!] Login {Fore.RED}Failed")
        elif any(kw in page_content for kw in success_keywords):
            print(f"[+] Login {Fore.CYAN}Successful{Style.RESET_ALL}")
        else:
            print(f"\n[-] {Fore.YELLOW}Login status uncertain")

        # Save session to file
        session_data = {
            "cookies": session.cookies.get_dict(),
            "headers": dict(session.headers)
        }
        
        with open(a.session_file, "w") as f:
            json.dump(session_data, f)
            
        print(f"\n\n{bg.BLACK}{Fore.WHITE}Session saved to: [{a.session_file}]")

    except Exception as e:
        print(f"[!] {bg.RED}{Fore.WHITE}Login failed: {e}")

def cli_main():
        p = argparse.ArgumentParser(description="Extract and submit login forms")
        p.add_argument("-u", "--url", required=True, help="Login page URL")
        p.add_argument("-un", "--username", default="admin", help="Username")
        p.add_argument("-pw", "--password", default="admin", help="Password")
        p.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
        p.add_argument("-ck", "--cookie", nargs="*", help="Cookies (key=value)")
        p.add_argument("-hd", "--header", nargs="*", help="Headers (key:value)")
        p.add_argument("-s", "--session-file", default="session.json", help="Session output file")
    
        args = p.parse_args()
        main(args)


if __name__ == "__main__":
    cli_main()
