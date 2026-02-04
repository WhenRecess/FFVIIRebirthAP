# Finding Chest Data Structures in Cheat Engine

## Goal
Find where chest data is stored in memory so we can patch item IDs before the player opens them.

## Method

### Step 1: Find a Specific Chest (Unknown Initial Value)

1. **Load your save** in an area with an unopened chest (e.g., Grasslands)
2. **Note the chest location** but DON'T open it yet
3. In CE:
   - New Scan
   - Value Type: **Unknown initial value**
   - Scan Type: **Exact Value**
   - Click **First Scan**

### Step 2: Narrow Down (Changed Value)

1. **Run around a bit** (but don't open the chest)
2. In CE:
   - Scan Type: **Changed value**
   - Click **Next Scan**
3. Repeat this 2-3 times to filter out dynamic values

### Step 3: Open the Chest

1. **Open the chest in-game**
2. In CE:
   - Scan Type: **Changed value**
   - Click **Next Scan**

You should now have fewer results. One of these is the "opened" flag.

### Step 4: Identify the Structure

Look at the addresses that changed. They'll be clustered:
```
0x7FF7F8940100  (changed from 0 to 1) ← Opened flag
0x7FF7F8940104  (changed)             ← Unknown
0x7FF7F8940108  (changed)             ← Unknown
```

### Step 5: Check Nearby Memory

1. **Right-click** one of the changed addresses
2. Select **Browse this memory region**
3. Look for patterns:

```
Offset  Value (hex)  Value (dec)  Possible meaning
+0x00   05 00 00 00  5            Chest ID
+0x04   64 00 00 00  100          Item ID (100 = Potion)
+0x08   01 00 00 00  1            Quantity
+0x0C   01 00 00 00  1            Opened flag (0→1 when opened)
+0x10   ...
```

### Step 6: Verify Item ID

1. **Add address +0x4 to the address list**
2. Type: **4 Bytes**
3. **Change the value** from 100 to 111 (Ether)
4. In game: **Load your save again**
5. **Open the same chest** - does it give Ether instead?

If YES → You found the item ID offset! 🎉

### Step 7: Find the Array Base

Now that you know one chest's structure:

1. **Save the chest address** (e.g., 0x7FF7F8940100)
2. **Find another chest** and repeat steps 1-6
3. Note the second chest's address (e.g., 0x7FF7F8940120)

Calculate structure size:
```
Chest 2 - Chest 1 = 0x120 - 0x100 = 0x20 (32 bytes)
```

Find base address pattern:
- Chests are likely in an array
- Chest[5] = base + (5 * 0x20)
- Search for pointer to this array

### Step 8: Find the Pointer

1. **Right-click** the chest address
2. **"Find out what accesses this address"**
3. **Open the chest in-game**
4. CE will show the instruction accessing it
5. Look for: `mov rax, [some_address]` ← This is the pointer!

Example:
```asm
ff7rebirth_.exe+123456 - mov rax, [ff7rebirth_.exe+ABCDEF0]
ff7rebirth_.exe+12345C - mov ecx, [rax+04]  // Reading item ID
```

The address `ff7rebirth_.exe+ABCDEF0` points to the chest array!

## What to Record

Once you find the structure, document:

```cpp
// Chest Structure (discovered via CE)
struct ChestData {
    int chest_id;        // Offset +0x0
    int item_id;         // Offset +0x4  ← CHANGE THIS
    int quantity;        // Offset +0x8
    int opened_flag;     // Offset +0xC  (0=closed, 1=opened)
    // ... more fields ...
};  // Total size: 0x20 (32 bytes)

// Array base pointer
// Static address: ff7rebirth_.exe+ABCDEF0
// Points to: ChestData chests[500];
```

## Testing

Create a CE Lua script to test patching:

```lua
-- Test: Change chest item before opening
chest_array_base = readPointer("ff7rebirth_.exe+ABCDEF0")
chest_id = 5
chest_address = chest_array_base + (chest_id * 0x20)

-- Read current item
current_item = readInteger(chest_address + 0x4)
print(string.format("Chest %d currently has item: %d", chest_id, current_item))

-- Change to Ether (111)
writeInteger(chest_address + 0x4, 111)
print("Changed to Ether - open chest in-game to test!")
```

## Next Steps

After finding the chest structure:
1. Document offsets in Memory Bridge code
2. Test patching a few chests
3. Verify game gives correct items
4. Scale to all chests in the game
