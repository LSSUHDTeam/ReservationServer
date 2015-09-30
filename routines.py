__author__ = 'jbosley2'


def generate_reservation_query(fields):

    query = "INSERT INTO reservations ( resStart, resEnd, resFor, resBy, location, deliveredBy, pickedupBy," \
            "timeDelivered, timePickedup, notes, inventoryList, repeatedIds)" \
            "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" \
            % (fields[0],fields[1],
               fields[2],fields[3],fields[4],
               fields[5],fields[6],fields[7],
               fields[8],fields[9],fields[10],
               fields[11])
    return query