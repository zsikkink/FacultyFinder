import requests
import psycopg2
import getpass
import json

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
        print(f"Fetched {len(results)} works for institution {institution_id}")  # Debug statement
        
        # Iterate through the works to extract authors
        for work in results:
            authors = work.get("authorships", [])
            for author in authors:
                author_id = author["author"]["id"]
                # Add the author to the list if they are unique and we haven't reached the limit
                if author_id not in seen_people and len(all_people) < 10:
                    detailed_author_info = fetch_author_details(author_id)
                    if detailed_author_info:  # Ensure valid data is returned
                        detailed_author_info["publications"] = fetch_author_publications(author_id)
                        detailed_author_info["institution_openalex_id"] = institution_id
                        all_people.append(detailed_author_info)
                        seen_people.add(author_id)
                if len(all_people) >= 10:
                    break
            if len(all_people) >= 10:
                break

        # Get the URL for the next page of results
        next_url = data.get("meta", {}).get("next_page_url")
        params = {}

    print(f"Total fetched authors for institution {institution_id}: {len(all_people)}")  # Debug statement
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

def fetch_author_publications(author_id):
    """
    Fetches the list of publications (openalex_id) for an author from OpenAlex.

    Args:
        author_id (str): The OpenAlex ID of the author.

    Returns:
        list: A list of openalex_id values for the author's publications.
    """
    publications = []
    works_api_url = f"https://api.openalex.org/works?filter=authorships.author.id:{author_id.split('/')[-1]}&per_page=200"
    next_url = works_api_url

    while next_url:
        response = requests.get(next_url)
        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            break

        try:
            data = response.json()
            publications.extend([work["id"] for work in data.get("results", [])])
            next_url = data.get("meta", {}).get("next_page_url")
        except requests.exceptions.JSONDecodeError:
            print(f"Error decoding JSON for author ID: {author_id}")
            break

    return publications

def clear_authors_table(user, password):
    conn = psycopg2.connect(
        dbname="uva_db",
        user=user,
        password=password,
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    # Clear the authors table
    cur.execute("DELETE FROM authors;")
    conn.commit()
    cur.close()
    conn.close()
    print("Cleared the authors table.")  # Debug statement

def clear_and_store_authors(authors, user, password):
    conn = psycopg2.connect(
        dbname="uva_db",
        user=user,
        password=password,
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    # Insert the new authors
    for author in authors:
        print(f"Inserting author: {author['display_name']}")  # Debug statement
        cur.execute("""
            INSERT INTO authors (openalex_id, display_name, orcid, works_count, cited_by_count, counts_by_year, works_api_url, cited_by_api_url, affiliations, h_index, i10_index, publications, updated_date, institution_openalex_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (openalex_id) DO NOTHING;
        """, (
            author["id"],
            author["display_name"],
            author.get("orcid"),
            author.get("works_count"),
            author.get("cited_by_count"),
            json.dumps(author.get("counts_by_year")),  # Convert dict to JSON string
            author.get("works_api_url"),
            author.get("cited_by_api_url"),
            json.dumps(author.get("affiliations")),  # Convert dict to JSON string
            author.get("h_index"),
            author.get("i10_index"),
            json.dumps(author.get("publications")),  # Convert list to JSON string
            author.get("updated_date"),
            author["institution_openalex_id"]
        ))

    conn.commit()
    cur.close()
    conn.close()
    print("Finished inserting authors.")  # Debug statement

def fetch_and_store_authors_from_all_institutions(user, password):
    conn = psycopg2.connect(
        dbname="uva_db",
        user=user,
        password=password,
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    # Fetch all institutions
    cur.execute("SELECT openalex_id FROM institutions;")
    institutions = cur.fetchall()

    all_authors = []

    for institution in institutions:
        institution_id = institution[0]
        print(f"Fetching authors for institution: {institution_id}")
        authors = fetch_institution_people(institution_id)
        all_authors.extend(authors)

    clear_and_store_authors(all_authors, user, password)
    conn.close()

def main():
    user = input("Enter the database username: ")
    password = getpass.getpass("Enter the database password: ")

    # Clear the authors table first
    clear_authors_table(user, password)

    # Fetch and store authors from all institutions
    fetch_and_store_authors_from_all_institutions(user, password)
    print("Stored authors from all institutions in the database.")

if __name__ == "__main__":
    main()