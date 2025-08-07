#!/usr/bin/env python3

"""
╔═══════════════════════════════════════════════════════════════╗
║                           IPFindX                             ║
║                 Advanced IP Intelligence Toolkit              ║
║═══════════════════════════════════════════════════════════════║
║ Version     : 3.0.1                                           ║
║ Author      : Alex Butler                                     ║
║ Organization: Vritra Security Organization                    ║
║ GitHub      : https://github.com/VritraSecz/IPFindX           ║
║ License     : MIT License                                     ║
╚═══════════════════════════════════════════════════════════════╝
"""

import argparse
import json
import requests
import os
import datetime
import ipaddress
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme
from rich.text import Text

custom_theme = Theme({
    "info": "bold blue",
    "warning": "bold yellow",
    "danger": "bold red",
    "success": "bold green",
    "banner": "bold gold1",
    "field": "bold gold1",
    "value": "white",
    "about_title": "bold gold1",
    "connect_title": "bold gold1",
    "panel_border": "bold blue",
    "table_header": "bold gold1",
    "saved_path": "bold blue",
})

console = Console(theme=custom_theme)

def print_banner():
    ascii_banner = '''
██╗██████╗ ███████╗██╗███╗   ██╗██████╗ ██╗  ██╗
██║██╔══██╗██╔════╝██║████╗  ██║██╔══██╗╚██╗██╔╝
██║██████╔╝█████╗  ██║██╔██╗ ██║██║  ██║ ╚███╔╝ 
██║██╔═══╝ ██╔══╝  ██║██║╚██╗██║██║  ██║ ██╔██╗ 
██║██║     ██║     ██║██║ ╚████║██████╔╝██╔╝ ██╗
╚═╝╚═╝     ╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝
'''
    banner_width = max(len(line) for line in ascii_banner.splitlines())
    terminal_width = console.size.width

    if terminal_width < banner_width + 16:
        fallback_text = Text(justify="center")
        fallback_text.append("⚡ IPFindX ⚡\n", style="banner")
        fallback_text.append("v3.0.1 • Alex Butler\n", style="italic green")
        fallback_text.append("Vritra Security Organization\n", style="dim")
        fallback_text.append("Advanced IP Intelligence Toolkit\n", style="bold cyan")
        fallback_text.append("GitHub: github.com/VritraSecz/IPFindX", style="underline magenta")

        fallback = Panel(
            fallback_text,
            border_style="bold magenta",
            padding=(1, 2),
            title="[bold red]Mini Bannere[/bold red]",
            subtitle="[info]Narrow Terminal Detected[/info]",
        )
        console.print(fallback)
        print()
    else:
        panel = Panel(
            Text(ascii_banner, style="banner", justify="center"),
            title="[bold]IPFindX v3.0.1[/bold]",
            subtitle="[info]Developed by Alex Butler | Vritra Security Organization[/info]",
            border_style="panel_border",
            padding=(0, 2),
            width=max(len(line) for line in ascii_banner.splitlines()) + 16
        )
        console.print(panel)
        print()

def show_about():
    """Displays detailed information about the tool and author."""
    about_text = """
    [about_title]About IPFindX[/about_title]
    IPFindX is a powerful command-line tool for gathering detailed information about IP addresses. It is designed for security professionals, network administrators, and anyone interested in network intelligence.

    [about_title]Author[/about_title]
    Alex Butler | Vritra Security Organization
    """
    console.print(Panel(about_text, title="[bold]About[/bold]", border_style="panel_border"))

def show_connect():
    """Displays social media connection details."""
    connect_text = """
    [connect_title]Connect with Vritra Security[/connect_title]
    - GitHub:    https://github.com/VritraSecz
    - Instagram: https://instagram.com/haxorlex
    - YouTube:   https://youtube.com/@Technolex
    - Website:   https://vritrasec.com
    - Community: t.me/VritraSecz
    - Channel:   t.me/LinkCentralX
    - Main:      t.me/VritraSec
    """
    console.print(Panel(connect_text, title="[bold]Connect[/bold]", border_style="panel_border"))

def is_valid_ip(ip_str: str):
    """Checks if an IP address is public and valid."""
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        if ip_obj.is_private or ip_obj.is_reserved or ip_obj.is_loopback:
            console.print(Panel(f"[warning]The IP address '{ip_str}' is a private, reserved, or loopback address and cannot be scanned publicly.[/warning]", title="[bold]Invalid IP[/bold]", border_style="warning"))
            return False
        return True
    except ValueError:
        console.print(Panel(f"[danger]The IP address '{ip_str}' is not valid.[/danger]", title="[bold]Invalid IP[/bold]", border_style="danger"))
        return False

def get_ip_info(ip_address: str):
    """Fetches all available IP information from the API."""
    if not is_valid_ip(ip_address):
        return None

    url = f"http://ip-api.com/json/{ip_address}?fields=status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
    with console.status(f"[info]Fetching IP information for {ip_address}...[/info]"):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            console.print(Panel(f"[danger]Error fetching info for {ip_address}: {e}[/danger]", title="[bold]Network Error[/bold]", border_style="danger"))
            return None

def display_ip_info(data: dict):
    """Displays IP information in a table."""
    if not data:
        return

    status = data.get("status", "fail")
    if status == "fail":
        console.print(Panel(f"[danger]Could not retrieve information for IP: {data.get('query')}[/danger]", title="[bold]Error[/bold]", border_style="danger"))
        return

    table = Table(title=f"[bold]IP Details for {data.get('query')}[/bold]", show_header=True, header_style="table_header", border_style="panel_border")
    table.add_column("Field", style="field", width=25)
    table.add_column("Value", style="value")

    for key, value in data.items():
        if key == "status":
            status_color = "success" if value == "success" else "danger"
            table.add_row(f"• {key.replace('_', ' ').title()}", f"[{status_color}]{value}[/{status_color}]")
        else:
            table.add_row(f"• {key.replace('_', ' ').title()}", str(value))

    console.print(table)

    lat = data.get("lat")
    lon = data.get("lon")
    if lat and lon:
        maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        console.print(Panel(f"[info]View on Google Maps:[/info] [saved_path]{maps_link}[/saved_path]", title="[bold]Location[/bold]", border_style="panel_border"))

def save_output_auto(data: dict):
    """Saves the IP information automatically to a timestamped file."""
    if not data or data.get("status") == "fail":
        return

    output_dir = "output-ipfindx"
    os.makedirs(output_dir, exist_ok=True)

    ip_address = data.get("query", "unknown_ip")
    timestamp = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")
    filename = os.path.join(output_dir, f"{ip_address}-{timestamp}.json")

    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        console.print(Panel(f"[success]Output saved to:[/success] [saved_path]{filename}[/saved_path]", title="[bold]File Saved[/bold]", border_style="success"))
    except IOError as e:
        console.print(Panel(f"[danger]Error saving file: {e}[/danger]", title="[bold]File Error[/bold]", border_style="danger"))

def scan_ip_list(filepath: str):
    """Scans a list of IPs from a file."""
    try:
        with open(filepath, "r") as f:
            ips = [line.strip() for line in f if line.strip()]
        
        console.print(f"[info]Scanning {len(ips)} IP addresses from {filepath}...[/info]")
        for ip in ips:
            ip_data = get_ip_info(ip)
            if ip_data:
                display_ip_info(ip_data)
                save_output_auto(ip_data)
                console.print("") 
    except FileNotFoundError:
        console.print(Panel(f"[danger]Error: The file '{filepath}' was not found.[/danger]", title="[bold]File Error[/bold]", border_style="danger"))
    except Exception as e:
        console.print(Panel(f"[danger]An error occurred: {e}[/danger]", title="[bold]Error[/bold]", border_style="danger"))

def main():
    """Main function to run the tool."""
    parser = argparse.ArgumentParser(
        description="A professional IP information tool.",
        epilog="Quick Guide: Use one option at a time. For example, use -i for a single IP or -l for a list of IPs.",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=40)
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--about", action="store_true", help="Show detailed info about the tool and author.")
    group.add_argument("--connect", action="store_true", help="Show author's social media profiles.")
    group.add_argument("-i", "--ip", type=str, help="A single IP address to look up.")
    group.add_argument("-l", "--list", type=str, dest="ip_list_file", metavar="FILE", help="Path to a file containing a list of IPs to scan.")

    args = parser.parse_args()

    if args.about:
        print_banner()
        show_about()
    elif args.connect:
        print_banner()
        show_connect()
    elif args.ip:
        print_banner()
        ip_data = get_ip_info(args.ip)
        if ip_data:
            display_ip_info(ip_data)
            save_output_auto(ip_data)
    elif args.ip_list_file:
        print_banner()
        scan_ip_list(args.ip_list_file)
    else:
        print_banner()
        parser.print_help()

if __name__ == "__main__":
    main()
