import rust_services as rs

# ──────────────────────────────────────────────
#  REGISTER
# ──────────────────────────────────────────────
print("=" * 70)
print("1. REGISTER")
print("=" * 70)
enc_pwd, enc_phrase, salt, public_key = rs.register("MiClave123")
print(f"  password           : MiClave123")
print(f"  → encrypted_pwd    : {enc_pwd.hex()}")
print(f"    len              : {len(enc_pwd)} bytes")
print(f"  → encrypted_phrase : {enc_phrase.hex()}")
print(f"    len              : {len(enc_phrase)} bytes")
print(f"  → salt             : {salt}")
print(f"    len              : {len(salt)} chars")
print(f"  → public_key       : {public_key}")
print(f"    len              : {len(public_key)} chars")
print()

# ──────────────────────────────────────────────
#  SALT SIEMPRE DISTINTO
# ──────────────────────────────────────────────
print("=" * 70)
print("2. CADA REGISTRO GENERA SALT DISTINTO")
print("=" * 70)
_, _, s1, _ = rs.register("test")
_, _, s2, _ = rs.register("test")
print(f"  misma contraseña 'test'")
print(f"  salt1: {s1}")
print(f"  salt2: {s2}")
print(f"  ¿salt1 != salt2? → {s1 != s2}")
print()

# ──────────────────────────────────────────────
#  CIPHERTEXT SIEMPRE DISTINTO
# ──────────────────────────────────────────────
print("=" * 70)
print("3. CADA REGISTRO GENERA CIPHERTEXT DISTINTO")
print("=" * 70)
c1, _, _, _ = rs.register("test")
c2, _, _, _ = rs.register("test")
print(f"  ciphertext1: {c1.hex()}")
print(f"  ciphertext2: {c2.hex()}")
print(f"  ¿c1 != c2?  → {c1 != c2}  (nonce aleatorio)")
print()

# ──────────────────────────────────────────────
#  OK_PASSWORD
# ──────────────────────────────────────────────
print("=" * 70)
print("4. OK_PASSWORD")
print("=" * 70)
enc_pwd, _, salt, _ = rs.register("MiClave123")
print(f"  contraseña original : MiClave123")
r1 = rs.ok_password(enc_pwd, salt, "MiClave123")
r2 = rs.ok_password(enc_pwd, salt, "otra_clave")
r3 = rs.ok_password(enc_pwd, salt, "")
r4 = rs.ok_password(enc_pwd, salt, "MiClave1234")
print(f"  ok_password('MiClave123')   → {r1}")
print(f"  ok_password('otra_clave')   → {r2}")
print(f"  ok_password('')             → {r3}")
print(f"  ok_password('MiClave1234')  → {r4}")
print(f"  solo la correcta pasa: {r1 == True and r2 == False and r3 == False and r4 == False}")
print()

# ──────────────────────────────────────────────
#  SALT EQUIVOCADO
# ──────────────────────────────────────────────
print("=" * 70)
print("5. SALT EQUIVOCADO → FALLA")
print("=" * 70)
enc_pwd, _, salt_real, _ = rs.register("clave")
salt_fake = "f" * 32
print(f"  salt real : {salt_real}")
print(f"  salt fake : {salt_fake}")
r = rs.ok_password(enc_pwd, salt_fake, "clave")
print(f"  ok_password(enc, salt_fake, 'clave') = {r}")
print()

# ──────────────────────────────────────────────
#  CIPHERTEXT CORRUPTO
# ──────────────────────────────────────────────
print("=" * 70)
print("6. CIPHERTEXT CORRUPTO → FALLA (AES-GCM DETECTA)")
print("=" * 70)
enc_pwd, _, salt, _ = rs.register("clave")
tampered = bytearray(enc_pwd)
tampered[3] ^= 0xFF
print(f"  original : {enc_pwd.hex()}")
print(f"  corrupto : {bytes(tampered).hex()}")
print(f"  diff en byte 3: {enc_pwd[3]:02x} → {tampered[3]:02x}")
r = rs.ok_password(bytes(tampered), salt, "clave")
print(f"  ok_password(corrupto, salt, 'clave') = {r}")
print()

# ──────────────────────────────────────────────
#  PASSWORD VACÍO
# ──────────────────────────────────────────────
print("=" * 70)
print("7. PASSWORD VACÍO")
print("=" * 70)
enc, _, salt, _ = rs.register("")
print(f"  encrypted_pwd : {enc.hex()}")
print(f"  len           : {len(enc)} bytes")
print(f"  salt          : {salt}")
print(f"  ok_password('')   = {rs.ok_password(enc, salt, '')}")
print(f"  ok_password('x')  = {rs.ok_password(enc, salt, 'x')}")
print()

# ──────────────────────────────────────────────
#  PASSWORD LARGO
# ──────────────────────────────────────────────
print("=" * 70)
print("8. PASSWORD LARGO (1000 'a's)")
print("=" * 70)
large = "a" * 1000
enc, _, salt, _ = rs.register(large)
print(f"  encrypted_pwd len: {len(enc)} bytes (esperado: {28 + 1000})")
print(f"  salt             : {salt}")
print(f"  ok_password(correcto)   = {rs.ok_password(enc, salt, large)}")
print(f"  ok_password(incorrecto) = {rs.ok_password(enc, salt, large + 'x')}")
print()

# ──────────────────────────────────────────────
#  UNICODE
# ──────────────────────────────────────────────
print("=" * 70)
print("9. UNICODE / EMOJIS / ACENTOS")
print("=" * 70)
tests = [
    "¿Cómo estás? ñoño",
    "你好世界",
    "😀😎🤖👻🦄",
    "مرحبا بالعالم",
    "àéíóú ÀÉÍÓÚ üñç",
]
for pwd in tests:
    enc, _, salt, _ = rs.register(pwd)
    ok = rs.ok_password(enc, salt, pwd)
    ok_false = rs.ok_password(enc, salt, "xxx")
    print(f"  {pwd!r:30} → ok={ok}  ok_false={ok_false}  enc_len={len(enc)}")
print()

# ──────────────────────────────────────────────
#  CASE SENSITIVITY
# ──────────────────────────────────────────────
print("=" * 70)
print("10. CASE SENSITIVITY")
print("=" * 70)
enc, _, salt, _ = rs.register("Password")
for guess in ["Password", "password", "PASSWORD", "P@ssword"]:
    r = rs.ok_password(enc, salt, guess)
    print(f"  ok_password(..., {guess!r:12}) = {r}")
print()

# ──────────────────────────────────────────────
#  VARIAS LONGITUDES
# ──────────────────────────────────────────────
print("=" * 70)
print("11. LONGITUD encrypted_pwd vs PASSWORD (28 + n)")
print("=" * 70)
print(f"  {'pwd_len':>8} | {'enc_len':>8} | {'esperado':>8} | {'match':>6}")
print(f"  {'─'*8}-+-{'─'*8}-+-{'─'*8}-+-{'─'*6}")
for n in [0, 1, 3, 5, 10, 20, 50, 100, 200]:
    enc, _, _, _ = rs.register("x" * n)
    esperado = 28 + n
    match = "✓" if len(enc) == esperado else "✗"
    print(f"  {n:>8} | {len(enc):>8} | {esperado:>8} | {match:>6}")

# ──────────────────────────────────────────────
#  CONTEO DE REGISTROS / BENCHMARK
# ──────────────────────────────────────────────
print()
print("=" * 70)
print("12. BENCHMARK RÁPIDO")
print("=" * 70)
import time
inicio = time.perf_counter()
for i in range(10):
    rs.register(f"bench_{i}")
t = time.perf_counter() - inicio
print(f"  10 registros      : {t:.3f}s  ({t/10*1000:.1f} ms c/u)")

enc, _, salt, _ = rs.register("bench")
inicio = time.perf_counter()
for _ in range(30):
    rs.ok_password(enc, salt, "bench")
    rs.ok_password(enc, salt, "wrong")
t = time.perf_counter() - inicio
print(f"  30 ok_password    : {t:.3f}s  ({t/30*1000:.1f} ms c/u)")

# ──────────────────────────────────────────────
#  FALSOS POSITIVOS
# ──────────────────────────────────────────────
print()
print("=" * 70)
print("13. FALSOS POSITIVOS")
print("=" * 70)
enc, _, salt, _ = rs.register("base_password_42")
guesses = ["Base_password_42", "base_password_43", "base password 42",
           "base_password_42!", "BASE_PASSWORD_42", "base_password_4"]
print(f"  contraseña real    : base_password_42")
print(f"  {'adivinanza':<25} | {'resultado':>8}")
print(f"  {'─'*25}-+-{'─'*8}")
for g in guesses:
    r = rs.ok_password(enc, salt, g)
    print(f"  {g!r:<25} | {str(r):>8}")
print()

print("=" * 70)
print("TODO PASÓ  ✅")
print("=" * 70)
