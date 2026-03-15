ALLOWED_DOMAINS = ['magazineluiza.com.br'] 

def is_corporate_email(email):
    """Verifica se o e-mail pertence aos domínios da empresa"""
    if '@' in email:
        domain = email.split('@')[-1]
        return domain in ALLOWED_DOMAINS
    return False