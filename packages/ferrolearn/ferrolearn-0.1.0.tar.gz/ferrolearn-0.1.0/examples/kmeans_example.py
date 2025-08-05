"""
Simple example demonstrating ferrolearn K-Means usage
"""

import matplotlib.pyplot as plt
from ferrolearn import KMeans
from sklearn.datasets import make_blobs
import time


def main():
    print("ferrolearn K-Means Example")
    print("=" * 50)
    
    # Generate sample data
    print("\nGenerating sample data...")
    n_samples = 5000
    n_features = 2
    n_clusters = 5
    
    X, y_true = make_blobs(
        n_samples=n_samples,
        n_features=n_features,
        centers=n_clusters,
        cluster_std=0.6,
        random_state=42
    )
    
    print(f"Data shape: {X.shape}")
    print(f"Number of clusters: {n_clusters}")
    
    # Fit K-Means
    print("\nFitting K-Means model...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    
    start_time = time.time()
    kmeans.fit(X)
    fit_time = time.time() - start_time
    
    print(f"Fitting completed in {fit_time:.3f} seconds")
    print(f"Number of iterations: {kmeans.n_iter_}")
    print(f"Final inertia: {kmeans.inertia_:.2f}")
    
    # Get predictions
    labels = kmeans.predict(X)
    centers = kmeans.cluster_centers_
    
    # Visualize results
    print("\nCreating visualization...")
    plt.figure(figsize=(10, 8))
    
    # Plot points
    scatter = plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis', 
                         alpha=0.6, edgecolors='k', linewidth=0.5)
    
    # Plot centers
    plt.scatter(centers[:, 0], centers[:, 1], c='red', s=200, alpha=0.8,
               edgecolors='k', linewidth=2, marker='*', label='Centers')
    
    plt.title(f'K-Means Clustering (n_clusters={n_clusters})', fontsize=16)
    plt.xlabel('Feature 1', fontsize=12)
    plt.ylabel('Feature 2', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.colorbar(scatter, label='Cluster')
    
    plt.tight_layout()
    plt.savefig('kmeans_example.png', dpi=150, bbox_inches='tight')
    print("Visualization saved as 'kmeans_example.png'")
    plt.show()
    
    # Performance comparison
    print("\n" + "=" * 50)
    print("Quick Performance Comparison")
    print("=" * 50)
    
    from sklearn.cluster import KMeans as SklearnKMeans
    
    # Larger dataset for comparison
    X_large, _ = make_blobs(n_samples=50000, n_features=50, centers=10, random_state=42)
    
    # ferrolearn
    print("\nferrolearn K-Means:")
    ferro_kmeans = KMeans(n_clusters=10, random_state=42, max_iters=100)
    start = time.time()
    ferro_kmeans.fit(X_large)
    ferro_time = time.time() - start
    print(f"  Time: {ferro_time:.3f}s")
    print(f"  Iterations: {ferro_kmeans.n_iter_}")
    
    # scikit-learn
    print("\nscikit-learn K-Means:")
    sk_kmeans = SklearnKMeans(n_clusters=10, random_state=42, max_iter=100, n_init=1)
    start = time.time()
    sk_kmeans.fit(X_large)
    sk_time = time.time() - start
    print(f"  Time: {sk_time:.3f}s")
    print(f"  Iterations: {sk_kmeans.n_iter_}")
    
    print(f"\nSpeedup: {sk_time/ferro_time:.2f}x faster!")


if __name__ == "__main__":
    main()