# QArt Implementation - RS Linearity Approach

## Overview

QArt uses the **linearity property of Reed-Solomon codes** to create valid QR codes (0 errors) that transform from message A to message B with minimal module changes.

## Key Mathematical Insight

Reed-Solomon encoding is **linear** in Galois Field arithmetic:

$$E(M_{original} \oplus M_{noise}) = E(M_{original}) \oplus E(M_{noise})$$

By flipping padding bits (free space after the message), we can control specific patterns of pixels in the error correction area without breaking the QR code.

## How It Works

### 1. Basis Vector Extraction

For each padding bit:
- Flip the bit in the data stream
- Re-encode the QR code
- Calculate XOR difference: `Basis = Encode(Original) XOR Encode(Original XOR Bit_Flip)`

This gives us the **basis vector** - the exact pattern of pixels controlled by that padding bit.

### 2. Coordinate Descent Solver

Using greedy coordinate descent over GF(2):

1. Start with `Current = BaseQR`
2. For each basis vector, check if flipping it improves similarity to target
3. Keep flips that reduce Hamming distance: `||Current XOR Target||`
4. Repeat until convergence

This minimizes the number of module changes while maintaining a **valid QR code** (0 errors).

## Advantages Over ILP

- **Valid QR codes**: Always produces QR codes with 0 errors (no decoder needed)
- **Exploits RS structure**: Uses mathematical properties, not brute force
- **Fast**: O(N·K) where N=pixels, K=modifiable bits
- **Optimal for visual QR**: Perfect for creating artistic QR codes

## Usage

```python
from src.transformer import QRTransformer

# Automatically uses QArt (RS linearity)
transformer = QRTransformer(ecc_level='H')  # High ECC for more padding
result = transformer.transform("Hello", "World")

print(f"Minimal flips: {result.min_flips}")
print(f"Valid QR code: {result.within_ecc}")  # Always True for QArt
```

## Implementation Details

### Basis Vector Extraction

The implementation:
1. Identifies padding bits in the data stream
2. Flips each bit and re-encodes
3. Calculates pixel differences
4. Stores basis vectors for coordinate descent

### Coordinate Descent

The solver:
- Iterates through basis vectors
- Tests each flip: `candidate = current XOR basis`
- Keeps flips that reduce Hamming distance to target
- Converges to local minimum

## Performance

- Small QR codes: Extracts basis vectors in < 1 second
- Medium QR codes: Solves in 1-5 seconds
- Large QR codes: May take longer due to basis extraction

## Comparison

| Method | Valid QR? | Errors | Speed | Optimality |
|--------|-----------|--------|-------|------------|
| QArt   | ✅ Yes    | 0      | Fast  | Local opt  |
| ILP    | ❌ No     | Uses ECC| Slower| Global opt |

QArt is preferred when you need **valid QR codes** that decode correctly without relying on error correction.

