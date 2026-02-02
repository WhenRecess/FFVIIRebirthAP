# FFVII Rebirth Data Extraction Tools

This directory contains helper tools for extracting game data from Final Fantasy VII: Rebirth.

## exporter_example.cs

A C# program that demonstrates how to use UAssetAPI to extract DataTable data from .uasset files and export to CSV format.

### Prerequisites

- .NET SDK 6.0 or later: [Download .NET](https://dotnet.microsoft.com/download)
- UAssetAPI NuGet package

### Setup

1. Create a new C# project:
   ```bash
   mkdir FFVIIRebirthExporter
   cd FFVIIRebirthExporter
   dotnet new console
   ```

2. Add UAssetAPI dependency:
   ```bash
   dotnet add package UAssetAPI
   ```

3. Copy `exporter_example.cs` content to `Program.cs`

4. Build:
   ```bash
   dotnet build
   ```

### Usage

```bash
dotnet run -- <path_to_uasset> <output_csv>
```

**Examples:**

Export item data:
```bash
dotnet run -- "C:\Games\FF7R\Content\Data\Items.uasset" items.csv
```

Export territory data:
```bash
dotnet run -- "C:\Games\FF7R\Content\Data\Territories.uasset" territories.csv
```

Export encounter data:
```bash
dotnet run -- "C:\Games\FF7R\Content\Data\Encounters.uasset" encounters.csv
```

### Extracting Game Files

Before you can export data, you need to extract .uasset files from the game's PAK files:

1. **Install UE4 PAK Extractor**:
   - [UnrealPakTool](https://github.com/allcoolthingsatoneplace/UnrealPakTool)
   - [QuickBMS with Unreal scripts](http://aluigi.altervista.org/quickbms.htm)

2. **Locate PAK files**:
   ```
   <Game Directory>\Content\Paks\
   ```

3. **Extract PAK contents**:
   ```bash
   UnrealPak.exe pakchunk0-WindowsNoEditor.pak -Extract OutputFolder/
   ```

4. **Find DataTable assets**:
   Look for .uasset files in paths like:
   - `Content/Data/Items/*.uasset`
   - `Content/Data/Territories/*.uasset`
   - `Content/Data/Encounters/*.uasset`
   - `Content/Data/Quests/*.uasset`

### Data to Export

For complete Archipelago integration, export:

1. **Items** (`items.csv`):
   - Item names and IDs
   - Item types (materia, equipment, consumable, key item)
   - Item classifications (progression, useful, filler)

2. **Territories** (`territories.csv`):
   - Territory/map indices
   - Territory names
   - Encounter lists (MobTemplateList, WaveMobTemplateList)

3. **Encounters** (`encounters.csv`):
   - Encounter IDs
   - Enemy compositions
   - Difficulty ratings

4. **Quests** (`quests.csv`):
   - Quest names
   - Quest IDs
   - Prerequisites and rewards

5. **Bosses** (`bosses.csv`):
   - Boss names
   - Boss IDs
   - Associated story flags

### CSV Output Format

The exporter will create CSV files compatible with the APWorld loaders:

**items.csv:**
```csv
ItemName,ItemID,Classification,Description
"Potion",100,filler,"Restores 500 HP"
"Chocobo Lure",201,progression,"Catch chocobos"
```

**territories.csv:**
```csv
UniqueIndex,TerritoryName,MobTemplateList,WaveMobTemplateList
100,"Grasslands_01","[1,2,3]","[4,5]"
101,"Junon_Harbor","[10,11]","[]"
```

## Alternative Tools

If you prefer not to use C# or UAssetAPI, consider:

### UEAssetExplorer / FModel
- GUI tool for viewing and exporting Unreal Engine assets
- [FModel Download](https://fmodel.app/)
- Supports viewing and exporting DataTables to JSON/CSV

### Python UAssetAPI Wrapper
- Python wrapper for UAssetAPI (if available)
- Easier to integrate with Archipelago Python code

### Manual Extraction
- Use UE4SS to dump game objects at runtime
- Hook into game functions to log data
- Use Cheat Engine to find and dump data structures

## Customization

You can modify `exporter_example.cs` to:

- Add custom filtering (e.g., only export specific item types)
- Transform data formats (e.g., convert arrays to different representations)
- Merge multiple uassets into a single CSV
- Add calculated fields (e.g., difficulty scores)

## Troubleshooting

### UAssetAPI version mismatch
- FFVII Rebirth may use a specific Unreal Engine version
- Try different UAssetAPI versions or engine version settings
- Check UAssetAPI documentation for compatibility

### Missing dependencies
- Ensure .NET SDK is installed correctly
- Verify UAssetAPI NuGet package is installed
- Check project file (.csproj) for correct package references

### Encrypted PAK files
- Some games encrypt their PAK files
- You may need to find or extract the encryption key
- Tools like UnrealPakTool may have built-in decryption

### Parsing errors
- Not all asset types are supported by UAssetAPI
- Some custom structures may need manual handling
- Check UAssetAPI GitHub issues for similar problems

## Resources

- [UAssetAPI GitHub](https://github.com/atenfyr/UAssetAPI)
- [UAssetAPI Documentation](https://github.com/atenfyr/UAssetAPI/wiki)
- [Unreal Engine Asset Format](https://docs.unrealengine.com/en-US/ProductionPipelines/AssetManagement/)
- [FModel](https://fmodel.app/) - Alternative asset viewer

## Contributing

If you develop better extraction tools or scripts:

1. Add them to this directory
2. Document usage in this README
3. Include examples and sample outputs
4. Consider adding automated tests

## License

TBD - To be determined by repository owner
