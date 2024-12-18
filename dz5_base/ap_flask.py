from flask import Flask, request, jsonify
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Підключення до бази даних з використанням змінних середовища
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dbname=os.getenv("DB_NAME"),
    sslmode="require"
)
cur = conn.cursor()

@app.route('/setup', methods=['POST'])
def setup_table():
    cur.execute("DROP TABLE IF EXISTS test_perf;")
    cur.execute("""
        CREATE TABLE test_perf (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50),
            value INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return jsonify({"message": "Таблицю успішно створено"})

@app.route('/insert', methods=['POST'])
def insert_data():
    data = request.json['data']  
    args_str = ",".join(cur.mogrify("(%s, %s)", (row['name'], row['value'])).decode() for row in data)
    cur.execute("INSERT INTO test_perf (name, value) VALUES " + args_str)
    conn.commit()
    return jsonify({"message": "Дані успішно додано"})

@app.route('/select', methods=['GET'])
def select_data():
    cur.execute("SELECT * FROM test_perf;")
    rows = cur.fetchall()
    return jsonify(rows)

@app.route('/update', methods=['PUT'])
def update_data():
    cur.execute("UPDATE test_perf SET value = value + 1;")
    conn.commit()
    return jsonify({"message": "Дані успішно оновлено"})

@app.route('/delete', methods=['DELETE'])
def delete_data():
    cur.execute("DELETE FROM test_perf;")
    conn.commit()
    return jsonify({"message": "Дані успішно видалено"})

if __name__ == '__main__':
    app.run(debug=True)
