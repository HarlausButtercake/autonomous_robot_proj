import csv


def print_line(csv_file_path, num):
    with open(csv_file_path, newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for i, row in enumerate(csvreader):
            if i == num - 1:  # 102 because indexing starts at 0
                print(row)
                break

def to_data(num):
    with open('Log_ULIS_c2.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for i, row in enumerate(csvreader):
            if i == num - 1:  # 102 because indexing starts at 0
                data = {
                    'time': row[0],
                    'lat': float(row[1]),
                    'lon': float(row[2]),
                    'Ax': float(row[3]),
                    'Ay': float(row[4]),
                    'Gz': float(row[5]),
                    'bearing': float(row[6])
                }
                return data


def time_parser(time):
    hh, mm, ss = map(int, time.strip().split(':'))
    return hh*3600 + mm*60 + ss

# Replace 'your_file.csv' with the path to your CSV file
dat1 = to_data(1003)
dat2 = to_data(1379)
print( )
