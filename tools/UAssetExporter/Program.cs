using System;
using System.IO;
using System.Collections.Generic;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UAssetAPI;
using UAssetAPI.ExportTypes;
using UAssetAPI.PropertyTypes.Objects;
using UAssetAPI.PropertyTypes.Structs;
using UAssetAPI.UnrealTypes;
using UAssetAPI.Unversioned;

namespace UAssetExporter
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("=== FFVII Rebirth UAsset Exporter ===");
            Console.WriteLine("Using UAssetAPI");
            Console.WriteLine();

            if (args.Length < 1)
            {
                Console.WriteLine("Usage:");
                Console.WriteLine("  Single file:  UAssetExporter <uasset_path> [output.json]");
                Console.WriteLine("  Batch folder: UAssetExporter <folder_path> --batch");
                return;
            }

            string target = args[0];
            bool batch = args.Length > 1 && args[1] == "--batch";

            if (batch && Directory.Exists(target))
            {
                BatchExport(target);
            }
            else if (File.Exists(target))
            {
                string output = args.Length > 1 && args[1] != "--batch"
                    ? args[1]
                    : Path.ChangeExtension(target, ".json");
                ExportFile(target, output);
            }
            else
            {
                Console.WriteLine($"Error: Path not found: {target}");
            }
        }

        static void BatchExport(string folderPath)
        {
            var files = Directory.GetFiles(folderPath, "*.uasset");
            Console.WriteLine($"Found {files.Length} .uasset files");

            string outputFolder = Path.Combine(folderPath, "exported_json");
            Directory.CreateDirectory(outputFolder);

            var results = new List<object>();

            foreach (var file in files)
            {
                try
                {
                    string outputFile = Path.Combine(outputFolder,
                        Path.GetFileNameWithoutExtension(file) + ".json");
                    ExportFile(file, outputFile);
                    results.Add(new { file, status = "success" });
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"  ERROR: {ex.Message}");
                    results.Add(new { file, status = "error", error = ex.Message });
                }
            }

            // Write summary
            string summaryPath = Path.Combine(outputFolder, "_export_summary.json");
            File.WriteAllText(summaryPath, JsonConvert.SerializeObject(results, Formatting.Indented));

            int successCount = results.Count(r => ((dynamic)r).status == "success");
            Console.WriteLine($"\nExported {successCount}/{results.Count} files");
            Console.WriteLine($"Output folder: {outputFolder}");
        }

        static void ExportFile(string uassetPath, string outputPath)
        {
            Console.WriteLine($"Loading: {uassetPath}");

            // Load .usmap if available
            Usmap mappings = null;
            string usmapPath = @"F:\Downloads\4.26.1-0+++UE4+Release-4.26-End.usmap";
            if (File.Exists(usmapPath))
            {
                try
                {
                    mappings = new Usmap(usmapPath);
                    Console.WriteLine($"  Loaded mappings: {usmapPath}");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"  Warning: Could not load .usmap: {ex.Message}");
                }
            }

            // Try different engine versions for FF7 Rebirth
            UAsset? asset = null;
            Exception? lastError = null;

            var versionsToTry = new[] {
                EngineVersion.VER_UE4_26,
                EngineVersion.VER_UE4_27,
                EngineVersion.VER_UE4_25,
                EngineVersion.VER_UE5_0
            };

            foreach (var version in versionsToTry)
            {
                try
                {
                    asset = new UAsset(uassetPath, version);
                    if (mappings != null)
                    {
                        asset.Mappings = mappings;
                    }
                    Console.WriteLine($"  Loaded with {version}");
                    break;
                }
                catch (Exception ex)
                {
                    lastError = ex;
                }
            }

            if (asset == null)
            {
                throw new Exception($"Could not load asset: {lastError?.Message}");
            }

            // Re-read asset to force property parsing with mappings
            if (mappings != null && asset.HasUnversionedProperties)
            {
                Console.WriteLine($"  Re-parsing with mappings for unversioned properties");
                var engineVersion = asset.GetEngineVersion();
                asset = new UAsset(uassetPath, engineVersion);
                asset.Mappings = mappings;
            }

            var result = new Dictionary<string, object>
            {
                ["file"] = uassetPath,
                ["engineVersion"] = asset.GetEngineVersion().ToString(),
                ["names"] = asset.GetNameMapIndexList(),
                ["exports"] = new List<object>(),
                ["hasUnversionedProperties"] = asset.HasUnversionedProperties
            };

            var exports = (List<object>)result["exports"];

            for (int i = 0; i < asset.Exports.Count; i++)
            {
                var export = asset.Exports[i];
                var exportData = new Dictionary<string, object>
                {
                    ["index"] = i,
                    ["objectName"] = export.ObjectName.ToString(),
                    ["classType"] = export.GetExportClassType().ToString()
                };

                // Handle DataTable exports specifically
                if (export is DataTableExport dataTable)
                {
                    exportData["type"] = "DataTable";
                    var rows = new List<Dictionary<string, object>>();

                    if (dataTable.Table != null && dataTable.Table.Data != null)
                    {
                        foreach (var row in dataTable.Table.Data)
                        {
                            var rowData = new Dictionary<string, object>
                            {
                                ["rowName"] = row.Name.ToString()
                            };

                            var values = new Dictionary<string, object>();
                            if (row.Value != null)
                            {
                                foreach (var prop in row.Value)
                                {
                                    values[prop.Name.ToString()] = SerializeProperty(prop);
                                }
                            }
                            rowData["values"] = values;
                            rows.Add(rowData);
                        }
                    }

                    exportData["rows"] = rows;
                    exportData["rowCount"] = rows.Count;
                }
                // Handle normal exports
                else if (export is NormalExport normalExport)
                {
                    exportData["type"] = "NormalExport";
                    var properties = new Dictionary<string, object>();

                    if (normalExport.Data != null)
                    {
                        foreach (var prop in normalExport.Data)
                        {
                            properties[prop.Name.ToString()] = SerializeProperty(prop);
                        }
                    }

                    exportData["properties"] = properties;

                    // Include raw Extras bytes if present (custom class data)
                    if (export.Extras != null && export.Extras.Length > 0)
                    {
                        exportData["extrasSize"] = export.Extras.Length;
                        // Try to parse extras as properties using the asset's name table
                        exportData["extrasData"] = ParseExtrasData(export.Extras, asset);
                    }
                }
                // Handle RawExport fallback
                else if (export is RawExport rawExport)
                {
                    exportData["type"] = "RawExport";
                    if (rawExport.Data != null && rawExport.Data.Length > 0)
                    {
                        exportData["dataSize"] = rawExport.Data.Length;
                        exportData["rawData"] = ParseExtrasData(rawExport.Data, asset);
                    }
                }
                else
                {
                    exportData["type"] = export.GetType().Name;
                    if (export.Extras != null && export.Extras.Length > 0)
                    {
                        exportData["extrasSize"] = export.Extras.Length;
                        exportData["extrasData"] = ParseExtrasData(export.Extras, asset);
                    }
                }

                exports.Add(exportData);
            }

            string json = JsonConvert.SerializeObject(result, Formatting.Indented, new JsonSerializerSettings
            {
                ReferenceLoopHandling = ReferenceLoopHandling.Ignore,
                MaxDepth = 64
            });

            File.WriteAllText(outputPath, json);
            Console.WriteLine($"  Exported to: {outputPath}");
        }

        static object SerializeProperty(PropertyData prop)
        {
            try
            {
                switch (prop)
                {
                    case IntPropertyData intProp:
                        return intProp.Value;

                    case FloatPropertyData floatProp:
                        return floatProp.Value;

                    case DoublePropertyData doubleProp:
                        return doubleProp.Value;

                    case BoolPropertyData boolProp:
                        return boolProp.Value;

                    case StrPropertyData strProp:
                        return strProp.Value?.ToString() ?? "";

                    case NamePropertyData nameProp:
                        return nameProp.Value.ToString();

                    case TextPropertyData textProp:
                        return textProp.Value?.ToString() ?? "";

                    case BytePropertyData byteProp:
                        if (byteProp.ByteType == BytePropertyType.Byte)
                            return byteProp.Value;
                        return byteProp.EnumValue.ToString();

                    case EnumPropertyData enumProp:
                        return enumProp.Value.ToString();

                    case ArrayPropertyData arrayProp:
                        var items = new List<object>();
                        if (arrayProp.Value != null)
                        {
                            foreach (var item in arrayProp.Value)
                            {
                                items.Add(SerializeProperty(item));
                            }
                        }
                        return items;

                    case StructPropertyData structProp:
                        var structDict = new Dictionary<string, object>
                        {
                            ["_structType"] = structProp.StructType.ToString()
                        };
                        if (structProp.Value != null)
                        {
                            foreach (var subProp in structProp.Value)
                            {
                                structDict[subProp.Name.ToString()] = SerializeProperty(subProp);
                            }
                        }
                        return structDict;

                    case ObjectPropertyData objProp:
                        return objProp.Value.ToString();

                    case SoftObjectPropertyData softObjProp:
                        return softObjProp.Value.ToString();

                    case MapPropertyData mapProp:
                        var mapDict = new Dictionary<string, object>();
                        if (mapProp.Value != null)
                        {
                            foreach (var kvp in mapProp.Value)
                            {
                                string key = kvp.Key?.ToString() ?? "null";
                                mapDict[key] = SerializeProperty(kvp.Value);
                            }
                        }
                        return mapDict;

                    default:
                        return new Dictionary<string, object>
                        {
                            ["_type"] = prop.GetType().Name,
                            ["_value"] = prop.ToString() ?? ""
                        };
                }
            }
            catch (Exception ex)
            {
                return new Dictionary<string, object>
                {
                    ["_error"] = ex.Message,
                    ["_type"] = prop.GetType().Name
                };
            }
        }

        static List<string> ExtractStringsFromBytes(byte[] data)
        {
            var strings = new HashSet<string>();
            var current = new List<char>();

            // Extract ASCII strings
            foreach (byte b in data)
            {
                if (b >= 32 && b < 127)
                {
                    current.Add((char)b);
                }
                else
                {
                    if (current.Count >= 4)
                    {
                        strings.Add(new string(current.ToArray()));
                    }
                    current.Clear();
                }
            }
            if (current.Count >= 4)
            {
                strings.Add(new string(current.ToArray()));
            }

            // Also try to find FString-style strings (length-prefixed)
            for (int i = 0; i < data.Length - 4; i++)
            {
                int length = BitConverter.ToInt32(data, i);
                if (length > 1 && length < 256 && i + 4 + length <= data.Length)
                {
                    try
                    {
                        string s = System.Text.Encoding.UTF8.GetString(data, i + 4, length - 1);
                        if (!string.IsNullOrEmpty(s) && s.All(c => !char.IsControl(c) || c == '\n' || c == '\r' || c == '\t'))
                        {
                            if (s.Length >= 3)
                                strings.Add(s);
                        }
                    }
                    catch { }
                }
            }

            return strings.OrderBy(s => s).ToList();
        }

        static Dictionary<string, object> ParseExtrasData(byte[] data, UAsset asset)
        {
            var result = new Dictionary<string, object>();
            var nameTable = asset.GetNameMapIndexList();

            // Find all name references in the data (4-byte indices into name table)
            var nameRefs = new List<object>();
            var intValues = new List<int>();
            var floatValues = new List<float>();

            for (int i = 0; i <= data.Length - 4; i += 4)
            {
                int val = BitConverter.ToInt32(data, i);

                // Check if it's a valid name table index
                if (val >= 0 && val < nameTable.Count)
                {
                    string name = nameTable[val].ToString();
                    // Skip common/noise names
                    if (!string.IsNullOrEmpty(name) && !name.StartsWith("/Script/") &&
                        !name.StartsWith("/Game/DataObject") && name != "None")
                    {
                        nameRefs.Add(new { index = i, nameIndex = val, name = name });
                    }
                }

                // Also track interesting int values
                if (val > 0 && val < 100000 && val != nameTable.Count)
                {
                    intValues.Add(val);
                }
            }

            // Try to extract row-like structures
            // Look for patterns: usually starts with row count, then row data
            if (data.Length >= 4)
            {
                int possibleRowCount = BitConverter.ToInt32(data, 0);
                if (possibleRowCount > 0 && possibleRowCount < 10000)
                {
                    result["possibleRowCount"] = possibleRowCount;
                }
            }

            // Group name references that appear to be in rows
            result["nameReferences"] = nameRefs.Take(500).ToList(); // Limit output
            result["dataSize"] = data.Length;

            // Try to identify the data structure by looking at the first 100 bytes
            var headerHex = BitConverter.ToString(data.Take(Math.Min(100, data.Length)).ToArray()).Replace("-", " ");
            result["headerHex"] = headerHex;

            return result;
        }
    }
}
