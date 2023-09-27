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
            phone_number VARCHAR(20) UNIQUE
        );
        """)
    conn.commit()

#Добавляем нового клиента
def add_client(conn, first_name, last_name, email):
    with conn.cursor() as cur:
        # Проверяем, есть ли клиент с таким именем и фамилией в базе данных
        cur.execute("SELECT client_id FROM clients WHERE first_name = %s AND last_name = %s", (first_name, last_name))
        existing_client = cur.fetchone()

        if existing_client:
            # Клиент с таким именем и фамилией уже существует, вернуть его идентификатор
            return existing_client[0]

        # Вставляем нового клиента, так как его имя и фамилия не совпадают с существующими
        cur.execute("INSERT INTO clients (first_name, last_name, email) VALUES (%s, %s, %s) RETURNING client_ID", (first_name, last_name, email))
        client_id = cur.fetchone()[0]

    conn.commit()
    return client_id



def add_phone_number_for_client(conn, client_id, phone_number):
    with conn.cursor() as cur:
        # Проверяем, существует ли клиент с указанным client_id
        cur.execute("SELECT 1 FROM clients WHERE client_id = %s", (client_id,))
        existing_client = cur.fetchone()

        if existing_client:
            # Если клиент существует, то проверяем, есть ли уже такой номер телефона
            cur.execute("SELECT 1 FROM phones WHERE client_id = %s AND phone_number = %s::VARCHAR", (client_id, str(phone_number)))
            existing_entry = cur.fetchone()

            if not existing_entry:
                # Если записи не существует, то вставляем номер телефона
                cur.execute("INSERT INTO phones (client_id, phone_number) VALUES (%s, %s::VARCHAR)", (client_id, str(phone_number)))

    conn.commit()

#Меняем некоторые данные клиента кроме телефона
def change_client_data(conn, client_id, new_first_name=None, new_last_name=None, new_email=None):
    with conn.cursor() as cur:
        query = "UPDATE clients SET "
        params = []

        if new_first_name is not None:
            query += "first_name = %s, "
            params.append(new_first_name)
        if new_last_name is not None:
            query += "last_name = %s, "
            params.append(new_last_name)
        if new_email is not None:
            query += "email = %s, "
            params.append(new_email)

        # Удаляем последнюю запятую и добавляем условие WHERE
        query = query.rstrip(", ") + " WHERE client_id = %s"
        params.append(client_id)

        cur.execute(query, params)

    conn.commit()

#Удаляем данные о телефоне клиента  
def delete_phone_number_for_client(conn, phone_id):
    with conn.cursor() as cur:

        cur.execute("DELETE FROM phones WHERE phone_id = %s", (phone_id,))

    conn.commit()

#Удаляем  клиента  
def delete_client(conn, client_id):
    with conn.cursor() as cur:
        try:
            # Удаляем записи о телефонах клиента
            cur.execute("DELETE FROM phones WHERE client_id = %s", (client_id,))
            
            # Теперь, после удаления связанных записей, можно удалить самого клиента
            cur.execute("DELETE FROM clients WHERE client_id = %s", (client_id,))
        except Exception as e:
            conn.rollback()
            raise e

    conn.commit()
                
# Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону.
def find_client(conn, search_string):
    with conn.cursor() as cur:
        cur.execute("""
        SELECT DISTINCT clients.client_id, first_name, last_name, email
        FROM clients
        LEFT JOIN phones ON clients.client_id = phones.client_id
        WHERE first_name LIKE %s 
        OR last_name LIKE %s 
        OR email LIKE %s 
        OR phone_number LIKE %s
        """, ('%' + search_string + '%', '%' + search_string + '%', '%' + search_string + '%', '%' + search_string + '%'))
        result = cur.fetchall()
    return result
        
       
if __name__ == "__main__": 

 # Создаем соединение с базой данных
    conn = psycopg2.connect(database="clients", user="postgres", password="Samsung000", host="localhost", port="5432")
    

    # Создаем структуру базы данных
    create_database_structure(conn)

    # # Добавляем нового клиента
    new_client_id = add_client(conn, 'John', 'Doe', 'johndoe@example.com')

    
    # Добавляем нового клиента
    new_client_id = add_client(conn, 'Bill', 'Duce', 'BillDuce@example.com')


    
    # Добавляем нового клиента
    new_client_id = add_client(conn, 'Sam', 'Wayn', 'SamWayn@example.com')


    # Добавляем номера телефонов новым клиентам
    new_phone_number = add_phone_number_for_client(conn, 1, 89112221111)

    new_phone_number = add_phone_number_for_client(conn, 1, 891122222222)

    new_phone_number = add_phone_number_for_client(conn, 2, 89133333333)
    
    new_phone_number = add_phone_number_for_client(conn, 3, 8914444444)


    # # Меняем данные клиента
    # change_client_data(conn, 1, 'Vasya', 'Petrov', None,)

    # change_client_data(conn, 2, 'Vasya', None, 'Petrov@test.ru')



    # #Удаляем данные о телефоне клиента  
    # delete_phone_number_for_client(conn, 3)

    # # delete_phone_number_for_client(conn, 2)



    # #Удаляем  клиента  
    # delete_client (conn, 1)



 # ищем клиента по его данным: имени, фамилии, email или телефону.
    
    results = find_client (conn, 'John')
    print("Результаты поиска:")
    if results:
        print("Результаты поиска:")
        for result in results:
            print(result)
    else:
        print("Клиент не найден.")






    # Закрываем соединение с базой данных
    conn.close()