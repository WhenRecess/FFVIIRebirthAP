# Testing Guide

This directory should contain tests for the Final Fantasy VII: Rebirth APWorld.

## Writing Tests

Use Archipelago's `WorldTestBase` class to write tests:

```python
from test.bases import WorldTestBase

class FFVIIRebirthTestBase(WorldTestBase):
    game = "Final Fantasy VII: Rebirth"
    
    # Optional: Specify options for this test
    options = {
        # "death_link": True,
    }


class TestGeneration(FFVIIRebirthTestBase):
    """Test that the world can generate successfully"""
    
    def test_basic_generation(self):
        """Test that world generation completes without errors"""
        self.assertGreater(len(self.multiworld.itempool), 0)
    
    def test_all_locations_reachable(self):
        """Test that all locations can be reached"""
        self.assertBeatable(True)


class TestItems(FFVIIRebirthTestBase):
    """Test item-related functionality"""
    
    def test_key_items_in_sphere_one(self):
        """Test that certain progression items are available early"""
        # TODO: Implement test
        pass


class TestLogic(FFVIIRebirthTestBase):
    """Test progression logic"""
    
    def test_cannot_reach_junon_without_prerequisite(self):
        """Test that Junon is gated behind required items"""
        # TODO: Implement test based on actual progression logic
        pass
```

## Running Tests

From the Archipelago root directory:

```bash
# Run all tests for this world
python -m pytest worlds/finalfantasy_rebirth/test/

# Run a specific test file
python -m pytest worlds/finalfantasy_rebirth/test/test_generation.py

# Run with verbose output
python -m pytest worlds/finalfantasy_rebirth/test/ -v

# Run a specific test
python -m pytest worlds/finalfantasy_rebirth/test/test_generation.py::TestGeneration::test_basic_generation
```

## Test Coverage

Recommended tests to add:
1. Basic generation succeeds
2. All regions are created
3. All locations are reachable
4. Progression items are required for advancement
5. Victory condition is achievable
6. No softlocks are possible
7. Options work correctly

## Resources

- [Archipelago Testing Documentation](https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/tests.md)
- Example tests in other worlds: `worlds/*/test/`
