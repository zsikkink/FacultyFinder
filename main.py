import requests


def fetch_all_uva_institutions():
    base_url = "https://api.openalex.org/institutions"
    params = {
        "search": "University of Virginia",
        "per_page": 50,
        "mailto": "your_email@example.com"
    }

    all_results = []
    next_url = base_url

    while next_url:
        response = requests.get(next_url, params=params)

        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            break

        data = response.json()

        # Debug: print the structure to see what's in it
        # print("RESPONSE DATA:", data)

        # If there's no "results" key or it's empty, just break
        results = data.get("results", [])
        if not results:
            break
        all_results.extend(results)

        # Use .get to avoid KeyErrors
        next_url = data.get("meta", {}).get("next_page_url")

        # Clear params for subsequent calls, because next_url already includes them
        params = {}

    return all_results


def main():
    institutions = fetch_all_uva_institutions()
    print(f"Found {len(institutions)} UVA-related institution records.")
    for inst in institutions:
        print(
            f"Name: {inst['display_name']}\n"
            f"OpenAlex ID: {inst['id']}\n"
            f"ROR: {inst.get('ror')}\n"
            f"Country Code: {inst.get('country_code')}"
        )
        print("-----")


if __name__ == "__main__":
    main()
