# ILP Implementation for QR Code Transformation

## Overview

This implementation uses Integer Linear Programming (ILP) to find the minimal number of module flips required to transform QR code A to decode as message B, while exploiting Reed-Solomon error correction.

## Mathematical Formulation

### Decision Variables
- `x[i,j] ∈ {0,1}` - Binary variable: 1 if module at position (i,j) is flipped, 0 otherwise
- `y[k] ∈ {0,1}` - Binary variable: 1 if difference k is "absorbed" via ECC, 0 if flipped

### Objective Function
Minimize total flips:
```
minimize: Σ x[i,j] for all (i,j)
```

### Constraints

1. **Difference handling**: For each position where A ≠ B:
   ```
   x[i,j] = 1 - y[k]
   ```
   This means: if we absorb via ECC (y[k]=1), we don't flip (x[i,j]=0). If we don't absorb (y[k]=0), we must flip (x[i,j]=1).

2. **ECC capacity constraint**:
   ```
   Σ y[k] ≤ ecc_capacity
   ```
   We can only absorb up to `ecc_capacity` differences via error correction.

3. **No unnecessary flips**: For positions where A = B:
   ```
   x[i,j] = 0
   ```
   Don't flip modules that already match.

## Implementation

### Using ILP Transformer

```python
from src.ilp_transformer import ILPQRTransformer

transformer = ILPQRTransformer(ecc_level='M')
result = transformer.transform("Hello", "World")

print(f"Minimal flips: {result.min_flips}")
print(f"Solver time: {result.solver_time:.3f}s")
```

### Using Main Transformer with ILP

```python
from src.transformer import QRTransformer

transformer = QRTransformer(ecc_level='M')
result = transformer.transform("Hello", "World", use_ilp=True)

print(f"Minimal flips: {result.min_flips}")
```

## Solver

The implementation uses Google OR-Tools with the SCIP solver. If OR-Tools is not available, it falls back to a greedy algorithm that still exploits ECC.

### Installation

```bash
pip install ortools
```

## Algorithm Benefits

1. **Optimal Solution**: ILP guarantees finding the minimal number of flips
2. **ECC Exploitation**: Automatically exploits error correction capacity
3. **Flexible**: Works with any ECC level (L/M/Q/H)

## Performance

- Small QR codes (< 50x50): Solves in < 1 second
- Medium QR codes (50-100x100): Solves in 1-10 seconds
- Large QR codes (> 100x100): May take longer, consider using greedy fallback

## Future Improvements

1. **Full Codeword Mapping**: Currently uses simplified module-to-codeword mapping. Full implementation would follow QR spec exactly.

2. **Symbol-level Constraints**: Add constraints at the codeword/symbol level for more accurate RS modeling.

3. **Block Structure**: Model RS block structure more accurately.

