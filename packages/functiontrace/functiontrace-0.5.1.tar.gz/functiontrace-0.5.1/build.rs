fn main() -> std::io::Result<()> {
    println!("cargo::rerun-if-changed=pyproject.toml");

    // Read pyproject.toml to expose our version to the Rust extension
    let pyproject = std::fs::read_to_string("pyproject.toml")?
        .parse::<toml::Table>()
        .expect("pyproject.toml is valid toml");
    let project = pyproject
        .get("project")
        .and_then(|p| p.as_table())
        .expect("project field is present in pyproject.toml");

    let version = project
        .get("version")
        .and_then(|v| v.as_str())
        .expect("version field is present in pyproject.toml");
    println!("cargo::rustc-env=PACKAGE_VERSION={}", version);

    let min_python = project
        .get("requires-python")
        .and_then(|v| v.as_str())
        .and_then(|v| v.strip_prefix(">=3."))
        .expect("requires-python field is present in pyproject.toml");
    println!("cargo::rustc-env=MIN_PYTHON_VERSION={}", min_python);

    // Figure out which Python version we're building for
    pyo3_build_config::use_pyo3_cfgs();

    Ok(())
}
