#!/usr/bin/env python3
"""
Simplified Topology Generator v2 - Interactive D3.js Visualization
Generates a star-shaped network topology with interactive D3.js visualization.
Input: Original MML text files (spsdmlinks.txt, spsstp.txt, or merged)
Output: Single HTML file with embedded D3.js interactive visualization
"""

import json
import sys
import re
import math
from datetime import datetime
from typing import Dict, List, Any, Optional


class SimplifiedTopoGeneratorV2:
    """Generate simplified star-shaped topology with interactive D3.js visualization"""
    
    def __init__(self):
        self.local_entity_id = "SPS_LOCAL"
        self.node_counter = 0
        self.nodes = []
        self.links = []
        
        # Simplified color scheme by protocol type only
        self.protocol_colors = {
            'SPS_CORE': '#2C3E50',      # Dark blue-gray for core
            'DIAMETER': '#E74C3C',      # Red for Diameter
            'MTP': '#3498DB',           # Blue for MTP  
            'M3UA': '#27AE60',          # Green for M3UA
            'M2UA': '#F39C12',          # Orange for M2UA
            'SCCP': '#9B59B6'           # Purple for SCCP
        }
        
        # Visual properties for different node types
        self.node_config = {
            'SPS_CORE': {'color': self.protocol_colors['SPS_CORE'], 'size': 40, 'shape': 'star'},
            'DIAMETER_PEER': {'color': self.protocol_colors['DIAMETER'], 'size': 25, 'shape': 'circle'},
            'DIAMETER_LINKSET': {'color': self.protocol_colors['DIAMETER'], 'size': 18, 'shape': 'rect'},
            'DIAMETER_LINK': {'color': self.protocol_colors['DIAMETER'], 'size': 12, 'shape': 'triangle'},
            'MTP_DSP': {'color': self.protocol_colors['MTP'], 'size': 25, 'shape': 'hexagon'},
            'MTP_LINKSET': {'color': self.protocol_colors['MTP'], 'size': 18, 'shape': 'rect'},
            'MTP_LINK': {'color': self.protocol_colors['MTP'], 'size': 12, 'shape': 'triangle'},
            'M3UA_AS': {'color': self.protocol_colors['M3UA'], 'size': 25, 'shape': 'diamond'},
            'M3UA_LINKSET': {'color': self.protocol_colors['M3UA'], 'size': 18, 'shape': 'rect'},
            'M3UA_LINK': {'color': self.protocol_colors['M3UA'], 'size': 12, 'shape': 'triangle'},
            'M2UA_SG': {'color': self.protocol_colors['M2UA'], 'size': 25, 'shape': 'diamond'},
            'M2UA_LINKSET': {'color': self.protocol_colors['M2UA'], 'size': 18, 'shape': 'rect'},
            'M2UA_LINK': {'color': self.protocol_colors['M2UA'], 'size': 12, 'shape': 'triangle'},
            'SCCP_DSP': {'color': self.protocol_colors['SCCP'], 'size': 25, 'shape': 'hexagon'},
            'SCCP_SSN': {'color': self.protocol_colors['SCCP'], 'size': 18, 'shape': 'rect'},
            'SCCP_GT': {'color': self.protocol_colors['SCCP'], 'size': 15, 'shape': 'triangle'}
        }
        
        # MML parsing patterns
        self.patterns = {
            'dmpeer': r'ADD\s+DMPEER:\s*(.+)',
            'dmlks': r'ADD\s+DMLKS:\s*(.+)',
            'dmlnk': r'ADD\s+DMLNK:\s*(.+)',
            'n7dsp': r'ADD\s+N7DSP:\s*(.+)',
            'n7lks': r'ADD\s+N7LKS:\s*(.+)',
            'n7lnk': r'ADD\s+N7LNK:\s*(.+)',
            'm3as': r'ADD\s+M3AS:\s*(.+)',
            'm3lks': r'ADD\s+M3LKS:\s*(.+)',
            'm3lnk': r'ADD\s+M3LNK:\s*(.+)',
            'm2sg': r'ADD\s+SG:\s*(.+)',
            'm2lks': r'ADD\s+M2LKS:\s*(.+)',
            'm2lnk': r'ADD\s+M2LNK:\s*(.+)',
            'sccpdsp': r'ADD\s+SCCPDSP:\s*(.+)',
            'sccpssn': r'ADD\s+SCCPSSN:\s*(.+)',
            'sccpgt': r'ADD\s+SCCPGT:\s*(.+)',
            'parameter_pair': r'(\w+)\s*=\s*([^,;]+)'
        }
    
    def generate_node_id(self) -> str:
        """Generate unique node ID"""
        self.node_counter += 1
        return f"node_{self.node_counter:04d}"
    
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
    
    def get_ssn_type_description(self, ssn: str) -> str:
        """Get SSN type description based on SSN number"""
        ssn_types = {
            '1': 'SCCP Management',
            '2': 'Reserved',
            '3': 'ISUP',
            '4': 'OMAP',
            '5': 'MAP',
            '6': 'HLR',
            '7': 'VLR',
            '8': 'MSC',
            '9': 'EIR',
            '10': 'AuC',
            '142': 'RANAP',
            '143': 'RNSAP',
            '145': 'GMLC',
            '146': 'CAP',
            '147': 'gsmSCF',
            '148': 'SMLC',
            '149': 'BSC',
            '150': 'MSC Server',
            '151': 'MME',
            '152': 'SGSN',
            '153': 'GGSN/PGW',
            '154': 'HSS'
        }
        return ssn_types.get(ssn, f'Custom SSN {ssn}')
    
    def get_gt_type_description(self, gt_type: str) -> str:
        """Get GT type description based on GTI value"""
        gt_types = {
            '0': 'No GT',
            '1': 'NOA only',
            '2': 'TT only', 
            '3': 'TT + NOA + NP',
            '4': 'TT + NOA + NP + ES'
        }
        return gt_types.get(gt_type, f'Unknown GTI {gt_type}')
    
    def get_translation_type_description(self, tt: str) -> str:
        """Get translation type description"""
        tt_types = {
            '0': 'Unknown/Not Used',
            '1': 'International Number',
            '2': 'National Number', 
            '3': 'Network Specific',
            '4': 'Subscriber Number',
            '5': 'Reserved',
            '6': 'Abbreviated Number',
            '7': 'Reserved for Extension'
        }
        return tt_types.get(tt, f'Custom TT {tt}')
    
    def add_central_node(self):
        """Add the central SPS node"""
        config = self.node_config['SPS_CORE']
        node = {
            'id': self.local_entity_id,
            'name': 'SPS_LOCAL',
            'type': 'SPS_CORE',
            'layer': 0,
            'x': 0,  # Center at origin - D3.js will handle viewport centering
            'y': 0,
            'fx': 0,  # Fixed position at center
            'fy': 0,
            'color': config['color'],
            'size': config['size'],
            'shape': config['shape'],
            'description': 'Local SPS Entity',
            'protocols': [],
            'details': {
                'Total Connections': 0,
                'Entity Type': 'SPS Core System',
                'Location': 'Local Entity'
            }
        }
        self.nodes.append(node)
        return node
    
    def add_node(self, node_id: str, name: str, node_type: str, layer: int, 
                 parent_id: str = None, **properties) -> Dict[str, Any]:
        """Add a node to the topology"""
        config = self.node_config.get(node_type, self.node_config['DIAMETER_PEER'])
        
        # Calculate position based on layer and existing nodes in that layer
        layer_nodes = [n for n in self.nodes if n.get('layer') == layer]
        nodes_in_layer = len(layer_nodes)
        
        # Distribute nodes evenly around a circle for each layer
        angle = (nodes_in_layer * 2 * math.pi) / max(8, nodes_in_layer + 4)  # At least 8 positions per layer
        radius = 100 + (layer * 80)  # Increase radius for each layer outward
        
        # Center around (0, 0) initially - D3.js will handle centering
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        
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
            'parent': parent_id,
            'x': x,
            'y': y,
            'color': config['color'],
            'size': config['size'],
            'shape': config['shape'],
            'details': details,
            **properties
        }
        
        self.nodes.append(node)
        return node
    
    def add_link(self, source_id: str, target_id: str, link_type: str, protocol: str, **properties):
        """Add a link between nodes"""
        link = {
            'source': source_id,
            'target': target_id,
            'type': link_type,
            'protocol': protocol,
            **properties
        }
        self.links.append(link)
        return link
    
    def parse_mml_file(self, filename: str):
        """Parse MML file and build topology"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
            
            lines = content.split('\n')
            
            # Track relationships
            peers = {}
            linksets = {}
            dsps = {}
            ases = {}
            sgs = {}  # Signal Gateways for M2UA
            
            # Parse all commands
            for line in lines:
                line = line.strip()
                if not line or line.startswith('/*'):
                    continue
                
                # Parse diameter peers
                if 'ADD DMPEER' in line.upper():
                    params = self.parse_parameters(line)
                    peer_name = params.get('DN', '')
                    if peer_name:
                        peer_id = self.generate_node_id()
                        peers[peer_name] = peer_id
                        
                        self.add_node(
                            peer_id, peer_name, 'DIAMETER_PEER', 1,
                            hostname=params.get('HN', ''),
                            realm=params.get('RN', ''),
                            interface=params.get('DEVTP', ''),
                            protocol_type=params.get('PRTTYPE', ''),
                            host_ip=params.get('HIP41', ''),
                            port=params.get('PPORT', '')
                        )
                        
                        self.add_link(self.local_entity_id, peer_id, 'PEER_CONNECTION', 'DIAMETER')
                
                # Parse diameter linksets
                elif 'ADD DMLKS' in line.upper():
                    params = self.parse_parameters(line)
                    linkset_name = params.get('LKSNAME', '')
                    peer_name = params.get('DN', '')
                    if linkset_name and peer_name in peers:
                        linkset_id = self.generate_node_id()
                        linksets[linkset_name] = linkset_id
                        
                        self.add_node(
                            linkset_id, linkset_name, 'DIAMETER_LINKSET', 2, peers[peer_name],
                            peer_name=peer_name,
                            da_name=params.get('DANAME', ''),
                            load_sharing_mode=params.get('LKSM', '')
                        )
                        
                        self.add_link(peers[peer_name], linkset_id, 'LINKSET_CONNECTION', 'DIAMETER')
                
                # Parse diameter links
                elif 'ADD DMLNK' in line.upper():
                    params = self.parse_parameters(line)
                    link_name = params.get('LNKNAME', '')
                    linkset_name = params.get('LKSNAME', '')
                    if link_name and linkset_name in linksets:
                        link_id = self.generate_node_id()
                        
                        local_port = params.get('LPORT', '')
                        peer_ip = params.get('PIP41', '')
                        peer_port = params.get('PPORT', '')
                        
                        # Create connection info for label
                        connection = f"Local:{local_port} ⟷ {peer_ip}:{peer_port}"
                        display_name = f"{link_name}\n{connection}"
                        
                        self.add_node(
                            link_id, display_name, 'DIAMETER_LINK', 3, linksets[linkset_name],
                            mid=params.get('MID', ''),
                            protocol_type=params.get('PTYPE', ''),
                            working_mode=params.get('WMODE', ''),
                            peer_ip=peer_ip,
                            peer_port=peer_port,
                            local_port=local_port,
                            connection=connection
                        )
                        
                        self.add_link(linksets[linkset_name], link_id, 'LINK_CONNECTION', 'DIAMETER',
                                    connection_info=connection,
                                    peer_ip=peer_ip,
                                    peer_port=peer_port,
                                    local_port=local_port)
                
                # Parse MTP DSPs
                elif 'ADD N7DSP' in line.upper():
                    params = self.parse_parameters(line)
                    dsp_name = params.get('STDNAME', '')
                    if dsp_name:
                        dsp_id = self.generate_node_id()
                        dsps[dsp_name] = dsp_id
                        
                        self.add_node(
                            dsp_id, dsp_name, 'MTP_DSP', 1,
                            point_code=params.get('NPC', ''),
                            network=params.get('LNN', ''),
                            sua_point=params.get('SUAPOINT', '')
                        )
                        
                        self.add_link(self.local_entity_id, dsp_id, 'ENTITY_CONNECTION', 'MTP')
                
                # Parse MTP linksets
                elif 'ADD N7LKS' in line.upper():
                    params = self.parse_parameters(line)
                    linkset_name = params.get('LKSNM', '')
                    dsp_name = params.get('ASPNM', '')
                    if linkset_name and dsp_name in dsps:
                        linkset_id = self.generate_node_id()
                        linksets[linkset_name] = linkset_id
                        
                        self.add_node(
                            linkset_id, linkset_name, 'MTP_LINKSET', 2, dsps[dsp_name],
                            entity_name=dsp_name,
                            network_indicator=params.get('NI', ''),
                            office_name=params.get('OFNM', '')
                        )
                        
                        self.add_link(dsps[dsp_name], linkset_id, 'LINKSET_CONNECTION', 'MTP')
                
                # Parse MTP links
                elif 'ADD N7LNK' in line.upper():
                    params = self.parse_parameters(line)
                    link_name = params.get('LNKNM', '')
                    linkset_name = params.get('LKSNM', '')
                    if link_name and linkset_name in linksets:
                        link_id = self.generate_node_id()
                        
                        local_port = params.get('LP', '')
                        remote_ip = params.get('RIP41', '')
                        remote_port = params.get('RP', '')
                        
                        # Create connection info for label
                        connection = f"Local:{local_port} ⟷ {remote_ip}:{remote_port}"
                        display_name = f"{link_name}\n{connection}"
                        
                        self.add_node(
                            link_id, display_name, 'MTP_LINK', 3, linksets[linkset_name],
                            connection_type=params.get('CT', ''),
                            remote_ip=remote_ip,
                            remote_port=remote_port,
                            local_port=local_port,
                            connection=connection,
                            signaling_link_code=params.get('SLC', '')
                        )
                        
                        self.add_link(linksets[linkset_name], link_id, 'LINK_CONNECTION', 'MTP',
                                    connection_info=connection,
                                    remote_ip=remote_ip,
                                    remote_port=remote_port,
                                    local_port=local_port)
                
                # Parse M3UA ASs
                elif 'ADD M3AS' in line.upper():
                    params = self.parse_parameters(line)
                    as_name = params.get('ASNM', '')
                    dsp_name = params.get('DPCT', '')  # M3AS links to DSP via DPCT
                    if as_name and dsp_name in dsps:
                        as_id = self.generate_node_id()
                        ases[as_name] = as_id
                        
                        self.add_node(
                            as_id, as_name, 'M3UA_AS', 2, dsps[dsp_name],  # Connect to DSP, not central
                            point_code=dsp_name,
                            network=params.get('NI', ''),
                            dsp_reference=dsp_name
                        )
                        
                        self.add_link(dsps[dsp_name], as_id, 'AS_CONNECTION', 'M3UA')  # Link DSP to AS
                
                # Parse M3UA linksets
                elif 'ADD M3LKS' in line.upper():
                    params = self.parse_parameters(line)
                    linkset_name = params.get('LKSNM', '')
                    as_name = params.get('ASNM', '')
                    if linkset_name and as_name in ases:
                        linkset_id = self.generate_node_id()
                        linksets[linkset_name] = linkset_id
                        
                        self.add_node(
                            linkset_id, linkset_name, 'M3UA_LINKSET', 3, ases[as_name],  # Layer 3
                            entity_name=as_name,
                            network_indicator=params.get('NI', ''),
                            office_name=params.get('OFNM', '')
                        )
                        
                        self.add_link(ases[as_name], linkset_id, 'LINKSET_CONNECTION', 'M3UA')
                
                # Parse M3UA links
                elif 'ADD M3LNK' in line.upper():
                    params = self.parse_parameters(line)
                    link_name = params.get('LNKNM', '')
                    linkset_name = params.get('LKSNM', '')
                    if link_name and linkset_name in linksets:
                        link_id = self.generate_node_id()
                        
                        local_port = params.get('LP', '')
                        remote_ip = params.get('RIP41', '')
                        remote_port = params.get('RP', '')
                        
                        # Create connection info for label
                        connection = f"Local:{local_port} ⟷ {remote_ip}:{remote_port}"
                        display_name = f"{link_name}\n{connection}"
                        
                        self.add_node(
                            link_id, display_name, 'M3UA_LINK', 4, linksets[linkset_name],  # Layer 4
                            remote_ip=remote_ip,
                            remote_port=remote_port,
                            local_port=local_port,
                            connection=connection,
                            media_id=params.get('MID', '')
                        )
                        
                        self.add_link(linksets[linkset_name], link_id, 'LINK_CONNECTION', 'M3UA',
                                    connection_info=connection,
                                    remote_ip=remote_ip,
                                    remote_port=remote_port,
                                    local_port=local_port)
                
                # Parse M2UA Signal Gateways
                elif 'ADD SG' in line.upper():
                    params = self.parse_parameters(line)
                    sg_name = params.get('SGNM', '')
                    if sg_name:
                        sg_id = self.generate_node_id()
                        sgs[sg_name] = sg_id
                        
                        self.add_node(
                            sg_id, sg_name, 'M2UA_SG', 1,
                            sg_name=sg_name,
                            description='M2UA Signal Gateway'
                        )
                        
                        self.add_link(self.local_entity_id, sg_id, 'SG_CONNECTION', 'M2UA')
                
                # Parse M2UA linksets
                elif 'ADD M2LKS' in line.upper():
                    params = self.parse_parameters(line)
                    linkset_name = params.get('LSNM', '')
                    sg_name = params.get('SGNM', '')
                    if linkset_name and sg_name in sgs:
                        linkset_id = self.generate_node_id()
                        linksets[linkset_name] = linkset_id
                        
                        self.add_node(
                            linkset_id, linkset_name, 'M2UA_LINKSET', 2, sgs[sg_name],
                            sg_name=sg_name,
                            max_number=params.get('MN', ''),
                            description='M2UA Link Set'
                        )
                        
                        self.add_link(sgs[sg_name], linkset_id, 'LINKSET_CONNECTION', 'M2UA')
                
                # Parse M2UA links
                elif 'ADD M2LNK' in line.upper():
                    params = self.parse_parameters(line)
                    link_name = params.get('LNKNM', '')
                    linkset_name = params.get('LSNM', '')
                    if link_name and linkset_name in linksets:
                        link_id = self.generate_node_id()
                        
                        local_ip = params.get('LOCIP1', '')
                        local_port = params.get('LOCPORT', '')
                        peer_ip = params.get('PIP41', '')
                        peer_port = params.get('PPORT', '')
                        
                        # Create connection info for label
                        connection = f"{local_ip}:{local_port} ⟷ {peer_ip}:{peer_port}"
                        display_name = f"{link_name}\n{connection}"
                        
                        self.add_node(
                            link_id, display_name, 'M2UA_LINK', 3, linksets[linkset_name],
                            ip_transport_protocol=params.get('IPTP', ''),
                            local_ip=local_ip,
                            local_port=local_port,
                            peer_ip=peer_ip,
                            peer_port=peer_port,
                            active_standby=params.get('ACTSTDBY', ''),
                            sctp_param_name=params.get('SCTPPARANAME', ''),
                            connection=connection
                        )
                        
                        self.add_link(linksets[linkset_name], link_id, 'LINK_CONNECTION', 'M2UA',
                                    connection_info=connection,
                                    peer_ip=peer_ip,
                                    peer_port=peer_port,
                                    local_ip=local_ip,
                                    local_port=local_port)
                
                # Parse SCCP DSPs
                elif 'ADD SCCPDSP' in line.upper():
                    params = self.parse_parameters(line)
                    sccp_dsp_name = params.get('DSPNM', '')
                    mtp_dsp_name = params.get('MTPASPNM', '')  # Links to MTP DSP
                    if sccp_dsp_name and mtp_dsp_name in dsps:
                        sccp_dsp_id = self.generate_node_id()
                        
                        self.add_node(
                            sccp_dsp_id, sccp_dsp_name, 'SCCP_DSP', 2, dsps[mtp_dsp_name],
                            mtp_entity=mtp_dsp_name,
                            point_code=params.get('NPC', ''),
                            network=params.get('LNN', ''),
                            sccp_version=params.get('SCCPVER', ''),
                            gtindicator=params.get('GTINDICATOR', '')
                        )
                        
                        # Store SCCP DSP for linking SSN and GT
                        if 'sccp_dsps' not in locals():
                            sccp_dsps = {}
                        sccp_dsps[sccp_dsp_name] = sccp_dsp_id
                        
                        self.add_link(dsps[mtp_dsp_name], sccp_dsp_id, 'SCCP_CONNECTION', 'SCCP')
                
                # Parse SCCP SSNs
                elif 'ADD SCCPSSN' in line.upper():
                    params = self.parse_parameters(line)
                    ssn_name = params.get('SSNNM', '')
                    sccp_dsp_name = params.get('DSPNM', '')
                    ssn_number = params.get('SSN', '')
                    
                    if ssn_name and sccp_dsp_name in locals() and sccp_dsp_name in sccp_dsps:
                        ssn_id = self.generate_node_id()
                        
                        # Get SSN type description
                        ssn_type = self.get_ssn_type_description(ssn_number)
                        display_name = f"{ssn_name}\nSSN:{ssn_number} ({ssn_type})"
                        
                        self.add_node(
                            ssn_id, display_name, 'SCCP_SSN', 3, sccp_dsps[sccp_dsp_name],
                            ssn_number=ssn_number,
                            ssn_type=ssn_type,
                            sccp_entity=sccp_dsp_name,
                            primary_backup=params.get('PRIBUTYPE', ''),
                            default_gtt=params.get('DEFGTT', '')
                        )
                        
                        self.add_link(sccp_dsps[sccp_dsp_name], ssn_id, 'SSN_CONNECTION', 'SCCP')
                
                # Parse SCCP Global Titles
                elif 'ADD SCCPGT' in line.upper():
                    params = self.parse_parameters(line)
                    gt_name = params.get('GTNM', '')
                    sccp_dsp_name = params.get('DSPNM', '')
                    gt_digits = params.get('GTD', '')
                    translation_type = params.get('TT', '')
                    gt_type = params.get('GTI', '')
                    
                    if gt_name and sccp_dsp_name in locals() and sccp_dsp_name in sccp_dsps:
                        gt_id = self.generate_node_id()
                        
                        # Get GT type and translation description
                        gt_type_desc = self.get_gt_type_description(gt_type)
                        tt_desc = self.get_translation_type_description(translation_type)
                        display_name = f"{gt_name}\nGT:{gt_digits}\nType:{gt_type_desc}\nTT:{tt_desc}"
                        
                        self.add_node(
                            gt_id, display_name, 'SCCP_GT', 4, sccp_dsps[sccp_dsp_name],
                            gt_digits=gt_digits,
                            gt_type=gt_type,
                            gt_type_description=gt_type_desc,
                            translation_type=translation_type,
                            translation_description=tt_desc,
                            sccp_entity=sccp_dsp_name,
                            result_type=params.get('RESULTTYPE', ''),
                            nature_of_address=params.get('NOA', ''),
                            numbering_plan=params.get('NP', ''),
                            af_number=params.get('AFN', '')
                        )
                        
                        self.add_link(sccp_dsps[sccp_dsp_name], gt_id, 'GT_CONNECTION', 'SCCP')
            
            # Update central node with protocols used
            central_node = next(n for n in self.nodes if n['id'] == self.local_entity_id)
            protocols = set()
            for link in self.links:
                if link['source'] == self.local_entity_id:
                    protocols.add(link['protocol'])
            central_node['protocols'] = list(protocols)
            central_node['details']['Total Connections'] = len([l for l in self.links if l['source'] == self.local_entity_id])
            central_node['details']['Protocols'] = ', '.join(protocols)
            
            return True
            
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return False
        except Exception as e:
            print(f"Error parsing file: {e}")
            return False
    
    def generate_html_with_data(self, config: dict, output_filename: str = 'sps_topology_interactive.html') -> dict:
        """Generate topology from parsed configuration data and return result"""
        try:
            # Reset internal state
            self.nodes = []
            self.links = []
            self.node_counter = 0
            
            # Add central SPS node
            self.add_central_node()
            
            # Process diameter peers
            peer_map = {}
            for peer in config.get('diameter_peers', []):
                peer_name = peer.get('name', '')
                if peer_name:
                    peer_id = self.generate_node_id()
                    peer_map[peer_name] = peer_id
                    
                    self.add_node(
                        peer_id, peer_name, 'DIAMETER_PEER', 1,
                        hostname=peer.get('hn', ''),
                        realm=peer.get('realm', ''),
                        interface=peer.get('interface', ''),
                        protocol_type=peer.get('type', ''),
                        binding_flag=peer.get('binding_flag', '')
                    )
                    
                    self.add_link(self.local_entity_id, peer_id, 'PEER_CONNECTION', 'DIAMETER')
            
            # Process diameter linksets
            linkset_map = {}
            for linkset in config.get('diameter_link_sets', []):
                linkset_name = linkset.get('name', '')
                peer_name = linkset.get('destination_name', '')
                if linkset_name and peer_name in peer_map:
                    linkset_id = self.generate_node_id()
                    linkset_map[linkset_name] = linkset_id
                    
                    self.add_node(
                        linkset_id, linkset_name, 'DIAMETER_LINKSET', 2, peer_map[peer_name],
                        peer_name=peer_name,
                        da_name=linkset.get('da_name', ''),
                        load_sharing_mode=linkset.get('load_sharing_mode', '')
                    )
                    
                    self.add_link(peer_map[peer_name], linkset_id, 'LINKSET_CONNECTION', 'DIAMETER')
            
            # Process diameter links
            for link in config.get('diameter_links', []):
                link_name = link.get('name', '')
                linkset_name = link.get('link_set_name', '')
                if link_name and linkset_name in linkset_map:
                    link_id = self.generate_node_id()
                    
                    local_port = str(link.get('local_port', ''))
                    peer_ip = link.get('peer_ip', '')
                    peer_port = str(link.get('peer_port', ''))
                    
                    connection = f"Local:{local_port} ⟷ {peer_ip}:{peer_port}"
                    display_name = f"{link_name}\n{connection}"
                    
                    self.add_node(
                        link_id, display_name, 'DIAMETER_LINK', 3, linkset_map[linkset_name],
                        peer_ip=peer_ip,
                        peer_port=peer_port,
                        local_port=local_port,
                        connection=connection,
                        media_id=str(link.get('mid', '')),
                        protocol_type=link.get('protocol_type', ''),
                        working_mode=link.get('working_mode', '')
                    )
                    
                    self.add_link(linkset_map[linkset_name], link_id, 'LINK_CONNECTION', 'DIAMETER',
                                connection_info=connection,
                                peer_ip=peer_ip,
                                peer_port=peer_port,
                                local_port=local_port)
            
            # Process MTP destination points
            dsp_map = {}
            for dsp in config.get('mtp_destination_points', []):
                dsp_name = dsp.get('standard_name', '')
                if dsp_name:
                    dsp_id = self.generate_node_id()
                    dsp_map[dsp_name] = dsp_id
                    
                    self.add_node(
                        dsp_id, dsp_name, 'MTP_DSP', 1,
                        point_code=dsp.get('node_point_code', ''),
                        network=dsp.get('logical_network_name', ''),
                        sua_point=dsp.get('sua_point', '')
                    )
                    
                    self.add_link(self.local_entity_id, dsp_id, 'ENTITY_CONNECTION', 'MTP')
            
            # Process M3UA Application Servers (flat list)
            as_map = {}
            for as_data in config.get('m3ua_application_servers', []):
                if isinstance(as_data, dict):
                    as_name = as_data.get('application_server_name', '')
                    if as_name:
                        as_id = self.generate_node_id()
                        as_map[as_name] = as_id
                        
                        self.add_node(
                            as_id, as_name, 'M3UA_AS', 1,
                            network_indicator=as_data.get('network_indicator', ''),
                            destination_point_code_table=as_data.get('destination_point_code_table', '')
                        )
                        
                        self.add_link(self.local_entity_id, as_id, 'AS_CONNECTION', 'M3UA')
            
            # Process M3UA Link Sets
            for linkset in config.get('m3ua_link_sets', []):
                ls_name = linkset.get('name', '')
                as_name = linkset.get('application_server_name', '')
                if ls_name and as_name in as_map:
                    ls_id = self.generate_node_id()
                    linkset_map[ls_name] = ls_id
                    
                    self.add_node(
                        ls_id, ls_name, 'M3UA_LINKSET', 2, as_map[as_name],
                        application_server_name=as_name,
                        timer_name=linkset.get('timer_name', ''),
                        screening=linkset.get('screening', '')
                    )
                    
                    self.add_link(as_map[as_name], ls_id, 'LINKSET_CONNECTION', 'M3UA')
            
            # Process M3UA Links
            for link in config.get('m3ua_links', []):
                link_name = link.get('name', '')
                linkset_name = link.get('link_set_name', '')
                if link_name and linkset_name in linkset_map:
                    link_id = self.generate_node_id()
                    
                    local_port = str(link.get('local_port', ''))
                    peer_ip = link.get('remote_ip', '')
                    peer_port = str(link.get('remote_port', ''))
                    
                    connection = f"Local:{local_port} ⟷ {peer_ip}:{peer_port}"
                    display_name = f"{link_name}\n{connection}"
                    
                    self.add_node(
                        link_id, display_name, 'M3UA_LINK', 3, linkset_map[linkset_name],
                        peer_ip=peer_ip,
                        peer_port=peer_port,
                        local_port=local_port,
                        connection=connection,
                        media_id=str(link.get('media_id', '')),
                        connection_state=link.get('connection_state', '')
                    )
                    
                    self.add_link(linkset_map[linkset_name], link_id, 'LINK_CONNECTION', 'M3UA',
                                connection_info=connection,
                                peer_ip=peer_ip,
                                peer_port=peer_port,
                                local_port=local_port)
            
            # Process SCCP subsystems (limited to avoid clutter)
            if config.get('sccp_subsystems'):
                sccp_layer_id = self.generate_node_id()
                self.add_node(
                    sccp_layer_id, 'SCCP Layer', 'SCCP_DSP', 1,
                    layer_type='SCCP Protocol Layer'
                )
                self.add_link(self.local_entity_id, sccp_layer_id, 'PROTOCOL_CONNECTION', 'SCCP')
                
                # Add a sample of subsystems (to avoid clutter)
                for i, ssn in enumerate(config.get('sccp_subsystems', [])[:5]):  # Limit to first 5
                    if isinstance(ssn, dict):
                        ssn_name = ssn.get('subsystem_name', f'SSN_{i+1}')
                        ssn_id = self.generate_node_id()
                        
                        self.add_node(
                            ssn_id, ssn_name, 'SCCP_SSN', 2, sccp_layer_id,
                            subsystem_number=ssn.get('subsystem_number', ''),
                            network_indicator=ssn.get('network_indicator', ''),
                            destination_name=ssn.get('destination_name', '')
                        )
                        
                        self.add_link(sccp_layer_id, ssn_id, 'SSN_CONNECTION', 'SCCP')
            
            # Update central node connection count
            central_node = next((node for node in self.nodes if node['id'] == self.local_entity_id), None)
            if central_node:
                central_node['details']['Total Connections'] = len([link for link in self.links if link['source'] == self.local_entity_id])
            
            # Generate the HTML visualization
            self.generate_d3_html(output_filename)
            
            # Return structured result for CLI
            return {
                'output_file': output_filename,
                'total_nodes': len(self.nodes),
                'total_links': len(self.links),
                'protocols': list({link['protocol'] for link in self.links}),
                'metadata': config.get('metadata', {})
            }
            
        except Exception as e:
            return {'error': f"Error generating topology: {e}"}
    
    def generate_d3_html(self, output_filename: str = 'sps_topology_interactive.html'):
        """Generate interactive D3.js HTML visualization"""
        
        # Calculate statistics and metadata
        stats = {
            'total_nodes': len(self.nodes),
            'total_links': len(self.links),
            'protocols': list(set(link['protocol'] for link in self.links)),
            'node_types': {},
            'layer_distribution': {},
            'metadata': {
                'all_ips': set(),
                'all_ports': set(),
                'ip_port_pairs': set(),
                'connections': []
            }
        }
        
        for node in self.nodes:
            node_type = node['type']
            layer = node['layer']
            stats['node_types'][node_type] = stats['node_types'].get(node_type, 0) + 1
            stats['layer_distribution'][f"layer_{layer}"] = stats['layer_distribution'].get(f"layer_{layer}", 0) + 1
            
            # Extract IP and port information
            for key, value in node.items():
                if 'ip' in key.lower() and value and value != '':
                    stats['metadata']['all_ips'].add(value)
                elif 'port' in key.lower() and value and value != '':
                    stats['metadata']['all_ports'].add(value)
                elif key == 'connection' and value:
                    stats['metadata']['connections'].append(value)
                    # Extract IP:Port pairs from connection strings
                    import re
                    ip_port_matches = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', value)
                    for match in ip_port_matches:
                        stats['metadata']['ip_port_pairs'].add(match)
        
        # Convert sets to sorted lists for JSON serialization
        stats['metadata']['all_ips'] = sorted(list(stats['metadata']['all_ips']))
        stats['metadata']['all_ports'] = sorted(list(stats['metadata']['all_ports']))
        stats['metadata']['ip_port_pairs'] = sorted(list(stats['metadata']['ip_port_pairs']))
        
        html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SPS Network Topology - Interactive Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            overflow: hidden;
        }}
        
        .container {{
            display: flex;
            flex-direction: column;
            height: 100vh;
        }}
        
        .header {{
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        h1 {{
            margin: 0;
            font-size: 1.8em;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .controls {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 8px 0;
            flex-wrap: wrap;
        }}
        
        .control-group {{
            background: rgba(255, 255, 255, 0.1);
            padding: 5px 10px;
            border-radius: 15px;
            backdrop-filter: blur(5px);
            font-size: 0.9em;
        }}
        
        .search-group {{
            background: rgba(255, 255, 255, 0.15);
            padding: 8px 12px;
            border-radius: 15px;
            backdrop-filter: blur(5px);
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .search-input {{
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 4px 8px;
            border-radius: 10px;
            font-size: 0.9em;
            min-width: 150px;
        }}
        
        .search-input::placeholder {{
            color: rgba(255, 255, 255, 0.7);
        }}
        
        .checkbox-wrapper {{
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 0.8em;
        }}
        
        input[type="checkbox"] {{
            accent-color: #4ECDC4;
        }}
        
        .filter-status {{
            background: rgba(74, 144, 226, 0.3);
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 0.75em;
            margin-left: 8px;
        }}
        
        button {{
            background: linear-gradient(45deg, #ff6b6b, #ff8e8e);
            border: none;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            cursor: pointer;
            margin: 0 3px;
            font-weight: bold;
            transition: all 0.3s ease;
            font-size: 0.85em;
        }}
        
        button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 3px 10px rgba(0,0,0,0.3);
        }}
        
        button.active {{
            background: linear-gradient(45deg, #4ECDC4, #44A08D);
        }}
        
        .layout-btn {{
            width: 35px;
            height: 35px;
            border-radius: 50%;
            background: linear-gradient(45deg, #667eea, #764ba2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }}
        
        .layout-btn:hover {{
            background: linear-gradient(45deg, #5a67d8, #6b46c1);
            transform: scale(1.1);
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 5px 0;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.15);
            padding: 8px 12px;
            border-radius: 8px;
            text-align: center;
            backdrop-filter: blur(5px);
            font-size: 0.8em;
        }}
        
        .stat-number {{
            font-size: 1.4em;
            font-weight: bold;
            color: #4ECDC4;
        }}
        
        @keyframes ledBreathing {{
            0% {{ 
                stroke: #FF0080;
                stroke-width: 2px;
                filter: drop-shadow(0 0 3px #FF0080);
            }}
            14% {{ 
                stroke: #FF4000;
                stroke-width: 3px;
                filter: drop-shadow(0 0 6px #FF4000);
            }}
            28% {{ 
                stroke: #FFFF00;
                stroke-width: 4px;
                filter: drop-shadow(0 0 8px #FFFF00);
            }}
            42% {{ 
                stroke: #00FF00;
                stroke-width: 3px;
                filter: drop-shadow(0 0 6px #00FF00);
            }}
            56% {{ 
                stroke: #0080FF;
                stroke-width: 4px;
                filter: drop-shadow(0 0 8px #0080FF);
            }}
            70% {{ 
                stroke: #8000FF;
                stroke-width: 3px;
                filter: drop-shadow(0 0 6px #8000FF);
            }}
            84% {{ 
                stroke: #FF0040;
                stroke-width: 2px;
                filter: drop-shadow(0 0 4px #FF0040);
            }}
            100% {{ 
                stroke: #FF0080;
                stroke-width: 2px;
                filter: drop-shadow(0 0 3px #FF0080);
            }}
        }}
        
        .node.search-match {{
            animation: ledBreathing 2s infinite;
        }}
        
        @keyframes flowPulse {{
            0%, 100% {{ stroke-width: 2px; stroke: rgba(255, 255, 255, 0.4); }}
            50% {{ stroke-width: 4px; stroke: rgba(255, 255, 255, 0.8); }}
        }}
        
        .link.flow-active {{
            animation: flowPulse 1.5s infinite;
        }}
        
        @keyframes searchPulse {{
            0%, 100% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.2); opacity: 0.7; }}
        }}
        
        .search-highlight {{
            animation: searchPulse 1s infinite;
        }}
        
        .main-content {{
            flex: 1;
            position: relative;
            overflow: hidden;
        }}
        
        #topology {{
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.1);
            cursor: grab;
        }}
        
        #topology:active {{
            cursor: grabbing;
        }}
        
        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 10px;
            border-radius: 8px;
            pointer-events: none;
            font-size: 11px;
            max-width: 280px;
            z-index: 1000;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        .tooltip h4 {{
            margin: 0 0 6px 0;
            color: #4ECDC4;
            font-size: 13px;
        }}
        
        .tooltip-content {{
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 3px 6px;
            font-size: 10px;
        }}
        
        .legend {{
            position: absolute;
            bottom: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.8);
            padding: 10px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
            max-width: 200px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            margin: 3px 0;
            font-size: 11px;
        }}
        
        .legend-circle {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            border: 1px solid rgba(255, 255, 255, 0.5);
        }}

        .metadata-legend {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.8);
            padding: 10px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
            max-width: 220px;
            font-size: 10px;
            color: white;
            z-index: 1000;
        }}
        
        .metadata-legend h4 {{
            margin: 0 0 8px 0;
            color: #4ECDC4;
            font-size: 12px;
            font-weight: bold;
        }}
        
        .metadata-item {{
            margin: 4px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .metadata-label {{
            color: #cccccc;
            font-weight: normal;
        }}
        
        .metadata-value {{
            color: #ffffff;
            font-weight: bold;
        }}
        
        .metadata-section {{
            margin-bottom: 10px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .metadata-section:last-child {{
            border-bottom: none;
            margin-bottom: 0;
        }}
        
        .zoom-controls {{
            position: absolute;
            top: 10px;
            right: 10px;
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        
        .zoom-btn {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .zoom-btn:hover {{
            background: rgba(0, 0, 0, 0.9);
        }}
        
        .scale-controls {{
            position: absolute;
            top: 10px;
            left: 250px;
            display: flex;
            flex-direction: column;
            gap: 3px;
        }}
        
        .scale-btn {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: rgba(76, 175, 80, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }}
        
        .scale-btn:hover {{
            background: rgba(76, 175, 80, 0.9);
            transform: scale(1.1);
        }}
        
        .node {{
            stroke: rgba(255, 255, 255, 0.8);
            stroke-width: 2px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .node:hover {{
            stroke-width: 3px;
            stroke: #FFD700;
        }}
        
        .node.selected {{
            stroke: #FFD700;
            stroke-width: 4px;
            filter: drop-shadow(0 0 8px #FFD700);
        }}
        
        .link {{
            stroke: rgba(255, 255, 255, 0.4);
            stroke-width: 2;
            transition: all 0.2s ease;
        }}
        
        .link:hover {{
            stroke: rgba(255, 255, 255, 0.8);
            stroke-width: 3;
        }}
        
        .node-label {{
            fill: white;
            font-size: 9px;
            font-weight: bold;
            text-anchor: middle;
            pointer-events: none;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
            dominant-baseline: middle;
        }}
        
        .node-label tspan {{
            dominant-baseline: middle;
        }}
        
        .node-label-group {{
            pointer-events: none;
        }}
        
        .filtered {{
            opacity: 0.2 !important;
        }}
        
        .highlighted {{
            opacity: 1 !important;
        }}
        
        .selection-rect {{
            fill: rgba(255, 215, 0, 0.2);
            stroke: #FFD700;
            stroke-width: 2;
            stroke-dasharray: 5,5;
            pointer-events: none;
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
        
        .notification {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 10px 15px;
            border-radius: 6px;
            z-index: 2000;
            border: 1px solid rgba(255, 255, 255, 0.3);
            backdrop-filter: blur(10px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        }}
        
        .notification.show {{
            transform: translateX(0);
        }}
        
        .flow-path {{
            stroke: #FFD700 !important;
            stroke-width: 4px !important;
            opacity: 1 !important;
            filter: drop-shadow(0 0 6px #FFD700);
        }}
        
        /* Modal Backdrop */
        .modal-backdrop {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.5);
            z-index: 9999;
            backdrop-filter: blur(5px);
        }}
        
        /* Metadata Panel Styles */
        .metadata-panel {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 0, 0.95);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 15px;
            padding: 0;
            width: 90vw;
            height: 80vh;
            max-width: 1200px;
            max-height: 800px;
            min-width: 600px;
            min-height: 400px;
            overflow: hidden;
            z-index: 10000;
            backdrop-filter: blur(10px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7);
            display: flex;
            flex-direction: column;
        }}
        
        .metadata-header {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .metadata-header h3 {{
            margin: 0;
            color: white;
            font-size: 1.2em;
        }}
        
        .close-btn {{
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1.1em;
        }}
        
        .close-btn:hover {{
            background: rgba(255, 0, 0, 0.3);
        }}
        
        .metadata-content {{
            padding: 20px;
            flex: 1;
            overflow-y: auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        
        .metadata-section {{
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .metadata-section h4 {{
            margin: 0 0 10px 0;
            color: #4ECDC4;
            font-size: 1em;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 5px;
        }}
        
        .metadata-list {{
            background: rgba(0, 0, 0, 0.3);
            padding: 10px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            max-height: 200px;
            overflow-y: auto;
            margin-bottom: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            word-wrap: break-word;
        }}
        
        .copy-btn {{
            background: linear-gradient(45deg, #27AE60, #2ECC71);
            border: none;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.8em;
            transition: all 0.3s ease;
        }}
        
        .copy-btn:hover {{
            background: linear-gradient(45deg, #2ECC71, #27AE60);
            transform: translateY(-1px);
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.15);
            padding: 8px 12px;
            border-radius: 8px;
            text-align: center;
            backdrop-filter: blur(5px);
            font-size: 0.8em;
            transition: all 0.3s ease;
        }}
        
        .stat-card:hover {{
            background: rgba(255, 255, 255, 0.25);
            transform: translateY(-2px);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌟 SPS Network Topology - Interactive Visualization</h1>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{stats['total_nodes']}</div>
                    <div>Nodes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['total_links']}</div>
                    <div>Links</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(stats['protocols'])}</div>
                    <div>Protocols</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len([n for n in self.nodes if n['layer'] == 1])}</div>
                    <div>Entities</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(stats['metadata']['all_ips'])}</div>
                    <div>IP Addresses</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(stats['metadata']['all_ports'])}</div>
                    <div>Ports</div>
                </div>
            </div>
            
            <div class="controls">
                <div class="search-group">
                    <input type="text" class="search-input" id="searchInput" placeholder="Search nodes (keywords or RegExp)..." oninput="handleSearch()" title="Search nodes by name or details. Use RegExp for advanced patterns.">
                    <div class="checkbox-wrapper">
                        <input type="checkbox" id="regexCheckbox" onchange="handleSearch()">
                        <label for="regexCheckbox">RegExp</label>
                    </div>
                    <button onclick="clearSearch()" style="padding: 2px 8px; font-size: 0.8em;" title="Clear search filter only">Clear Search</button>
                    <button onclick="clearAllFilters()" style="padding: 2px 8px; font-size: 0.8em; margin-left: 4px;" title="Clear both search and protocol filters">Clear All</button>
                    <span class="filter-status" id="filterStatus">No filter</span>
                </div>
            </div>
            
            <div class="controls">
                <div class="control-group">
                    <label>Controls:</label>
                    <button onclick="restartSimulation()">🔄 Restart</button>
                    <button onclick="centerView()">🎯 Center</button>
                    <button onclick="toggleLabels()" id="labelBtn">🏷️ Labels</button>
                    <button onclick="clearSelection()">🔓 Clear Selection</button>
                </div>
                <div class="control-group">
                    <label>View:</label>
                    {' '.join(f'<button onclick="filterProtocol(\'{protocol}\')" id="btn_{protocol}" class="protocol-btn" title="Filter by {protocol} protocol. Combines with search if active.">{protocol}</button>' for protocol in stats['protocols'])}
                    <button onclick="showAll()" id="btnAll" class="protocol-btn active" title="Show all protocols. Preserves search filter if active.">All</button>
                </div>
            </div>
        </div>
        
        <div class="main-content">
            <svg id="topology"></svg>
            
            <div class="zoom-controls">
                <div class="zoom-btn" onclick="zoomIn()">+</div>
                <div class="zoom-btn" onclick="zoomOut()">−</div>
                <div class="zoom-btn" onclick="resetZoom()" style="font-size: 14px;">⌂</div>
            </div>
            
            <div class="legend">
                <div style="font-weight: bold; margin-bottom: 6px; color: #3498DB;">Network Protocol Colors</div>
                <div class="legend-item">
                    <div class="legend-circle" style="background: #2C3E50;"></div>
                    <span>SPS Core</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="background: #E74C3C;"></div>
                    <span>Diameter Protocol</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="background: #3498DB;"></div>
                    <span>MTP Protocol</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="background: #27AE60;"></div>
                    <span>M3UA Protocol</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="background: #F39C12;"></div>
                    <span>M2UA Protocol</span>
                </div>
                <div class="legend-item">
                    <div class="legend-circle" style="background: #9B59B6;"></div>
                    <span>SCCP Protocol</span>
                </div>
                <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 9px;">
                    <div style="color: #3498DB; font-weight: bold; margin-bottom: 3px;">Node Information:</div>
                    <div>• Hover over nodes for detailed information</div>
                    <div>• Link labels show IP:Port connections</div>
                    <div>• Click Metadata for IP/Port summaries</div>
                </div>
                <div style="margin-top: 6px; padding-top: 4px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 9px;">
                    <div style="color: #3498DB; font-weight: bold; margin-bottom: 3px;">Search Features:</div>
                    <div>• LED Breathing: Primary search matches</div>
                    <div>• Highlighted: Parent/child relationships</div>
                    <div>• Filtered: Non-matching nodes (dimmed)</div>
                </div>
                <div style="margin-top: 6px; padding-top: 4px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 9px;">
                    <div style="color: #3498DB; font-weight: bold; margin-bottom: 3px;">Layout Controls:</div>
                    <div>• Scale Out (⬌): Expand node spacing</div>
                    <div>• Scale In (⬍): Contract node spacing</div>
                    <div>• Reset Scale (⌂): Restore default spacing</div>
                    <div>• Zoom In (+): Increase view scale</div>
                    <div>• Zoom Out (−): Decrease view scale</div>
                    <div>• Reset Zoom (⌂): Restore default view</div>
                </div>
                <div style="margin-top: 6px; padding-top: 4px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 9px;">
                    <div style="color: #4ECDC4; font-weight: bold; margin-bottom: 3px;">Metadata Panel:</div>
                    <div>• Right-click for copy options</div>
                    <div>• Copy all metadata, IPs, ports</div>
                    <div>• Export network statistics</div>
                </div>
                <div style="margin-top: 6px; padding-top: 4px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 9px;">
                    <div style="color: #3498DB; font-weight: bold; margin-bottom: 3px;">Shortcuts:</div>
                    <div>• Ctrl+F: Focus search</div>
                    <div>• Ctrl+A: Select all nodes</div>
                    <div>• Esc: Clear search/selection</div>
                    <div>• Shift+Click: Multi-select</div>
                    <div>• Ctrl+Drag: Rectangle select</div>
                </div>
            </div>
            
            <!-- Metadata Legend - Bottom Right Corner -->
            <div class="metadata-legend" oncontextmenu="showMetadataContextMenu(event)">
                <h4>📊 Network Metadata</h4>
                <div class="metadata-section">
                    <div class="metadata-item">
                        <span class="metadata-label">📍 IP Addresses:</span>
                        <span class="metadata-value">{len(stats['metadata']['all_ips'])}</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">🔌 Ports:</span>
                        <span class="metadata-value">{len(stats['metadata']['all_ports'])}</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">🔗 IP:Port Pairs:</span>
                        <span class="metadata-value">{len(stats['metadata']['ip_port_pairs'])}</span>
                    </div>
                </div>
                <div class="metadata-section">
                    <div class="metadata-item">
                        <span class="metadata-label">🌐 Connections:</span>
                        <span class="metadata-value">{len(stats['metadata']['connections'])}</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">🏠 Nodes:</span>
                        <span class="metadata-value">{stats['total_nodes']}</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">🔗 Links:</span>
                        <span class="metadata-value">{stats['total_links']}</span>
                    </div>
                </div>
            </div>
            
            <!-- Scale Controls -->
            <div class="scale-controls">
                <div class="scale-btn" onclick="scaleOut()" title="Scale Out - Increase node spacing">⬌</div>
                <div class="scale-btn" onclick="scaleIn()" title="Scale In - Decrease node spacing">⬍</div>
                <div class="scale-btn" onclick="resetScale()" title="Reset Scale" style="font-size: 14px;">⌂</div>
            </div>
        </div>
    </div>

    <script>

        
        // Data
        const nodes = {json.dumps(self.nodes, indent=8)};
        const links = {json.dumps(self.links, indent=8)};
        
        // SVG setup
        const svg = d3.select("#topology");
        const container = d3.select(".main-content");
        
        // Get container dimensions
        const containerRect = container.node().getBoundingClientRect();
        const width = containerRect.width;
        const height = containerRect.height;
        
        svg.attr("width", width).attr("height", height);
        
        // Create zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", handleZoom);
        
        svg.call(zoom);
        
        // Create main group for zooming/panning
        const g = svg.append("g");
        
        // Create tooltip
        const tooltip = d3.select("body").append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);
        
        // Global variables for enhanced functionality
        let selectedNodes = new Set();
        let isDragging = false;
        let dragStartPos = null;
        let selectionRect = null;
        let currentSearchResults = new Set();
        let currentProtocolFilter = null;
        let layoutMultiplier = 1.0;
        let contextMenu = null;
        
        // Force simulation with improved forces
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(d => {{
                // Dynamic distance based on node layers and layout multiplier
                const sourceLayer = d.source.layer || 0;
                const targetLayer = d.target.layer || 0;
                const baseDistance = 60 + (Math.abs(sourceLayer - targetLayer) * 20);
                return baseDistance * layoutMultiplier;
            }}))
            .force("charge", d3.forceManyBody().strength(d => {{
                // Stronger repulsion for central nodes, scaled by layout multiplier
                const baseStrength = d.layer === 0 ? -800 : -300;
                return baseStrength * layoutMultiplier;
            }}))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(d => (d.size + 8) * layoutMultiplier))
            .force("radial", d3.forceRadial(d => {{
                // Radial positioning based on layers with proper spacing
                const baseRadius = 60 + (d.layer * 50);
                return baseRadius * layoutMultiplier;
            }}, width / 2, height / 2).strength(0.1));
        
        // Create links
        const link = g.append("g")
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("class", "link")
            .style("stroke-width", d => {{
                // Thicker lines for higher layer connections
                const maxLayer = Math.max(d.source.layer || 0, d.target.layer || 0);
                return Math.max(2, 4 - maxLayer);
            }})
            .style("marker-end", "url(#arrow)")
            .on("mouseover", function(event, d) {{
                d3.select(this).classed("flow-active", true);
                // Show link tooltip with connection info
                if (d.connection_info) {{
                    tooltip.transition()
                        .duration(200)
                        .style("opacity", .9);
                    
                    tooltip.html(`
                        <h4>${{d.type}} - ${{d.protocol}}</h4>
                        <div class="tooltip-content">
                            <div>Connection:</div><div>${{d.connection_info}}</div>
                            ${{d.remote_ip ? `<div>Remote IP:</div><div>${{d.remote_ip}}</div>` : ''}}
                            ${{d.remote_port ? `<div>Remote Port:</div><div>${{d.remote_port}}</div>` : ''}}
                            ${{d.local_port ? `<div>Local Port:</div><div>${{d.local_port}}</div>` : ''}}
                        </div>
                    `)
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY - 28) + "px");
                }}
            }})
            .on("mouseout", function(event, d) {{
                d3.select(this).classed("flow-active", false);
                tooltip.transition()
                    .duration(500)
                    .style("opacity", 0);
            }});
        
        // Add arrow markers
        g.append("defs").append("marker")
            .attr("id", "arrow")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 15)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("class", "arrow")
            .style("fill", "rgba(255, 255, 255, 0.6)");
        
        // Create nodes
        const node = g.append("g")
            .selectAll("circle")
            .data(nodes)
            .join("circle")
            .attr("class", "node")
            .attr("r", d => d.size)
            .attr("fill", d => d.color)
            .call(enhancedDrag(simulation))
            .on("mouseover", showTooltip)
            .on("mousemove", moveTooltip)
            .on("mouseout", hideTooltip)
            .on("click", enhancedNodeClick)
            .on("contextmenu", showContextMenu);
        
        // Create labels with multi-line support
        let labelsVisible = true;
        const labels = g.append("g")
            .selectAll("g")
            .data(nodes)
            .join("g")
            .attr("class", "node-label-group");
        
        // Function to intelligently split long node names
        function splitNodeName(name, maxCharsPerLine = 12) {{
            if (name.length <= maxCharsPerLine) {{
                return [name];
            }}
            
            const lines = [];
            const parts = name.split('_');
            let currentLine = '';
            
            for (let i = 0; i < parts.length; i++) {{
                const part = parts[i];
                const testLine = currentLine ? currentLine + '_' + part : part;
                
                if (testLine.length <= maxCharsPerLine) {{
                    currentLine = testLine;
                }} else {{
                    if (currentLine) {{
                        lines.push(currentLine);
                        currentLine = part;
                    }} else {{
                        // If a single part is too long, split it
                        if (part.length > maxCharsPerLine) {{
                            for (let j = 0; j < part.length; j += maxCharsPerLine) {{
                                lines.push(part.substring(j, j + maxCharsPerLine));
                            }}
                        }} else {{
                            lines.push(part);
                        }}
                        currentLine = '';
                    }}
                }}
            }}
            
            if (currentLine) {{
                lines.push(currentLine);
            }}
            
            return lines;
        }}

        // Add main text elements with tspan for multi-line
        labels.each(function(d) {{
            const group = d3.select(this);
            let labelLines = [];
            
            // First line: Always show the node name (or simplified version)
            if (d.type.includes('LINK') && d.connection) {{
                // For LINK nodes: First line is link name, second line is connection
                const linkName = d.name.split(/[\\s\\(]/)[0]; // Get first word before space or parenthesis
                labelLines.push(linkName);
                labelLines.push(d.connection);
            }} else if (d.type === 'SPS_CORE') {{
                // For core node: Just show the name
                labelLines.push(d.name);
            }} else {{
                // For all other nodes: First line is node name, second line is type and details
                const nameLines = splitNodeName(d.name);
                labelLines.push(nameLines[0]); // First part of name on first line
                
                // Second line: Combine remaining name parts + type + details
                let secondLine = '';
                
                // Add remaining name parts if any
                if (nameLines.length > 1) {{
                    secondLine = nameLines.slice(1).join('_');
                }}
                
                // Add type information
                const typeShort = d.type.replace(/_/g, '').substring(0, 6);
                if (secondLine) {{
                    secondLine += ` [${{typeShort}}]`;
                }} else {{
                    secondLine = `[${{typeShort}}]`;
                }}
                
                // Add specific details based on node type
                if (d.type === 'DIAMETER_PEER' && d.hostname) {{
                    secondLine += ` ${{d.hostname}}`;
                }} else if ((d.type === 'MTP_DSP' || d.type === 'M3UA_AS') && d.point_code) {{
                    secondLine += ` SPC:${{d.point_code}}`;
                }} else if (d.connection) {{
                    secondLine += ` ${{d.connection}}`;
                }}
                
                labelLines.push(secondLine);
            }}
            
            // Create text element with tspan elements
            const textElement = group.append("text")
                .attr("class", "node-label")
                .style("font-size", Math.max(8, d.size / 3) + "px");
            
            // Add each line as a tspan with improved spacing
            labelLines.forEach((line, index) => {{
                textElement.append("tspan")
                    .attr("x", 0)
                    .attr("dy", index === 0 ? "0" : "1.1em") // Better line spacing
                    .text(line);
            }});
        }});
        
        // Enhanced multi-select functionality
        svg.on("mousedown", function(event) {{
            if (event.ctrlKey || event.metaKey) {{
                event.preventDefault();
                startRectSelection(event);
            }}
        }});
        
        function startRectSelection(event) {{
            const [x, y] = d3.pointer(event, g.node());
            dragStartPos = {{x, y}};
            isDragging = true;
            
            selectionRect = g.append("rect")
                .attr("class", "selection-rect")
                .attr("x", x)
                .attr("y", y)
                .attr("width", 0)
                .attr("height", 0);
            
            svg.on("mousemove.selection", function(event) {{
                if (!isDragging) return;
                
                const [currentX, currentY] = d3.pointer(event, g.node());
                const rectX = Math.min(dragStartPos.x, currentX);
                const rectY = Math.min(dragStartPos.y, currentY);
                const rectWidth = Math.abs(currentX - dragStartPos.x);
                const rectHeight = Math.abs(currentY - dragStartPos.y);
                
                selectionRect
                    .attr("x", rectX)
                    .attr("y", rectY)
                    .attr("width", rectWidth)
                    .attr("height", rectHeight);
                
                // Select nodes within rectangle
                node.each(function(d) {{
                    const nodeX = d.x;
                    const nodeY = d.y;
                    if (nodeX >= rectX && nodeX <= rectX + rectWidth &&
                        nodeY >= rectY && nodeY <= rectY + rectHeight) {{
                        selectedNodes.add(d.id);
                        d3.select(this).classed("selected", true);
                    }}
                }});
            }});
            
            svg.on("mouseup.selection", function() {{
                isDragging = false;
                if (selectionRect) {{
                    selectionRect.remove();
                    selectionRect = null;
                }}
                svg.on("mousemove.selection", null);
                svg.on("mouseup.selection", null);
            }});
        }}
        
        // Update positions on simulation tick
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
            
            // Position labels with better spacing to prevent overlap
            labels
                .attr("transform", d => {{
                    // Offset label below the node to prevent overlap with the node itself
                    const labelOffsetY = d.size + 12; // Position label below the node
                    return `translate(${{d.x}}, ${{d.y + labelOffsetY}})`;
                }});
        }});
        
        // Enhanced search functionality with RegExp support
        function handleSearch() {{
            const searchTerm = document.getElementById('searchInput').value.trim();
            const useRegex = document.getElementById('regexCheckbox').checked;
            const filterStatus = document.getElementById('filterStatus');
            
            // Clear previous search results
            currentSearchResults.clear();
            
            if (!searchTerm) {{
                updateFilterStatus();
                applyCombinedFilter();
                return;
            }}
            
            let pattern;
            let matchCount = 0;
            
            try {{
                if (useRegex) {{
                    pattern = new RegExp(searchTerm, 'i');
                }} else {{
                    // Simple text search
                }}
                
                // Search and highlight matching nodes
                nodes.forEach(nodeData => {{
                    let isMatch = false;
                    
                    if (useRegex) {{
                        isMatch = pattern.test(nodeData.name) || 
                                 (nodeData.details && Object.values(nodeData.details).some(val => 
                                     typeof val === 'string' && pattern.test(val)));
                    }} else {{
                        const searchLower = searchTerm.toLowerCase();
                        isMatch = nodeData.name.toLowerCase().includes(searchLower) ||
                                 (nodeData.details && Object.values(nodeData.details).some(val => 
                                     typeof val === 'string' && val.toLowerCase().includes(searchLower)));
                    }}
                    
                    if (isMatch) {{
                        currentSearchResults.add(nodeData.id);
                        matchCount++;
                    }}
                }});
                
                // Apply combined search and protocol filter
                applyCombinedFilter();
                
                // Update filter status with combined information
                updateFilterStatus();
                
            }} catch (error) {{
                // Handle invalid regex
                if (useRegex) {{
                    filterStatus.textContent = `Invalid RegExp: ${{searchTerm}}`;
                    console.warn('Invalid regex pattern:', error);
                }} else {{
                    // Fallback to simple search
                    handleSearch();
                }}
            }}
        }}
        
        function applySearchFilter(searchResults) {{
            // Find all connected nodes (parents and children) in the full hierarchical path
            const highlightedNodes = new Set(searchResults);
            const highlightedLinks = new Set();
            
            // Function to recursively trace full path from root to leaves
            function traceFullPath(nodeId, visited = new Set()) {{
                if (visited.has(nodeId)) return; // Prevent infinite loops
                visited.add(nodeId);
                highlightedNodes.add(nodeId);
                
                // Find all connections (both parent and child relationships)
                links.forEach(link => {{
                    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
                    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
                    
                    if (sourceId === nodeId) {{
                        // This node is the source, target is connected
                        highlightedNodes.add(targetId);
                        highlightedLinks.add(link);
                        traceFullPath(targetId, visited);
                    }} else if (targetId === nodeId) {{
                        // This node is the target, source is connected
                        highlightedNodes.add(sourceId);
                        highlightedLinks.add(link);
                        traceFullPath(sourceId, visited);
                    }}
                }});
                
                // Also trace using parent-child relationships from node data
                const currentNode = nodes.find(n => n.id === nodeId);
                if (currentNode) {{
                    // Trace upward to root
                    if (currentNode.parent && !visited.has(currentNode.parent)) {{
                        traceFullPath(currentNode.parent, visited);
                    }}
                    
                    // Trace downward to all children
                    nodes.forEach(node => {{
                        if (node.parent === nodeId && !visited.has(node.id)) {{
                            traceFullPath(node.id, visited);
                        }}
                    }});
                }}
            }}
            
            // Trace full paths for all search results with a shared visited set
            const globalVisited = new Set();
            searchResults.forEach(nodeId => {{
                traceFullPath(nodeId, globalVisited);
            }});
            
            // Apply visual effects
            node.each(function(d) {{
                const element = d3.select(this);
                if (searchResults.has(d.id)) {{
                    // Primary matches get LED breathing effect
                    element.classed("search-match", true)
                           .classed("filtered", false)
                           .classed("highlighted", true);
                }} else if (highlightedNodes.has(d.id)) {{
                    // Connected nodes in the path are highlighted but no LED effect
                    element.classed("search-match", false)
                           .classed("filtered", false)
                           .classed("highlighted", true);
                }} else {{
                    // Non-matching nodes are filtered
                    element.classed("search-match", false)
                           .classed("filtered", true)
                           .classed("highlighted", false);
                }}
            }});
            
            // Highlight all connected links in the path
            link.each(function(d) {{
                const element = d3.select(this);
                if (highlightedLinks.has(d)) {{
                    element.classed("filtered", false)
                           .classed("highlighted", true);
                }} else {{
                    element.classed("filtered", true)
                           .classed("highlighted", false);
                }}
            }});
        }}
        
        function applyCombinedFilter() {{
            // Clear all filter states first
            node.classed("search-match", false)
                .classed("filtered", false)
                .classed("highlighted", false);
            
            link.classed("filtered", false)
                .classed("highlighted", false);
            
            // If no search and no protocol filter, show everything
            if (currentSearchResults.size === 0 && !currentProtocolFilter) {{
                return;
            }}
            
            // Apply combined filtering logic
            if (currentSearchResults.size > 0 && currentProtocolFilter) {{
                // Both search and protocol filter active
                applyCombinedSearchAndProtocolFilter();
            }} else if (currentSearchResults.size > 0) {{
                // Only search filter active
                applySearchFilter(currentSearchResults);
            }} else if (currentProtocolFilter) {{
                // Only protocol filter active
                applyProtocolFilter(currentProtocolFilter);
            }}
        }}
        
        function applyCombinedSearchAndProtocolFilter() {{
            // Find nodes that match both search criteria AND protocol
            const highlightedNodes = new Set();
            const highlightedLinks = new Set();
            
            // Function to recursively trace full path from root to leaves
            function traceFullPath(nodeId, visited = new Set()) {{
                if (visited.has(nodeId)) return;
                visited.add(nodeId);
                
                const nodeData = nodes.find(n => n.id === nodeId);
                const nodeProtocol = getNodeProtocol(nodeData);
                
                // Only include nodes that match the protocol filter OR are central/parent nodes
                if (nodeProtocol === currentProtocolFilter || nodeData.id === 'SPS_LOCAL' || nodeData.layer === 0) {{
                    highlightedNodes.add(nodeId);
                }}
                
                // Find all connections
                links.forEach(link => {{
                    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
                    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
                    
                    if (sourceId === nodeId || targetId === nodeId) {{
                        // Only include links that match the protocol filter
                        if (link.protocol === currentProtocolFilter) {{
                            highlightedLinks.add(link);
                            
                            if (sourceId === nodeId) {{
                                traceFullPath(targetId, visited);
                            }} else {{
                                traceFullPath(sourceId, visited);
                            }}
                        }}
                    }}
                }});
                
                // Also trace using parent-child relationships
                if (nodeData) {{
                    if (nodeData.parent && !visited.has(nodeData.parent)) {{
                        traceFullPath(nodeData.parent, visited);
                    }}
                    
                    nodes.forEach(node => {{
                        if (node.parent === nodeId && !visited.has(node.id)) {{
                            const childProtocol = getNodeProtocol(node);
                            if (childProtocol === currentProtocolFilter) {{
                                traceFullPath(node.id, visited);
                            }}
                        }}
                    }});
                }}
            }}
            
            // Trace paths for search results that also match protocol
            currentSearchResults.forEach(nodeId => {{
                const nodeData = nodes.find(n => n.id === nodeId);
                const nodeProtocol = getNodeProtocol(nodeData);
                
                // Only trace if the node matches the protocol filter or is a central node
                if (nodeProtocol === currentProtocolFilter || nodeData.id === 'SPS_LOCAL' || nodeData.layer === 0) {{
                    traceFullPath(nodeId);
                }}
            }});
            
            // Apply visual effects
            node.each(function(d) {{
                const element = d3.select(this);
                const nodeProtocol = getNodeProtocol(d);
                const matchesSearch = currentSearchResults.has(d.id);
                const matchesProtocol = nodeProtocol === currentProtocolFilter || d.id === 'SPS_LOCAL';
                
                if (matchesSearch && matchesProtocol) {{
                    // Primary matches: both search and protocol
                    element.classed("search-match", true)
                           .classed("filtered", false)
                           .classed("highlighted", true);
                }} else if (highlightedNodes.has(d.id) && matchesProtocol) {{
                    // Connected nodes in the path that match protocol
                    element.classed("search-match", false)
                           .classed("filtered", false)
                           .classed("highlighted", true);
                }} else {{
                    // Non-matching nodes are filtered
                    element.classed("search-match", false)
                           .classed("filtered", true)
                           .classed("highlighted", false);
                }}
            }});
            
            // Highlight links that match protocol
            link.each(function(d) {{
                const element = d3.select(this);
                if (highlightedLinks.has(d) && d.protocol === currentProtocolFilter) {{
                    element.classed("filtered", false)
                           .classed("highlighted", true);
                }} else {{
                    element.classed("filtered", true)
                           .classed("highlighted", false);
                }}
            }});
        }}
        
        function applyProtocolFilter(protocol) {{
            // Filter nodes and links by protocol only
            node.each(function(d) {{
                const element = d3.select(this);
                const nodeProtocol = getNodeProtocol(d);
                
                if (nodeProtocol === protocol || d.id === 'SPS_LOCAL') {{
                    element.classed("filtered", false)
                           .classed("highlighted", true);
                }} else {{
                    element.classed("filtered", true)
                           .classed("highlighted", false);
                }}
            }});
            
            link.each(function(d) {{
                const element = d3.select(this);
                if (d.protocol === protocol) {{
                    element.classed("filtered", false)
                           .classed("highlighted", true);
                }} else {{
                    element.classed("filtered", true)
                           .classed("highlighted", false);
                }}
            }});
        }}
        
        function updateFilterStatus() {{
            const filterStatus = document.getElementById('filterStatus');
            const searchTerm = document.getElementById('searchInput').value.trim();
            const useRegex = document.getElementById('regexCheckbox').checked;
            
            let statusParts = [];
            
            if (searchTerm) {{
                const matchCount = currentSearchResults.size;
                const searchText = useRegex ? 
                    `RegExp: ${{searchTerm}} (${{matchCount}} matches)` :
                    `Search: "${{searchTerm}}" (${{matchCount}} matches)`;
                statusParts.push(searchText);
            }}
            
            if (currentProtocolFilter) {{
                statusParts.push(`${{currentProtocolFilter}} filter`);
            }}
            
            if (statusParts.length === 0) {{
                filterStatus.textContent = 'No filter';
            }} else {{
                filterStatus.textContent = statusParts.join(' + ');
            }}
        }}
        
        function clearSearchResults() {{
            // Remove all search-related classes
            node.classed("search-match", false)
                .classed("filtered", false)
                .classed("highlighted", false);
            
            link.classed("filtered", false)
                .classed("highlighted", false);
            
            currentSearchResults.clear();
        }}
        
        function clearSearch() {{
            document.getElementById('searchInput').value = '';
            currentSearchResults.clear();
            updateFilterStatus();
            applyCombinedFilter(); // This will now apply protocol filter if one is active, or show all
        }}
        
        function clearAllFilters() {{
            document.getElementById('searchInput').value = '';
            currentSearchResults.clear();
            currentProtocolFilter = null;
            
            // Reset all button states
            document.querySelectorAll('.protocol-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            document.getElementById('btnAll').classList.add('active');
            
            updateFilterStatus();
            applyCombinedFilter();
        }}
        
        // Context menu functionality
        function showContextMenu(event, d) {{
            event.preventDefault();
            event.stopPropagation();
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
            
            // Add MML command copy if available
            if (d.mml_command || d.details) {{
                contextMenu.append("div")
                    .attr("class", "context-menu-item")
                    .text("📝 Copy Details")
                    .on("click", () => copyNodeDetails(d));
            }}
            
            contextMenu.append("div").attr("class", "context-menu-separator");
            
            // Network metadata section
            contextMenu.append("div")
                .attr("class", "context-menu-item")
                .text("🌐 Copy Network Metadata")
                .on("click", () => copyNetworkMetadata());
            
            contextMenu.append("div")
                .attr("class", "context-menu-item")
                .text("📊 Copy All IP Addresses")
                .on("click", () => copyAllIPs());
            
            contextMenu.append("div")
                .attr("class", "context-menu-item")
                .text("🔌 Copy All Ports")
                .on("click", () => copyAllPorts());
            
            contextMenu.append("div")
                .attr("class", "context-menu-item")
                .text("🔗 Copy IP:Port Pairs")
                .on("click", () => copyIPPortPairs());
            
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
            
            contextMenu.append("div").attr("class", "context-menu-separator");
            
            contextMenu.append("div")
                .attr("class", "context-menu-item")
                .text("🏷️ Add to Selection")
                .on("click", () => addToSelection(d));
            
            contextMenu.append("div")
                .attr("class", "context-menu-item")
                .text("📌 Pin Node")
                .on("click", () => pinNode(d));
            
            if (d.fx !== null || d.fy !== null) {{
                contextMenu.append("div")
                    .attr("class", "context-menu-item")
                    .text("📍 Unpin Node")
                    .on("click", () => unpinNode(d));
            }}
        }}
        
        function hideContextMenu() {{
            if (contextMenu) {{
                contextMenu.remove();
                contextMenu = null;
            }}
        }}
        
        // Metadata context menu functionality
        function showMetadataContextMenu(event) {{
            event.preventDefault();
            event.stopPropagation();
            hideContextMenu();
            
            contextMenu = d3.select("body")
                .append("div")
                .attr("class", "context-menu")
                .style("left", event.pageX + "px")
                .style("top", event.pageY + "px");
            
            // Add metadata copy options
            contextMenu.append("div")
                .attr("class", "context-menu-item")
                .text("📊 Copy All Metadata")
                .on("click", () => copyAllMetadata());
            
            contextMenu.append("div")
                .attr("class", "context-menu-item")
                .text("📍 Copy IP Addresses")
                .on("click", () => copyAllIPs());
            
            contextMenu.append("div")
                .attr("class", "context-menu-item")
                .text("🔌 Copy Ports")
                .on("click", () => copyAllPorts());
            
            contextMenu.append("div")
                .attr("class", "context-menu-item")
                .text("🔗 Copy IP:Port Pairs")
                .on("click", () => copyIPPortPairs());
            
            contextMenu.append("div").attr("class", "context-menu-separator");
            
            contextMenu.append("div")
                .attr("class", "context-menu-item")
                .text("🌐 Copy Network Stats")
                .on("click", () => copyNetworkStats());
            
            contextMenu.append("div")
                .attr("class", "context-menu-item")
                .text("📋 Copy Connection Summary")
                .on("click", () => copyConnectionSummary());
        }}
        
        function copyNodeInfo(d) {{
            const info = `Node: ${{d.name}}
Type: ${{d.type}}
ID: ${{d.id}}
Layer: ${{d.layer}}
${{Object.entries(d.details || {{}}).map(([k, v]) => `${{k}}: ${{v}}`).join('\\n')}}
${{d.connection ? `Connection: ${{d.connection}}` : ''}}
${{d.hostname ? `Hostname: ${{d.hostname}}` : ''}}
${{d.point_code ? `Point Code: ${{d.point_code}}` : ''}}`;
            
            navigator.clipboard.writeText(info).then(() => {{
                console.log("Node info copied to clipboard");
                showNotification("Node info copied!");
            }}).catch(() => {{
                console.log("Failed to copy to clipboard");
                showNotification("Copy failed - check console");
            }});
            hideContextMenu();
        }}
        
        function copyNodeDetails(d) {{
            let details = '';
            if (d.mml_command) {{
                details = d.mml_command;
            }} else if (d.details) {{
                details = Object.entries(d.details)
                    .map(([k, v]) => `${{k}}: ${{v}}`)
                    .join('\\n');
            }}
            
            if (details) {{
                navigator.clipboard.writeText(details).then(() => {{
                    console.log("Node details copied to clipboard");
                    showNotification("Details copied!");
                }}).catch(() => {{
                    showNotification("Copy failed - check console");
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
        
        function highlightPath(startNode) {{
            // Reset all highlighting
            node.classed("search-match highlighted", false);
            link.classed("flow-path highlighted", false);
            
            // Find and highlight all descendants recursively using the same logic as showConnectedNodes
            const connectedIds = new Set([startNode.id]);
            const highlightedLinks = new Set();
            
            // Function to recursively trace all descendants
            function traceAllDescendants(nodeId, visited = new Set()) {{
                if (visited.has(nodeId)) return; // Prevent infinite loops
                visited.add(nodeId);
                connectedIds.add(nodeId);
                
                // Find all connections via links
                links.forEach(link => {{
                    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
                    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
                    
                    if (sourceId === nodeId) {{
                        // This node is the source, target is a child
                        connectedIds.add(targetId);
                        highlightedLinks.add(link);
                        traceAllDescendants(targetId, visited);
                    }} else if (targetId === nodeId) {{
                        // This node is the target, source is a parent
                        connectedIds.add(sourceId);
                        highlightedLinks.add(link);
                        traceAllDescendants(sourceId, visited);
                    }}
                }});
                
                // Also trace using parent-child relationships from node data
                const currentNode = nodes.find(n => n.id === nodeId);
                if (currentNode) {{
                    // Trace upward to parent
                    if (currentNode.parent && !visited.has(currentNode.parent)) {{
                        traceAllDescendants(currentNode.parent, visited);
                    }}
                    
                    // Trace downward to all children
                    nodes.forEach(node => {{
                        if (node.parent === nodeId && !visited.has(node.id)) {{
                            traceAllDescendants(node.id, visited);
                        }}
                    }});
                }}
            }}
            
            // Start tracing from the selected node
            traceAllDescendants(startNode.id);
            
            // Highlight all connected nodes
            node.filter(d => connectedIds.has(d.id)).classed("highlighted", true);
            
            // Highlight all connected links
            highlightedLinks.forEach(link => {{
                const linkSId = typeof link.source === 'object' ? link.source.id : link.source;
                const linkTId = typeof link.target === 'object' ? link.target.id : link.target;
                
                svg.selectAll(".link").filter(l => {{
                    const sId = typeof l.source === 'object' ? l.source.id : l.source;
                    const tId = typeof l.target === 'object' ? l.target.id : l.target;
                    return sId === linkSId && tId === linkTId;
                }}).classed("flow-path", true);
            }});
            
            hideContextMenu();
            showNotification(`Highlighted path from ${{startNode.name}} (${{connectedIds.size}} nodes)`);
        }}
        
        function showConnectedNodes(d) {{
            // Reset highlighting
            node.classed("search-match highlighted", false);
            link.classed("flow-path highlighted", false);
            
            // Highlight the selected node
            node.filter(n => n.id === d.id).classed("highlighted", true);
            
            // Find and highlight all descendants recursively (children, grandchildren, etc.)
            const connectedIds = new Set([d.id]);
            const highlightedLinks = new Set();
            
            // Function to recursively trace all descendants
            function traceAllDescendants(nodeId, visited = new Set()) {{
                if (visited.has(nodeId)) return; // Prevent infinite loops
                visited.add(nodeId);
                connectedIds.add(nodeId);
                
                // Find all connections via links
                links.forEach(link => {{
                    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
                    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
                    
                    if (sourceId === nodeId) {{
                        // This node is the source, target is a child
                        connectedIds.add(targetId);
                        highlightedLinks.add(link);
                        traceAllDescendants(targetId, visited);
                    }} else if (targetId === nodeId) {{
                        // This node is the target, source is a parent
                        connectedIds.add(sourceId);
                        highlightedLinks.add(link);
                        traceAllDescendants(sourceId, visited);
                    }}
                }});
                
                // Also trace using parent-child relationships from node data
                const currentNode = nodes.find(n => n.id === nodeId);
                if (currentNode) {{
                    // Trace upward to parent
                    if (currentNode.parent && !visited.has(currentNode.parent)) {{
                        traceAllDescendants(currentNode.parent, visited);
                    }}
                    
                    // Trace downward to all children
                    nodes.forEach(node => {{
                        if (node.parent === nodeId && !visited.has(node.id)) {{
                            traceAllDescendants(node.id, visited);
                        }}
                    }});
                }}
            }}
            
            // Start tracing from the selected node
            traceAllDescendants(d.id);
            
            // Highlight all connected nodes
            node.filter(n => connectedIds.has(n.id)).classed("highlighted", true);
            
            // Highlight all connected links
            highlightedLinks.forEach(link => {{
                const linkSId = typeof link.source === 'object' ? link.source.id : link.source;
                const linkTId = typeof link.target === 'object' ? link.target.id : link.target;
                
                svg.selectAll(".link").filter(l => {{
                    const sId = typeof l.source === 'object' ? l.source.id : l.source;
                    const tId = typeof l.target === 'object' ? l.target.id : l.target;
                    return sId === linkSId && tId === linkTId;
                }}).classed("flow-path", true);
            }});
            
            hideContextMenu();
            showNotification(`Showing ${{connectedIds.size}} nodes connected to ${{d.name}} (including all descendants)`);
        }}
        
        function addToSelection(d) {{
            selectedNodes.add(d.id);
            node.filter(n => n.id === d.id).classed("selected", true);
            hideContextMenu();
            showNotification(`Added ${{d.name}} to selection (${{selectedNodes.size}} selected)`);
        }}
        
        function pinNode(d) {{
            d.fx = d.x;
            d.fy = d.y;
            hideContextMenu();
            showNotification(`Pinned ${{d.name}} at current position`);
        }}
        
        function unpinNode(d) {{
            d.fx = null;
            d.fy = null;
            simulation.alpha(0.3).restart();
            hideContextMenu();
            showNotification(`Unpinned ${{d.name}} - will move freely`);
        }}
        
        function showNotification(message) {{
            // Remove any existing notification
            d3.selectAll(".notification").remove();
            
            const notification = d3.select("body")
                .append("div")
                .attr("class", "notification")
                .text(message);
            
            // Trigger animation
            setTimeout(() => notification.classed("show", true), 10);
            
            // Auto-remove after 3 seconds
            setTimeout(() => {{
                notification.classed("show", false);
                setTimeout(() => notification.remove(), 300);
            }}, 3000);
        }}
        
        // Network metadata copy functions
        function copyNetworkMetadata() {{
            const metadata = {{
                totalNodes: nodes.length,
                totalLinks: links.length,
                protocols: Array.from(new Set(links.map(l => l.protocol))),
                nodeTypes: {{}},
                allIPs: {json.dumps(stats['metadata']['all_ips'])},
                allPorts: {json.dumps(stats['metadata']['all_ports'])},
                ipPortPairs: {json.dumps(stats['metadata']['ip_port_pairs'])},
                timestamp: new Date().toISOString(),
                source: 'SPS Network Topology Visualization'
            }};
            
            // Count node types
            nodes.forEach(node => {{
                metadata.nodeTypes[node.type] = (metadata.nodeTypes[node.type] || 0) + 1;
            }});
            
            const metadataText = `SPS Network Topology - Complete Metadata
========================================
Generated: ${{metadata.timestamp}}
Source: ${{metadata.source}}

Network Summary:
- Total Nodes: ${{metadata.totalNodes}}
- Total Links: ${{metadata.totalLinks}}
- Protocols: ${{metadata.protocols.join(', ')}}
- IP Addresses: ${{metadata.allIPs.length}}
- Ports: ${{metadata.allPorts.length}}
- IP:Port Pairs: ${{metadata.ipPortPairs.length}}

Node Type Distribution:
${{Object.entries(metadata.nodeTypes).map(([type, count]) => `- ${{type}}: ${{count}}`).join('\\n')}}

All IP Addresses:
${{metadata.allIPs.join('\\n')}}

All Ports:
${{metadata.allPorts.join('\\n')}}

IP:Port Connection Pairs:
${{metadata.ipPortPairs.join('\\n')}}

Raw JSON Metadata:
${{JSON.stringify(metadata, null, 2)}}`;
            
            navigator.clipboard.writeText(metadataText).then(() => {{
                showNotification("Complete network metadata copied to clipboard!");
            }}).catch(() => {{
                showNotification("Copy failed - check console");
            }});
            hideContextMenu();
        }}
        
        function copyAllIPs() {{
            const allIPs = {json.dumps(stats['metadata']['all_ips'])};
            const ipText = `SPS Network - All IP Addresses (${{allIPs.length}} total)
================================================================
${{allIPs.join('\\n')}}`;
            
            navigator.clipboard.writeText(ipText).then(() => {{
                showNotification(`Copied ${{allIPs.length}} IP addresses to clipboard!`);
            }}).catch(() => {{
                showNotification("Copy failed - check console");
            }});
            hideContextMenu();
        }}
        
        function copyAllPorts() {{
            const allPorts = {json.dumps(stats['metadata']['all_ports'])};
            const portText = `SPS Network - All Ports (${{allPorts.length}} total)
==================================================
${{allPorts.join('\\n')}}`;
            
            navigator.clipboard.writeText(portText).then(() => {{
                showNotification(`Copied ${{allPorts.length}} ports to clipboard!`);
            }}).catch(() => {{
                showNotification("Copy failed - check console");
            }});
            hideContextMenu();
        }}
        
        function copyIPPortPairs() {{
            const ipPortPairs = {json.dumps(stats['metadata']['ip_port_pairs'])};
            const pairText = `SPS Network - All IP:Port Connection Pairs (${{ipPortPairs.length}} total)
==================================================================
${{ipPortPairs.join('\\n')}}`;
            
            navigator.clipboard.writeText(pairText).then(() => {{
                showNotification(`Copied ${{ipPortPairs.length}} IP:Port pairs to clipboard!`);
            }}).catch(() => {{
                showNotification("Copy failed - check console");
            }});
            hideContextMenu();
        }}
        
        // New metadata copy functions
        function copyAllMetadata() {{
            const metadata = {{
                totalNodes: nodes.length,
                totalLinks: links.length,
                protocols: Array.from(new Set(links.map(l => l.protocol))),
                nodeTypes: {{}},
                allIPs: {json.dumps(stats['metadata']['all_ips'])},
                allPorts: {json.dumps(stats['metadata']['all_ports'])},
                ipPortPairs: {json.dumps(stats['metadata']['ip_port_pairs'])},
                timestamp: new Date().toISOString(),
                source: 'SPS Network Topology Visualization'
            }};
            
            // Count node types
            nodes.forEach(node => {{
                metadata.nodeTypes[node.type] = (metadata.nodeTypes[node.type] || 0) + 1;
            }});
            
            const metadataText = `SPS Network Topology - Complete Metadata
========================================
Generated: ${{metadata.timestamp}}
Source: ${{metadata.source}}

Network Summary:
- Total Nodes: ${{metadata.totalNodes}}
- Total Links: ${{metadata.totalLinks}}
- Protocols: ${{metadata.protocols.join(', ')}}
- IP Addresses: ${{metadata.allIPs.length}}
- Ports: ${{metadata.allPorts.length}}
- IP:Port Pairs: ${{metadata.ipPortPairs.length}}

Node Type Distribution:
${{Object.entries(metadata.nodeTypes).map(([type, count]) => `- ${{type}}: ${{count}}`).join('\\n')}}

All IP Addresses:
${{metadata.allIPs.join('\\n')}}

All Ports:
${{metadata.allPorts.join('\\n')}}

IP:Port Connection Pairs:
${{metadata.ipPortPairs.join('\\n')}}

Raw JSON Metadata:
${{JSON.stringify(metadata, null, 2)}}`;
            
            navigator.clipboard.writeText(metadataText).then(() => {{
                showNotification("Complete network metadata copied to clipboard!");
            }}).catch(() => {{
                showNotification("Copy failed - check console");
            }});
            hideContextMenu();
        }}
        
        function copyNetworkStats() {{
            const stats = {{
                totalNodes: nodes.length,
                totalLinks: links.length,
                protocols: Array.from(new Set(links.map(l => l.protocol))),
                ipCount: {len(stats['metadata']['all_ips'])},
                portCount: {len(stats['metadata']['all_ports'])},
                connectionCount: {len(stats['metadata']['ip_port_pairs'])},
                nodeTypes: {{}}
            }};
            
            nodes.forEach(node => {{
                stats.nodeTypes[node.type] = (stats.nodeTypes[node.type] || 0) + 1;
            }});
            
            const statsText = `SPS Network Statistics
======================
Total Nodes: ${{stats.totalNodes}}
Total Links: ${{stats.totalLinks}}
Protocols: ${{stats.protocols.join(', ')}}
IP Addresses: ${{stats.ipCount}}
Ports: ${{stats.portCount}}
Connections: ${{stats.connectionCount}}

Node Distribution:
${{Object.entries(stats.nodeTypes).map(([type, count]) => `${{type}}: ${{count}}`).join('\\n')}}`;
            
            navigator.clipboard.writeText(statsText).then(() => {{
                showNotification("Network statistics copied to clipboard!");
            }}).catch(() => {{
                showNotification("Copy failed - check console");
            }});
            hideContextMenu();
        }}
        
        function copyConnectionSummary() {{
            const connections = {json.dumps(stats['metadata']['ip_port_pairs'])};
            const connectionsByProtocol = {{}};
            
            links.forEach(link => {{
                if (!connectionsByProtocol[link.protocol]) {{
                    connectionsByProtocol[link.protocol] = [];
                }}
                connectionsByProtocol[link.protocol].push(link);
            }});
            
            let summaryText = `SPS Network Connection Summary
===============================
Total Connections: ${{connections.length}}

Connections by Protocol:
${{Object.entries(connectionsByProtocol).map(([protocol, links]) => 
    `${{protocol}}: ${{links.length}} connections`).join('\\n')}}

All Connection Details:
${{connections.join('\\n')}}`;
            
            navigator.clipboard.writeText(summaryText).then(() => {{
                showNotification("Connection summary copied to clipboard!");
            }}).catch(() => {{
                showNotification("Copy failed - check console");
            }});
            hideContextMenu();
        }}
        
        // Click outside to hide context menu
        d3.select("body").on("click", hideContextMenu);
        
        // Layout control functions
        // Enhanced node selection and interaction
        function enhancedNodeClick(event, d) {{
            event.stopPropagation();
            
            if (event.shiftKey) {{
                // Multi-select with Shift
                if (selectedNodes.has(d.id)) {{
                    selectedNodes.delete(d.id);
                    d3.select(this).classed("selected", false);
                }} else {{
                    selectedNodes.add(d.id);
                    d3.select(this).classed("selected", true);
                }}
            }} else if (event.ctrlKey || event.metaKey) {{
                // Toggle selection with Ctrl/Cmd
                if (selectedNodes.has(d.id)) {{
                    selectedNodes.delete(d.id);
                    d3.select(this).classed("selected", false);
                }} else {{
                    selectedNodes.add(d.id);
                    d3.select(this).classed("selected", true);
                }}
            }} else {{
                // Single select (clear others)
                clearSelection();
                selectedNodes.add(d.id);
                d3.select(this).classed("selected", true);
                
                // Zoom to clicked node
                const transform = d3.zoomIdentity
                    .translate(width / 2 - d.x, height / 2 - d.y)
                    .scale(1.5);
                
                svg.transition()
                    .duration(750)
                    .call(zoom.transform, transform);
            }}
        }}
        
        function clearSelection() {{
            selectedNodes.clear();
            node.classed("selected", false);
        }}
        
        // Enhanced drag behavior with group dragging
        function enhancedDrag(simulation) {{
            function dragstarted(event, d) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                
                if (!selectedNodes.has(d.id)) {{
                    // If dragging a non-selected node, select it
                    if (!event.shiftKey && !event.ctrlKey && !event.metaKey) {{
                        clearSelection();
                    }}
                    selectedNodes.add(d.id);
                    d3.select(this).classed("selected", true);
                }}
                
                // Set fixed positions for all selected nodes
                selectedNodes.forEach(nodeId => {{
                    const nodeData = nodes.find(n => n.id === nodeId);
                    if (nodeData) {{
                        nodeData.fx = nodeData.x;
                        nodeData.fy = nodeData.y;
                    }}
                }});
            }}
            
            function dragged(event, d) {{
                const dx = event.x - d.x;
                const dy = event.y - d.y;
                
                // Move all selected nodes together
                selectedNodes.forEach(nodeId => {{
                    const nodeData = nodes.find(n => n.id === nodeId);
                    if (nodeData) {{
                        nodeData.fx += dx;
                        nodeData.fy += dy;
                    }}
                }});
            }}
            
            function dragended(event, d) {{
                if (!event.active) simulation.alphaTarget(0);
                
                // Release fixed positions
                selectedNodes.forEach(nodeId => {{
                    const nodeData = nodes.find(n => n.id === nodeId);
                    if (nodeData) {{
                        nodeData.fx = null;
                        nodeData.fy = null;
                    }}
                }});
            }}
            
            return d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended);
        }}
        
        // Zoom and pan handlers
        function handleZoom(event) {{
            g.attr("transform", event.transform);
        }}
        
        function zoomIn() {{
            svg.transition().duration(300).call(
                zoom.scaleBy, 1.5
            );
        }}
        
        function zoomOut() {{
            svg.transition().duration(300).call(
                zoom.scaleBy, 1 / 1.5
            );
        }}
        
        function resetZoom() {{
            svg.transition().duration(500).call(
                zoom.transform,
                d3.zoomIdentity.translate(0, 0).scale(1)
            );
        }}
        
        // Scale control functions for layout spacing
        function scaleOut() {{
            layoutMultiplier = Math.min(layoutMultiplier * 1.2, 3.0);
            updateLayoutMultiplier();
        }}
        
        function scaleIn() {{
            layoutMultiplier = Math.max(layoutMultiplier / 1.2, 0.3);
            updateLayoutMultiplier();
        }}
        
        function resetScale() {{
            layoutMultiplier = 1.0;
            updateLayoutMultiplier();
        }}
        
        function updateLayoutMultiplier() {{
            // Update force simulation with new layout multiplier
            simulation
                .force("link", d3.forceLink()
                    .id(d => d.id)
                    .distance(d => {{
                        const baseDistance = d.type === 'main' ? 150 : 
                                           d.source.layer === 1 ? 120 : 80;
                        return baseDistance * layoutMultiplier;
                    }})
                )
                .force("charge", d3.forceManyBody()
                    .strength(d => {{
                        const baseStrength = d.layer === 0 ? -2000 : -800;
                        return baseStrength * layoutMultiplier;
                    }})
                )
                .force("collision", d3.forceCollide()
                    .radius(d => (d.size + 8) * layoutMultiplier)
                )
                .force("radial", d3.forceRadial(d => {{
                    const baseRadius = d.layer * 200 + 100;
                    return baseRadius * layoutMultiplier;
                }}, width / 2, height / 2));
            
            // Re-link the data to the updated force
            simulation.force("link").links(links);
            
            // Restart simulation to apply changes
            simulation.alpha(0.5).restart();
        }}
        
        // Drag behavior with improved constraints
        function drag(simulation) {{
            function dragstarted(event) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            }}
            
            function dragged(event) {{
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            }}
            
            function dragended(event) {{
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            }}
            
            return d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended);
        }}
        
        // Tooltip functions
        function showTooltip(event, d) {{
            const details = Object.entries(d.details || {{}})
                .map(([key, value]) => `<div>${{key}}:</div><div>${{value}}</div>`)
                .join('');
            
            tooltip.transition()
                .duration(200)
                .style("opacity", .9);
            
            tooltip.html(`
                <h4>${{d.name}}</h4>
                <div class="tooltip-content">
                    ${{details}}
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
        
        function nodeClick(event, d) {{
            console.log("Clicked node:", d);
            // Zoom to clicked node
            const transform = d3.zoomIdentity
                .translate(width / 2 - d.x, height / 2 - d.y)
                .scale(1.5);
            
            svg.transition()
                .duration(750)
                .call(zoom.transform, transform);
        }}
        
        // Control functions
        function restartSimulation() {{
            simulation.alpha(1).restart();
        }}
        
        function centerView() {{
            resetZoom();
            simulation.force("center", d3.forceCenter(width / 2, height / 2));
            simulation.alpha(0.3).restart();
        }}
        
        function toggleLabels() {{
            labelsVisible = !labelsVisible;
            labels.style("opacity", labelsVisible ? 1 : 0);
            document.getElementById("labelBtn").style.background = 
                labelsVisible ? "linear-gradient(45deg, #4ECDC4, #44A08D)" : "linear-gradient(45deg, #ff6b6b, #ff8e8e)";
        }}
        
        function filterProtocol(protocol) {{
            // Store current protocol filter
            currentProtocolFilter = protocol;
            
            // Update button states
            document.querySelectorAll('.protocol-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            document.getElementById(`btn_${{protocol}}`).classList.add('active');
            
            // Update status and apply combined filter
            updateFilterStatus();
            applyCombinedFilter();
        }}
        
        function showAll() {{
            // Clear protocol filter
            currentProtocolFilter = null;
            
            // Update button states
            document.querySelectorAll('.protocol-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            document.getElementById('btnAll').classList.add('active');
            
            // Update status and apply combined filter (will show search results if any, otherwise show all)
            updateFilterStatus();
            applyCombinedFilter();
        }}
        
        function getNodeProtocol(node) {{
            // Find the protocol by checking connected links
            const connectedLink = links.find(l => 
                l.source.id === node.id || l.target.id === node.id
            );
            return connectedLink ? connectedLink.protocol : 'UNKNOWN';
        }}
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape') {{
                clearSearch();
                clearSelection();
                showAll();
            }} else if (event.key === 'Delete' && selectedNodes.size > 0) {{
                // Could implement node deletion here
                console.log('Delete pressed with selected nodes:', Array.from(selectedNodes));
            }} else if (event.ctrlKey || event.metaKey) {{
                if (event.key === 'a') {{
                    event.preventDefault();
                    // Select all nodes
                    selectedNodes.clear();
                    nodes.forEach(n => selectedNodes.add(n.id));
                    node.classed("selected", true);
                }} else if (event.key === 'f') {{
                    event.preventDefault();
                    // Focus on search input
                    document.getElementById('searchInput').focus();
                }}
            }}
        }});
        
        // Resize handler
        window.addEventListener('resize', () => {{
            const newRect = container.node().getBoundingClientRect();
            const newWidth = newRect.width;
            const newHeight = newRect.height;
            
            svg.attr("width", newWidth).attr("height", newHeight);
            simulation.force("center", d3.forceCenter(newWidth / 2, newHeight / 2));
            simulation.alpha(0.3).restart();
        }});
        
        // Initialize with enhanced features
        console.log("🚀 Enhanced SPS Topology loaded with", nodes.length, "nodes and", links.length, "links");
        console.log("🔍 Features: LED breathing search, RegExp support, multi-select, layout controls");
        console.log("⌨️  Shortcuts: Ctrl+A (select all), Ctrl+F (search), Esc (clear), Shift+Click (multi-select)");
        console.log("🎛️  Controls: Ctrl+Drag (rectangle select), Shift+Drag (group move)");
        console.log("🌐 Protocols:", {stats['protocols']});
    </script>
</body>
</html>'''
        
        try:
            with open(output_filename, 'w', encoding='utf-8') as file:
                file.write(html_template)
            print(f"✅ Interactive D3.js visualization saved to '{output_filename}'")
            print(f"📊 Generated topology with {len(self.nodes)} nodes and {len(self.links)} links")
            print(f"🌐 Protocols: {', '.join(stats['protocols'])}")
            print(f"🚀 Open '{output_filename}' in your web browser to view the interactive topology!")
            return True
        except Exception as e:
            print(f"❌ Error saving HTML file: {e}")
            return False
    
    def generate_topology(self, input_file: str):
        """Generate complete topology from input file"""
        print(f"🔄 Parsing MML file: {input_file}")
        
        # Add central node
        self.add_central_node()
        
        # Parse the MML file
        if not self.parse_mml_file(input_file):
            return False
        
        # Generate interactive HTML
        output_file = input_file.replace('.txt', '_interactive.html')
        return self.generate_d3_html(output_file)


def main():
    if len(sys.argv) != 2:
        print("Usage: python spslinks_topo.py <mml_file>")
        print("Example: python spslinks_topo.py spsdmlinks.txt")
        print("Example: python spslinks_topo.py spsstp.txt")
        print("Example: python spslinks_topo.py merged_config.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    generator = SimplifiedTopoGeneratorV2()
    
    if generator.generate_topology(input_file):
        print("✅ Topology generation completed successfully!")
    else:
        print("❌ Topology generation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()


