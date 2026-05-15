use pyo3::prelude::*;

pub mod mcrypto;
pub mod mtopy;
pub mod mblockchain;

#[pyfunction]
fn register(password: String) -> PyResult<(Vec<u8>, Vec<u8>, String)> {
    Ok(mtopy::register(&password))
}

#[pymodule]
fn rust_services(_py: Python, m: &Bound<PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(register, m)?)?;
    Ok(())
}
