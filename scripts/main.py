import requests

def fetch_uva_institutions():
    base_url = "https://api.openalex.org/institutions"
    params = {
        "search": "University of Virginia",
        "per_page": 6,
        "mailto": "ted2ce@virginia.edu"
    }

    all_results = []
    next_url = base_url

    while next_url:
        response = requests.get(next_url, params=params)

        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            break

        data = response.json()
        results = data.get("results", [])
        print(f"Fetched {len(results)} results")  # Debug statement
        all_results.extend(results)
        next_url = data.get("meta", {}).get("next_page_url")
        params = {}

    print(f"Total fetched institutions: {len(all_results)}")  # Debug statement
    return all_results

def store_institutions(institutions):
    institution_list = []

    for inst in institutions:
        institution_data = {
            "display_name": inst["display_name"],
            "openalex_id": inst["id"],
            "ror_id": inst.get("ror"),
            "country_code": inst.get("country_code")
        }
        print(f"Storing institution: {institution_data}")  # Debug statement
        institution_list.append(institution_data)

    return institution_list

def filter_institutions(institutions):
    print("Fetched Institutions:")
    for i, inst in enumerate(institutions):
        print(f"{i + 1}. {inst['display_name']}")

    indices_to_remove = input("Enter the numbers of institutions to remove, separated by commas: ")
    indices_to_remove = [int(index) - 1 for index in indices_to_remove.split(",") if index.strip().isdigit()]

    filtered_institutions = [inst for i, inst in enumerate(institutions) if i not in indices_to_remove]
    return filtered_institutions

def main():
    institutions = fetch_uva_institutions()
    filtered_institutions = filter_institutions(institutions)
    stored_institutions = store_institutions(filtered_institutions)
    print(f"Stored {len(stored_institutions)} institutions in the list.")

if __name__ == "__main__":
    main()