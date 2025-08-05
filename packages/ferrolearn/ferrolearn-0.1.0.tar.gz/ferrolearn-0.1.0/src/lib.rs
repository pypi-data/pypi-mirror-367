use pyo3::prelude::*;

mod kmeans;
use kmeans::KMeans;

/// ferrolearn - High-performance machine learning library powered by Rust
#[pymodule]
fn ferrolearn(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<KMeans>()?;
    m.add("__version__", "0.1.0")?;
    Ok(())
}