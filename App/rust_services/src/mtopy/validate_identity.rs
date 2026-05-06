use crate::mcrypto;

pub fn wallet_conformance(wallet_content: &[u8], encrypted_wallet: &[u8], master_pass: &str) -> bool {
    let decrypted_wallet = mcrypto::decrypt_data(encrypted_wallet, master_pass);
    decrypted_wallet == wallet_content
}