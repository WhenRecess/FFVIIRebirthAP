/*
 * UAsset DataTable Exporter Example
 * 
 * This C# console application demonstrates how to use UAssetAPI to open Unreal Engine
 * .uasset files and export DataTable rows to CSV format.
 * 
 * Usage:
 *   dotnet run -- <path_to_uasset_file> [output.csv]
 * 
 * Prerequisites:
 *   1. Install .NET SDK 6.0 or later (https://dotnet.microsoft.com/download)
 *   2. Add UAssetAPI NuGet package:
 *      dotnet add package UAssetAPI
 * 
 * Building:
 *   dotnet build
 * 
 * Running:
 *   dotnet run -- "C:\Path\To\Game\Content\DataTables\ItemTable.uasset"
 *   dotnet run -- "C:\Path\To\Game\Content\DataTables\LocationTable.uasset" locations.csv
 */

using System;
using System.IO;
using System.Linq;
using System.Text;
using UAssetAPI;
using UAssetAPI.ExportTypes;
using UAssetAPI.PropertyTypes.Objects;
using UAssetAPI.PropertyTypes.Structs;
using UAssetAPI.UnrealTypes;

namespace FFVIIRebirthDataExporter
{
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length < 1)
            {
                Console.WriteLine("Usage: dotnet run -- <path_to_uasset_file> [output.csv]");
                Console.WriteLine();
                Console.WriteLine("Example:");
                Console.WriteLine("  dotnet run -- \"C:\\Game\\Content\\DataTables\\ItemTable.uasset\"");
                Console.WriteLine("  dotnet run -- \"C:\\Game\\Content\\DataTables\\ItemTable.uasset\" items.csv");
                return;
            }

            string uassetPath = args[0];
            string outputPath = args.Length > 1 ? args[1] : Path.ChangeExtension(uassetPath, ".csv");

            if (!File.Exists(uassetPath))
            {
                Console.WriteLine($"Error: File not found: {uassetPath}");
                return;
            }

            try
            {
                Console.WriteLine($"Loading {uassetPath}...");
                
                // Load the .uasset file
                UAsset asset = new UAsset(uassetPath, EngineVersion.VER_UE4_27);
                
                Console.WriteLine($"Asset loaded. Engine version: {asset.EngineVersion}");
                Console.WriteLine($"Export count: {asset.Exports.Count}");

                // Find DataTable export
                DataTableExport dataTable = null;
                foreach (var export in asset.Exports)
                {
                    if (export is DataTableExport dt)
                    {
                        dataTable = dt;
                        break;
                    }
                }

                if (dataTable == null)
                {
                    Console.WriteLine("Error: No DataTable found in this asset.");
                    Console.WriteLine("This tool only works with DataTable assets.");
                    return;
                }

                Console.WriteLine($"DataTable found: {dataTable.Table.Data.Count} rows");

                // Export to CSV
                ExportDataTableToCSV(dataTable, outputPath);

                Console.WriteLine($"Export successful: {outputPath}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
                Console.WriteLine(ex.StackTrace);
            }
        }

        static void ExportDataTableToCSV(DataTableExport dataTable, string outputPath)
        {
            using (var writer = new StreamWriter(outputPath, false, Encoding.UTF8))
            {
                // Determine columns from the first row
                if (dataTable.Table.Data.Count == 0)
                {
                    Console.WriteLine("Warning: DataTable is empty.");
                    return;
                }

                var firstRow = dataTable.Table.Data.First();
                var columnNames = new[] { "RowName" }
                    .Concat(firstRow.Value.Select(prop => prop.Name.ToString()))
                    .ToArray();

                // Write header
                writer.WriteLine(string.Join(",", columnNames.Select(EscapeCSV)));

                // Write rows
                foreach (var row in dataTable.Table.Data)
                {
                    var rowName = row.Key.ToString();
                    var values = new[] { rowName }
                        .Concat(row.Value.Select(prop => GetPropertyValueAsString(prop)))
                        .ToArray();

                    writer.WriteLine(string.Join(",", values.Select(EscapeCSV)));
                }
            }
        }

        static string GetPropertyValueAsString(PropertyData property)
        {
            try
            {
                switch (property)
                {
                    case StructPropertyData structProp:
                        // For struct properties, try to extract meaningful data
                        // This is simplified - you may need to handle specific struct types
                        if (structProp.Value != null && structProp.Value.Count > 0)
                        {
                            return string.Join(";", structProp.Value.Select(p => GetPropertyValueAsString(p)));
                        }
                        return structProp.StructType?.ToString() ?? "";

                    case ArrayPropertyData arrayProp:
                        // For array properties, join elements with semicolon
                        if (arrayProp.Value != null && arrayProp.Value.Length > 0)
                        {
                            return string.Join(";", arrayProp.Value.Select(p => GetPropertyValueAsString(p)));
                        }
                        return "";

                    case IntPropertyData intProp:
                        return intProp.Value.ToString();

                    case FloatPropertyData floatProp:
                        return floatProp.Value.ToString();

                    case BoolPropertyData boolProp:
                        return boolProp.Value.ToString();

                    case StrPropertyData strProp:
                        return strProp.Value?.ToString() ?? "";

                    case NamePropertyData nameProp:
                        return nameProp.Value?.ToString() ?? "";

                    case TextPropertyData textProp:
                        return textProp.CultureInvariantString ?? "";

                    case ObjectPropertyData objProp:
                        return objProp.Value?.ToString() ?? "";

                    case EnumPropertyData enumProp:
                        return enumProp.Value?.ToString() ?? "";

                    default:
                        return property.ToString() ?? "";
                }
            }
            catch
            {
                return "";
            }
        }

        static string EscapeCSV(string value)
        {
            if (string.IsNullOrEmpty(value))
                return "";

            // Escape quotes and wrap in quotes if needed
            if (value.Contains(",") || value.Contains("\"") || value.Contains("\n"))
            {
                return "\"" + value.Replace("\"", "\"\"") + "\"";
            }

            return value;
        }
    }
}

/*
 * To create a new C# project with this code:
 * 
 * 1. Create a new console project:
 *    dotnet new console -n FFVIIRebirthDataExporter
 *    cd FFVIIRebirthDataExporter
 * 
 * 2. Add UAssetAPI package:
 *    dotnet add package UAssetAPI
 * 
 * 3. Replace Program.cs with this file
 * 
 * 4. Build and run:
 *    dotnet build
 *    dotnet run -- "C:\Path\To\DataTable.uasset"
 * 
 * Notes:
 * - UAssetAPI may not support all Unreal Engine versions or asset types
 * - You may need to adjust EngineVersion (e.g., VER_UE4_25, VER_UE5_0)
 * - Complex struct types may require custom parsing logic
 * - Large DataTables may take some time to process
 * 
 * Alternative approach:
 * - Use Unreal Engine's built-in CSV export functionality in the editor
 * - Use FModel (https://fmodel.app/) for visual asset browsing and export
 * - Use UEViewer/UModel for extracting mesh/texture data
 */
