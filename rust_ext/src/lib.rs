// hermes-fast: Rust hot-path extensions for hermes-agent.
//
// Phase 3 (perf): three pyfunctions exposed to Python via PyO3.
//
// * `parse_tool_call_delta(buf)` - incremental JSON parser for streaming
//   tool-call deltas. Returns (ok, value, consumed_bytes).
// * `estimate_tokens(text)` - ~4-char-per-token heuristic mirror of the
//   pure-Python implementation in agent.context_compressor.
// * `truncate_messages_to_limit(messages_json, max_tokens)` - trim oldest
//   non-system messages until total estimated tokens fit max_tokens.
//
// Build: `cd rust_ext && maturin develop --release`.
// Without the extension built, agent._hermes_fast falls back to pure
// Python so the agent keeps working unchanged.

use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyString};
use serde::{Deserialize, Serialize};

#[pyfunction]
fn parse_tool_call_delta(py: Python<'_>, buf: &str) -> PyResult<(bool, PyObject, usize)> {
    let trimmed = buf.trim_start();
    if trimmed.is_empty() {
        return Ok((false, py.None(), 0));
    }

    let leading_ws = buf.len() - trimmed.len();
    let mut de = serde_json::Deserializer::from_str(trimmed).into_iter::<serde_json::Value>();
    match de.next() {
        Some(Ok(value)) => {
            let consumed = leading_ws + de.byte_offset();
            let py_obj = json_value_to_py(py, &value)?;
            Ok((true, py_obj, consumed))
        }
        Some(Err(err)) if err.is_eof() => Ok((false, py.None(), 0)),
        Some(Err(err)) => Err(pyo3::exceptions::PyValueError::new_err(err.to_string())),
        None => Ok((false, py.None(), 0)),
    }
}

#[pyfunction]
fn estimate_tokens(text: &str) -> usize {
    if text.is_empty() {
        0
    } else {
        (text.len() + 3) / 4
    }
}

#[derive(Serialize, Deserialize)]
struct Message {
    #[serde(default)]
    role: String,
    #[serde(default)]
    content: serde_json::Value,
    #[serde(flatten)]
    rest: serde_json::Map<String, serde_json::Value>,
}

fn message_token_cost(msg: &Message) -> usize {
    let role_tokens = estimate_tokens(&msg.role);
    let content_tokens = match &msg.content {
        serde_json::Value::String(s) => estimate_tokens(s),
        serde_json::Value::Array(items) => items
            .iter()
            .map(|item| match item {
                serde_json::Value::String(s) => estimate_tokens(s),
                serde_json::Value::Object(obj) => obj
                    .values()
                    .map(|v| match v {
                        serde_json::Value::String(s) => estimate_tokens(s),
                        other => estimate_tokens(&other.to_string()),
                    })
                    .sum(),
                other => estimate_tokens(&other.to_string()),
            })
            .sum(),
        serde_json::Value::Null => 0,
        other => estimate_tokens(&other.to_string()),
    };
    role_tokens + content_tokens + 4
}

#[pyfunction]
fn truncate_messages_to_limit(
    py: Python<'_>,
    messages_json: &str,
    max_tokens: usize,
) -> PyResult<Py<PyString>> {
    let mut messages: Vec<Message> = serde_json::from_str(messages_json)
        .map_err(|err| pyo3::exceptions::PyValueError::new_err(err.to_string()))?;

    let mut total: usize = messages.iter().map(message_token_cost).sum();

    if total <= max_tokens {
        let out = serde_json::to_string(&messages)
            .map_err(|err| pyo3::exceptions::PyValueError::new_err(err.to_string()))?;
        return Ok(PyString::new_bound(py, &out).into());
    }

    let mut idx = 0;
    while total > max_tokens && idx < messages.len() {
        if messages[idx].role == "system" {
            idx += 1;
            continue;
        }
        let cost = message_token_cost(&messages[idx]);
        messages.remove(idx);
        total = total.saturating_sub(cost);
    }

    let out = serde_json::to_string(&messages)
        .map_err(|err| pyo3::exceptions::PyValueError::new_err(err.to_string()))?;
    Ok(PyString::new_bound(py, &out).into())
}

fn json_value_to_py(py: Python<'_>, value: &serde_json::Value) -> PyResult<PyObject> {
    let buf = serde_json::to_vec(value)
        .map_err(|err| pyo3::exceptions::PyValueError::new_err(err.to_string()))?;
    let bytes = PyBytes::new_bound(py, &buf);
    let json_mod = py.import_bound("json")?;
    let obj = json_mod.call_method1("loads", (bytes,))?;
    Ok(obj.into())
}

#[pymodule]
fn hermes_fast(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_tool_call_delta, m)?)?;
    m.add_function(wrap_pyfunction!(estimate_tokens, m)?)?;
    m.add_function(wrap_pyfunction!(truncate_messages_to_limit, m)?)?;
    Ok(())
}
