# SI 201 HW4 (Library Checkout System)
# Your name: Wesley Chan
# Your student id: 78133291
# Your email: wesleycc@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT): Gemini
# If you worked with generative AI also add a statement for how you used it.
# e.g.: 
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
# I used Gen AI to come up with questions and hints that would help me figure out code structure. If I was really stuck on something, which happened a couple times during debugging, I would ask Gen AI for an explanation behind the right answer. 
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
# Yes
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results
    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================

    #used GenAI to ask me leading questions, hints, as well as explanation of code for this part

    results = []

    with open(html_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    listings = soup.find_all('div', class_='c1l1h97y dir dir-ltr')
    #finds all llistings on page

    for listing in listings: 
        title_tag = listing.find('div', class_=re.compile(r't1jojoys'))
        title = title_tag.text.strip() if title_tag else ""
        #extracts listing title

        a_tag = listing.find('a', href=re.compile(r'/rooms/'))
        listing_id = ''
        if a_tag:
            href= a_tag.get('href', '')
            match = re.search(r'/rooms/(?:plus/)?(\d+)', href)
            if match:
                listing_id = match.group(1)
        
        results.append((title, listing_id))

    return results


    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================

    #used GenAI to ask me leading questions, hints, as well as explanation of code for this part

    html_path = os.path.join("html_files", f"listing_{listing_id}.html")

    details = {
        'policy_number': "Exempt",
        'host_type': "Regular", 
        'host_name': "", 
        "room_type": "",
        'location_rating': None
    }

    try: 
        with open(html_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

    except FileNotFoundError:
        return {listing_id: details}
    
    #1. policy number
    for li in soup.find_all('li', class_='f19phm7j dir dir-ltr'):
        if 'Policy number' in li.get_text():
            span = li.find('span')
            extracted = span.get_text().strip() if span else ''
            details['policy_number'] = extracted if extracted else "Pending"
            break

    #2. host type
    superhost_span = soup.find('span', class_='_1mhorg9')
    if superhost_span and 'Superhost' in superhost_span.get_text():
        details['host_type'] = "Superhost"

    #3. host name + room type
    h2 = soup.find('h2', class_='_14i3z6h')
    raw_room = ''
    if h2:
        text = h2.get_text()
        parts = re.split(r'hosted by\xa0|hostedby ', text, maxsplit=1)
        raw_room = parts[0].strip()
        details['host_name'] = parts[1].strip() if len(parts) > 1 else ''

    if not raw_room:
        kh3 = soup.find('div', class_='_kh3xmo')
        if kh3:
            raw_room = kh3.get_text().strip()

    if not details['host_name']:
        for h2b in soup.find_all('h2', class_='hnwb2pb dir dir-ltr'):
            txt = h2b.get_text()
            if txt.startswith('Hosted by '):
                details['host_name'] = txt.replace('Hosted by ', '').strip()

                break

    if raw_room.lower().startswith('entire'):
        details['room_type'] = 'Entire Room'
    elif raw_room.lower().startswith('private room'):
        details['room_type'] = 'Private Room'
    else:
        details['room)_type'] = raw_room


    #5. location rating
    for d in soup.find_all('div', class_='_y1ba89'):
        if d.get_text().strip() == 'Location':
            parent = d.find_parent('div', class_='_a3qxec')

            if parent: 
                score_span = parent.find('span', class_='_4oybiu')

                if score_span:
                    details['location_rating'] = float(score_span.get_text())

            break

    return {listing_id: details}

    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    database = [] #initialize empty list

    listings = load_listing_results(html_path) #call load_listing_results to get list of tuples

    for title, listing_id in listings:

        details_dict = get_listing_details(listing_id) #each listing id

        info = details_dict[listing_id] #extracting inner dictionary

        policy = info.get("policy_number")
        host_type = info.get("host_type")
        host_name = info.get("host_name")
        room_type = info.get("room_type")
        rating = info.get("location_rating")
        #extracting specific fields

        full_tuple = (title, listing_id, policy, host_type, host_name, room_type, rating)
        database.append(full_tuple)

    return database


    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    header = [
        "Listing Title", "Listing ID", "Policy Number", "Host Type", "host Name", "Room Type", "Location Rating"
    ]
    data.sort(key=lambda x: x[6] if x[6] is not None else 0.0, reverse=True)

    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)

    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    ratings_by_type = {}

    for row in data:
        room_type = row[5]
        location_rating = row[6]

        if location_rating is not None and location_rating != 0.0:
            if room_type not in ratings_by_type:
                ratings_by_type[room_type] = []
            ratings_by_type[room_type].append(location_rating)

    avg_ratings = {}
    for room_type, ratings in ratings_by_type.items():
        avg = sum(ratings) / len(ratings)
        avg_ratings[room_type] = round(avg, 1)

    return avg_ratings
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    invalid_ids = []

    #regex pattern: "STR-" followed by 7 digits
    valid_str_pattern = r"^STR-\d{7}$" #SF format
    valid_year_pattern = r"^\d{4}-\d+STR$" #city format

    for row in data:
        listing_id = row[1]
        policy = row[2]

        # stripping all whitespace and invisible characters
        policy_clean = re.sub(r'[\s ]+', '', policy).lower()

        #skip exempt and pending listings
        if policy_clean in ["exempt", "pending"] or not policy_clean:
            continue
        
        #strip only regular whitespace for regegx matching
        policy_stripped = policy.strip()

        #check against both valid formats
        if not re.match(valid_str_pattern, policy_stripped) and not re.match(valid_year_pattern, policy_stripped):
            invalid_ids.append(listing_id)

    return invalid_ids
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    from urllib.parse import quote_plus #encodes spaces as '+' for URL query params
    base_url = "https://scholar.google.com/scholar"
    url = base_url + "?q=" + quote_plus(query)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Wiin54; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "chrome/120.0.0.0 Safari/537.36"
        )
    }
    # gen AI helped me with headers

    response = response.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    titles = []

    for h3 in soup.find_all("h3", class_="gs_rt"):
        a_tag = h3.find("a")
        if a_tag: 
            title = a_tag.get_text().strip()
        else: 
            title = h3.get_text().strip
        if title:
            titles.append(title)

    return titles

    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.
        self.assertIsInstance(self.listings, list)

        self.assertEqual(len(self.listings), 18)

        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        self.assertIsInstance(self.listings[0], tuple)

        expected_first = ("Loft in Mission District", "1944564")

        self.assertEqual(self.listings[0], expected_first)
        pass

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # TODO: Call get_listing_details() on each listing id above and save results in a list.
        details_list = [get_listing_details(listing_id) for listing_id in html_list] #create a list of dictionaries by calling the function for each ID
        self.assertEqual(len(details_list), 5) #check there are 5 dictionaries returned

        for i, listing_id in enumerate(html_list):
            inner_dict = details_list[i][listing_id]
            self.assertIsInstance(inner_dict, dict)
            self.assertEqual(len(inner_dict), 5)



        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
            if listing_id == "467507":
                self.assertEqual(inner_dict.get("policy_number"), "STR-0005349")
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
            if listing_id == "1944564":
                self.assertEqual(inner_dict.get("host_type"), "Superhost")
                self.assertEqual(inner_dict.get("room_type"), "Entire Room")
        # 3) Check that listing 1944564 has the correct location rating 4.9.
                self.assertEqual(inner_dict.get("location_rating"), 4.9)
        pass

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
        for item in self.detailed_data:
            self.assertEqual(len(item), 7)

        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        expected_last = ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8)
        self.assertEqual(self.detailed_data[-1], expected_last)

        pass

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        output_csv(self.detailed_data, out_path)

        # TODO: Read the CSV back in and store rows in a list.
        with open(out_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)

        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].
        expected_first_data_row = ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"]
        self.assertEqual(rows[1], expected_first_data_row)

        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        result = avg_location_rating_by_room_type(self.detailed_data)

        # TODO: Check that the average for "Private Room" is 4.9.
        self.assertEqual(result.get("Private Room"), 4.9)

        pass

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        invalid_listings = validate_policy_numbers(self.detailed_data)

        # TODO: Check that the list contains exactly "16204265" for this dataset.
        expected_invalid = ["16204265"]
        self.assertEqual(invalid_listings, expected_invalid)

        pass


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)