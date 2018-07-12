import requests
import json
import datetime
import logging
from bs4 import BeautifulSoup


def setup_logging():
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name).24s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='schwerpunkt.log')

def get_html():
    url = "https://www.zeit.de/index"
    return requests.get(url)

def extract_tags(html):
    soup = BeautifulSoup(html.content, 'html.parser')
    return soup.find_all('a', class_='nav__tag')

def timestamp():
    return datetime.datetime.now().isoformat()

def tags_as_text(tags):
    return sorted([tag.text.strip() for tag in tags])

def are_tags_changed(new_data, old_data):
    if len(old_data.keys()) == 0:
        return True
    else:
        last_entry = old_data[list(old_data.keys())[-1]]
        return set(last_entry) != set(new_data)


if __name__ == '__main__':
    setup_logging()

    with open('data.json') as f:
        data = json.load(f) 
        logging.debug("Loaded {} datasets".format(len(data.keys())))
    
    try:
        html = get_html()
        tags = extract_tags(html)
        new_data = tags_as_text(tags)
    except Exception as e:
        logging.error("Error extracting: {}".format(e))
    else:
        if are_tags_changed(new_data, data):
            data[timestamp()] = new_data

            with open('data.json', 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logging.info("Inserted new tags: {}".format(", ".join(new_data)))
        else:
            logging.debug("No new tags")