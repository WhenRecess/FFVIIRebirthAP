"""
UE4.26 DataTable Parser for FFVII Rebirth
Extracts structured data from .uasset DataTable files.

Usage: python uasset_datatable_parser.py <uasset_path> [output.json]
       python uasset_datatable_parser.py <folder_path> --batch
"""

import sys
import json
import struct
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, BinaryIO

class UE4DataTableParser:
    """Parser for UE4 DataTable .uasset files."""
    
    PACKAGE_FILE_TAG = 0x9E2A83C1
    
    def __init__(self, uasset_path: str):
        self.uasset_path = uasset_path
        self.uexp_path = uasset_path.replace('.uasset', '.uexp')
        self.data = b''
        self.uexp_data = b''
        self.names: List[str] = []
        self.imports: List[Dict] = []
        self.exports: List[Dict] = []
        self.name_offset = 0
        self.export_offset = 0
        self.import_offset = 0
        self.total_header_size = 0
        self.bulk_data_start = 0
        
    def read_file(self) -> Dict[str, Any]:
        """Read and parse the uasset file."""
        with open(self.uasset_path, 'rb') as f:
            self.data = f.read()
        
        if os.path.exists(self.uexp_path):
            with open(self.uexp_path, 'rb') as f:
                self.uexp_data = f.read()
        
        result = {
            "file": self.uasset_path,
            "names": [],
            "rows": [],
            "raw_data": {}
        }
        
        try:
            # Parse the package header
            header_info = self._parse_header()
            result["header"] = header_info
            
            # Parse name table
            self.names = self._parse_name_table()
            result["names"] = self.names
            
            # Parse imports
            self.imports = self._parse_import_table()
            result["imports"] = self.imports
            
            # Parse exports
            self.exports = self._parse_export_table()
            result["exports_meta"] = self.exports
            
            # Now try to parse DataTable content from uexp
            if self.uexp_data:
                rows = self._parse_datatable_content()
                result["rows"] = rows
            
        except Exception as e:
            result["parse_error"] = str(e)
            # Fallback to enhanced string extraction
            result["extracted_data"] = self._enhanced_extraction()
        
        return result
    
    def _read_uint8(self, data: bytes, pos: int) -> Tuple[int, int]:
        return data[pos], pos + 1
    
    def _read_int32(self, data: bytes, pos: int) -> Tuple[int, int]:
        val = struct.unpack('<i', data[pos:pos+4])[0]
        return val, pos + 4
    
    def _read_uint32(self, data: bytes, pos: int) -> Tuple[int, int]:
        val = struct.unpack('<I', data[pos:pos+4])[0]
        return val, pos + 4
    
    def _read_int64(self, data: bytes, pos: int) -> Tuple[int, int]:
        val = struct.unpack('<q', data[pos:pos+8])[0]
        return val, pos + 8
    
    def _read_uint64(self, data: bytes, pos: int) -> Tuple[int, int]:
        val = struct.unpack('<Q', data[pos:pos+8])[0]
        return val, pos + 8
    
    def _read_float(self, data: bytes, pos: int) -> Tuple[float, int]:
        val = struct.unpack('<f', data[pos:pos+4])[0]
        return val, pos + 4
    
    def _read_double(self, data: bytes, pos: int) -> Tuple[float, int]:
        val = struct.unpack('<d', data[pos:pos+8])[0]
        return val, pos + 8
    
    def _read_guid(self, data: bytes, pos: int) -> Tuple[str, int]:
        guid_bytes = data[pos:pos+16]
        return guid_bytes.hex(), pos + 16
    
    def _read_fstring(self, data: bytes, pos: int) -> Tuple[str, int]:
        """Read a length-prefixed FString."""
        if pos + 4 > len(data):
            return "", pos
        
        length, pos = self._read_int32(data, pos)
        
        if length == 0:
            return "", pos
        
        if length < 0:  # UTF-16
            byte_length = -length * 2
            if pos + byte_length > len(data):
                return "", pos
            try:
                s = data[pos:pos+byte_length-2].decode('utf-16-le')
            except:
                s = ""
            return s, pos + byte_length
        else:  # ASCII/UTF-8
            if pos + length > len(data):
                return "", pos
            try:
                s = data[pos:pos+length-1].decode('utf-8', errors='replace')
            except:
                s = ""
            return s, pos + length
    
    def _read_fname(self, data: bytes, pos: int) -> Tuple[str, int]:
        """Read an FName (index into name table + number)."""
        if pos + 8 > len(data):
            return "<invalid>", pos
        
        name_idx, pos = self._read_int32(data, pos)
        name_num, pos = self._read_int32(data, pos)
        
        if 0 <= name_idx < len(self.names):
            name = self.names[name_idx]
            if name_num > 0:
                name = f"{name}_{name_num-1}"
            return name, pos
        return f"<name_{name_idx}>", pos
    
    def _parse_header(self) -> Dict[str, Any]:
        """Parse the package file header."""
        pos = 0
        data = self.data
        
        magic, pos = self._read_uint32(data, pos)
        if magic != self.PACKAGE_FILE_TAG:
            raise ValueError(f"Invalid magic: {hex(magic)}")
        
        legacy_version, pos = self._read_int32(data, pos)
        legacy_ue3, pos = self._read_int32(data, pos)
        file_version_ue4, pos = self._read_int32(data, pos)
        file_version_ue5, pos = self._read_int32(data, pos)
        file_version_licensee, pos = self._read_int32(data, pos)
        
        # Custom versions
        custom_version_count, pos = self._read_int32(data, pos)
        for _ in range(custom_version_count):
            pos += 20  # GUID (16) + version (4)
        
        self.total_header_size, pos = self._read_uint32(data, pos)
        folder_name, pos = self._read_fstring(data, pos)
        package_flags, pos = self._read_uint32(data, pos)
        
        name_count, pos = self._read_uint32(data, pos)
        self.name_offset, pos = self._read_uint32(data, pos)
        
        # Soft object paths (UE4.26+)
        soft_obj_count, pos = self._read_int32(data, pos)
        soft_obj_offset, pos = self._read_int32(data, pos)
        
        # Gatherable text
        gather_count, pos = self._read_int32(data, pos)
        gather_offset, pos = self._read_int32(data, pos)
        
        export_count, pos = self._read_uint32(data, pos)
        self.export_offset, pos = self._read_uint32(data, pos)
        import_count, pos = self._read_uint32(data, pos)
        self.import_offset, pos = self._read_uint32(data, pos)
        depends_offset, pos = self._read_uint32(data, pos)
        
        # More offsets
        soft_pkg_count, pos = self._read_uint32(data, pos)
        soft_pkg_offset, pos = self._read_uint32(data, pos)
        searchable_offset, pos = self._read_int32(data, pos)
        thumbnail_offset, pos = self._read_uint32(data, pos)
        
        guid, pos = self._read_guid(data, pos)
        
        # Generations
        gen_count, pos = self._read_uint32(data, pos)
        for _ in range(gen_count):
            pos += 8  # export count + name count
        
        # Engine version
        pos += 4  # Saved by engine version
        
        # Compatible engine version
        pos += 20  # major(2) + minor(2) + patch(2) + changelist(4) + branch string
        
        self.bulk_data_start = self.total_header_size
        
        return {
            "file_version_ue4": file_version_ue4,
            "name_count": name_count,
            "export_count": export_count,
            "import_count": import_count
        }
    
    def _parse_name_table(self) -> List[str]:
        """Parse the name table."""
        names = []
        pos = self.name_offset
        data = self.data
        
        # Read names until we hit export offset or run out
        while pos < self.import_offset and pos < len(data) - 4:
            try:
                name, pos = self._read_fstring(data, pos)
                if not name:
                    break
                # Skip hash (UE4 stores case-insensitive hash after name)
                if pos + 4 <= len(data):
                    pos += 4
                names.append(name)
            except:
                break
        
        return names
    
    def _parse_import_table(self) -> List[Dict]:
        """Parse the import table."""
        imports = []
        pos = self.import_offset
        data = self.data
        
        while pos < self.export_offset and pos < len(data) - 32:
            try:
                class_package, pos = self._read_int64(data, pos)
                class_name, pos = self._read_int64(data, pos)
                outer_index, pos = self._read_int32(data, pos)
                object_name, pos = self._read_int64(data, pos)
                
                # For UE4.26+
                if pos + 4 <= len(data):
                    pos += 4  # Optional
                
                imports.append({
                    "class_package": self._get_name(class_package),
                    "class_name": self._get_name(class_name),
                    "object_name": self._get_name(object_name)
                })
            except:
                break
        
        return imports
    
    def _parse_export_table(self) -> List[Dict]:
        """Parse the export table."""
        exports = []
        pos = self.export_offset
        data = self.data
        
        while pos < len(data) - 64:
            try:
                class_idx, pos = self._read_int64(data, pos)
                super_idx, pos = self._read_int64(data, pos)
                template_idx, pos = self._read_int32(data, pos)
                outer_idx, pos = self._read_int32(data, pos)
                object_name, pos = self._read_int64(data, pos)
                
                obj_flags, pos = self._read_uint32(data, pos)
                serial_size, pos = self._read_int64(data, pos)
                serial_offset, pos = self._read_int64(data, pos)
                
                forced_export, pos = self._read_int32(data, pos)
                not_for_client, pos = self._read_int32(data, pos)
                not_for_server, pos = self._read_int32(data, pos)
                
                pkg_guid, pos = self._read_guid(data, pos)
                pkg_flags, pos = self._read_uint32(data, pos)
                
                not_always, pos = self._read_int32(data, pos)
                is_asset, pos = self._read_int32(data, pos)
                
                # First export class to load
                pos += 4
                
                # Get class name
                class_name = ""
                if class_idx < 0:
                    imp_idx = -class_idx - 1
                    if imp_idx < len(self.imports):
                        class_name = self.imports[imp_idx].get("object_name", "")
                
                exports.append({
                    "object_name": self._get_name(object_name),
                    "class_name": class_name,
                    "serial_size": serial_size,
                    "serial_offset": serial_offset
                })
                
                if serial_size <= 0:
                    break
                    
            except:
                break
        
        return exports
    
    def _get_name(self, index: int) -> str:
        """Get name from index."""
        idx = index & 0xFFFFFFFF
        if 0 <= idx < len(self.names):
            return self.names[idx]
        return f"<name_{idx}>"
    
    def _parse_datatable_content(self) -> List[Dict]:
        """Parse the actual DataTable rows from uexp data."""
        rows = []
        data = self.uexp_data
        pos = 0
        
        if len(data) < 4:
            return rows
        
        # Try to find DataTable structure
        # DataTables typically start with row count
        
        # First, try to read as standard property list
        try:
            # Skip any leading zeros or padding
            while pos < len(data) - 4 and data[pos:pos+4] == b'\x00\x00\x00\x00':
                pos += 4
            
            # Try reading row count
            row_count, pos = self._read_int32(data, pos)
            
            if 0 < row_count < 10000:  # Sanity check
                for i in range(row_count):
                    if pos >= len(data) - 8:
                        break
                    
                    row = {"_index": i}
                    
                    # Read row name (FName)
                    row_name, pos = self._read_fname(data, pos)
                    row["_row_name"] = row_name
                    
                    # Read properties until None
                    props, pos = self._read_properties(data, pos)
                    row.update(props)
                    
                    rows.append(row)
            
        except Exception as e:
            # Try alternative parsing
            rows = self._parse_datatable_alternative(data)
        
        return rows
    
    def _read_properties(self, data: bytes, pos: int) -> Tuple[Dict, int]:
        """Read a list of properties until 'None' terminator."""
        props = {}
        max_props = 100  # Safety limit
        
        for _ in range(max_props):
            if pos >= len(data) - 8:
                break
            
            # Read property name
            prop_name, new_pos = self._read_fname(data, pos)
            
            if prop_name == "None" or prop_name == "" or prop_name.startswith("<"):
                pos = new_pos
                break
            
            pos = new_pos
            
            # Read property type
            prop_type, pos = self._read_fname(data, pos)
            
            # Read property size
            prop_size, pos = self._read_int64(data, pos)
            
            # Read array index
            array_idx, pos = self._read_int32(data, pos)
            
            # Read property value based on type
            value, pos = self._read_property_value(data, pos, prop_type, int(prop_size))
            
            if array_idx > 0:
                prop_name = f"{prop_name}[{array_idx}]"
            
            props[prop_name] = value
        
        return props, pos
    
    def _read_property_value(self, data: bytes, pos: int, prop_type: str, size: int) -> Tuple[Any, int]:
        """Read a property value based on its type."""
        try:
            if prop_type == "IntProperty":
                val, pos = self._read_int32(data, pos)
                return val, pos
            
            elif prop_type == "FloatProperty":
                val, pos = self._read_float(data, pos)
                return val, pos
            
            elif prop_type == "BoolProperty":
                val, pos = self._read_uint8(data, pos)
                return val != 0, pos
            
            elif prop_type == "StrProperty":
                val, pos = self._read_fstring(data, pos)
                return val, pos
            
            elif prop_type == "NameProperty":
                val, pos = self._read_fname(data, pos)
                return val, pos
            
            elif prop_type == "ByteProperty":
                # Check for enum
                enum_name, pos = self._read_fname(data, pos)
                if enum_name != "None":
                    val, pos = self._read_fname(data, pos)
                    return f"{enum_name}::{val}", pos
                else:
                    val, pos = self._read_uint8(data, pos)
                    return val, pos
            
            elif prop_type == "EnumProperty":
                enum_type, pos = self._read_fname(data, pos)
                val, pos = self._read_fname(data, pos)
                return f"{enum_type}::{val}", pos
            
            elif prop_type == "ArrayProperty":
                inner_type, pos = self._read_fname(data, pos)
                pos += 1  # Skip null byte
                count, pos = self._read_int32(data, pos)
                arr = []
                for _ in range(min(count, 100)):
                    elem, pos = self._read_property_value(data, pos, inner_type, 0)
                    arr.append(elem)
                return arr, pos
            
            elif prop_type == "StructProperty":
                struct_type, pos = self._read_fname(data, pos)
                pos += 17  # Skip GUID + null
                struct_props, pos = self._read_properties(data, pos)
                return {"_struct_type": struct_type, **struct_props}, pos
            
            elif prop_type == "ObjectProperty" or prop_type == "SoftObjectProperty":
                # Object reference
                val, pos = self._read_int32(data, pos)
                return f"<object_{val}>", pos
            
            else:
                # Unknown type - skip by size
                if size > 0:
                    raw = data[pos:pos+size]
                    pos += size
                    # Try to extract any strings
                    return f"<{prop_type}:{raw[:32].hex()}>", pos
                return f"<{prop_type}>", pos
                
        except Exception as e:
            return f"<error:{e}>", pos + max(size, 1)
    
    def _parse_datatable_alternative(self, data: bytes) -> List[Dict]:
        """Alternative parsing - extract structured data patterns."""
        rows = []
        
        # Look for FName patterns (name_index, name_number both int32)
        # followed by property data
        
        pos = 0
        row_id = 0
        
        while pos < len(data) - 16:
            # Look for a valid name index
            name_idx = struct.unpack('<I', data[pos:pos+4])[0]
            
            if name_idx < len(self.names):
                row_name = self.names[name_idx]
                
                # Check if this looks like a row name (not "None", not empty)
                if row_name and row_name != "None" and not row_name.startswith("/"):
                    # Try to read properties starting after the FName
                    try:
                        props, _ = self._read_properties(data, pos + 8)
                        if props:
                            rows.append({
                                "_index": row_id,
                                "_row_name": row_name,
                                **props
                            })
                            row_id += 1
                    except:
                        pass
            
            pos += 1
        
        return rows
    
    def _enhanced_extraction(self) -> Dict[str, Any]:
        """Enhanced extraction that finds patterns in the data."""
        result = {
            "names": self.names,
            "integers": [],
            "floats": [],
            "strings": [],
            "name_references": []
        }
        
        all_data = self.data + self.uexp_data
        
        # Find all strings (both ASCII and in name table references)
        strings = set()
        
        # Extract from name table
        for name in self.names:
            if name and not name.startswith("/Script") and len(name) > 2:
                strings.add(name)
        
        # Look for length-prefixed strings
        pos = 0
        while pos < len(all_data) - 8:
            length = struct.unpack('<i', all_data[pos:pos+4])[0]
            if 3 < length < 200:
                try:
                    s = all_data[pos+4:pos+4+length-1].decode('utf-8', errors='strict')
                    if s.isprintable() and len(s) >= 3:
                        strings.add(s)
                except:
                    pass
            pos += 1
        
        result["strings"] = sorted(list(strings))
        
        # Find integer patterns (look for reasonable values)
        pos = 0
        ints = []
        while pos < len(all_data) - 4:
            val = struct.unpack('<i', all_data[pos:pos+4])[0]
            if 0 < val < 100000 and val not in ints:
                ints.append(val)
            pos += 4
        result["integers"] = sorted(set(ints))[:100]
        
        # Find float patterns
        pos = 0
        floats = []
        while pos < len(all_data) - 4:
            try:
                val = struct.unpack('<f', all_data[pos:pos+4])[0]
                if 0.001 < abs(val) < 10000 and val == val:  # Not NaN
                    floats.append(round(val, 3))
            except:
                pass
            pos += 4
        result["floats"] = sorted(set(floats))[:100]
        
        return result


def export_to_json(uasset_path: str, output_path: str = None) -> str:
    """Export a .uasset file to JSON."""
    print(f"Parsing: {uasset_path}")
    
    parser = UE4DataTableParser(uasset_path)
    result = parser.read_file()
    
    if output_path is None:
        output_path = str(Path(uasset_path).with_suffix('.json'))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, default=str)
    
    row_count = len(result.get("rows", []))
    print(f"  Exported to: {output_path} ({row_count} rows)")
    return output_path


def batch_export(folder_path: str):
    """Export all .uasset files in a folder."""
    folder = Path(folder_path)
    uasset_files = list(folder.glob('*.uasset'))
    
    print(f"Found {len(uasset_files)} .uasset files")
    
    output_folder = folder / "parsed_json"
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
    
    summary_path = output_folder / "_parse_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    success = sum(1 for r in results if r['status'] == 'success')
    print(f"\nParsed {success}/{len(results)} files")
    print(f"Output folder: {output_folder}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single file:  python uasset_datatable_parser.py <uasset_path> [output.json]")
        print("  Batch:        python uasset_datatable_parser.py <folder_path> --batch")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if "--batch" in sys.argv:
        batch_export(target)
    else:
        output = sys.argv[2] if len(sys.argv) > 2 else None
        export_to_json(target, output)
