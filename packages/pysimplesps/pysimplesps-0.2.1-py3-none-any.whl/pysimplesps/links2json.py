import json
import re
import glob
from typing import Dict, Any, Optional
from datetime import datetime


class SPSUnifiedLinksParser:
    """Parser for SPS Diameter, M2UA, M3UA, and MTP Links MML configuration."""
    
    def __init__(self, file_path: str = "spsdmlinks.txt"):
        self.file_path = file_path
        self.config = {
            # Diameter Configuration
            "diameter_peers": [],
            "diameter_link_sets": [],
            "diameter_links": [],
            
            # MTP (Message Transfer Part) Configuration
            "mtp_destination_points": [],
            "mtp_link_sets": [],
            "mtp_links": [],
            "mtp_routes": [],
            
            # M2UA Configuration
            "m2ua_application_servers": [],
            "m2ua_link_sets": [],
            "m2ua_links": [],
            "m2ua_routes": [],
            
            # M3UA Configuration  
            "m3ua_application_servers": [],
            "m3ua_link_sets": [],
            "m3ua_links": [],
            "m3ua_routes": [],
            
            # SCCP Configuration
            "sccp_subsystems": [],
            "sccp_global_titles": [],
            
            "hierarchical_structure": {},
            "metadata": {
                "meid": None,
                "parsed_at": datetime.now().isoformat(),
                "total_peers": 0,
                "total_link_sets": 0,
                "total_links": 0,
                "total_network_points": 0,
                "all_ips": [],
                "all_ports": [],
                "all_ip_port_pairs": [],
                "unique_ips": [],
                "unique_ports": [],
                "unique_ip_port_pairs": [],
                "unique_networks": set(),
                "unique_point_codes": set(),
                "ip_port_pairs": set()
            }
        }
        
        # File patterns to search for
        self.file_patterns = [
            "spsdmlinks*.txt",
            "spsstp*.txt",
            "*stp*.txt", 
            "*sccp*.txt",
            "*mtp*.txt",
            "*m2ua*.txt",
            "*m3ua*.txt"
        ]
        
        # MML command patterns for STP/SCCP
        self.mml_patterns = {
            # MTP DSP (Destination Signaling Point)
            "ADD_N7DSP": re.compile(
                r'ADD\s+N7DSP:\s*'
                r'STDNAME="([^"]*)"'
                r'(?:,\s*NPC="([^"]*)")?'
                r'(?:,\s*SUAPOINT=([^,]*))?'
                r'(?:,\s*TMN="([^"]*)")?'
                r'(?:,\s*LNN="([^"]*)")?'
                r'[^;]*;', re.IGNORECASE
            ),
            
            # MTP Link Set
            "ADD_N7LKS": re.compile(
                r'ADD\s+N7LKS:\s*'
                r'LKSNM="([^"]*)"'
                r'(?:,\s*ASPNM="([^"]*)")?'
                r'(?:,\s*OFNM="([^"]*)")?'
                r'(?:,\s*NI=([^,]*))?'
                r'(?:,\s*SLS=([^,]*))?'
                r'(?:,\s*WRNNM="([^"]*)")?'
                r'(?:,\s*TNM="([^"]*)")?'
                r'(?:,\s*RRT=([^,]*))?'
                r'(?:,\s*CPPOLICY=([^,]*))?'
                r'(?:,\s*SCRN=([^,]*))?'
                r'[^;]*;', re.IGNORECASE
            ),
            
            # MTP Link
            "ADD_N7LNK": re.compile(
                r'ADD\s+N7LNK:\s*'
                r'LNKNM="([^"]*)"'
                r'(?:,\s*LKSNM="([^"]*)")?'
                r'(?:,\s*CT=([^,]*))?'
                r'(?:,\s*MID=([^,]*))?'
                r'(?:,\s*SLC=([^,]*))?'
                r'(?:,\s*TNM="([^"]*)")?'
                r'(?:,\s*IPTYPE=([^,]*))?'
                r'(?:,\s*ADDRID1="([^"]*)")?'
                r'(?:,\s*LP=([^,]*))?'
                r'(?:,\s*RIP41="([^"]*)")?'
                r'(?:,\s*RP=([^,]*))?'
                r'(?:,\s*CS=([^,]*))?'
                r'(?:,\s*REGPORTFLAG=([^,]*))?'
                r'(?:,\s*SCTPNM="([^"]*)")?'
                r'[^;]*;', re.IGNORECASE
            ),
            
            # MTP Route
            "ADD_N7RT": re.compile(
                r'ADD\s+N7RT:\s*'
                r'RTNM="([^"]*)"'
                r'(?:,\s*LSNM="([^"]*)")?'
                r'(?:,\s*DPNM="([^"]*)")?'
                r'(?:,\s*TMNM="([^"]*)")?'
                r'[^;]*;', re.IGNORECASE
            ),
            
            # M2UA Application Server
            "ADD_M2AS": re.compile(
                r'ADD\s+M2AS:\s*'
                r'ASNM="([^"]*)"'
                r'(?:,\s*NI=([^,]*))?'
                r'(?:,\s*DPCT="([^"]*)")?'
                r'[^;]*;', re.IGNORECASE
            ),
            
            # M2UA Link Set
            "ADD_M2LKS": re.compile(
                r'ADD\s+M2LKS:\s*'
                r'LKSNM="([^"]*)"'
                r'(?:,\s*ASNM="([^"]*)")?'
                r'(?:,\s*OFNM="([^"]*)")?'
                r'(?:,\s*TIMERNM="([^"]*)")?'
                r'(?:,\s*RRT=([^,]*))?'
                r'(?:,\s*CPPOLICY=([^,]*))?'
                r'(?:,\s*SCRN=([^,]*))?'
                r'[^;]*;', re.IGNORECASE
            ),
            
            # M2UA Link
            "ADD_M2LNK": re.compile(
                r'ADD\s+M2LNK:\s*'
                r'LNKNM="([^"]*)"'
                r'(?:,\s*LKSNM="([^"]*)")?'
                r'(?:,\s*MID=([^,]*))?'
                r'(?:,\s*IPTYPE=([^,]*))?'
                r'(?:,\s*ADDRID1="([^"]*)")?'
                r'(?:,\s*LP=([^,]*))?'
                r'(?:,\s*RIP41="([^"]*)")?'
                r'(?:,\s*RP=([^,]*))?'
                r'(?:,\s*CS=([^,]*))?'
                r'(?:,\s*REGPORTFLAG=([^,]*))?'
                r'(?:,\s*SCTPNM="([^"]*)")?'
                r'(?:,\s*TIMERNM="([^"]*)")?'
                r'[^;]*;', re.IGNORECASE
            ),
            
            # M2UA Route
            "ADD_M2RT": re.compile(
                r'ADD\s+M2RT:\s*'
                r'RTNM="([^"]*)"'
                r'(?:,\s*ASNM="([^"]*)")?'
                r'(?:,\s*LKSNM="([^"]*)")?'
                r'[^;]*;', re.IGNORECASE
            ),
            
            # M3UA Application Server
            "ADD_M3AS": re.compile(
                r'ADD\s+M3AS:\s*'
                r'ASNM="([^"]*)"'
                r'(?:,\s*NI=([^,]*))?'
                r'(?:,\s*DPCT="([^"]*)")?'
                r'[^;]*;', re.IGNORECASE
            ),
            
            # M3UA Link Set
            "ADD_M3LKS": re.compile(
                r'ADD\s+M3LKS:\s*'
                r'LKSNM="([^"]*)"'
                r'(?:,\s*ASNM="([^"]*)")?'
                r'(?:,\s*OFNM="([^"]*)")?'
                r'(?:,\s*TIMERNM="([^"]*)")?'
                r'(?:,\s*RRT=([^,]*))?'
                r'(?:,\s*CPPOLICY=([^,]*))?'
                r'(?:,\s*SCRN=([^,]*))?'
                r'[^;]*;', re.IGNORECASE
            ),
            
            # M3UA Link
            "ADD_M3LNK": re.compile(
                r'ADD\s+M3LNK:\s*'
                r'LNKNM="([^"]*)"'
                r'(?:,\s*LKSNM="([^"]*)")?'
                r'(?:,\s*MID=([^,]*))?'
                r'(?:,\s*IPTYPE=([^,]*))?'
                r'(?:,\s*ADDRID1="([^"]*)")?'
                r'(?:,\s*LP=([^,]*))?'
                r'(?:,\s*RIP41="([^"]*)")?'
                r'(?:,\s*RP=([^,]*))?'
                r'(?:,\s*CS=([^,]*))?'
                r'(?:,\s*REGPORTFLAG=([^,]*))?'
                r'(?:,\s*SCTPNM="([^"]*)")?'
                r'(?:,\s*TIMERNM="([^"]*)")?'
                r'[^;]*;', re.IGNORECASE
            ),
            
            # M3UA Route
            "ADD_M3RT": re.compile(
                r'ADD\s+M3RT:\s*'
                r'RTNM="([^"]*)"'
                r'(?:,\s*ASNM="([^"]*)")?'
                r'(?:,\s*LKSNM="([^"]*)")?'
                r'[^;]*;', re.IGNORECASE
            ),
            
            # SCCP Subsystem
            "ADD_SCCPSSN": re.compile(
                r'ADD\s+SCCPSSN:\s*'
                r'SSNNM="([^"]*)"'
                r'(?:,\s*NI=([^,]*))?'
                r'(?:,\s*SSN=([^,]*))?'
                r'(?:,\s*DNM="([^"]*)")?'
                r'[^;]*;', re.IGNORECASE
            ),
            
            # SCCP Global Title
            "ADD_SCCPGT": re.compile(
                r'ADD\s+SCCPGT:\s*'
                r'GTNM="([^"]*)"'
                r'(?:,\s*NI=([^,]*))?'
                r'(?:,\s*RT=([^,]*))?'
                r'(?:,\s*WM=([^,]*))?'
                r'(?:,\s*DT="([^"]*)")?'
                r'(?:,\s*GT=([^,]*))?'
                r'[^;]*;', re.IGNORECASE
            )
        }
    
    def parse_mml_line(self, line: str) -> Dict[str, Any]:
        """Parse a single MML command line into a dictionary."""
        # Remove comments and whitespace
        line = line.strip()
        if line.startswith('/*') or not line:
            return {}
        
        # Extract command type
        if line.startswith('USE ME:'):
            # Parse MEID
            meid_match = re.search(r'MEID=(\d+)', line)
            if meid_match:
                return {"command": "USE_ME", "meid": int(meid_match.group(1)), "full_mml": line}
        
        # Diameter commands
        elif line.startswith('ADD DMPEER:'):
            # Parse Diameter Peer
            params = self._parse_parameters(line)
            return {
                "command": "ADD_DMPEER",
                "name": params.get("DN", "").strip('"'),
                "type": params.get("PRTTYPE", "").strip('"'),
                "interface": params.get("DEVTP", "").strip('"'),
                "hn": params.get("HN", "").strip('"'),
                "realm": params.get("RN", "").strip('"'),
                "fcinswt": params.get("FCINSWT", "").strip('"'),
                "fcoutswt": params.get("FCOUTSWT", "").strip('"'),
                "binding_flag": params.get("BINDINGFLAG", "").strip('"'),
                "diameter_peer_pp_name": params.get("DIAMPEERPPNAME", "").strip('"'),
                "full_mml": line
            }
        
        elif line.startswith('ADD DMLKS:'):
            # Parse Diameter Link Set
            params = self._parse_parameters(line)
            return {
                "command": "ADD_DMLKS",
                "name": params.get("LKSNAME", "").strip('"'),
                "da_name": params.get("DANAME", "").strip('"'),
                "destination_name": params.get("DN", "").strip('"'),
                "load_sharing_mode": params.get("LKSM", "").strip('"'),
                "full_mml": line
            }
        
        elif line.startswith('ADD DMLNK:'):
            # Parse Diameter Link
            params = self._parse_parameters(line)
            return {
                "command": "ADD_DMLNK",
                "name": params.get("LNKNAME", "").strip('"'),
                "link_set_name": params.get("LKSNAME", "").strip('"'),
                "mid": int(params.get("MID", 0)) if params.get("MID") else 0,
                "protocol_type": params.get("PTYPE", "").strip('"'),
                "working_mode": params.get("WMODE", "").strip('"'),
                "ip_type": params.get("IPTP", "").strip('"'),
                "address_id": params.get("ADDRID1", "").strip('"'),
                "local_port": int(params.get("LPORT", 0)) if params.get("LPORT") else 0,
                "register_port_flag": params.get("REGPORTFLAG", "").strip('"'),
                "peer_ip": params.get("PIP41", "").strip('"'),
                "peer_port": int(params.get("PPORT", 0)) if params.get("PPORT") else 0,
                "sctp_parameter_name": params.get("SCTPPARANAME", "").strip('"'),
                "full_mml": line
            }
        
        # Parse using STP/SCCP patterns
        for pattern_name, pattern in self.mml_patterns.items():
            match = pattern.match(line)
            if match:
                return self._parse_stp_sccp_command(pattern_name, match, line)
        
        return {}
    
    def _parse_stp_sccp_command(self, pattern_name: str, match, line: str) -> Dict[str, Any]:
        """Parse STP/SCCP commands using regex matches."""
        groups = match.groups()
        
        if pattern_name == "ADD_N7DSP":
            return {
                "command": "ADD_N7DSP",
                "standard_name": groups[0] or "",
                "node_point_code": groups[1] or "",
                "sua_point": groups[2] or "",
                "timer_name": groups[3] or "",
                "logical_network_name": groups[4] or "",
                "full_mml": line
            }
        
        elif pattern_name == "ADD_N7LKS":
            return {
                "command": "ADD_N7LKS",
                "link_set_name": groups[0] or "",
                "asp_name": groups[1] or "",
                "office_name": groups[2] or "",
                "network_indicator": groups[3] or "",
                "sls": groups[4] or "",
                "warning_network_name": groups[5] or "",
                "timer_name": groups[6] or "",
                "route_restriction_test": groups[7] or "",
                "cluster_policy": groups[8] or "",
                "screening": groups[9] or "",
                "full_mml": line
            }
        
        elif pattern_name == "ADD_N7LNK":
            return {
                "command": "ADD_N7LNK",
                "link_name": groups[0] or "",
                "link_set_name": groups[1] or "",
                "connection_type": groups[2] or "",
                "media_id": groups[3] or "",
                "signaling_link_code": groups[4] or "",
                "timer_name": groups[5] or "",
                "ip_type": groups[6] or "",
                "address_id": groups[7] or "",
                "local_port": groups[8] or "",
                "remote_ip": groups[9] or "",
                "remote_port": groups[10] or "",
                "connection_state": groups[11] or "",
                "register_port_flag": groups[12] or "",
                "sctp_name": groups[13] or "",
                "full_mml": line
            }
        
        elif pattern_name == "ADD_N7RT":
            return {
                "command": "ADD_N7RT",
                "route_name": groups[0] or "",
                "link_set_name": groups[1] or "",
                "destination_point_name": groups[2] or "",
                "timer_name": groups[3] or "",
                "full_mml": line
            }
        
        elif pattern_name == "ADD_M2AS":
            return {
                "command": "ADD_M2AS",
                "application_server_name": groups[0] or "",
                "network_indicator": groups[1] or "",
                "destination_point_code_table": groups[2] or "",
                "full_mml": line
            }
        
        elif pattern_name == "ADD_M2LKS":
            return {
                "command": "ADD_M2LKS",
                "link_set_name": groups[0] or "",
                "application_server_name": groups[1] or "",
                "office_name": groups[2] or "",
                "timer_name": groups[3] or "",
                "route_restriction_test": groups[4] or "",
                "cluster_policy": groups[5] or "",
                "screening": groups[6] or "",
                "full_mml": line
            }
        
        elif pattern_name == "ADD_M2LNK":
            return {
                "command": "ADD_M2LNK",
                "link_name": groups[0] or "",
                "link_set_name": groups[1] or "",
                "media_id": groups[2] or "",
                "ip_type": groups[3] or "",
                "address_id": groups[4] or "",
                "local_port": groups[5] or "",
                "remote_ip": groups[6] or "",
                "remote_port": groups[7] or "",
                "connection_state": groups[8] or "",
                "register_port_flag": groups[9] or "",
                "sctp_name": groups[10] or "",
                "timer_name": groups[11] or "",
                "full_mml": line
            }
        
        elif pattern_name == "ADD_M2RT":
            return {
                "command": "ADD_M2RT",
                "route_name": groups[0] or "",
                "application_server_name": groups[1] or "",
                "link_set_name": groups[2] or "",
                "full_mml": line
            }
        
        elif pattern_name == "ADD_M3AS":
            return {
                "command": "ADD_M3AS",
                "application_server_name": groups[0] or "",
                "network_indicator": groups[1] or "",
                "destination_point_code_table": groups[2] or "",
                "full_mml": line
            }
        
        elif pattern_name == "ADD_M3LKS":
            return {
                "command": "ADD_M3LKS",
                "link_set_name": groups[0] or "",
                "application_server_name": groups[1] or "",
                "office_name": groups[2] or "",
                "timer_name": groups[3] or "",
                "route_restriction_test": groups[4] or "",
                "cluster_policy": groups[5] or "",
                "screening": groups[6] or "",
                "full_mml": line
            }
        
        elif pattern_name == "ADD_M3LNK":
            return {
                "command": "ADD_M3LNK",
                "link_name": groups[0] or "",
                "link_set_name": groups[1] or "",
                "media_id": groups[2] or "",
                "ip_type": groups[3] or "",
                "address_id": groups[4] or "",
                "local_port": groups[5] or "",
                "remote_ip": groups[6] or "",
                "remote_port": groups[7] or "",
                "connection_state": groups[8] or "",
                "register_port_flag": groups[9] or "",
                "sctp_name": groups[10] or "",
                "timer_name": groups[11] or "",
                "full_mml": line
            }
        
        elif pattern_name == "ADD_M3RT":
            return {
                "command": "ADD_M3RT",
                "route_name": groups[0] or "",
                "application_server_name": groups[1] or "",
                "link_set_name": groups[2] or "",
                "full_mml": line
            }
        
        elif pattern_name == "ADD_SCCPSSN":
            return {
                "command": "ADD_SCCPSSN",
                "subsystem_name": groups[0] or "",
                "network_indicator": groups[1] or "",
                "subsystem_number": groups[2] or "",
                "destination_name": groups[3] or "",
                "full_mml": line
            }
        
        elif pattern_name == "ADD_SCCPGT":
            return {
                "command": "ADD_SCCPGT",
                "global_title_name": groups[0] or "",
                "network_indicator": groups[1] or "",
                "routing_type": groups[2] or "",
                "working_mode": groups[3] or "",
                "destination_table": groups[4] or "",
                "address_field": groups[5] or "",
                "full_mml": line
            }
        
        return {}
    
    def _parse_parameters(self, line: str) -> Dict[str, str]:
        """Extract parameters from MML command line."""
        # Find the part after the colon
        if ':' in line:
            params_part = line.split(':', 1)[1].strip()
            # Remove trailing semicolon
            if params_part.endswith(';'):
                params_part = params_part[:-1]
            
            # Parse key=value pairs
            params = {}
            # Handle quoted values and unquoted values
            pattern = r'(\w+)=(".*?"|[^,\s]+)'
            matches = re.findall(pattern, params_part)
            
            for key, value in matches:
                params[key] = value
            
            return params
        
        return {}
    
    def parse_file(self) -> Dict[str, Any]:
        """Parse the entire MML file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            for line in lines:
                parsed = self.parse_mml_line(line)
                
                if parsed.get("command") == "USE_ME":
                    self.config["metadata"]["meid"] = parsed.get("meid")
                
                # Diameter commands
                elif parsed.get("command") == "ADD_DMPEER":
                    self.config["diameter_peers"].append({
                        "name": parsed.get("name"),
                        "type": parsed.get("type"),
                        "interface": parsed.get("interface"),
                        "hn": parsed.get("hn"),
                        "realm": parsed.get("realm"),
                        "fcinswt": parsed.get("fcinswt"),
                        "fcoutswt": parsed.get("fcoutswt"),
                        "binding_flag": parsed.get("binding_flag"),
                        "diameter_peer_pp_name": parsed.get("diameter_peer_pp_name"),
                        "full_mml": parsed.get("full_mml")
                    })
                
                elif parsed.get("command") == "ADD_DMLKS":
                    self.config["diameter_link_sets"].append({
                        "name": parsed.get("name"),
                        "da_name": parsed.get("da_name"),
                        "destination_name": parsed.get("destination_name"),
                        "load_sharing_mode": parsed.get("load_sharing_mode"),
                        "full_mml": parsed.get("full_mml")
                    })
                
                elif parsed.get("command") == "ADD_DMLNK":
                    self.config["diameter_links"].append({
                        "name": parsed.get("name"),
                        "link_set_name": parsed.get("link_set_name"),
                        "mid": parsed.get("mid"),
                        "protocol_type": parsed.get("protocol_type"),
                        "working_mode": parsed.get("working_mode"),
                        "ip_type": parsed.get("ip_type"),
                        "address_id": parsed.get("address_id"),
                        "local_port": parsed.get("local_port"),
                        "register_port_flag": parsed.get("register_port_flag"),
                        "peer_ip": parsed.get("peer_ip"),
                        "peer_port": parsed.get("peer_port"),
                        "sctp_parameter_name": parsed.get("sctp_parameter_name"),
                        "full_mml": parsed.get("full_mml")
                    })
                
                # MTP commands
                elif parsed.get("command") == "ADD_N7DSP":
                    self.config["mtp_destination_points"].append({
                        "standard_name": parsed.get("standard_name"),
                        "node_point_code": parsed.get("node_point_code"),
                        "sua_point": parsed.get("sua_point"),
                        "timer_name": parsed.get("timer_name"),
                        "logical_network_name": parsed.get("logical_network_name"),
                        "full_mml": parsed.get("full_mml")
                    })
                
                elif parsed.get("command") == "ADD_N7LKS":
                    self.config["mtp_link_sets"].append({
                        "link_set_name": parsed.get("link_set_name"),
                        "asp_name": parsed.get("asp_name"),
                        "office_name": parsed.get("office_name"),
                        "network_indicator": parsed.get("network_indicator"),
                        "sls": parsed.get("sls"),
                        "warning_network_name": parsed.get("warning_network_name"),
                        "timer_name": parsed.get("timer_name"),
                        "route_restriction_test": parsed.get("route_restriction_test"),
                        "cluster_policy": parsed.get("cluster_policy"),
                        "screening": parsed.get("screening"),
                        "full_mml": parsed.get("full_mml")
                    })
                
                elif parsed.get("command") == "ADD_N7LNK":
                    self.config["mtp_links"].append({
                        "link_name": parsed.get("link_name"),
                        "link_set_name": parsed.get("link_set_name"),
                        "connection_type": parsed.get("connection_type"),
                        "media_id": parsed.get("media_id"),
                        "signaling_link_code": parsed.get("signaling_link_code"),
                        "timer_name": parsed.get("timer_name"),
                        "ip_type": parsed.get("ip_type"),
                        "address_id": parsed.get("address_id"),
                        "local_port": parsed.get("local_port"),
                        "remote_ip": parsed.get("remote_ip"),
                        "remote_port": parsed.get("remote_port"),
                        "connection_state": parsed.get("connection_state"),
                        "register_port_flag": parsed.get("register_port_flag"),
                        "sctp_name": parsed.get("sctp_name"),
                        "full_mml": parsed.get("full_mml")
                    })
                
                elif parsed.get("command") == "ADD_N7RT":
                    self.config["mtp_routes"].append({
                        "route_name": parsed.get("route_name"),
                        "link_set_name": parsed.get("link_set_name"),
                        "destination_point_name": parsed.get("destination_point_name"),
                        "timer_name": parsed.get("timer_name"),
                        "full_mml": parsed.get("full_mml")
                    })
                
                # M2UA commands
                elif parsed.get("command") == "ADD_M2AS":
                    self.config["m2ua_application_servers"].append({
                        "application_server_name": parsed.get("application_server_name"),
                        "network_indicator": parsed.get("network_indicator"),
                        "destination_point_code_table": parsed.get("destination_point_code_table"),
                        "full_mml": parsed.get("full_mml")
                    })
                
                elif parsed.get("command") == "ADD_M2LKS":
                    self.config["m2ua_link_sets"].append({
                        "link_set_name": parsed.get("link_set_name"),
                        "application_server_name": parsed.get("application_server_name"),
                        "office_name": parsed.get("office_name"),
                        "timer_name": parsed.get("timer_name"),
                        "route_restriction_test": parsed.get("route_restriction_test"),
                        "cluster_policy": parsed.get("cluster_policy"),
                        "screening": parsed.get("screening"),
                        "full_mml": parsed.get("full_mml")
                    })
                
                elif parsed.get("command") == "ADD_M2LNK":
                    self.config["m2ua_links"].append({
                        "link_name": parsed.get("link_name"),
                        "link_set_name": parsed.get("link_set_name"),
                        "media_id": parsed.get("media_id"),
                        "ip_type": parsed.get("ip_type"),
                        "address_id": parsed.get("address_id"),
                        "local_port": parsed.get("local_port"),
                        "remote_ip": parsed.get("remote_ip"),
                        "remote_port": parsed.get("remote_port"),
                        "connection_state": parsed.get("connection_state"),
                        "register_port_flag": parsed.get("register_port_flag"),
                        "sctp_name": parsed.get("sctp_name"),
                        "timer_name": parsed.get("timer_name"),
                        "full_mml": parsed.get("full_mml")
                    })
                
                elif parsed.get("command") == "ADD_M2RT":
                    self.config["m2ua_routes"].append({
                        "route_name": parsed.get("route_name"),
                        "application_server_name": parsed.get("application_server_name"),
                        "link_set_name": parsed.get("link_set_name"),
                        "full_mml": parsed.get("full_mml")
                    })
                
                # M3UA commands
                elif parsed.get("command") == "ADD_M3AS":
                    self.config["m3ua_application_servers"].append({
                        "application_server_name": parsed.get("application_server_name"),
                        "network_indicator": parsed.get("network_indicator"),
                        "destination_point_code_table": parsed.get("destination_point_code_table"),
                        "full_mml": parsed.get("full_mml")
                    })
                
                elif parsed.get("command") == "ADD_M3LKS":
                    self.config["m3ua_link_sets"].append({
                        "link_set_name": parsed.get("link_set_name"),
                        "application_server_name": parsed.get("application_server_name"),
                        "office_name": parsed.get("office_name"),
                        "timer_name": parsed.get("timer_name"),
                        "route_restriction_test": parsed.get("route_restriction_test"),
                        "cluster_policy": parsed.get("cluster_policy"),
                        "screening": parsed.get("screening"),
                        "full_mml": parsed.get("full_mml")
                    })
                
                elif parsed.get("command") == "ADD_M3LNK":
                    self.config["m3ua_links"].append({
                        "link_name": parsed.get("link_name"),
                        "link_set_name": parsed.get("link_set_name"),
                        "media_id": parsed.get("media_id"),
                        "ip_type": parsed.get("ip_type"),
                        "address_id": parsed.get("address_id"),
                        "local_port": parsed.get("local_port"),
                        "remote_ip": parsed.get("remote_ip"),
                        "remote_port": parsed.get("remote_port"),
                        "connection_state": parsed.get("connection_state"),
                        "register_port_flag": parsed.get("register_port_flag"),
                        "sctp_name": parsed.get("sctp_name"),
                        "timer_name": parsed.get("timer_name"),
                        "full_mml": parsed.get("full_mml")
                    })
                
                elif parsed.get("command") == "ADD_M3RT":
                    self.config["m3ua_routes"].append({
                        "route_name": parsed.get("route_name"),
                        "application_server_name": parsed.get("application_server_name"),
                        "link_set_name": parsed.get("link_set_name"),
                        "full_mml": parsed.get("full_mml")
                    })
                
                # SCCP commands
                elif parsed.get("command") == "ADD_SCCPSSN":
                    self.config["sccp_subsystems"].append({
                        "subsystem_name": parsed.get("subsystem_name"),
                        "network_indicator": parsed.get("network_indicator"),
                        "subsystem_number": parsed.get("subsystem_number"),
                        "destination_name": parsed.get("destination_name"),
                        "full_mml": parsed.get("full_mml")
                    })
                
                elif parsed.get("command") == "ADD_SCCPGT":
                    self.config["sccp_global_titles"].append({
                        "global_title_name": parsed.get("global_title_name"),
                        "network_indicator": parsed.get("network_indicator"),
                        "routing_type": parsed.get("routing_type"),
                        "working_mode": parsed.get("working_mode"),
                        "destination_table": parsed.get("destination_table"),
                        "address_field": parsed.get("address_field"),
                        "full_mml": parsed.get("full_mml")
                    })
            
            # Update metadata
            self.config["metadata"]["total_peers"] = len(self.config["diameter_peers"])
            self.config["metadata"]["total_link_sets"] = (
                len(self.config["diameter_link_sets"]) + 
                len(self.config["mtp_link_sets"]) + 
                len(self.config["m2ua_link_sets"]) + 
                len(self.config["m3ua_link_sets"])
            )
            self.config["metadata"]["total_links"] = (
                len(self.config["diameter_links"]) + 
                len(self.config["mtp_links"]) + 
                len(self.config["m2ua_links"]) + 
                len(self.config["m3ua_links"])
            )
            self.config["metadata"]["total_network_points"] = (
                len(self.config["mtp_destination_points"]) + 
                len(self.config["m2ua_application_servers"]) + 
                len(self.config["m3ua_application_servers"])
            )
            
            # Build hierarchical structure
            self._build_hierarchical_structure()
            
            # Extract IP and port metadata
            self._extract_ip_port_metadata()
            
            return self.config
        
        except FileNotFoundError:
            print(f"Error: File '{self.file_path}' not found.")
            return self.config
        except Exception as e:
            print(f"Error parsing file: {e}")
            return self.config
    
    def parse_files(self) -> Dict[str, Any]:
        """Parse multiple files using file patterns."""
        for pattern in self.file_patterns:
            files = glob.glob(pattern)
            for file_path in files:
                print(f"Processing file: {file_path}")
                self.file_path = file_path
                self.parse_file()
        
        return self.config
    
    def _build_hierarchical_structure(self):
        """Build a hierarchical structure showing relationships between all types of links."""
        hierarchical = {}
        
        # Build Diameter hierarchy: Peers → LinkSets → Links
        for peer in self.config["diameter_peers"]:
            peer_name = peer["name"]
            hierarchical[peer_name] = {
                "type": "DIAMETER_PEER",
                "peer_info": {
                    "name": peer["name"],
                    "type": peer["type"],
                    "interface": peer["interface"],
                    "hn": peer["hn"],
                    "realm": peer["realm"],
                    "full_mml": peer["full_mml"]
                },
                "link_sets": {},
                "total_link_sets": 0,
                "total_links": 0
            }
        
        # Add diameter link sets under their corresponding peers
        for link_set in self.config["diameter_link_sets"]:
            destination_name = link_set["destination_name"]
            if destination_name in hierarchical:
                link_set_name = link_set["name"]
                hierarchical[destination_name]["link_sets"][link_set_name] = {
                    "type": "DIAMETER_LINKSET",
                    "link_set_info": {
                        "name": link_set["name"],
                        "da_name": link_set["da_name"],
                        "destination_name": link_set["destination_name"],
                        "load_sharing_mode": link_set["load_sharing_mode"],
                        "full_mml": link_set["full_mml"]
                    },
                    "links": [],
                    "total_links": 0
                }
                hierarchical[destination_name]["total_link_sets"] += 1
        
        # Add diameter links under their corresponding link sets
        for link in self.config["diameter_links"]:
            link_set_name = link["link_set_name"]
            
            # Find which peer this link set belongs to
            for peer_name, peer_data in hierarchical.items():
                if peer_data.get("type") == "DIAMETER_PEER" and link_set_name in peer_data["link_sets"]:
                    link_info = {
                        "type": "DIAMETER_LINK",
                        "name": link["name"],
                        "mid": link["mid"],
                        "protocol_type": link["protocol_type"],
                        "working_mode": link["working_mode"],
                        "ip_type": link["ip_type"],
                        "address_id": link["address_id"],
                        "local_port": link["local_port"],
                        "peer_ip": link["peer_ip"],
                        "peer_port": link["peer_port"],
                        "register_port_flag": link["register_port_flag"],
                        "sctp_parameter_name": link["sctp_parameter_name"],
                        "full_mml": link["full_mml"]
                    }
                    
                    hierarchical[peer_name]["link_sets"][link_set_name]["links"].append(link_info)
                    hierarchical[peer_name]["link_sets"][link_set_name]["total_links"] += 1
                    hierarchical[peer_name]["total_links"] += 1
                    break
        
        # Build MTP hierarchy: DSP → LinkSets → Links → Routes
        for dsp in self.config["mtp_destination_points"]:
            dsp_name = dsp["standard_name"]
            hierarchical[dsp_name] = {
                "type": "MTP_DSP",
                "dsp_info": {
                    "standard_name": dsp["standard_name"],
                    "node_point_code": dsp["node_point_code"],
                    "sua_point": dsp["sua_point"],
                    "timer_name": dsp["timer_name"],
                    "logical_network_name": dsp["logical_network_name"],
                    "full_mml": dsp["full_mml"]
                },
                "link_sets": {},
                "routes": [],
                "total_link_sets": 0,
                "total_links": 0,
                "total_routes": 0
            }
        
        # Add MTP link sets
        for lks in self.config["mtp_link_sets"]:
            asp_name = lks["asp_name"]
            if asp_name in hierarchical:
                link_set_name = lks["link_set_name"]
                hierarchical[asp_name]["link_sets"][link_set_name] = {
                    "type": "MTP_LINKSET",
                    "link_set_info": {
                        "link_set_name": lks["link_set_name"],
                        "asp_name": lks["asp_name"],
                        "office_name": lks["office_name"],
                        "network_indicator": lks["network_indicator"],
                        "sls": lks["sls"],
                        "warning_network_name": lks["warning_network_name"],
                        "timer_name": lks["timer_name"],
                        "route_restriction_test": lks["route_restriction_test"],
                        "cluster_policy": lks["cluster_policy"],
                        "screening": lks["screening"],
                        "full_mml": lks["full_mml"]
                    },
                    "links": [],
                    "total_links": 0
                }
                hierarchical[asp_name]["total_link_sets"] += 1
        
        # Add MTP links
        for link in self.config["mtp_links"]:
            link_set_name = link["link_set_name"]
            
            for dsp_name, dsp_data in hierarchical.items():
                if dsp_data.get("type") == "MTP_DSP" and link_set_name in dsp_data["link_sets"]:
                    link_info = {
                        "type": "MTP_LINK",
                        "link_name": link["link_name"],
                        "connection_type": link["connection_type"],
                        "media_id": link["media_id"],
                        "signaling_link_code": link["signaling_link_code"],
                        "timer_name": link["timer_name"],
                        "ip_type": link["ip_type"],
                        "address_id": link["address_id"],
                        "local_port": link["local_port"],
                        "remote_ip": link["remote_ip"],
                        "remote_port": link["remote_port"],
                        "connection_state": link["connection_state"],
                        "register_port_flag": link["register_port_flag"],
                        "sctp_name": link["sctp_name"],
                        "full_mml": link["full_mml"]
                    }
                    
                    hierarchical[dsp_name]["link_sets"][link_set_name]["links"].append(link_info)
                    hierarchical[dsp_name]["link_sets"][link_set_name]["total_links"] += 1
                    hierarchical[dsp_name]["total_links"] += 1
                    break
        
        # Add MTP routes
        for route in self.config["mtp_routes"]:
            dp_name = route["destination_point_name"]
            if dp_name in hierarchical and hierarchical[dp_name].get("type") == "MTP_DSP":
                route_info = {
                    "type": "MTP_ROUTE",
                    "route_name": route["route_name"],
                    "link_set_name": route["link_set_name"],
                    "destination_point_name": route["destination_point_name"],
                    "timer_name": route["timer_name"],
                    "full_mml": route["full_mml"]
                }
                hierarchical[dp_name]["routes"].append(route_info)
                hierarchical[dp_name]["total_routes"] += 1
        
        # Build M2UA hierarchy: Application Server → LinkSets → Links
        for app_server in self.config["m2ua_application_servers"]:
            as_name = app_server["application_server_name"]
            hierarchical[as_name] = {
                "type": "M2UA_AS",
                "as_info": {
                    "application_server_name": app_server["application_server_name"],
                    "network_indicator": app_server["network_indicator"],
                    "destination_point_code_table": app_server["destination_point_code_table"],
                    "full_mml": app_server["full_mml"]
                },
                "link_sets": {},
                "routes": [],
                "total_link_sets": 0,
                "total_links": 0,
                "total_routes": 0
            }
        
        # Add M2UA link sets
        for lks in self.config["m2ua_link_sets"]:
            as_name = lks["application_server_name"]
            if as_name in hierarchical:
                link_set_name = lks["link_set_name"]
                hierarchical[as_name]["link_sets"][link_set_name] = {
                    "type": "M2UA_LINKSET",
                    "link_set_info": {
                        "link_set_name": lks["link_set_name"],
                        "application_server_name": lks["application_server_name"],
                        "office_name": lks["office_name"],
                        "timer_name": lks["timer_name"],
                        "route_restriction_test": lks["route_restriction_test"],
                        "cluster_policy": lks["cluster_policy"],
                        "screening": lks["screening"],
                        "full_mml": lks["full_mml"]
                    },
                    "links": [],
                    "total_links": 0
                }
                hierarchical[as_name]["total_link_sets"] += 1
        
        # Add M2UA links
        for link in self.config["m2ua_links"]:
            link_set_name = link["link_set_name"]
            
            for as_name, as_data in hierarchical.items():
                if as_data.get("type") == "M2UA_AS" and link_set_name in as_data["link_sets"]:
                    link_info = {
                        "type": "M2UA_LINK",
                        "link_name": link["link_name"],
                        "media_id": link["media_id"],
                        "ip_type": link["ip_type"],
                        "address_id": link["address_id"],
                        "local_port": link["local_port"],
                        "remote_ip": link["remote_ip"],
                        "remote_port": link["remote_port"],
                        "connection_state": link["connection_state"],
                        "register_port_flag": link["register_port_flag"],
                        "sctp_name": link["sctp_name"],
                        "timer_name": link["timer_name"],
                        "full_mml": link["full_mml"]
                    }
                    
                    hierarchical[as_name]["link_sets"][link_set_name]["links"].append(link_info)
                    hierarchical[as_name]["link_sets"][link_set_name]["total_links"] += 1
                    hierarchical[as_name]["total_links"] += 1
                    break
        
        # Add M2UA routes
        for route in self.config["m2ua_routes"]:
            as_name = route["application_server_name"]
            if as_name in hierarchical and hierarchical[as_name].get("type") == "M2UA_AS":
                route_info = {
                    "type": "M2UA_ROUTE",
                    "route_name": route["route_name"],
                    "application_server_name": route["application_server_name"],
                    "link_set_name": route["link_set_name"],
                    "full_mml": route["full_mml"]
                }
                hierarchical[as_name]["routes"].append(route_info)
                hierarchical[as_name]["total_routes"] += 1
        
        # Build M3UA hierarchy: Application Server → LinkSets → Links
        for app_server in self.config["m3ua_application_servers"]:
            as_name = app_server["application_server_name"]
            hierarchical[as_name] = {
                "type": "M3UA_AS",
                "as_info": {
                    "application_server_name": app_server["application_server_name"],
                    "network_indicator": app_server["network_indicator"],
                    "destination_point_code_table": app_server["destination_point_code_table"],
                    "full_mml": app_server["full_mml"]
                },
                "link_sets": {},
                "routes": [],
                "total_link_sets": 0,
                "total_links": 0,
                "total_routes": 0
            }
        
        # Add M3UA link sets
        for lks in self.config["m3ua_link_sets"]:
            as_name = lks["application_server_name"]
            if as_name in hierarchical:
                link_set_name = lks["link_set_name"]
                hierarchical[as_name]["link_sets"][link_set_name] = {
                    "type": "M3UA_LINKSET",
                    "link_set_info": {
                        "link_set_name": lks["link_set_name"],
                        "application_server_name": lks["application_server_name"],
                        "office_name": lks["office_name"],
                        "timer_name": lks["timer_name"],
                        "route_restriction_test": lks["route_restriction_test"],
                        "cluster_policy": lks["cluster_policy"],
                        "screening": lks["screening"],
                        "full_mml": lks["full_mml"]
                    },
                    "links": [],
                    "total_links": 0
                }
                hierarchical[as_name]["total_link_sets"] += 1
        
        # Add M3UA links
        for link in self.config["m3ua_links"]:
            link_set_name = link["link_set_name"]
            
            for as_name, as_data in hierarchical.items():
                if as_data.get("type") == "M3UA_AS" and link_set_name in as_data["link_sets"]:
                    link_info = {
                        "type": "M3UA_LINK",
                        "link_name": link["link_name"],
                        "media_id": link["media_id"],
                        "ip_type": link["ip_type"],
                        "address_id": link["address_id"],
                        "local_port": link["local_port"],
                        "remote_ip": link["remote_ip"],
                        "remote_port": link["remote_port"],
                        "connection_state": link["connection_state"],
                        "register_port_flag": link["register_port_flag"],
                        "sctp_name": link["sctp_name"],
                        "timer_name": link["timer_name"],
                        "full_mml": link["full_mml"]
                    }
                    
                    hierarchical[as_name]["link_sets"][link_set_name]["links"].append(link_info)
                    hierarchical[as_name]["link_sets"][link_set_name]["total_links"] += 1
                    hierarchical[as_name]["total_links"] += 1
                    break
        
        # Add M3UA routes
        for route in self.config["m3ua_routes"]:
            as_name = route["application_server_name"]
            if as_name in hierarchical and hierarchical[as_name].get("type") == "M3UA_AS":
                route_info = {
                    "type": "M3UA_ROUTE",
                    "route_name": route["route_name"],
                    "application_server_name": route["application_server_name"],
                    "link_set_name": route["link_set_name"],
                    "full_mml": route["full_mml"]
                }
                hierarchical[as_name]["routes"].append(route_info)
                hierarchical[as_name]["total_routes"] += 1
        
        # Build SCCP layer as separate section with chained relationships
        if self.config["sccp_subsystems"] or self.config["sccp_global_titles"]:
            sccp_layer = {
                "type": "SCCP_LAYER",
                "subsystems": self.config["sccp_subsystems"],
                "global_titles": [],
                "total_subsystems": len(self.config["sccp_subsystems"]),
                "total_global_titles": len(self.config["sccp_global_titles"])
            }
            
            # Build Global Title chains: GT → Destination Table → M3UA/MTP
            for gt in self.config["sccp_global_titles"]:
                gt_chain = {
                    "gt_info": gt,
                    "destination_chain": None
                }
                
                # Find the destination table (which should be an M3UA AS or MTP DSP)
                destination_table = gt["destination_table"]
                
                # Look for matching M3UA Application Server
                for as_name, as_data in hierarchical.items():
                    if as_data.get("type") == "M3UA_AS" and as_name == destination_table:
                        gt_chain["destination_chain"] = {
                            "destination_type": "M3UA_AS",
                            "destination_name": as_name,
                            "destination_info": as_data["as_info"],
                            "link_sets": as_data["link_sets"],
                            "routes": as_data["routes"],
                            "total_links": as_data["total_links"]
                        }
                        break
                
                # If not found in M3UA, look for matching MTP DSP
                if not gt_chain["destination_chain"]:
                    for dsp_name, dsp_data in hierarchical.items():
                        if dsp_data.get("type") == "MTP_DSP" and dsp_name == destination_table:
                            gt_chain["destination_chain"] = {
                                "destination_type": "MTP_DSP",
                                "destination_name": dsp_name,
                                "destination_info": dsp_data["dsp_info"],
                                "link_sets": dsp_data["link_sets"],
                                "routes": dsp_data["routes"],
                                "total_links": dsp_data["total_links"]
                            }
                            break
                
                # If still not found, mark as unresolved
                if not gt_chain["destination_chain"]:
                    gt_chain["destination_chain"] = {
                        "destination_type": "UNRESOLVED",
                        "destination_name": destination_table,
                        "destination_info": None,
                        "link_sets": {},
                        "routes": [],
                        "total_links": 0
                    }
                
                sccp_layer["global_titles"].append(gt_chain)
            
            hierarchical["SCCP_LAYER"] = sccp_layer
        
        self.config["hierarchical_structure"] = hierarchical

    def _extract_ip_port_metadata(self):
        """Extract and organize IP and port information for metadata."""
        all_ips = []
        all_ports = []
        all_ip_port_pairs = []
        unique_networks = set()
        unique_point_codes = set()
        ip_port_pairs = set()
        
        # Extract from diameter links
        for link in self.config["diameter_links"]:
            peer_ip = link.get("peer_ip")
            peer_port = link.get("peer_port")
            local_port = link.get("local_port")
            
            if peer_ip:
                all_ips.append(peer_ip)
                if peer_port:
                    all_ports.append(peer_port)
                    all_ip_port_pairs.append(f"{peer_ip}:{peer_port}")
                    ip_port_pairs.add(f"{peer_ip}:{peer_port}")
                if local_port:
                    all_ports.append(local_port)
        
        # Extract from MTP links
        for link in self.config["mtp_links"]:
            if link.get("remote_ip"):
                all_ips.append(link["remote_ip"])
                if link.get("remote_port"):
                    all_ports.append(int(link["remote_port"]))
                    ip_port_pairs.add(f"{link['remote_ip']}:{link['remote_port']}")
            if link.get("local_port"):
                all_ports.append(int(link["local_port"]))
        
        # Extract from M2UA links
        for link in self.config["m2ua_links"]:
            if link.get("remote_ip"):
                all_ips.append(link["remote_ip"])
                if link.get("remote_port"):
                    all_ports.append(int(link["remote_port"]))
                    ip_port_pairs.add(f"{link['remote_ip']}:{link['remote_port']}")
            if link.get("local_port"):
                all_ports.append(int(link["local_port"]))
        
        # Extract from M3UA links
        for link in self.config["m3ua_links"]:
            if link.get("remote_ip"):
                all_ips.append(link["remote_ip"])
                if link.get("remote_port"):
                    all_ports.append(int(link["remote_port"]))
                    ip_port_pairs.add(f"{link['remote_ip']}:{link['remote_port']}")
            if link.get("local_port"):
                all_ports.append(int(link["local_port"]))
        
        # Extract from MTP destination points
        for dsp in self.config["mtp_destination_points"]:
            if dsp.get("node_point_code"):
                unique_point_codes.add(dsp["node_point_code"])
            if dsp.get("logical_network_name"):
                unique_networks.add(dsp["logical_network_name"])
        
        # Update metadata with all collections and unique sets
        self.config["metadata"]["all_ips"] = all_ips
        self.config["metadata"]["all_ports"] = all_ports
        self.config["metadata"]["all_ip_port_pairs"] = all_ip_port_pairs
        self.config["metadata"]["unique_ips"] = sorted(list(set(all_ips)))
        self.config["metadata"]["unique_ports"] = sorted(list(set(all_ports)))
        self.config["metadata"]["unique_ip_port_pairs"] = sorted(list(ip_port_pairs))
        self.config["metadata"]["unique_networks"] = unique_networks
        self.config["metadata"]["unique_point_codes"] = unique_point_codes
        self.config["metadata"]["ip_port_pairs"] = ip_port_pairs
    
    def to_json(self, indent: int = 2) -> str:
        """Convert configuration to JSON string."""
        return json.dumps(self.config, indent=indent, ensure_ascii=False)
    
    def save_json(self, output_file: str = "spsdmlinks_config.json"):
        """Save configuration to JSON file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(self.config, file, indent=2, ensure_ascii=False)
            print(f"Configuration saved to '{output_file}'")
        except Exception as e:
            print(f"Error saving JSON file: {e}")
    
    def print_summary(self):
        """Print a summary of the parsed configuration."""
        print("=== SPS Unified Links Configuration Summary ===")
        print(f"MEID: {self.config['metadata']['meid']}")
        
        # Diameter summary
        print(f"\n--- Diameter Configuration ---")
        print(f"Total Diameter Peers: {len(self.config['diameter_peers'])}")
        print(f"Total Diameter Link Sets: {len(self.config['diameter_link_sets'])}")
        print(f"Total Diameter Links: {len(self.config['diameter_links'])}")
        
        # MTP summary
        print(f"\n--- MTP Configuration ---")
        print(f"Total MTP Destination Points: {len(self.config['mtp_destination_points'])}")
        print(f"Total MTP Link Sets: {len(self.config['mtp_link_sets'])}")
        print(f"Total MTP Links: {len(self.config['mtp_links'])}")
        print(f"Total MTP Routes: {len(self.config['mtp_routes'])}")
        
        # M2UA summary
        print(f"\n--- M2UA Configuration ---")
        print(f"Total M2UA Application Servers: {len(self.config['m2ua_application_servers'])}")
        print(f"Total M2UA Link Sets: {len(self.config['m2ua_link_sets'])}")
        print(f"Total M2UA Links: {len(self.config['m2ua_links'])}")
        print(f"Total M2UA Routes: {len(self.config['m2ua_routes'])}")
        
        # M3UA summary
        print(f"\n--- M3UA Configuration ---")
        print(f"Total M3UA Application Servers: {len(self.config['m3ua_application_servers'])}")
        print(f"Total M3UA Link Sets: {len(self.config['m3ua_link_sets'])}")
        print(f"Total M3UA Links: {len(self.config['m3ua_links'])}")
        print(f"Total M3UA Routes: {len(self.config['m3ua_routes'])}")
        
        # SCCP summary
        print(f"\n--- SCCP Configuration ---")
        print(f"Total SCCP Subsystems: {len(self.config['sccp_subsystems'])}")
        print(f"Total SCCP Global Titles: {len(self.config['sccp_global_titles'])}")
        
        # Overall totals
        print(f"\n--- Overall Totals ---")
        print(f"Total Network Points: {self.config['metadata']['total_network_points']}")
        print(f"Total Link Sets: {self.config['metadata']['total_link_sets']}")
        print(f"Total Links: {self.config['metadata']['total_links']}")
        
        # Display IP and Port metadata
        metadata = self.config['metadata']
        print("\n--- Network Endpoints Summary ---")
        print(f"Unique IP addresses: {len(metadata['unique_ips'])} - {metadata['unique_ips']}")
        print(f"Unique ports: {len(metadata['unique_ports'])} - {metadata['unique_ports']}")
        print(f"Unique IP:Port pairs: {len(metadata['unique_ip_port_pairs'])}")
        for pair in metadata['unique_ip_port_pairs']:
            print(f"  • {pair}")
        
        if metadata.get('unique_point_codes'):
            print(f"Unique Point Codes: {len(metadata['unique_point_codes'])} - {sorted(list(metadata['unique_point_codes']))}")
        if metadata.get('unique_networks'):
            print(f"Unique Networks: {len(metadata['unique_networks'])} - {sorted(list(metadata['unique_networks']))}")

    def print_hierarchical_summary(self):
        """Print a hierarchical summary showing relationships for all link types."""
        print("\n=== Unified Network Topology (All Link Types) ===")
        
        hierarchical = self.config.get("hierarchical_structure", {})
        
        for element_name, element_data in hierarchical.items():
            element_type = element_data.get("type", "UNKNOWN")
            
            if element_type == "DIAMETER_PEER":
                peer_info = element_data["peer_info"]
                print(f"\n📡 DIAMETER PEER: {element_name}")
                print(f"   Host: {peer_info['hn']}")
                print(f"   Realm: {peer_info['realm']}")
                print(f"   Interface: {peer_info['interface']}")
                print(f"   Link Sets: {element_data['total_link_sets']}, Total Links: {element_data['total_links']}")
                
                for link_set_name, link_set_data in element_data["link_sets"].items():
                    link_set_info = link_set_data["link_set_info"]
                    print(f"   ├── 🔗 DIAMETER LINK SET: {link_set_name}")
                    print(f"   │   DA Name: {link_set_info['da_name']}")
                    print(f"   │   Load Sharing: {link_set_info['load_sharing_mode']}")
                    print(f"   │   Links: {link_set_data['total_links']}")
                    
                    for i, link in enumerate(link_set_data["links"]):
                        is_last_link = (i == len(link_set_data["links"]) - 1)
                        prefix = "   │   └──" if is_last_link else "   │   ├──"
                        
                        print(f"{prefix} 🔌 DIAMETER LINK: {link['name']}")
                        print(f"   │   {'    ' if is_last_link else '│   '}   MID: {link['mid']}")
                        print(f"   │   {'    ' if is_last_link else '│   '}   Peer: {link['peer_ip']}:{link['peer_port']}")
                        print(f"   │   {'    ' if is_last_link else '│   '}   Local Port: {link['local_port']}")
                        print(f"   │   {'    ' if is_last_link else '│   '}   Protocol: {link['protocol_type']} ({link['working_mode']})")
            
            elif element_type == "MTP_DSP":
                dsp_info = element_data["dsp_info"]
                print(f"\n🏗️ MTP DSP: {element_name}")
                print(f"   Point Code: {dsp_info['node_point_code']}")
                print(f"   Logical Network: {dsp_info['logical_network_name']}")
                print(f"   Link Sets: {element_data['total_link_sets']}, Links: {element_data['total_links']}, Routes: {element_data['total_routes']}")
                
                for link_set_name, link_set_data in element_data["link_sets"].items():
                    link_set_info = link_set_data["link_set_info"]
                    print(f"   ├── 🔗 MTP LINK SET: {link_set_name}")
                    print(f"   │   Network Indicator: {link_set_info['network_indicator']}")
                    print(f"   │   Links: {link_set_data['total_links']}")
                    
                    for link in link_set_data["links"]:
                        print(f"   │       └── 📍 MTP LINK: {link['link_name']} ({link['connection_type']}) → {link['remote_ip']}:{link['remote_port']}")
                
                for route in element_data["routes"]:
                    print(f"   └── 🛣️ MTP ROUTE: {route['route_name']} → {route['link_set_name']}")
            
            elif element_type == "M2UA_AS":
                as_info = element_data["as_info"]
                print(f"\n🌐 M2UA APPLICATION SERVER: {element_name}")
                print(f"   DPCT: {as_info['destination_point_code_table']}")
                print(f"   Link Sets: {element_data['total_link_sets']}, Links: {element_data['total_links']}, Routes: {element_data['total_routes']}")
                
                for link_set_name, link_set_data in element_data["link_sets"].items():
                    print(f"   ├── 🔗 M2UA LINK SET: {link_set_name}")
                    print(f"   │   Links: {link_set_data['total_links']}")
                    
                    for link in link_set_data["links"]:
                        print(f"   │       └── 📍 M2UA LINK: {link['link_name']} → {link['remote_ip']}:{link['remote_port']}")
                
                for route in element_data["routes"]:
                    print(f"   └── 🛣️ M2UA ROUTE: {route['route_name']} → {route['link_set_name']}")
            
            elif element_type == "M3UA_AS":
                as_info = element_data["as_info"]
                print(f"\n🌍 M3UA APPLICATION SERVER: {element_name}")
                print(f"   DPCT: {as_info['destination_point_code_table']}")
                print(f"   Link Sets: {element_data['total_link_sets']}, Links: {element_data['total_links']}, Routes: {element_data['total_routes']}")
                
                for link_set_name, link_set_data in element_data["link_sets"].items():
                    print(f"   ├── 🔗 M3UA LINK SET: {link_set_name}")
                    print(f"   │   Links: {link_set_data['total_links']}")
                    
                    for link in link_set_data["links"]:
                        print(f"   │       └── 📍 M3UA LINK: {link['link_name']} → {link['remote_ip']}:{link['remote_port']}")
                
                for route in element_data["routes"]:
                    print(f"   └── 🛣️ M3UA ROUTE: {route['route_name']} → {route['link_set_name']}")
            
            elif element_type == "SCCP_LAYER":
                print(f"\n📋 SCCP LAYER:")
                print(f"   Subsystems: {element_data['total_subsystems']}, Global Titles: {element_data['total_global_titles']}")
                
                print("   ├── 🏢 Subsystems:")
                for ssn in element_data["subsystems"][:5]:  # Show first 5
                    print(f"   │   └── {ssn['subsystem_name']} (SSN: {ssn['subsystem_number']}) → {ssn['destination_name']}")
                
                if len(element_data["subsystems"]) > 5:
                    print(f"   │   └── ... and {len(element_data['subsystems']) - 5} more")
                
                print("   └── 🌍 Global Title Chains:")
                for gt_chain in element_data["global_titles"][:5]:  # Show first 5
                    gt_info = gt_chain["gt_info"]
                    dest_chain = gt_chain["destination_chain"]
                    
                    print(f"       ├── 📞 GT: {gt_info['global_title_name']} ({gt_info['address_field']})")
                    print(f"       │   └── 🎯 Destination: {gt_info['destination_table']}")
                    
                    if dest_chain and dest_chain["destination_type"] != "UNRESOLVED":
                        print(f"       │       └── 📡 {dest_chain['destination_type']}: {dest_chain['destination_name']}")
                        print(f"       │           └── Links: {dest_chain['total_links']}")
                    else:
                        print(f"       │       └── ❌ Unresolved: {dest_chain['destination_name']}")
                
                if len(element_data["global_titles"]) > 5:
                    print(f"       └── ... and {len(element_data['global_titles']) - 5} more")
            
            print()  # Add spacing between elements
    
    def get_topology(self, element_name: str) -> Dict[str, Any]:
        """Get the complete topology for a specific network element."""
        hierarchical = self.config.get("hierarchical_structure", {})
        return hierarchical.get(element_name, {})

    def save_json(self, output_file: str = "sps_unified_links_config.json"):
        """Save configuration to JSON file."""
        try:
            # Convert sets to lists for JSON serialization
            config_copy = self.config.copy()
            if config_copy["metadata"].get("unique_networks"):
                config_copy["metadata"]["unique_networks"] = sorted(list(config_copy["metadata"]["unique_networks"]))
            if config_copy["metadata"].get("unique_point_codes"):
                config_copy["metadata"]["unique_point_codes"] = sorted(list(config_copy["metadata"]["unique_point_codes"]))
            if config_copy["metadata"].get("ip_port_pairs"):
                config_copy["metadata"]["ip_port_pairs"] = sorted(list(config_copy["metadata"]["ip_port_pairs"]))
            
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(config_copy, file, indent=2, ensure_ascii=False)
            print(f"Configuration saved to '{output_file}'")
        except Exception as e:
            print(f"Error saving JSON file: {e}")

    def to_json(self, indent: int = 2) -> str:
        """Convert configuration to JSON string."""
        # Convert sets to lists for JSON serialization
        config_copy = self.config.copy()
        if config_copy["metadata"].get("unique_networks"):
            config_copy["metadata"]["unique_networks"] = sorted(list(config_copy["metadata"]["unique_networks"]))
        if config_copy["metadata"].get("unique_point_codes"):
            config_copy["metadata"]["unique_point_codes"] = sorted(list(config_copy["metadata"]["unique_point_codes"]))
        if config_copy["metadata"].get("ip_port_pairs"):
            config_copy["metadata"]["ip_port_pairs"] = sorted(list(config_copy["metadata"]["ip_port_pairs"]))
        
        return json.dumps(config_copy, indent=indent, ensure_ascii=False)


def main():
    """Main function to demonstrate the unified parser."""
    import sys
    
    # Parse multiple files or single file
    if len(sys.argv) > 1:
        parser = SPSUnifiedLinksParser(sys.argv[1])
        print(f"Parsing single file: {sys.argv[1]}")
        config = parser.parse_file()
    else:
        parser = SPSUnifiedLinksParser()
        print("Parsing all SPS configuration files...")
        config = parser.parse_files()
    
    if config:
        # Print comprehensive summary
        parser.print_summary()
        
        # Print hierarchical summary
        parser.print_hierarchical_summary()
        
        # Save to JSON file
        parser.save_json("sps_unified_links_config.json")
        
        # Demonstrate specific topology queries
        print("\n=== Sample Network Element Topologies ===")
        
        # Look for common element names
        hierarchical = config.get("hierarchical_structure", {})
        sample_elements = list(hierarchical.keys())[:3]  # First 3 elements
        
        for element_name in sample_elements:
            element_data = parser.get_topology(element_name)
            if element_data:
                element_type = element_data.get("type", "UNKNOWN")
                total_links = element_data.get("total_links", 0)
                total_link_sets = element_data.get("total_link_sets", 0)
                print(f"{element_name} ({element_type}): {total_link_sets} link sets, {total_links} total links")
        
        print(f"\n✅ Configuration successfully parsed and saved to 'sps_unified_links_config.json'")
        print(f"Total network elements processed: {len(hierarchical)}")
        
        # Summary of link types
        link_types_summary = {
            "Diameter": len(config["diameter_links"]),
            "MTP": len(config["mtp_links"]),
            "M2UA": len(config["m2ua_links"]),
            "M3UA": len(config["m3ua_links"])
        }
        
        print("\n--- Link Types Summary ---")
        for link_type, count in link_types_summary.items():
            if count > 0:
                print(f"{link_type} Links: {count}")
        
    else:
        print("❌ Failed to parse configuration files.")


if __name__ == "__main__":
    main()
