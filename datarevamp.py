import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import csv

# Create an empty set to store the visited URLs
visited_urls = set()

def navigate_website(url, parent_url="", clicked_text=""):
    # Check if the URL ends with ".jpg" and return if it does
    if url.endswith(".jpg"):
        return

    # Check if the URL has a valid scheme
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = urljoin('http://', url)

    # Send an HTTP GET request to the current URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract relevant information from the current page
        extract_information(soup, url)

        # Add the current URL to the visited_urls set
        visited_urls.add(url)

        # Find all anchor tags on the page
        links = soup.find_all('a')

        # Follow each link and recursively navigate the website
        for link in links:
            # Get the absolute URL of the link
            href = link.get('href')
            absolute_url = urljoin(url, href)

            # Check if the absolute URL belongs to the /dentistry section
            if absolute_url.startswith("https://www.schulich.uwo.ca/dentistry/"):

                # Check if the absolute URL has already been visited
                if absolute_url not in visited_urls:
                    # Check if the link ends with ".jpg" and skip it
                    if href.endswith(".jpg"):
                        continue

                    # Recursive call to navigate the next page
                    navigate_website(absolute_url, url, link.text.strip())

    else:
        # Store the broken link information in the results list
        broken_link = {"URL": url, "Parent URL": parent_url, "Clicked Text": clicked_text}

        # Check if the broken link already exists in the visited_urls set
        if url not in visited_urls:
            # Print the title of the broken link (if available)
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string.strip() if soup.title else "N/A"
            broken_link["Title"] = title
            print(f"Broken Link: {url} (Title: {title})")

            # Add the broken link to the visited_urls set
            visited_urls.add(url)

            # Update the CSV file with the new broken link
            add_row_to_csv("schulich_results.csv", broken_link)

def extract_information(soup, url):
    title = soup.title
    if title is not None and title.string is not None:
        title_text = title.string.strip()

def add_row_to_csv(file_path, data_dict):
    # Write a row to the CSV file
    with open(file_path, "a", newline="") as csv_file:
        fieldnames = data_dict.keys()

        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Check if the file is empty, then write the headers
        if csv_file.tell() == 0:
            writer.writeheader()

        writer.writerow(data_dict)

# Starting point URL for the /dentistry section
starting_url = "https://www.schulich.uwo.ca/dentistry/"

# Create a new CSV file and save the headers
with open("schulich_results.csv", "w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["URL", "Parent URL", "Clicked Text", "Title"])

# Start navigating the website
navigate_website(starting_url)
