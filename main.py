import psycopg2



def create_database_structure(conn):
    with conn.cursor() as cur:
        # Создаем таблицу клиентов (если ее нет)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            client_id SERIAL PRIMARY KEY,
            first_name VARCHAR(128) NOT NULL,
            last_name VARCHAR(128) NOT NULL,
            email VARCHAR(128) NOT NULL
        );
        """)

        # Создаем таблицу телефонов клиентов (если ее нет)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS phones (
            phone_id SERIAL PRIMARY KEY,
            client_id INT REFERENCES clients(client_id),
            phone_number VARCHAR(20)
        );
        """)
    conn.commit()


def add_client(conn, first_name, last_name, email):
    with conn.cursor() as cur:
        cur.execute ("INSERT INTO clients (first_name, last_name, email) VALUES (%s, %s, %s) RETURNING client_ID, first_name, last_name, email")
        client_id = cur.fetchone()[0]
    
    conn.commit()

    return client_id

def new_phone_number_for_client(conn, client_id, phone_number):
    with conn.cursor() as cur:
        # Вставляем телефон для клиента в таблицу phones
        cur.execute("INSERT INTO phones (client_id, phone_number) VALUES (%s, %s)", (client_id, phone_number))

    conn.commit()


    
def change_client_data(conn, client_id, first_name, last_name, email):
    with conn.cursor() as cur:

        cur.execute("UPDATE clients SET first_name = %s, last_name = %s, email = %s WHERE client_id = %s", (first_name, last_name, email, client_id))

    conn.commit()


def delete_phone_number_for_client(conn, phone_id):
    with conn.cursor() as cur:

        cur.execute("DELETE FROM phones WHERE phone_id = %s", (phone_id,))

    conn.commit()


def delete_client (conn, client_id):
    with conn.cursor() as cur:
    
        cur.execute("DELETE FROM CLIENT WHERE client_id = %s", (client_id,))

    conn.commit()
                

def find_client (conn, search_string):
    with conn.cursor() as cur:
         # Ищем клиента по имени, фамилии, email или телефону
        cur.execute("""
        SELECT clients.* 
        FROM clients
        LEFT JOIN phones ON clients.client_id = phones.client_id
        WHERE first_name = %s 
        OR last_name = %s 
        OR email = %s 
        OR phone_number = %s
        """, ('%' + search_string + '%', '%' + search_string + '%', '%' + search_string + '%', '%' + search_string + '%'))
        result = cur.fetchall()
    return result
        
       
if __name__ == "__main__": 

 # Создаем соединение с базой данных
    conn = psycopg2.connect(database="clients", user="postgress", password="Goblin000", host="localhost", port="5432")

    # Создаем структуру базы данных
    create_database_structure(conn)

    # Добавляем нового клиента
    new_client_id = add_client(conn, 'John', 'Doe', 'johndoe@example.com')

    
    # Добавляем нового клиента
    new_client_id = add_client(conn, 'Bill', 'Duce', 'BillDuce@example.com')


    
    # Добавляем нового клиента
    new_client_id = add_client(conn, 'Sam', 'Wayn', 'SamWayn@example.com')



    new_phone_number = new_phone_number_for_client(conn, 1, 89112221111)





    # Закрываем соединение с базой данных
    conn.close()