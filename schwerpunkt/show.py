import json
import logging
import operator
import dateutil.parser
from datetime import datetime, timedelta

colors = ["#A1C9F4", "#FFB482", "#8DE5A1", "#FF9F9B", "#D0BBFF",
            "#DEBB9B", "#FAB0E4", "#FFFEA3", "#B9F2F0"]

colors = ['7BA1C6','7B87C6','877BC6','A17BC6','BA7BC6','C67BA1','C67B87','C6877B','C6A17B']

SCALE_FACTOR = 2.5

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name).24s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='schwerpunkt.log')

def print_logs(data):
    for key in sorted(data.keys()):
        dt = dateutil.parser.parse(key)
        print("{}\t{}".format(
            dt.strftime("%m/%d %H:%M"),
            ", ".join(sorted(data[key]))
        ))


def print_top(data):
    count = {}
    for tags in data.values():
        for tag in tags:
            try:
                count[tag] += 1
            except KeyError:
                count[tag] = 1
    top = sorted(count.items(), key=operator.itemgetter(1), reverse=True)
    for tag, count in top:
        if count > 1:
            print("  {} {}".format(count, tag))


def gen_palette(data):
    alltags = set()
    for tags in data.values():
        for tag in tags:
            alltags.add(tag)
    rv = {}
    for i, tag in enumerate(sorted(alltags)):
        rv[tag] = colors[i % len(colors)]
    rv['Podcasts'] = "#fefefe"
    return rv

def gen_cols(data):
    # Distribute tags on three columns, making sure that repeating tags
    # are represented as a continuous block

    # Each column is represented as a list of 3-tuples, each of which contains
    # a tag name, starting datetime and ending datetime
    cols = [[], [], []]

    # This is to keep track of tags that may continue on the column they started
    # on
    current_start = {}

    for dtstring in sorted(data.keys()):
        # dtstring is iso-8601 formatted
        dt = dateutil.parser.parse(dtstring)

        # If a tag from the previous set is not in the current tagset: remove
        # from current_start and update ending time to => dt
        for tag in list(current_start.keys()):
            col, pos = current_start[tag]
            if tag not in data[dtstring]:
                cols[col][pos][2] = dt
                del current_start[tag]

        for i, tag in enumerate(data[dtstring]):
            logging.debug(tag)

            if tag in current_start.keys():
                col, pos = current_start[tag]
                cols[col][pos][2] = dt
            else:
                # Determine a column for inserting if this tag is not cont.
                # from before. This is, well, clumsy. But I'm tired and it works.
                if len(cols[i]) == 0 or cols[i][-1][0] not in data[dtstring]:
                    j = i
                    logging.debug("insert {}".format(j % 3))
                else:
                    j = (i + 1) % 3
                    if len(cols[j]) != 0 and cols[j][-1][0] in data[dtstring]:
                        j = (j + 1) % 3
                j = j % 3
                current_start[tag] = [j, len(cols[j])]
                cols[j].append([tag, dt, None])

        prev = data[dtstring]

    # Extend last tags in each column to the end
    for i in range(3):
        cols[i][-1][2] = datetime.now()

    # Now the starting and ending datetime can be converted to a height
    # for css styling by calculating their delta
    def height(entry):
        try:
            delta = entry[2] - entry[1]
        except TypeError:
            delta = datetime.now() - entry[1]
        rv = SCALE_FACTOR * delta.total_seconds() / (60 * 60)
        return (entry[0], rv)

    cols = [list(map(height, col)) for col in cols]

    # print(json.dumps(cols, indent=2, ensure_ascii=False))
    return cols

def make_html(data, links):
    cols = gen_cols(data)
    palette = gen_palette(data)

    out_template = """
    <html>
    <head>
        <meta charset="utf-8"/>
        <title>Schwerpunkte der Zeit</title>
        <meta name="description" content="Auf Zeit.de werden stets drei Schwerpunkt-Themen benannt, die gerade
            die Nachrichten bestimmen. Diese Seite zeigt eine laufende Chronologie dieser 
            Schwerpunkte und beginnt dabei tief im Sommerloch...">
        <meta property="og:image" content="http://zeit.001.land/screen.png"/>  
        <link rel='stylesheet' href='reset.css' />
        <link rel='stylesheet' href='styles.css' />
    </head>
    <body>
        <div class='intro'>
            <h1>Schwerpunkte der Zeit</h1>
            <p>Auf Zeit.de werden stets drei Schwerpunkt-Themen benannt, die gerade
            die Nachrichten bestimmen. Diese Seite zeigt eine laufende Chronologie dieser 
            Schwerpunkte und beginnt dabei tief im Sommerloch...
            </p>
        </div>
        <div class='content'>
            <div class='index' style='width: 10%'>
                {col0}
            </div>

            <div class='flex-container'>
                {col1}
            </div>

            <div class='flex-container'>
                {col2}
            </div>

            <div class='flex-container'>
                {col3}
            </div>
        </div>

        <p>Ein Projekt von <a href='https://vincentahrend.com'>Vincent Ahrend</a>. 
        Kontakt über <a href='mailto:zeit-schwerpunkt@vincentahrend.com'>Email</a> 
        oder <a href='http://telegram.me/ululu'>Telegram</a>. 
        <a href='https://blog.vincentahrend.com/impressum/'>Impressum</a></p>
    </body>
    </html>
    """
    elem_template = """<div 
    style='min-height: {height}px; background-color: {color}'>
        {tag}
    </div>
    """
    html = ["" for i in range(4)]
    for i, col in enumerate(cols):
        for entry in col:
            if entry[0] == 'Podcasts':
                tag = ''
            else:
                tag = "<a href='{}'>{}</a>".format(
                    links[entry[0]] if entry[0] in links else '', entry[0])
            html[i + 1] += elem_template.format(
                tag=tag, 
                height=entry[1],
                color=palette[entry[0]]
            )

    beginning = dateutil.parser \
        .parse(sorted(data.keys())[0]) \
        .replace(hour=0, minute=0, second=0)
    days = (datetime.now() - beginning).total_seconds() / (60 * 60 * 24)
    for i in range(round(days)):
        day = beginning + timedelta(days=i)
        html[0] += "<div class='day'>{}</div>".format(
            day.strftime("%d.%m"))

    return out_template.format(
        col0=html[0], col1=html[1], col2=html[2], col3=html[3])


if __name__ == '__main__':
    with open('data.json', 'r') as f:
        store = json.load(f)
        data = store['data']
        links = store['links']
    # print_top(data)
    print_logs(data)
    
    html = make_html(data, links)
    with open('out/index1.html', 'w') as f:
        f.write(html)