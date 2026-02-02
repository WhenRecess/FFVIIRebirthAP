# Testing Final Fantasy VII: Rebirth World

This directory is for unit tests that validate the Final Fantasy VII: Rebirth Archipelago World implementation.

## Writing Tests

Archipelago provides a `WorldTestBase` class for writing world tests. Create test files in this directory that inherit from `WorldTestBase`:

```python
# test_ffvii_rebirth.py

from test.bases import WorldTestBase


class TestFFVIIRebirthGeneration(WorldTestBase):
    game = "Final Fantasy VII: Rebirth"
    
    def test_item_counts(self):
        """Test that the correct number of items are generated."""
        # Your test logic here
        pass
    
    def test_all_locations_reachable(self):
        """Test that all locations are reachable with the generated item pool."""
        # Your test logic here
        pass
    
    def test_victory_condition(self):
        """Test that the victory condition is set correctly."""
        # Your test logic here
        pass
```

## Running Tests

From the Archipelago root directory:

```bash
# Run all tests for this world
python -m pytest worlds/finalfantasy_rebirth/test/

# Run a specific test file
python -m pytest worlds/finalfantasy_rebirth/test/test_ffvii_rebirth.py

# Run a specific test case
python -m pytest worlds/finalfantasy_rebirth/test/test_ffvii_rebirth.py::TestFFVIIRebirthGeneration::test_item_counts
```

## Test Examples

### Example 1: Basic Generation Test

```python
from test.bases import WorldTestBase


class TestFFVIIRebirthBasic(WorldTestBase):
    game = "Final Fantasy VII: Rebirth"
    
    def test_world_creates_successfully(self):
        """Test that the world can be created without errors."""
        # If this test runs without exceptions, world creation works
        self.assertIsNotNone(self.multiworld)
        self.assertIsNotNone(self.world)
```

### Example 2: Item Classification Test

```python
from test.bases import WorldTestBase
from BaseClasses import ItemClassification


class TestFFVIIRebirthItems(WorldTestBase):
    game = "Final Fantasy VII: Rebirth"
    
    def test_key_items_are_progression(self):
        """Test that key items are classified as progression."""
        key_items = ["Keystone", "Cargo Ship Access"]
        
        for item_name in key_items:
            with self.subTest(item=item_name):
                item = self.world.create_item(item_name)
                self.assertEqual(
                    item.classification, 
                    ItemClassification.progression,
                    f"{item_name} should be progression"
                )
```

### Example 3: Location Accessibility Test

```python
from test.bases import WorldTestBase
from Fill import distribute_items_restrictive


class TestFFVIIRebirthAccess(WorldTestBase):
    game = "Final Fantasy VII: Rebirth"
    
    def test_all_locations_accessible(self):
        """Test that all locations are accessible with the item pool."""
        # Generate items and distribute them
        self.world.generate_early()
        self.world.create_regions()
        self.world.create_items()
        self.world.set_rules()
        
        distribute_items_restrictive(self.multiworld)
        
        # Check that all locations are accessible
        for location in self.multiworld.get_locations(self.player):
            with self.subTest(location=location.name):
                self.assertTrue(
                    location.can_reach(self.multiworld.state),
                    f"Location {location.name} is not accessible"
                )
```

## Resources

- [Archipelago Test Documentation](https://github.com/ArchipelagoMW/Archipelago/blob/main/test/bases.py)
- [pytest Documentation](https://docs.pytest.org/)
- Examples from other Archipelago worlds (e.g., `worlds/alttp/test/`, `worlds/factorio/test/`)

## TODO

- [ ] Write basic generation tests
- [ ] Write item classification tests
- [ ] Write location accessibility tests
- [ ] Write victory condition tests
- [ ] Write option validation tests
