"""
Export .uasset files to JSON format for analysis.
Uses raw binary parsing - no external packages required.

Usage: python uasset_to_json.py <path_to_uasset> [output.json]
       python uasset_to_json.py <folder_path> --batch   (exports all .uasset files in folder)
"""

import sys
import json
import struct
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

class UAssetReader:
    """Basic UE4 .uasset file reader."""
    
    # UE4 magic number
    PACKAGE_FILE_TAG = 0x9E2A83C1
    
    def __init__(self, uasset_path: str):
        self.uasset_path = uasset_path
        self.uexp_path = uasset_path.replace('.uasset', '.uexp')
        self.data = b''
        self.uexp_data = b''
        self.pos = 0
        self.names: List[str] = []
        self.imports: List[Dict] = []
        self.exports: List[Dict] = []
        
    def read(self) -> Dict[str, Any]:
        """Read and parse the uasset file."""
        with open(self.uasset_path, 'rb') as f:
            self.data = f.read()
        
        # Read .uexp if exists (contains bulk data)
        if os.path.exists(self.uexp_path):
            with open(self.uexp_path, 'rb') as f:
                self.uexp_data = f.read()
        
        self.pos = 0
        
        # Parse header
        header = self._read_header()
        
        # Parse name table
        self._read_names(header)
        
        # Parse import table
        self._read_imports(header)
        
        # Parse export table
        self._read_exports(header)
        
        # Try to extract string data from the file
        strings = self._extract_strings()
        
        return {
            "file": self.uasset_path,
            "header": header,
            "names": self.names,
            "imports": self.imports,
            "exports": self.exports,
            "extracted_strings": strings
        }
    
    def _read_uint32(self) -> int:
        val = struct.unpack('<I', self.data[self.pos:self.pos+4])[0]
        self.pos += 4
        return val
    
    def _read_int32(self) -> int:
        val = struct.unpack('<i', self.data[self.pos:self.pos+4])[0]
        self.pos += 4
        return val
    
    def _read_uint64(self) -> int:
        val = struct.unpack('<Q', self.data[self.pos:self.pos+8])[0]
        self.pos += 8
        return val
    
    def _read_int64(self) -> int:
        val = struct.unpack('<q', self.data[self.pos:self.pos+8])[0]
        self.pos += 8
        return val
    
    def _read_guid(self) -> str:
        data = self.data[self.pos:self.pos+16]
        self.pos += 16
        return data.hex()
    
    def _read_fstring(self) -> str:
        """Read an FString (length-prefixed string)."""
        length = self._read_int32()
        if length == 0:
            return ""
        
        # Negative length means UTF-16
        if length < 0:
            length = -length * 2
            try:
                s = self.data[self.pos:self.pos+length-2].decode('utf-16-le')
            except:
                s = f"<binary:{self.data[self.pos:self.pos+length].hex()}>"
            self.pos += length
        else:
            try:
                s = self.data[self.pos:self.pos+length-1].decode('utf-8')
            except:
                s = f"<binary:{self.data[self.pos:self.pos+length].hex()}>"
            self.pos += length
        
        return s
    
    def _read_header(self) -> Dict[str, Any]:
        """Read the package file header."""
        magic = self._read_uint32()
        if magic != self.PACKAGE_FILE_TAG:
            raise ValueError(f"Invalid magic number: {hex(magic)}")
        
        legacy_version = self._read_int32()
        legacy_ue3_version = self._read_int32()
        file_version_ue4 = self._read_int32()
        file_version_ue5 = self._read_int32()
        file_version_licensee = self._read_int32()
        
        # Custom versions array
        custom_version_count = self._read_int32()
        custom_versions = []
        for _ in range(custom_version_count):
            key = self._read_guid()
            version = self._read_int32()
            custom_versions.append({"key": key, "version": version})
        
        total_header_size = self._read_uint32()
        folder_name = self._read_fstring()
        package_flags = self._read_uint32()
        
        name_count = self._read_uint32()
        name_offset = self._read_uint32()
        
        # Soft object paths (UE4.26+)
        self.pos += 8  # Skip soft object paths count and offset
        
        # Localization ID
        localization_id = self._read_fstring() if file_version_ue4 >= 516 else ""
        
        # Gatherable text data
        self.pos += 8  # Skip gatherable text count and offset
        
        export_count = self._read_uint32()
        export_offset = self._read_uint32()
        import_count = self._read_uint32()
        import_offset = self._read_uint32()
        depends_offset = self._read_uint32()
        
        # More offsets
        soft_package_refs_count = self._read_uint32()
        soft_package_refs_offset = self._read_uint32()
        searchable_names_offset = self._read_uint32()
        thumbnail_table_offset = self._read_uint32()
        
        guid = self._read_guid()
        
        # Generations
        gen_count = self._read_uint32()
        generations = []
        for _ in range(gen_count):
            export_count_gen = self._read_int32()
            name_count_gen = self._read_int32()
            generations.append({"exports": export_count_gen, "names": name_count_gen})
        
        return {
            "magic": hex(magic),
            "file_version_ue4": file_version_ue4,
            "folder_name": folder_name,
            "package_flags": package_flags,
            "name_count": name_count,
            "name_offset": name_offset,
            "export_count": export_count,
            "export_offset": export_offset,
            "import_count": import_count,
            "import_offset": import_offset,
            "guid": guid
        }
    
    def _read_names(self, header: Dict):
        """Read the name table."""
        self.pos = header["name_offset"]
        
        for _ in range(header["name_count"]):
            name = self._read_fstring()
            # Skip hash
            if self.pos + 4 <= len(self.data):
                self._read_uint32()  # case insensitive hash
            self.names.append(name)
    
    def _read_imports(self, header: Dict):
        """Read the import table."""
        self.pos = header["import_offset"]
        
        for _ in range(header["import_count"]):
            class_package = self._read_int64()
            class_name = self._read_int64()
            outer_index = self._read_int32()
            object_name = self._read_int64()
            
            # Resolve names
            class_package_name = self._get_name(class_package) if class_package >= 0 else ""
            class_name_str = self._get_name(class_name) if class_name >= 0 else ""
            object_name_str = self._get_name(object_name) if object_name >= 0 else ""
            
            self.imports.append({
                "class_package": class_package_name,
                "class_name": class_name_str,
                "outer_index": outer_index,
                "object_name": object_name_str
            })
    
    def _read_exports(self, header: Dict):
        """Read the export table."""
        self.pos = header["export_offset"]
        
        for _ in range(header["export_count"]):
            class_index = self._read_int64()
            super_index = self._read_int64()
            template_index = self._read_int32()
            outer_index = self._read_int32()
            object_name = self._read_int64()
            
            save = self._read_uint32()  # ObjectFlags
            serial_size = self._read_int64()
            serial_offset = self._read_int64()
            
            forced_export = self._read_int32()
            not_for_client = self._read_int32()
            not_for_server = self._read_int32()
            
            package_guid = self._read_guid()
            package_flags = self._read_uint32()
            
            not_always_loaded_for_editor_game = self._read_int32()
            is_asset = self._read_int32()
            
            # First export class to load (UE4.26+)
            self.pos += 4
            
            # Additional data based on flags
            if serial_size > 0:
                # Skip public export hash
                self.pos += 8
            
            # Resolve names
            object_name_str = self._get_name(object_name) if object_name >= 0 else ""
            
            # Get class name from imports
            class_name = ""
            if class_index < 0:
                import_idx = -class_index - 1
                if import_idx < len(self.imports):
                    class_name = self.imports[import_idx].get("object_name", "")
            
            export_info = {
                "object_name": object_name_str,
                "class_name": class_name,
                "serial_size": serial_size,
                "serial_offset": serial_offset,
                "data": None
            }
            
            # Try to read export data
            if serial_size > 0 and serial_offset > 0:
                export_info["data"] = self._read_export_data(serial_offset, serial_size)
            
            self.exports.append(export_info)
    
    def _get_name(self, index: int) -> str:
        """Get a name from the name table."""
        # Name index is in lower 32 bits
        idx = index & 0xFFFFFFFF
        if idx < len(self.names):
            return self.names[idx]
        return f"<name_{idx}>"
    
    def _read_export_data(self, offset: int, size: int) -> Dict:
        """Read and parse export data."""
        # Data might be in .uexp file
        if self.uexp_data:
            # Offset is typically relative to end of header in uasset
            # For split packages, data is in uexp
            data = self.uexp_data
            # Adjust offset - uexp data starts after uasset header
            adj_offset = offset - len(self.data) + 4  # rough adjustment
            if adj_offset < 0:
                adj_offset = 0
            if adj_offset + size <= len(data):
                raw = data[adj_offset:adj_offset + size]
            else:
                raw = data[:min(size, len(data))]
        else:
            if offset + size <= len(self.data):
                raw = self.data[offset:offset + size]
            else:
                raw = self.data[offset:] if offset < len(self.data) else b''
        
        # Extract readable strings from the data
        strings = self._extract_strings_from_bytes(raw)
        
        return {
            "size": len(raw),
            "strings_found": strings[:100],  # Limit to first 100
            "hex_preview": raw[:256].hex() if raw else ""
        }
    
    def _extract_strings_from_bytes(self, data: bytes) -> List[str]:
        """Extract readable strings from binary data."""
        strings = []
        current = []
        
        for byte in data:
            if 32 <= byte < 127:  # Printable ASCII
                current.append(chr(byte))
            else:
                if len(current) >= 4:  # Minimum string length
                    strings.append(''.join(current))
                current = []
        
        if len(current) >= 4:
            strings.append(''.join(current))
        
        # Also try to find length-prefixed strings
        pos = 0
        while pos < len(data) - 4:
            length = struct.unpack('<i', data[pos:pos+4])[0]
            if 1 < length < 256:  # Reasonable string length
                try:
                    if pos + 4 + length <= len(data):
                        s = data[pos+4:pos+4+length-1].decode('utf-8', errors='ignore')
                        if s and all(c.isprintable() or c.isspace() for c in s):
                            if s not in strings and len(s) >= 3:
                                strings.append(s)
                except:
                    pass
            pos += 1
        
        return list(set(strings))
    
    def _extract_strings(self) -> List[str]:
        """Extract all readable strings from the file."""
        all_data = self.data + self.uexp_data
        return self._extract_strings_from_bytes(all_data)


def export_to_json(uasset_path: str, output_path: str = None) -> str:
    """Export a .uasset file to JSON."""
    print(f"Loading: {uasset_path}")
    
    try:
        reader = UAssetReader(uasset_path)
        result = reader.read()
    except Exception as e:
        print(f"  Warning: Could not fully parse: {e}")
        # Fallback: just extract strings
        result = {
            "file": uasset_path,
            "parse_error": str(e),
            "extracted_strings": []
        }
        try:
            with open(uasset_path, 'rb') as f:
                data = f.read()
            uexp_path = uasset_path.replace('.uasset', '.uexp')
            if os.path.exists(uexp_path):
                with open(uexp_path, 'rb') as f:
                    data += f.read()
            
            # Extract strings
            strings = []
            current = []
            for byte in data:
                if 32 <= byte < 127:
                    current.append(chr(byte))
                else:
                    if len(current) >= 4:
                        strings.append(''.join(current))
                    current = []
            result["extracted_strings"] = list(set(strings))
        except Exception as e2:
            result["string_extraction_error"] = str(e2)
    
    # Determine output path
    if output_path is None:
        output_path = str(Path(uasset_path).with_suffix('.json'))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"  Exported to: {output_path}")
    return output_path


def batch_export(folder_path: str):
    """Export all .uasset files in a folder."""
    folder = Path(folder_path)
    uasset_files = list(folder.glob('*.uasset'))  # Non-recursive for now
    
    print(f"Found {len(uasset_files)} .uasset files")
    
    output_folder = folder / "exported_json"
    output_folder.mkdir(exist_ok=True)
    
    results = []
    for uasset_file in uasset_files:
        try:
            output_file = output_folder / (uasset_file.stem + ".json")
            export_to_json(str(uasset_file), str(output_file))
            results.append({"file": str(uasset_file), "status": "success"})
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"file": str(uasset_file), "status": "error", "error": str(e)})
    
    # Write summary
    summary_path = output_folder / "_export_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nExported {sum(1 for r in results if r['status'] == 'success')}/{len(results)} files")
    print(f"Output folder: {output_folder}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single file:  python uasset_to_json.py <uasset_path> [output.json]")
        print("  Batch:        python uasset_to_json.py <folder_path> --batch")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if "--batch" in sys.argv:
        batch_export(target)
    else:
        output = sys.argv[2] if len(sys.argv) > 2 else None
        export_to_json(target, output)
