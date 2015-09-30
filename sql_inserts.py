__author__ = 'jbosley2'

import sql_settings as SQLS
import routines as ROUTINES


def insert_new_delivery_location(data):

    SQLS.db_update("INSERT INTO rooms (roomName) VALUES ('%s');" % data)

    SQLS.output_update_to_screen("Created new delivery destination . . . . . ")
    return "1"


def insert_new_delivery(data):

    fields = data[2].split("|")

    if fields[11] == "NA":
        return generate_non_repeated_delivery(fields)
    else:
        return generate_repeated_delivery(data)


def generate_non_repeated_delivery(fields):


   # Make new delivery query
    query = ROUTINES.generate_reservation_query(fields)

    # Submit it



    SQLS.db_update(query)

    if fields[10] != "NA":

       # Update inventorySchedule. - Go through each item in reservation and append schedule
        for el in fields[10].split(", "):


           # Get device schedule by id
            date_time_list_get = \
                SQLS.db_fetch("SELECT datesUnavailable FROM inventorySchedule WHERE inventoryItemID = %s;" % el)
            devices_current_schedule = date_time_list_get[0][0]

           # Build new schedule. If a blank schedule, set schedule to new data. Else: Append
            data_to_add_to_schedule = "%s | %s" % (fields[0], fields[1])

            new_device_schedule = ""
            if devices_current_schedule == "0000-00-00 00:00:00 | 0000-00-00 00:00:00":
                new_device_schedule = data_to_add_to_schedule
            else:
                new_device_schedule = devices_current_schedule + " # " + data_to_add_to_schedule

            query2 = "UPDATE inventorySchedule SET datesUnavailable = '%s' WHERE inventoryItemID = %s;"\
                     % (new_device_schedule, el)
            SQLS.db_update(query2)

    SQLS.output_update_to_screen("Created new non repeated delivery . . . . . ")

    return "1"


def generate_repeated_delivery(fields):

    # FIELDS : ['i', 'newr', '2015-01-07 20:00:27|2015-01-09 20:39:27|TEST|TEST|CRW 204|
    # NA|NA|0000-00-00 00:00:00|0000-00-00 00:00:00|NA|94|REFACTOR', '2015-01-07|2015-01-08|2015-01-09', 'D']

    # Range list for updating schedule
    scheduled_datetime_blocks = []
    # Range of dates that the delivery takes place
    range_of_dates = fields[3].split("|")
    # Information pertaining to delivery
    delivery_information = fields[2].split("|")

    # Go through each date and generate them
    # Original date time (first occurrence) also is in list
    reservation_start_time = delivery_information[0].split(" ")[1]
    reservation_end_time = delivery_information[1].split(" ")[1]

    # Record first and last occurrence for repeated table
    first_occurrence = delivery_information[0]
    last_occurrence = delivery_information[1]

    for el in range_of_dates:

        # Create start / end date-times from date el, and reservation times
        el_start = "%s %s" % (el, reservation_start_time)
        el_end = "%s %s" % (el, reservation_end_time)

        # Using generated start and end time on date el, make date block for scheduling
        datetime_block = "%s | %s" % (el_start, el_end)
        scheduled_datetime_blocks.append(datetime_block)

        # Set fields of start and end time to created start and end times for creating query
        delivery_information[0] = el_start
        delivery_information[1] = el_end

        # Send data to be made into an insert query, and submit it to the server

        SQLS.db_update(ROUTINES.generate_reservation_query(delivery_information))

    # Find ids of the deliveries generated
    id_list = ""
    for el in SQLS.db_fetch("SELECT resId FROM reservations WHERE repeatedIds = 'REFACTOR';"):
        if el[0] is not None:
            id_list += str(el[0])
            id_list += ","
    # Remove trailing comma
    id_list = id_list[:-1]

    # Make new entry for the repeated table with ids and insert into db
    SQLS.db_update(
        "INSERT INTO repeated (reservations, type, firstOccurance, lastOccurance) VALUES ('%s','%s','%s','%s');" %
        (id_list, fields[4], first_occurrence, last_occurrence))

    # Get id of new entry in repeated table, and assign to all reservations with repeatedIds = 'REFACTOR'
    id_of_new_entry = SQLS.db_fetch("SELECT repeatedid FROM repeated WHERE reservations = '%s';" % id_list)[0][0]

    # Update repeatedIds field in reservations to the new id for finalizing link
    SQLS.db_update("UPDATE reservations SET repeatedIds = '%s' WHERE repeatedIds = 'REFACTOR';" % id_of_new_entry)

    # Build string from new scheduled dates
    schedule_blocks = ""
    for el in scheduled_datetime_blocks:
        schedule_blocks += el
        schedule_blocks += " # "
    schedule_blocks = schedule_blocks[:-3]


    if delivery_information[10] != "NA":
        # Update each item in deliveries schedule
        for el in delivery_information[10].split(", "):

            date_time_list_get = \
                SQLS.db_fetch("SELECT datesUnavailable FROM inventorySchedule WHERE inventoryItemID = %s;" % el)
            devices_current_schedule = date_time_list_get[0][0]

            new_device_schedule = ""
            if devices_current_schedule == "0000-00-00 00:00:00 | 0000-00-00 00:00:00":
                new_device_schedule = schedule_blocks
            else:
                new_device_schedule = devices_current_schedule + " # " + schedule_blocks

            SQLS.db_update(
                "UPDATE inventorySchedule SET datesUnavailable = '%s' WHERE inventoryItemID = %s;" \
                % (new_device_schedule, el))

    SQLS.output_update_to_screen("Created new repeated delivery . . . . . ")

    return "1"


def insert_time_block_to_inventory_schedule(time_block, inventory_id):

    inv_data = SQLS.db_fetch(
        "SELECT * FROM inventorySchedule WHERE inventoryItemID = %s;" % inventory_id
    )[0]

    print inv_data

    if inv_data[2] == '0000-00-00 00:00:00 | 0000-00-00 00:00:00':

        SQLS.db_update(
            "UPDATE inventorySchedule SET datesUnavailable = '%s' WHERE inventoryItemID = %s;"
            % (time_block, inventory_id)
        )

    else:

        new_schedule = inv_data[2] + " # " + time_block

        SQLS.db_update(
            "UPDATE inventorySchedule SET datesUnavailable = '%s' WHERE inventoryItemID = %s;"
            % (new_schedule, inventory_id)
        )

    return