import argparse
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Sample data
PORTS = [
    ["20", "FTP (Data)", "File Transfer Protocol (Data)"],
    ["21", "FTP (Control)", "File Transfer Protocol (Control)"],
    ["22", "SSH", "Secure Shell for remote login"],
    ["23", "Telnet", "Insecure remote access (deprecated)"],
    ["25", "SMTP", "Send email (Simple Mail Transfer Protocol)"],
    ["53", "DNS", "Domain Name System (TCP/UDP)"],
    ["67/68", "DHCP", "Dynamic Host Configuration Protocol (UDP)"],
    ["69", "TFTP", "Trivial File Transfer Protocol (UDP)"],
    ["80", "HTTP", "Web traffic (unsecured)"],
    ["110", "POP3", "Receive email (Post Office Protocol v3)"],
    ["143", "IMAP", "Synchronize email (Internet Message Access Protocol)"],
    ["161/162", "SNMP", "Simple Network Management Protocol (UDP)"],
    ["443", "HTTPS", "Secure web traffic"],
    ["445", "SMB", "Windows file sharing (Server Message Block)"],
    ["3389", "RDP", "Remote Desktop Protocol (TCP/UDP)"]
]


COMMANDS = [
    ["ping", "All", "Check network connectivity"],
    ["ipconfig", "Windows", "Display network config"],
    ["ifconfig", "Linux", "Display network config"],
    ["tracert", "Windows", "Trace route to host"],
    ["traceroute", "Linux", "Trace route to host"],
    ["nslookup", "All", "Query DNS servers"]
]

WIFI_BANDS = [
    ["2.4 GHz", "Longer range, better wall penetration", "Slower, more interference"],
    ["5 GHz", "Faster speeds, less interference", "Shorter range, weaker wall penetration"],
    ["6 GHz", "Very high speeds, low latency", "Very short range, new hardware required"]
]

IP_TABLE = [
    ["0.0.0.0", "/8", "Reserved", "Default route or unspecified IP (e.g., bind to all interfaces)"],
    ["127.0.0.0 – 127.255.255.255", "127.0.0.0/8", "Loopback", "Localhost testing (e.g., 127.0.0.1)"],
    ["169.254.0.0 – 169.254.255.255", "169.254.0.0/16", "APIPA", "Self-assigned when DHCP fails (e.g., 'No internet')"],
    ["10.0.0.0 – 10.255.255.255", "10.0.0.0/8", "Private", "Used by routers, WSL1, VirtualBox (host-only)"],
    ["172.16.0.0 – 172.31.255.255", "172.16.0.0/12", "Private", "Used by Docker, WSL2, Hyper-V, VPN clients"],
    ["192.168.0.0 – 192.168.255.255", "192.168.0.0/16", "Private", "Most home routers and VMs (e.g., 192.168.1.1)"],
    ["100.64.0.0 – 100.127.255.255", "100.64.0.0/10", "Shared", "Carrier-grade NAT (used by ISPs and mobile data)"],
    ["192.0.2.0 – 192.0.2.255", "192.0.2.0/24", "TEST-NET-1", "Reserved for documentation and testing"],
    ["198.51.100.0 – 198.51.100.255", "198.51.100.0/24", "TEST-NET-2", "Used in training/demos (not routable)"],
    ["203.0.113.0 – 203.0.113.255", "203.0.113.0/24", "TEST-NET-3", "Used in documentation and tools"],
    ["224.0.0.0 – 239.255.255.255", "224.0.0.0/4", "Multicast", "Streaming, OSPF, games, and group messaging"],
    ["240.0.0.0 – 255.255.255.254", "240.0.0.0/4", "Reserved", "For future use (not publicly routable)"],
    ["255.255.255.255", "/32", "Broadcast", "Broadcast to all hosts on local subnet (e.g., DHCP request)"]
]


WIFI_STANDARDS = [
    ["802.11a", "5 GHz", "54 Mbps", "Rare today"],
    ["802.11b", "2.4 GHz", "11 Mbps", "Obsolete"],
    ["802.11g", "2.4 GHz", "54 Mbps", "Legacy support"],
    ["802.11n", "2.4 & 5 GHz", "Up to 600 Mbps", "First dual-band"],
    ["802.11ac", "5 GHz", "1+ Gbps", "Widely used"],
    ["802.11ax", "2.4 & 5 GHz", "Up to 10 Gbps", "Wi-Fi 6 (latest)"],
    ["802.11ax (6E)", "6 GHz", "Up to 10 Gbps", "Wi-Fi 6E (emerging)"]
]

WIFI_TRICKS = [
    "- 'A' = 5 GHz → **Airplanes fly high**",
    "- 'B' and 'G' = 2.4 GHz → **Basic, Ground level**",
    "- 'N' = Both → **Neutral** / dual-band",
    "- 'AC' and 'AX' = Modern fast 5 GHz and 6 GHz"
]

CONNECTIONS = [
    ["USB 2.0", "480 Mbps", "Keyboards, mice, flash drives"],
    ["USB 3.0", "5 Gbps", "External storage, hubs"],
    ["USB 3.1", "10 Gbps", "Fast data transfer, newer devices"],
    ["USB-C", "10–40 Gbps", "Reversible universal cable"],
    ["SATA I", "1.5 Gbps", "Older hard drives"],
    ["SATA II", "3 Gbps", "Mid-generation SSDs/HDDs"],
    ["SATA III", "6 Gbps", "Modern SSDs and HDDs"],
    ["NVMe (PCIe)", "Up to 4 GBps", "Ultra-fast internal SSDs"],
    ["PCIe x1", "Up to 1 GBps", "Low-bandwidth cards"],
    ["PCIe x16", "Up to 16 GBps", "Graphics cards"]
]

CONN_TRICKS = [
    "- SATA = used for storage drives (1.5–6 Gbps depending on version)",
    "- PCIe = used for add-in cards (e.g., GPU, sound, Wi-Fi)",
    "- USB = used for external peripherals (2.0 = slow, 3.x = fast)",
    "- USB-C = reversible and supports power + data + video",
    "- NVMe = fastest storage, uses PCIe lanes"
]

VIDEO_CONNECTORS = [
    ["HDMI", "Digital video + audio", "Type A (19-pin), up to 20m, no analog"],
    ["DisplayPort", "Digital video + audio", "Packet-based, adapters to HDMI/DVI"],
    ["Mini DisplayPort", "Digital", "Smaller version, used in Apple devices"],
    ["DVI-D", "Digital only", "No audio, Single/Dual link, up to 7.4 Gbps"],
    ["DVI-A", "Analog only", "Backwards-compatible with VGA"],
    ["DVI-I", "Digital + Analog", "Integrated — supports both"],
    ["VGA (DE-15)", "Analog only", "Blue 15-pin, signal loss after 5–10m"],
    ["USB-C", "Digital video/audio/data/power", "Supports video via 'Alt Mode'"]
]

VIDEO_TIPS = [
    "- HDMI = digital, common for TVs and monitors",
    "- DisplayPort = digital, can be adapted to HDMI/DVI",
    "- VGA = analog only, degrades with distance",
    "- DVI: D = digital, A = analog, I = both",
    "- USB-C = reversible, supports video/audio/data/power"
]

CABLES = [
    ["RJ45", "Twisted Pair", "8P8C Ethernet connector (Cat5/6)"],
    ["RJ11", "Twisted Pair", "Used for telephones and DSL (6P2C)"],
    ["DB-9 (RS-232)", "Serial", "Legacy console/config interface"],
    ["BNC", "Coaxial", "Bayonet-style for CCTV/older networks"],
    ["F-Connector", "Coaxial", "Threaded connector for cable/TV"],
    ["SC", "Fiber (Square)", "Push-pull, snap-in connector"],
    ["ST", "Fiber (Twist)", "Bayonet-style fiber connector"],
    ["LC", "Fiber (Little)", "Small form factor with locking clip"]
]

STORAGE_TYPES = [
    ["HDD", "Magnetic (Spinning)", "High capacity, low cost, slow performance"],
    ["SSD", "Flash memory", "Fast, silent, no moving parts"],
    ["NVMe", "PCIe Flash", "Very fast SSDs over PCIe lanes"],
    ["M.2", "Form Factor", "Supports SATA or NVMe drives"],
    ["eSATA", "External SATA", "Connects external drives with SATA speeds"],
    ["Optical", "Laser-based", "CD/DVD/Blu-ray for archives or media"],
    ["Flash", "EEPROM", "USB drives, SD cards, compact & portable"],
    ["SCSI/SAS", "Enterprise", "Used in servers, fast and reliable"]
]

WIFI_SECURITY = [
    ["WEP", "Wired Equivalent Privacy", "Very weak — obsolete and cracked"],
    ["WPA", "Wi-Fi Protected Access", "Temporary fix using TKIP (deprecated)"],
    ["WPA2", "WPA with AES", "Strong and widely adopted standard"],
    ["WPA3", "WPA2 + modern enhancements", "Forward secrecy, better for public Wi-Fi"]
]

CPU_TYPES = [
    ["LGA 1700", "Intel", "12th–14th Gen Core CPUs (Alder/Raptor Lake)"],
    ["LGA 1200", "Intel", "10th–11th Gen Core (Comet/Rocket Lake)"],
    ["AM4", "AMD", "Ryzen 1000–5000 series (PGA socket)"],
    ["AM5", "AMD", "Ryzen 7000+ series (LGA socket)"],
    ["Socket TR4", "AMD", "Threadripper HEDT CPUs (LGA)"]
]



# Functions
def print_section_title(title):
    print(Fore.GREEN + Style.BRIGHT + f"\n\n{'=' * 10} {title.upper()} {'=' * 10}\n")

def show_commands(os_filter="all", keyword=None):
    print_section_title("Commands")

    filtered = []

    for cmd in COMMANDS:
        name, os, desc = cmd
        if (os_filter == "all" or os_filter.lower() == os.lower()) and (
            not keyword or keyword.lower() in name.lower() or keyword.lower() in desc.lower()
        ):
            color = Fore.GREEN if os.lower() == "windows" else Fore.YELLOW if os.lower() == "linux" else Fore.BLUE
            filtered.append([color + name, os, desc])

    headers = [Fore.CYAN + "Command", Fore.CYAN + "OS", Fore.CYAN + "Description"]
    print(tabulate(filtered, headers=headers, tablefmt="fancy_grid"))

def show_ports(keyword=None):
    print_section_title("Port Numbers")

    filtered = PORTS
    if keyword:
        keyword = keyword.lower()
        filtered = [
            row for row in PORTS
            if any(keyword in str(cell).lower() for cell in row)
        ]

    headers = [Fore.CYAN + "Port", Fore.CYAN + "Protocol", Fore.CYAN + "Description"]
    print(tabulate(filtered, headers=headers, tablefmt="fancy_grid"))


def show_wifi(keyword=None):
    print_section_title("Wi-Fi Bands and Standards")

    # Wi-Fi Bands
    bands = WIFI_BANDS
    if keyword:
        keyword = keyword.lower()
        bands = [row for row in WIFI_BANDS if any(keyword in str(cell).lower() for cell in row)]

    print(Fore.MAGENTA + "\n📡 Wi-Fi Frequency Bands:\n")
    headers_bands = [Fore.CYAN + "Band", Fore.CYAN + "Advantages", Fore.CYAN + "Limitations"]
    print(tabulate(bands, headers=headers_bands, tablefmt="fancy_grid"))

    # Wi-Fi Standards
    standards = WIFI_STANDARDS
    if keyword:
        standards = [row for row in WIFI_STANDARDS if any(keyword in str(cell).lower() for cell in row)]

    print(Fore.MAGENTA + "\n📶 Wi-Fi Standards (802.11):\n")
    headers_standards = [Fore.CYAN + "Standard", Fore.CYAN + "Frequency", Fore.CYAN + "Max Speed", Fore.CYAN + "Notes"]
    print(tabulate(standards, headers=headers_standards, tablefmt="fancy_grid"))

    if not keyword:
        print(Fore.MAGENTA + "\n🧠 Memory Tricks:\n")
        for tip in WIFI_TRICKS:
            print(Fore.YELLOW + tip)


def show_ip_table(keyword=None):
    print_section_title("Common IP Address Ranges")

    filtered = IP_TABLE
    if keyword:
        keyword = keyword.lower()
        filtered = [
            row for row in IP_TABLE
            if any(keyword in str(cell).lower() for cell in row)
        ]

    headers = [Fore.CYAN + "Range", Fore.CYAN + "CIDR", Fore.CYAN + "Type", Fore.CYAN + "Use / Example"]
    print(tabulate(filtered, headers=headers, tablefmt="fancy_grid"))

import ipaddress


def show_ip_calculator(cidr_input):
    print_section_title("IP Address Calculator")

    try:
        # Parse input
        net = ipaddress.IPv4Interface(cidr_input)
        network = net.network
        ip = net.ip
        mask = network.netmask
        broadcast = network.broadcast_address
        total_hosts = network.num_addresses - 2 if network.num_addresses > 2 else network.num_addresses

        first_host = ipaddress.IPv4Address(int(network.network_address) + 1)
        last_host = ipaddress.IPv4Address(int(network.broadcast_address) - 1)

        headers = ["Field", "Value"]
        rows = [
            ["IP Address", str(ip)],
            ["CIDR Notation", f"/{network.prefixlen}"],
            ["Subnet Mask", str(mask)],
            ["Network Address", str(network.network_address)],
            ["Broadcast Address", str(broadcast)],
            ["Host Range", f"{first_host} – {last_host}" if total_hosts >= 2 else "N/A"],
            ["Total Hosts", f"{total_hosts} usable" if total_hosts >= 2 else f"{total_hosts} total"],
        ]

        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
        # Add smart environment summary
        env_summary = ""

        if network.prefixlen == 32:
            env_summary = "🔒 This is likely a public Wi-Fi, VPN, or isolated host. No other devices share this subnet."
        elif network.prefixlen == 24:
            env_summary = "🏠 This is a common home or small office LAN subnet (e.g., 192.168.x.x/24)."
        elif network.prefixlen == 16:
            env_summary = "🏢 This is a large LAN or departmental network (e.g., 172.16.0.0/16)."
        elif network.prefixlen <= 8:
            env_summary = "🌐 This is a very large network, possibly enterprise-grade or ISP-level."
        elif network.prefixlen == 30:
            env_summary = "🔗 This is often used for point-to-point links, routers, or VPN tunnels."
        else:
            env_summary = "ℹ️ This is a custom or uncommon subnet size."

        print(Fore.BLUE + f"\n{env_summary}\n")
        print(Fore.YELLOW + "\n💡 Tip: Find your IP using 'ip a' (Linux) or 'ipconfig' (Windows) — look for an IPv4 address on eth0 or your active interface.\n")

    except Exception as e:
        print(Fore.RED + f"\n[!] Invalid input. Please use CIDR notation (e.g., 192.168.1.100/24).")
        print(Fore.RED + f"Error: {e}\n")

def show_connections(keyword=None):
    print_section_title("Connection Interfaces")

    CONN_TRICKS = [
        "- SATA = storage drives (1.5–6 Gbps depending on version)",
        "- PCIe = used for expansion cards (e.g., GPUs, sound cards)",
        "- USB = general-purpose external interface (USB 2.0 = slow, 3.x = faster)",
        "- USB-C = reversible, supports power + data + video",
        "- NVMe = fastest storage, uses PCIe lanes"
    ]

    filtered = CONNECTIONS
    if keyword:
        keyword = keyword.lower()
        filtered = [
            row for row in CONNECTIONS
            if any(keyword in str(cell).lower() for cell in row)
        ]

    headers = [Fore.CYAN + "Interface", Fore.CYAN + "Max Speed", Fore.CYAN + "Used For"]
    print(tabulate(filtered, headers=headers, tablefmt="fancy_grid"))

    if not keyword:
        print(Fore.MAGENTA + "\n🧠 Memory Tricks:\n")
        for tip in CONN_TRICKS:
            print(Fore.YELLOW + tip)


def show_video_connectors(keyword=None):
    print_section_title("Video Connectors")

    VIDEO_TIPS = [
        "- HDMI = digital, carries video + audio, very common",
        "- DisplayPort = packet-based, supports adapters to HDMI/DVI",
        "- VGA = analog only, degrades over 5–10m",
        "- DVI: D = digital, A = analog, I = both",
        "- USB-C = Alt Mode supports video output"
    ]

    filtered = VIDEO_CONNECTORS
    if keyword:
        keyword = keyword.lower()
        filtered = [
            row for row in VIDEO_CONNECTORS
            if any(keyword in str(cell).lower() for cell in row)
        ]

    headers = [Fore.CYAN + "Connector", Fore.CYAN + "Signal Type", Fore.CYAN + "Notes"]
    print(tabulate(filtered, headers=headers, tablefmt="fancy_grid"))

    if not keyword:
        print(Fore.MAGENTA + "\n🧠 Memory Tricks:\n")
        for tip in VIDEO_TIPS:
            print(Fore.YELLOW + tip)

def show_cables(keyword=None):
    print_section_title("Cable Types")

    CABLE_TIPS = [
        "- RJ45 = Ethernet, 8P8C, Cat5e/6/6a",
        "- RJ11 = DSL/phones, smaller than RJ45",
        "- DB-9 = serial/console, still used in networking gear",
        "- BNC = coax, twist-to-lock",
        "- F-Connector = threaded coax (TV, modem)",
        "- SC = Square Connector (snap-in)",
        "- ST = Stick and Twist (bayonet)",
        "- LC = Little Connector (compact fiber)"
    ]

    filtered = CABLES
    if keyword:
        keyword = keyword.lower()
        filtered = [
            row for row in CABLES
            if any(keyword in str(cell).lower() for cell in row)
        ]

    headers = [Fore.CYAN + "Connector", Fore.CYAN + "Type", Fore.CYAN + "Notes"]
    print(tabulate(filtered, headers=headers, tablefmt="fancy_grid"))

    if not keyword:
        print(Fore.MAGENTA + "\n🧠 Memory Tricks:\n")
        for tip in CABLE_TIPS:
            print(Fore.YELLOW + tip)

def show_storage(keyword=None):
    print_section_title("Storage Technologies")

    STORAGE_TIPS = [
        "- HDD = spinning disks, high capacity, low performance",
        "- SSD = fast, no moving parts, more expensive",
        "- NVMe = fastest SSDs using PCIe lanes",
        "- M.2 = physical format, supports SATA or NVMe",
        "- eSATA = external SATA connector",
        "- Optical = CD/DVD/BD, slower and outdated",
        "- Flash = USB, SD, portable and convenient",
        "- SCSI/SAS = enterprise, fast & redundant"
    ]

    filtered = STORAGE_TYPES
    if keyword:
        keyword = keyword.lower()
        filtered = [
            row for row in STORAGE_TYPES
            if any(keyword in str(cell).lower() for cell in row)
        ]

    headers = [Fore.CYAN + "Type", Fore.CYAN + "Technology", Fore.CYAN + "Description"]
    print(tabulate(filtered, headers=headers, tablefmt="fancy_grid"))

    if not keyword:
        print(Fore.MAGENTA + "\n🧠 Memory Tricks:\n")
        for tip in STORAGE_TIPS:
            print(Fore.YELLOW + tip)

def show_wifi_security(keyword=None):
    print_section_title("Wireless Encryption Standards")

    WIFI_SECURITY_TIPS = [
        "- WEP = old, weak, cracked — never use it",
        "- WPA = short-term fix with TKIP encryption",
        "- WPA2 = strong AES encryption, widely used",
        "- WPA3 = modern upgrade with forward secrecy, great for public networks"
    ]

    filtered = WIFI_SECURITY
    if keyword:
        keyword = keyword.lower()
        filtered = [
            row for row in WIFI_SECURITY
            if any(keyword in str(cell).lower() for cell in row)
        ]

    headers = [Fore.CYAN + "Standard", Fore.CYAN + "Full Name", Fore.CYAN + "Notes"]
    print(tabulate(filtered, headers=headers, tablefmt="fancy_grid"))

    if not keyword:
        print(Fore.MAGENTA + "\n🧠 Memory Tricks:\n")
        for tip in WIFI_SECURITY_TIPS:
            print(Fore.YELLOW + tip)

def show_cpu_sockets(keyword=None):
    print_section_title("CPU Sockets & Types")

    CPU_TIPS = [
        "- Intel = LGA (pins on motherboard), e.g., LGA 1700/1200",
        "- AMD AM4 = PGA (pins on CPU), used in Ryzen 1000–5000",
        "- AMD AM5 = LGA (like Intel), newer Ryzen 7000+",
        "- TR4 = Threadripper socket for high-end desktops"
    ]

    filtered = CPU_TYPES
    if keyword:
        keyword = keyword.lower()
        filtered = [
            row for row in CPU_TYPES
            if any(keyword in str(cell).lower() for cell in row)
        ]

    headers = [Fore.CYAN + "Socket", Fore.CYAN + "Brand", Fore.CYAN + "Used For"]
    print(tabulate(filtered, headers=headers, tablefmt="fancy_grid"))

    if not keyword:
        print(Fore.MAGENTA + "\n🧠 Memory Tricks:\n")
        for tip in CPU_TIPS:
            print(Fore.YELLOW + tip)
def main():
    # Argument parser setup
    parser = argparse.ArgumentParser(
        description="Common CLI Tool – Ports & Network Commands",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-all", "--all", action="store_true", help="Show all sections")
    parser.add_argument("-p", "--ports", action="store_true", help="Show common port numbers")
    parser.add_argument("-cmd", "--commands", action="store_true", help="Show common network commands")
    parser.add_argument("-os", choices=["win", "linux", "all"], default="all", help="Filter commands by OS")
    parser.add_argument("-s", "--search", type=str, help="Search for a keyword")
    parser.add_argument("-wifi", "--wifi", action="store_true", help="Show Wi-Fi bands and standards")
    parser.add_argument("-conn", "--connections", action="store_true", help="Show common connection types")
    parser.add_argument("-video", "--video", action="store_true", help="Show video/display connector types")
    parser.add_argument("-cable", "--cable", action="store_true", help="Show fiber and copper connector types")
    parser.add_argument("-storage","--storage", action="store_true", help="Show storage technologies and interfaces")
    parser.add_argument("-ws", "--wifi-sec", action="store_true", help="Show wireless encryption types")
    parser.add_argument("-cpu","--cpu", action="store_true", help="Show CPU socket types and platforms")
    parser.add_argument("-ip", "--iptable", action="store_true", help="Show common IP address ranges")
    parser.add_argument("-calc", "--ipcalc", type=str, metavar="CIDR", help="Calculate subnet details from an IP/CIDR")


    args = parser.parse_args()

    # Main Logic
    if args.ports:
        show_ports(keyword=args.search)
    elif args.commands:
        show_commands(os_filter=args.os, keyword=args.search)
    elif args.wifi:
        show_wifi(keyword=args.search)
    elif args.connections:
        show_connections(keyword=args.search)
    elif args.video:
        show_video_connectors(keyword=args.search)
    elif args.cable:
        show_cables(keyword=args.search)
    elif args.storage:
        show_storage(keyword=args.search)
    elif args.wifi_sec:
        show_wifi_security(keyword=args.search)
    elif args.iptable:
        show_ip_table(keyword=args.search)
    elif args.ipcalc:
        show_ip_calculator(args.ipcalc)  
    elif args.cpu:
        show_cpu_sockets(keyword=args.search)
    elif args.all:
        keyword = args.search  # optional filter

        print_section_title("Ports")
        show_ports(keyword=keyword)

        print_section_title("Commands")
        show_commands(os_filter=args.os, keyword=keyword)

        print_section_title("Wi-Fi Bands")
        show_wifi(keyword=keyword)

        print_section_title("Connection Interfaces")
        show_connections(keyword=keyword)

        print_section_title("Video Connectors")
        show_video_connectors(keyword=keyword)

        print_section_title("Cable Types")
        show_cables(keyword=keyword)

        print_section_title("Storage Technologies")
        show_storage(keyword=keyword)

        print_section_title("Wi-Fi Security")
        show_wifi_security(keyword=keyword)

        print_section_title("IP Table")
        show_ip_table(keyword=keyword)

        print_section_title("IP Calc")
        show_ip_calculator(keyword=keyword)

        print_section_title("CPU Sockets")
        show_cpu_sockets(keyword=keyword)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
