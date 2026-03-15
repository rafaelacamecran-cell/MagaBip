import psycopg2

conn_str = "postgresql://postgres:R%40f%4008049226*%23@localhost:5432/magabip_db"

try:
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    cur.execute("SELECT id, username, role FROM users WHERE role IS NULL;")
    users = cur.fetchall()
    print("Usuários com role NULL:")
    for u in users:
        print(f"ID {u[0]} ({u[1]})")
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Erro: {e}")
