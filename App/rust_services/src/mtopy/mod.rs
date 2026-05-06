use argon2::password_hash;

use super::mblockchain;
use super::mcrypto;

pub fn register() {
    println!("Registering user...");
    let secret = "test_secret";
    // 1. Derivar la llave (esto no es un PasswordHash, es una clave cruda)
    let master_key = mcrypto::derive_key(secret, "poteto_teto");

    let wallet = mblockchain::wallet_gen::gen_wallet().1.into_bytes();
    let encrypted_wallet = mcrypto::encrypt_data(&wallet, secret);


    println!("Encrypted wallet: {:?}", encrypted_wallet);
}