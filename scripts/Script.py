import requests

def fetch_institution_people(institution_id):
    """
    Fetches up to 10 people/faculty members associated with a given institution from OpenAlex.

    Args:
        institution_id (str): The OpenAlex ID of the institution.

    Returns:
        list: A list of dictionaries, each containing information about a person/faculty member.
    """
    base_url = "https://api.openalex.org/works"
    params = {
        "filter": f"institutions.id:{institution_id}",
        "per_page": 50,
        "mailto": "your_email@example.com"
    }

    all_people = []  # List to store the fetched people/faculty members
    seen_people = set()  # Set to keep track of unique author IDs
    next_url = base_url

    while next_url and len(all_people) < 10:
        response = requests.get(next_url, params=params)

        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            break

        data = response.json()
        results = data.get("results", [])
        
        # Iterate through the works to extract authors
        for work in results:
            authors = work.get("authorships", [])
            for author in authors:
                author_id = author["author"]["id"]
                # Add the author to the list if they are unique and we haven't reached the limit
                if author_id not in seen_people and len(all_people) < 10:
                    detailed_author_info = fetch_author_details(author_id)
                    if detailed_author_info:  # Ensure valid data is returned
                        all_people.append(detailed_author_info)
                        seen_people.add(author_id)
                if len(all_people) >= 10:
                    break
            if len(all_people) >= 10:
                break

        # Get the URL for the next page of results
        next_url = data.get("meta", {}).get("next_page_url")
        params = {}

    return all_people

def fetch_author_details(author_id):
    """
    Fetches detailed information about an author from OpenAlex.

    Args:
        author_id (str): The OpenAlex ID of the author.

    Returns:
        dict: A dictionary containing detailed information about the author.
    """
    author_api_url = f"https://api.openalex.org/authors/{author_id.split('/')[-1]}"
    response = requests.get(author_api_url)
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        return {}

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Error decoding JSON for author ID: {author_id}")
        return {}

def main():
    """
    Main function to fetch and print people/faculty members from a specified institution.
    """
    institution_id = "https://openalex.org/I51556381"  # Replace with the actual institution ID
    people = fetch_institution_people(institution_id)
    print(f"Fetched {len(people)} people/faculty from the institution.")
    for person in people:
        print(f"ID: {person['id']}")
        print(f"Name: {person['display_name']}")
        print(f"ORCID: {person.get('orcid')}")
        print(f"Works Count: {person.get('works_count')}")
        print(f"Cited By Count: {person.get('cited_by_count')}")
        print(f"Last Known Institution: {person.get('last_known_institution')}")
        print(f"Concepts: {person.get('x_concepts')}")
        print(f"Counts By Year: {person.get('counts_by_year')}")
        print(f"Works API URL: {person.get('works_api_url')}")
        print(f"Updated Date: {person.get('updated_date')}")
        print()

if __name__ == "__main__":
    main()