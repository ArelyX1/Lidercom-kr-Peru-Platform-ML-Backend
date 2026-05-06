use argon2::{
    password_hash::{rand_core::OsRng, PasswordHash, PasswordHasher, PasswordVerifier, SaltString},
    Argon2,
};
pub mod validate_identity;

use super::mblockchain;
use super::mcrypto;

pub fn register() {
    println!("Registering user...");

    let psswrd = "Elmomero123";

    let usr_salt_obj = mcrypto::generate_random_salt(); 
    let usr_salt = usr_salt_obj.as_str(); // Ahora la referencia es válida mientras usr_salt_obj exista

    
    // 1. Derivar la llave (esto no es un PasswordHash, es una clave cruda)
    let master_key = mcrypto::derive_key(psswrd, usr_salt);
    //todo: mandarlo a la DB
    println!("Master key: {:?}", master_key);
    
    let psswrd_hash = mcrypto::encrypt_data(psswrd.as_bytes(), &master_key);
    println!("Password hash: {:?}", psswrd_hash);
    let decrypted_bytes = mcrypto::decrypt_data(&psswrd_hash, &master_key).unwrap();
    println!("original password: {}", String::from_utf8(decrypted_bytes).expect("Invalid UTF-8"));
    let is_valid = validate_identity::wallet_conformance(&psswrd.as_bytes(), &psswrd_hash, &master_key);
    println!("Is valid psswd: {}", is_valid);

    let wallet_info = mblockchain::wallet_gen::gen_wallet();
    let mnemonic_phrase = wallet_info.1; // Esto es el String
    let wallet_bytes = mnemonic_phrase.as_bytes();


    let wallet = mcrypto::encrypt_data(&wallet_bytes, &master_key);
    let encrypted_wallet = mcrypto::encrypt_data(&wallet_bytes, &master_key);

    let is_valid = validate_identity::wallet_conformance(&wallet_bytes, &encrypted_wallet, &master_key);
    println!("Encrypted wallet: {:?}", encrypted_wallet);
    println!("Decrypted wallet: {:?}", mcrypto::decrypt_data(&encrypted_wallet, &master_key).unwrap());
    println!("Original wallet: {:?}", mnemonic_phrase);
    println!("Is same: {}", is_valid);
}