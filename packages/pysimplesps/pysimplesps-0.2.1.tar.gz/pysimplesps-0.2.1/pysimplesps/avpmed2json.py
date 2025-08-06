#!/usr/bin/env python3
"""
SPS AVP Mediation Configuration Parser
Parses Huawei SPS AVP mediation configuration including filters, actions, rules and peer assignments.
"""

import re
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional


class SPSAVPMediationParser:
    """Parser for Huawei SPS AVP Mediation configuration"""
    
    def __init__(self):
        self.mediation_filters = []
        self.mediation_actions = []
        self.mediation_rules = []
        self.peer_assignments = []
        self.software_parameters = []
        
        # Regex patterns for different MML commands
        self.patterns = {
            'medfilter': r'ADD\s+MEDFILTER:\s*(.+)',
            'medaction': r'ADD\s+MEDACTION:\s*(.+)',
            'medrule': r'ADD\s+MEDRULE:\s*(.+)',
            'peer_mod': r'MOD\s+DMPEER:\s*(.+)',
            'sfp_mod': r'MOD\s+SFP:\s*(.+)',
            'comment': r'/\*.*?\*/',
            'parameter_pair': r'(\w+)\s*=\s*([^,;]+)'
        }
    
    def parse_parameters(self, param_string: str) -> Dict[str, str]:
        """Parse parameter string into key-value pairs"""
        params = {}
        # Remove comments and clean up
        clean_string = re.sub(self.patterns['comment'], '', param_string)
        
        # Find all parameter pairs
        matches = re.findall(self.patterns['parameter_pair'], clean_string)
        for key, value in matches:
            # Clean up quotes and whitespace
            clean_value = value.strip().strip('"').strip("'")
            params[key.upper()] = clean_value
        
        return params
    
    def parse_mediation_filter(self, line: str) -> Dict[str, Any]:
        """Parse ADD MEDFILTER command"""
        match = re.search(self.patterns['medfilter'], line, re.IGNORECASE)
        if not match:
            return None
        
        params = self.parse_parameters(match.group(1))
        
        filter_config = {
            'filter_condition_name': params.get('EMEDCONNAME', ''),
            'layer1_avp_code': params.get('AVPAL1', ''),
            'layer1_avp_vendor_id': params.get('AVPAL1VID', ''),
            'layer1_avp_type': params.get('AVPAL1T', ''),
            'condition': params.get('CONDTA', ''),
            'avp_value': params.get('AVPAV', ''),
            'layer2_avp_code': params.get('AVPAL2', ''),
            'layer2_avp_vendor_id': params.get('AVPAL2VID', ''),
            'layer2_avp_type': params.get('AVPAL2T', ''),
            'avp_value2': params.get('AVPAV2', ''),
            'relationship_of_conditions': params.get('RELOFCON', ''),
            'full_mml': line.strip()
        }
        
        return filter_config
    
    def parse_mediation_action(self, line: str) -> Dict[str, Any]:
        """Parse ADD MEDACTION command"""
        match = re.search(self.patterns['medaction'], line, re.IGNORECASE)
        if not match:
            return None
        
        params = self.parse_parameters(match.group(1))
        
        action_config = {
            'mediation_action_name': params.get('OFM', ''),
            'mediation_action': params.get('AFM', ''),
            'layer1_avp_code': params.get('AVPL1', ''),
            'layer1_avp_vendor_id': params.get('AVPL1VID', ''),
            'layer1_avp_type': params.get('AVPL1T', ''),
            'layer2_avp_code': params.get('AVPL2', ''),
            'layer2_avp_vendor_id': params.get('AVPL2VID', ''),
            'layer2_avp_type': params.get('AVPL2T', ''),
            'layer3_avp_code': params.get('AVPL3', ''),
            'layer3_avp_vendor_id': params.get('AVPL3VID', ''),
            'layer3_avp_type': params.get('AVPL3T', ''),
            'location_for_adding_avp': params.get('LOCFORADAVP', ''),
            'subavp_code': params.get('SUBAVPC', ''),
            'subavp_vendor_id': params.get('SUBAVPVID', ''),
            'subavp_type': params.get('SUBAVPT', ''),
            'original_avp_code': params.get('OAVPC', ''),
            'original_avp_vendor_id': params.get('OAVPVID', ''),
            'original_avp_type': params.get('OAVPT', ''),
            'condition': params.get('CONDITION', ''),
            'old_avp_value': params.get('OAVPV', ''),
            'method_to_obtain_new_avp_value': params.get('GETNAVPVMTD', ''),
            'new_avp_value': params.get('NAVPV', ''),
            'new_avp_code_value': params.get('NAVPCV', ''),
            'new_avp_flag_value': params.get('NAVPFV', ''),
            'new_vendor_id_value': params.get('NVIDV', ''),
            'new_command_code_value': params.get('NCCV', ''),
            'new_application_id_value': params.get('NAIDV', ''),
            'new_command_flag_value': params.get('NCFV', ''),
            'original_string': params.get('ORIGS', ''),
            'new_string': params.get('NEWS', ''),
            'restoration_flag': params.get('RESTFLAG', ''),
            'open_related_conditions': params.get('OPRELATECON', ''),
            'related_avp_code': params.get('AVPRELA', ''),
            'related_avp_vendor_id': params.get('AVPVIDRELA', ''),
            'related_avp_type': params.get('AVPTRELA', ''),
            'related_conditions': params.get('RELATECON', ''),
            'related_avp_value': params.get('AVPVRELA', ''),
            'parent_avp_layer': params.get('PAREAVPLEV', ''),
            'filter_condition': params.get('EMEDCON', ''),
            'filter_condition_name': params.get('EMEDCONNAME', ''),
            'full_mml': line.strip()
        }
        
        return action_config
    
    def parse_mediation_rule(self, line: str) -> Dict[str, Any]:
        """Parse ADD MEDRULE command"""
        match = re.search(self.patterns['medrule'], line, re.IGNORECASE)
        if not match:
            return None
        
        params = self.parse_parameters(match.group(1))
        
        # Parse multiple action names (OFM1, OFM2, etc.)
        action_names = []
        for i in range(1, 11):  # Support up to 10 actions
            action_key = f'OFM{i}'
            if action_key in params:
                action_names.append(params[action_key])
        
        rule_config = {
            'mediation_rule_name': params.get('NOMC', ''),
            'mediation_set': params.get('MEDSET', ''),
            'application_id': params.get('AID', ''),
            'original_realm': params.get('ORLM', ''),
            'destination_realm': params.get('DRLM', ''),
            'original_host': params.get('OHOST', ''),
            'destination_host': params.get('DHOST', ''),
            'command_code': params.get('CMDCODE', ''),
            'message_type': params.get('MT', ''),
            'mediation_action_names': action_names,
            'full_mml': line.strip()
        }
        
        return rule_config
    
    def parse_peer_assignment(self, line: str) -> Dict[str, Any]:
        """Parse MOD DMPEER command"""
        match = re.search(self.patterns['peer_mod'], line, re.IGNORECASE)
        if not match:
            return None
        
        params = self.parse_parameters(match.group(1))
        
        peer_config = {
            'peer_name': params.get('DN', ''),
            'protocol_type': params.get('PRTTYPE', ''),
            'receive_message_mediation_set': params.get('MEDSETRM', ''),
            'send_message_mediation_set': params.get('MEDSETSM', ''),
            'full_mml': line.strip()
        }
        
        return peer_config
    
    def parse_software_parameter(self, line: str) -> Dict[str, Any]:
        """Parse MOD SFP command"""
        match = re.search(self.patterns['sfp_mod'], line, re.IGNORECASE)
        if not match:
            return None
        
        params = self.parse_parameters(match.group(1))
        
        sfp_config = {
            'software_parameter_id': params.get('SPID', ''),
            'modification_type': params.get('MODTYPE', ''),
            'value': params.get('VAL', ''),
            'full_mml': line.strip()
        }
        
        return sfp_config
    
    def parse_file(self, filename: str):
        """Parse the AVP mediation configuration file"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Split into lines and process
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('/*') and line.endswith('*/'):
                    continue
                
                # Parse different command types
                if 'ADD MEDFILTER' in line.upper():
                    filter_config = self.parse_mediation_filter(line)
                    if filter_config:
                        self.mediation_filters.append(filter_config)
                
                elif 'ADD MEDACTION' in line.upper():
                    action_config = self.parse_mediation_action(line)
                    if action_config:
                        self.mediation_actions.append(action_config)
                
                elif 'ADD MEDRULE' in line.upper():
                    rule_config = self.parse_mediation_rule(line)
                    if rule_config:
                        self.mediation_rules.append(rule_config)
                
                elif 'MOD DMPEER' in line.upper():
                    peer_config = self.parse_peer_assignment(line)
                    if peer_config:
                        self.peer_assignments.append(peer_config)
                
                elif 'MOD SFP' in line.upper():
                    sfp_config = self.parse_software_parameter(line)
                    if sfp_config:
                        self.software_parameters.append(sfp_config)
        
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return False
        except Exception as e:
            print(f"Error parsing file: {e}")
            return False
        
        return True
    
    def build_mediation_chains(self) -> Dict[str, Any]:
        """Build mediation chains linking rules to actions to filters"""
        chains = {}
        
        for rule in self.mediation_rules:
            mediation_set = rule['mediation_set']
            if mediation_set not in chains:
                chains[mediation_set] = {
                    'mediation_set_name': mediation_set,
                    'rules': [],
                    'total_rules': 0,
                    'total_actions': 0,
                    'total_filters': 0
                }
            
            # Build action chain for this rule
            rule_chain = {
                'rule_info': rule,
                'actions': [],
                'filters_used': []
            }
            
            # Link actions to this rule
            for action_name in rule['mediation_action_names']:
                action_details = None
                for action in self.mediation_actions:
                    if action['mediation_action_name'] == action_name:
                        action_details = action
                        break
                
                if action_details:
                    action_chain = {
                        'action_info': action_details,
                        'filters': []
                    }
                    
                    # Link filters to this action
                    filter_name = action_details.get('filter_condition_name', '')
                    if filter_name:
                        for filter_config in self.mediation_filters:
                            if filter_config['filter_condition_name'] == filter_name:
                                action_chain['filters'].append(filter_config)
                                rule_chain['filters_used'].append(filter_config)
                                break
                    
                    rule_chain['actions'].append(action_chain)
            
            chains[mediation_set]['rules'].append(rule_chain)
            chains[mediation_set]['total_rules'] += 1
            chains[mediation_set]['total_actions'] += len(rule_chain['actions'])
            chains[mediation_set]['total_filters'] += len(rule_chain['filters_used'])
        
        return chains
    
    def generate_config(self) -> Dict[str, Any]:
        """Generate the complete configuration dictionary"""
        mediation_chains = self.build_mediation_chains()
        
        # Get unique mediation sets
        mediation_sets = list(set(rule['mediation_set'] for rule in self.mediation_rules))
        
        # Get unique application IDs
        application_ids = list(set(rule['application_id'] for rule in self.mediation_rules if rule['application_id']))
        
        # Get unique realms
        realms = set()
        for rule in self.mediation_rules:
            if rule['original_realm']:
                realms.add(rule['original_realm'])
            if rule['destination_realm']:
                realms.add(rule['destination_realm'])
        
        # Get unique hosts
        hosts = set()
        for rule in self.mediation_rules:
            if rule['original_host']:
                hosts.add(rule['original_host'])
            if rule['destination_host']:
                hosts.add(rule['destination_host'])
        
        # Get unique command codes
        command_codes = list(set(rule['command_code'] for rule in self.mediation_rules if rule['command_code']))
        
        config = {
            'mediation_filters': self.mediation_filters,
            'mediation_actions': self.mediation_actions,
            'mediation_rules': self.mediation_rules,
            'peer_assignments': self.peer_assignments,
            'software_parameters': self.software_parameters,
            'mediation_chains': mediation_chains,
            'metadata': {
                'parsed_at': datetime.now().isoformat(),
                'total_filters': len(self.mediation_filters),
                'total_actions': len(self.mediation_actions),
                'total_rules': len(self.mediation_rules),
                'total_peer_assignments': len(self.peer_assignments),
                'total_software_parameters': len(self.software_parameters),
                'unique_mediation_sets': mediation_sets,
                'unique_application_ids': application_ids,
                'unique_realms': list(realms),
                'unique_hosts': list(hosts),
                'unique_command_codes': command_codes
            }
        }
        
        return config
    
    def save_config(self, filename: str = 'spsavpmediation_config.json'):
        """Save configuration to JSON file"""
        config = self.generate_config()
        
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(config, file, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def print_summary(self):
        """Print a summary of the parsed configuration"""
        print("Parsing SPS AVP mediation configuration...")
        print("=== SPS AVP Mediation Configuration Summary ===")
        print(f"Total Mediation Filters: {len(self.mediation_filters)}")
        print(f"Total Mediation Actions: {len(self.mediation_actions)}")
        print(f"Total Mediation Rules: {len(self.mediation_rules)}")
        print(f"Total Peer Assignments: {len(self.peer_assignments)}")
        print(f"Total Software Parameters: {len(self.software_parameters)}")
        
        if self.software_parameters:
            print("\n--- Software Parameters ---")
            for sfp in self.software_parameters:
                print(f"📋 SFP: {sfp['software_parameter_id']} = {sfp['value']} (Type: {sfp['modification_type']})")
        
        if self.mediation_filters:
            print("\n--- Mediation Filters ---")
            for filter_config in self.mediation_filters:
                print(f"🔍 Filter: {filter_config['filter_condition_name']}")
                print(f"   AVP: {filter_config['layer1_avp_code']} ({filter_config['layer1_avp_type']})")
                print(f"   Condition: {filter_config['condition']} = {filter_config['avp_value']}")
        
        if self.mediation_actions:
            print("\n--- Mediation Actions ---")
            for action in self.mediation_actions:
                print(f"⚡ Action: {action['mediation_action_name']} ({action['mediation_action']})")
                if action['layer1_avp_code']:
                    print(f"   Target AVP: {action['layer1_avp_code']} ({action['layer1_avp_type']})")
                if action['old_avp_value'] and action['new_avp_value']:
                    print(f"   Value Change: {action['old_avp_value']} → {action['new_avp_value']}")
                if action['filter_condition_name']:
                    print(f"   Filter: {action['filter_condition_name']}")
        
        if self.mediation_rules:
            print("\n--- Mediation Rules ---")
            for rule in self.mediation_rules:
                print(f"📜 Rule: {rule['mediation_rule_name']} (Set: {rule['mediation_set']})")
                if rule['application_id']:
                    print(f"   Application: {rule['application_id']}")
                if rule['command_code']:
                    print(f"   Command Code: {rule['command_code']} ({rule['message_type']})")
                if rule['original_realm'] and rule['destination_realm']:
                    print(f"   Route: {rule['original_realm']} → {rule['destination_realm']}")
                if rule['mediation_action_names']:
                    print(f"   Actions: {', '.join(rule['mediation_action_names'])}")
        
        # Print mediation chains
        chains = self.build_mediation_chains()
        if chains:
            print("\n=== Mediation Chains ===")
            for set_name, chain_info in chains.items():
                print(f"🔗 Mediation Set: {set_name}")
                print(f"   Rules: {chain_info['total_rules']}, Actions: {chain_info['total_actions']}, Filters: {chain_info['total_filters']}")
                
                for rule_chain in chain_info['rules']:
                    rule = rule_chain['rule_info']
                    print(f"   ├── 📜 {rule['mediation_rule_name']} ({rule['application_id']} - CMD:{rule['command_code']})")
                    
                    for action_chain in rule_chain['actions']:
                        action = action_chain['action_info']
                        print(f"   │   ├── ⚡ {action['mediation_action_name']} ({action['mediation_action']})")
                        
                        for filter_config in action_chain['filters']:
                            print(f"   │   │   └── 🔍 {filter_config['filter_condition_name']} ({filter_config['condition']})")
        
        if self.peer_assignments:
            print("\n--- Peer Assignments ---")
            for peer in self.peer_assignments:
                print(f"🌐 Peer: {peer['peer_name']} ({peer['protocol_type']})")
                if peer['receive_message_mediation_set']:
                    print(f"   RX Mediation Set: {peer['receive_message_mediation_set']}")
                if peer['send_message_mediation_set']:
                    print(f"   TX Mediation Set: {peer['send_message_mediation_set']}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python spsavpmediation.py <mediation_config_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    parser = SPSAVPMediationParser()
    
    if parser.parse_file(filename):
        parser.print_summary()
        
        # Save configuration
        if parser.save_config():
            print(f"\nConfiguration saved to 'spsavpmediation_config.json'")
            print("✅ Configuration successfully parsed and saved to 'spsavpmediation_config.json'")
        else:
            print("❌ Failed to save configuration")
    else:
        print("❌ Failed to parse configuration file")
        sys.exit(1)


if __name__ == "__main__":
    main()
