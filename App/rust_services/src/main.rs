use argon2::password_hash;

mod mtopy;
mod mblockchain;
mod mcrypto;

use sp_core::Pair;


fn main() {
    let password = "Elmomero123";
    let wallet = mtopy::register(password);
    println!("Init: {:?}", wallet);
    println!("psswrd_hash: {:?}", wallet.0);
    println!("seed : {:?}", wallet.1);
    println!("pair : {:?}", wallet.2);
    println!("phrase : {:?}", wallet.3);
    println!("salt : {:?}", wallet.4);
    let master_key = mcrypto::derive_key(password, &wallet.4);
    let items = [&wallet.0, &wallet.1, &wallet.2, &wallet.3];
    print!("----------------------------------------------------------------------------\n");
    for (i, data) in items.iter().enumerate() {
    match mcrypto::decrypt_data(data, &master_key) {
        Ok(decrypted_bytes) => {
            // Intentamos convertir los bytes a texto
            match String::from_utf8(decrypted_bytes) {
                Ok(texto) => println!("Dato {}: {}", i, texto),
                Err(_) => println!("Dato {}: {:?}", i, data), // Si no es texto (como el seed), imprime los bytes
            }
        },
        Err(e) => eprintln!("Error desencriptando {}: {:?}", i, e),
    }
    }

    println!("Password : {:?}", mcrypto::decrypt_to_string(mcrypto::decrypt_data(&wallet.0, &master_key).expect("Failed to decrypt password hash")));

    let decrypt_phrase = mcrypto::decrypt_data(&wallet.3, &master_key).expect("Failed to decrypt");

    let recovered = mblockchain::wallet_gen::recover_wallet_from_phrase(&String::from_utf8_lossy(decrypt_phrase.as_ref()));
    let (pair, phrase, seed) = recovered;
    println!("Recovered pair: {:?}", pair.t o_raw_vec());
    println!("Recovered phrase: {:?}", phrase);
    println!("Recovered seed: {:?}", seed);

    
    //let phase = mblockchain::entity::user::get_phrase_from_wallet(wallet.1.2, password, &wallet.3);

    //println!("Phrase from wallet: {:?}", phase);

//    let password_admin = "Admin123";
//    let wallet_admin = mtopy::register(password_admin);

    // mtopy::assign_role(
//        &wallet.2.as_slice(), 
//        &master_key,
//        vec![0],
//        0,
//        &wallet_admin.2.as_slice()
//    );
    
}
