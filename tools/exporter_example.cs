/*
 * FFVII Rebirth Data Exporter
 * 
 * This C# program demonstrates how to use UAssetAPI to open .uasset files
 * from FFVII Rebirth and export DataTables to CSV format for use with
 * the Archipelago world definition.
 * 
 * Usage:
 *   dotnet run -- <path_to_uasset> <output_csv>
 * 
 * Example:
 *   dotnet run -- "C:\Games\FF7R\Content\Data\Items.uasset" items.csv
 */

using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Collections.Generic;

// TODO: Add UAssetAPI NuGet package reference
// dotnet add package UAssetAPI
// using UAssetAPI;
// using UAssetAPI.PropertyTypes.Objects;
// using UAssetAPI.UnrealTypes;
// using UAssetAPI.ExportTypes;

namespace FFVIIRebirthExporter
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("=== FFVII Rebirth Data Exporter ===");
            Console.WriteLine("Powered by UAssetAPI");
            Console.WriteLine();

            if (args.Length < 2)
            {
                Console.WriteLine("Usage: dotnet run -- <uasset_path> <output_csv>");
                Console.WriteLine("Example: dotnet run -- Items.uasset items.csv");
                return;
            }

            string uassetPath = args[0];
            string outputCsv = args[1];

            if (!File.Exists(uassetPath))
            {
                Console.WriteLine($"Error: File not found: {uassetPath}");
                return;
            }

            try
            {
                Console.WriteLine($"Loading: {uassetPath}");
                ExportDataTable(uassetPath, outputCsv);
                Console.WriteLine($"Exported to: {outputCsv}");
                Console.WriteLine("Done!");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
                Console.WriteLine(ex.StackTrace);
            }
        }

        /// <summary>
        /// Export a DataTable uasset to CSV
        /// </summary>
        static void ExportDataTable(string uassetPath, string outputCsv)
        {
            // TODO: Uncomment when UAssetAPI is available
            /*
            // Load the asset
            var asset = new UAsset(uassetPath, EngineVersion.VER_UE4_27);
            
            // Find DataTable export
            var dataTableExport = asset.Exports.FirstOrDefault(e => 
                e.ClassName.ToString() == "DataTable" || 
                e is DataTableExport
            );

            if (dataTableExport == null)
            {
                Console.WriteLine("Warning: No DataTable found in asset");
                return;
            }

            // Get table data
            var table = dataTableExport as DataTableExport;
            if (table == null || table.Table == null)
            {
                Console.WriteLine("Warning: DataTable has no rows");
                return;
            }

            // Determine column names from first row
            var firstRow = table.Table.Data.FirstOrDefault();
            if (firstRow == null || firstRow.Value == null)
            {
                Console.WriteLine("Warning: DataTable has no data");
                return;
            }

            var columns = new List<string>();
            foreach (var prop in firstRow.Value)
            {
                columns.Add(prop.Name.ToString());
            }

            // Write CSV
            using (var writer = new StreamWriter(outputCsv, false, Encoding.UTF8))
            {
                // Write header
                writer.WriteLine(string.Join(",", columns.Select(QuoteCsv)));

                // Write rows
                foreach (var row in table.Table.Data)
                {
                    var values = new List<string>();
                    
                    foreach (var column in columns)
                    {
                        var prop = row.Value.FirstOrDefault(p => p.Name.ToString() == column);
                        
                        if (prop == null)
                        {
                            values.Add("");
                            continue;
                        }

                        // Convert property value to string
                        string value = ConvertPropertyToString(prop);
                        values.Add(QuoteCsv(value));
                    }

                    writer.WriteLine(string.Join(",", values));
                }
            }

            Console.WriteLine($"Exported {table.Table.Data.Count} rows");
            */

            // Placeholder implementation until UAssetAPI is integrated
            Console.WriteLine("TODO: Implement UAssetAPI integration");
            Console.WriteLine("Install UAssetAPI: dotnet add package UAssetAPI");
            Console.WriteLine("Then uncomment the code in ExportDataTable()");
            
            // Create a sample CSV for demonstration
            using (var writer = new StreamWriter(outputCsv, false, Encoding.UTF8))
            {
                writer.WriteLine("// TODO: This is a placeholder CSV");
                writer.WriteLine("// Replace with actual export from UAssetAPI");
                writer.WriteLine("RowName,Value1,Value2");
                writer.WriteLine("\"Example\",\"123\",\"456\"");
            }
        }

        /// <summary>
        /// Convert a UAsset property to a string representation
        /// </summary>
        static string ConvertPropertyToString(object property)
        {
            // TODO: Uncomment when UAssetAPI is available
            /*
            switch (property)
            {
                case IntProperty intProp:
                    return intProp.Value.ToString();
                
                case FloatProperty floatProp:
                    return floatProp.Value.ToString();
                
                case StrProperty strProp:
                    return strProp.Value?.ToString() ?? "";
                
                case NameProperty nameProp:
                    return nameProp.Value?.ToString() ?? "";
                
                case BoolProperty boolProp:
                    return boolProp.Value.ToString();
                
                case ArrayProperty arrayProp:
                    // Convert array to "[1,2,3]" format
                    var items = arrayProp.Value
                        .Select(v => ConvertPropertyToString(v))
                        .ToArray();
                    return "[" + string.Join(",", items) + "]";
                
                case StructProperty structProp:
                    // For structs, you might want to serialize to JSON
                    // or extract specific fields
                    return "{struct}";
                
                default:
                    return property?.ToString() ?? "";
            }
            */

            return property?.ToString() ?? "";
        }

        /// <summary>
        /// Quote a string for CSV output, escaping quotes
        /// </summary>
        static string QuoteCsv(string value)
        {
            if (string.IsNullOrEmpty(value))
                return "\"\"";

            // Escape quotes
            value = value.Replace("\"", "\"\"");

            // Quote if contains comma, quote, or newline
            if (value.Contains(",") || value.Contains("\"") || value.Contains("\n"))
                return "\"" + value + "\"";

            return "\"" + value + "\"";
        }
    }
}
