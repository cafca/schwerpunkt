import json
import operator
import dateutil.parser

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



if __name__ == '__main__':
    with open('data.json', 'r') as f:
        data = json.load(f)
    print_top(data)
    print_logs(data)