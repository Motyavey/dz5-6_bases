import requests
from time import time
from openpyxl import Workbook
import os
from dotenv import load_dotenv

# Завантаження змінних середовища з файлу .env
load_dotenv()

# Отримання базової URL-адреси зі змінної середовища
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")  # За замовчуванням використовується localhost, якщо не вказано

def generate_data(num_records):
    return [{"name": f"Name {i}", "value": i} for i in range(num_records)]

def test_api_performance(num_records, results):
    print(f"\n--- Тестування API з {num_records} записами ---")

    requests.post(f"{BASE_URL}/setup")

    start = time()
    batch_size = 10000
    data = generate_data(num_records)
    for i in range(0, num_records, batch_size):
        requests.post(f"{BASE_URL}/insert", json={"data": data[i:i + batch_size]})
    insert_time = time() - start
    print(f"INSERT: {insert_time:.2f} сек")

    start = time()
    response = requests.get(f"{BASE_URL}/select")
    select_time = time() - start
    print(f"SELECT: {select_time:.2f} сек")
    select_plan = response.json().get("execution_plan", [])

    start = time()
    response = requests.put(f"{BASE_URL}/update")
    update_time = time() - start
    print(f"UPDATE: {update_time:.2f} сек")
    update_plan = response.json().get("execution_plan", [])

    start = time()
    response = requests.delete(f"{BASE_URL}/delete")
    delete_time = time() - start
    print(f"DELETE: {delete_time:.2f} сек")
    delete_plan = response.json().get("execution_plan", [])

    results.append([num_records, insert_time, select_time, update_time, delete_time, select_plan, update_plan, delete_plan])

def save_results_to_excel(results):
    wb = Workbook()
    ws = wb.active
    ws.title = "Результати продуктивності API"
    ws.append(["Кількість записів", "INSERT (сек)", "SELECT (сек)", "UPDATE (сек)", "DELETE (сек)", "SELECT (план)", "UPDATE (план)", "DELETE (план)"])
    for row in results:
        ws.append([
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            "\n".join([" ".join(map(str, plan)) for plan in row[5]]),
            "\n".join([" ".join(map(str, plan)) for plan in row[6]]),
            "\n".join([" ".join(map(str, plan)) for plan in row[7]])
        ])
    wb.save("api_performance_results.xlsx")
    print("\nРезультати збережено у файл 'api_performance_results.xlsx'.")

results = []
for records in [1000, 10000, 100000, 1000000]:
    test_api_performance(records, results)

save_results_to_excel(results)
