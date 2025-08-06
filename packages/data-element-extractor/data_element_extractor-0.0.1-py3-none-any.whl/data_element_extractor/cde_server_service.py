import requests
import json

from .helpers import MockText
from .config import config



class CDEServerService:
    def get_cde_server_url(self):
        return config.get_server_url()

    def set_cde_server_url(self, url):
        config.set_server_url(url)

    def fetch_data_from_server(self):
        """
        Example function to fetch data from the configured server URL.
        """
        try:
            response = requests.get(f"{self.get_cde_server_url()}/data", verify=False)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from server: {e}")
            return None

cde_server_service = CDEServerService()

def fetch_data_elements_from_server():
    """
    Fetches data elements from the server and returns them as a JSON object.
    """
    url=config.get_server_url() + "/api/data-elements"
    print(f"Fetching data from {url}...")
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.ConnectionError:
        print(f"\nError: Could not connect to the server at {url}.")
        print("Please make sure the Node.js server is running.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\nError fetching data from server: {e}")
        return None
    except json.JSONDecodeError:
        print("\nError: Could not decode JSON response from the server.")
        return None
    except requests.exceptions.SSLError as err:
        print(f"SSL Error: {err}")
        print("This might be because you are using a self-signed certificate.")
        print("Ensure you are using 'https' and, for development, you can use 'verify=False'.")
    except requests.exceptions.ConnectionError as err:
        print(f"Connection Error: {err}")
        print("Please ensure the Node.js server is running and listening on the correct port.")

    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")




def get_all_cdes():
    """
    Fetches all data elements (non-group) from the server.
    """
    data_elements = fetch_data_elements_from_server()
    if not data_elements:
        return []

    cdes = [cde for cde in data_elements if cde.get('type') == 'Value List' or cde.get('type') == 'Text' or cde.get('type') == 'Date' or cde.get('type') == 'Number']
    return cdes



def load_cdes_as_topics():

    all_cdes = get_all_cdes()
    if not all_cdes:
        return []

    topics = []
    for cde in all_cdes:

        tmp_topic_data = cde.get('type').lower()
        if tmp_topic_data == 'value list':
            tmp_topic_data = [pv.get('label') for pv in cde.get('permissibleValues', [])]
        topic = {
            'id': cde.get('id'),
            'name': cde.get('name'),
            'prompt': cde.get('prompt', ''),
            'categories': [pv.get('label') for pv in cde.get('permissibleValues', [])],
            'topic_data': tmp_topic_data,
            'condition': cde.get('condition', ''),
        }
        topics.append(topic)
    return topics


def get_cde_lists_from_server():
    """
    Fetches all CDE lists from the server.
    """
    url=config.get_server_url() + "/api/cdelists"
    print(f"Fetching CDE lists from {url}...")
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.ConnectionError:
        print(f"\nError: Could not connect to the server at {url}.")
        print("Please make sure the Node.js server is running.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\nError fetching data from server: {e}")
        return None
    except json.JSONDecodeError:
        print("\nError: Could not decode JSON response from the server.")
        return None




def _transform_cdes_to_topics(cdes: list):
    """
    Transforms a list of CDEs into a topic/category structure, filtering for 'Value List' type.
    """
    topics = []
    for cde in cdes:
        if cde.get('type') == 'Value List':
            categories = []
            #load categories (labels as names, ids as ids)
            for pv in cde.get('permissibleValues', []):
                category_id = pv.get('id')
                category_name = pv.get('label')
                categories.append((MockText(category_name), category_id))
            topic = {
                'id': cde.get('id'),
                'name': cde.get('name'),
                'prompt': cde.get('prompt', ''),
                'topic_data': [pv.get('label') for pv in cde.get('permissibleValues', [])],
                'categories': categories,
                'condition': cde.get('condition', ''),
            }
            topics.append(topic)
        if cde.get('type') == 'Text':
            topic = {
                'id': cde.get('id'),
                'name': cde.get('name'),
                'prompt': cde.get('prompt', ''),
                'topic_data': "text",
                'categories': [],
                'condition': cde.get('condition', ''),
            }
            topics.append(topic)
        if cde.get('type') == 'Date':
            topic = {
                'id': cde.get('id'),
                'name': cde.get('name'),
                'prompt': cde.get('prompt', ''),
                'topic_data': "date",
                'categories': [],
                'condition': cde.get('condition', ''),
            }
            topics.append(topic)
        if cde.get('type') == 'Number':
            topic = {
                'id': cde.get('id'),
                'name': cde.get('name'),
                'prompt': cde.get('prompt', ''),
                'topic_data': "number",
                'categories': [],
                'condition': cde.get('condition', ''),
            }
            topics.append(topic)
    return topics


def load_data_element_list_from_server(list_id: str):
    """
    Fetches a CDE list from the server and transforms its CDEs into topics.
    Args:
        list_id (str): The ID of the CDE list to load.
    """
    url = f"{config.get_server_url()}/api/cdelists/{list_id}"
    print(f"Fetching CDE list from {url}...")
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        cde_list = response.json()
        # The 'cdes' field is populated by the server route
        cdes = cde_list.get('cdes', [])
        if not cdes:
            print(f"Warning: CDE List '{list_id}' is empty or does not contain CDEs.")
            return []
            
        return _transform_cdes_to_topics(cdes)

    except requests.exceptions.ConnectionError:
        print(f"\nError: Could not connect to the server at {url}.")
        print("Please make sure the Node.js server is running.")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"\nError: CDE List with ID '{list_id}' not found.")
        else:
            print(f"\nError fetching data from server: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\nError fetching data from server: {e}")
        return None
    except json.JSONDecodeError:
        print("\nError: Could not decode JSON response from the server.")
        return None


def load_data_element_from_server(cde_id: str):
    """
    Fetches a CDE from the server and transforms it into a topic.
    Args:
        cde_id (str): The ID of the CDE to load.
    """
    url = f"{config.get_server_url()}/api/cdes/{cde_id}"
    print(f"Fetching CDE from {url}...")
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        cde = response.json()
        print(cde)
        return _transform_cdes_to_topics([cde])
    except requests.exceptions.ConnectionError:
        print(f"\nError: Could not connect to the server at {url}.")
        print("Please make sure the Node.js server is running.")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"\nError: CDE with ID '{cde_id}' not found.")
        else:
            print(f"\nError fetching data from server: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\nError fetching data from server: {e}")
        return None
    except json.JSONDecodeError:
        print("\nError: Could not decode JSON response from the server.")
        return None
        

if __name__ == '__main__':
    # This allows the script to be run directly for testing
    print("--- Testing load_cdes_as_topics() ---")
    topics = load_cdes_as_topics()
    if topics:
        print("\nSuccessfully loaded and transformed 'Value List' CDEs into topics:")
        print(json.dumps(topics, indent=4))
    else:
        print("\nNo topics were created.")
