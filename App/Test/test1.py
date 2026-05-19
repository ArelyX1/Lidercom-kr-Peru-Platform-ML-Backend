import rust_services as rs

# Wrap it in quotes as a standard string
pwd_str = "6de75b9e00c41511b755b5d7bb79cab299c5789a7ab038a92e91f86b8ee3c2fb5d4c62e75a632d"
salt_str = "9f73383c6240e5dcd1c29c194c901618"


pwd = bytes.fromhex(pwd_str)
salt = bytes.fromhex(salt_str)


isOk = rs.ok_password(pwd, salt_str, "Elmomer0123")

print(f"misma psswrd {isOk}")
