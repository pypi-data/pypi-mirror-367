import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ferrolearn import KMeans as FerroKMeans
from sklearn.cluster import KMeans as SklearnKMeans
from sklearn.datasets import make_blobs
import warnings

warnings.filterwarnings('ignore')


def benchmark_kmeans(n_samples, n_features, n_clusters, n_runs=5):
    """Benchmark K-Means implementations"""
    # Generate data
    X, _ = make_blobs(n_samples=n_samples, n_features=n_features, 
                      centers=n_clusters, random_state=42)
    
    # Ferrolearn timing
    ferro_times = []
    for _ in range(n_runs):
        kmeans = FerroKMeans(n_clusters=n_clusters, random_state=42, max_iters=100)
        start = time.time()
        kmeans.fit(X)
        ferro_times.append(time.time() - start)
    
    # Scikit-learn timing
    sklearn_times = []
    for _ in range(n_runs):
        kmeans = SklearnKMeans(n_clusters=n_clusters, random_state=42, 
                              max_iter=100, n_init=1, init='k-means++')
        start = time.time()
        kmeans.fit(X)
        sklearn_times.append(time.time() - start)
    
    return {
        'ferrolearn_mean': np.mean(ferro_times),
        'ferrolearn_std': np.std(ferro_times),
        'sklearn_mean': np.mean(sklearn_times),
        'sklearn_std': np.std(sklearn_times),
        'speedup': np.mean(sklearn_times) / np.mean(ferro_times)
    }


def run_benchmark_suite():
    """Run comprehensive benchmarks"""
    print("Running K-Means benchmarks...\n")
    print("=" * 70)
    print(f"{'Dataset':<30} {'Ferrolearn':<15} {'Scikit-learn':<15} {'Speedup':<10}")
    print("=" * 70)
    
    results = []
    
    # Different benchmark scenarios
    scenarios = [
        # (n_samples, n_features, n_clusters, name)
        (1000, 10, 5, "Small dataset"),
        (10000, 50, 5, "Medium dataset"),
        (10000, 100, 10, "High dimensions"),
        (50000, 50, 20, "Many clusters"),
        (100000, 50, 10, "Large dataset"),
        (100000, 100, 20, "Large + complex"),
    ]
    
    for n_samples, n_features, n_clusters, name in scenarios:
        desc = f"{name} ({n_samples:,}×{n_features})"
        print(f"{desc:<30}", end="", flush=True)
        
        result = benchmark_kmeans(n_samples, n_features, n_clusters)
        
        ferro_time = f"{result['ferrolearn_mean']:.3f}s"
        sklearn_time = f"{result['sklearn_mean']:.3f}s"
        speedup = f"{result['speedup']:.1f}x"
        
        print(f"{ferro_time:<15} {sklearn_time:<15} {speedup:<10}")
        
        results.append({
            'scenario': name,
            'n_samples': n_samples,
            'n_features': n_features,
            'n_clusters': n_clusters,
            **result
        })
    
    print("=" * 70)
    
    # Save results
    df = pd.DataFrame(results)
    df.to_csv('benchmark_results.csv', index=False)
    
    # Create visualization
    create_benchmark_plot(df)
    
    return df


def create_benchmark_plot(df):
    """Create benchmark visualization"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Time comparison
    x = np.arange(len(df))
    width = 0.35
    
    ax1.bar(x - width/2, df['ferrolearn_mean'], width, label='ferrolearn',
            yerr=df['ferrolearn_std'], capsize=5, color='#1f77b4')
    ax1.bar(x + width/2, df['sklearn_mean'], width, label='scikit-learn',
            yerr=df['sklearn_std'], capsize=5, color='#ff7f0e')
    
    ax1.set_xlabel('Scenario')
    ax1.set_ylabel('Time (seconds)')
    ax1.set_title('K-Means Performance Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df['scenario'], rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Speedup chart
    ax2.bar(x, df['speedup'], color='#2ca02c')
    ax2.axhline(y=1, color='red', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Scenario')
    ax2.set_ylabel('Speedup Factor')
    ax2.set_title('ferrolearn Speedup vs scikit-learn')
    ax2.set_xticks(x)
    ax2.set_xticklabels(df['scenario'], rotation=45, ha='right')
    ax2.grid(True, alpha=0.3)
    
    # Add speedup values on bars
    for i, v in enumerate(df['speedup']):
        ax2.text(i, v + 0.1, f'{v:.1f}x', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('benchmark_results.png', dpi=150, bbox_inches='tight')
    print("\nBenchmark plot saved as 'benchmark_results.png'")


def benchmark_scaling():
    """Benchmark scaling with data size"""
    print("\nRunning scaling benchmark...")
    
    sizes = [1000, 5000, 10000, 25000, 50000, 75000, 100000]
    ferro_times = []
    sklearn_times = []
    
    for size in sizes:
        print(f"  Testing size: {size:,}")
        result = benchmark_kmeans(size, 50, 10, n_runs=3)
        ferro_times.append(result['ferrolearn_mean'])
        sklearn_times.append(result['sklearn_mean'])
    
    # Plot scaling
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, ferro_times, 'o-', label='ferrolearn', linewidth=2, markersize=8)
    plt.plot(sizes, sklearn_times, 's-', label='scikit-learn', linewidth=2, markersize=8)
    plt.xlabel('Number of Samples')
    plt.ylabel('Time (seconds)')
    plt.title('K-Means Scaling with Dataset Size')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xscale('log')
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig('scaling_benchmark.png', dpi=150, bbox_inches='tight')
    print("Scaling plot saved as 'scaling_benchmark.png'")


if __name__ == "__main__":
    print("ferrolearn K-Means Benchmark Suite")
    print("=" * 70)
    print()
    
    # Run main benchmarks
    results = run_benchmark_suite()
    
    # Run scaling benchmark
    benchmark_scaling()
    
    print("\nBenchmark complete!")
    print(f"\nAverage speedup: {results['speedup'].mean():.2f}x")
    print(f"Best speedup: {results['speedup'].max():.2f}x on {results.loc[results['speedup'].idxmax(), 'scenario']}")