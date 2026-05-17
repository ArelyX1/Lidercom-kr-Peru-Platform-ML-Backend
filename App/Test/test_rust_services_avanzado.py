import rust_services as rs
import secrets
import string
import time

SEP = "─" * 62

# ─── 1. Registro y login simulando flujo real ─────────────

def test_flujo_completo():
    """simula registro + inicio de sesión de un usuario"""
    email = "user@example.com"
    password = "MiClaveSegura_2024!"
    print(f"\n  📧 {email}")
    print(f"  🔑 {password}")

    enc_pwd, enc_phrase, salt, public_key = rs.register(password)
    print(f"  🧂 salt          : {salt}")
    print(f"  🔐 encrypted_pwd  : {enc_pwd.hex()[:48]}... ({len(enc_pwd)} bytes)")
    print(f"  📝 encrypted_phrase: {enc_phrase.hex()[:48]}... ({len(enc_phrase)} bytes)")
    print(f"  🔑 public_key     : {public_key[:48]}... ({len(public_key)} chars)")

    assert rs.ok_password(enc_pwd, salt, password), "login debería funcionar"

    for wrong in [password[:-1], password.upper(), "", password * 2]:
        assert not rs.ok_password(enc_pwd, salt, wrong), f"'{wrong}' no debería validar"

    print("  ✅ registro + login exitosos")

# ─── 2. Contraseñas aleatorias (round-trip) ───────────────

def test_random_passwords():
    """genera N passwords aleatorios y verifica round-trip"""
    N = 15
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    for _ in range(N):
        length = secrets.randbelow(64) + 1
        pwd = "".join(secrets.choice(chars) for _ in range(length))
        enc, _, salt, _ = rs.register(pwd)
        assert rs.ok_password(enc, salt, pwd), f"round-trip falló para len={length}"
    print(f"\n  ✅ {N} passwords aleatorios verificados (1-64 chars)")

# ─── 3. Contraseñas con bytes nulos y bordes ──────────────

def test_password_with_null():
    """password con caracter nulo \\x00 en distintas posiciones"""
    pwd = "abc\x00def"
    enc, _, salt, _ = rs.register(pwd)
    print(f"\n  password (repr)  : {pwd!r}")
    assert rs.ok_password(enc, salt, pwd), "null byte debe funcionar"
    assert not rs.ok_password(enc, salt, "abcdef"), "sin null no debe validar"
    print("  ✅ null byte manejado correctamente")

def test_password_only_numbers():
    pwd = "1234567890"
    enc, _, salt, _ = rs.register(pwd)
    assert rs.ok_password(enc, salt, pwd)
    assert not rs.ok_password(enc, salt, "123456789")
    print("  ✅ password numérico OK")

def test_password_only_spaces():
    for pwd in [" ", "   ", "\t", "\n"]:
        enc, _, salt, _ = rs.register(pwd)
        assert rs.ok_password(enc, salt, pwd), f"password={pwd!r} falló"
    print("  ✅ passwords de solo whitespace OK")

# ─── 4. Verificación de propiedades criptográficas ────────

def test_avalanche_effect():
    """un bit de diferencia en el password → ciphertext completamente distinto"""
    a, _, _, _ = rs.register("AAAAAA")
    b, _, _, _ = rs.register("AAAAAB")  # un carácter de diferencia
    # contar bytes iguales al inicio
    iguales = sum(1 for x, y in zip(a, b) if x == y)
    print(f"\n  ciphertext len       : {len(a)} bytes")
    print(f"  bytes idénticos      : {iguales} (de {min(len(a), len(b))})")
    # el nonce (12 bytes) puede coincidir raramente, pero el ciphertext no
    assert iguales <= 14, f"demasiados bytes en común: {iguales}"
    print("  ✅ avalanche effect OK")

def test_avalanche_effect_salt():
    """un bit de diferencia en el password → salt completamente distinto"""
    _, _, s1, _ = rs.register("AAAAAA")
    _, _, s2, _ = rs.register("AAAAAB")
    print(f"\n  salt AAAAAA : {s1}")
    print(f"  salt AAAAAB : {s2}")
    assert s1 != s2
    iguales = sum(1 for x, y in zip(s1, s2) if x == y)
    print(f"  chars iguales: {iguales}/32 (ideal ~2-3 por azar)")
    print("  ✅ salts independientes")

def test_nonce_aleatorio():
    """cada ciphertext empieza con nonce distinto (probabilidad ~0)"""
    nonces = set()
    for _ in range(50):
        enc, _, _, _ = rs.register("fixed_password")
        nonce = enc[:12]  # primeros 12 bytes = nonce AES-GCM
        nonces.add(nonce)
    print(f"\n  nonces únicos en 50 llamadas: {len(nonces)}/50")
    assert len(nonces) > 48, "deberían ser prácticamente todos distintos"
    print("  ✅ nonce aleatorio OK")

# ─── 5. Consistencia ──────────────────────────────────────

def test_deterministic_verify():
    """ok_password es determinístico para mismos inputs"""
    enc, _, salt, _ = rs.register("deterministic_test")
    resultados = [rs.ok_password(enc, salt, "deterministic_test") for _ in range(10)]
    assert all(resultados), "ok_password debe ser determinístico"
    print(f"\n  ✅ 10 llamadas a ok_password = todas True")

def test_false_deterministic():
    """ok_password False también es determinístico"""
    enc, _, salt, _ = rs.register("det_test")
    resultados = [rs.ok_password(enc, salt, "wrong") for _ in range(10)]
    assert not any(resultados), "ok_password False debe ser determinístico"
    print(f"  ✅ 10 llamadas a ok_password(wrong) = todas False")

# ─── 6. Baseline: estructura invariante ───────────────────

def test_salt_siempre_32_hex_chars():
    for _ in range(100):
        _, _, salt, _ = rs.register("a")
        assert len(salt) == 32
        int(salt, 16)  # debe ser hex válido
    print("  ✅ 100 salts: 32 hex chars")

def test_encrypted_password_structure():
    """ciphertext = nonce(12) + ciphertext + tag(16) → len = 28 + plain_len"""
    for length in [0, 1, 5, 10, 50, 100, 200]:
        pwd = "x" * length
        enc, _, _, _ = rs.register(pwd)
        expected = 28 + length
        assert len(enc) == expected, f"len={len(enc)} esperado={expected} (pwd_len={length})"
    print("  ✅ estructura ciphertext: len = 28 + plain_len")

# ─── 7. Rendimiento (solo benchmark, sin assert estricto) ──

def test_perf_register():
    N = 20
    inicio = time.perf_counter()
    for _ in range(N):
        rs.register("perf_test_password_" + secrets.token_hex(4))
    total = time.perf_counter() - inicio
    promedio = (total / N) * 1000
    print(f"\n  {N} registros en {total:.2f}s ({promedio:.1f} ms c/u)")
    # Argon2 está configurado con params default, ~10-50 ms por llamada
    assert promedio < 500, f"muy lento: {promedio:.1f} ms"
    print("  ✅ rendimiento aceptable")

def test_perf_ok_password():
    enc, _, salt, _ = rs.register("perf_check")
    N = 50
    inicio = time.perf_counter()
    for _ in range(N):
        rs.ok_password(enc, salt, "perf_check")
        rs.ok_password(enc, salt, "wrong")
    total = time.perf_counter() - inicio
    promedio = (total / (N * 2)) * 1000
    print(f"  {N*2} verificaciones en {total:.2f}s ({promedio:.1f} ms c/u)")
    assert promedio < 200, f"muy lento: {promedio:.1f} ms"
    print("  ✅ rendimiento ok_password aceptable")

# ─── 8. Resistencia a dict attack simulado ────────────────

def test_no_false_positives():
    """con passwords similares, nunca falso positivo"""
    base = "base_password_42"
    enc, _, salt, _ = rs.register(base)
    # variaciones típicas de "adivinanza"
    guesses = [
        base.capitalize(),
        base.replace("42", "43"),
        base + "!",
        "Base_password_42",
        "base password 42",
        base[::-1],
        base[:-1],
        base + base[:5],
    ]
    for g in guesses:
        assert not rs.ok_password(enc, salt, g), f"falso positivo: {g!r}"
    print(f"  ✅ 0 falsos positivos en {len(guesses)} adivinanzas")
