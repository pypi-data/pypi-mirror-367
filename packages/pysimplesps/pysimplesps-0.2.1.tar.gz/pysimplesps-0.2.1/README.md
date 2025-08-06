# 🔗 pysimplesps - SPS MML Configuration Parser & Topology Generator

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> 🚀 **Transform boring MML configurations into beautiful, interactive network topologies**

pysimplesps is a comprehensive Python library that parses Huawei SPS (Signaling Point Systems) MML configurations and generates structured JSON data or stunning D3.js topology visualizations. Say goodbye to boring MML dumps and hello to intuitive network understanding!

## ✨ Features

### 🎯 **Multi-Format Support**
- **Links Configuration** - Diameter, M2UA, M3UA, MTP links parsing
- **DMRT** - Diameter Routing configuration analysis  
- **AVPMED** - AVP Mediation rules and transformations

### 📊 **Output Formats**
- **JSON** - Structured data for programmatic analysis
- **D3.js Topology** - Interactive network visualizations
- **HTML** - Self-contained visualization files

### 🛠️ **Enterprise Features**
- Comprehensive error handling and validation
- Rich logging with loguru
- Extensive test coverage with pytest
- Module execution support (`python -m pysimplesps`)
- Programmatic API for integration

## 🚀 Quick Start

### Installation

```bash
# Install pysimplesps
pip install -e .

# Or install with development dependencies
pip install -e .[dev]
```

### Module Execution

```bash
# Run as Python module
python -m pysimplesps links links.txt
python -m pysimplesps dmrt dmrt1.txt dmrt2.txt
python -m pysimplesps avpmed avpmed.txt

# With options
python -m pysimplesps links links.txt -o output.json
python -m pysimplesps links links.txt -f topology -o network.html
python -m pysimplesps dmrt dmrt_host.txt dmrt_id.txt -v
```

### Programmatic Usage

```python
from pysimplesps import SPSUnifiedLinksParser, SPSDiameterRoutingParser, SPSAVPMediationParser

# Parse links configuration
parser = SPSUnifiedLinksParser("spsdmlinks.txt")
config = parser.parse_file()
parser.print_summary()
parser.save_json("output.json")

# Parse DMRT configuration
dmrt_parser = SPSDiameterRoutingParser()
dmrt_parser.parse_file("spsdmrt_host.txt")
dmrt_parser.parse_file("spsdmrt_id.txt")
dmrt_config = dmrt_parser.get_config()

# Parse AVPMED configuration
avp_parser = SPSAVPMediationParser("spsavpmediation.txt")
avp_config = avp_parser.parse_file()
```

## 📋 Command Reference

### Links Parser
```bash
python -m pysimplesps links <input_file> [OPTIONS]

Options:
  -o, --output PATH     Output file path
  -f, --format FORMAT   Output format: json|topology [default: json]
  -v, --verbose         Enable verbose logging
```

### DMRT Parser  
```bash
python -m pysimplesps dmrt <input_files>... [OPTIONS]

Options:
  -o, --output PATH     Output file path
  -f, --format FORMAT   Output format: json|topology [default: json]  
  -v, --verbose         Enable verbose logging
```

### AVPMED Parser
```bash
python -m pysimplesps avpmed <input_file> [OPTIONS]

Options:
  -o, --output PATH     Output file path
  -v, --verbose         Enable verbose logging
```

## 🎨 Examples

### Parse SPS Links Configuration

```bash
# Basic JSON output
python -m pysimplesps links spsdmlinks.txt

# Save to file with topology visualization
python -m pysimplesps links spsdmlinks.txt -f topology -o network_topology.html

# Verbose parsing with detailed logs
python -m pysimplesps links spsdmlinks.txt -v -o detailed_links.json
```

### Diameter Routing Analysis

```bash
# Parse multiple DMRT files
python -m pysimplesps dmrt spsdmrt_host.txt spsdmrt_id.txt spsdmrt_ip.txt

# Generate routing topology
python -m pysimplesps dmrt dmrt_config.txt -f topology -o routing_flow.html
```

### AVP Mediation Processing

```bash
# Parse mediation rules
python -m pysimplesps avpmed spsavpmediation.txt -o mediation_config.json
```

## 🏗️ Architecture

```
pysimplesps/
├── __main__.py         # 🚀 Module execution entry point
├── links2json.py       # 🔗 Links configuration parser  
├── links2topo.py       # 🌐 Links topology generator
├── dmrt2json.py        # 📡 DMRT configuration parser
├── dmrt2topo.py        # 🔄 DMRT topology generator  
├── avpmed2json.py      # 🔧 AVPMED configuration parser
└── __init__.py         # 📦 Package initialization
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pysimplesps --cov-report=html

# Run specific test categories
pytest -m unit         # Unit tests only
pytest -m integration  # Integration tests only
pytest -v              # Verbose output

# Run test script
python run_tests.py
```

## 📊 Sample Output

### JSON Structure
```json
{
  "diameter_peers": [...],
  "diameter_link_sets": [...], 
  "diameter_links": [...],
  "mtp_destination_points": [...],
  "metadata": {
    "parsed_at": "2025-08-03T...",
    "total_peers": 4,
    "total_link_sets": 6,
    "total_links": 12,
    "unique_ips": ["172.21.1.101", "172.21.1.102"],
    "unique_networks": ["172.21.1.0/24"]
  }
}
```

### Topology Features
- **Interactive D3.js visualizations**
- **Color-coded node types** (Diameter, MTP, M2UA, M3UA)
- **Drag-and-drop network exploration**
- **Connection details on hover**
- **Responsive design**

## 🎯 Supported MML Commands

### Links Configuration
- `ADD DMPEER` - Diameter peers
- `ADD DMLKS` - Diameter link sets  
- `ADD DMLNK` - Diameter links
- `ADD N7DSP` - MTP destination points
- `ADD N7LKS` - MTP link sets
- `ADD N7LNK` - MTP links

### DMRT Configuration  
- `ADD DMROUTERESULT` - Route results
- `ADD DMROUTEENTRANCE` - Route entrances
- `ADD DMROUTEEXIT` - Route exits
- `ADD DMROUTERULE_*` - Routing rules

### AVPMED Configuration
- `ADD MEDFILTER` - Mediation filters
- `ADD MEDACTION` - Mediation actions  
- `ADD MEDRULE` - Mediation rules
- `MOD DMPEER` - Peer assignments
- `MOD SFP` - Software parameters

## 🔧 Development

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/fxyzbtc/pysimplesps.git
cd pysimplesps

# Install in development mode
pip install -e .[dev]

# Run linting
ruff check pysimplesps/
ruff format pysimplesps/

# Type checking
mypy pysimplesps/
```

### Contributing Guidelines
1. 🍴 Fork the repository
2. 🌟 Create a feature branch (`git checkout -b feature/amazing-feature`)
3. 📝 Make your changes with tests
4. ✅ Run the test suite (`pytest`)
5. 🚀 Submit a pull request

## 📚 Documentation

- **API Documentation**: Coming soon
- **Wiki**: [https://deepwiki.com/fxyzbtc/pysimplesps](https://deepwiki.com/fxyzbtc/pysimplesps)
- **Examples**: Check the `tests/` directory for usage examples

## 🤝 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/fxyzbtc/pysimplesps/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/fxyzbtc/pysimplesps/discussions)
- 📧 **Email**: fxyzbtc@example.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ for telecommunications engineers
- Powered by Python 3.12+ and modern tooling
- Inspired by the need to make MML configurations more accessible

---

<div align="center">

**⭐ Star this repo if pysimplesps helps you visualize your networks! ⭐**

Made with 🔥 by [fxyzbtc](https://github.com/fxyzbtc)

</div>

## 🎨 Examples

### Parse SPS Links Configuration

```bash
# Basic JSON output
pysimplesps links spsdmlinks.txt

# Save to file with topology visualization
pysimplesps links spsdmlinks.txt -f topology -o network_topology.html

# Verbose parsing with detailed logs
pysimplesps links spsdmlinks.txt -v -o detailed_links.json
```

### Diameter Routing Analysis

```bash
# Parse multiple DMRT files
pysimplesps dmrt spsdmrt_host.txt spsdmrt_id.txt spsdmrt_ip.txt

# Generate routing topology
pysimplesps dmrt dmrt_config.txt -f topology -o routing_flow.html
```

### AVP Mediation Processing

```bash
# Parse mediation rules
pysimplesps avpmed spsavpmediation.txt -o mediation_config.json
```

## 🏗️ Architecture

```
pysimplesps/
├── cli.py              # 🎯 Main CLI interface with Typer
├── links2json.py       # 🔗 Links configuration parser  
├── links2topo.py       # 🌐 Links topology generator
├── dmrt2json.py        # 📡 DMRT configuration parser
├── dmrt2topo.py        # 🔄 DMRT topology generator  
├── avpmed2json.py      # 🔧 AVPMED configuration parser
├── __main__.py         # 🚀 Module execution entry point
└── __init__.py         # 📦 Package initialization
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pysimplesps --cov-report=html

# Run specific test categories
pytest -m unit         # Unit tests only
pytest -m integration  # Integration tests only
pytest -v              # Verbose output
```

## 📊 Sample Output

### JSON Structure
```json
{
  "diameter_peers": [...],
  "diameter_link_sets": [...], 
  "diameter_links": [...],
  "mtp_destination_points": [...],
  "metadata": {
    "parsed_at": "2025-08-03T...",
    "total_peers": 4,
    "total_link_sets": 6,
    "total_links": 12,
    "unique_ips": ["172.21.1.101", "172.21.1.102"],
    "unique_networks": ["172.21.1.0/24"]
  }
}
```

### Topology Features
- **Interactive D3.js visualizations**
- **Color-coded node types** (Diameter, MTP, M2UA, M3UA)
- **Drag-and-drop network exploration**
- **Connection details on hover**
- **Responsive design**

## 🎯 Supported MML Commands

### Links Configuration
- `ADD DMPEER` - Diameter peers
- `ADD DMLKS` - Diameter link sets  
- `ADD DMLNK` - Diameter links
- `ADD N7DSP` - MTP destination points
- `ADD N7LKS` - MTP link sets
- `ADD N7LNK` - MTP links

### DMRT Configuration  
- `ADD DMROUTERESULT` - Route results
- `ADD DMROUTEENTRANCE` - Route entrances
- `ADD DMROUTEEXIT` - Route exits
- `ADD DMROUTERULE_*` - Routing rules

### AVPMED Configuration
- `ADD MEDFILTER` - Mediation filters
- `ADD MEDACTION` - Mediation actions  
- `ADD MEDRULE` - Mediation rules
- `MOD DMPEER` - Peer assignments
- `MOD SFP` - Software parameters

## 🔧 Development

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/fxyzbtc/pysimplesps.git
cd pysimplesps

# Install in development mode
pip install -e .[dev]

# Run linting
ruff check pysimplesps/
ruff format pysimplesps/

# Type checking
mypy pysimplesps/
```

### Contributing Guidelines
1. 🍴 Fork the repository
2. 🌟 Create a feature branch (`git checkout -b feature/amazing-feature`)
3. 📝 Make your changes with tests
4. ✅ Run the test suite (`pytest`)
5. 🚀 Submit a pull request

## 📚 Documentation

- **API Documentation**: Coming soon
- **Wiki**: [https://deepwiki.com/fxyzbtc/pysimplesps](https://deepwiki.com/fxyzbtc/pysimplesps)
- **Examples**: Check the `tests/` directory for usage examples

## 🤝 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/fxyzbtc/pysimplesps/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/fxyzbtc/pysimplesps/discussions)
- 📧 **Email**: fxyzbtc@example.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ for telecommunications engineers
- Powered by Python 3.12+ and modern tooling
- Inspired by the need to make MML configurations more accessible

---

<div align="center">

**⭐ Star this repo if pysimplesps helps you visualize your networks! ⭐**

Made with 🔥 by [fxyzbtc](https://github.com/fxyzbtc)

</div>
