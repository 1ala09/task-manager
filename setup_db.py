from db import get_connection

conn = get_connection()
conn.execute(""" 
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL    
    )
""")
conn.execute(""" 
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        title VARCHAR(200) NOT NULL,
        completed BOOLEAN DEFAULT FALSE,
        user_id INTEGER REFERENCES users(id)
    )
""")


conn.commit()
conn.close()

print("Users table created successfully!")
