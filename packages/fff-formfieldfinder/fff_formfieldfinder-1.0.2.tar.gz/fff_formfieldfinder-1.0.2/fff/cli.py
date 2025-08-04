# In The Name of God


import argparse
from re import S
from bs4 import BeautifulSoup, Tag
import requests
from urllib.parse import urljoin
import colorama
from colorama import Back as bg, Fore, Style, init
init(autoreset=True)


def vprint(msg, a):
    if getattr(a, "verbose", False):
        print(msg)

def dump_form_like(tag: Tag, index: int):
    """
    Pretty‐print a <form> or any container that
    looks like a login form (password + at least one more input).
    """
    tag_name = tag.name
    action = tag.get("action", "").strip()
    method = tag.get("method", "GET").upper()

    heading = f"{Fore.CYAN}Container{Style.RESET_ALL} #{index}: <{tag_name}"
    if tag_name == "form":
        heading += f" action='{bg.BLACK}{Fore.GREEN}{action}{Style.RESET_ALL}' method='{bg.BLACK}{Fore.GREEN}{method}{Style.RESET_ALL}'"
    heading += ">"

    print(f"\n{heading}")
    for inp in tag.find_all("input"):
        itype = inp.get("type", "").strip().lower()
        name  = inp.get("name", "").strip()
        value = inp.get("value", "")
        print(f"{bg.BLACK}{Fore.WHITE}<input type='{itype}' name='{name}' value='{value}'>")


def verbose_dump_all(soup: BeautifulSoup):
    """
    Find all real <form> tags plus any
    pseudo‐forms (containers with password+other inputs)
    """
    forms = soup.find_all("form")
    containers = []

    # 1) every real <form>
    for form in forms:
        containers.append(form)

    # 2) every other tag that has a password input
    #    AND at least one other input
    pw_inputs = soup.find_all("input", {"type":"password"})
    seen = set()
    for pw in pw_inputs:
        parent = pw.find_parent()
        # climb until you hit <form> or the document root
        while parent and parent.name != "form":
            # if it has at least two inputs, count it
            if len(parent.find_all("input")) >= 2:
                if parent not in seen:
                    seen.add(parent)
                    containers.append(parent)
                break
            parent = parent.find_parent()

    if not containers:
        print(f"\n{Fore.YELLOW}[verbose] No <form> tags or password‐based containers found.")
        return

    print(f"\n{Fore.CYAN}[verbose] Dumping form‐like containers (real forms first):")
    for i, container in enumerate(containers, 1):
        dump_form_like(container, i)



def extract_login_payload(a):

    formtype = "Not Detected"

    print(f"\n{bg.BLACK}{Fore.GREEN}FFF - Form Field Finder")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "no-cache"
        }
        if a.header:
            for h in a.header:
                k, v = h.split(":", 1)
                headers[k.strip()] = v.strip()
        cookies = {}
        if a.cookie:
            for c in a.cookie:
                k, v = c.split("=", 1)
                cookies[k.strip()] = v.strip()
        
        r = requests.get(a.url,cookies=cookies, headers=headers, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"\n{bg.RED}{Fore.WHITE}Error fetching URL: {e}")
        return

    soup = BeautifulSoup(r.text, "html.parser")

    forms = soup.find_all("form")
    

    if a.verbose:
        verbose_dump_all(soup)

    login_forms = []

    for form in forms:
        input_tags = form.find_all("input")
        input_types = [inp.get("type", "").lower() for inp in input_tags]

        if "password" in input_types and any(t in input_types for t in ["text", "email", "hidden", "number"]):
            login_forms.append(form)
            formtype = "<Form>"

    # Main fallback block
    if not login_forms:
        pw_input = soup.find("input", {"type": "password"})
        if pw_input:
            # Traverse up through <div>, <section>, <dialog>, <article>, <aside>, <main>
            container = pw_input.find_parent(["form", "div", "section", "dialog", "article", "aside", "main"])

            # Traverse up once more if too shallow (e.g. <input> inside <label> inside <div>)
            if container and len(container.find_all("input")) < 2:
                container = container.find_parent(["form", "div", "section", "dialog", "article", "aside", "main"])

            # Ensure it's still a valid container with multiple inputs
            if container and len(container.find_all("input")) >= 2:
                vprint(f"\n\n{Fore.YELLOW}Fallback mode{Style.RESET_ALL}: Using nearest container with <input type='password'>", a)
                vprint(f"\n\nTag={bg.BLACK}{Fore.WHITE}{container.name}{Style.RESET_ALL}, inputs={bg.BLACK}{Fore.WHITE}{[inp.get('name') for inp in container.find_all('input')]}{Style.RESET_ALL}", a)
                
                formtype = "<div>/<section>/<main>"

                login_forms = [container]
    
        # Split-parents fallback
        if not login_forms:
            pw_input = soup.find("input", {"type": "password"})
            user_input = soup.find("input", {"type": lambda x: x in ["text", "email", "number"]})
            if pw_input and user_input:
                pw_parent = pw_input.find_parent(["div", "section", "dialog", "article", "aside", "main"])
                user_parent = user_input.find_parent(["div", "section", "dialog", "article", "aside", "main"])

                # Use a common ancestor if possible
                common = None
                if pw_parent and user_parent:
                    current = pw_parent
                    while current:
                        if current == user_parent or current.find(user_parent.name):
                            common = current
                            break
                        current = current.find_parent(["div", "section", "dialog", "article", "aside", "main"])
                if common:
                    vprint(f"\n{bg.YELLOW}{Fore.BLACK}Split-input fallback: username and password in separate containers.", a)
                    vprint(f"\nTag={bg.BLACK}{Fore.WHITE}{common.name}{Style.RESET_ALL}, inputs={bg.BLACK}{Fore.WHITE}{[inp.get('name') for inp in common.find_all('input')]}", a)
                    
                    formtype = "split inputs (merged ancestor)"

                    login_forms = [common]

        # Sibling fallback
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

                        vprint(f"\n{bg.YELLOW}{Fore.BLACK}Sibling fallback: Inputs split across sibling containers.", a)
                        vprint(f"\nTag={bg.BLACK}{Fore.WHITE}SYNTHETIC{Style.RESET_ALL}, inputs={bg.BLACK}{Fore.WHITE}{[inp.get('name') for inp in synthetic_soup.find_all('input')]}", a)
                        
                        formtype = "split layout (inputs in sibling blocks)"

                        login_forms = [synthetic_soup]


    if not login_forms:
        raise Exception(f"\n{bg.RED}{Fore.WHITE}Login form not found — no <form> or <input type='password'> detected")

    for form in login_forms:
        action = form.get("action") if form.name == "form" else None
        actionurl = urljoin(a.url, action) if action else a.url

        if not action:
            print(f"\n\n{Fore.YELLOW}Warning:{Style.RESET_ALL} Form has no action — assuming {bg.BLACK}{Fore.WHITE}[{a.url}]")
        elif not actionurl.startswith("http"):
            print(f"\n\n{Fore.YELLOW}Warning:{Style.RESET_ALL} Suspicious action URL → {bg.BLACK}{Fore.WHITE}[{actionurl}]")
        else:
            print(f"\n\n{Fore.CYAN}Detected{Style.RESET_ALL} login form action URL: {bg.BLACK}{Fore.WHITE}[{actionurl}]")

        payload = {}
        for input_tag in form.find_all("input"):
            name = input_tag.get("name")
            if not name:
                continue

            t = input_tag.get("type", "").lower()
            if t in ["text", "email", "number"]:
                payload[name] = a.username
            elif t == "password":
                payload[name] = a.password
            elif t == "submit":
                payload[name] = input_tag.get("value", "Login")
            elif t == "hidden":
                payload[name] = input_tag.get("value", "")
            elif "csrf" in name.lower():
                payload[name] = input_tag.get("value", "")

        print(f"\n\n{Fore.CYAN}Detected{Style.RESET_ALL} login fields: {bg.BLACK}{Fore.WHITE}{payload}")
        
        print(f"\n\n{Fore.CYAN}Detected{Style.RESET_ALL} Login form structure: {bg.BLACK}{Fore.WHITE} {formtype}")
        
        vprint("", a)
        
        return payload

def main():
    p = argparse.ArgumentParser(description="FFF - Form Field Finder: Extracts login form fields and action URL for fuzzing tools like ffuf/wfuzz.")
    p.add_argument("-u", "--url", metavar="", required=True, help="Input Target URL")
    p.add_argument("-un", "--username", metavar="", default="admin", help="Username to use in the login payload")
    p.add_argument("-pw", "--password", metavar="", default="admin", help="Password to use in the login payload")
    p.add_argument("-v", "--verbose", action="store_true", help="Enable verbose debug output")
    p.add_argument("-ck", "--cookie", metavar="K=V", nargs="*", help="Add cookies to the request (format: key=value)")
    p.add_argument("-hd", "--header", metavar="K:V", nargs="*", help="Add custom headers to the request (format: key:value)")
    
    a = p.parse_args()

    extract_login_payload(a)



if __name__ == "__main__":
    main()
