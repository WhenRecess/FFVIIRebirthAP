# Manual Cheat Engine Item ID Testing

Since the Lua scripting has API limitations, here's the manual approach (takes 5 minutes):

## Prerequisites
✓ Cheat Engine running  
✓ FF7R running with inventory open  
✓ ce.txt table loaded in CE  
✓ "Inventory/Item Control [Hover to update]" **ENABLED** in the table

## Step-by-Step Instructions

### 1. Activate the Inventory Pointer
- In FF7R, **hover your mouse** over any item in your inventory
- This activates the pointer in the CE table
- You should see values change in the CE window

### 2. Find the Item ID Address
- In CE, look at the Address List at the bottom of the main window
- Expand the "Inventory/Item Control [Hover to update]" entry
- Find the sub-entry labeled **"Item ID"** (this should show your current first inventory item)
- Note its address (it will be something like `[address]+OFFSET`)

### 3. Test Each ID
For **each** of these 5 IDs:

| # | ID | Expected Item |
|---|---|---|
| 1 | 100 | Potion |
| 2 | 9001 | Power Wristguards |
| 3 | 3000 | Queen's Blood Card |
| 4 | 6100 | Chadley Data - Gongaga |
| 5 | 10102 | Crystal: Kjata2 |

**For each test:**
1. Right-click the "Item ID" address in CE → **Modify**
2. Clear the current value
3. Enter the test ID value (e.g., `100`)
4. Click **OK** or press **Enter**
5. Watch your FF7R inventory - the item should change
6. Note down: **Y** (correct item) or **N** (wrong item)
7. Move to next test ID

## Recording Results

Save your results in `ITEM_TEST_TEMPLATE.txt`:

```
Test ID,Category,Expected Item,Actual Item,Match
100,Potion,Potion,?,Y/N
9001,E_ACC_0001,Power Wristguards,?,Y/N
3000,Minigame Card,Queen's Blood Card,?,Y/N
6100,Chadly Data,Chadley Data - Gongaga,?,Y/N
10102,Crystal,Crystal Kjata2,?,Y/N
```

## Evaluation

**If 4-5 match**: ✅ Your 244-item mapping is TRUSTWORTHY  
**If 2-3 match**: ⚠️ Some patterns are wrong, needs refinement  
**If 0-1 match**: ❌ ID ranges are incorrect, need different approach

## Troubleshooting

**"Can't find Item ID"?**
- Make sure "Inventory/Item Control" is ENABLED (checkbox visible)
- Make sure you're hovering over an inventory item in FF7R
- Close and reopen CE to refresh

**"Value won't change"?**
- Right-click address → Pointer
- Then modify the pointer value instead

**"Item doesn't change"?**
- The address might be frozen/locked
- Unfreeze it first (if it has a lock icon, click to unlock)
