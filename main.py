import psycopg2

def create_clients_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL);
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS phones (
                id SERIAL PRIMARY KEY,
                client_id INTEGER NOT NULL,
                phone VARCHAR(255) NOT NULL,
                FOREIGN KEY (client_id) REFERENCES clients (id));
        """)

def add_client(conn, first_name, last_name, email):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO clients (first_name, last_name, email)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (first_name, last_name, email))
        client_id = cur.fetchone()[0]
        return client_id

def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO phones (client_id, phone)
            VALUES (%s, %s);
        """, (client_id, phone))

def change_client(conn, client_id, first_name, last_name, email):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE clients
            SET first_name = COALESCE(%s, first_name),
                last_name = COALESCE(%s, last_name),
                email = COALESCE(%s, email)
            WHERE id = %s;
        """, (first_name, last_name, email, client_id))

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM phones
            WHERE client_id = %s AND phone = %s;
        """, (client_id, phone))

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM phones
            WHERE client_id = %s;
        """, (client_id,))
        cur.execute("""
            DELETE FROM clients
            WHERE id = %s;
        """, (client_id,))

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        query = """
            SELECT c.id, c.first_name, c.last_name, c.email, p.phone
            FROM clients c
            LEFT JOIN phones p ON c.id = p.client_id
            WHERE (%s IS NULL OR c.first_name = %s) 
                AND (%s IS NULL OR c.last_name = %s) 
                AND (%s IS NULL OR c.email = %s) 
                AND (%s IS NULL OR p.phone = %s);
        """
        cur.execute(query,
                    (first_name, first_name,
                     last_name, last_name,
                     email, email,
                     phone, phone))
        return cur.fetchall()

def get_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT clients.first_name, clients.last_name, clients.email, phones.phone
            FROM clients
            JOIN phones ON clients.id = phones.client_id
            WHERE clients.id = %s;
        """, (client_id,))
        client = cur.fetchone()
        return client

if __name__ == "__main__":
    with psycopg2.connect(
        database="ENTER DB NAME",
        user="ENTER USER NAME FOR DB",
        password="ENTER PASSWORD FOR DB",
    ) as conn:
        create_clients_db(conn)
        client_1 = add_client(conn, "John", "Doe", "client1@example.com")
        client_2 = add_client(conn, "Jane", "Pierce", "client2@example.com")
        add_phone(conn, client_1, "1234567890")
        add_phone(conn, client_1, "9876543210")
        add_phone(conn, client_2, "1234567891")
        print(get_client(conn, client_1))
        print(get_client(conn, client_2))
        change_client(conn, client_1, "Jane", "Doe", "client2@example.ru")
        print(get_client(conn, client_2))
        print(find_client(conn, phone="1234567891"))
        delete_phone(conn, client_1, "1234567890")
        delete_client(conn, client_2)