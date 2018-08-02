import os
import pdb
import logging
import json
from datetime import datetime
from main import tags_to_text, extract_tags, setup_logging, are_tags_changed

WAYBACK_FOLDER = "../wayback/websites/zeit.de/"


def file_list(root):
    # Return a listing of all archived index.html files in a folder
    collection = {}
    for root, dirs, files in os.walk(root):
        if root.endswith('zeit.de/'):
            logging.info("{} folders in total".format(len(dirs)))
        elif 'index.html' in files:
            ts = root.split(os.sep)[-2]
            collection[ts] = os.path.sep.join([root, 'index.html'])
    logging.info("{} folders with index.html".format(len(collection.keys())))
    return collection

def timestamp(ts):
    # Convert Wayback Archive timestamp to ISO-8601
    # Example: 20161223222443
    assert len(ts) == 14
    year = int(ts[0:4])
    month = int(ts[4:6])
    day = int(ts[6:8])
    hour = int(ts[8:10])
    minute = int(ts[10:12])
    second = int(ts[12:14])
    return datetime(year, month, day, hour, minute, second).isoformat()


if __name__ == "__main__":
    setup_logging(name='wayback')
    file_list = file_list(WAYBACK_FOLDER)

    with open('data.json') as f:
        store = json.load(f) 
        data = store['data']
        links = store['links']
        logging.debug("Loaded {} datasets and {} links".format(
            len(data.keys()), len(links.keys())))

    for ts, fn in list(file_list.items()):
        with open(fn) as f:
            try:
                html = f.read()
            except UnicodeDecodeError:
                logging.error("Could not decode possibly broken source file {}".format(fn))
        tags = extract_tags(html)
        new_data, new_links = tags_to_text(tags)

        if are_tags_changed(new_data, data):
            data[timestamp(ts)] = new_data
            links.update(new_links)
            store = {
                'data': data,
                'links': links
            }
            logging.info("On {}: {}".format(ts, ", ".join(new_data)))

    with open('data.json', 'w') as f:
        json.dump(store, f, indent=2, ensure_ascii=False, sort_keys=True)
    logging.debug("Updated: {} datasets and {} links".format(
        len(data.keys()), len(links.keys())))
