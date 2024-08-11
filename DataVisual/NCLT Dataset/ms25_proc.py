import csv

from matplotlib import pyplot as plt

def getline(num):
    with open('ms25.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for i, row in enumerate(csvreader):
            if i == num:
                # if row[1] == "N/A" or row[1] == 0:
                #     continue
                data = {
                    'time': row[0],
                    'hx': row[1],
                    'hy': row[2],
                    'ax': float(row[4]),
                    'ay': float(row[5]),
                    'gz': float(row[9])
                }
                return data

ax = []
ay = []
gz = []
ia = []
with open('ms25.csv', newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for i, row in enumerate(csvreader):
        if i % 2 == 0:
            # if row[1] == "N/A" or row[1] == 0:
            #     continue
            data = {
                'time': row[0],
                'hx': row[1],
                'hy': row[2],
                'ax': float(row[4]),
                'ay': float(row[5]),
                'gz': float(row[9])
            }
            ax.append(data['ax'])
            ay.append(data['ay'])
            gz.append(data['gz'])
            ia.append(i)
            with open('ms_trim.csv', mode='a', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=['time', 'hx', 'hy', 'ax', 'ay', 'gz'])
                    writer.writerow(data)

    # plt.plot(ia, ax, color='red', label='GPS RTK')
    # plt.plot(ia, ay, color='red', label='GPS RTK')
    #
    # plt.xlabel('X Coordinate')
    # plt.ylabel('Y Coordinate')
    # # plt.xlim(-20, 0)
    # # plt.ylim(-17, -7)
    # plt.title('Scatter Plot of Points')
    # # plt.gca().invert_yaxis()
    #
    # plt.legend()
    #
    # plt.show()