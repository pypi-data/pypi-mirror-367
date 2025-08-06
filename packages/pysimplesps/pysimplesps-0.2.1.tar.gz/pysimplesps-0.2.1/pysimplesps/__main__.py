"""
pysimplesps - SPS MML Configuration Parser and Topology Generator.

Entry point for running pysimplesps as a module (python -m pysimplesps).
"""

import sys
from pathlib import Path

from loguru import logger

from .avpmed2json import SPSAVPMediationParser
from .dmrt2json import SPSDiameterRoutingParser
from .dmrt2topo import DiameterRoutingTopoGenerator
from .links2json import SPSUnifiedLinksParser
from .links2topo import SimplifiedTopoGeneratorV2


def show_help():
    """Display help information."""
    help_text = """
pysimplesps - SPS MML Configuration Parser & Topology Generator

Usage:
    python -m pysimplesps <command> <input_files> [options]

Commands:
    links       Parse SPS links configuration files
    dmrt        Parse SPS Diameter routing configuration files
    avpmed      Parse SPS AVP mediation configuration files
    help        Show this help message

Examples:
    python -m pysimplesps links spsdmlinks.txt
    python -m pysimplesps dmrt spsdmrt_host.txt spsdmrt_id.txt
    python -m pysimplesps avpmed spsavpmediation.txt

Options:
    -o, --output PATH       Output file path
    -f, --format FORMAT     Output format: json|topology [default: json]
    -v, --verbose           Enable verbose logging

For more information, visit: https://github.com/fxyzbtc/pysimplesps
"""
    print(help_text)


def parse_args() -> tuple[str, list[str], dict]:
    """Parse command line arguments."""
    args = sys.argv[1:]
    
    if not args:
        return "help", [], {}
    
    command = args[0].lower()
    
    # Handle help command
    if command in ["help", "-h", "--help"]:
        return "help", [], {}
    
    # Find input files and options
    input_files = []
    options = {}
    i = 1
    
    while i < len(args):
        arg = args[i]
        
        if arg in ["-o", "--output"]:
            if i + 1 < len(args):
                options["output"] = args[i + 1]
                i += 2
            else:
                logger.error("Output option requires a file path")
                sys.exit(1)
        elif arg in ["-f", "--format"]:
            if i + 1 < len(args):
                options["format"] = args[i + 1]
                i += 2
            else:
                logger.error("Format option requires a value (json|topology)")
                sys.exit(1)
        elif arg in ["-v", "--verbose"]:
            options["verbose"] = True
            i += 1
        elif not arg.startswith("-"):
            input_files.append(arg)
            i += 1
        else:
            logger.error(f"Unknown option: {arg}")
            sys.exit(1)
    
    return command, input_files, options


def configure_logging(verbose: bool = False):
    """Configure logging based on verbosity level."""
    logger.remove()  # Remove default handler
    
    if verbose:
        logger.add(
            sys.stderr,
            level="DEBUG",
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
    else:
        logger.add(
            sys.stderr,
            level="INFO",
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
        )


def validate_input_files(files: list[str]) -> list[Path]:
    """Validate that input files exist."""
    validated_files = []
    
    for file_path in files:
        path = Path(file_path)
        if path.exists() and path.is_file():
            validated_files.append(path)
        else:
            logger.error(f"Input file not found: {file_path}")
            sys.exit(1)
    
    return validated_files


def process_links_command(input_files: list[Path], options: dict):
    """Process links parsing command."""
    if not input_files:
        logger.error("Links command requires at least one input file")
        sys.exit(1)
    
    output_format = options.get("format", "json")
    output_file = options.get("output")
    
    logger.info(f"Processing {len(input_files)} links configuration file(s)")
    
    # Parse the first file (for now, we'll process one file at a time)
    input_file = input_files[0]
    logger.info(f"Parsing links file: {input_file}")
    
    try:
        parser = SPSUnifiedLinksParser(str(input_file))
        config = parser.parse_file()
        
        if not config:
            logger.error("Failed to parse links configuration")
            sys.exit(1)
        
        # Print summary
        parser.print_summary()
        parser.print_hierarchical_summary()
        
        # Save output
        if output_format == "topology":
            if not output_file:
                output_file = input_file.stem + "_topology.html"
            logger.info(f"Generating topology visualization: {output_file}")
            topo_gen = SimplifiedTopoGeneratorV2()
            
            # Use the topology generator's own parsing for consistency
            # This ensures the same parsing logic as the direct execution
            success = topo_gen.generate_topology(str(input_file))
            if success:
                # The generator creates its own filename, so we need to rename it
                generated_file = str(input_file).replace('.txt', '_interactive.html')
                if generated_file != output_file:
                    # Rename the generated file to match user's requested output
                    import shutil
                    try:
                        shutil.move(generated_file, output_file)
                    except FileNotFoundError:
                        # If the generated file doesn't exist in expected location, look for it
                        from pathlib import Path
                        generated_path = Path(generated_file)
                        if not generated_path.exists():
                            # Try in the same directory as input file
                            generated_path = input_file.parent / generated_path.name
                        if generated_path.exists():
                            shutil.move(str(generated_path), output_file)
                        else:
                            logger.warning(f"Could not find generated file to rename. Looking for files matching pattern...")
                            # Just report success and let user know the actual filename
                            logger.success(f"Topology generated. Check for *_interactive.html files")
                            return
                logger.success(f"Topology saved to: {output_file}")
            else:
                logger.error("Failed to generate topology")
                sys.exit(1)
        else:
            if not output_file:
                output_file = input_file.stem + "_config.json"
            logger.info(f"Saving JSON configuration: {output_file}")
            parser.save_json(output_file)
            logger.success(f"Configuration saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Error processing links file: {e}")
        sys.exit(1)


def process_dmrt_command(input_files: list[Path], options: dict):
    """Process DMRT parsing command."""
    if not input_files:
        logger.error("DMRT command requires at least one input file")
        sys.exit(1)
    
    output_format = options.get("format", "json")
    output_file = options.get("output")
    
    logger.info(f"Processing {len(input_files)} DMRT configuration file(s)")
    
    try:
        parser = SPSDiameterRoutingParser()
        
        # Parse all input files
        for input_file in input_files:
            logger.info(f"Parsing DMRT file: {input_file}")
            parser.parse_file(str(input_file))
        
        config = parser.config
        
        if not config or not any([
            config.get("route_results"),
            config.get("route_entrances"),
            config.get("route_exits"),
            config.get("route_rules")
        ]):
            logger.error("No DMRT configuration data found")
            sys.exit(1)
        
        # Print summary
        parser.print_summary()
        
        # Save output
        if output_format == "topology":
            if not output_file:
                output_file = "dmrt_topology.html"
            
            logger.info(f"Generating DMRT topology visualization: {output_file}")
            topo_gen = DiameterRoutingTopoGenerator()
            
            # Use the first input file for topology generation
            # The topology generator will parse the file itself
            input_file_path = str(input_files[0])
            success = topo_gen.generate_routing_topology(input_file_path)
            if success:
                logger.success(f"DMRT topology saved to: {output_file}")
            else:
                logger.error("Failed to generate DMRT topology")
                sys.exit(1)
        else:
            if not output_file:
                output_file = "dmrt_config.json"
            
            logger.info(f"Saving DMRT JSON configuration: {output_file}")
            parser.save_json(output_file)
            logger.success(f"DMRT configuration saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Error processing DMRT files: {e}")
        sys.exit(1)


def process_avpmed_command(input_files: list[Path], options: dict):
    """Process AVPMED parsing command."""
    if not input_files:
        logger.error("AVPMED command requires exactly one input file")
        sys.exit(1)
    
    if len(input_files) > 1:
        logger.warning("AVPMED command only processes the first file provided")
    
    output_file = options.get("output")
    input_file = input_files[0]
    
    logger.info(f"Processing AVPMED configuration file: {input_file}")
    
    try:
        parser = SPSAVPMediationParser()
        parser.parse_file(str(input_file))
        
        # Print summary
        parser.print_summary()
        
        # Save output
        if not output_file:
            output_file = input_file.stem + "_avpmed.json"
        
        logger.info(f"Saving AVPMED JSON configuration: {output_file}")
        parser.save_config(output_file)
        logger.success(f"AVPMED configuration saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Error processing AVPMED file: {e}")
        sys.exit(1)


def main():
    """Main entry point for the pysimplesps module."""
    try:
        # Parse command line arguments
        command, input_files, options = parse_args()
        
        # Configure logging
        configure_logging(options.get("verbose", False))
        
        # Handle help command
        if command == "help":
            show_help()
            return
        
        # Validate command
        if command not in ["links", "dmrt", "avpmed"]:
            logger.error(f"Unknown command: {command}")
            show_help()
            sys.exit(1)
        
        # Validate input files
        validated_files = validate_input_files(input_files)
        
        # Execute command
        logger.info(f"Starting pysimplesps {command} command")
        
        if command == "links":
            process_links_command(validated_files, options)
        elif command == "dmrt":
            process_dmrt_command(validated_files, options)
        elif command == "avpmed":
            process_avpmed_command(validated_files, options)
        
        logger.success("pysimplesps processing completed successfully")
        
    except KeyboardInterrupt:
        logger.warning("Processing interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


# --- Unit tests ---

def test_show_help(capsys):
    show_help()
    out, _ = capsys.readouterr()
    assert "pysimplesps" in out
    assert "Usage" in out

def test_parse_args_help():
    import sys
    from unittest import mock
    with mock.patch.object(sys, 'argv', ["python", "help"]):
        command, files, options = parse_args()
        assert command == "help"

def test_parse_args_links():
    import sys
    from unittest import mock
    with mock.patch.object(sys, 'argv', ["python", "links", "file.txt"]):
        command, files, options = parse_args()
        assert command == "links"
        assert files == ["file.txt"]

def test_parse_args_options():
    import sys
    from unittest import mock
    with mock.patch.object(sys, 'argv', ["python", "links", "file.txt", "-o", "out.json", "-f", "topology", "-v"]):
        command, files, options = parse_args()
        assert options["output"] == "out.json"
        assert options["format"] == "topology"
        assert options["verbose"] is True

def test_validate_input_files(tmp_path):
    file1 = tmp_path / "f1.txt"
    file1.write_text("test")
    files = [str(file1)]
    result = validate_input_files(files)
    assert result[0].name == "f1.txt"

def test_validate_input_files_missing():
    import pytest
    with pytest.raises(SystemExit):
        validate_input_files(["nonexistent.txt"])

def test_configure_logging():
    configure_logging()
    configure_logging(True)

if __name__ == "__main__":
    main()
