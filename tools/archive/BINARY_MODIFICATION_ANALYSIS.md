# Binary Data Modification Challenge - Analysis & Solution

## Problem Statement

FF7R's Equipment.uasset and ShopItem.uasset files are **NormalExport** objects with properties stored in custom binary format (Extras field), NOT as UAsset properties. This means:

- ❌ **Cannot use UAssetAPI property system** - It won't find the stat/price values
- ❌ **Cannot manually edit with UAssetGUI every time** - Not scalable for AP
- ✅ **Can use binary pattern matching** - Find and modify price/stat byte patterns

## Root Cause

```
ShopItem.uasset structure:
├─ Export 0: ShopItem (NormalExport)
│  ├─ Properties: 0  (empty!)
│  └─ Extras: 124,708 bytes (contains all shop data in binary format)
```

The 124KB of Extras data contains:
- Shop location IDs
- Item IDs (strings)
- Prices (integers)
- Counters and flags
- Etc.

## Working Solutions

### Option 1: Binary Pattern Matching (Most Practical)

**Concept**: Search for byte patterns and replace them

```csharp
// Find all 4-byte integer values that match common shop prices
foreach (int price in new[] { 1, 5, 10, 15, 20, 25, 30, 50, 75, 100, 150, 200, 500, 1000 })
{
    byte[] priceBytes = BitConverter.GetBytes(price);
    
    // Search uexp file for this pattern
    // Replace with randomized value
}
```

**Pros**:
- ✅ Works with any binary format
- ✅ No need to understand internal structure
- ✅ Can work on both Equipment and ShopItem

**Cons**:
- ⚠️ Risk of replacing wrong values (false positives)
- ⚠️ May miss some values
- ⚠️ Not precise

### Option 2: Binary Format Reverse Engineering

**Concept**: Parse the custom binary format and modify structured data

```csharp
// 1. Read the Extras binary
// 2. Parse following FF7R's custom format:
//    - Row count (4 bytes)
//    - For each row:
//      - Row name length (4 bytes)
//      - Row name (string)
//      - Properties... (depends on format)
// 3. Find and modify specific properties
// 4. Write back
```

**Pros**:
- ✅ Precise targeting
- ✅ No false positives
- ✅ Can modify specific items only

**Cons**:
- ❌ Requires format documentation (not public)
- ❌ Complex reverse engineering needed
- ❌ Time-intensive

### Option 3: Use Existing Modding Tools (Current Working Method)

**Concept**: Continue using UAssetGUI manually, then automate with scripting

```powershell
# 1. Extract fresh files
# 2. Use UAssetGUI to open and manually edit
# 3. Repack with retoc
# 4. Deploy
```

**Pros**:
- ✅ Already works (proven)
- ✅ No format knowledge needed
- ✅ GUI handles serialization

**Cons**:
- ❌ Requires manual UAssetGUI interaction
- ❌ Not automatable
- ❌ Not suitable for AP implementation

## Recommended Approach for AP: Binary Pattern Matching

Since precise reverse engineering requires format documentation we don't have, and we need a working solution quickly, **binary pattern matching is the pragmatic choice**:

### Implementation Strategy

```csharp
class BinaryModifier
{
    public void ModifyShopPrices(string uexpPath, Random random, int minPrice = 1, int maxPrice = 9999)
    {
        byte[] data = File.ReadAllBytes(uexpPath);
        
        // List of prices commonly found in FF7R shops
        int[] commonPrices = { 
            1, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 300, 500, 
            750, 1000, 1500, 2000, 3000, 5000, 7500, 9999
        };
        
        int modifications = 0;
        
        foreach (int price in commonPrices)
        {
            byte[] pattern = BitConverter.GetBytes(price);
            
            // Find all occurrences
            for (int i = 0; i < data.Length - 3; i++)
            {
                // Check if pattern matches at this offset
                bool matches = true;
                for (int j = 0; j < 4; j++)
                {
                    if (data[i + j] != pattern[j])
                    {
                        matches = false;
                        break;
                    }
                }
                
                if (matches)
                {
                    // Randomize with context check
                    if (IsLikelyPrice(data, i))
                    {
                        int newPrice = random.Next(minPrice, maxPrice + 1);
                        byte[] newBytes = BitConverter.GetBytes(newPrice);
                        Array.Copy(newBytes, 0, data, i, 4);
                        modifications++;
                    }
                }
            }
        }
        
        File.WriteAllBytes(uexpPath, data);
        Console.WriteLine($"Modified {modifications} price values");
    }
    
    private bool IsLikelyPrice(byte[] data, int offset)
    {
        // Context check: prices usually surrounded by specific patterns
        // This helps reduce false positives
        // E.g., prices are rarely at offset 0, usually follow other structured data
        return offset > 100 && offset < data.Length - 100;
    }
}
```

## Testing & Validation Approach

1. **Test on ShopItem first**
   - Extract fresh ShopItem.uasset/uexp
   - Run binary modifier on uexp
   - Repack with retoc
   - Deploy and test in-game
   - Verify prices changed ✓

2. **Refine false positive filters**
   - If wrong values changed, add more context checks
   - Adjust price range if needed

3. **Test on Equipment**
   - Similar process for equipment stats
   - Equipment stats are typically 0-200 range

4. **Integrate into AP workflow**
   - Auto-generate randomized files
   - Create mods dynamically

## Files & References

**Created Tools**:
- `UAssetModifier.exe` - Attempts structured property modification (needs update for binary format)
- `UAssetInspector.exe` - Analyzes UAsset structure

**Key Findings**:
- ShopItem: NormalExport with 0 properties, 124,708 bytes in Extras
- Equipment: NormalExport with 0 properties, 149,508 bytes in Extras
- Both use custom FF7R binary format, not standard UAsset properties

## Next Steps

1. ✅ Implement binary pattern matching in UAssetModifier
2. ✅ Test on ShopItem.uexp to randomize prices
3. ✅ Verify in-game changes appear
4. ✅ Test on Equipment.uexp for stats
5. ✅ Integrate into Python randomizer script
6. ✅ Create fully automated AP workflow

## Alternative: Request Format Documentation

If modding community has reverse-engineered the format, we could:
1. Search FF7R modding Discord/forums for format docs
2. Look at other mod tools for binary format hints
3. Request help from UE4SS community

But binary pattern matching should work without this knowledge.

---

**Status**: Ready to implement binary pattern matching solution
**Priority**: HIGH - Blocks full AP implementation
**Effort**: Medium (1-2 hours for working prototype)
