import datetime

month_map = {'Jan': 1, 'Feb': 2}

turnin = open('./cs460p1_turnin_test.txt')
for line in turnin.readlines():
    fields = line.split()
    year = 2016
    month = month_map[fields[5]]
    day = int(fields[6])
    hm = fields[7]
    hour = int(fields[7].split(':')[0])
    minute = int(fields[7].split(':')[1])
    netID = fields[8]

    dt = datetime.datetime(year, month, day, hour, minute)
    print(dt)
    #print(year, month, day, hour, minute, netID)
