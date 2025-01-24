import requests
import psycopg2
import getpass
import json

def fetch_publication_details(publication_url):
    """
    Fetches the title and abstract of a publication from OpenAlex.

    Args:
        publication_url (str): The OpenAlex URL of the publication.

    Returns:
        dict: A dictionary containing the title and abstract of the publication.
    """
    response = requests.get(publication_url)
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        return None

    try:
        data = response.json()
        title = data.get("title")
        abstract = data.get("abstract")
        return {"title": title, "abstract": abstract}
    except requests.exceptions.JSONDecodeError:
        print(f"Error decoding JSON for publication URL: {publication_url}")
        return None

def fetch_and_store_publications(user, password):
    conn = psycopg2.connect(
        dbname="uva_db",
        user=user,
        password=password,
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    # Fetch all authors and their publications
    cur.execute("SELECT openalex_id, publications FROM authors;")
    authors = cur.fetchall()

    all_publications = {}

    for author in authors:
        author_id, publications = author
        if not isinstance(publications, list):
            print(f"Error: publications for author {author_id} is not a list")
            continue

        for publication_url in publications:
            publication_details = fetch_publication_details(publication_url)
            if publication_details:
                title = publication_details["title"]
                abstract = publication_details["abstract"]
                if title and abstract:
                    all_publications[title] = abstract

    cur.close()
    conn.close()

    return all_publications

def main():
    user = input("Enter the database username: ")
    password = getpass.getpass("Enter the database password: ")

    publications_dict = fetch_and_store_publications(user, password)
    print("Fetched and stored publications:")
    for title, abstract in publications_dict.items():
        print(f"Title: {title}\nAbstract: {abstract}\n")

if __name__ == "__main__":
    main()