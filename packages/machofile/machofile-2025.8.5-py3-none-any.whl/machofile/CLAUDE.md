# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **machofile**, a pure Python module for parsing Mach-O binary files (the executable format used by macOS, iOS, watchOS, and tvOS). It's inspired by Ero Carrera's pefile module and aims to provide comprehensive Mach-O analysis capabilities without external dependencies.

## Development Commands

### Running the Tool
The main module serves as both a Python library and a CLI tool:

```bash
# Run as CLI with all analysis options
python3 machofile.py -a -f /path/to/binary

# Run with JSON output
python3 machofile.py -j -a -f /path/to/binary

# Run specific analysis types
python3 machofile.py -g -f /path/to/binary        # General info
python3 machofile.py -hdr -f /path/to/binary      # Header info  
python3 machofile.py -l -f /path/to/binary        # Load commands
python3 machofile.py -seg -f /path/to/binary      # Segments
python3 machofile.py -d -f /path/to/binary        # Dylib info
python3 machofile.py -sim -f /path/to/binary      # Similarity hashes
python3 machofile.py -sig -f /path/to/binary      # Code signature
python3 machofile.py -ep -f /path/to/binary       # Entry point
python3 machofile.py -i -f /path/to/binary        # Imports
python3 machofile.py -e -f /path/to/binary        # Exports
python3 machofile.py -v -f /path/to/binary        # Version info

# Architecture-specific analysis (for FAT/Universal binaries)
python3 machofile.py --arch x86_64 -sim -f /path/to/fat_binary
python3 machofile.py --arch arm64 -sim -f /path/to/fat_binary
```

### Testing
Use the test samples in `test_data/` directory for development and validation:
```bash
python3 machofile.py -a -f test_data/curl
python3 machofile.py -j -sim -f test_data/dec750b9d596b14aeab1ed6f6d6d370022443ceceb127e7d2468b903c2d9477a
```

## Code Architecture

### Core Class Structure
- **UniversalMachO**: Top-level class that handles both single-architecture and FAT/Universal binaries
  - Initialized with either `file_path` or `data` parameter
  - Call `parse()` method to begin parsing process
  - Provides unified interface for both single and multi-architecture binaries
  - Automatically detects FAT binaries and creates MachO instances for each architecture

- **MachO**: Architecture-specific class that handles individual Mach-O parsing
  - Contains all parsed data as instance attributes for a single architecture
  - Handles all the detailed parsing operations

### Key Features of UniversalMachO
- **FAT Binary Support**: Automatically detects and parses Universal/FAT binaries containing multiple architectures
- **Architecture Management**: Provides methods to get specific architectures or iterate over all
- **Unified API**: Same interface works for both single-arch and multi-arch binaries
- **Combined Similarity Hashes**: For FAT binaries, generates combined hashes that merge data from all architectures

### Key Parsing Methods
- `parse()`: Main entry point that orchestrates all parsing
- `parse_all_load_commands()`: Processes Mach-O load commands
- `parse_code_signature()`: Handles code signing information and certificates
- `parse_export_trie()`: Parses export trie for symbol information

### Data Extraction Methods (UniversalMachO)
All methods support `formatted=False` (default) for raw data and `formatted=True` for human-readable output:

- `get_general_info(arch=None, formatted=False)`: File metadata (hashes, size, etc.)
- `get_macho_header(arch=None, formatted=False)`: Mach-O header structure
- `get_imported_functions(arch=None, formatted=False)`: Functions imported from dylibs
- `get_exported_symbols(arch=None, formatted=False)`: Exported symbols and functions
- `get_load_commands(arch=None, formatted=False)`: Load command structures
- `get_load_commands_set(arch=None, formatted=False)`: Set of unique load command types
- `get_segments(arch=None, formatted=False)`: File segment information
- `get_dylib_commands(arch=None, formatted=False)`: Dynamic library commands
- `get_dylib_names(arch=None, formatted=False)`: Dynamic library names
- `get_uuid(arch=None, formatted=False)`: UUID information
- `get_entry_point(arch=None, formatted=False)`: Entry point information
- `get_version_info(arch=None, formatted=False)`: Version information
- `get_code_signature_info(arch=None, formatted=False)`: Code signature details
- `get_similarity_hashes(arch=None, formatted=False)`: Various hashes for similarity analysis
- `get_dylib_hash(arch=None, formatted=False)`: Dylib hash for specific architecture or combined
- `get_import_hash(arch=None, formatted=False)`: Import hash for specific architecture or combined
- `get_export_hash(arch=None, formatted=False)`: Export hash for specific architecture or combined
- `get_entitlement_hash(arch=None, formatted=False)`: Entitlement hash for specific architecture or combined
- `get_symhash(arch=None, formatted=False)`: Symhash for specific architecture or combined
- `get_architectures()`: List of architectures in the binary
- `get_macho_for_arch(arch_name)`: Get MachO instance for specific architecture

### Similarity Hashes
The module provides comprehensive similarity hashing for malware analysis:

#### Individual Architecture Hashes
- **dylib_hash**: MD5 of sorted, deduplicated dynamic library names
- **import_hash**: MD5 of sorted, deduplicated imported function names
- **export_hash**: MD5 of sorted, deduplicated exported symbol names
- **entitlement_hash**: MD5 of sorted, deduplicated entitlement names and array values (following YARA-X pattern)
- **symhash**: MD5 of sorted, deduplicated external undefined symbols (following Anomali Labs/CRITS logic)

#### Combined Hashes (FAT Binaries Only)
For Universal/FAT binaries, the tool generates **combined similarity hashes** that merge data from all architectures:
- **combined.dylib_hash**: All dylibs from all architectures, deduplicated
- **combined.import_hash**: All imports from all architectures, deduplicated
- **combined.export_hash**: All exports from all architectures, deduplicated
- **combined.entitlement_hash**: All entitlements from all architectures, deduplicated
- **combined.symhash**: All symbols from all architectures, deduplicated

These combined hashes are valuable for malware analysis as they enable cross-architecture detection of the same malware family, reducing false negatives when comparing samples compiled for different architectures.

### Key Features Supported
- Both 32-bit and 64-bit Mach-O files, as well as FAT/Universal binaries
- All major load command types (LC_SEGMENT*, LC_DYLIB*, LC_SYMTAB, etc.)
- Code signature parsing including certificates and entitlements
- Import/export analysis with hash generation
- Entitlement analysis with hash generation (following YARA-X pattern)
- Segment entropy calculation
- UUID and version information extraction
- Cross-architecture similarity analysis for FAT binaries

### Instance Attributes (MachO class, set after parsing)
- `header`: Mach-O header information
- `load_commands`: List of load command structures
- `segments`: File segment information
- `dylib_commands`: Dynamic library commands
- `imported_functions`: Dictionary of imported functions by dylib
- `exported_symbols`: Dictionary of exported symbols
- `code_signature_info`: Code signing and certificate information

### Instance Properties (UniversalMachO class)
- `entitlements`: Access entitlements from code signature info for all architectures

### Formatted API Support
All data extraction methods now support a `formatted` parameter:
- `formatted=False` (default): Returns raw binary values
- `formatted=True`: Returns human-readable formatted values

**Fields that benefit from formatting:**
- Headers: Magic numbers, CPU types, file types, flags
- Load commands: Command type names instead of numbers
- Version info: Platform names instead of numbers

**Fields that are identical in both modes:**
- General info, UUID, imports, exports, similarity hashes, segments, dylib info, entry point, code signature info

### File Structure
The entire module is contained in a single file (`machofile.py`) with:
- Extensive Mach-O structure definitions and constants at the top
- `UniversalMachO` class for handling both single and multi-architecture binaries
- `MachO` class implementation for individual architecture parsing
- JSON serialization helpers and data collection functions
- CLI argument parsing and output formatting at the bottom
- No external dependencies beyond Python standard library

### Development Notes
- The module is completely self-contained with no external dependencies
- Endianness independent and works across platforms
- Supports both single-architecture and multi-architecture (FAT/Universal) binaries
- Combined similarity hashes provide enhanced malware analysis capabilities
- Entitlement hash implementation follows YARA-X pattern for compatibility
- Formatted API provides human-readable output for all data types
- Backward compatible - all existing code continues to work unchanged
- Archive folder contains the old CLI-only version for reference
- Current version: 2025.08.05

### JSON Output
The tool supports JSON output mode with `-j` flag:
- Raw data output with `--raw` flag (preserves original data types)
- Formatted output by default (human-readable formatting applied)
- Architecture-specific filtering with `--arch` parameter
- Complete data structure serialization for programmatic use
- Consistent formatting across all data types (headers, load commands, version info, etc.)