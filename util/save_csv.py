import csv

def save_csv(filename, header, rows):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    f = open(filename, 'w+', encoding='UTF8')
    writer = csv.writer(f)
    writer.writerow(header)
    for r in rows:
        writer.writerow(r)
