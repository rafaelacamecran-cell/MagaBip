import psycopg2

conn_str = "postgresql://postgres:R%40f%4008049226*%23@localhost:5432/magabip_db"

try:
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    cur.execute("SELECT username, role FROM users;")
    users = cur.fetchall()
    print("Usuários e Papéis:")
    for user in users:
        print(f"- {user[0]}: {user[1]}")
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Erro: {e}")
