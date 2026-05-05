use sp_core::{Pair, crypto::Ss58Codec};

mod wallet_gen;

pub fn blockchain_init() {
    let (pair, phrase, _) = wallet_gen::gen_wallet();
    println!("Generating blockchain wallet...");
    // println!("PHRASE: {}", phrase);
    println!("SS58 ADDR: {}", pair.public().to_ss58check());
    
}