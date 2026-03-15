import psycopg2

conn_str = "postgresql://postgres:R%40f%4008049226*%23@localhost:5432/magabip_db"

try:
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    cur.execute("SELECT id, zendesk_link FROM support_tickets WHERE zendesk_link IS NOT NULL;")
    tickets = cur.fetchall()
    print("Tickets e links:")
    for t in tickets:
        print(f"ID {t[0]}: '{t[1]}'")
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Erro: {e}")
