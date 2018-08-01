import json
import operator
import dateutil.parser
from datetime import datetime, timedelta

colors = ["#A1C9F4", "#FFB482", "#8DE5A1", "#FF9F9B", "#D0BBFF",
            "#DEBB9B", "#FAB0E4", "#FFFEA3", "#B9F2F0"]

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
    rv['Podcasts'] = "#CFCFCF"
    return rv

def gen_cols(data):
    cols = [[], [], []]
    current_start = {}
    for dtstring in sorted(data.keys()):
        # print('\n\n' + dtstring)
        # print(data[dtstring])
        dt = dateutil.parser.parse(dtstring)

        for tag in list(current_start.keys()):
            col, pos = current_start[tag]
            if tag not in data[dtstring]:
                cols[col][pos][2] = dt
                del current_start[tag]
                # print('end ' + tag)

        for i, tag in enumerate(data[dtstring]):
            # print(tag)
            # if tag == 'Atomabkommen':
            #     import pdb; pdb.set_trace()
            if tag in current_start.keys():
                col, pos = current_start[tag]
                cols[col][pos][2] = dt
                # print('cont in {}'.format(col))
            else:
                if len(cols[i]) == 0 or cols[i][-1][0] not in data[dtstring]:
                    j = i
                    # print("insert {}".format(j % 3))
                else:
                    j = (i + 1) % 3
                    if len(cols[j]) == 0 or cols[j][-1][0] not in data[dtstring]:
                        # print("insert {} because {} is taken".format(j, i))
                        pass
                    else:
                        j = (j + 1) % 3
                        # print("insert {} because {} and {} is taken".format(j, i % 3, (i + 1) % 3))
                j = j % 3
                current_start[tag] = [j, len(cols[j])]
                cols[j].append([tag, dt, None])

        prev = data[dtstring]


    def dist(entry):
        try:
            delta = entry[2] - entry[1]
        except TypeError:
            delta = datetime.now() - entry[1]
        delta_total = 3 * delta.total_seconds() / (60 * 60)
        return (entry[0], delta_total)

    # extend current tags to the end
    for i in range(3):
        cols[i][-1][2] = datetime.now()

    cols = [list(map(dist, col)) for col in cols]

    
    # print(json.dumps(cols, indent=2, ensure_ascii=False))
    return cols

def make_html(data, links):
    cols = gen_cols(data)
    palette = gen_palette(data)
    out_template = """
    <html>
    <head>
        <link rel='stylesheet' href='styles.css' />
    </head>
    <body>
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
            tag = entry[0]
            if tag in links:
                tag = "<a href='{}'>{}</a>".format(links[tag], tag)
            if tag == 'Podcasts':
                tag = ''
            html[i + 1] += elem_template.format(
                tag=tag, 
                height=entry[1],
                color=palette[entry[0]]
            )

    beginning = dateutil.parser.parse(list(data.keys())[0])
    days = (datetime.now() - beginning).total_seconds() / (60 * 60 * 24)
    for i in range(round(days)):
        day = beginning + timedelta(days=i)
        html[0] += "<div class='day'>{}</div>".format(
            day.strftime("%d.%m"))

    return out_template.format(col0=html[0], col1=html[1], col2=html[2], col3=html[3])





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