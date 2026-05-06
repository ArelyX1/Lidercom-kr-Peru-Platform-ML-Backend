use crate::mcrypto;

pub fn wallet_conformance(plain_content: &[u8], encrypted_wallet: &[u8], master_pass: &[u8; 32]) -> bool {
    if let Ok(decrypted_target) = mcrypto::decrypt_data(encrypted_wallet, master_pass) {
        return plain_content == decrypted_target;
    }
    false
}