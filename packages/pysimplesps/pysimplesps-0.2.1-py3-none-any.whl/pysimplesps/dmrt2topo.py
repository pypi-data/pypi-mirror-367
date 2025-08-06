#!/usr/bin/env python3
"""
Diameter Routing Topology Generator - Interactive D3.js Zig-Zag Visualization
Generates a zig-zag flow-chart style network routing topology with interactive D3.js visualization.
The zig-zag layout provides clearer information display by alternating node positions vertically.
Input: Diameter routing MML text files (spsdmrt*.txt)
Output: Single HTML file with embedded D3.js interactive zig-zag routing flow visualization
"""

import json
import sys
import re
import math
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple


class DiameterRoutingTopoGenerator:
    """Generate interactive Diameter routing flow topology with D3.js zig-zag visualization"""
    
    def __init__(self):
        self.node_counter = 0
        self.nodes = []
        self.links = []
        
        # Visual properties for different routing node types
        self.node_config = {
            'SPS_CORE': {'color': '#FF4444', 'size': 40, 'shape': 'star'},
            'ROUTE_ENTRANCE': {'color': '#4ECDC4', 'size': 30, 'shape': 'circle'},
            'ROUTE_RULE': {'color': '#FECA57', 'size': 25, 'shape': 'rect'},
            'ROUTE_EXIT': {'color': '#FF9FF3', 'size': 30, 'shape': 'diamond'},
            'ROUTE_RESULT': {'color': '#5F27CD', 'size': 35, 'shape': 'hexagon'},
            'ROUTE_DEVICE': {'color': '#2ECC71', 'size': 28, 'shape': 'octagon'},
            'DIAMETER_REALM': {'color': '#45B7D1', 'size': 20, 'shape': 'circle'},
            'ROUTING_CHAIN': {'color': '#96CEB4', 'size': 15, 'shape': 'triangle'}
        }
        
        # Routing rule type mappings
        self.rule_types = {
            'RTDH': 'Dest-Host Route',
            'RTOPEER': 'Origin-Peer Route', 
            'RTOHOST': 'Origin-Host Route',
            'RTOREALM': 'Origin-Realm Route',
            'RTCC': 'Command Code Route',
            'RTCMDCODE': 'Command Code Route',
            'RTIMSI': 'IMSI Route',
            'RTNAI': 'NAI Route',
            'RTMSISDN': 'MSISDN Route',
            'RTIMPI': 'IMPI Route',
            'RTIMPU': 'IMPU Route',
            'RTAPN': 'APN Route',
            'RTIPDMNID': 'IP-Domain-ID Route',
            'RTAVP': 'AVP Route',
            'RTIP': 'IP Route',
            'RTEXIT': 'Route Exit'
        }
        
        # MML parsing patterns
        self.patterns = {
            'dmrt': r'ADD\s+DMRT:\s*(.+)',
            'rtent': r'ADD\s+RTENT:\s*(.+)',
            'rtexit': r'ADD\s+RTEXIT:\s*(.+)',
            'rtresult': r'ADD\s+RTRESULT:\s*(.+)',
            'rtdhost': r'ADD\s+RTDHOST:\s*(.+)',
            'rtopeer': r'ADD\s+RTOPEER:\s*(.+)',
            'rtohost': r'ADD\s+RTOHOST:\s*(.+)',
            'rtorealm': r'ADD\s+RTOREALM:\s*(.+)',
            'rtcmdcode': r'ADD\s+RTCMDCODE:\s*(.+)',
            'rtimsi': r'ADD\s+RTIMSI:\s*(.+)',
            'rtnai': r'ADD\s+RTNAI:\s*(.+)',
            'rtmsisdn': r'ADD\s+RTMSISDN:\s*(.+)',
            'rtimpi': r'ADD\s+RTIMPI:\s*(.+)',
            'rtimpu': r'ADD\s+RTIMPU:\s*(.+)',
            'rtapn': r'ADD\s+RTAPN:\s*(.+)',
            'rtipdmnid': r'ADD\s+RTIPDMNID:\s*(.+)',
            'rtavp': r'ADD\s+RTAVP:\s*(.+)',
            'rtip': r'ADD\s+RTIP:\s*(.+)',
            'parameter_pair': r'(\w+)\s*=\s*([^,;]+)'
        }
        
        # Data structures for routing logic
        self.realms = {}
        self.entrances = {}
        self.exits = {}
        self.results = {}
        self.routing_rules = {}
        self.routing_chains = []
    
    def generate_node_id(self) -> str:
        """Generate unique node ID"""
        self.node_counter += 1
        return f"route_node_{self.node_counter:04d}"
    
    def parse_parameters(self, param_string: str) -> Dict[str, str]:
        """Parse parameter string into key-value pairs"""
        params = {}
        # Remove comments and clean up
        clean_string = re.sub(r'/\*.*?\*/', '', param_string)
        
        # Find all parameter pairs
        matches = re.findall(self.patterns['parameter_pair'], clean_string)
        for key, value in matches:
            # Clean up quotes and whitespace
            clean_value = value.strip().strip('"').strip("'")
            params[key.upper()] = clean_value
        
        return params
    
    def add_central_node(self):
        """Add the central SPS routing core node if it doesn't already exist"""
        # Check if central node already exists
        for node in self.nodes:
            if node['id'] == 'SPS_ROUTING_CORE':
                return node
        
        config = self.node_config['SPS_CORE']
        node = {
            'id': 'SPS_ROUTING_CORE',
            'name': 'SPS Routing Engine',
            'type': 'SPS_CORE',
            'layer': 0,
            'x': 400,  # Center of viewport
            'y': 150,  # Top center
            'fx': 400,  # Fixed position
            'fy': 150,
            'color': config['color'],
            'size': config['size'],
            'shape': config['shape'],
            'description': 'Diameter Routing Core',
            'details': {
                'Component': 'SPS Routing Engine',
                'Function': 'Process Diameter Messages',
                'Total Routes': 0,
                'Total Chains': 0
            }
        }
        self.nodes.append(node)
        return node
    
    def add_node(self, node_id: str, name: str, node_type: str, layer: int, 
                 x: float = None, y: float = None, **properties) -> Dict[str, Any]:
        """Add a routing node to the topology"""
        config = self.node_config.get(node_type, self.node_config['ROUTE_RULE'])
        
        # Build details for hover information
        details = {'Node Type': node_type, 'Layer': layer}
        for key, value in properties.items():
            if value and value != '':
                details[key.replace('_', ' ').title()] = str(value)
        
        node = {
            'id': node_id,
            'name': name,
            'type': node_type,
            'layer': layer,
            'x': x or (200 + layer * 150),
            'y': y or (300 + len([n for n in self.nodes if n.get('layer') == layer]) * 60),
            'color': config['color'],
            'size': config['size'],
            'shape': config['shape'],
            'details': details,
            **properties
        }
        
        self.nodes.append(node)
        return node
    
    def add_link(self, source_id: str, target_id: str, link_type: str, 
                 label: str = '', **properties):
        """Add a routing link between nodes"""
        link = {
            'source': source_id,
            'target': target_id,
            'type': link_type,
            'label': label,
            **properties
        }
        self.links.append(link)
        return link
    
    def calculate_flow_positions(self, chain_nodes: List[Dict], chain_index: int) -> List[Tuple[float, float]]:
        """Calculate dynamic zig-zag positions for routing chain flow with adaptive spacing"""
        # Dynamic spacing based on total number of chains and complexity
        total_chains = len(self.routing_chains)
        total_nodes = len(chain_nodes)
        
        # Base parameters with increased spacing
        start_x = 150
        min_chain_spacing = 500  # Increased from 200
        max_chain_spacing = 800  # Increased from 400
        
        # Calculate dynamic chain spacing based on content density
        if total_chains <= 3:
            chain_spacing = max_chain_spacing  # More space for fewer chains
        elif total_chains <= 6:
            chain_spacing = min_chain_spacing + (max_chain_spacing - min_chain_spacing) // 2
        else:
            chain_spacing = min_chain_spacing  # Compact spacing for many chains
        
        # Dynamic horizontal spacing based on chain length - increased margins
        if total_nodes <= 3:
            horizontal_spacing = 500  # Increased from 280
        elif total_nodes <= 6:
            horizontal_spacing = 500  # Increased from 240
        else:
            horizontal_spacing = 500  # Increased from 200
        
        # Dynamic zigzag offset based on chain complexity (minimal wave)
        zigzag_offset = min(30, 15 + (total_nodes * 1))  # Very small wave for almost flat layout
        
        # Calculate base Y position with dynamic spacing
        base_y = 250 + (chain_index * chain_spacing)
        
        positions = []
        for i, node in enumerate(chain_nodes):
            x = start_x + (i * horizontal_spacing)
            
            # Minimal wave pattern with tiny offset
            is_even = i % 2 == 0
            y_offset = 0 if is_even else zigzag_offset
            
            # Add minimal progressive offset for very long chains
            if total_nodes > 8:
                progressive_offset = (i // 8) * 15  # Every 8 nodes, add tiny offset
                y_offset += progressive_offset
            
            y = base_y + y_offset
            positions.append((x, y))
        
        return positions
    
    def parse_routing_file(self, filename: str) -> bool:
        """Parse routing MML file and build topology"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
            
            lines = content.split('\n')
            
            # First pass: Parse all routing components
            for line in lines:
                line = line.strip()
                if not line or line.startswith('/*') or line.startswith('NOTE'):
                    continue
                
                # Parse different routing commands
                if 'ADD DMRT' in line.upper():
                    self._parse_diameter_realm(line)
                elif 'ADD RTENT' in line.upper():
                    self._parse_route_entrance(line)
                elif 'ADD RTEXIT' in line.upper():
                    self._parse_route_exit(line)
                elif 'ADD RTRESULT' in line.upper():
                    self._parse_route_result(line)
                else:
                    # Parse various routing rule types
                    for rule_type in ['RTDHOST', 'RTOPEER', 'RTOHOST', 'RTOREALM', 
                                    'RTCMDCODE', 'RTIMSI', 'RTNAI', 'RTMSISDN', 
                                    'RTIMPI', 'RTIMPU', 'RTAPN', 'RTIPDMNID', 
                                    'RTAVP', 'RTIP']:
                        if f'ADD {rule_type}' in line.upper():
                            self._parse_routing_rule(line, rule_type)
                            break
            
            # Always add the central node before building topology
            self.add_central_node()
            
            # Second pass: Build routing chains and topology
            self._build_routing_chains()
            self._build_topology_visualization()
            
            return True
            
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return False
        except Exception as e:
            import traceback
            print(f"Error parsing routing file: {e}\n{traceback.format_exc()}")
            return False
    
    def _parse_diameter_realm(self, line: str):
        """Parse ADD DMRT command"""
        params = self.parse_parameters(line)
        realm_name = params.get('RTNAME', '')
        if realm_name:
            self.realms[realm_name] = {
                'realm_route_name': realm_name,
                'realm': params.get('RN', ''),
                'device_type': params.get('DEVTP', ''),
                'local_action': params.get('LOCACT', ''),
                'entrance_name': params.get('FLEXROUTEENTNAME', ''),
                'failure_action': params.get('FLEXROUTEFAILACT', ''),
                'error_code': params.get('ERRORCODE', ''),
                'mml_command': line.strip(),  # Store original MML command
                'command_type': 'DMRT',  # Add command type for filtering
                'display_label': f"Realm: {params.get('RN', realm_name)} ({params.get('DEVTP', 'Unknown')})"
            }
    
    def _parse_route_entrance(self, line: str):
        """Parse ADD RTENT command"""
        params = self.parse_parameters(line)
        entrance_name = params.get('FLEXROUTEENTNAME', '')
        if entrance_name:
            # Map abbreviations to full rule types
            rule_abbrev_map = {
                'RTDH': 'RTDHOST',
                'RTOPEER': 'RTOPEER', 
                'RTOHOST': 'RTOHOST',
                'RTCC': 'RTCMDCODE',
                'RTCMDCODE': 'RTCMDCODE',
                'RTIMSI': 'RTIMSI',
                'RTNAI': 'RTNAI',
                'RTMSISDN': 'RTMSISDN',
                'RTOR': 'RTOREALM',
                'RTOREALM': 'RTOREALM',
                'RTIP': 'RTIP',
                'RTEXIT': 'RTEXIT'
            }
            
            next_rule = params.get('NEXTRULE', '')
            if next_rule in rule_abbrev_map:
                next_rule = rule_abbrev_map[next_rule]
            
            self.entrances[entrance_name] = {
                'name': entrance_name,
                'next_rule': next_rule,
                'next_index': params.get('NEXTINDEX', ''),
                'mml_command': line.strip(),  # Store original MML command
                'command_type': 'RTENT',  # Add command type for filtering
                'display_label': f"Entry: {entrance_name}"
            }
    
    def _parse_route_exit(self, line: str):
        """Parse ADD RTEXIT command"""
        params = self.parse_parameters(line)
        refer_index = params.get('REFERINDEX', '')
        if refer_index:
            # Convert index to integer for consistent lookup
            try:
                index_key = int(refer_index)
            except (ValueError, TypeError):
                index_key = refer_index
                
            self.exits[index_key] = {
                'index': index_key,
                'route_type': params.get('RTRESULT', ''),
                'result_name': params.get('RTRSLTNAME', ''),
                'mml_command': line.strip(),  # Store original MML command
                'command_type': 'RTEXIT',  # Add command type for filtering
                'display_label': f"Exit: {params.get('RTRSLTNAME', refer_index)}"
            }
    
    def _parse_route_result(self, line: str):
        """Parse ADD RTRESULT command"""
        params = self.parse_parameters(line)
        result_name = params.get('RTRSLTNAME', '')
        if result_name:
            device1 = params.get('RLDEV1', '')
            self.results[result_name] = {
                'name': result_name,
                'route_type': params.get('RT', ''),
                'protocol': params.get('PROTOCOLTYPE', ''),
                'selection_mode': params.get('RLSMOD', ''),
                'device1': device1,
                'device2': params.get('RLDEV2', ''),
                'device3': params.get('RLDEV3', ''),
                'priority1': params.get('PRIRLDEV1', ''),
                'priority2': params.get('PRIRLDEV2', ''),
                'priority3': params.get('PRIRLDEV3', ''),
                'mml_command': line.strip(),  # Store original MML command
                'display_label': f"Route: {device1}" if device1 else f"Result: {result_name}"
            }
    
    def _parse_routing_rule(self, line: str, rule_type: str):
        """Parse routing rule commands"""
        params = self.parse_parameters(line)
        refer_index = params.get('REFERINDEX', '')
        if refer_index:
            # Convert index to integer for consistent lookup
            try:
                index_key = int(refer_index)
            except (ValueError, TypeError):
                index_key = refer_index
            
            # Map abbreviations in next rule
            rule_abbrev_map = {
                'RTDH': 'RTDHOST',
                'RTOPEER': 'RTOPEER', 
                'RTOHOST': 'RTOHOST',
                'RTCC': 'RTCMDCODE',
                'RTCMDCODE': 'RTCMDCODE',
                'RTIMSI': 'RTIMSI',
                'RTNAI': 'RTNAI',
                'RTMSISDN': 'RTMSISDN',
                'RTOR': 'RTOREALM',
                'RTOREALM': 'RTOREALM',
                'RTIP': 'RTIP',
                'RTEXIT': 'RTEXIT'
            }
            
            next_rule = params.get('NEXTRULE', '')
            if next_rule in rule_abbrev_map:
                next_rule = rule_abbrev_map[next_rule]
            
            rule_data = {
                'type': rule_type,
                'index': index_key,
                'next_rule': next_rule,
                'next_index': params.get('NEXTINDEX', ''),
                'rule_name': self.rule_types.get(rule_type, rule_type),
                'mml_command': line.strip()  # Store original MML command
            }
            
            # Add rule-specific parameters with better labeling
            if rule_type == 'RTDHOST':
                rule_data['dest_host'] = params.get('DESTHOST', '')
                rule_data['display_value'] = params.get('DESTHOST', '')
                rule_data['display_label'] = f"Host: {params.get('DESTHOST', 'N/A')}"
            elif rule_type == 'RTOPEER':
                rule_data['origin_peer'] = params.get('ORIGINPEER', '')
                rule_data['display_value'] = params.get('ORIGINPEER', '')
                rule_data['display_label'] = f"Peer: {params.get('ORIGINPEER', 'N/A')}"
            elif rule_type == 'RTOHOST':
                rule_data['origin_host'] = params.get('ORIGINHOST', '')
                rule_data['display_value'] = params.get('ORIGINHOST', '')
                rule_data['display_label'] = f"Host: {params.get('ORIGINHOST', 'N/A')}"
            elif rule_type == 'RTOREALM':
                rule_data['origin_realm'] = params.get('ORIGINREALM', '')
                rule_data['display_value'] = params.get('ORIGINREALM', '')
                rule_data['display_label'] = f"Realm: {params.get('ORIGINREALM', 'N/A')}"
            elif rule_type == 'RTCMDCODE':
                rule_data['command_code'] = params.get('COMMANDCODE', '')
                rule_data['display_value'] = params.get('COMMANDCODE', '')
                rule_data['display_label'] = f"CC: {params.get('COMMANDCODE', 'N/A')}"
            elif rule_type == 'RTIMSI':
                rule_data['imsi'] = params.get('IMSI', '')
                rule_data['display_value'] = params.get('IMSI', '')
                rule_data['display_label'] = f"IMSI: {params.get('IMSI', 'N/A')}"
            elif rule_type == 'RTNAI':
                rule_data['nai'] = params.get('NAI', '')
                rule_data['display_value'] = params.get('NAI', '')
                rule_data['display_label'] = f"NAI: {params.get('NAI', 'N/A')}"
            elif rule_type == 'RTMSISDN':
                rule_data['msisdn'] = params.get('MSISDN', '')
                rule_data['display_value'] = params.get('MSISDN', '')
                rule_data['display_label'] = f"MSISDN: {params.get('MSISDN', 'N/A')}"
            elif rule_type == 'RTIP':
                rule_data['ip_address'] = params.get('IPADDRESS', '')
                rule_data['display_value'] = params.get('IPADDRESS', '')
                rule_data['display_label'] = f"IP: {params.get('IPADDRESS', 'N/A')}"
            elif rule_type == 'RTAVP':
                avp_code = params.get('AVPCODE', '')
                avp_value = params.get('AVPVALUE', '')
                rule_data['avp_code'] = avp_code
                rule_data['avp_value'] = avp_value
                rule_data['display_value'] = f"{avp_code}={avp_value}"
                rule_data['display_label'] = f"AVP: {avp_code}={avp_value}"
            else:
                rule_data['display_value'] = rule_type
                rule_data['display_label'] = rule_data['rule_name']
            
            self.routing_rules[index_key] = rule_data
    
    def _build_routing_chains(self):
        """Build routing chains from parsed data"""
        for entrance_name, entrance_data in self.entrances.items():
            chain = self._trace_routing_chain(entrance_data)
            if chain:
                self.routing_chains.append({
                    'entrance': entrance_name,
                    'chain': chain,
                    'length': len(chain)
                })
    
    def _trace_routing_chain(self, entrance_data: Dict) -> List[Dict]:
        """Trace a complete routing chain from entrance to exit"""
        chain = []
        current_rule = entrance_data.get('next_rule', '')
        current_index = entrance_data.get('next_index', '')
        
        # Map abbreviations to full rule types
        rule_abbrev_map = {
            'RTDH': 'RTDHOST',
            'RTOPEER': 'RTOPEER', 
            'RTOHOST': 'RTOHOST',
            'RTCC': 'RTCMDCODE',
            'RTCMDCODE': 'RTCMDCODE',
            'RTIMSI': 'RTIMSI',
            'RTNAI': 'RTNAI',
            'RTMSISDN': 'RTMSISDN',
            'RTOR': 'RTOREALM',
            'RTOREALM': 'RTOREALM',
            'RTIP': 'RTIP',
            'RTEXIT': 'RTEXIT'
        }
        
        visited_indices = set()
        step_count = 1
        
        while current_index and current_index not in visited_indices:
            visited_indices.add(current_index)
            
            # Convert string index to int for lookup
            try:
                index_key = int(current_index) if isinstance(current_index, str) else current_index
            except (ValueError, TypeError):
                index_key = current_index
            
            if index_key in self.routing_rules:
                rule = self.routing_rules[index_key].copy()
                rule['step_number'] = step_count
                rule['chain_position'] = step_count
                
                # Enhance rule display with step information
                rule_type = rule.get('type', '')
                if 'display_label' not in rule or not rule['display_label']:
                    rule['display_label'] = f"Step {step_count}: {rule.get('rule_name', rule_type)}"
                
                chain.append(rule)
                current_rule = rule.get('next_rule', '')
                current_index = rule.get('next_index', '')
                step_count += 1
                
                # Handle rule type abbreviations
                if current_rule in rule_abbrev_map:
                    current_rule = rule_abbrev_map[current_rule]
                
            elif index_key in self.exits:
                exit_rule = self.exits[index_key].copy()
                exit_rule.update({
                    'type': 'RTEXIT',
                    'index': index_key,
                    'rule_name': 'Route Exit',
                    'step_number': step_count,
                    'chain_position': step_count,
                    'display_label': f"Step {step_count}: Route Exit → {exit_rule.get('result_name', 'N/A')}"
                })
                chain.append(exit_rule)
                break
            else:
                # Debug: print missing index for troubleshooting
                print(f"Warning: Could not find routing step at index {current_index}")
                print(f"Available rule indices: {list(self.routing_rules.keys())}")
                print(f"Available exit indices: {list(self.exits.keys())}")
                break
        
        return chain
    
    def _build_topology_visualization(self):
        """Build the visual topology from routing data"""
        chain_count = 0
        
        # Create realm nodes
        for realm_name, realm_data in self.realms.items():
            realm_id = self.generate_node_id()
            self.add_node(
                realm_id, realm_data.get('display_label', realm_name), 'DIAMETER_REALM', 1,
                x=100, y=200 + len(self.realms) * 40,
                realm=realm_data['realm'],
                device_type=realm_data['device_type'],
                local_action=realm_data['local_action'],
                entrance_ref=realm_data['entrance_name'],
                mml_command=realm_data.get('mml_command', ''),
                command_type=realm_data.get('command_type', 'DMRT'),
                display_label=realm_data.get('display_label', realm_name)
            )
            
            # Link realm to core
            self.add_link('SPS_ROUTING_CORE', realm_id, 'REALM_CONNECTION',
                         f"Realm: {realm_data['realm']}")
        
        # Create routing chains visualization
        for chain_data in self.routing_chains:
            chain = chain_data['chain']
            entrance_name = chain_data['entrance']
            
            if not chain:
                continue
            
            # Calculate positions for this chain
            positions = self.calculate_flow_positions(chain, chain_count)
            
            # Create entrance node
            entrance_id = self.generate_node_id()
            entrance_x, entrance_y = positions[0] if positions else (150, 300)
            
            entrance_data = self.entrances.get(entrance_name, {})
            entrance_display = entrance_data.get('display_label', entrance_name)
            
            self.add_node(
                entrance_id, entrance_display, 'ROUTE_ENTRANCE', 2,
                x=entrance_x, y=entrance_y,
                entrance_name=entrance_name,
                mml_command=entrance_data.get('mml_command', ''),
                command_type=entrance_data.get('command_type', 'RTENT'),
                display_label=entrance_display
            )
            
            # Link from realm to entrance (find associated realm)
            realm_node = None
            for realm_name, realm_data in self.realms.items():
                if realm_data.get('entrance_name') == entrance_name:
                    realm_node = next((n for n in self.nodes 
                                     if n['name'] == realm_data.get('display_label', realm_name)), None)
                    break
            
            if realm_node:
                self.add_link(realm_node['id'], entrance_id, 'ENTRANCE_CONNECTION',
                             'Route Entrance')
            
            # Create chain nodes
            prev_node_id = entrance_id
            
            for i, rule in enumerate(chain):
                if i + 1 < len(positions):
                    rule_x, rule_y = positions[i + 1]
                else:
                    rule_x, rule_y = entrance_x + ((i + 1) * 180), entrance_y
                
                rule_id = self.generate_node_id()
                rule_display = rule.get('display_label', rule.get('rule_name', rule.get('type', 'Unknown')))
                
                if rule.get('type') == 'RTEXIT':
                    # This is an exit node
                    exit_data = self.exits.get(rule.get('index', ''), {})
                    exit_display = exit_data.get('display_label', 'Route Exit')
                    
                    self.add_node(
                        rule_id, exit_display, 'ROUTE_EXIT', 3 + i,
                        x=rule_x, y=rule_y,
                        result_name=rule.get('result_name', ''),
                        exit_index=rule.get('index', ''),
                        mml_command=exit_data.get('mml_command', ''),
                        command_type=exit_data.get('command_type', 'RTEXIT'),
                        display_label=exit_display
                    )
                    
                    # Create result node if exists
                    result_name = rule.get('result_name', '')
                    if result_name and result_name in self.results:
                        result_data = self.results[result_name]
                        result_id = self.generate_node_id()
                        result_display = result_data.get('display_label', result_name)
                        
                        self.add_node(
                            result_id, result_display, 'ROUTE_RESULT', 4 + i,
                            x=rule_x + 150, y=rule_y,
                            selection_mode=result_data.get('selection_mode', ''),
                            device1=result_data.get('device1', ''),
                            device2=result_data.get('device2', ''),
                            device3=result_data.get('device3', ''),
                            protocol=result_data.get('protocol', ''),
                            mml_command=result_data.get('mml_command', ''),
                            display_label=result_display
                        )
                        
                        self.add_link(rule_id, result_id, 'RESULT_CONNECTION',
                                     f"To: {result_data.get('device1', 'Unknown')}")
                        
                        # Create device nodes following the result node
                        device_y_offset = 0
                        device_spacing = 80
                        devices = [
                            (result_data.get('device1', ''), result_data.get('priority1', '')),
                            (result_data.get('device2', ''), result_data.get('priority2', '')),
                            (result_data.get('device3', ''), result_data.get('priority3', ''))
                        ]
                        
                        for idx, (device_name, priority) in enumerate(devices):
                            if device_name:  # Only create node if device exists
                                device_id = self.generate_node_id()
                                priority_text = f" (P{priority})" if priority else ""
                                device_display = f"{device_name}{priority_text}"
                                
                                self.add_node(
                                    device_id, device_display, 'ROUTE_DEVICE', 5 + i + idx,
                                    x=rule_x + 300, y=rule_y + device_y_offset,
                                    device_name=device_name,
                                    priority=priority,
                                    parent_result=result_name,
                                    mml_command=f"Device: {device_name}, Priority: {priority}",
                                    display_label=device_display
                                )
                                
                                # Link result to device with priority information
                                link_label = f"Priority {priority}" if priority else f"Device {idx + 1}"
                                self.add_link(result_id, device_id, 'DEVICE_CONNECTION', link_label)
                                
                                device_y_offset += device_spacing
                else:
                    # This is a routing rule
                    self.add_node(
                        rule_id, rule_display, 'ROUTE_RULE', 3 + i,
                        x=rule_x, y=rule_y,
                        rule_type=rule.get('type', ''),
                        mml_command=rule.get('mml_command', ''),
                        command_type=rule.get('type', 'UNKNOWN'),  # Use the rule type as command type
                        display_label=rule_display,
                        display_value=rule.get('display_value', ''),
                        **{k: v for k, v in rule.items() 
                           if k not in ['type', 'rule_name', 'next_rule', 'next_index', 'mml_command', 'display_label', 'display_value']}
                    )
                
                # Link to previous node
                self.add_link(prev_node_id, rule_id, 'FLOW_CONNECTION',
                             f"Next: {rule_display}")
                
                prev_node_id = rule_id
            
            chain_count += 1
        
        # Update central node statistics
        central_node = next(n for n in self.nodes if n['id'] == 'SPS_ROUTING_CORE')
        central_node['details']['Total Routes'] = len(self.realms)
        central_node['details']['Total Chains'] = len(self.routing_chains)
        central_node['details']['Total Rules'] = len(self.routing_rules)
    
    def generate_d3_html(self, output_filename: str = 'diameter_routing_interactive.html'):
        """Generate interactive D3.js HTML visualization for routing flows"""
        
        # Calculate statistics
        stats = {
            'total_nodes': len(self.nodes),
            'total_links': len(self.links),
            'total_realms': len(self.realms),
            'total_chains': len(self.routing_chains),
            'total_rules': len(self.routing_rules),
            'total_devices': len([node for node in self.nodes if node['type'] == 'ROUTE_DEVICE']),
            'node_types': {},
            'rule_types': list(set(rule.get('type', 'Unknown') for rule in self.routing_rules.values()))
        }
        
        for node in self.nodes:
            node_type = node['type']
            stats['node_types'][node_type] = stats['node_types'].get(node_type, 0) + 1
        
        html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SPS Diameter Routing Flow - Interactive Multi-Select Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #2C3E50 0%, #3498DB 100%);
            color: white;
            overflow: hidden;
        }}
        
        .container {{
            display: flex;
            flex-direction: column;
            height: 100vh;
        }}
        
        .header {{
            padding: 8px 20px;
            background: rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        h1 {{
            margin: 0;
            font-size: 1.6em;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .controls {{
            display: flex;
            justify-content: center;
            gap: 8px;
            margin: 6px 0;
            flex-wrap: wrap;
        }}
        
        .control-group {{
            background: rgba(255, 255, 255, 0.1);
            padding: 4px 8px;
            border-radius: 12px;
            backdrop-filter: blur(5px);
            font-size: 0.85em;
        }}
        
        button {{
            background: linear-gradient(45deg, #E74C3C, #C0392B);
            border: none;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            cursor: pointer;
            margin: 0 2px;
            font-weight: bold;
            transition: all 0.3s ease;
            font-size: 0.8em;
        }}
        
        button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 3px 8px rgba(0,0,0,0.3);
        }}
        
        button.active {{
            background: linear-gradient(45deg, #27AE60, #2ECC71);
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 8px;
            margin: 4px 0;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.15);
            padding: 6px 10px;
            border-radius: 6px;
            text-align: center;
            backdrop-filter: blur(5px);
            font-size: 0.75em;
        }}
        
        .stat-number {{
            font-size: 1.3em;
            font-weight: bold;
            color: #3498DB;
        }}
        
        .main-content {{
            flex: 1;
            position: relative;
            overflow: hidden;
        }}
        
        #routing-flow {{
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.1);
            cursor: grab;
        }}
        
        #routing-flow:active {{
            cursor: grabbing;
        }}
        
        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 8px;
            border-radius: 6px;
            pointer-events: none;
            font-size: 10px;
            max-width: 250px;
            z-index: 1000;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        .tooltip h4 {{
            margin: 0 0 4px 0;
            color: #3498DB;
            font-size: 12px;
        }}
        
        .tooltip-content {{
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 2px 5px;
            font-size: 9px;
        }}
        
        .legend {{
            position: absolute;
            bottom: 10px;
            left: 60px;
            background: rgba(0, 0, 0, 0.8);
            padding: 8px;
            border-radius: 6px;
            backdrop-filter: blur(10px);
            max-width: 180px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
            margin: 2px 0;
            font-size: 10px;
        }}
        
        .legend-circle {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            border: 1px solid rgba(255, 255, 255, 0.5);
        }}
        
        .zoom-controls {{
            position: absolute;
            top: 10px;
            right: 10px;
            display: flex;
            flex-direction: column;
            gap: 3px;
        }}
        
        .zoom-btn {{
            width: 35px;
            height: 35px;
            border-radius: 50%;
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .zoom-btn:hover {{
            background: rgba(0, 0, 0, 0.9);
        }}
        
        .layout-controls {{
            position: absolute;
            top: 10px;
            left: 10px;
            display: flex;
            flex-direction: column;
            gap: 3px;
        }}
        
        .layout-btn {{
            width: 35px;
            height: 35px;
            border-radius: 50%;
            background: rgba(44, 62, 80, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }}
        
        .layout-btn:hover {{
            background: rgba(44, 62, 80, 1);
            transform: scale(1.05);
        }}
        
        .layout-btn.active {{
            background: linear-gradient(45deg, #27AE60, #2ECC71);
            border-color: #27AE60;
        }}
        
        .node {{
            stroke: rgba(255, 255, 255, 0.8);
            stroke-width: 2px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .node:hover {{
            stroke-width: 3px;
            stroke: #F39C12;
        }}
        
        .link {{
            stroke: rgba(255, 255, 255, 0.6);
            stroke-width: 2;
            transition: all 0.2s ease;
            marker-end: url(#arrow);
        }}
        
        .link:hover {{
            stroke: rgba(255, 255, 255, 0.9);
            stroke-width: 3;
        }}
        
        .node-label {{
            fill: white;
            font-size: 10px;
            font-weight: bold;
            text-anchor: middle;
            pointer-events: none;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        
        .filtered {{
            opacity: 0.15 !important;
            filter: grayscale(80%);
        }}
        
        .highlighted {{
            opacity: 1 !important;
        }}
        
        .search-highlighted {{
            stroke: #F39C12 !important;
            stroke-width: 4px !important;
            opacity: 1 !important;
            filter: drop-shadow(0 0 8px #F39C12);
            animation: ledBreathing 2s ease-in-out infinite;
        }}
        
        .search-parent {{
            stroke: #E74C3C !important;
            stroke-width: 3px !important;
            opacity: 1 !important;
            filter: drop-shadow(0 0 6px #E74C3C);
        }}
        
        .search-child {{
            stroke: #3498DB !important;
            stroke-width: 3px !important;
            opacity: 1 !important;
            filter: drop-shadow(0 0 6px #3498DB);
        }}
        
        .context-menu {{
            position: absolute;
            background: rgba(0, 0, 0, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 6px;
            padding: 8px 0;
            z-index: 1000;
            backdrop-filter: blur(10px);
            min-width: 180px;
        }}
        
        .context-menu-item {{
            padding: 6px 12px;
            color: white;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.2s ease;
        }}
        
        .context-menu-item:hover {{
            background: rgba(255, 255, 255, 0.1);
        }}
        
        .context-menu-separator {{
            height: 1px;
            background: rgba(255, 255, 255, 0.2);
            margin: 4px 0;
        }}
        
        #filterInput {{
            color: white !important;
        }}
        
        #filterInput::placeholder {{
            color: rgba(255, 255, 255, 0.6);
        }}
        
        .flow-path {{
            stroke: #F39C12;
            stroke-width: 4;
            opacity: 0.8;
            animation: flowPulse 2s infinite;
        }}
        
        .selection-rect {{
            fill: rgba(52, 152, 219, 0.2);
            stroke: #3498DB;
            stroke-width: 2;
            stroke-dasharray: 5,5;
            pointer-events: none;
        }}
        
        .selected-node {{
            stroke: #F39C12 !important;
            stroke-width: 4px !important;
            filter: drop-shadow(0 0 8px #F39C12);
        }}
        
        .selection-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            pointer-events: none;
            z-index: 100;
        }}
        
        @keyframes flowPulse {{
            0%, 100% {{ opacity: 0.8; }}
            50% {{ opacity: 1; }}
        }}
        
        @keyframes searchPulse {{
            0%, 100% {{ 
                filter: drop-shadow(0 0 8px #F39C12);
                stroke-width: 4px;
            }}
            50% {{ 
                filter: drop-shadow(0 0 12px #F39C12);
                stroke-width: 5px;
            }}
        }}
        
        @keyframes ledBreathing {{
            0% {{ 
                filter: drop-shadow(0 0 5px #F39C12) drop-shadow(0 0 10px #F39C12);
                stroke: #F39C12;
                stroke-width: 4px;
                opacity: 0.7;
            }}
            15% {{ 
                filter: drop-shadow(0 0 8px #FFD700) drop-shadow(0 0 15px #FFD700);
                stroke: #FFD700;
                stroke-width: 5px;
                opacity: 0.85;
            }}
            30% {{ 
                filter: drop-shadow(0 0 12px #FFA500) drop-shadow(0 0 20px #FFA500);
                stroke: #FFA500;
                stroke-width: 6px;
                opacity: 1;
            }}
            45% {{ 
                filter: drop-shadow(0 0 15px #FF6347) drop-shadow(0 0 25px #FF6347);
                stroke: #FF6347;
                stroke-width: 6px;
                opacity: 1;
            }}
            60% {{ 
                filter: drop-shadow(0 0 12px #FFA500) drop-shadow(0 0 20px #FFA500);
                stroke: #FFA500;
                stroke-width: 6px;
                opacity: 1;
            }}
            75% {{ 
                filter: drop-shadow(0 0 8px #FFD700) drop-shadow(0 0 15px #FFD700);
                stroke: #FFD700;
                stroke-width: 5px;
                opacity: 0.85;
            }}
            100% {{ 
                filter: drop-shadow(0 0 5px #F39C12) drop-shadow(0 0 10px #F39C12);
                stroke: #F39C12;
                stroke-width: 4px;
                opacity: 0.7;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔄 SPS Diameter Routing Flow - Multi-Select Interactive Visualization</h1>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{stats['total_nodes']}</div>
                    <div>Nodes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['total_links']}</div>
                    <div>Flows</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['total_realms']}</div>
                    <div>Realms</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['total_chains']}</div>
                    <div>Chains</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['total_rules']}</div>
                    <div>Rules</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['total_devices']}</div>
                    <div>Devices</div>
                </div>
            </div>
            
            <div class="controls">
                <div class="control-group">
                    <label>Controls:</label>
                    <button onclick="toggleLabels()" id="labelBtn">�️ Labels</button>
                    <button onclick="animateFlow()" id="flowBtn">⚡ Flow</button>
                    <button onclick="clearSelection()" id="clearSelBtn">🚫 Clear Selection</button>
                </div>
                <div class="control-group">
                    <label>Filter:</label>
                    <input type="text" id="filterInput" placeholder="Search nodes (RegExp supported)..." onkeyup="filterNodes(this.value)" style="padding: 3px 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.3); background: rgba(255,255,255,0.1); color: white; font-size: 0.8em; width: 170px;">
                    <button onclick="clearFilter()">✖️ Clear</button>
                    <label style="font-size: 0.7em; margin-left: 8px;">
                        <input type="checkbox" id="regexMode" style="margin-right: 4px;"> RegExp
                    </label>
                </div>
                <div id="filterStatus" style="display: none; font-size: 0.7em; color: #F39C12; margin-top: 4px; padding: 4px 8px; background: rgba(243, 156, 18, 0.1); border-radius: 4px; border: 1px solid rgba(243, 156, 18, 0.3);">
                    Filter active: <span id="filterInfo"></span>
                </div>
                <div class="control-group">
                    <label>View:</label>
                    <button onclick="showRealms()" id="btnRealms">Realms</button>
                    <button onclick="showEntrances()" id="btnEntrances">Entrances</button>
                    <button onclick="showExits()" id="btnExits">Exits</button>
                    <button onclick="showResults()" id="btnResults">Results</button>
                    <button onclick="showDevices()" id="btnDevices">Devices</button>
                    <button onclick="showAll()" id="btnAll" class="active">All</button>
                </div>
            </div>
        </div>
        
        <div class="main-content">
            <svg id="routing-flow"></svg>
            
            <div class="zoom-controls">
                <div class="zoom-btn" onclick="zoomIn()">+</div>
                <div class="zoom-btn" onclick="zoomOut()">−</div>
                <div class="zoom-btn" onclick="resetZoom()" style="font-size: 12px;">⌂</div>
            </div>
            
            <div class="layout-controls">
                <div class="layout-btn" onclick="scaleOutLayout()" id="scaleOutBtn" title="Scale Out Layout">📏</div>
                <div class="layout-btn" onclick="scaleInLayout()" id="scaleInBtn" title="Scale In Layout">📐</div>
                <div class="layout-btn" onclick="resetSpacing()" id="resetSpacingBtn" title="Reset Layout Spacing">↔️</div>
            </div>
            
            <div class="legend">
                <div style="font-weight: bold; margin-bottom: 6px; color: #3498DB;">Routing Flow</div>
                <div class="legend-item">
                    <div class="legend-circle" style="background: #FF4444;"></div>
                    <span>SPS Core</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="background: #45B7D1;"></div>
                    <span>Realms</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="background: #4ECDC4;"></div>
                    <span>Entrances</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="background: #FECA57;"></div>
                    <span>Rules</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="background: #FF9FF3;"></div>
                    <span>Exits</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="background: #5F27CD;"></div>
                    <span>Results</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="background: #2ECC71;"></div>
                    <span>Devices</span>
                </div>
                <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 9px;">
                    <div style="color: #3498DB; font-weight: bold; margin-bottom: 3px;">Layout Controls:</div>
                    <div>• Scale Out: Increase node spacing (+0.2x per click)</div>
                    <div>• Scale In: Decrease node spacing (-0.2x per click)</div>
                    <div>• Reset Spacing: Default node spacing</div>
                </div>
                <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 9px;">
                    <div style="color: #F39C12; font-weight: bold; margin-bottom: 3px;">Filter Highlighting:</div>
                    <div style="color: #F39C12;">� Direct matches (LED breathing)</div>
                    <div style="color: #E74C3C;">🔴 Connected nodes (path)</div>
                    <div style="color: #95A5A6;">⚪ Filtered out (dimmed)</div>
                    <div style="color: #3498DB; margin-top: 3px; font-size: 8px;">RegExp: /pattern/flags syntax supported</div>
                </div>
                <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 9px;">
                    <div style="color: #F39C12; font-weight: bold; margin-bottom: 3px;">Multi-Selection Controls:</div>
                    <div>• Shift+Click: Add nodes to selection</div>
                    <div>• Ctrl+Drag: Rectangle select</div>
                    <div>• Drag selected: Move group together</div>
                    <div>• Clear button: Reset selection</div>
                </div>
                <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 8px;">
                    <div style="color: #3498DB; font-weight: bold; margin-bottom: 3px;">RegExp Examples:</div>
                    <div>• ^RT.*: Nodes starting with "RT"</div>
                    <div>• .*PCRF.*: Nodes containing "PCRF"</div>
                    <div>• (HSS|MME): Nodes with "HSS" or "MME"</div>
                    <div>• \\d+: Nodes with numbers</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Data
        const nodes = {json.dumps(self.nodes, indent=8)};
        const links = {json.dumps(self.links, indent=8)};
        
        // SVG setup
        const svg = d3.select("#routing-flow");
        const container = d3.select(".main-content");
        
        // Get container dimensions
        const containerRect = container.node().getBoundingClientRect();
        let width = containerRect.width;
        let height = containerRect.height;
        
        svg.attr("width", width).attr("height", height);
        
        // Create zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 3])
            .on("zoom", handleZoom);
        
        svg.call(zoom);
        
        // Create main group for zooming/panning
        const g = svg.append("g");
        
        // Create tooltip
        const tooltip = d3.select("body").append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);
        
        // Add arrow markers
        g.append("defs").append("marker")
            .attr("id", "arrow")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 20)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("class", "arrow")
            .style("fill", "rgba(255, 255, 255, 0.6)");
        
        // Layout spacing multipliers for expand/compact functionality
        let horizontalSpacingMultiplier = 1.0;
        let verticalSpacingMultiplier = 1.0;
        
        // Initialize minimal wave layout with subtle responsive spacing
        function initializeTreeLayout() {{
            const startX = 150;
            const startY = height / 2;
            
            // Dynamic spacing based on viewport size and node count (minimal wave)
            const nodeCount = nodes.length;
            const baseHorizontalSpacing = Math.min(400, Math.max(250, width / (nodeCount / 3))) * horizontalSpacingMultiplier;
            const baseVerticalSpacing = Math.min(100, Math.max(60, height / (nodeCount / 2))) * verticalSpacingMultiplier;
            const dynamicZigzagOffset = Math.min(50, Math.max(25, height / 20)) * verticalSpacingMultiplier; // Slightly larger wave
            
            // Position SPS_ROUTING_CORE as root at left
            const coreNode = nodes.find(n => n.id === 'SPS_ROUTING_CORE');
            if (coreNode) {{
                coreNode.x = startX;
                coreNode.y = startY;
            }}
            
            // Group nodes by type and layer for minimal wave layout
            const nodesByLayer = {{}};
            nodes.filter(n => n.id !== 'SPS_ROUTING_CORE').forEach(node => {{
                const layer = node.layer || 1;
                if (!nodesByLayer[layer]) {{
                    nodesByLayer[layer] = [];
                }}
                nodesByLayer[layer].push(node);
            }});
            
            // Calculate optimal layer spacing based on content
            const layerCount = Object.keys(nodesByLayer).length;
            const horizontalSpacing = (layerCount > 5 ? baseHorizontalSpacing * 0.8 : baseHorizontalSpacing) * horizontalSpacingMultiplier;
            
            // Position nodes in minimal wave pattern
            Object.keys(nodesByLayer).sort((a, b) => parseInt(a) - parseInt(b)).forEach((layer, layerIndex) => {{
                const layerNodes = nodesByLayer[layer];
                const layerX = startX + (layerIndex + 1) * horizontalSpacing;
                
                // Minimal wave pattern with tiny vertical offset
                const isEvenLayer = layerIndex % 2 === 0;
                const layerOffset = isEvenLayer ? -dynamicZigzagOffset : dynamicZigzagOffset;
                const baseY = startY + layerOffset;
                
                // Calculate vertical distribution with enlarged spacing
                const nodeSpacing = Math.max(baseVerticalSpacing, layerNodes.length > 10 ? 75 : 85) * verticalSpacingMultiplier;
                const totalHeight = (layerNodes.length - 1) * nodeSpacing;
                const layerStartY = baseY - totalHeight / 2;
                
                layerNodes.forEach((node, nodeIndex) => {{
                    node.x = layerX;
                    // Enhanced wave within layer for better visibility
                    const nodeZigzag = (nodeIndex % 2 === 0) ? 0 : Math.min(20, nodeSpacing * 0.25) * verticalSpacingMultiplier;
                    const progressiveOffset = Math.floor(nodeIndex / 10) * 15 * verticalSpacingMultiplier; // Group every 10 nodes with larger offset
                    node.y = layerStartY + nodeIndex * nodeSpacing + nodeZigzag + progressiveOffset;
                }});
            }});
            
            console.log("Enhanced layout initialized with configurable spacing - horizontal:", horizontalSpacingMultiplier, "vertical:", verticalSpacingMultiplier);
        }}
        
        // Initialize with tree layout
        initializeTreeLayout();
        
        // No force simulation - static positioning
        const simulation = null;
        
        // Create curved links for zig-zag flow visualization
        const link = g.append("g")
            .selectAll("path")
            .data(links)
            .join("path")
            .attr("class", "link")
            .style("stroke-width", d => {{
                return d.type === 'FLOW_CONNECTION' ? 3 : 2;
            }})
            .style("fill", "none");
        
        // Create nodes with multi-select drag positioning
        const node = g.append("g")
            .selectAll("circle")
            .data(nodes)
            .join("circle")
            .attr("class", "node")
            .attr("r", d => d.size)
            .attr("fill", d => d.color)
            .call(createMultiSelectDrag())
            .on("mouseover", showTooltip)
            .on("mousemove", moveTooltip)
            .on("mouseout", hideTooltip)
            .on("click", nodeClick)
            .on("contextmenu", showContextMenu);
        
        // Create labels with static positioning
        let labelsVisible = true;
        const labels = g.append("g")
            .selectAll("text")
            .data(nodes)
            .join("text")
            .attr("class", "node-label")
            .text(d => {{
                // Enhanced labels with correct command prefixes
                let labelText = '';
                
                // Use actual MML command prefixes based on node type
                let typePrefix = '';
                if (d.type === 'DIAMETER_REALM') {{
                    typePrefix = 'DMRT';
                }} else if (d.type === 'ROUTE_ENTRANCE') {{
                    typePrefix = 'RTENT';
                }} else if (d.type === 'ROUTE_EXIT') {{
                    typePrefix = 'RTEXIT';
                }} else if (d.type === 'ROUTE_RESULT') {{
                    typePrefix = 'RTRESULT';
                }} else if (d.type === 'ROUTE_DEVICE') {{
                    typePrefix = 'DEVICE';
                }} else if (d.type === 'ROUTE_RULE') {{
                    // Extract actual rule type from rule data
                    if (d.rule_type) {{
                        typePrefix = d.rule_type;
                    }} else {{
                        typePrefix = 'RULE';
                    }}
                }} else if (d.type === 'SPS_CORE') {{
                    typePrefix = '';
                }} else {{
                    typePrefix = d.type || '';
                }}
                
                // Get the main label text
                let mainText = d.display_label || d.name;
                if (d.display_value && d.display_value !== d.name) {{
                    mainText = d.display_value;
                }}
                
                // Combine command prefix and label
                if (typePrefix && typePrefix !== '') {{
                    labelText = `[${{typePrefix}}] ${{mainText}}`;
                }} else {{
                    labelText = mainText;
                }}
                
                // Display complete label without truncation
                return labelText;
            }})
            .style("font-size", d => Math.max(9, d.size / 3) + "px");
        
        // Initial positioning update
        updatePositions();
        
        // Function to update all positions with curved zig-zag connections
        function updatePositions() {{
            // Update links to connect source and target nodes
            links.forEach(link => {{
                const sourceNode = nodes.find(n => n.id === link.source.id || n.id === link.source);
                const targetNode = nodes.find(n => n.id === link.target.id || n.id === link.target);
                if (sourceNode && targetNode) {{
                    link.source = sourceNode;
                    link.target = targetNode;
                }}
            }});
            
            // Create curved paths for zig-zag visualization
            link.attr("d", d => {{
                const x1 = d.source.x;
                const y1 = d.source.y;
                const x2 = d.target.x;
                const y2 = d.target.y;
                
                // Calculate control points for smooth curves
                const dx = x2 - x1;
                const dy = y2 - y1;
                const dr = Math.sqrt(dx * dx + dy * dy);
                
                // Create curved path for flow connections to emphasize zig-zag
                if (d.type === 'FLOW_CONNECTION' && Math.abs(dy) > 30) {{
                    const midX = (x1 + x2) / 2;
                    const curve = Math.min(50, Math.abs(dy) * 0.3);
                    return `M${{x1}},${{y1}} Q${{midX}},${{y1 + curve}} ${{x2}},${{y2}}`;
                }} else {{
                    // Slight curve for other connections
                    const curve = Math.min(20, dr * 0.1);
                    return `M${{x1}},${{y1}} Q${{x1 + dx/2}},${{y1 + curve}} ${{x2}},${{y2}}`;
                }}
            }});
            
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
            
            labels
                .attr("x", d => d.x)
                .attr("y", d => d.y + 4); // Slightly better offset for label positioning
        }}
        
        // Zoom and pan handlers
        function handleZoom(event) {{
            g.attr("transform", event.transform);
        }}
        
        function zoomIn() {{
            svg.transition().duration(300).call(zoom.scaleBy, 1.5);
        }}
        
        function zoomOut() {{
            svg.transition().duration(300).call(zoom.scaleBy, 1 / 1.5);
        }}
        
        function resetZoom() {{
            svg.transition().duration(500).call(
                zoom.transform,
                d3.zoomIdentity.translate(0, 0).scale(1)
            );
        }}
        
        // Manual drag behavior (no force simulation)
        function manualDrag() {{
            function dragstarted(event, d) {{
                // Visual feedback
                d3.select(this).style("cursor", "grabbing");
            }}
            
            function dragged(event, d) {{
                // Update node position
                d.x = event.x;
                d.y = event.y;
                
                // Update visual positions immediately
                d3.select(this)
                    .attr("cx", d.x)
                    .attr("cy", d.y);
                
                // Update label position
                labels.filter(n => n.id === d.id)
                    .attr("x", d.x)
                    .attr("y", d.y + 4);
                
                // Update connected links with curved paths
                link.filter(l => l.source.id === d.id || l.target.id === d.id)
                    .attr("d", l => {{
                        const x1 = l.source.x;
                        const y1 = l.source.y;
                        const x2 = l.target.x;
                        const y2 = l.target.y;
                        
                        const dx = x2 - x1;
                        const dy = y2 - y1;
                        const dr = Math.sqrt(dx * dx + dy * dy);
                        
                        if (l.type === 'FLOW_CONNECTION' && Math.abs(dy) > 30) {{
                            const midX = (x1 + x2) / 2;
                            const curve = Math.min(50, Math.abs(dy) * 0.3);
                            return `M${{x1}},${{y1}} Q${{midX}},${{y1 + curve}} ${{x2}},${{y2}}`;
                        }} else {{
                            const curve = Math.min(20, dr * 0.1);
                            return `M${{x1}},${{y1}} Q${{x1 + dx/2}},${{y1 + curve}} ${{x2}},${{y2}}`;
                        }}
                    }});
            }}
            
            function dragended(event, d) {{
                // Reset cursor
                d3.select(this).style("cursor", "pointer");
            }}
            
            return d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended);
        }}
        
        // Legacy drag function (kept for compatibility)
        function drag(simulation) {{
            return manualDrag();
        }}
        
        // Selection functionality
        let selectedNodes = new Set();
        let isSelecting = false;
        let selectionStart = null;
        let selectionRect = null;
        let isDraggingSelection = false;
        
        // Add selection rectangle to the SVG
        const selectionLayer = g.append("g").attr("class", "selection-layer");
        
        // Mouse event handlers for selection
        svg.on("mousedown", function(event) {{
            if (event.ctrlKey || event.metaKey) {{
                // Start rectangle selection
                isSelecting = true;
                const coords = d3.pointer(event, g.node());
                selectionStart = {{ x: coords[0], y: coords[1] }};
                
                // Create selection rectangle
                selectionRect = selectionLayer.append("rect")
                    .attr("class", "selection-rect")
                    .attr("x", selectionStart.x)
                    .attr("y", selectionStart.y)
                    .attr("width", 0)
                    .attr("height", 0);
                
                event.stopPropagation();
                event.preventDefault();
            }}
        }});
        
        svg.on("mousemove", function(event) {{
            if (isSelecting && selectionRect) {{
                const coords = d3.pointer(event, g.node());
                const width = coords[0] - selectionStart.x;
                const height = coords[1] - selectionStart.y;
                
                selectionRect
                    .attr("x", Math.min(selectionStart.x, coords[0]))
                    .attr("y", Math.min(selectionStart.y, coords[1]))
                    .attr("width", Math.abs(width))
                    .attr("height", Math.abs(height));
            }}
        }});
        
        svg.on("mouseup", function(event) {{
            if (isSelecting && selectionRect) {{
                // Finalize selection
                const coords = d3.pointer(event, g.node());
                const minX = Math.min(selectionStart.x, coords[0]);
                const maxX = Math.max(selectionStart.x, coords[0]);
                const minY = Math.min(selectionStart.y, coords[1]);
                const maxY = Math.max(selectionStart.y, coords[1]);
                
                // Clear previous selection if not holding shift
                if (!event.shiftKey) {{
                    clearSelection();
                }}
                
                // Select nodes within rectangle
                nodes.forEach(node => {{
                    if (node.x >= minX && node.x <= maxX && 
                        node.y >= minY && node.y <= maxY) {{
                        selectedNodes.add(node.id);
                    }}
                }});
                
                updateSelectionVisual();
                selectionRect.remove();
                selectionRect = null;
                isSelecting = false;
            }}
        }});
        
        function updateSelectionVisual() {{
            node.classed("selected-node", d => selectedNodes.has(d.id));
            console.log("Selection updated. Currently selected nodes:", Array.from(selectedNodes));
        }}
        
        function clearSelection() {{
            const prevSize = selectedNodes.size;
            selectedNodes.clear();
            updateSelectionVisual();
            if (prevSize > 0) {{
                console.log("Cleared", prevSize, "selected nodes");
            }}
        }}
        
        // Enhanced drag for multiple selection
        function createMultiSelectDrag() {{
            function dragstarted(event, d) {{
                if (selectedNodes.has(d.id) && selectedNodes.size > 1) {{
                    // Multiple nodes selected, prepare for group drag
                    isDraggingSelection = true;
                    // Store initial positions for all selected nodes
                    selectedNodes.forEach(nodeId => {{
                        const node = nodes.find(n => n.id === nodeId);
                        if (node) {{
                            node._dragStartX = node.x;
                            node._dragStartY = node.y;
                        }}
                    }});
                    console.log("Starting group drag with", selectedNodes.size, "nodes");
                }} else {{
                    // Single node or unselected node being dragged
                    if (!selectedNodes.has(d.id)) {{
                        // If dragging an unselected node and shift is not pressed, clear selection
                        if (!event.shiftKey && !event.ctrlKey && !event.metaKey) {{
                            clearSelection();
                        }}
                        selectedNodes.add(d.id);
                        updateSelectionVisual();
                    }}
                    isDraggingSelection = false;
                    // Store position for single node drag
                    d._dragStartX = d.x;
                    d._dragStartY = d.y;
                }}
                d3.select(this).style("cursor", "grabbing");
            }}
            
            function dragged(event, d) {{
                if (isDraggingSelection && selectedNodes.size > 1) {{
                    // Move all selected nodes together
                    const dx = event.x - d._dragStartX;
                    const dy = event.y - d._dragStartY;
                    
                    selectedNodes.forEach(nodeId => {{
                        const node = nodes.find(n => n.id === nodeId);
                        if (node && node._dragStartX !== undefined) {{
                            node.x = node._dragStartX + dx;
                            node.y = node._dragStartY + dy;
                        }}
                    }});
                    
                    // Update all visual elements for selected nodes
                    node.filter(n => selectedNodes.has(n.id))
                        .attr("cx", n => n.x)
                        .attr("cy", n => n.y);

                    labels.filter(n => selectedNodes.has(n.id))
                        .attr("x", n => n.x)
                        .attr("y", n => n.y + 4);
                    
                    // Update links connected to any selected node
                    updateLinksForSelectedNodes();
                }} else {{
                    // Single node drag behavior
                    d.x = event.x;
                    d.y = event.y;
                    
                    d3.select(this)
                        .attr("cx", d.x)
                        .attr("cy", d.y);
                    
                    labels.filter(n => n.id === d.id)
                        .attr("x", d.x)
                        .attr("y", d.y + 4);
                    
                    updateLinksForNode(d);
                }}
            }}
            
            function dragended(event, d) {{
                isDraggingSelection = false;
                // Clear drag start positions
                nodes.forEach(node => {{
                    delete node._dragStartX;
                    delete node._dragStartY;
                }});
                d3.select(this).style("cursor", "pointer");
            }}
            
            return d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended);
        }}
        
        function updateLinksForSelectedNodes() {{
            selectedNodes.forEach(nodeId => {{
                const node = nodes.find(n => n.id === nodeId);
                if (node) {{
                    updateLinksForNode(node);
                }}
            }});
        }}
        
        function updateLinksForNode(node) {{
            // Update connected links with curved paths
            link.filter(l => l.source.id === node.id || l.target.id === node.id)
                .attr("d", l => {{
                    const x1 = l.source.x;
                    const y1 = l.source.y;
                    const x2 = l.target.x;
                    const y2 = l.target.y;
                    
                    const dx = x2 - x1;
                    const dy = y2 - y1;
                    const dr = Math.sqrt(dx * dx + dy * dy);
                    
                    if (l.type === 'FLOW_CONNECTION' && Math.abs(dy) > 30) {{
                        const midX = (x1 + x2) / 2;
                        const curve = Math.min(50, Math.abs(dy) * 0.3);
                        return `M${{x1}},${{y1}} Q${{midX}},${{y1 + curve}} ${{x2}},${{y2}}`;
                    }} else {{
                        const curve = Math.min(20, dr * 0.1);
                        return `M${{x1}},${{y1}} Q${{x1 + dx/2}},${{y1 + curve}} ${{x2}},${{y2}}`;
                    }}
                }});
        }}
        
        // Tooltip functions with enhanced information
        function showTooltip(event, d) {{
            const details = Object.entries(d.details || {{}})
                .filter(([key, value]) => value && value !== '' && value !== 'N/A')
                .map(([key, value]) => `<div>${{key}}:</div><div>${{value}}</div>`)
                .join('');
            
            let additionalInfo = '';
            if (d.display_value && d.display_value !== d.name) {{
                additionalInfo += `<div>Value:</div><div>${{d.display_value}}</div>`;
            }}
            if (d.mml_command) {{
                const shortMml = d.mml_command.length > 50 ? 
                    d.mml_command.substring(0, 50) + "..." : d.mml_command;
                additionalInfo += `<div>MML:</div><div style="font-family: monospace; font-size: 8px;">${{shortMml}}</div>`;
            }}
            
            tooltip.transition()
                .duration(200)
                .style("opacity", .9);
            
            tooltip.html(`
                <h4>${{d.display_label || d.name}}</h4>
                <div class="tooltip-content">
                    ${{details}}
                    ${{additionalInfo}}
                </div>
            `);
        }}
        
        function moveTooltip(event) {{
            tooltip
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
        }}
        
        function hideTooltip() {{
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        }}
        
        // Context menu functionality
        let contextMenu = null;
        
        function showContextMenu(event, d) {{
            event.preventDefault();
            hideContextMenu();
            
            contextMenu = d3.select("body")
                .append("div")
                .attr("class", "context-menu")
                .style("left", event.pageX + "px")
                .style("top", event.pageY + "px");
            
            // Add menu items
            contextMenu.append("div")
                .attr("class", "context-menu-item")
                .text("📋 Copy Node Info")
                .on("click", () => copyNodeInfo(d));
            
            if (d.mml_command) {{
                contextMenu.append("div")
                    .attr("class", "context-menu-item")
                    .text("📝 Copy MML Command")
                    .on("click", () => copyMMLCommand(d));
            }}
            
            contextMenu.append("div").attr("class", "context-menu-separator");
            
            contextMenu.append("div")
                .attr("class", "context-menu-item")
                .text("🎯 Center on Node")
                .on("click", () => centerOnNode(d));
            
            contextMenu.append("div")
                .attr("class", "context-menu-item")
                .text("🔗 Highlight Path")
                .on("click", () => highlightPath(d));
            
            contextMenu.append("div")
                .attr("class", "context-menu-item")
                .text("🔍 Show Connected")
                .on("click", () => showConnectedNodes(d));
        }}
        
        function hideContextMenu() {{
            if (contextMenu) {{
                contextMenu.remove();
                contextMenu = null;
            }}
        }}
        
        function copyNodeInfo(d) {{
            const info = `Node: ${{d.name}}
Type: ${{d.type}}
ID: ${{d.id}}
${{Object.entries(d.details || {{}}).map(([k, v]) => `${{k}}: ${{v}}`).join('\\n')}}
${{d.display_value ? `Value: ${{d.display_value}}` : ''}}`;
            
            navigator.clipboard.writeText(info).then(() => {{
                console.log("Node info copied to clipboard");
                showNotification("Node info copied!");
            }});
            hideContextMenu();
        }}
        
        function copyMMLCommand(d) {{
            if (d.mml_command) {{
                navigator.clipboard.writeText(d.mml_command).then(() => {{
                    console.log("MML command copied to clipboard");
                    showNotification("MML command copied!");
                }});
            }}
            hideContextMenu();
        }}
        
        function centerOnNode(d) {{
            const transform = d3.zoomIdentity
                .translate(width / 2 - d.x, height / 2 - d.y)
                .scale(1.5);
            
            svg.transition()
                .duration(750)
                .call(zoom.transform, transform);
            
            hideContextMenu();
        }}
        
        function showConnectedNodes(d) {{
            // Reset highlighting
            node.classed("search-highlighted search-parent", false);
            link.classed("flow-path", false);
            
            // Highlight the selected node
            node.filter(n => n.id === d.id).classed("search-highlighted", true);
            
            // Find and highlight connected nodes
            const connectedIds = new Set();
            links.forEach(l => {{
                if (l.source.id === d.id) {{
                    connectedIds.add(l.target.id);
                    link.filter(link => link.source.id === d.id && link.target.id === l.target.id)
                        .classed("flow-path", true);
                }} else if (l.target.id === d.id) {{
                    connectedIds.add(l.source.id);
                    link.filter(link => link.source.id === l.source.id && link.target.id === d.id)
                        .classed("flow-path", true);
                }}
            }});
            
            // Highlight connected nodes
            node.filter(n => connectedIds.has(n.id)).classed("search-parent", true);
            
            hideContextMenu();
        }}
        
        function showNotification(message) {{
            const notification = d3.select("body")
                .append("div")
                .style("position", "fixed")
                .style("top", "20px")
                .style("right", "20px")
                .style("background", "rgba(0, 0, 0, 0.8)")
                .style("color", "white")
                .style("padding", "10px 15px")
                .style("border-radius", "6px")
                .style("z-index", "2000")
                .text(message);
            
            setTimeout(() => notification.remove(), 3000);
        }}
        
        // Click outside to hide context menu
        d3.select("body").on("click", hideContextMenu);
        
        function nodeClick(event, d) {{
            console.log("Clicked node:", d);
            
            // Handle selection if modifier keys are pressed
            if (event.ctrlKey || event.metaKey) {{
                // Toggle selection (Ctrl/Cmd + click)
                if (selectedNodes.has(d.id)) {{
                    selectedNodes.delete(d.id);
                }} else {{
                    selectedNodes.add(d.id);
                }}
                updateSelectionVisual();
                event.stopPropagation();
            }} else if (event.shiftKey) {{
                // Add to selection (Shift + click) - never removes, only adds
                selectedNodes.add(d.id);
                updateSelectionVisual();
                event.stopPropagation();
                console.log("Added node to selection with Shift+click. Total selected:", selectedNodes.size);
            }} else {{
                // Regular click - clear previous selection and either select this node or highlight path
                if (selectedNodes.size > 0) {{
                    // If we have multiple selections, clear them and select this one
                    clearSelection();
                    selectedNodes.add(d.id);
                    updateSelectionVisual();
                }} else {{
                    // Single node - highlight routing path from this node
                    highlightPath(d);
                }}
            }}
        }}
        
        function highlightPath(startNode) {{
            // Reset all highlighting
            node.classed("highlighted", false);
            link.classed("flow-path", false);
            
            // Find and highlight path
            const visited = new Set();
            const queue = [startNode];
            
            while (queue.length > 0) {{
                const current = queue.shift();
                if (visited.has(current.id)) continue;
                visited.add(current.id);
                
                // Highlight current node
                node.filter(d => d.id === current.id).classed("highlighted", true);
                
                // Find connected nodes and links
                links.forEach(l => {{
                    if (l.source.id === current.id) {{
                        link.filter(d => d.source.id === current.id && d.target.id === l.target.id)
                            .classed("flow-path", true);
                        if (!visited.has(l.target.id)) {{
                            queue.push(l.target);
                        }}
                    }}
                }});
            }}
        }}
        
        // Control functions
        function toggleLabels() {{
            labelsVisible = !labelsVisible;
            labels.style("opacity", labelsVisible ? 1 : 0);
            document.getElementById("labelBtn").classList.toggle("active");
        }}
        
        // Layout control functions - now allow multiple clicks
        function scaleOutLayout() {{
            horizontalSpacingMultiplier += 0.2;
            verticalSpacingMultiplier += 0.2;
            // Cap the maximum scaling to prevent excessive spacing
            horizontalSpacingMultiplier = Math.min(horizontalSpacingMultiplier, 3.0);
            verticalSpacingMultiplier = Math.min(verticalSpacingMultiplier, 3.0);
            
            initializeTreeLayout();
            updatePositions();
            setActiveLayoutButton('scaleOutBtn');
            console.log("Layout scaled out - spacing multipliers now:", horizontalSpacingMultiplier.toFixed(1) + "x");
        }}
        
        function scaleInLayout() {{
            horizontalSpacingMultiplier -= 0.2;
            verticalSpacingMultiplier -= 0.2;
            // Cap the minimum scaling to prevent too compact layout
            horizontalSpacingMultiplier = Math.max(horizontalSpacingMultiplier, 0.3);
            verticalSpacingMultiplier = Math.max(verticalSpacingMultiplier, 0.3);
            
            initializeTreeLayout();
            updatePositions();
            setActiveLayoutButton('scaleInBtn');
            console.log("Layout scaled in - spacing multipliers now:", horizontalSpacingMultiplier.toFixed(1) + "x");
        }}
        
        function resetSpacing() {{
            horizontalSpacingMultiplier = 1.0;
            verticalSpacingMultiplier = 1.0;
            initializeTreeLayout();
            updatePositions();
            setActiveLayoutButton('resetSpacingBtn');
            console.log("Layout spacing reset to default");
        }}
        
        function setActiveLayoutButton(activeId) {{
            document.querySelectorAll('#scaleOutBtn, #scaleInBtn, #resetSpacingBtn')
                .forEach(btn => btn.classList.remove('active'));
            document.getElementById(activeId).classList.add('active');
        }}
        
        // Enhanced filter functionality with complete path highlighting and RegExp support
        function filterNodes(searchTerm) {{
            if (!searchTerm.trim()) {{
                clearFilter();
                return;
            }}
            
            const term = searchTerm;
            const isRegexMode = document.getElementById('regexMode').checked;
            let searchPattern = null;
            let isValidRegex = false;
            
            // Prepare search pattern
            if (isRegexMode) {{
                try {{
                    searchPattern = new RegExp(term, 'i'); // Case-insensitive regex
                    isValidRegex = true;
                }} catch (e) {{
                    console.warn("Invalid regex pattern, falling back to string search:", e.message);
                    isValidRegex = false;
                }}
            }}
            
            // Reset all highlighting
            node.classed("search-highlighted search-parent search-child filtered", false);
            link.classed("flow-path filtered", false);
            
            const matchedNodes = new Set();
            const pathNodes = new Set();
            const pathLinks = new Set();
            
            // Enhanced matching function with RegExp support
            function matchesPattern(text) {{
                if (!text) return false;
                
                if (isRegexMode && isValidRegex) {{
                    return searchPattern.test(text.toString());
                }} else {{
                    return text.toString().toLowerCase().includes(term.toLowerCase());
                }}
            }}
            
            // Find matching nodes with comprehensive search and RegExp support
            nodes.forEach(n => {{
                const matches = 
                    matchesPattern(n.name) ||
                    matchesPattern(n.display_label) ||
                    matchesPattern(n.display_value) ||
                    matchesPattern(n.type) ||
                    matchesPattern(n.command_type) ||
                    matchesPattern(n.mml_command) ||
                    Object.values(n.details || {{}}).some(v => matchesPattern(v)) ||
                    Object.keys(n).some(key => 
                        n[key] && typeof n[key] === 'string' && matchesPattern(n[key])
                    );
                
                if (matches) {{
                    matchedNodes.add(n.id);
                }}
            }});
            
            // Enhanced path discovery - find complete routing chains for matched nodes
            function traceCompletePath(startNodeId, visited = new Set()) {{
                if (visited.has(startNodeId)) return;
                visited.add(startNodeId);
                pathNodes.add(startNodeId);
                
                // Find all connected links and nodes
                links.forEach(link => {{
                    let connectedNodeId = null;
                    let linkKey = null;
                    
                    if (link.source.id === startNodeId) {{
                        connectedNodeId = link.target.id;
                        linkKey = `${{link.source.id}}-${{link.target.id}}`;
                    }} else if (link.target.id === startNodeId) {{
                        connectedNodeId = link.source.id;
                        linkKey = `${{link.source.id}}-${{link.target.id}}`;
                    }}
                    
                    if (connectedNodeId && !visited.has(connectedNodeId)) {{
                        pathLinks.add(linkKey);
                        pathNodes.add(connectedNodeId);
                        
                        // Continue tracing for routing chains (limit depth to prevent infinite loops)
                        const connectedNode = nodes.find(n => n.id === connectedNodeId);
                        if (connectedNode && 
                            (connectedNode.type === 'ROUTE_RULE' || 
                             connectedNode.type === 'ROUTE_ENTRANCE' || 
                             connectedNode.type === 'ROUTE_EXIT' ||
                             connectedNode.type === 'ROUTE_RESULT') &&
                            visited.size < 20) {{
                            traceCompletePath(connectedNodeId, visited);
                        }}
                    }}
                }});
            }}
            
            // Trace complete paths for all matched nodes
            matchedNodes.forEach(nodeId => {{
                traceCompletePath(nodeId);
            }});
            
            // Special handling for core node - always include it in path if any routing nodes are matched
            const coreNode = nodes.find(n => n.id === 'SPS_ROUTING_CORE');
            if (coreNode && pathNodes.size > 0) {{
                pathNodes.add(coreNode.id);
            }}
            
            // Apply advanced filtering with path highlighting
            node.classed("filtered", n => {{
                // Always show the core node
                if (n.id === 'SPS_ROUTING_CORE') return false;
                // Show nodes that are part of the matched paths
                return !matchedNodes.has(n.id) && !pathNodes.has(n.id);
            }});
            
            // Apply different highlighting classes with LED breathing effect for direct matches
            node.classed("search-highlighted", n => matchedNodes.has(n.id));
            node.classed("search-parent", n => {{
                return pathNodes.has(n.id) && !matchedNodes.has(n.id) && n.id !== 'SPS_ROUTING_CORE';
            }});
            
            // Enhanced link filtering and highlighting
            link.classed("filtered", l => {{
                const sourceVisible = matchedNodes.has(l.source.id) || pathNodes.has(l.source.id);
                const targetVisible = matchedNodes.has(l.target.id) || pathNodes.has(l.target.id);
                return !(sourceVisible && targetVisible);
            }});
            
            // Highlight all links in the routing paths
            link.classed("flow-path", l => {{
                const linkKey1 = `${{l.source.id}}-${{l.target.id}}`;
                const linkKey2 = `${{l.target.id}}-${{l.source.id}}`;
                const sourceInPath = matchedNodes.has(l.source.id) || pathNodes.has(l.source.id);
                const targetInPath = matchedNodes.has(l.target.id) || pathNodes.has(l.target.id);
                
                return (pathLinks.has(linkKey1) || pathLinks.has(linkKey2)) || 
                       (sourceInPath && targetInPath);
            }});
            
            // Show filter statistics
            const visibleNodes = nodes.filter(n => !n.classList || !n.classList.contains('filtered')).length;
            const searchType = isRegexMode && isValidRegex ? "RegExp" : "Text";
            console.log(`Filter applied (${{searchType}}): "${{term}}" - Showing ${{matchedNodes.size}} matched nodes, ${{pathNodes.size}} path nodes, ${{visibleNodes}} total visible nodes`);
            
            // Update filter status display
            const filterStatus = document.getElementById('filterStatus');
            const filterInfo = document.getElementById('filterInfo');
            if (filterStatus && filterInfo) {{
                const modeText = isRegexMode ? " (RegExp)" : "";
                filterInfo.textContent = `"${{term}}"${{modeText}} - ${{matchedNodes.size}} matches, ${{pathNodes.size}} path nodes shown`;
                filterStatus.style.display = 'block';
            }}
        }}
        
        function clearFilter() {{
            document.getElementById('filterInput').value = '';
            node.classed("filtered search-highlighted search-parent search-child", false);
            link.classed("filtered flow-path", false);
            
            // Hide filter status display
            const filterStatus = document.getElementById('filterStatus');
            if (filterStatus) {{
                filterStatus.style.display = 'none';
            }}
            
            console.log("Filter cleared - all nodes and links visible");
        }}
        
        function animateFlow() {{
            link.classed("flow-path", true);
            setTimeout(() => {{
                link.classed("flow-path", false);
            }}, 3000);
        }}
        
        function showRealms() {{
            updateTypeFilter('DIAMETER_REALM');
            setActiveButton('btnRealms');
        }}
        
        function showEntrances() {{
            updateTypeFilter('ROUTE_ENTRANCE');
            setActiveButton('btnEntrances');
        }}
        
        function showExits() {{
            updateTypeFilter('ROUTE_EXIT');
            setActiveButton('btnExits');
        }}
        
        function showResults() {{
            updateTypeFilter('ROUTE_RESULT');
            setActiveButton('btnResults');
        }}
        
        function showDevices() {{
            updateTypeFilter('ROUTE_DEVICE');
            setActiveButton('btnDevices');
        }}
        
        function showAll() {{
            node.classed("filtered", false);
            link.classed("filtered", false);
            setActiveButton('btnAll');
        }}
        
        function updateTypeFilter(nodeType) {{
            node.classed("filtered", d => {{
                if (d.id === 'SPS_ROUTING_CORE') return false;
                return d.type !== nodeType;
            }});
            
            link.classed("filtered", d => {{
                const sourceVisible = d.source.id === 'SPS_ROUTING_CORE' || d.source.type === nodeType;
                const targetVisible = d.target.id === 'SPS_ROUTING_CORE' || d.target.type === nodeType;
                return !(sourceVisible && targetVisible);
            }});
        }}
        
        function updateViewFilter(filterType) {{
            node.classed("filtered", d => {{
                return !d.type.includes(filterType) && d.id !== 'SPS_ROUTING_CORE';
            }});
            
            link.classed("filtered", d => {{
                const sourceVisible = !d.source.type || d.source.type.includes(filterType) || d.source.id === 'SPS_ROUTING_CORE';
                const targetVisible = !d.target.type || d.target.type.includes(filterType) || d.target.id === 'SPS_ROUTING_CORE';
                return !(sourceVisible && targetVisible);
            }});
        }}
        
        function setActiveButton(activeId) {{
            document.querySelectorAll('#btnRealms, #btnEntrances, #btnExits, #btnResults, #btnDevices, #btnAll')
                .forEach(btn => btn.classList.remove('active'));
            document.getElementById(activeId).classList.add('active');
        }}
        
        // Resize handler
        window.addEventListener('resize', () => {{
            const newRect = container.node().getBoundingClientRect();
            const newWidth = newRect.width;
            const newHeight = newRect.height;
            
            svg.attr("width", newWidth).attr("height", newHeight);
            
            // Update global width/height variables
            width = newWidth;
            height = newHeight;
            
            // Optionally reposition nodes to fit new dimensions
            updatePositions();
        }});
        
        // Initialize
        console.log("SPS Routing Flow loaded with", nodes.length, "nodes and", links.length, "links");
        console.log("Routing chains:", {stats['total_chains']});
        console.log("Device nodes with priorities:", {stats['total_devices']});
        console.log("Enhanced with multi-node selection and drag capabilities");
        console.log("Enhanced with layout spacing controls:");
        console.log("  • Scale Out: Increase node spacing (+0.2x per click, max 3.0x)");
        console.log("  • Scale In: Decrease node spacing (-0.2x per click, min 0.3x)");
        console.log("  • Reset Spacing: Return to default node spacing (1.0x)");
        console.log("Enhanced Filter Features:");
        console.log("  • LED Breathing Effects: Direct matches show multi-color LED breathing animation");
        console.log("  • RegExp Support: Enable RegExp checkbox for pattern matching");
        console.log("  • Pattern Examples: ^RT.*, .*PCRF.*, (HSS|MME), \\\\d+");
        console.log("  • Path Highlighting: Shows complete routing paths for matched nodes");
        console.log("Multi-Selection Controls:");
        console.log("  • Shift+Click: Add individual nodes to selection");
        console.log("  • Ctrl+Drag: Rectangle selection for multiple nodes");
        console.log("  • Drag multiple selected nodes together for group positioning");
        console.log("  • Ctrl/Cmd+Click: Toggle individual node selection");
        console.log("  • Regular click: Clear selection or highlight routing path");
        
        // Set default active layout button
        setActiveLayoutButton('resetSpacingBtn');
        
        // Set default view to "All" instead of DMRT
        showAll();
    </script>
</body>
</html>'''
        
        try:
            with open(output_filename, 'w', encoding='utf-8') as file:
                file.write(html_template)
            print(f"✅ Interactive routing visualization saved to '{output_filename}'")
            print(f"📊 Generated routing flow with {len(self.nodes)} nodes and {len(self.links)} flows")
            print(f"🔄 Routing chains: {len(self.routing_chains)}")
            print(f"📋 Routing rules: {len(self.routing_rules)}")
            print(f"🌐 Diameter realms: {len(self.realms)}")
            print(f"🚀 Open '{output_filename}' in your web browser to view the interactive routing flow!")
            return True
        except Exception as e:
            print(f"❌ Error saving HTML file: {e}")
            return False
    
    def generate_routing_topology(self, input_file: str):
        """Generate complete routing topology from input file"""
        print(f"🔄 Parsing routing MML file: {input_file}")
        
        # Add central routing core node
        self.add_central_node()
        
        # Parse the routing MML file
        if not self.parse_routing_file(input_file):
            return False
        
        # Generate interactive HTML
        output_file = input_file.replace('.txt', '_routing_flow.html')
        return self.generate_d3_html(output_file)


def main():
    if len(sys.argv) != 2:
        print("Usage: python spsdmrt_topo.py <routing_mml_file>")
        print("Example: python spsdmrt_topo.py spsdmrt.txt")
        print("Example: python spsdmrt_topo.py spsdmrt_complex.txt")
        print("Example: python spsdmrt_topo.py spsdmrt_host.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    generator = DiameterRoutingTopoGenerator()
    
    if generator.generate_routing_topology(input_file):
        print("✅ Routing topology generation completed successfully!")
    else:
        print("❌ Routing topology generation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
