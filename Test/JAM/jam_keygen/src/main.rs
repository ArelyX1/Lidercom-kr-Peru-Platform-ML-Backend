use sp_core::{sr25519, Pair, crypto::Ss58Codec};

fn main() {
    // Genera frase y llaves en un solo paso
    let (pair, phrase, _) = sr25519::Pair::generate_with_phrase(None);
    
    println!("---");
    println!("PHRASE: {}", phrase);
    println!("SS58 ADDR: {}", pair.public().to_ss58check());
    println!("---");
}
