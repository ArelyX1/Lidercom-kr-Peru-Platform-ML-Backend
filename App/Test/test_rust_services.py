import rust_services as rs

# ─── helpers ────────────────────────────────────────────────

def enc_pwd_len(plain_len: int) -> int:
    """encrypted_password = 12 (nonce) + plain_len + 16 (GCM tag)"""
    return 12 + plain_len + 16

# ─── 1. register: tipo y estructura básica ─────────────────

def test_register_returns_tuple():
    enc_pwd, enc_phrase, salt, public_key = rs.register("test_password")
    print(f"\n  encrypted_password (hex) : {enc_pwd.hex()}")
    print(f"  encrypted_password (len) : {len(enc_pwd)} bytes")
    print(f"  encrypted_phrase  (hex) : {enc_phrase.hex()}")
    print(f"  encrypted_phrase  (len) : {len(enc_phrase)} bytes")
    print(f"  salt                     : {salt}")
    print(f"  public_key               : {public_key}")
    print(f"  public_key          (len): {len(public_key)} chars")
    assert isinstance(enc_pwd, bytes)
    assert isinstance(enc_phrase, bytes)
    assert isinstance(salt, str)
    assert isinstance(public_key, str)
    assert len(salt) == 32
    assert len(enc_pwd) > 0
    assert len(enc_phrase) > 0
    assert len(public_key) == 48

# ─── 2. register: determinismo ────────────────────────────

def test_register_different_salts():
    _, _, salt1, _ = rs.register("same_password")
    _, _, salt2, _ = rs.register("same_password")
    print(f"\n  salt1 : {salt1}")
    print(f"  salt2 : {salt2}")
    assert salt1 != salt2

def test_register_different_ciphertexts():
    a, _, _, _ = rs.register("same")
    b, _, _, _ = rs.register("same")
    print(f"\n  ciphertext1 (hex) : {a.hex()}")
    print(f"  ciphertext2 (hex) : {b.hex()}")
    assert a != b, "mismo password debe producir ciphertext distinto (nonce aleatorio)"

def test_register_different_phrases():
    """cada registro genera un nuevo wallet → encrypted_phrase distinto"""
    _, a, _, _ = rs.register("x")
    _, b, _, _ = rs.register("x")
    print(f"\n  phrase1 (hex) : {a.hex()}")
    print(f"  phrase2 (hex) : {b.hex()}")
    assert a != b

# ─── 3. ok_password: verificación ──────────────────────────

def test_ok_password_correct():
    enc_pwd, _, salt, _ = rs.register("mi_clave_secreta")
    result = rs.ok_password(enc_pwd, salt, "mi_clave_secreta")
    print(f"\n  encrypted_password (hex) : {enc_pwd.hex()[:50]}...")
    print(f"  salt                     : {salt}")
    print(f"  ok_password(correcta)    = {result}")
    assert result is True

def test_ok_password_incorrect():
    enc_pwd, _, salt, _ = rs.register("mi_clave_secreta")
    result = rs.ok_password(enc_pwd, salt, "otra_clave")
    print(f"\n  encrypted_password (hex) : {enc_pwd.hex()[:50]}...")
    print(f"  salt                     : {salt}")
    print(f"  ok_password(incorrecta)  = {result}")
    assert result is False

def test_ok_password_wrong_salt():
    """salt incorrecto → derive_key produce clave distinta → decrypt falla"""
    enc_pwd, _, salt, _ = rs.register("password")
    fake_salt = "f" * 32
    result = rs.ok_password(enc_pwd, fake_salt, "password")
    print(f"\n  salt real     : {salt}")
    print(f"  salt falso    : {fake_salt}")
    print(f"  ok_password   = {result}")
    assert result is False

def test_ok_password_tampered_ciphertext():
    """ciphertext corrupto → AES-GCM detecta → decrypt falla"""
    enc_pwd, _, salt, _ = rs.register("password")
    tampered = bytearray(enc_pwd)
    tampered[5] ^= 0xff  # flip bit en nonce
    result = rs.ok_password(bytes(tampered), salt, "password")
    print(f"\n  ciphertext original (hex) : {enc_pwd.hex()}")
    print(f"  ciphertext tampered (hex) : {bytes(tampered).hex()}")
    print(f"  ok_password               = {result}")
    assert result is False

# ─── 4. edge cases: longitud de password ──────────────────

def test_register_password_empty():
    enc_pwd, enc_phrase, salt, _ = rs.register("")
    print(f"\n  encrypted_password (hex) : {enc_pwd.hex()}")
    print(f"  encrypted_password (len) : {len(enc_pwd)} bytes (esperado: {enc_pwd_len(0)})")
    print(f"  encrypted_phrase  (len) : {len(enc_phrase)} bytes")
    assert len(enc_pwd) == enc_pwd_len(0)
    assert rs.ok_password(enc_pwd, salt, "") is True
    assert rs.ok_password(enc_pwd, salt, "x") is False

def test_register_password_single_char():
    enc_pwd, _, salt, _ = rs.register("a")
    print(f"\n  encrypted_password (len) : {len(enc_pwd)} bytes (esperado: {enc_pwd_len(1)})")
    print(f"  salt                     : {salt}")
    assert len(enc_pwd) == enc_pwd_len(1)
    assert rs.ok_password(enc_pwd, salt, "a") is True
    assert rs.ok_password(enc_pwd, salt, "b") is False

def test_register_password_short():
    enc_pwd, _, salt, _ = rs.register("ab")
    print(f"\n  encrypted_password (len) : {len(enc_pwd)} bytes (esperado: {enc_pwd_len(2)})")
    assert len(enc_pwd) == enc_pwd_len(2)
    assert rs.ok_password(enc_pwd, salt, "ab") is True

def test_register_password_medium():
    pwd = "password123!@#"
    enc_pwd, _, salt, _ = rs.register(pwd)
    print(f"\n  password len : {len(pwd)} chars")
    print(f"  enc_pwd len  : {len(enc_pwd)} bytes (esperado: {enc_pwd_len(len(pwd))})")
    assert len(enc_pwd) == enc_pwd_len(len(pwd))
    assert rs.ok_password(enc_pwd, salt, pwd) is True

def test_register_password_long():
    long_pwd = "a" * 1000
    enc_pwd, enc_phrase, salt, _ = rs.register(long_pwd)
    print(f"\n  password len        : {len(long_pwd)} chars")
    print(f"  encrypted_pwd len   : {len(enc_pwd)} bytes (esperado: {enc_pwd_len(1000)})")
    print(f"  encrypted_phrase len: {len(enc_phrase)} bytes")
    assert len(enc_pwd) == enc_pwd_len(1000)
    assert rs.ok_password(enc_pwd, salt, long_pwd) is True
    assert rs.ok_password(enc_pwd, salt, long_pwd + "x") is False

# ─── 5. caracteres especiales y unicode ───────────────────

def test_register_special_chars():
    special = "¡Hola! ¿Cómo están? ñoño 你好 🔐"
    enc_pwd, _, salt, _ = rs.register(special)
    print(f"\n  password          : {special}")
    print(f"  password bytes    : {special.encode('utf-8')}")
    print(f"  password len      : {len(special)} chars / {len(special.encode('utf-8'))} bytes")
    print(f"  encrypted_pwd len : {len(enc_pwd)} bytes")
    assert rs.ok_password(enc_pwd, salt, special) is True

def test_register_unicode_emojis():
    pwd = "😀😎🤖👻🦄"
    enc_pwd, _, salt, _ = rs.register(pwd)
    print(f"\n  password          : {pwd}")
    print(f"  encrypted_pwd len : {len(enc_pwd)} bytes")
    assert rs.ok_password(enc_pwd, salt, pwd) is True


def test_register_unicode_accents():
    pwd = "àáâãäåèéêëìíîïòóôõöùúûüñçÀÁÂÃÄÅÈÉÊËÌÍÎÏÒÓÔÕÖÙÚÛÜÑÇ"
    enc_pwd, _, salt, _ = rs.register(pwd)
    print(f"\n  password          : {pwd}")
    print(f"  encrypted_pwd len : {len(enc_pwd)} bytes")
    assert rs.ok_password(enc_pwd, salt, pwd) is True


def test_register_unicode_rtl():
    pwd = "مرحبا بالعالم שלום עולם"
    enc_pwd, _, salt, _ = rs.register(pwd)
    print(f"\n  password          : {pwd}")
    assert rs.ok_password(enc_pwd, salt, pwd) is True

# ─── 6. ok_password con datos de otro registro ────────────

def test_cross_password():
    """enc_pwd de un registro no funciona con salt de otro"""
    a_pwd, _, a_salt, _ = rs.register("alpha")
    b_pwd, _, b_salt, _ = rs.register("beta")
    print(f"\n  alpha enc_pwd con beta salt → {rs.ok_password(a_pwd, b_salt, 'alpha')}")
    print(f"  beta  enc_pwd con alpha salt → {rs.ok_password(b_pwd, a_salt, 'beta')}")
    assert rs.ok_password(a_pwd, b_salt, "alpha") is False
    assert rs.ok_password(b_pwd, a_salt, "beta") is False

def test_cross_password_same_salt_impossible():
    """verificar que es virtualmente imposible tener mismo salt"""
    salts = {rs.register(f"pwd_{i}")[2] for i in range(20)}
    print(f"\n  salts únicos en 20 registros: {len(salts)}")
    assert len(salts) == 20

# ─── 7. forma del encrypted_phrase ─────────────────────────

def test_encrypted_phrase_length():
    """la frase mnemotécnica tiene largo consistente (12 palabras ~ 80-120 chars)"""
    for pwd in ["a", "short", "a_large_password_here!"*5]:
        _, enc_phrase, _, _ = rs.register(pwd)
        # nonce(12) + plaintext(mnemonic ~80-120) + tag(16) = ~108-148
        print(f"\n  password={pwd!r:30} → encrypted_phrase len={len(enc_phrase)} bytes")
        assert 90 <= len(enc_phrase) <= 160, \
            f"encrypted_phrase len {len(enc_phrase)} fuera de rango esperado (90-160)"

def test_encrypted_phrase_differs_each_time():
    """cada register genera un wallet distinto → encrypted_phrase distinto"""
    phrases = [rs.register("x")[1] for _ in range(5)]
    print(f"\n  encrypted_phrases (len): {[len(p) for p in phrases]}")
    assert len(set(phrases)) == 5

# ─── 8. ok_password con datos corruptos ────────────────────

def test_ok_password_short_ciphertext():
    """ciphertext < 12 bytes → AES-GCM nonce inválido"""
    result = rs.ok_password(b"\x01\x02\x03", "a" * 32, "x")
    print(f"\n  ok_password([1,2,3], ...) = {result}")
    assert result is False

def test_ok_password_empty_ciphertext():
    result = rs.ok_password(b"", "a" * 32, "x")
    print(f"\n  ok_password(b'', ...) = {result}")
    assert result is False

def test_ok_password_wrong_salt_length():
    """salt de largo distinto (pero válido para Argon2) → verificación falla"""
    enc_pwd, _, salt, _ = rs.register("test")
    print(f"\n  salt original (32 chars): {salt}")
    for bad_len in [31, 33, 40, 64]:
        bad_salt = "b" * bad_len
        r = rs.ok_password(enc_pwd, bad_salt, "test")
        print(f"  salt len={bad_len:3} → ok_password = {r}")
        assert r is False, f"con salt len={bad_len} debería fallar"

def test_ok_password_salt_too_short_panics():
    """salt muy corto causa pánico en Argon2 — solo 0 y 1 byte"""
    enc_pwd, _, _, _ = rs.register("test")
    for short_len in [0, 1]:
        bad_salt = "c" * short_len
        try:
            rs.ok_password(enc_pwd, bad_salt, "test")
            print(f"\n  salt len={short_len} → NO panic (inesperado)")
            assert False, f"salt len={short_len} debería haber lanzado panic"
        except BaseException as e:
            print(f"\n  salt len={short_len} → panic capturado: {type(e).__name__}")

# ─── 9. múltiples registros y verificación ─────────────────

def test_multiple_registrations():
    passwords = ["alpha", "beta", "gamma", "delta"]
    results = [rs.register(pwd) for pwd in passwords]
    salts = [r[2] for r in results]
    print()
    for i, pwd in enumerate(passwords):
        ok = rs.ok_password(results[i][0], results[i][2], pwd)
        print(f"  [{i}] password={pwd!r:8} → salt={results[i][2]}, "
              f"enc_pwd_len={len(results[i][0])}, ok_password={ok}")
    assert len(set(salts)) == len(passwords)
    for i, pwd in enumerate(passwords):
        assert rs.ok_password(results[i][0], results[i][2], pwd) is True

# ─── 10. sensibilidad a mayúsculas/minúsculas ──────────────

def test_case_sensitivity():
    enc_pwd, _, salt, _ = rs.register("Password")
    print(f"\n  ok_password('Password')     = {rs.ok_password(enc_pwd, salt, 'Password')}")
    print(f"  ok_password('password')     = {rs.ok_password(enc_pwd, salt, 'password')}")
    print(f"  ok_password('PASSWORD')     = {rs.ok_password(enc_pwd, salt, 'PASSWORD')}")
    assert rs.ok_password(enc_pwd, salt, "Password") is True
    assert rs.ok_password(enc_pwd, salt, "password") is False
    assert rs.ok_password(enc_pwd, salt, "PASSWORD") is False

# ─── 11. re-asociación: mismo password con distinto salt ──

def test_same_password_multiple_salts():
    """mismo password registrado 2 veces: cada ok_password funciona con su propio salt"""
    a, _, a_salt, _ = rs.register("shared")
    b, _, b_salt, _ = rs.register("shared")
    print(f"\n  ok_password(a, a_salt) = {rs.ok_password(a, a_salt, 'shared')}")
    print(f"  ok_password(b, b_salt) = {rs.ok_password(b, b_salt, 'shared')}")
    print(f"  ok_password(a, b_salt) = {rs.ok_password(a, b_salt, 'shared')}")
    assert rs.ok_password(a, a_salt, "shared") is True
    assert rs.ok_password(b, b_salt, "shared") is True
