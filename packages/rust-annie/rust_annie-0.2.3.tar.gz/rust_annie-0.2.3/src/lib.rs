pub mod py_index;
pub mod utils;
pub mod index;
mod storage;
pub mod metrics;
mod errors;
pub mod concurrency;
mod backend;
pub mod hnsw_index;
mod index_enum;
mod filters;
pub mod distance_registry;
pub mod monitoring;

// Add GPU module
#[cfg(any(feature = "cuda", feature = "rocm"))]
pub mod gpu;

use crate::py_index::PyIndex;
use pyo3::prelude::*;
use numpy::{PyReadonlyArray1, PyReadonlyArray2,PyUntypedArrayMethods,PyArrayDescrMethods};
use crate::backend::AnnBackend;
use crate::index::AnnIndex;
use crate::metrics::Distance;
use crate::concurrency::ThreadSafeAnnIndex;
use crate::hnsw_index::HnswIndex;
use crate::distance_registry::{register_metric, list_metrics, init_distance_registry};
use crate::monitoring::PyMetricsCollector;
use pyo3::Bound;
use pyo3::types::PyModule;
use crate::hnsw_index::HnswConfig;

#[pyclass(name = "HnswConfig")]
#[derive(Clone)]
pub struct PyHnswConfig {
    #[pyo3(get, set)]
    pub m: usize,
    #[pyo3(get, set)]
    pub ef_construction: usize,
    #[pyo3(get, set)]
    pub ef_search: usize,
    #[pyo3(get, set)]
    pub max_elements: usize,
}

#[pymethods]
impl PyHnswConfig {
    #[new]
    pub fn new(
        m: Option<usize>,
        ef_construction: Option<usize>,
        ef_search: Option<usize>,
        max_elements: Option<usize>,
    ) -> Self {
        let default = HnswConfig::default();
        PyHnswConfig {
            m: m.unwrap_or(default.m),
            ef_construction: ef_construction.unwrap_or(default.ef_construction),
            ef_search: ef_search.unwrap_or(default.ef_search),
            max_elements: max_elements.unwrap_or(default.max_elements),
        }
    }

    #[staticmethod]
    pub fn default() -> Self {
        let default = HnswConfig::default();
        PyHnswConfig {
            m: default.m,
            ef_construction: default.ef_construction,
            ef_search: default.ef_search,
            max_elements: default.max_elements,
        }
    }

    pub fn validate(&self) -> PyResult<()> {
        let config = self.to_config();
        config.validate().map_err(|e| e.into_pyerr())
    }
}

impl PyHnswConfig {
    pub fn to_config(&self) -> HnswConfig {
        HnswConfig {
            m: self.m,
            ef_construction: self.ef_construction,
            ef_search: self.ef_search,
            max_elements: self.max_elements,
        }
    }
}

#[pyclass]
pub struct PyHnswIndex {
    inner: HnswIndex,
}

#[pymethods]
impl PyHnswIndex {
    #[new]
    fn new(dims: usize) -> Self {
        PyHnswIndex {
            inner: HnswIndex::new(dims, Distance::Euclidean()),
        }
    }

    fn add_item(&mut self, item: Vec<f32>) {
        self.inner.add_item(item);
    }

    fn add(&mut self, py: Python, data: PyReadonlyArray2<f32>, ids: PyReadonlyArray1<i64>) -> PyResult<()> {
        if !data.dtype().is_equiv_to(&numpy::dtype::<f32>(py)) {
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>("Input data must be of type f32"));
        }

        if !ids.dtype().is_equiv_to(&numpy::dtype::<i64>(py)) {
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "ids array must be of type i64",
            ));
        }
        
        let dims = self.inner.dims();
        let shape = data.shape();
        if shape.len() != 2 || shape[1] != dims {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Input data must be of shape (n, {})", dims),
            ));
        }

        let data_slice = data.as_slice()?;
        let ids_slice = ids.as_slice()?;
        let n_vectors = shape[0];

        if ids_slice.len() != n_vectors {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "ids length must match number of vectors",
            ));
        }

        for (i, vector) in data_slice.chunks_exact(dims).enumerate() {
            self.inner.insert(vector, ids_slice[i]);
        }
        Ok(())
    }

    fn build(&mut self) {
        self.inner.build();
    }

    fn search(&self, vector: Vec<f32>, k: usize) -> Vec<usize> {
        self.inner.search(&vector, k)
    }

    fn save(&self, path: String) {
        self.inner.save(&path);
    }

    #[staticmethod]
    fn load(_path: String) -> PyResult<Self> {
        Err(PyErr::new::<pyo3::exceptions::PyNotImplementedError, _>(
            "load() is not supported in hnsw-rs v0.3.2",
        ))
    }
}

#[pymodule]
fn rust_annie(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Initialize the distance registry
    init_distance_registry();
    
    m.add_class::<AnnIndex>()?;
    m.add_class::<Distance>()?;
    m.add_class::<ThreadSafeAnnIndex>()?;
    m.add_class::<PyHnswIndex>()?;
    m.add_class::<PyIndex>()?;
    m.add_class::<PyMetricsCollector>()?;
    m.add_class::<PyHnswConfig>()?;
    m.add_function(wrap_pyfunction!(register_metric, m)?)?;
    m.add_function(wrap_pyfunction!(list_metrics, m)?)?;
    Ok(())
}
