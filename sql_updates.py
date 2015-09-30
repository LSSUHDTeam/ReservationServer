__author__ = 'jbosley2'

import sql_settings as SQLS
import routines as ROUTINES
import sql_inserts as INSERTS

def update_delivery_set_delivered(request):

    SQLS.db_update("UPDATE reservations SET deliveredBy = '%s', timeDelivered = '%s' WHERE resId = %s;" %
                   (request[3], request[4], request[2]))

    SQLS.output_update_to_screen(" Updated delivery [%s] . . . . . . ." % request[2])

    return "1"


def update_reservation_for_pickup(request):

    reservationId = request[2]
    timePickedUp = request[3].split("|")[0]
    pickedUpBy = request[3].split("|")[1]

    SQLS.db_update("UPDATE reservations SET pickedupBy = '%s', timePickedup = '%s' WHERE resId = %s; "
                   % (pickedUpBy, timePickedUp, reservationId))

    remove_times_from_schedule_by_reservation_id(reservationId)


    SQLS.output_update_to_screen(" Updated reservation [%s] . . . . . . ." % reservationId)

    return "1"


def remove_times_from_schedule_by_reservation_id(resId):

    the_reservation = SQLS.db_fetch("SELECT * from reservations WHERE resId = %s;" % resId)[0]

    time_block = str(the_reservation[1]) + " | " + str(the_reservation[2])

    # For each item in inventory list
    if the_reservation[11] != "NA":
        for el in the_reservation[11].split(", "):

            new_time_blocks = []

            # Get schedule and go through each time block
            for the_time_block in SQLS.db_fetch(
                    "SELECT datesUnavailable FROM inventorySchedule WHERE inventoryItemID = %s;" %
                    el)[0][0].split(" # "):

                # If the specific time_block doesn't equal the one being weeded out, add to the new_time_blocks list
                if the_time_block != time_block:
                    new_time_blocks.append(the_time_block)

            # Once time blocks list is built, turn into a formatted schedule string and update DB
            new_schedule = ""
            for item in new_time_blocks:
                new_schedule += item
                new_schedule += " # "

            if len(new_schedule) > 1:
                new_schedule = new_schedule[:-3]
            else:
                new_schedule = "0000-00-00 00:00:00 | 0000-00-00 00:00:00"

            SQLS.db_update("UPDATE inventorySchedule SET datesUnavailable = '%s' WHERE inventoryItemID = %s;"
                           % (new_schedule, el))

    SQLS.output_update_to_screen(" Removed times in schedule for reservation [%s] . . . ." % resId)

    return


def update_delivery_series(request):

    if request[2] != "REMOVE":

        cells = request[2].split("|")
        update_type = cells[11].split("#")

        # UPDATE A SINGLE DELIVERY
        if update_type[0] == "UPDATE_SINGLE":

            #print "Updating single delivery"
            #print len(request)

            # Turn the single delivery into a repeated delivery
            if len(request) == 5:
                #print "Making it a repeated delivery"
                delivery_series_repeated_from_single(request)

            # Change the information in the single delivery
            elif len(request) == 3:

                #print "Altering single delivery"
                # Remove Schedule times
                remove_times_from_schedule_by_reservation_id(update_type[1])

                # Remove from DB
                SQLS.db_update(
                    "DELETE FROM reservations WHERE resId = '%s';" % update_type[1]
                )
                # Generate Delivery in its place
                cells[11] = "NA"
                INSERTS.generate_non_repeated_delivery(cells)

        # UPDATE A REPEATED DELIVERY
        if update_type[0] == "UPDATE_REPEATED":

            # All editing of repeated deliveries will remove and re-add so perform this function asap

            # Select the reservation ids from repeated table
            linked_information = SQLS.db_fetch(
                "SELECT reservations FROM repeated WHERE repeatedid = %s;" % update_type[1]
            )[0][0]

            reservations_in_series = linked_information.split(",")

            for el in reservations_in_series:

                # Remove from schedule all date times in this series
                remove_times_from_schedule_by_reservation_id(el)

                # Delete all reservations currently in this series
                SQLS.db_update(
                    "DELETE FROM reservations WHERE resId = '%s';" % el
                )

            # Delete repeated link
            SQLS.db_update(
                "DELETE FROM repeated WHERE repeatedid = %s;" % update_type[1]
            )

            # Change the repetition of a delivery
            if len(request) == 5:

                # Edit request to INSERTS.generate_repeated_delivery specifications
                cells[11] = "REFACTOR"
                dummy_field = ""
                for el in cells:
                    dummy_field += el
                    dummy_field += "|"
                dummy_field = dummy_field[:-1]
                request[2] = dummy_field

                # Generate new repeated delivery
                INSERTS.generate_repeated_delivery(request)

            # Remove the repetition of a delivery
            elif len(request) == 4:

                #print " Removing the repetition of a delivery"
                cells = request[2].split("|")
                cells[11] = "NA"
                INSERTS.generate_non_repeated_delivery(cells)

    if request[2] == "REMOVE":

        # REMOVE ALL DELIVERIES OF SERIES
        #print " REMOVE ALL IN SERIES "
        repeated_id = request[4]

        # get deliveries from repeated table, remove deliveries with delete, and trim devices out of schedule
        if repeated_id != "NA":
            linked_information = SQLS.db_fetch(
                "SELECT reservations FROM repeated WHERE repeatedid = %s;" % repeated_id
            )[0][0]

            for el in linked_information.split(","):

                remove_times_from_schedule_by_reservation_id(el)

                SQLS.db_update(
                    "DELETE FROM reservations WHERE resId = '%s' AND DATE(resStart) >= CURDATE();" % el
                )

            SQLS.db_update(
                "DELETE FROM repeated WHERE repeatedid = %s;" % repeated_id
            )
        else:

            remove_times_from_schedule_by_reservation_id(request[3])

            SQLS.db_update(
                "DELETE FROM reservations WHERE resId = %s;" % request[3]
            )

    return "1"


# Called by update_delivery_series
def delivery_series_changed_schedule(request):

    cells = request[2].split("|")
    current_link_id = cells[11].split("#")[1]

    # Get each delivery in series and remove schedule information
    for resId in SQLS.db_fetch("SELECT reservations FROM repeated WHERE repeatedid = '%s';" % current_link_id)\
        [0][0].split(","):
        remove_times_from_schedule_by_reservation_id(resId)

    # Remove future deliveries in this series
    SQLS.db_update(
        "DELETE FROM reservations WHERE repeatedIds = '%s' AND DATE(resStart) >= CURDATE();" % current_link_id)

    # Remove repeated link if any
    SQLS.db_update(
        "DELETE FROM repeated WHERE repeatedid = '%s';" % current_link_id
    )

    cells[11] = "REFACTOR"

    new_delivery_string = ""
    for el in cells:
        new_delivery_string += el
        new_delivery_string += "|"
    new_delivery_string = new_delivery_string[:-1]

    new_request = ["MOOT", "MOOT", new_delivery_string, request[3], request[4]]

    INSERTS.insert_new_delivery(new_request)

    SQLS.output_update_to_screen("Edited an existing delivery schedule . . . . . ")
    return


# Called by update_delivery_series
def delivery_series_repeated_from_single(request):

    x = request[2].split("|")
    res_id = x[11].split("#")[1]
    x[11] = "REFACTOR"

    new_delivery_string = ""
    for el in x:
        new_delivery_string += el
        new_delivery_string += "|"
    new_delivery_string = new_delivery_string[:-1]

    # Remove from schedule
    remove_times_from_schedule_by_reservation_id(res_id)

    # Delete existing delivery, and remove from schedule
    SQLS.db_update(
        "DELETE FROM reservations WHERE resId = '%s';" % res_id
    )

    # Package info, and have reservation created
    new_request = ["MOOT", "MOOT", new_delivery_string, request[3], request[4]]
    INSERTS.insert_new_delivery(new_request)
    return