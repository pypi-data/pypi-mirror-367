#[cfg(feature = "python")]
use pyo3::prelude::*;
#[cfg(feature = "python")]
use pyo3::types::PyDict;
#[cfg(feature = "python")]
use std::collections::HashMap;
#[cfg(feature = "python")]
use std::path::Path;

#[cfg(feature = "python")]
use crate::XacroProcessor;

#[cfg(feature = "python")]
#[pyclass]
pub struct PyXacroProcessor {
    processor: XacroProcessor,
}

#[cfg(feature = "python")]
#[pymethods]
impl PyXacroProcessor {
    #[new]
    fn new(verbosity: Option<u8>) -> Self {
        Self {
            processor: XacroProcessor::new(verbosity.unwrap_or(1)),
        }
    }

    fn set_format_output(&mut self, format: bool) {
        self.processor.set_format_output(format);
    }

    fn set_remove_first_joint(&mut self, remove: bool) {
        self.processor.set_remove_first_joint(remove);
    }

    fn process_file(&mut self, input_file: &str, mappings: Option<&PyDict>) -> PyResult<String> {
        let mappings = if let Some(dict) = mappings {
            let mut map = HashMap::new();
            for (key, value) in dict {
                let key: String = key.extract()?;
                let value: String = value.extract()?;
                map.insert(key, value);
            }
            Some(map)
        } else {
            None
        };

        match self.processor.process_file(Path::new(input_file), mappings) {
            Ok(doc) => Ok(self.processor.element_to_string(&doc)),
            Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!("{}", e))),
        }
    }

    fn process_string(&mut self, xml_content: &str, mappings: Option<&PyDict>) -> PyResult<String> {
        let mappings = if let Some(dict) = mappings {
            let mut map = HashMap::new();
            for (key, value) in dict {
                let key: String = key.extract()?;
                let value: String = value.extract()?;
                map.insert(key, value);
            }
            Some(map)
        } else {
            None
        };

        match self.processor.process_string(xml_content, mappings) {
            Ok(doc) => Ok(self.processor.element_to_string(&doc)),
            Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!("{}", e))),
        }
    }
}

#[cfg(feature = "python")]
#[pyfunction]
fn xacro_to_string(
    input_file: &str,
    mappings: Option<&PyDict>,
    verbosity: Option<u8>,
    format_output: Option<bool>,
    remove_first_joint: Option<bool>,
) -> PyResult<String> {
    let mut processor = XacroProcessor::new(verbosity.unwrap_or(1));
    processor.set_format_output(format_output.unwrap_or(false));
    processor.set_remove_first_joint(remove_first_joint.unwrap_or(false));

    let mappings = if let Some(dict) = mappings {
        let mut map = HashMap::new();
        for (key, value) in dict {
            let key: String = key.extract()?;
            let value: String = value.extract()?;
            map.insert(key, value);
        }
        Some(map)
    } else {
        None
    };

    match processor.process_file(Path::new(input_file), mappings) {
        Ok(doc) => Ok(processor.element_to_string(&doc)),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!("{}", e))),
    }
}

#[cfg(feature = "python")]
#[pyfunction]
fn xacro_from_string(
    xml_content: &str,
    mappings: Option<&PyDict>,
    verbosity: Option<u8>,
    format_output: Option<bool>,
    remove_first_joint: Option<bool>,
) -> PyResult<String> {
    let mut processor = XacroProcessor::new(verbosity.unwrap_or(1));
    processor.set_format_output(format_output.unwrap_or(false));
    processor.set_remove_first_joint(remove_first_joint.unwrap_or(false));

    let mappings = if let Some(dict) = mappings {
        let mut map = HashMap::new();
        for (key, value) in dict {
            let key: String = key.extract()?;
            let value: String = value.extract()?;
            map.insert(key, value);
        }
        Some(map)
    } else {
        None
    };

    match processor.process_string(xml_content, mappings) {
        Ok(doc) => Ok(processor.element_to_string(&doc)),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!("{}", e))),
    }
}

#[cfg(feature = "python")]
#[pyfunction]
fn xacro_to_file(
    input_file: &str,
    output_file: &str,
    mappings: Option<&PyDict>,
    verbosity: Option<u8>,
    format_output: Option<bool>,
    remove_first_joint: Option<bool>,
) -> PyResult<()> {
    let result = xacro_to_string(
        input_file,
        mappings,
        verbosity,
        format_output,
        remove_first_joint,
    )?;

    // Create output directory if needed
    if let Some(parent) = Path::new(output_file).parent() {
        std::fs::create_dir_all(parent).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to create directory: {}", e))
        })?;
    }

    std::fs::write(output_file, result).map_err(|e| {
        pyo3::exceptions::PyIOError::new_err(format!("Failed to write file: {}", e))
    })?;

    Ok(())
}

#[cfg(feature = "python")]
#[pymodule]
fn zacro(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyXacroProcessor>()?;
    m.add_function(wrap_pyfunction!(xacro_to_string, m)?)?;
    m.add_function(wrap_pyfunction!(xacro_from_string, m)?)?;
    m.add_function(wrap_pyfunction!(xacro_to_file, m)?)?;
    Ok(())
}
