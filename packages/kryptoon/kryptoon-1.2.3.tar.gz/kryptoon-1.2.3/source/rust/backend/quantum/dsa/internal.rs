// IMPORT
use oqs::sig::{Algorithm, Sig};
use pyo3::exceptions::*;
use pyo3::prelude::*;

// MAIN
fn dsaalgorithm(name: &str) -> Result<Sig, PyErr> {
    let algorithm = match name {
        "CrossRsdp128Balanced" => Algorithm::CrossRsdp128Balanced,
        "CrossRsdp128Fast" => Algorithm::CrossRsdp128Fast,
        "CrossRsdp128Small" => Algorithm::CrossRsdp128Small,
        "CrossRsdp192Balanced" => Algorithm::CrossRsdp192Balanced,
        "CrossRsdp192Fast" => Algorithm::CrossRsdp192Fast,
        "CrossRsdp192Small" => Algorithm::CrossRsdp192Small,
        "CrossRsdp256Balanced" => Algorithm::CrossRsdp256Balanced,
        "CrossRsdp256Fast" => Algorithm::CrossRsdp256Fast,
        "CrossRsdp256Small" => Algorithm::CrossRsdp256Small,
        "CrossRsdpg128Balanced" => Algorithm::CrossRsdpg128Balanced,
        "CrossRsdpg128Fast" => Algorithm::CrossRsdpg128Fast,
        "CrossRsdpg128Small" => Algorithm::CrossRsdpg128Small,
        "CrossRsdpg192Balanced" => Algorithm::CrossRsdpg192Balanced,
        "CrossRsdpg192Fast" => Algorithm::CrossRsdpg192Fast,
        "CrossRsdpg192Small" => Algorithm::CrossRsdpg192Small,
        "CrossRsdpg256Balanced" => Algorithm::CrossRsdpg256Balanced,
        "CrossRsdpg256Fast" => Algorithm::CrossRsdpg256Fast,
        "CrossRsdpg256Small" => Algorithm::CrossRsdpg256Small,
        //
        "Dilithium2" => Algorithm::Dilithium2,
        "Dilithium3" => Algorithm::Dilithium3,
        "Dilithium5" => Algorithm::Dilithium5,
        //
        "Falcon512" => Algorithm::Falcon512,
        "Falcon1024" => Algorithm::Falcon1024,
        //
        "Mayo1" => Algorithm::Mayo1,
        "Mayo2" => Algorithm::Mayo2,
        "Mayo3" => Algorithm::Mayo3,
        "Mayo5" => Algorithm::Mayo5,
        //
        "MlDsa44" => Algorithm::MlDsa44,
        "MlDsa65" => Algorithm::MlDsa65,
        "MlDsa87" => Algorithm::MlDsa87,
        //
        "SphincsSha2128fSimple" => Algorithm::SphincsSha2128fSimple,
        "SphincsSha2128sSimple" => Algorithm::SphincsSha2128sSimple,
        "SphincsSha2192fSimple" => Algorithm::SphincsSha2192fSimple,
        "SphincsSha2192sSimple" => Algorithm::SphincsSha2192sSimple,
        "SphincsSha2256fSimple" => Algorithm::SphincsSha2256fSimple,
        "SphincsSha2256sSimple" => Algorithm::SphincsSha2256sSimple,
        "SphincsShake128fSimple" => Algorithm::SphincsShake128fSimple,
        "SphincsShake128sSimple" => Algorithm::SphincsShake128sSimple,
        "SphincsShake192fSimple" => Algorithm::SphincsShake192fSimple,
        "SphincsShake192sSimple" => Algorithm::SphincsShake192sSimple,
        "SphincsShake256fSimple" => Algorithm::SphincsShake256fSimple,
        "SphincsShake256sSimple" => Algorithm::SphincsShake256sSimple,
        //
        "UovOvIII" => Algorithm::UovOvIII,
        "UovOvIIIPkc" => Algorithm::UovOvIIIPkc,
        "UovOvIIIPkcSkc" => Algorithm::UovOvIIIPkcSkc,
        "UovOvIp" => Algorithm::UovOvIp,
        "UovOvIpPkc" => Algorithm::UovOvIpPkc,
        "UovOvIpPkcSkc" => Algorithm::UovOvIpPkcSkc,
        "UovOvIs" => Algorithm::UovOvIs,
        "UovOvIsPkc" => Algorithm::UovOvIsPkc,
        "UovOvIsPkcSkc" => Algorithm::UovOvIsPkcSkc,
        "UovOvV" => Algorithm::UovOvV,
        "UovOvVPkc" => Algorithm::UovOvVPkc,
        "UovOvVPkcSkc" => Algorithm::UovOvVPkcSkc,
        _ => return Err(PyRuntimeError::new_err(format!("Unsupported algorithm: {}", name))),
    };
    let result = Sig::new(algorithm)
        .map_err(|problem| PyRuntimeError::new_err(format!("Algorithm failure: {}", problem)))?;
    //
    Ok(result)
}

#[pyfunction]
pub fn dsakeygen(name: &str) -> PyResult<(Vec<u8>, Vec<u8>)> {
    let algorithm = dsaalgorithm(name)?;
    let (publickey, secretkey) = algorithm
        .keypair()
        .map_err(|problem| PyRuntimeError::new_err(format!("Algorithm failure: {}", problem)))?;
    //
    Ok((secretkey.into_vec(), publickey.into_vec()))
}

#[pyfunction]
pub fn dsasign(name: &str, secretkey: &[u8], message: &[u8]) -> PyResult<Vec<u8>> {
    let algorithm = dsaalgorithm(name)?;
    let secretkey = algorithm
        .secret_key_from_bytes(secretkey)
        .ok_or_else(|| PyRuntimeError::new_err("Invalid SecretKey"))?;
    let signature = algorithm.sign(message, secretkey)
        .map_err(|problem| PyRuntimeError::new_err(format!("Algorithm failure: {}", problem)))?;
    //
    Ok(signature.into_vec())
}

#[pyfunction]
pub fn dsaverify(name: &str, publickey: &[u8], signature: &[u8], message: &[u8]) -> PyResult<bool> {
    let algorithm = dsaalgorithm(name)?;
    let publickey = algorithm
        .public_key_from_bytes(publickey)
        .ok_or_else(|| PyRuntimeError::new_err("Invalid PublicKey"))?;
    let signature = algorithm
        .signature_from_bytes(signature)
        .ok_or_else(|| PyRuntimeError::new_err("Invalid Signature"))?;
    let valid = algorithm.verify(message, signature, publickey).is_ok();
    //
    Ok(valid)
}
