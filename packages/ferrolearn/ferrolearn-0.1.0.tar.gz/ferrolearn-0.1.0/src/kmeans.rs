use ndarray::{Array2, ArrayView1, ArrayView2, Axis};
use numpy::{PyArray1, PyArray2, PyReadonlyArray2};
use pyo3::prelude::*;
use pyo3::Bound;
use rand::prelude::*;
use rand_chacha::ChaCha8Rng;
use rayon::prelude::*;
use std::sync::Arc;

#[pyclass]
pub struct KMeans {
    n_clusters: usize,
    max_iters: usize,
    tol: f64,
    random_state: Option<u64>,
    centers: Option<Arc<Array2<f64>>>,
    n_iter_: usize,
    inertia_: f64,
}

#[pymethods]
impl KMeans {
    #[new]
    #[pyo3(signature = (n_clusters=8, max_iters=300, tol=1e-4, random_state=None))]
    pub fn new(
        n_clusters: usize,
        max_iters: usize,
        tol: f64,
        random_state: Option<u64>,
    ) -> Self {
        KMeans {
            n_clusters,
            max_iters,
            tol,
            random_state,
            centers: None,
            n_iter_: 0,
            inertia_: 0.0,
        }
    }

    pub fn fit<'py>(&mut self, py: Python<'py>, x: PyReadonlyArray2<'py, f64>) -> PyResult<()> {
        let data = x.as_array();
        let n_samples = data.nrows();
        let n_features = data.ncols();

        if n_samples < self.n_clusters {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "n_samples < n_clusters",
            ));
        }

        let mut rng = match self.random_state {
            Some(seed) => ChaCha8Rng::seed_from_u64(seed),
            None => ChaCha8Rng::from_entropy(),
        };

        // Initialize centers using K-Means++
        let mut centers = self.init_centers(&data, &mut rng);
        let mut prev_inertia = f64::INFINITY;

        for iter in 0..self.max_iters {
            // Allow Python to handle signals (e.g., Ctrl+C)
            py.check_signals()?;

            // Assign points to nearest center
            let new_labels: Vec<usize> = (0..n_samples)
                .into_par_iter()
                .map(|i| {
                    let point = data.row(i);
                    nearest_center(&point, &centers)
                })
                .collect();

            // Update centers
            let mut new_centers = Array2::<f64>::zeros((self.n_clusters, n_features));
            let mut counts = vec![0usize; self.n_clusters];

            for (i, &label) in new_labels.iter().enumerate() {
                new_centers.row_mut(label).scaled_add(1.0, &data.row(i));
                counts[label] += 1;
            }

            // Compute mean
            for k in 0..self.n_clusters {
                if counts[k] > 0 {
                    new_centers.row_mut(k).mapv_inplace(|x| x / counts[k] as f64);
                } else {
                    // Handle empty cluster by reinitializing
                    let idx = random_index(n_samples, &mut rng);
                    new_centers.row_mut(k).assign(&data.row(idx));
                }
            }

            // Compute inertia
            let inertia: f64 = new_labels
                .par_iter()
                .enumerate()
                .map(|(i, &label)| {
                    let point = data.row(i);
                    let center = new_centers.row(label);
                    squared_euclidean_distance(&point, &center)
                })
                .sum();

            // Check convergence
            if (prev_inertia - inertia).abs() < self.tol {
                self.n_iter_ = iter + 1;
                self.inertia_ = inertia;
                centers = new_centers;
                break;
            }

            prev_inertia = inertia;
            centers = new_centers;
            self.n_iter_ = iter + 1;
            self.inertia_ = inertia;
        }

        self.centers = Some(Arc::new(centers));
        Ok(())
    }

    pub fn predict<'py>(
        &self,
        py: Python<'py>,
        x: PyReadonlyArray2<'py, f64>,
    ) -> PyResult<Bound<'py, PyAny>> {
        if self.centers.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Model not fitted yet. Call fit() first.",
            ));
        }

        let data = x.as_array();
        let centers = self.centers.as_ref().unwrap();
        
        let labels: Vec<i32> = (0..data.nrows())
            .into_par_iter()
            .map(|i| {
                let point = data.row(i);
                nearest_center(&point, centers) as i32
            })
            .collect();

        Ok(PyArray1::<i32>::from_vec_bound(py, labels).into_any())
    }

    pub fn fit_predict<'py>(
        &mut self,
        py: Python<'py>,
        x: PyReadonlyArray2<'py, f64>,
    ) -> PyResult<Bound<'py, PyAny>> {
        self.fit(py, x.clone())?;
        self.predict(py, x)
    }

    #[getter]
    pub fn cluster_centers_<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyAny>>> {
        match &self.centers {
            Some(centers) => Ok(Some(PyArray2::<f64>::from_owned_array_bound(py, centers.as_ref().clone()).into_any())),
            None => Ok(None),
        }
    }

    #[getter]
    pub fn n_iter_(&self) -> usize {
        self.n_iter_
    }

    #[getter]
    pub fn inertia_(&self) -> f64 {
        self.inertia_
    }
}

impl KMeans {
    fn init_centers<R: Rng>(&self, data: &ArrayView2<f64>, rng: &mut R) -> Array2<f64> {
        let n_samples = data.nrows();
        let n_features = data.ncols();
        let mut centers = Array2::<f64>::zeros((self.n_clusters, n_features));
        
        // K-Means++ initialization
        let first_idx = rng.gen_range(0..n_samples);
        centers.row_mut(0).assign(&data.row(first_idx));

        let mut distances = vec![f64::INFINITY; n_samples];

        for k in 1..self.n_clusters {
            // Update distances to nearest center
            for i in 0..n_samples {
                let point = data.row(i);
                let dist = squared_euclidean_distance(&point, &centers.row(k - 1));
                if dist < distances[i] {
                    distances[i] = dist;
                }
            }

            // Sample next center with probability proportional to squared distance
            let total_dist: f64 = distances.iter().sum();
            if total_dist == 0.0 {
                // All points are already centers, pick random
                let idx = rng.gen_range(0..n_samples);
                centers.row_mut(k).assign(&data.row(idx));
                continue;
            }
            let mut cumsum = 0.0;
            let threshold: f64 = rng.gen::<f64>() * total_dist;

            for (i, &dist) in distances.iter().enumerate() {
                cumsum += dist;
                if cumsum >= threshold {
                    centers.row_mut(k).assign(&data.row(i));
                    break;
                }
            }
        }

        centers
    }
}

fn nearest_center(point: &ArrayView1<f64>, centers: &Array2<f64>) -> usize {
    let mut min_dist = f64::INFINITY;
    let mut nearest = 0;

    for (k, center) in centers.axis_iter(Axis(0)).enumerate() {
        let dist = squared_euclidean_distance(point, &center);
        if dist < min_dist {
            min_dist = dist;
            nearest = k;
        }
    }

    nearest
}

fn squared_euclidean_distance(
    a: &ArrayView1<f64>,
    b: &ArrayView1<f64>,
) -> f64 {
    a.iter()
        .zip(b.iter())
        .map(|(x, y)| {
            let diff = x - y;
            diff * diff
        })
        .sum()
}

fn random_index<R: Rng>(max: usize, rng: &mut R) -> usize {
    rng.gen_range(0..max)
}