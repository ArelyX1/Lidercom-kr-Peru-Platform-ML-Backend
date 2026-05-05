use aes_gcm::{
    aead::{Aead, KeyInit, OsRng},
    Aes256Gcm, Nonce
};

pub fn encrypt_data(key: &[u8; 32], plaintext: &[u8]) -> Vec<u8> {
    let cipher = Aes256Gcm::new_from_slice(key).expect("Failed to create cipher");
    let nonce = Nonce::from_slice(&rand::random::<[u8; 12]>());
    let ciphertext = cipher.encrypt(nonce, plaintext).expect("Encryption failed");
    
    [nonce.as_slice(), &ciphertext].concat()
}
