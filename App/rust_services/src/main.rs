use argon2::password_hash;

mod mtopy;
mod mblockchain;
mod mcrypto;


fn main() {
    let password = "Elmomero123";
    let wallet = mtopy::register(password);
    println!("Wallet info: {:?}", wallet);
    println!("Wallet info 0 : {:?}", wallet.0);
    println!("Wallet info 1 seed : {:?}", wallet.1);
    println!("Wallet info 2 : {:?}", wallet.2);
    println!("Wallet info 3 : {:?}", wallet.3);
    let master_key = mcrypto::derive_key(password, &wallet.3);

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
