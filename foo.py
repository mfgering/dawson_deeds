import csv

f = open('reports/dawson.csv', 'r')
rdr = csv.reader(f, delimiter=',')

for row in rdr:
    print(row)