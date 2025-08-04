use ed25519_dalek::Signature;
use ed25519_dalek::Signer;
use ed25519_dalek::SigningKey as Ed25519SigningKey;
use ed25519_dalek::VerifyingKey as Ed25519VerifyingKey;
use ed25519_dalek::Verifier as Ed25519Verifier;
use pqcrypto_falcon::falcon1024;
use pqcrypto_falcon::falcon512;
use pqcrypto_traits::sign::{DetachedSignature, PublicKey, SecretKey};
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use pyo3::Bound;
use rand::rngs::OsRng;

#[cfg(feature="rsa_dep")]
use rsa::pkcs1::{
    DecodeRsaPrivateKey, DecodeRsaPublicKey, EncodeRsaPrivateKey, EncodeRsaPublicKey,
};
#[cfg(feature="rsa_dep")]
use rsa::pkcs1v15::{SigningKey, VerifyingKey};
#[cfg(feature="rsa_dep")]
use rsa::sha2::Sha256;
#[cfg(feature="rsa_dep")]
use rsa::signature::{Keypair, RandomizedSigner, SignatureEncoding};
#[cfg(feature="rsa_dep")]
use rsa::{RsaPrivateKey, RsaPublicKey};


#[cfg(feature = "rsa_dep")]
#[pyclass]
#[deprecated(note = "RSA is insecure and deprecated due to timing attacks. Use Ed25519 or Falcon.")]
struct Rsa {}

#[pyclass]
struct Ed25519 {}

#[pyclass]
struct Falcon512 {}

#[pyclass]
struct Falcon1024 {}


#[cfg(feature = "rsa_dep")]
#[pymethods]
impl Rsa {
    #[staticmethod]
    fn generate_keypair(
        py: Python,
        pk_size: usize,
    ) -> PyResult<(Py<PyBytes>, Py<PyBytes>, Py<PyBytes>)> {
        let mut rng = OsRng;

        let private_key = RsaPrivateKey::new(&mut rng, pk_size).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Key generation failed: {e}"))
        })?;

        let signing_key = SigningKey::<Sha256>::new(private_key.clone());
        let verifying_key = signing_key.verifying_key();

        let priv_pem = private_key.to_pkcs1_pem(Default::default()).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!(
                "Private key serialization failed: {e}"
            ))
        })?;

        let signing_pem = private_key.to_pkcs1_pem(Default::default()).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!(
                "Signing key serialization failed: {e}"
            ))
        })?;

        let pub_key: &RsaPublicKey = verifying_key.as_ref();
        let verifying_pem = pub_key.to_pkcs1_pem(Default::default()).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!(
                "Verifying key serialization failed: {e}"
            ))
        })?;

        Ok((
            PyBytes::new(py, priv_pem.as_bytes()).into(),
            PyBytes::new(py, signing_pem.as_bytes()).into(),
            PyBytes::new(py, verifying_pem.as_bytes()).into(),
        ))
    }

    #[staticmethod]
    fn sign(
        py: Python,
        data: &Bound<'_, PyBytes>,
        signing_key_pem: &Bound<'_, PyBytes>,
    ) -> PyResult<Py<PyBytes>> {
        let data = data.as_bytes();
        let pem_str = std::str::from_utf8(signing_key_pem.as_bytes()).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("PEM decode error: {e}"))
        })?;

        let private_key = RsaPrivateKey::from_pkcs1_pem(pem_str).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Invalid private key: {e}"))
        })?;

        let signing_key = SigningKey::<Sha256>::new(private_key);
        let mut rng = OsRng;
        let signature = signing_key.sign_with_rng(&mut rng, data);

        Ok(PyBytes::new(py, &signature.to_bytes()).into())
    }

    #[staticmethod]
    fn verify(
        _py: Python,
        data: &Bound<'_, PyBytes>,
        signature: &Bound<'_, PyBytes>,
        verifying_key_pem: &Bound<'_, PyBytes>,
    ) -> PyResult<bool> {
        let data = data.as_bytes();
        let signature_bytes = signature.as_bytes();
        let pem_str = std::str::from_utf8(verifying_key_pem.as_bytes()).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("PEM decode error: {e}"))
        })?;

        let public_key = RsaPublicKey::from_pkcs1_pem(pem_str).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Invalid public key: {e}"))
        })?;

        let verifying_key = VerifyingKey::<Sha256>::new(public_key);

        let sig = rsa::pkcs1v15::Signature::try_from(signature_bytes).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Invalid signature format: {e}"))
        })?;

        Ok(verifying_key.verify(data, &sig).is_ok())
    }
}

#[pymethods]
impl Ed25519 {
    #[staticmethod]
    fn generate_keypair(py: Python) -> PyResult<(Py<PyBytes>, Py<PyBytes>)> {
        let mut csprng = OsRng;

        // Сгенерировать 32 байта для секретного ключа
        let mut secret_bytes = [0u8; 32];
        use rand::RngCore;
        csprng.fill_bytes(&mut secret_bytes);

        // Используем TryFrom для создания SecretKey
        let secret = ed25519_dalek::SecretKey::try_from(&secret_bytes[..]).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Secret key error: {e}"))
        })?;

        // Создаём SigningKey
        let signing_key = Ed25519SigningKey::from(&secret);
        let verifying_key = signing_key.verifying_key();

        // Собираем 64 байта: 32 секрета + 32 паблика
        let mut signing_key_bytes = [0u8; 64];
        signing_key_bytes[..32].copy_from_slice(&secret_bytes);
        signing_key_bytes[32..].copy_from_slice(verifying_key.as_bytes());

        Ok((
            PyBytes::new(py, &signing_key_bytes).into(),
            PyBytes::new(py, verifying_key.as_bytes()).into(),
        ))
    }

    #[staticmethod]
    fn sign(
        py: Python,
        message: &Bound<'_, PyBytes>,
        signing_key_bytes: &Bound<'_, PyBytes>,
    ) -> PyResult<Py<PyBytes>> {
        let signing_key_bytes = signing_key_bytes.as_bytes();
        if signing_key_bytes.len() != 64 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Signing key must be 64 bytes",
            ));
        }

        let signing_key =
            Ed25519SigningKey::from_bytes(&signing_key_bytes[..32].try_into().unwrap());
        let signature = signing_key.sign(message.as_bytes());

        Ok(PyBytes::new(py, &signature.to_bytes()).into())
    }

    #[staticmethod]
    fn verify(
        _py: Python,
        message: &Bound<'_, PyBytes>,
        signature_bytes: &Bound<'_, PyBytes>,
        verifying_key_bytes: &Bound<'_, PyBytes>,
    ) -> PyResult<bool> {
        let verifying_key_bytes = verifying_key_bytes.as_bytes();
        if verifying_key_bytes.len() != 32 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Verifying key must be 32 bytes",
            ));
        }

        let signature_bytes = signature_bytes.as_bytes();
        if signature_bytes.len() != 64 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Signature must be 64 bytes",
            ));
        }

        let verifying_key =
            Ed25519VerifyingKey::from_bytes(verifying_key_bytes.try_into().unwrap()).map_err(
                |e| pyo3::exceptions::PyValueError::new_err(format!("Invalid verifying key: {e}")),
            )?;
        let signature = Signature::from_bytes(signature_bytes.try_into().unwrap());

        Ok(verifying_key.verify(message.as_bytes(), &signature).is_ok())
    }
}

#[pymethods]
impl Falcon512 {
    #[staticmethod]
    fn generate_keypair(py: Python) -> PyResult<(Py<PyBytes>, Py<PyBytes>)> {
        let (secret_key, public_key) = falcon512::keypair();

        Ok((
            PyBytes::new(py, public_key.as_bytes()).into(),
            PyBytes::new(py, secret_key.as_bytes()).into(),
        ))
    }

    #[staticmethod]
    fn sign(
        py: Python,
        message: &Bound<'_, PyBytes>,
        signing_key_bytes: &Bound<'_, PyBytes>,
    ) -> PyResult<Py<PyBytes>> {
        let secret_key = SecretKey::from_bytes(signing_key_bytes.as_bytes()).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Invalid secret key: {e}"))
        })?;

        let signature = falcon512::detached_sign(message.as_bytes(), &secret_key);
        Ok(PyBytes::new(py, signature.as_bytes()).into())
    }

    #[staticmethod]
    fn verify(
        _py: Python,
        message: &Bound<'_, PyBytes>,
        signature_bytes: &Bound<'_, PyBytes>,
        public_key_bytes: &Bound<'_, PyBytes>,
    ) -> PyResult<bool> {
        let public_key = PublicKey::from_bytes(public_key_bytes.as_bytes()).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Invalid public key: {e}"))
        })?;

        let signature = DetachedSignature::from_bytes(signature_bytes.as_bytes()).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Invalid signature: {e}"))
        })?;

        Ok(
            falcon512::verify_detached_signature(&signature, message.as_bytes(), &public_key)
                .is_ok(),
        )
    }
}

#[pymethods]
impl Falcon1024 {
    #[staticmethod]
    fn generate_keypair(py: Python) -> PyResult<(Py<PyBytes>, Py<PyBytes>)> {
        let (secret_key, public_key) = falcon1024::keypair();

        Ok((
            PyBytes::new(py, public_key.as_bytes()).into(),
            PyBytes::new(py, secret_key.as_bytes()).into(),
        ))
    }

    #[staticmethod]
    fn sign(
        py: Python,
        message: &Bound<'_, PyBytes>,
        signing_key_bytes: &Bound<'_, PyBytes>,
    ) -> PyResult<Py<PyBytes>> {
        let secret_key = SecretKey::from_bytes(signing_key_bytes.as_bytes()).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Invalid secret key: {e}"))
        })?;

        let signature = falcon1024::detached_sign(message.as_bytes(), &secret_key);
        Ok(PyBytes::new(py, signature.as_bytes()).into())
    }

    #[staticmethod]
    fn verify(
        _py: Python,
        message: &Bound<'_, PyBytes>,
        signature_bytes: &Bound<'_, PyBytes>,
        public_key_bytes: &Bound<'_, PyBytes>,
    ) -> PyResult<bool> {
        let public_key = PublicKey::from_bytes(public_key_bytes.as_bytes()).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Invalid public key: {e}"))
        })?;

        let signature = DetachedSignature::from_bytes(signature_bytes.as_bytes()).map_err(|e| {
            pyo3::exceptions::PyValueError::new_err(format!("Invalid signature: {e}"))
        })?;

        Ok(
            falcon1024::verify_detached_signature(&signature, message.as_bytes(), &public_key)
                .is_ok(),
        )
    }
}

#[pymodule]
fn stpc(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    #[cfg(feature = "rsa_dep")]
    m.add_class::<Rsa>()?;

    m.add_class::<Ed25519>()?;
    m.add_class::<Falcon512>()?;
    m.add_class::<Falcon1024>()?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}
