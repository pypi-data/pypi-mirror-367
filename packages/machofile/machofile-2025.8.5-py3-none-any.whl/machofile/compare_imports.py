#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from machofile import UniversalMachO

def compare_imports_and_symbols(file_path):
    """Compare imports and symbols between architectures in a FAT binary."""
    
    # Parse the Mach-O file
    macho = UniversalMachO(file_path=file_path)
    macho.parse()
    
    if not macho.is_fat:
        print("This is not a FAT binary. Only single architecture found.")
        return
    
    architectures = macho.get_architectures()
    print(f"Analyzing FAT binary with architectures: {', '.join(architectures)}")
    print("=" * 80)
    
    # Get imports for each architecture
    imports_by_arch = {}
    for arch in architectures:
        macho_instance = macho.get_macho_for_arch(arch)
        if macho_instance and hasattr(macho_instance, 'imported_functions'):
            imports = macho_instance.imported_functions
            if imports:
                # Flatten the imports (remove dylib grouping)
                flat_imports = []
                for dylib, funcs in imports.items():
                    for func in funcs:
                        flat_imports.append(func.strip().lower())
                imports_by_arch[arch] = sorted(set(flat_imports))
            else:
                imports_by_arch[arch] = []
        else:
            imports_by_arch[arch] = []
    
    # Get symbols for each architecture
    symbols_by_arch = {}
    for arch in architectures:
        macho_instance = macho.get_macho_for_arch(arch)
        if macho_instance:
            symbols = macho._extract_symbols_from_macho(macho_instance)
            symbols_by_arch[arch] = sorted(set(symbols))
        else:
            symbols_by_arch[arch] = []
    
    # Compare imports
    print("IMPORT COMPARISON")
    print("=" * 40)
    for i, arch1 in enumerate(architectures):
        for arch2 in architectures[i+1:]:
            print(f"\nComparing {arch1} vs {arch2} (Imports):")
            print("-" * 40)
            
            imports1 = set(imports_by_arch[arch1])
            imports2 = set(imports_by_arch[arch2])
            
            # Find differences
            only_in_arch1 = imports1 - imports2
            only_in_arch2 = imports2 - imports1
            common = imports1 & imports2
            
            print(f"Total imports in {arch1}: {len(imports1)}")
            print(f"Total imports in {arch2}: {len(imports2)}")
            print(f"Common imports: {len(common)}")
            print(f"Unique to {arch1}: {len(only_in_arch1)}")
            print(f"Unique to {arch2}: {len(only_in_arch2)}")
            
            if only_in_arch1:
                print(f"\nImports only in {arch1}:")
                for imp in sorted(only_in_arch1):
                    print(f"  - {imp}")
            
            if only_in_arch2:
                print(f"\nImports only in {arch2}:")
                for imp in sorted(only_in_arch2):
                    print(f"  - {imp}")
            
            if not only_in_arch1 and not only_in_arch2:
                print("  No differences found - imports are identical")
    
    # Compare symbols
    print(f"\n" + "=" * 80)
    print("SYMBOL COMPARISON")
    print("=" * 40)
    for i, arch1 in enumerate(architectures):
        for arch2 in architectures[i+1:]:
            print(f"\nComparing {arch1} vs {arch2} (Symbols):")
            print("-" * 40)
            
            symbols1 = set(symbols_by_arch[arch1])
            symbols2 = set(symbols_by_arch[arch2])
            
            # Find differences
            only_in_arch1 = symbols1 - symbols2
            only_in_arch2 = symbols2 - symbols1
            common = symbols1 & symbols2
            
            print(f"Total symbols in {arch1}: {len(symbols1)}")
            print(f"Total symbols in {arch2}: {len(symbols2)}")
            print(f"Common symbols: {len(common)}")
            print(f"Unique to {arch1}: {len(only_in_arch1)}")
            print(f"Unique to {arch2}: {len(only_in_arch2)}")
            
            if only_in_arch1:
                print(f"\nSymbols only in {arch1}:")
                for sym in sorted(only_in_arch1):
                    print(f"  - {sym}")
            
            if only_in_arch2:
                print(f"\nSymbols only in {arch2}:")
                for sym in sorted(only_in_arch2):
                    print(f"  - {sym}")
            
            if not only_in_arch1 and not only_in_arch2:
                print("  No differences found - symbols are identical")
    
    # Show combined analysis
    print(f"\n" + "=" * 80)
    print("COMBINED ANALYSIS")
    print("=" * 80)
    
    # Combined imports
    all_imports = set()
    for imports in imports_by_arch.values():
        all_imports.update(imports)
    
    print(f"Total unique imports across all architectures: {len(all_imports)}")
    
    # Combined symbols
    all_symbols = set()
    for symbols in symbols_by_arch.values():
        all_symbols.update(symbols)
    
    print(f"Total unique symbols across all architectures: {len(all_symbols)}")
    
    # Show some examples of symbols with architecture distribution
    print(f"\nSample symbols and their architecture distribution:")
    sample_symbols = sorted(all_symbols)[:10]  # Show first 10 symbols
    for sym in sample_symbols:
        archs_with_symbol = [arch for arch, symbols in symbols_by_arch.items() if sym in symbols]
        arch_list = ", ".join(archs_with_symbol)
        print(f"  - {sym} [{arch_list}]")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 compare_imports.py <macho_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    
    compare_imports_and_symbols(file_path) 