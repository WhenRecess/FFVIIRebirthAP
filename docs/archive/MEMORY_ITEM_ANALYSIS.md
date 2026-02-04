# FF7 Rebirth Item Manipulation - Memory Structure

## Key Discovery from Cheat Engine Table Analysis

The Cheat Engine table `ff7rebirth_- sharing.CT` by BigBear743 proves that **item quantities CAN be directly modified in memory**.

---

## Critical Memory Addresses (from CE Table)

### Inventory Base Pointer
```
Name: binven_ptr
Method: AOBscan for pattern "458B????442B????4489"
Injection Point: ff7rebirth_.exe + 0xF40A2F
Signature: "89 8F ? ? ? ? 48 8D ? ? ? E8 ? ? ? ? 48 8D"
```

### Item Memory Structure (relative to `binven_ptr`)
```
binven_ptr + 0x8  = Item ID (4 bytes / 32-bit int)
binven_ptr + 0xC  = Item Quantity (4 bytes / 32-bit int)
```

---

## Item ID Mappings (from CE Table)

### Consumables
- **100** = Potion
- **101** = Hi-Potion  
- **102** = Mega Potion
- **110** = Elixir
- **120** = Phoenix Down
- **130** = Remedy

### Currency
- **2** = Moogle Medals
- **3** = Golden Plums
- **1** = GP (likely Gil)

### Equipment (Armor/Accessories)
- **2000** = Metal Bracer
- **2001** = Leather Bangle
- **2004** = Copper Bracer
- (See CE table for complete list - 100+ items)

### Materia
- **10001** = Healing Materia
- **10002** = Cleansing Materia
- **10003** = Revival Materia
- **13007** = Item Master Materia
- (See CE table for complete list)

---

## How the CE Table Modifies Items

1. **Locate the pointer** - Uses AOBscan to find the memory injection point
2. **Set breakpoint** - When inventory is accessed, captures `binven_ptr`
3. **Direct write** - Modifies integer at `binven_ptr + 0x8` and `binven_ptr + 0xC`
4. **Persist** - The game reads from these same addresses

---

## Implementation Strategy

### Current Approach (MemoryItem.lua)
1. Find the inventory base pointer (needs signature scan)
2. Read/write 4-byte integers at offset 0x8 and 0xC
3. No reverse-engineering needed - just memory access

### Challenges
- **Pointer finding** - UE4SS Lua may not have direct signature scanning
- **Memory access** - UE4SS Lua needs `readInteger()` and `writeInteger()` functions
- **Stability** - Direct memory writes may cause crashes if pointer is wrong

### Workarounds
1. **Manual pointer discovery**
   - User runs CE table and finds `binven_ptr` value
   - Enters it into mod via console command
   - Mod uses that known address

2. **Signature scan fallback**
   - If UE4SS exposes memory scanning functions
   - Use CE's signature pattern

3. **Dynamic discovery**
   - Hook when inventory is opened
   - Capture the pointer at that moment

---

## Technical Notes

**Why This Works:**
- FF7R uses Unreal Engine's memory model
- Item inventory is a flat structure in RAM
- Direct memory writes bypass the (read-only) API functions
- WeMod/FLiNG trainers prove this is persistent

**Risks:**
- Wrong pointer = crash or memory corruption
- Game updates may shift memory layout
- Anti-cheat could flag direct memory modification

**Advantages:**
- Bypasses API limitations completely
- No function hooks needed
- Works with any item ID
- Quantities can be set directly

---

## Next Steps

1. ✅ Identify memory structure - DONE (from CE table)
2. ✅ Create Lua implementation - DONE (MemoryItem.lua)
3. ⏳ Find/implement signature scanning in UE4SS
4. ⏳ Test with actual pointer discovery
5. ⏳ Verify items persist after save/reload
6. ⏳ Integrate with Archipelago client

---

## References

- **CE Table:** F:\Downloads\ff7rebirth_- sharing.CT (by BigBear743)
- **Pattern Scan:** ff7rebirth_.exe + 0x00F40A2F
- **Signature:** 89 8F ? ? ? ? 48 8D ? ? ? E8 ? ? ? ? 48 8D

---

*Last Updated: 2026-02-03*
*Status: Memory structure identified, awaiting pointer discovery test*
