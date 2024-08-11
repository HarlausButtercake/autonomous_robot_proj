import csv

with open('LDT_St.csv', newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for i, row in enumerate(csvreader):
        if i > 50:
            data = {
                'time': row[0],
                'lat': float(row[1]),
                'lon': float(row[2]),
                'Ax': float(row[3]),
                'Ay': float(row[4]),
                'Ax_lin': float(row[5]),
                'Ay_lin': float(row[6]),
                'Gz': float(row[7]),
                'bearing': float(row[8])
            }
            if data['Ax_lin'] > -0.1 and data['Ax_lin'] < 0.1:
                if data['Ay_lin'] > -0.1 and data['Ay_lin'] < 0.1:
                    print(i)
                    break