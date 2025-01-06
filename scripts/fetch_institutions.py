import requests
import psycopg2
import getpass

def fetch_uva_institutions():
    base_url = "https://api.openalex.org/institutions"
    params = {
        "search": "University of Virginia",
        "per_page": 6,
        "mailto": "your_email@example.com"
    }

    all_results = []
    next_url = base_url

    while next_url and len(all_results) < 6:
        response = requests.get(next_url, params=params)

        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            break

        data = response.json()
        results = data.get("results", [])
        print(f"Fetched {len(results)} results")  # Debug statement
        all_results.extend(results[:6 - len(all_results)])
        next_url = data.get("meta", {}).get("next_page_url")
        params = {}

    print(f"Total fetched institutions: {len(all_results)}")  # Debug statement
    return all_results

def clear_and_store_institutions(institutions, user, password):
    conn = psycopg2.connect(
        dbname="institutions",
        user=user,
        password=password,
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    # Clear the institutions table
    cur.execute("DELETE FROM institutions;")

    # Insert the new institutions
    for inst in institutions:
        cur.execute("""
            INSERT INTO institutions (display_name, openalex_id, ror_id, country_code, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            ON CONFLICT (openalex_id) DO NOTHING;
        """, (
            inst["display_name"],
            inst["id"],
            inst.get("ror"),
            inst.get("country_code")
        ))

    conn.commit()
    cur.close()
    conn.close()

def filter_institutions(institutions):
    print("Fetched Institutions:")
    for i, inst in enumerate(institutions):
        print(f"{i + 1}. {inst['display_name']}")

    remove = input("Do you want to remove any institutions? (yes/no): ").strip().lower()
    if remove == 'yes':
        indices_to_remove = input("Enter the numbers of institutions to remove, separated by commas: ")
        indices_to_remove = [int(index) - 1 for index in indices_to_remove.split(",") if index.strip().isdigit()]
        institutions = [inst for i, inst in enumerate(institutions) if i not in indices_to_remove]

    return institutions

def main():
    user = input("Enter the database username: ")
    password = getpass.getpass("Enter the database password: ")

    institutions = fetch_uva_institutions()
    filtered_institutions = filter_institutions(institutions)
    clear_and_store_institutions(filtered_institutions, user, password)
    print(f"Stored {len(filtered_institutions)} institutions in the database.")

if __name__ == "__main__":
    main()