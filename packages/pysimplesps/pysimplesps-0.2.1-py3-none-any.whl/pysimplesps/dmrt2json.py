import json
import re
from typing import Dict, Any


class SPSDiameterRoutingParser:
    """Parser for SPS Diameter Routing (DMRT) configuration."""
    
    def __init__(self, file_paths: list = None):
        if file_paths is None:
            file_paths = [
                "spsdmrt_host.txt",
                "spsdmrt_id.txt", 
                "spsdmrt_ip.txt",
                "spsdmrt_orealm.txt"
            ]
        self.file_paths = file_paths
        self.config = {
            "route_results": [],
            "route_entrances": [],
            "route_exits": [],
            "route_rules": {
                "dest_host": [],
                "origin_realm": [],
                "imsi": [],
                "ip_address": [],
                "origin_peer": [],
                "origin_host": [],
                "command_code": [],
                "nai": [],
                "msisdn": [],
                "impi": [],
                "impu": [],
                "apn": [],
                "ip_domain_id": [],
                "avp": []
            },
            "diameter_routes": [],
            "hierarchical_structure": {},
            "metadata": {
                "total_route_results": 0,
                "total_route_entrances": 0,
                "total_route_exits": 0,
                "total_route_rules": 0,
                "total_diameter_routes": 0,
                "all_realms": [],
                "all_hosts": [],
                "all_devices": [],
                "all_applications": [],
                "unique_realms": [],
                "unique_hosts": [],
                "unique_devices": [],
                "unique_applications": [],
                "routing_chains": []
            }
        }
    
    def parse_mml_line(self, line: str) -> Dict[str, Any]:
        """Parse a single MML command line into a dictionary."""
        line = line.strip()
        if line.startswith('/*') or not line or line.startswith('Set '):
            return {}
        
        # Route Result
        if line.startswith('ADD RTRESULT:'):
            params = self._parse_parameters(line)
            return {
                "command": "ADD_RTRESULT",
                "name": params.get("RTRSLTNAME", "").strip('"'),
                "route_type": params.get("RT", "").strip('"'),
                "protocol_type": params.get("PROTOCOLTYPE", "").strip('"'),
                "relay_selection_mode": params.get("RLSMOD", "").strip('"'),
                "relay_device_1": params.get("RLDEV1", "").strip('"'),
                "relay_device_2": params.get("RLDEV2", "").strip('"'),
                "relay_device_3": params.get("RLDEV3", "").strip('"'),
                "priority_device_1": int(params.get("PRIRLDEV1", 0)) if params.get("PRIRLDEV1") else None,
                "priority_device_2": int(params.get("PRIRLDEV2", 0)) if params.get("PRIRLDEV2") else None,
                "priority_device_3": int(params.get("PRIRLDEV3", 0)) if params.get("PRIRLDEV3") else None,
                "dynamic_balance": params.get("DYNBALANCE", "").strip('"'),
                "change_dr": params.get("CHGDR", "").strip('"'),
                "gyb_ps_flag": params.get("GYBPSFLAG", "").strip('"'),
                "full_mml": line
            }
        
        # Route Entrance
        elif line.startswith('ADD RTENT:'):
            params = self._parse_parameters(line)
            return {
                "command": "ADD_RTENT",
                "name": params.get("FLEXROUTEENTNAME", "").strip('"'),
                "next_rule": params.get("NEXTRULE", "").strip('"'),
                "next_index": int(params.get("NEXTINDEX", 0)) if params.get("NEXTINDEX") else 0,
                "full_mml": line
            }
        
        # Route Exit
        elif line.startswith('ADD RTEXIT:'):
            params = self._parse_parameters(line)
            return {
                "command": "ADD_RTEXIT",
                "reference_index": int(params.get("REFERINDEX", 0)) if params.get("REFERINDEX") else 0,
                "route_result": params.get("RTRESULT", "").strip('"'),
                "route_result_name": params.get("RTRSLTNAME", "").strip('"'),
                "full_mml": line
            }
        
        # Dest Host Route
        elif line.startswith('ADD RTDHOST:'):
            params = self._parse_parameters(line)
            return {
                "command": "ADD_RTDHOST",
                "reference_index": int(params.get("REFERINDEX", 0)) if params.get("REFERINDEX") else 0,
                "dest_host": params.get("DESTHOST", "").strip('"'),
                "next_rule": params.get("NEXTRULE", "").strip('"'),
                "next_index": int(params.get("NEXTINDEX", 0)) if params.get("NEXTINDEX") else 0,
                "full_mml": line
            }
        
        # Origin Realm Route
        elif line.startswith('ADD RTOREALM:'):
            params = self._parse_parameters(line)
            return {
                "command": "ADD_RTOREALM",
                "reference_index": int(params.get("REFERINDEX", 0)) if params.get("REFERINDEX") else 0,
                "origin_realm": params.get("ORIGINREALM", "").strip('"'),
                "next_rule": params.get("NEXTRULE", "").strip('"'),
                "next_index": int(params.get("NEXTINDEX", 0)) if params.get("NEXTINDEX") else 0,
                "full_mml": line
            }
        
        # IMSI Route
        elif line.startswith('ADD RTIMSI:'):
            params = self._parse_parameters(line)
            return {
                "command": "ADD_RTIMSI",
                "reference_index": int(params.get("REFERINDEX", 0)) if params.get("REFERINDEX") else 0,
                "imsi": params.get("IMSI", "").strip('"'),
                "next_rule": params.get("NEXTRULE", "").strip('"'),
                "next_index": int(params.get("NEXTINDEX", 0)) if params.get("NEXTINDEX") else 0,
                "full_mml": line
            }
        
        # IP Address Route
        elif line.startswith('ADD RTIP:'):
            params = self._parse_parameters(line)
            return {
                "command": "ADD_RTIP",
                "name": params.get("NAME", "").strip('"'),
                "reference_index": int(params.get("REFERINDEX", 0)) if params.get("REFERINDEX") else 0,
                "ip_type": params.get("IPTYPE", "").strip('"'),
                "ipv4": params.get("IPV4", "").strip('"'),
                "ipv6": params.get("IPV6", "").strip('"'),
                "mask_length_v4": int(params.get("MASKLENV4", 0)) if params.get("MASKLENV4") else None,
                "mask_length_v6": int(params.get("MASKLENV6", 0)) if params.get("MASKLENV6") else None,
                "next_rule": params.get("NEXTRULE", "").strip('"'),
                "next_index": int(params.get("NEXTINDEX", 0)) if params.get("NEXTINDEX") else 0,
                "full_mml": line
            }
        
        # Origin Peer Route
        elif line.startswith('ADD RTOPEER:'):
            params = self._parse_parameters(line)
            return {
                "command": "ADD_RTOPEER",
                "reference_index": int(params.get("REFERINDEX", 0)) if params.get("REFERINDEX") else 0,
                "origin_peer": params.get("ORIGINPEER", "").strip('"'),
                "next_rule": params.get("NEXTRULE", "").strip('"'),
                "next_index": int(params.get("NEXTINDEX", 0)) if params.get("NEXTINDEX") else 0,
                "full_mml": line
            }
        
        # Origin Host Route
        elif line.startswith('ADD RTOHOST:'):
            params = self._parse_parameters(line)
            return {
                "command": "ADD_RTOHOST",
                "reference_index": int(params.get("REFERINDEX", 0)) if params.get("REFERINDEX") else 0,
                "origin_host": params.get("ORIGINHOST", "").strip('"'),
                "next_rule": params.get("NEXTRULE", "").strip('"'),
                "next_index": int(params.get("NEXTINDEX", 0)) if params.get("NEXTINDEX") else 0,
                "full_mml": line
            }
        
        # Command Code Route
        elif line.startswith('ADD RTCC:'):
            params = self._parse_parameters(line)
            return {
                "command": "ADD_RTCC",
                "reference_index": int(params.get("REFERINDEX", 0)) if params.get("REFERINDEX") else 0,
                "command_code": int(params.get("COMMANDCODE", 0)) if params.get("COMMANDCODE") else 0,
                "next_rule": params.get("NEXTRULE", "").strip('"'),
                "next_index": int(params.get("NEXTINDEX", 0)) if params.get("NEXTINDEX") else 0,
                "full_mml": line
            }
        
        # NAI Route
        elif line.startswith('ADD RTNAI:'):
            params = self._parse_parameters(line)
            return {
                "command": "ADD_RTNAI",
                "reference_index": int(params.get("REFERINDEX", 0)) if params.get("REFERINDEX") else 0,
                "nai": params.get("NAI", "").strip('"'),
                "next_rule": params.get("NEXTRULE", "").strip('"'),
                "next_index": int(params.get("NEXTINDEX", 0)) if params.get("NEXTINDEX") else 0,
                "full_mml": line
            }
        
        # MSISDN Route
        elif line.startswith('ADD RTMSISDN:'):
            params = self._parse_parameters(line)
            return {
                "command": "ADD_RTMSISDN",
                "reference_index": int(params.get("REFERINDEX", 0)) if params.get("REFERINDEX") else 0,
                "msisdn": params.get("MSISDN", "").strip('"'),
                "next_rule": params.get("NEXTRULE", "").strip('"'),
                "next_index": int(params.get("NEXTINDEX", 0)) if params.get("NEXTINDEX") else 0,
                "full_mml": line
            }
        
        # Diameter Route
        elif line.startswith('ADD DMRT:'):
            params = self._parse_parameters(line)
            return {
                "command": "ADD_DMRT",
                "route_name": params.get("RTNAME", "").strip('"'),
                "realm_name": params.get("RN", "").strip('"'),
                "device_type": params.get("DEVTP", "").strip('"'),
                "local_action": params.get("LOCACT", "").strip('"'),
                "flex_route_entrance_name": params.get("FLEXROUTEENTNAME", "").strip('"'),
                "flex_route_failure_action": params.get("FLEXROUTEFAILACT", "").strip('"'),
                "error_code": params.get("ERRORCODE", "").strip('"'),
                "full_mml": line
            }
        
        # Software Parameter
        elif line.startswith('MOD SFP:'):
            params = self._parse_parameters(line)
            return {
                "command": "MOD_SFP",
                "sp_id": params.get("SPID", "").strip('"'),
                "mod_type": params.get("MODTYPE", "").strip('"'),
                "bit": int(params.get("BIT", 0)) if params.get("BIT") else 0,
                "bit_value": int(params.get("BITVAL", 0)) if params.get("BITVAL") else 0,
                "full_mml": line
            }
        
        return {}
    
    def _parse_parameters(self, line: str) -> Dict[str, str]:
        """Extract parameters from MML command line."""
        if ':' in line:
            params_part = line.split(':', 1)[1].strip()
            if params_part.endswith(';'):
                params_part = params_part[:-1]
            
            params = {}
            pattern = r'(\w+)=(".*?"|[^,\s]+)'
            matches = re.findall(pattern, params_part)
            
            for key, value in matches:
                params[key] = value
            
            return params
        
        return {}
    
    def parse_files(self) -> Dict[str, Any]:
        """Parse all routing configuration files."""
        for file_path in self.file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                
                for line in lines:
                    parsed = self.parse_mml_line(line)
                    self._categorize_parsed_data(parsed)
            
            except FileNotFoundError:
                print(f"Warning: File '{file_path}' not found, skipping...")
                continue
            except Exception as e:
                print(f"Error parsing file '{file_path}': {e}")
                continue
        
        # Build hierarchical structure and metadata
        self._build_hierarchical_structure()
        self._extract_metadata()
        
        return self.config
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a single routing configuration file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            for line in lines:
                parsed = self.parse_mml_line(line)
                self._categorize_parsed_data(parsed)
        
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return {}
        except Exception as e:
            print(f"Error parsing file '{file_path}': {e}")
            return {}
        
        # Build hierarchical structure and metadata
        self._build_hierarchical_structure()
        self._extract_metadata()
        
        return self.config
    
    def _categorize_parsed_data(self, parsed: Dict[str, Any]):
        """Categorize parsed data into appropriate sections."""
        if not parsed:
            return
        
        command = parsed.get("command")
        
        if command == "ADD_RTRESULT":
            self.config["route_results"].append({
                "name": parsed.get("name"),
                "route_type": parsed.get("route_type"),
                "protocol_type": parsed.get("protocol_type"),
                "relay_selection_mode": parsed.get("relay_selection_mode"),
                "relay_devices": [
                    {"device": parsed.get("relay_device_1"), "priority": parsed.get("priority_device_1")},
                    {"device": parsed.get("relay_device_2"), "priority": parsed.get("priority_device_2")},
                    {"device": parsed.get("relay_device_3"), "priority": parsed.get("priority_device_3")}
                ],
                "dynamic_balance": parsed.get("dynamic_balance"),
                "change_dr": parsed.get("change_dr"),
                "gyb_ps_flag": parsed.get("gyb_ps_flag"),
                "full_mml": parsed.get("full_mml")
            })
        
        elif command == "ADD_RTENT":
            self.config["route_entrances"].append({
                "name": parsed.get("name"),
                "next_rule": parsed.get("next_rule"),
                "next_index": parsed.get("next_index"),
                "full_mml": parsed.get("full_mml")
            })
        
        elif command == "ADD_RTEXIT":
            self.config["route_exits"].append({
                "reference_index": parsed.get("reference_index"),
                "route_result": parsed.get("route_result"),
                "route_result_name": parsed.get("route_result_name"),
                "full_mml": parsed.get("full_mml")
            })
        
        elif command == "ADD_RTDHOST":
            self.config["route_rules"]["dest_host"].append({
                "reference_index": parsed.get("reference_index"),
                "dest_host": parsed.get("dest_host"),
                "next_rule": parsed.get("next_rule"),
                "next_index": parsed.get("next_index"),
                "full_mml": parsed.get("full_mml")
            })
        
        elif command == "ADD_RTOREALM":
            self.config["route_rules"]["origin_realm"].append({
                "reference_index": parsed.get("reference_index"),
                "origin_realm": parsed.get("origin_realm"),
                "next_rule": parsed.get("next_rule"),
                "next_index": parsed.get("next_index"),
                "full_mml": parsed.get("full_mml")
            })
        
        elif command == "ADD_RTIMSI":
            self.config["route_rules"]["imsi"].append({
                "reference_index": parsed.get("reference_index"),
                "imsi": parsed.get("imsi"),
                "next_rule": parsed.get("next_rule"),
                "next_index": parsed.get("next_index"),
                "full_mml": parsed.get("full_mml")
            })
        
        elif command == "ADD_RTIP":
            self.config["route_rules"]["ip_address"].append({
                "name": parsed.get("name"),
                "reference_index": parsed.get("reference_index"),
                "ip_type": parsed.get("ip_type"),
                "ipv4": parsed.get("ipv4"),
                "ipv6": parsed.get("ipv6"),
                "mask_length_v4": parsed.get("mask_length_v4"),
                "mask_length_v6": parsed.get("mask_length_v6"),
                "next_rule": parsed.get("next_rule"),
                "next_index": parsed.get("next_index"),
                "full_mml": parsed.get("full_mml")
            })
        
        elif command == "ADD_RTOPEER":
            self.config["route_rules"]["origin_peer"].append({
                "reference_index": parsed.get("reference_index"),
                "origin_peer": parsed.get("origin_peer"),
                "next_rule": parsed.get("next_rule"),
                "next_index": parsed.get("next_index"),
                "full_mml": parsed.get("full_mml")
            })
        
        elif command == "ADD_RTOHOST":
            self.config["route_rules"]["origin_host"].append({
                "reference_index": parsed.get("reference_index"),
                "origin_host": parsed.get("origin_host"),
                "next_rule": parsed.get("next_rule"),
                "next_index": parsed.get("next_index"),
                "full_mml": parsed.get("full_mml")
            })
        
        elif command == "ADD_RTCC":
            self.config["route_rules"]["command_code"].append({
                "reference_index": parsed.get("reference_index"),
                "command_code": parsed.get("command_code"),
                "next_rule": parsed.get("next_rule"),
                "next_index": parsed.get("next_index"),
                "full_mml": parsed.get("full_mml")
            })
        
        elif command == "ADD_RTNAI":
            self.config["route_rules"]["nai"].append({
                "reference_index": parsed.get("reference_index"),
                "nai": parsed.get("nai"),
                "next_rule": parsed.get("next_rule"),
                "next_index": parsed.get("next_index"),
                "full_mml": parsed.get("full_mml")
            })
        
        elif command == "ADD_RTMSISDN":
            self.config["route_rules"]["msisdn"].append({
                "reference_index": parsed.get("reference_index"),
                "msisdn": parsed.get("msisdn"),
                "next_rule": parsed.get("next_rule"),
                "next_index": parsed.get("next_index"),
                "full_mml": parsed.get("full_mml")
            })
        
        elif command == "ADD_DMRT":
            self.config["diameter_routes"].append({
                "route_name": parsed.get("route_name"),
                "realm_name": parsed.get("realm_name"),
                "device_type": parsed.get("device_type"),
                "local_action": parsed.get("local_action"),
                "flex_route_entrance_name": parsed.get("flex_route_entrance_name"),
                "flex_route_failure_action": parsed.get("flex_route_failure_action"),
                "error_code": parsed.get("error_code"),
                "full_mml": parsed.get("full_mml")
            })
    
    def _build_hierarchical_structure(self):
        """Build a hierarchical structure showing routing chains."""
        hierarchical = {}
        
        # Start with diameter routes as the top level
        for dmrt in self.config["diameter_routes"]:
            route_name = dmrt["route_name"]
            hierarchical[route_name] = {
                "route_info": dmrt,
                "entrance": None,
                "routing_chain": [],
                "exit": None,
                "result": None
            }
            
            # Find the corresponding entrance
            entrance_name = dmrt["flex_route_entrance_name"]
            entrance = next((ent for ent in self.config["route_entrances"] if ent["name"] == entrance_name), None)
            if entrance:
                hierarchical[route_name]["entrance"] = entrance
                
                # Build the routing chain
                self._build_routing_chain(hierarchical[route_name], entrance)
        
        self.config["hierarchical_structure"] = hierarchical
    
    def _build_routing_chain(self, route_structure, entrance):
        """Build the complete routing chain from entrance to final route result."""
        current_rule = entrance["next_rule"]
        current_index = entrance["next_index"]
        chain = []
        
        # Build the routing rule chain until we reach RTEXIT
        while current_rule != "RTEXIT":
            rule_data = self._find_rule_by_index(current_rule, current_index)
            if rule_data:
                chain.append({
                    "rule_type": current_rule,
                    "rule_data": rule_data
                })
                current_rule = rule_data.get("next_rule", "RTEXIT")
                current_index = rule_data.get("next_index", 0)
            else:
                break
        
        # Now add the RTEXIT step to the chain
        
        # Find the exit - use the current_index from the last rule in the chain
        # If multiple exits have the same reference index, we need to match by the route name context
        exit_candidates = [exit for exit in self.config["route_exits"] if exit["reference_index"] == current_index]
        
        exit_data = None
        if len(exit_candidates) == 1:
            exit_data = exit_candidates[0]
        elif len(exit_candidates) > 1:
            # Multiple exits with same index - try to match by route context
            route_name = route_structure["route_info"]["route_name"]
            realm_name = route_structure["route_info"]["realm_name"]
            device_type = route_structure["route_info"]["device_type"]
            
            # Create better matching heuristics
            for candidate in exit_candidates:
                result_name = candidate["route_result_name"]
                
                # Check for exact substring matches
                if "SPS_B" in route_name and "SPS_B" in result_name:
                    exit_data = candidate
                    break
                elif "PCRF2" in route_name and "PCRF2" in result_name:
                    exit_data = candidate
                    break
                elif "PCRFb" in route_name and "PCRFb" in result_name:
                    exit_data = candidate
                    break
                elif "DEA" in route_name and "DEA" in result_name:
                    exit_data = candidate
                    break
                # Check realm-based matching for more context
                elif "33ims" in realm_name and "B_SPS_B" in result_name:
                    exit_data = candidate
                    break
                elif "Rx" == device_type and "B_SPS_B" in result_name:
                    exit_data = candidate
                    break
            
            # If no contextual match, take the first one (fallback)
            if not exit_data:
                exit_data = exit_candidates[0]
        
        # Add the RTEXIT step to the chain if we found an exit
        if exit_data:
            chain.append({
                "rule_type": "RTEXIT",
                "rule_data": exit_data
            })
            
            # Find the route result and add it to the chain
            result_name = exit_data["route_result_name"]
            result_data = next((result for result in self.config["route_results"] if result["name"] == result_name), None)
            if result_data:
                chain.append({
                    "rule_type": "RTRESULT",
                    "rule_data": result_data
                })
                
                # Also add the individual relay devices as the final execution targets
                relay_devices = []
                for device_info in result_data["relay_devices"]:
                    if device_info["device"]:  # Skip empty devices
                        relay_devices.append({
                            "rule_type": "RELAY_TARGET",
                            "rule_data": {
                                "device": device_info["device"],
                                "priority": device_info["priority"],
                                "selection_mode": result_data["relay_selection_mode"]
                            }
                        })
                
                if relay_devices:
                    chain.extend(relay_devices)
        
        route_structure["routing_chain"] = chain
        
        if exit_data:
            route_structure["exit"] = exit_data
            
            # Find the result using the exit's route_result_name
            result_name = exit_data["route_result_name"]
            result_data = next((result for result in self.config["route_results"] if result["name"] == result_name), None)
            if result_data:
                route_structure["result"] = result_data
    
    def _find_rule_by_index(self, rule_type, index):
        """Find a specific rule by type and reference index."""
        rule_mapping = {
            "RTDH": "dest_host",
            "RTOR": "origin_realm", 
            "RTIMSI": "imsi",
            "RTIP": "ip_address",
            "RTOPEER": "origin_peer",
            "RTOHOST": "origin_host",
            "RTCC": "command_code",
            "RTNAI": "nai",
            "RTMSISDN": "msisdn",
            # Add more rule mappings as needed for additional rule types
            "RTIMPI": "impi",
            "RTIMPU": "impu",
            "RTAPN": "apn",
            "RTIPDOMAINID": "ip_domain_id",
            "RTAVP": "avp"
        }
        
        rule_category = rule_mapping.get(rule_type)
        if rule_category:
            rules = self.config["route_rules"][rule_category]
            return next((rule for rule in rules if rule["reference_index"] == index), None)
        
        return None
    
    def _extract_metadata(self):
        """Extract and organize metadata."""
        metadata = self.config["metadata"]
        
        # Basic counts
        metadata["total_route_results"] = len(self.config["route_results"])
        metadata["total_route_entrances"] = len(self.config["route_entrances"])
        metadata["total_route_exits"] = len(self.config["route_exits"])
        metadata["total_diameter_routes"] = len(self.config["diameter_routes"])
        
        # Count all route rules
        total_rules = sum(len(rules) for rules in self.config["route_rules"].values())
        metadata["total_route_rules"] = total_rules
        
        # Extract unique values
        all_realms = []
        all_hosts = []
        all_devices = []
        all_applications = []
        
        # From diameter routes
        for dmrt in self.config["diameter_routes"]:
            if dmrt["realm_name"]:
                all_realms.append(dmrt["realm_name"])
            if dmrt["device_type"]:
                all_applications.append(dmrt["device_type"])
        
        # From route results
        for result in self.config["route_results"]:
            for device_info in result["relay_devices"]:
                if device_info["device"]:
                    all_devices.append(device_info["device"])
        
        # From dest host rules
        for rule in self.config["route_rules"]["dest_host"]:
            if rule["dest_host"]:
                all_hosts.append(rule["dest_host"])
        
        # From origin realm rules
        for rule in self.config["route_rules"]["origin_realm"]:
            if rule["origin_realm"]:
                all_realms.append(rule["origin_realm"])
        
        # Store all and unique values
        metadata["all_realms"] = all_realms
        metadata["all_hosts"] = all_hosts
        metadata["all_devices"] = all_devices
        metadata["all_applications"] = all_applications
        
        metadata["unique_realms"] = sorted(list(set(all_realms)))
        metadata["unique_hosts"] = sorted(list(set(all_hosts)))
        metadata["unique_devices"] = sorted(list(set(filter(None, all_devices))))
        metadata["unique_applications"] = sorted(list(set(all_applications)))
        
        # Build routing chains summary with actual topology chain (linked structure)
        routing_chains = []
        for route_name, route_data in self.config["hierarchical_structure"].items():
            # Build the actual routing topology as a linked chain
            routing_chain = {}
            current_step_id = None
            
            route_info = route_data["route_info"]
            entrance = route_data["entrance"]
            chain = route_data["routing_chain"]
            
            # Start with the entrance
            if entrance:
                entrance_id = f"{route_name}_ENTRANCE"
                routing_chain[entrance_id] = {
                    "step_id": entrance_id,
                    "component_type": "ENTRANCE",
                    "component_name": entrance["name"],
                    "description": f"Entry point for {route_info['device_type']} traffic",
                    "criteria": None,
                    "next_step": None,  # Will be filled later
                    "is_terminal": False
                }
                current_step_id = entrance_id
            
            # Process each step in the routing chain and link them
            step_counter = 1
            for step in chain:
                rule_type = step["rule_type"]
                rule_data = step["rule_data"]
                step_id = f"{route_name}_{rule_type}_{step_counter}"
                
                if rule_type in ["RTDH", "RTOR", "RTIMSI", "RTIP"]:
                    # Routing rule step
                    criteria = ""
                    description = ""
                    
                    if rule_type == "RTDH":
                        criteria = f"Destination Host: {rule_data.get('dest_host', 'N/A')}"
                        description = "Route based on destination host matching"
                    elif rule_type == "RTOR":
                        criteria = f"Origin Realm: {rule_data.get('origin_realm', 'N/A')}"
                        description = "Route based on origin realm matching"
                    elif rule_type == "RTIMSI":
                        criteria = f"IMSI Pattern: {rule_data.get('imsi', 'N/A')}"
                        description = "Route based on IMSI pattern matching"
                    elif rule_type == "RTIP":
                        ip_range = f"{rule_data.get('ipv4', 'N/A')}/{rule_data.get('mask_length_v4', 'N/A')}"
                        criteria = f"IP Range: {ip_range}"
                        description = "Route based on IP address matching"
                    
                    routing_chain[step_id] = {
                        "step_id": step_id,
                        "component_type": "ROUTING_RULE",
                        "component_name": rule_type,
                        "description": description,
                        "criteria": criteria,
                        "next_step": None,  # Will be filled later
                        "is_terminal": False
                    }
                    
                    # Link previous step to current step
                    if current_step_id:
                        routing_chain[current_step_id]["next_step"] = step_id
                    current_step_id = step_id
                    step_counter += 1
                
                elif rule_type == "RTEXIT":
                    # Exit step
                    routing_chain[step_id] = {
                        "step_id": step_id,
                        "component_type": "EXIT",
                        "component_name": f"RTEXIT (Index {rule_data.get('reference_index')})",
                        "description": "Exit to route result",
                        "criteria": f"Target: {rule_data.get('route_result_name')}",
                        "next_step": None,  # Will be filled later
                        "is_terminal": False
                    }
                    
                    # Link previous step to current step
                    if current_step_id:
                        routing_chain[current_step_id]["next_step"] = step_id
                    current_step_id = step_id
                    step_counter += 1
                
                elif rule_type == "RTRESULT":
                    # Route result step
                    routing_chain[step_id] = {
                        "step_id": step_id,
                        "component_type": "ROUTE_RESULT",
                        "component_name": rule_data.get("name"),
                        "description": f"Route result with {rule_data.get('relay_selection_mode', 'N/A')} selection",
                        "criteria": f"Protocol: {rule_data.get('protocol_type')}",
                        "selection_mode": rule_data.get("relay_selection_mode"),
                        "next_step": None,  # Will be filled later
                        "is_terminal": False
                    }
                    
                    # Link previous step to current step
                    if current_step_id:
                        routing_chain[current_step_id]["next_step"] = step_id
                    current_step_id = step_id
                    step_counter += 1
                
                elif rule_type == "RELAY_TARGET":
                    # Final relay target - these are parallel end points
                    device = rule_data.get("device")
                    priority = rule_data.get("priority")
                    selection_mode = rule_data.get("selection_mode")
                    
                    priority_text = f" (Priority: {priority})" if priority is not None else ""
                    target_step_id = f"{route_name}_TARGET_{device}"
                    
                    routing_chain[target_step_id] = {
                        "step_id": target_step_id,
                        "component_type": "RELAY_TARGET",
                        "component_name": device,
                        "description": f"Final relay device with {selection_mode} selection{priority_text}",
                        "criteria": f"Device: {device}, Priority: {priority}",
                        "device": device,
                        "priority": priority,
                        "selection_mode": selection_mode,
                        "next_step": None,  # Terminal step
                        "is_terminal": True
                    }
                    
                    # Link the route result to relay targets (parallel paths)
                    if current_step_id and current_step_id in routing_chain:
                        # Initialize next_step as list for multiple targets
                        if routing_chain[current_step_id]["next_step"] is None:
                            routing_chain[current_step_id]["next_step"] = []
                        elif isinstance(routing_chain[current_step_id]["next_step"], str):
                            # Convert single string to list
                            routing_chain[current_step_id]["next_step"] = [routing_chain[current_step_id]["next_step"]]
                        
                        # Add target to the list
                        if isinstance(routing_chain[current_step_id]["next_step"], list):
                            routing_chain[current_step_id]["next_step"].append(target_step_id)
                    
                    step_counter += 1
            
            # Create the chain summary with topology flow
            final_devices = [step["component_name"] for step in routing_chain.values() if step["component_type"] == "RELAY_TARGET"]
            
            # Build linear chain path (for simple display)
            chain_path = []
            current = None
            # Find the entrance step
            for step in routing_chain.values():
                if step["component_type"] == "ENTRANCE":
                    current = step
                    break
            
            while current:
                chain_path.append(current["component_name"])
                next_step_id = current.get("next_step")
                if next_step_id:
                    if isinstance(next_step_id, list):
                        # Multiple next steps (relay targets) - take first for linear path
                        next_step_id = next_step_id[0]
                    current = routing_chain.get(next_step_id)
                else:
                    break
            
            chain_summary = {
                "route_name": route_name,
                "realm": route_info["realm_name"],
                "application": route_info["device_type"],
                "local_action": route_info["local_action"],
                "topology_chain": routing_chain,
                "chain_path": " → ".join(chain_path),
                "final_targets": final_devices,
                "total_steps": len(routing_chain),
                "entry_point": f"{route_name}_ENTRANCE" if entrance else None
            }
            
            routing_chains.append(chain_summary)
        
        metadata["routing_chains"] = routing_chains
    
    def to_json(self, indent: int = 2) -> str:
        """Convert configuration to JSON string."""
        return json.dumps(self.config, indent=indent, ensure_ascii=False)
    
    def save_json(self, output_file: str = "spsdmrt_config.json"):
        """Save configuration to JSON file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(self.config, file, indent=2, ensure_ascii=False)
            print(f"Configuration saved to '{output_file}'")
        except Exception as e:
            print(f"Error saving JSON file: {e}")
    
    def print_summary(self):
        """Print a summary of the parsed configuration."""
        print("=== SPS Diameter Routing Configuration Summary ===")
        metadata = self.config["metadata"]
        
        print(f"Total Route Results: {metadata['total_route_results']}")
        print(f"Total Route Entrances: {metadata['total_route_entrances']}")
        print(f"Total Route Exits: {metadata['total_route_exits']}")
        print(f"Total Route Rules: {metadata['total_route_rules']}")
        print(f"Total Diameter Routes: {metadata['total_diameter_routes']}")
        
        # Network elements summary
        print("\n--- Network Elements Summary ---")
        print(f"Unique Realms: {len(metadata['unique_realms'])} - {metadata['unique_realms']}")
        print(f"Unique Hosts: {len(metadata['unique_hosts'])} - {metadata['unique_hosts']}")
        print(f"Unique Devices: {len(metadata['unique_devices'])} - {metadata['unique_devices']}")
        print(f"Unique Applications: {len(metadata['unique_applications'])} - {metadata['unique_applications']}")
        
        # Route rules breakdown
        print("\n--- Route Rules Breakdown ---")
        for rule_type, rules in self.config["route_rules"].items():
            if rules:
                print(f"  {rule_type.replace('_', ' ').title()}: {len(rules)}")
    
    def print_hierarchical_summary(self):
        """Print a hierarchical summary showing complete routing topology chains."""
        print("\n=== Complete Routing Topology Chains ===")
        
        for route_name, route_data in self.config["hierarchical_structure"].items():
            route_info = route_data["route_info"]
            print(f"\n🛣️  DIAMETER ROUTE: {route_name}")
            print(f"   Realm: {route_info['realm_name']}")
            print(f"   Application: {route_info['device_type']}")
            print(f"   Local Action: {route_info['local_action']}")
            
            if route_data["entrance"]:
                entrance = route_data["entrance"]
                print(f"   ├── 🚪 ENTRANCE: {entrance['name']}")
                print(f"   │   ➡️  Next Rule: {entrance['next_rule']} (Index: {entrance['next_index']})")
                
                # Show complete routing chain with improved flow visualization
                chain = route_data["routing_chain"]
                
                # Group chain elements by type for better display
                routing_rules = []
                exit_step = None
                result_step = None
                relay_targets = []
                
                for step in chain:
                    rule_type = step["rule_type"]
                    if rule_type in ["RTDH", "RTOR", "RTIMSI", "RTIP"]:
                        routing_rules.append(step)
                    elif rule_type == "RTEXIT":
                        exit_step = step
                    elif rule_type == "RTRESULT":
                        result_step = step
                    elif rule_type == "RELAY_TARGET":
                        relay_targets.append(step)
                
                # Display routing rules
                for i, step in enumerate(routing_rules):
                    rule_data = step["rule_data"]
                    rule_type = step["rule_type"]
                    
                    print(f"   │   ├── 🔍 ROUTING RULE: {rule_type}")
                    
                    # Show rule-specific details
                    if rule_type == "RTDH":
                        print(f"   │   │   📍 Destination Host: {rule_data.get('dest_host', 'N/A')}")
                    elif rule_type == "RTOR":
                        print(f"   │   │   🌐 Origin Realm: {rule_data.get('origin_realm', 'N/A')}")
                    elif rule_type == "RTIMSI":
                        print(f"   │   │   📱 IMSI Pattern: {rule_data.get('imsi', 'N/A')}")
                    elif rule_type == "RTIP":
                        ip_info = f"{rule_data.get('ipv4', 'N/A')}/{rule_data.get('mask_length_v4', 'N/A')}"
                        print(f"   │   │   🔢 IP Range: {ip_info}")
                    
                    next_rule = rule_data.get('next_rule', 'N/A')
                    next_index = rule_data.get('next_index', 'N/A')
                    print(f"   │   │   ➡️  Next: {next_rule} (Index: {next_index})")
                
                # Display exit
                if exit_step:
                    exit_data = exit_step["rule_data"]
                    print(f"   │   ├── 🚪 EXIT: Reference Index {exit_data['reference_index']}")
                    print(f"   │   │   ➡️  Route to: {exit_data['route_result_name']}")
                
                # Display route result
                if result_step:
                    result_data = result_step["rule_data"]
                    print(f"   │   ├── 🎯 ROUTE RESULT: {result_data['name']}")
                    print(f"   │   │   ⚙️  Selection Mode: {result_data['relay_selection_mode']}")
                    print(f"   │   │   📡 Protocol: {result_data['protocol_type']}")
                
                # Display relay targets (final execution destinations)
                if relay_targets:
                    print("   │   └── 🚀 FINAL RELAY TARGETS:")
                    for i, target in enumerate(relay_targets):
                        target_data = target["rule_data"]
                        device = target_data['device']
                        priority = target_data.get('priority')
                        is_last_target = (i == len(relay_targets) - 1)
                        
                        priority_info = f" (Priority: {priority})" if priority is not None else ""
                        prefix = "       └──" if is_last_target else "       ├──"
                        print(f"   │   {prefix} 📡 {device}{priority_info}")
                else:
                    # Fallback to show devices from result if no relay targets
                    if route_data["result"]:
                        result = route_data["result"]
                        devices = [dev["device"] for dev in result["relay_devices"] if dev["device"]]
                        if devices:
                            print(f"   │   └── 🚀 FINAL TARGETS: {', '.join(devices)}")
                
                # Show legacy summary for reference
                if route_data["exit"] and route_data["result"]:
                    exit_data = route_data["exit"]
                    result = route_data["result"]
                    devices = [dev["device"] for dev in result["relay_devices"] if dev["device"]]
                    print(f"   └── 📋 FLOW SUMMARY: {entrance['name']} → ... → {exit_data['route_result_name']} → {', '.join(devices)}")


def main():
    """Main function to demonstrate the parser."""
    import sys
    
    parser = SPSDiameterRoutingParser()
    
    print("Parsing SPS Diameter Routing configuration...")
    
    # Use command line argument if provided, otherwise use default file patterns
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        config = parser.parse_file(config_file)
    else:
        config = parser.parse_files()
    
    if config:
        # Print flat summary
        parser.print_summary()
        
        # Print hierarchical summary
        parser.print_hierarchical_summary()
        
        # Save to JSON file
        parser.save_json("spsdmrt_config.json")
        
        print("\n✅ Configuration successfully parsed and saved to 'spsdmrt_config.json'")
    else:
        print("❌ Failed to parse configuration files.")


if __name__ == "__main__":
    main()
