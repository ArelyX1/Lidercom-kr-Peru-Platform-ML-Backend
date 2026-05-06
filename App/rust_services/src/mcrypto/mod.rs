use argon2::{
    password_hash::{SaltString},
    Argon2, PasswordHasher
};
use aes_gcm::{Aes256Gcm, aead::{KeyInit, Aead}, Nonce};
use rand::RngExt;


pub fn derive_key(master_password: &str, salt: &str) -> [u8; 32] {
    let mut config = Argon2::default();
    let mut key = [0u8; 32];
    
    let salt_bytes = salt.as_bytes();

    config.hash_password_into(master_password.as_bytes(), salt_bytes, &mut key)
        .expect("Error derivando clave");
    
    key
}

pub fn encrypt_data(plaintext: &[u8], master_pass: &str) -> Vec<u8> {
    let key = derive_key(master_pass, "perripopo");
    let cipher = Aes256Gcm::new(&key.into());

    let mut nonce_bytes = [0u8; 12];
    rand::rng().fill(&mut nonce_bytes);
    let nonce = Nonce::from_slice(&nonce_bytes);
    
    let ciphertext = cipher.encrypt(nonce, plaintext).expect("Cifrado fallido");

    [nonce_bytes.as_slice(), &ciphertext].concat()
}

pub fn decrypt_data(ciphertext: &[u8], master_pass: &str) -> Vec<u8> {
    let key = derive_key(master_pass, "perripopo");
    let cipher = Aes256Gcm::new(&key.into());

    let (nonce_bytes, ciphertext) = ciphertext.split_at(12);
    let nonce = Nonce::from_slice(nonce_bytes);

    cipher.decrypt(nonce, ciphertext).expect("Descifrado fallido")
}