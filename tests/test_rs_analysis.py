"""Tests for RS analysis."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rs_analysis import RSAnalyzer


def test_rs_analyzer_initialization():
    """Test RS analyzer initialization."""
    analyzer = RSAnalyzer(version=1, ecc_level='M')
    
    assert analyzer.version == 1
    assert analyzer.ecc_level == 'M'
    assert analyzer.ecc_capacity > 0
    assert analyzer.total_codewords > 0


def test_ecc_capacity():
    """Test ECC capacity calculation."""
    analyzer = RSAnalyzer(version=1, ecc_level='M')
    
    # Should be able to correct errors within capacity
    assert analyzer.can_correct_errors(analyzer.ecc_capacity)
    assert analyzer.can_correct_errors(analyzer.ecc_capacity - 1)
    
    # Should not be able to correct errors beyond capacity
    assert not analyzer.can_correct_errors(analyzer.ecc_capacity + 1)


def test_different_ecc_levels():
    """Test that different ECC levels have different capacities."""
    capacities = {}
    for ecc in ['L', 'M', 'Q', 'H']:
        analyzer = RSAnalyzer(version=1, ecc_level=ecc)
        capacities[ecc] = analyzer.ecc_capacity
    
    # Higher ECC levels should have higher capacity
    assert capacities['H'] >= capacities['Q']
    assert capacities['Q'] >= capacities['M']
    assert capacities['M'] >= capacities['L']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

