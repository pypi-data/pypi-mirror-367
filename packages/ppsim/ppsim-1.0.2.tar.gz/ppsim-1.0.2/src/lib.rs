use pyo3::prelude::*;

pub mod simulator;
pub mod simulator_sequential;
pub mod urn;
pub mod util;

use simulator::SimulatorMultiBatch;
use simulator_sequential::SimulatorSequentialArray;

/// A Python module implemented in Rust.
#[pymodule]
fn ppsim_rust(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SimulatorSequentialArray>()?;
    m.add_class::<SimulatorMultiBatch>()?;
    Ok(())
}

// In a file like src/profiling.rs
#[cfg(feature = "flm")]
pub use flame;

// mock crate with no-op functions when not profiling
#[cfg(not(feature = "flm"))]
pub mod flame {
    use std::io::Write;

    #[derive(Debug, Clone)]
    pub struct Span {
        pub name: String,
        pub delta: u64,
        pub children: Vec<Span>,
    }
    // Define no-op versions of the flame functions you use
    pub fn start(_name: &str) {}
    pub fn end(_name: &str) {}
    pub fn spans() -> Vec<Span> {
        vec![]
    }
    pub fn dump_json<W: Write>(_out: &mut W) -> std::io::Result<()> {
        Ok(())
    }
    pub fn dump_html<W: Write>(_out: W) -> std::io::Result<()> {
        Ok(())
    }
    pub fn dump_stdout() {}
}
