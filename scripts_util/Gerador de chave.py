import secrets

# --- CHAVE SECRETA PRINCIPAL DO FLASK ---
# (Pode ser usada como SECRET_KEY, WTF_CSRF_SECRET_KEY, ou SECURITY_PASSWORD_SALT)
# Gera uma string aleatória de 32 bytes (64 caracteres hexadecimais)
chave_principal = secrets.token_hex(32)

print("-" * 50)
print("CHAVE PARA WTF_CSRF_SECRET_KEY:")
print(f'WTF_CSRF_SECRET_KEY = "{chave_principal}"')
print("\n(Copie e cole essa chave no seu config.py)")

# --- CHAVE PARA SENHAS (SALT) ---
# É altamente recomendado usar uma chave DIFERENTE para o salt de senhas.
chave_salt = secrets.token_hex(24) # Um salt de 24 bytes (48 caracteres) é suficiente

print("-" * 50)
print("CHAVE PARA SECURITY_PASSWORD_SALT:")
print(f'SECURITY_PASSWORD_SALT = "{chave_salt}"')
print("\n(Copie e cole essa chave no seu config.py)")
print("-" * 50)
