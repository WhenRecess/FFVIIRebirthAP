/*
 * UAssetAPI Example: DataTable to CSV Exporter
 * 
 * This C# program demonstrates how to use UAssetAPI to:
 * 1. Open .uasset files from Unreal Engine games
 * 2. Find DataTable exports
 * 3. Extract data from DataTable rows
 * 4. Export the data to CSV format
 * 
 * Use this as a template for extracting item, territory, and enemy data
 * from Final Fantasy VII: Rebirth asset files.
 */

using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using UAssetAPI;
using UAssetAPI.ExportTypes;
using UAssetAPI.UnrealTypes;

namespace FF7RebirthDataExporter
{
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length < 1)
            {
                Console.WriteLine("Usage: exporter_example <path_to_uasset_file> [output_csv]");
                Console.WriteLine("");
                Console.WriteLine("Example:");
                Console.WriteLine("  exporter_example ItemTable.uasset items.csv");
                Console.WriteLine("  exporter_example TerritoryData.uasset territories.csv");
                return;
            }

            string uassetPath = args[0];
            string outputPath = args.Length > 1 ? args[1] : Path.ChangeExtension(uassetPath, ".csv");

            try
            {
                Console.WriteLine($"Loading asset: {uassetPath}");
                UAsset asset = new UAsset(uassetPath, EngineVersion.VER_UE4_27);
                
                Console.WriteLine($"Asset loaded. Export count: {asset.Exports.Count}");
                
                // Find DataTable exports
                List<DataTableExport> dataTables = FindDataTableExports(asset);
                
                if (dataTables.Count == 0)
                {
                    Console.WriteLine("No DataTable exports found in this asset.");
                    return;
                }
                
                Console.WriteLine($"Found {dataTables.Count} DataTable(s)");
                
                // Export the first DataTable to CSV
                DataTableExport dataTable = dataTables[0];
                Console.WriteLine($"Exporting DataTable: {dataTable.ObjectName}");
                
                ExportDataTableToCSV(dataTable, outputPath);
                
                Console.WriteLine($"Successfully exported to: {outputPath}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
                Console.WriteLine(ex.StackTrace);
            }
        }

        /// <summary>
        /// Find all DataTable exports in an asset
        /// </summary>
        static List<DataTableExport> FindDataTableExports(UAsset asset)
        {
            List<DataTableExport> dataTables = new List<DataTableExport>();
            
            foreach (Export export in asset.Exports)
            {
                if (export is DataTableExport dataTableExport)
                {
                    dataTables.Add(dataTableExport);
                }
            }
            
            return dataTables;
        }

        /// <summary>
        /// Export a DataTable to CSV format
        /// </summary>
        static void ExportDataTableToCSV(DataTableExport dataTable, string outputPath)
        {
            if (dataTable.Table == null || dataTable.Table.Data == null)
            {
                throw new Exception("DataTable has no data");
            }

            using (StreamWriter writer = new StreamWriter(outputPath, false, Encoding.UTF8))
            {
                // Get column names from the first row's property names
                if (dataTable.Table.Data.Count > 0)
                {
                    var firstRow = dataTable.Table.Data[0];
                    List<string> columnNames = new List<string> { "RowName" }; // First column is row name
                    
                    foreach (var property in firstRow.Value)
                    {
                        columnNames.Add(property.Name.ToString());
                    }
                    
                    // Write header
                    writer.WriteLine(string.Join(",", columnNames));
                }

                // Write data rows
                foreach (var row in dataTable.Table.Data)
                {
                    List<string> values = new List<string>();
                    
                    // Add row name as first column
                    values.Add(EscapeCSV(row.Key.ToString()));
                    
                    // Add property values
                    foreach (var property in row.Value)
                    {
                        string value = PropertyToString(property);
                        values.Add(EscapeCSV(value));
                    }
                    
                    writer.WriteLine(string.Join(",", values));
                }
            }
        }

        /// <summary>
        /// Convert a UAssetAPI property to a string representation
        /// </summary>
        static string PropertyToString(PropertyData property)
        {
            // Handle different property types
            switch (property)
            {
                case IntPropertyData intProp:
                    return intProp.Value.ToString();
                
                case FloatPropertyData floatProp:
                    return floatProp.Value.ToString();
                
                case StrPropertyData strProp:
                    return strProp.Value ?? "";
                
                case NamePropertyData nameProp:
                    return nameProp.Value?.ToString() ?? "";
                
                case TextPropertyData textProp:
                    return textProp.Value?.ToString() ?? "";
                
                case BoolPropertyData boolProp:
                    return boolProp.Value.ToString();
                
                case ObjectPropertyData objProp:
                    return objProp.Value.ToString();
                
                case StructPropertyData structProp:
                    // For structs, you may want to serialize nested properties
                    return $"[Struct:{structProp.StructType}]";
                
                case ArrayPropertyData arrayProp:
                    // For arrays, you may want to serialize elements
                    return $"[Array:{arrayProp.ArrayType}]";
                
                default:
                    return property.ToString();
            }
        }

        /// <summary>
        /// Escape special characters for CSV format
        /// </summary>
        static string EscapeCSV(string value)
        {
            if (value == null)
                return "";
            
            // If value contains comma, quote, or newline, wrap in quotes and escape quotes
            if (value.Contains(",") || value.Contains("\"") || value.Contains("\n"))
            {
                return "\"" + value.Replace("\"", "\"\"") + "\"";
            }
            
            return value;
        }
    }
}

/* 
 * Building and Running
 * ====================
 * 
 * Prerequisites:
 * - .NET SDK 6.0 or later
 * - UAssetAPI NuGet package
 * 
 * Build:
 *   dotnet new console -n FF7RebirthDataExporter
 *   cd FF7RebirthDataExporter
 *   dotnet add package UAssetAPI
 *   # Copy this file as Program.cs
 *   dotnet build
 * 
 * Run:
 *   dotnet run path/to/game/Content/DataTables/ItemTable.uasset items.csv
 *   dotnet run path/to/game/Content/Territories/TerritoryData.uasset territories.csv
 * 
 * 
 * Adapting for FF7 Rebirth
 * =========================
 * 
 * 1. Locate game asset files:
 *    - Usually in <GameDir>/FF7Rebirth/Content/
 *    - May be inside .pak files (use tools like u4pak to extract)
 * 
 * 2. Find relevant DataTables:
 *    - Items: Look for DataTables with "Item", "Equipment", "Materia" in the name
 *    - Territories: Look for "Territory", "Encounter", "Battle" tables
 *    - Enemies: Look for "Enemy", "Monster", "MobTemplate" tables
 * 
 * 3. Customize PropertyToString:
 *    - Add custom handling for game-specific struct types
 *    - Format complex data as needed for your CSV
 * 
 * 4. Filter and transform:
 *    - Add filtering logic to extract only relevant items
 *    - Map game property names to AP-friendly column names
 *    - Add classification logic (progression vs filler)
 * 
 * 5. Output format:
 *    - Ensure output matches the CSV format expected by the APWorld
 *    - See worlds/finalfantasy_rebirth/README_WORLD.md for format specs
 * 
 * 
 * Advanced: Batch Processing
 * ==========================
 * 
 * Process multiple files:
 * 
 *   foreach (string file in Directory.GetFiles(dataTablesPath, "*.uasset"))
 *   {
 *       string outputFile = Path.Combine(outputPath, Path.GetFileNameWithoutExtension(file) + ".csv");
 *       ProcessAsset(file, outputFile);
 *   }
 * 
 * 
 * Alternative Tools
 * =================
 * 
 * - UAssetGUI: GUI tool for viewing/exporting UAsset files
 *   https://github.com/atenfyr/UAssetGUI
 * 
 * - FModel: Game asset explorer with export capabilities
 *   https://fmodel.app/
 * 
 * - u4pak: Extract files from .pak archives
 *   https://github.com/panzi/u4pak
 */
