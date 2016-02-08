import csv

roster_file = open('roster.csv')
roster_csv = csv.reader(roster_file, delimiter=',')
for row in roster_csv:
    lname = row[0].strip()
    fmname = row[1].strip()
    fname = fmname.split()[0]
    netID = row[2].strip()
    status = row[3].strip()
    csID = row[4].strip()
    print(lname, fname, netID, status, csID)
