import numpy as np
import pytest
from ferrolearn import KMeans
from sklearn.cluster import KMeans as SklearnKMeans
from sklearn.datasets import make_blobs
from sklearn.metrics import adjusted_rand_score


class TestKMeans:
    def test_basic_functionality(self):
        """Test basic K-Means functionality"""
        # Generate simple clustered data
        X, y_true = make_blobs(n_samples=300, centers=3, n_features=2, random_state=42)
        
        # Fit ferrolearn KMeans
        kmeans = KMeans(n_clusters=3, random_state=42)
        kmeans.fit(X)
        
        # Get predictions
        labels = kmeans.predict(X)
        
        # Check basic properties
        assert labels.shape == (300,)
        assert len(np.unique(labels)) == 3
        assert kmeans.cluster_centers_.shape == (3, 2)
        assert kmeans.n_iter_ > 0
        assert kmeans.inertia_ > 0
    
    def test_fit_predict(self):
        """Test fit_predict method"""
        X, _ = make_blobs(n_samples=100, centers=2, n_features=2, random_state=42)
        
        kmeans = KMeans(n_clusters=2, random_state=42)
        labels = kmeans.fit_predict(X)
        
        assert labels.shape == (100,)
        assert len(np.unique(labels)) == 2
    
    def test_convergence(self):
        """Test that algorithm converges properly"""
        X, _ = make_blobs(n_samples=200, centers=4, n_features=3, random_state=42)
        
        kmeans = KMeans(n_clusters=4, max_iters=300, tol=1e-4, random_state=42)
        kmeans.fit(X)
        
        # Should converge before max_iters
        assert kmeans.n_iter_ < 300
    
    def test_empty_cluster_handling(self):
        """Test handling of empty clusters"""
        # Create data with clear clusters
        X = np.array([[0, 0], [0, 1], [10, 10], [10, 11]], dtype=np.float64)
        
        # Try to create more clusters than natural groups
        kmeans = KMeans(n_clusters=3, random_state=42)
        kmeans.fit(X)
        
        # Should still produce valid results
        assert kmeans.cluster_centers_.shape == (3, 2)
        assert not np.any(np.isnan(kmeans.cluster_centers_))
    
    def test_error_cases(self):
        """Test error handling"""
        X = np.random.rand(5, 2)
        
        # More clusters than samples
        kmeans = KMeans(n_clusters=10)
        with pytest.raises(ValueError, match="n_samples < n_clusters"):
            kmeans.fit(X)
        
        # Predict before fit
        kmeans = KMeans(n_clusters=2)
        with pytest.raises(ValueError, match="Model not fitted"):
            kmeans.predict(X)
    
    def test_reproducibility(self):
        """Test that results are reproducible with random_state"""
        X, _ = make_blobs(n_samples=100, centers=3, n_features=2, random_state=42)
        
        # Fit twice with same random_state
        kmeans1 = KMeans(n_clusters=3, random_state=42)
        labels1 = kmeans1.fit_predict(X)
        
        kmeans2 = KMeans(n_clusters=3, random_state=42)
        labels2 = kmeans2.fit_predict(X)
        
        # Results should be identical
        assert np.array_equal(labels1, labels2)
        assert np.allclose(kmeans1.cluster_centers_, kmeans2.cluster_centers_)
    
    def test_comparison_with_sklearn(self):
        """Compare results with scikit-learn"""
        X, y_true = make_blobs(n_samples=500, centers=5, n_features=10, 
                               cluster_std=0.5, random_state=42)
        
        # Ferrolearn
        ferro_kmeans = KMeans(n_clusters=5, random_state=42, max_iters=100)
        ferro_labels = ferro_kmeans.fit_predict(X)
        
        # Scikit-learn
        sk_kmeans = SklearnKMeans(n_clusters=5, random_state=42, max_iter=100, 
                                  init='k-means++', n_init=1)
        sk_labels = sk_kmeans.fit_predict(X)
        
        # Compare clustering quality
        ferro_score = adjusted_rand_score(y_true, ferro_labels)
        sk_score = adjusted_rand_score(y_true, sk_labels)
        
        # Both should achieve good clustering
        assert ferro_score > 0.8
        assert sk_score > 0.8
        
        # Results should be similar (not necessarily identical due to implementation differences)
        assert abs(ferro_score - sk_score) < 0.2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])