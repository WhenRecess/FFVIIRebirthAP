# FFVII Rebirth World Tests

This directory should contain test cases for the FFVII Rebirth Archipelago world.

## Writing Tests

Use Archipelago's WorldTestBase to create tests:

```python
from test.bases import WorldTestBase

class FFVIIRebirthTestBase(WorldTestBase):
    game = "Final Fantasy VII: Rebirth"


class TestItemGeneration(FFVIIRebirthTestBase):
    def test_all_progression_items_exist(self):
        """Test that all progression items are in the pool"""
        progression_items = [item for item in self.multiworld.get_items() 
                           if item.advancement]
        self.assertGreater(len(progression_items), 0)


class TestLogic(FFVIIRebirthTestBase):
    def test_grasslands_accessible(self):
        """Test that Grasslands is accessible from start"""
        self.assertTrue(self.can_reach_region("Grasslands"))
    
    def test_chocobo_lure_required(self):
        """Test that certain locations require Chocobo Lure"""
        # Without Chocobo Lure, shouldn't reach certain encounters
        self.assertFalse(self.can_reach_location("Grasslands: Encounter 5"))
        
        # With Chocobo Lure, should be accessible
        self.collect_by_name("Chocobo Lure")
        self.assertTrue(self.can_reach_location("Grasslands: Encounter 5"))


class TestGeneration(FFVIIRebirthTestBase):
    def test_generates_without_error(self):
        """Test that world generation completes successfully"""
        # If we get here, generation succeeded
        self.assertTrue(True)
```

## Running Tests

From the Archipelago root directory:

```bash
python -m pytest worlds/finalfantasy_rebirth/test/
```

Run a specific test file:

```bash
python -m pytest worlds/finalfantasy_rebirth/test/test_logic.py
```

Run with verbose output:

```bash
python -m pytest -v worlds/finalfantasy_rebirth/test/
```

## Test Coverage

Consider adding tests for:
- Item generation (all expected items created)
- Location generation (all locations created with correct IDs)
- Access logic (progression requirements work correctly)
- Region connectivity (all regions are reachable)
- Edge cases (minimum/maximum item counts, etc.)
- Option variations (different world settings)

## TODO

- [ ] Add test_items.py for item generation tests
- [ ] Add test_locations.py for location tests
- [ ] Add test_logic.py for access logic tests
- [ ] Add test_generation.py for world generation tests
- [ ] Set up continuous integration (CI) for automated testing

## Resources

- [Archipelago Testing Documentation](https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/world%20api.md#testing)
- [pytest Documentation](https://docs.pytest.org/)
