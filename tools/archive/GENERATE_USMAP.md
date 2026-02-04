# Generating a .usmap for FF7 Rebirth

A `.usmap` file contains mappings for unversioned properties in Unreal Engine assets. FF7 Rebirth uses unversioned properties, so we need this to parse and modify .uasset files.

## Option 1: FModel (Easiest)

**FModel** is a GUI tool that can generate .usmap files automatically.

### Steps:

1. **Download FModel**
   - Get the latest release: https://fmodel.app/
   - Extract and run `FModel.exe`

2. **Configure FModel for FF7 Rebirth**
   - Click **Directory Selector** (folder icon)
   - Navigate to your FF7 Rebirth game directory
   - Select the folder containing `.pak` files (usually `EndGame/Content/Paks/`)
   - FModel will scan and load the game files

3. **Generate .usmap**
   - In FModel, go to **Mappings** menu
   - Click **Generate Mappings**
   - FModel will analyze the game and create a `.usmap` file
   - Save it as `FF7Rebirth.usmap`

4. **Copy to project**
   - Copy the generated `FF7Rebirth.usmap` to:
     ```
     tools/FF7Rebirth.usmap
     ```

---

## Option 2: Dumper-7 (Advanced)

**Dumper-7** generates SDK files and .usmap mappings by injecting into the game process.

### Prerequisites:
- FF7 Rebirth must be runnable
- Administrator privileges
- Windows Defender / Antivirus may flag it (whitelist the folder)

### Steps:

1. **Download Dumper-7**
   - GitHub: https://github.com/Encryqed/Dumper-7
   - Download the latest release
   - Extract to a folder (e.g., `C:\Dumper-7\`)

2. **Configure Dumper-7**
   - Navigate to the Dumper-7 folder
   - Edit `Config.json`:
     ```json
     {
       "Game": "FF7Rebirth",
       "GameVersion": "1.0",
       "DumpObjects": true,
       "DumpProperties": true,
       "GenerateMappings": true
     }
     ```

3. **Launch the game**
   - Start FF7 Rebirth normally
   - Let it load to the main menu or in-game

4. **Inject Dumper-7**
   - Run `Injector.exe` as Administrator
   - Select `ff7rebirth.exe` from the process list
   - Click **Inject**
   - Wait for the dump to complete (may take 1-5 minutes)
   - A console window will show progress

5. **Locate the output**
   - Dumper-7 creates a folder: `C:\Dumper-7\Output\FF7Rebirth\`
   - Find the `.usmap` file (e.g., `FF7Rebirth-Win64-Shipping.usmap`)

6. **Copy to project**
   - Copy the `.usmap` file to:
     ```
     tools/FF7Rebirth.usmap
     ```

---

## Option 3: UEDumper (Alternative)

**UEDumper** is another memory dumper tool, similar to Dumper-7.

### Steps:

1. **Download UEDumper**
   - GitHub: https://github.com/Spuckwaffel/UEDumper
   - Download latest release
   - Extract to a folder

2. **Launch and configure**
   - Run `UEDumper.exe` as Administrator
   - Select `ff7rebirth.exe` from the process list
   - Enable **Generate .usmap** option
   - Click **Dump**

3. **Locate output**
   - Check `UEDumper/Output/FF7Rebirth/`
   - Copy the `.usmap` file to `tools/FF7Rebirth.usmap`

---

## Verifying the .usmap

Once you have the `.usmap` file:

1. **Check file size**
   - Valid `.usmap` files are typically 100KB - 50MB
   - If it's only a few KB, it might be incomplete

2. **Test with UAssetAPI**
   - Place `FF7Rebirth.usmap` in the `tools/` folder
   - I'll update the exporter to load mappings
   - Re-run the export to verify properties are parsed

---

## Recommended: FModel

**Start with FModel** - it's the easiest and most reliable:
- No game injection required
- Works offline with extracted PAK files
- GUI interface
- Automatic mapping generation
- Can browse and export assets visually

Once you have the `.usmap`, let me know and I'll integrate it into the UAssetExporter to enable proper property parsing and modification.
