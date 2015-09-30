__author__ = 'jbosley2'

import sql_settings as SQLS
import sql_selects as SELECT
import sql_inserts as INSERT

def admin_check_login(request):
    user_id = SQLS.db_fetch("SELECT username FROM userAccess WHERE username = '%s';" % request[2])
    if len(user_id) > 0:
        user_id = user_id[0][0]
        password = SQLS.db_fetch("SELECT password FROM userAccess WHERE username = '%s';" % user_id)[0][0]
        if password == request[3]:
            return "1"
    else:
        return "3"
    return "2"


def admin_edit_device_by_id(request):

    cells = request.split("|")

    SQLS.db_update(
        "UPDATE inventory SET title = '%s', description = '%s', type = '%s', barcode = '%s' WHERE invID = %s ;"
        % (cells[1], cells[2], cells[3], cells[4],  cells[0])
    )
    return "1"


def admin_add_device(request):

    cells = request.split("|")
    SQLS.db_update(
        "INSERT INTO inventory (title, description, type, barcode) VALUES ('%s','%s','%s','%s');" %
        (cells[0], cells[1], cells[2], cells[3])
    )

    new_id = SQLS.db_fetch(
        "SELECT invID FROM inventory WHERE title = '%s' AND barcode = '%s';" % (cells[0], cells[3])
    )[0][0]

    SQLS.db_update(
        "INSERT INTO inventorySchedule (inventoryItemID, datesUnavailable) "
        "VALUES ('%s','%s');" %
        (new_id, "0000-00-00 00:00:00 | 0000-00-00 00:00:00")
    )
    return "1"


def admin_remove_device(request):

    # Get list of reservations
    future_reservations = SQLS.db_fetch(
        "SELECT * from reservations WHERE DATE(resStart) >= CURDATE();"
    )

    conflicts = []
    repeated_ids_checked = []

    for el in future_reservations:

        each_device_in_reservation = el[11].split(", ")

        for ell in each_device_in_reservation:

            if ell == request:

                conflict_map = ""

                if el[12] != "NA" and el[12] not in repeated_ids_checked:

                    repeated_ids_checked = el[12]

                    startEndDateTimes = SQLS.db_fetch(
                        "SELECT firstOccurance, lastOccurance, type FROM repeated WHERE repeatedid = %s;" % el[12]
                    )

                    # If current reservation is part of a series, place in it's id and dates for repeated table
                    conflict_map = "r" + "|" + str(el[12]) + "|" + str(startEndDateTimes[0][0]) \
                                   + "|" + str(startEndDateTimes[0][1]) + "|" + startEndDateTimes[0][2] + "|" + str(ell)

                elif el[12] == "NA":

                    startEndDateTimes = SQLS.db_fetch(
                        "SELECT resStart, resEnd FROM reservations WHERE resId = %s;" % el[0]
                    )

                    # If current reservation is not part of a series, place in its resId, and dateTimes
                    conflict_map = "s" + "|" + str(el[0]) + "|" + str(startEndDateTimes[0][0]) \
                                   + "|" + str(startEndDateTimes[0][1]) + "|" + str(ell)

                if conflict_map != "":
                    conflicts.append(conflict_map)
                    conflicts.append("%")

    if len(conflicts) > 0:
        if conflicts[-1] == "%":
            conflicts.pop(-1)

    conflicts_to_return = ""

    for el in conflicts:
        conflicts_to_return += el

    # If there are conflicts with removing the device, alert the user to do a replacement call
    if conflicts_to_return != "":

        return conflicts_to_return

    else:

        SQLS.output_update_to_screen(("Removing device : " + request + ". No conflicts found."))

        SQLS.db_update(
            "DELETE FROM inventory WHERE invID = %s;" % request
        )

        SQLS.db_update(
            "DELETE FROM inventoryschedule WHERE inventoryItemID = %s;" % request
        )
    return "1"


def admin_do_remove_device(request):

    print " Replacing item in reservation(s)"

    cells = request.split("|")

    if cells[0] == "r":

        repeated_info = SQLS.db_fetch(
            "SELECT * FROM repeated WHERE repeatedid = %s; " % cells[1]
        )[0]

        for reservation_id in repeated_info[1].split(","):

            reservation = SQLS.db_fetch(
                "SELECT * FROM reservations WHERE resId = %s;" % reservation_id
            )[0]

            # Add time of reservation to the inventory schedule
            new_time_block = str(reservation[1]) + " | " + str(reservation[2])
            INSERT.insert_time_block_to_inventory_schedule(new_time_block, cells[2])

            new_items = []
            items = reservation[11].split(", ")
            for el in items:
                if el == cells[3]:
                    new_items.append(cells[2])
                    new_items.append(", ")
                else:
                    new_items.append(el)
                    new_items.append(", ")

            if len(new_items) > 0:
                if new_items[-1] == ", ":
                    new_items.pop(-1)

            list_string = ""
            for el in new_items:
                list_string += el

            SQLS.db_update(
                "UPDATE reservations SET inventoryList = '%s' WHERE resId = %s;" % (list_string, reservation_id)
            )

    elif cells[0] == "s":

        reservation = SQLS.db_fetch(
            "SELECT * FROM reservations WHERE resId = %s;" % cells[1]
        )[0]

        # Add time of reservation to the inventory schedule
        new_time_block = str(reservation[1]) + " | " + str(reservation[2])
        INSERT.insert_time_block_to_inventory_schedule(new_time_block, cells[2])

        new_items = []
        items = reservation[11].split(", ")
        for el in items:
            if el == cells[3]:
                new_items.append(cells[2])
                new_items.append(", ")
            else:
                new_items.append(el)
                new_items.append(", ")

        if len(new_items) > 0:
            if new_items[-1] == ", ":
                new_items.pop(-1)

        list_string = ""
        for el in new_items:
            list_string += el

        SQLS.db_update(
            "UPDATE reservations SET inventoryList = '%s' WHERE resId = %s;" % (list_string, cells[1])
        )

    return "1"


def change_user_password(request):

    SQLS.db_update(
        "UPDATE useraccess SET password = '%s' WHERE username = '%s';" % (request[3], request[2])
    )

    return "1"


# Technically an Admin function, but its sole purpose is to select
def proxy_select_future_reservations(date):
    return SELECT.select_reservations_by_date(date)
