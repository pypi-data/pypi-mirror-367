#!/usr/bin/env python3

"""sr2t Nmap parser"""

import sys
from dataclasses import dataclass

from prettytable import PrettyTable
from sr2t.shared.export import export_all
from sr2t.shared.utils import load_yaml


@dataclass
class NmapParams:
    """Nmap parameters for parsing"""

    var1: str
    var2: list
    var3: str
    host: object
    addr: str
    args: object


def nmap_loopy(params: NmapParams):
    """Loop to collect addresses or port IDs based on protocol and state"""

    for port in params.host.findall("ports/port"):
        if port.get("protocol") == params.var3:
            portid = port.get("portid")
            for root_state in port.findall("state"):
                if root_state.get("state") == params.args.nmap_state:
                    if params.var1 == "address":
                        params.var2.append(params.addr)
                    elif params.var1 == "portid":
                        params.var2.append(portid)
                    else:
                        sys.exit(1)


def nmap_service_loopy(host, args, addr, data_nmap_services):
    """Loop to collect service information from ports"""

    for port in host.findall("ports/port"):
        portid = port.get("portid")
        for root_state in port.findall("state"):
            if root_state.get("state") == args.nmap_state:
                for service in port.findall("service"):
                    proto = port.get("protocol")
                    service_name = service.get("name")
                    state = root_state.get("state")
                    data_nmap_services.append(
                        [addr, portid, proto, service_name, state]
                    )


def load_and_prepare_yaml(data_package, filename, column_map):
    """Load a YAML file and prepare mappings"""
    yaml_raw = load_yaml(None, data_package, filename)
    reverse_map = {v: k for k, v in column_map.items()}
    yaml_filtered = {
        column_map[category]: patterns
        for category, patterns in yaml_raw.items()
        if category in column_map
    }
    return yaml_filtered, reverse_map


def extract_algorithms(host, addr, script_id, yaml_config, algo_data):
    """Generic algorithm extractor for SSH, RDP, etc."""

    for port in host.findall("ports/port"):
        if port.get("protocol") == "tcp":
            script = port.find(f"script[@id='{script_id}']")
            if script is not None:
                extracted = {}
                portid = port.get("portid")
                ip_port = f"{addr}:{portid}"

                if script_id == "ssh2-enum-algos":
                    for table in script.findall("table"):
                        key = table.get("key")
                        values = [elem.text for elem in table.findall("elem")]
                        extracted[key] = ", ".join(values)
                elif script_id == "rdp-enum-encryption":
                    output = script.get("output", "").lower()
                    extracted = {k: output for k in yaml_config.keys()}
                elif script_id == "ssl-enum-ciphers":
                    tls_versions = []
                    cipher_texts = []

                    for tls_table in script.findall("table"):
                        tls_key = tls_table.get("key", "").lower()
                        if tls_key.startswith("tlsv"):
                            tls_versions.append(tls_key)

                            for cipher_parent in tls_table.findall(
                                "table[@key='ciphers']"
                            ):
                                for cipher_entry in cipher_parent.findall("table"):
                                    name_elem = cipher_entry.find("elem[@key='name']")
                                    if name_elem is not None:
                                        cipher_texts.append(name_elem.text.lower())

                    extracted["tls_versions"] = ", ".join(tls_versions)
                    extracted["cipher_features"] = ", ".join(cipher_texts)
                    extracted["hash_algorithms"] = ", ".join(cipher_texts)
                    extracted["kex_algorithms"] = ", ".join(cipher_texts)

                flags = []
                for category, patterns in yaml_config.items():
                    content = extracted.get(category, "").lower()
                    for pattern in patterns:
                        if category == "kex_algorithms":
                            if pattern.lower() == "dh":
                                match = any("_dh_" in c for c in content.split(", "))
                            elif pattern.lower() == "ecdh":
                                match = any("_ecdh_" in c for c in content.split(", "))
                            else:
                                match = pattern.lower() in content
                        elif category == "hash_algorithms":
                            if pattern.lower() == "sha1":
                                match = any(
                                    c.endswith("sha") for c in content.split(", ")
                                )
                        else:
                            match = pattern.lower() in content

                        flags.append("X" if match else "")

                algo_data.append([ip_port] + flags)


def build_algo_table(algo_data, yaml_config, reverse_map):
    """Generic table builder for extracted algorithm flags"""

    base_header = ["ip address"]
    flag_columns = [
        f"{reverse_map.get(category, category).capitalize()}" f"{pattern.capitalize()}"
        for category, patterns in yaml_config.items()
        for pattern in patterns
    ]
    header = base_header + flag_columns

    used_flags = set()
    for row in algo_data:
        for idx, val in enumerate(row[1:], start=1):
            if val == "X":
                used_flags.add(idx)

    keep_indices = [0] + sorted(used_flags)
    filtered_header = [header[i] for i in keep_indices]

    table = PrettyTable()
    table.field_names = filtered_header
    table.align = "l"

    csv_array = []
    for row in algo_data:
        filtered_row = [row[i] for i in keep_indices]
        table.add_row(filtered_row)
        csv_array.append(filtered_row)

    return table, csv_array, filtered_header


def extract_host_data(host, args):
    """Extract address and port data from a host element"""

    addr = host.find("address").get("addr")

    list_addr_tcp = []
    list_portid_tcp = []
    list_addr_udp = []
    list_portid_udp = []

    param_sets = []
    for proto, addr_list, portid_list in [
        ("tcp", list_addr_tcp, list_portid_tcp),
        ("udp", list_addr_udp, list_portid_udp),
    ]:
        for var1, var2 in [("address", addr_list), ("portid", portid_list)]:
            param_sets.append(
                NmapParams(
                    var1=var1, var2=var2, var3=proto, host=host, addr=addr, args=args
                )
            )

    for params in param_sets:
        nmap_loopy(params)

    return addr, list_addr_tcp, list_portid_tcp, list_addr_udp, list_portid_udp


def build_protocol_table(data, ports):
    """Build PrettyTable and CSV array for TCP/UDP data"""

    table = PrettyTable()
    header = ["ip address"] + ports
    table.field_names = header
    table.align["ip address"] = "l"

    csv_array = []
    for ip_address, open_ports in data:
        row = [ip_address]
        row.extend("X" if str(port) in open_ports else "" for port in ports)
        table.add_row(row)
        csv_array.append(row)

    return table, csv_array, header


def build_services_table(data_nmap_services):
    """Build PrettyTable and CSV array for service data"""

    header = ["ip address", "port", "proto", "service", "state"]
    table = PrettyTable()
    table.field_names = header
    table.align = "l"

    csv_array = []
    for row in data_nmap_services:
        table.add_row(row)
        csv_array.append(row)

    return table, csv_array, header


def nmap_parser(args, root, workbook):
    """Main Nmap parser function"""

    data_nmap_tcp = []
    data_nmap_udp = []
    data_nmap_services = []

    # Load YAML
    data_package = "sr2t.data"
    ssh_algo_data = []
    ssh_column_names = {
        "kex": "kex_algorithms",
        "cipher": "encryption_algorithms",
        "mac": "mac_algorithms",
        "compression": "compression_algorithms",  # You can omit if unused
    }
    ssh_yaml, reverse_column_names = load_and_prepare_yaml(
        data_package, "nmap_ssh.yaml", ssh_column_names
    )
    rdp_algo_data = []
    rdp_column_names = {
        "sec": "rdp_security_layer",
        "enc": "rdp_encryption_level",
        "proto": "rdp_protocol_version",
    }
    rdp_yaml, reverse_rdp_column_names = load_and_prepare_yaml(
        data_package, "nmap_rdp.yaml", rdp_column_names
    )
    ssl_algo_data = []
    ssl_column_names = {
        "cipher enc": "cipher_features",
        "cipher hash": "hash_algorithms",
        "kex": "kex_algorithms",
        "proto": "tls_versions",
    }
    ssl_yaml, reverse_ssl_column_names = load_and_prepare_yaml(
        data_package, "nmap_ssl.yaml", ssl_column_names
    )

    # Parse hosts
    for element in root:
        for host in element.findall("host"):
            addr, list_addr_tcp, list_portid_tcp, list_addr_udp, list_portid_udp = (
                extract_host_data(host, args)
            )
            extract_algorithms(host, addr, "ssh2-enum-algos", ssh_yaml, ssh_algo_data)
            extract_algorithms(
                host, addr, "rdp-enum-encryption", rdp_yaml, rdp_algo_data
            )
            extract_algorithms(host, addr, "ssl-enum-ciphers", ssl_yaml, ssl_algo_data)
            nmap_service_loopy(host, args, addr, data_nmap_services)

            if list_addr_tcp:
                data_nmap_tcp.append([list_addr_tcp[0], list_portid_tcp])
            if list_addr_udp:
                data_nmap_udp.append([list_addr_udp[0], list_portid_udp])

    # Get sorted port lists
    tcp_ports = (
        sorted({int(port) for _, ports in data_nmap_tcp for port in ports})
        if data_nmap_tcp
        else []
    )
    udp_ports = (
        sorted({int(port) for _, ports in data_nmap_udp for port in ports})
        if data_nmap_udp
        else []
    )

    # Build tables
    my_nmap_tcp_table, csv_array_tcp, header_tcp = build_protocol_table(
        data_nmap_tcp, tcp_ports
    )
    my_nmap_udp_table, csv_array_udp, header_udp = build_protocol_table(
        data_nmap_udp, udp_ports
    )
    my_nmap_services_table, csv_array_services, header_services = build_services_table(
        data_nmap_services
    )
    ssh_table, csv_array_ssh, header_ssh = build_algo_table(
        ssh_algo_data, ssh_yaml, reverse_column_names
    )
    rdp_table, csv_array_rdp, header_rdp = build_algo_table(
        rdp_algo_data, rdp_yaml, reverse_rdp_column_names
    )
    ssl_table, csv_array_ssl, header_ssl = build_algo_table(
        ssl_algo_data, ssl_yaml, reverse_ssl_column_names
    )

    # Host lists
    my_nmap_host_list_tcp = (
        [ip for ip, _ in data_nmap_tcp] if args.nmap_host_list else []
    )
    my_nmap_host_list_udp = (
        [ip for ip, _ in data_nmap_udp] if args.nmap_host_list else []
    )

    exportables = [
        ("Nmap TCP", csv_array_tcp, header_tcp),
        ("Nmap UDP", csv_array_udp, header_udp),
        (
            ("Nmap Services", csv_array_services, header_services)
            if args.nmap_services == 1
            else None
        ),
        ("ssh", csv_array_ssh, header_ssh),
        ("rdp", csv_array_rdp, header_rdp),
        ("ssl", csv_array_ssl, header_ssl),
    ]
    export_all(args, workbook, [e for e in exportables if e])

    return (
        my_nmap_tcp_table if csv_array_tcp else [],
        my_nmap_udp_table if csv_array_udp else [],
        my_nmap_services_table if csv_array_services else [],
        my_nmap_host_list_tcp,
        my_nmap_host_list_udp,
        ssh_table if csv_array_ssh else [],
        rdp_table if csv_array_rdp else [],
        ssl_table if csv_array_ssl else [],
        workbook,
    )
