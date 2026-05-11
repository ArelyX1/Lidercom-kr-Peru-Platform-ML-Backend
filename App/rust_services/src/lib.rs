use pyo3::{PyResult, pyfunction};

pub mod mcrypto;
pub mod mtopy;
pub mod mblockchain;

#[pyfunction]
fn register(password: String) -> PyResult<(Vec<u8>, Vec<u8>, Vec<u8>, Vec<u8>, String)> {
    Ok(mtopy::register(&password))    
}