use sp_core::{sr25519, Pair};

pub fn gen_wallet() -> (sr25519::Pair, String, [u8; 32]) {
    sr25519::Pair::generate_with_phrase(None)
}