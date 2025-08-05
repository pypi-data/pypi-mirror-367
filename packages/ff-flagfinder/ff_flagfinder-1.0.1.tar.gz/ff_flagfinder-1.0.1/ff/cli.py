#In The Name of God


#!/usr/bin/env python3
# File: FF-FlagFinder.py

"""
Grab flag from authenticated CTF page
Usage:
    $ python3 FF-FlagFinder.py -fu https://target.com/flag -f CTF{FLAG} 
    $ python3 FF-FlagFinder.py -fu https://target.com/flag -f CTF{FLAG} -s session.json
    $ python3 FF-FlagFinder.py -fu https://target.com/flag -f CTF{FLAG} -ck sessionid=abcd
"""

import requests
import argparse
import re
import json
import colorama
from colorama import Back as bg, Fore, Style, init
init(autoreset=True)


def parse_args():
    parser = argparse.ArgumentParser(description="Grab CTF flag from authenticated page")
    parser.add_argument("-fu", "--flagurl", metavar="", required=True, help="Flag page URL")
    parser.add_argument("-f", "--flag", metavar="", help="Flag")
    parser.add_argument("-o", "--output", metavar="", default="flag.txt", help="Name of the output file")
    parser.add_argument("-ck", "--cookie", metavar="", nargs="*", help="Cookies (key=value)")
    parser.add_argument("-hd", "--header", metavar="", nargs="*", help="Headers (key:value)")
    parser.add_argument("-s", "--session", metavar="", help=".json Session file")
    parser.add_argument("-r", "--regex", action="store_true", help="Treat -f as a regex pattern")
    
    return parser.parse_args()

def parse_kv_args(items):
    result = {}
    if items:
        for item in items:
            if "=" in item:
                k, v = item.split("=", 1)
                result[k.strip()] = v.strip()
            elif ":" in item:
                k, v = item.split(":", 1)
                result[k.strip()] = v.strip()
    return result

def load_session(file_path):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return data.get("cookies", {}), data.get("headers", {})
    except:
        return {}, {}

def grab_flag():
    print(f"\n{bg.BLACK}{Fore.GREEN}FF-FlagFinder{Style.RESET_ALL}\n\n")
    
    args = parse_args()
    cookies = parse_kv_args(args.cookie)
    headers = parse_kv_args(args.header)

    session_cookies, session_headers = {}, {}
    if args.session:
        session_cookies, session_headers = load_session(args.session)

    final_cookies = {**session_cookies, **cookies}
    final_headers = {**session_headers, **headers}

    try:
        r = requests.get(
            args.flagurl,
            cookies=final_cookies,
            headers=final_headers,
            timeout=10
        )
        r.raise_for_status()
    except Exception as e:
        print(f"{bg.RED}{Fore.WHITE}Request failed: {e}")
        return

    content = r.text
    found_flags = []

    with open("debug.html", "w", encoding="utf-8") as f:
        f.write(content)

    if args.flag:

        try:
            pattern = args.flag if args.regex else re.escape(args.flag)
            match = re.search(pattern, content, re.IGNORECASE)

            if match:
                print(f"\n[+] {bg.BLACK}{Fore.CYAN}SUCCESS: Flag found!{Style.RESET_ALL}")
                print(f"\n\n{bg.BLACK}{Fore.WHITE}Flag saved to: [{args.output}]")
                print(f"\n{bg.BLACK}{Fore.WHITE}Response content saved to: [debug.html]")
                with open(args.output, "w") as f:
                    f.write(match.group(0) + "\n")
                return
        except re.error as e:
            print(f"{bg.RED}{Fore.WHITE}[!] Invalid pattern: {e}{Style.RESET_ALL}\n")

        print(f"\n[!] {bg.RED}{Fore.WHITE}Flag not found{Style.RESET_ALL}:->{bg.BLACK}{Fore.WHITE}[{args.flag}]{Style.RESET_ALL}\n")
        print(f"\n{bg.BLACK}{Fore.WHITE}Response content saved to: [debug.html]")

    else:
        print(f"\n{Fore.YELLOW}[*] --flag not provided. Attempting automatic flag detection...{Style.RESET_ALL}")
        patterns = [r"FLAG{.*?}", r"CTF{.*?}", r"HTB{.*?}", r"picoCTF{.*?}", r"AKASEC{.*?}"]
        for pat in patterns:
            found_flags += re.findall(pat, content)

        if found_flags:
            print(f"\n{Fore.GREEN}[+] Flags Found:{Style.RESET_ALL}")
            for flag in set(found_flags):
                print(f"  - {flag}")
            with open(args.output, "w") as f:
                for flag in set(found_flags):
                    f.write(flag + "\n")
        else:
            print(f"\n{Fore.RED}[-] No flags detected automatically.{Style.RESET_ALL}")
            print(f"\n{bg.BLACK}{Fore.WHITE}Response content saved to: [debug.html]")


if __name__ == "__main__":
    grab_flag()
