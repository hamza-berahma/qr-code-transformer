"""Test script to compare QArt vs ILP algorithms with many string pairs."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.transformer import QRTransformer
import time
from collections import defaultdict
import random
import string


def generate_string_pairs(num_pairs: int = 100, base_length: int = 10):
    """Generate pairs of strings that differ by exactly one character."""
    pairs = []
    
    # Generate random base strings
    for _ in range(num_pairs):
        # Create base string
        base = ''.join(random.choices(string.ascii_letters + string.digits, k=base_length))
        
        # Create variant by changing one character
        pos = random.randint(0, len(base) - 1)
        new_char = random.choice(string.ascii_letters + string.digits)
        while new_char == base[pos]:
            new_char = random.choice(string.ascii_letters + string.digits)
        
        variant = base[:pos] + new_char + base[pos + 1:]
        pairs.append((base, variant))
    
    return pairs


def test_algorithms(pairs, ecc_level='H'):
    """Test both algorithms on string pairs and compare results."""
    transformer = QRTransformer(ecc_level=ecc_level)
    
    results = {
        'qart_wins': 0,
        'ilp_wins': 0,
        'ties': 0,
        'qart_only': 0,
        'ilp_only': 0,
        'both_fail': 0,
        'total_tested': 0,
        'qart_flips': [],
        'ilp_flips': [],
        'qart_times': [],
        'ilp_times': []
    }
    
    print(f"Testing {len(pairs)} string pairs with ECC level {ecc_level}...")
    print("=" * 60)
    
    for i, (str_a, str_b) in enumerate(pairs, 1):
        try:
            # Run transformation (runs both algorithms internally)
            start_time = time.time()
            result = transformer.transform(str_a, str_b)
            total_time = time.time() - start_time
            
            results['total_tested'] += 1
            
            # Get algorithm results
            algo_results = getattr(result, 'algorithm_results', {})
            qart_result = algo_results.get('qart', {})
            ilp_result = algo_results.get('ilp', {})
            
            qart_flips = qart_result.get('min_flips', float('inf')) if not qart_result.get('error') else float('inf')
            ilp_flips = ilp_result.get('min_flips', float('inf')) if not ilp_result.get('error') else float('inf')
            
            qart_success = qart_result.get('success', False) and not qart_result.get('error')
            ilp_success = ilp_result.get('success', False) and not ilp_result.get('error')
            
            # Track results
            if qart_success:
                results['qart_flips'].append(qart_flips)
            if ilp_success:
                results['ilp_flips'].append(ilp_flips)
            
            # Determine winner
            if qart_success and ilp_success:
                if qart_flips < ilp_flips:
                    results['qart_wins'] += 1
                    winner = "QArt"
                elif ilp_flips < qart_flips:
                    results['ilp_wins'] += 1
                    winner = "ILP"
                else:
                    results['ties'] += 1
                    winner = "Tie"
            elif qart_success and not ilp_success:
                results['qart_only'] += 1
                winner = "QArt (only)"
            elif ilp_success and not qart_success:
                results['ilp_only'] += 1
                winner = "ILP (only)"
            else:
                results['both_fail'] += 1
                winner = "Both failed"
            
            # Print progress every 10 tests
            if i % 10 == 0 or i == len(pairs):
                print(f"Progress: {i}/{len(pairs)} | "
                      f"QArt wins: {results['qart_wins']} | "
                      f"ILP wins: {results['ilp_wins']} | "
                      f"Ties: {results['ties']}")
            
        except Exception as e:
            print(f"Error testing pair {i} ({str_a} -> {str_b}): {e}")
            results['both_fail'] += 1
            continue
    
    return results


def print_statistics(results):
    """Print detailed statistics."""
    print("\n" + "=" * 60)
    print("ALGORITHM COMPARISON STATISTICS")
    print("=" * 60)
    
    total = results['total_tested']
    print(f"\nTotal pairs tested: {total}")
    print(f"\nWins:")
    print(f"  QArt wins: {results['qart_wins']} ({100*results['qart_wins']/total:.1f}%)")
    print(f"  ILP wins: {results['ilp_wins']} ({100*results['ilp_wins']/total:.1f}%)")
    print(f"  Ties: {results['ties']} ({100*results['ties']/total:.1f}%)")
    print(f"  QArt only: {results['qart_only']} ({100*results['qart_only']/total:.1f}%)")
    print(f"  ILP only: {results['ilp_only']} ({100*results['ilp_only']/total:.1f}%)")
    print(f"  Both failed: {results['both_fail']} ({100*results['both_fail']/total:.1f}%)")
    
    if results['qart_flips']:
        qart_avg = sum(results['qart_flips']) / len(results['qart_flips'])
        qart_min = min(results['qart_flips'])
        qart_max = max(results['qart_flips'])
        print(f"\nQArt Statistics:")
        print(f"  Average flips: {qart_avg:.1f}")
        print(f"  Min flips: {qart_min}")
        print(f"  Max flips: {qart_max}")
        print(f"  Successful runs: {len(results['qart_flips'])}")
    
    if results['ilp_flips']:
        ilp_avg = sum(results['ilp_flips']) / len(results['ilp_flips'])
        ilp_min = min(results['ilp_flips'])
        ilp_max = max(results['ilp_flips'])
        print(f"\nILP Statistics:")
        print(f"  Average flips: {ilp_avg:.1f}")
        print(f"  Min flips: {ilp_min}")
        print(f"  Max flips: {ilp_max}")
        print(f"  Successful runs: {len(results['ilp_flips'])}")
    
    # When does each algorithm win?
    print(f"\n{'='*60}")
    print("WHEN DOES EACH ALGORITHM WIN?")
    print(f"{'='*60}")
    
    if results['qart_wins'] > results['ilp_wins']:
        print(f"✓ QArt wins more often ({results['qart_wins']} vs {results['ilp_wins']})")
        print("  QArt is better for: High ECC level transformations")
        print("  QArt exploits RS linearity to find valid QR codes with fewer flips")
    elif results['ilp_wins'] > results['qart_wins']:
        print(f"✓ ILP wins more often ({results['ilp_wins']} vs {results['qart_wins']})")
        print("  ILP is better for: Optimal mathematical solutions")
        print("  ILP finds globally optimal solutions using integer programming")
    else:
        print("Algorithms are roughly equal in performance")
    
    if results['qart_only'] > 0:
        print(f"\nQArt succeeded when ILP failed: {results['qart_only']} times")
    if results['ilp_only'] > 0:
        print(f"ILP succeeded when QArt failed: {results['ilp_only']} times")


def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Compare QArt vs ILP algorithms')
    parser.add_argument('--num-pairs', type=int, default=50, help='Number of string pairs to test (default: 50)')
    parser.add_argument('--string-length', type=int, default=10, help='Length of test strings (default: 10)')
    parser.add_argument('--ecc-level', type=str, default='H', choices=['L', 'M', 'Q', 'H'], 
                       help='ECC level (default: H)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("ALGORITHM COMPARISON TEST")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  Number of pairs: {args.num_pairs}")
    print(f"  String length: {args.string_length}")
    print(f"  ECC level: {args.ecc_level}")
    print()
    
    # Generate test pairs
    print("Generating test string pairs...")
    pairs = generate_string_pairs(args.num_pairs, args.string_length)
    print(f"Generated {len(pairs)} pairs")
    print(f"Sample pairs: {pairs[:3]}")
    print()
    
    # Run tests
    start_time = time.time()
    results = test_algorithms(pairs, ecc_level=args.ecc_level)
    total_time = time.time() - start_time
    
    # Print statistics
    print_statistics(results)
    
    print(f"\n{'='*60}")
    print(f"Total test time: {total_time:.2f} seconds")
    print(f"Average time per pair: {total_time/args.num_pairs:.3f} seconds")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()

