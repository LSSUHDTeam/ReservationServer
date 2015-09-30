__author__ = 'jbosley2'

import sql_settings as SQLS


def select_future_deliveries():

    info = []
    info_get = SQLS.db_fetch(
        "select * from reservations where DATE(resStart) = CURDATE() AND deliveredBy = 'NA' ORDER BY resStart;")

    try:
        for el in info_get:
            for ell in el:
                info.append(str(ell))
                info.append("|")
            info.append("%")
        info.pop(-1)

        if info[-1] == "|":
            info.pop(-1)
    except :
        # If there are no deliveries for the day, send this back :
        info.append("NA")

    SQLS.output_update_to_screen("Received a request for today's deliveries . . . . . ")

    return info


def select_past_deliveries():

    info = []
    info_get = SQLS.db_fetch("SELECT * FROM reservations WHERE timeDelivered != '0000-00-00 00:00:00' AND timePickedup \
    = '0000-00-00 00:00:00' AND DATE(resEnd) <= CURDATE() ORDER BY resEnd;")

    # "SELECT * FROM reservations WHERE timeDelivered != '0000-00-00 00:00:00' AND timePickedup \
    #  = '0000-00-00 00:00:00' AND resEnd <= NOW() ORDER BY resEnd;"

    try:
        for el in info_get:
            for ell in el:
                info.append(str(ell))
                info.append("|")
            info.append("%")
        info.pop(-1)
    except:
        info.append("NA")

    SQLS.output_update_to_screen("Request for today's pickups . . . . . . . . . . . . . ")

    return info


def select_links():

    info = []
    info_get = SQLS.db_fetch("SELECT * FROM repeated ;")

    try:
        for el in info_get:
            for ell in el:
                info.append(str(ell))
                info.append("|")
            info.append("%")
        info.pop(-1)
    except:
        info.append("NA")

    SQLS.output_update_to_screen("Received a request for linked items . . . . . . . ")

    return info;


def select_inventory():

    info = []
    info_get = SQLS.db_fetch("SELECT * from inventory ORDER BY title;")

    try:
        for el in info_get:
            for ell in el:
                info.append(str(ell).replace('\n', ' '))
                info.append("|")
            info.append("%")
        info.pop(-1)
    except :
        info.append("NA")

    SQLS.output_update_to_screen("Received a request for inventory items . . . . . . . ")

    return info


def select_schedule():

    info = []
    info_get = SQLS.db_fetch("SELECT inventoryItemID, datesUnavailable from inventorySchedule;")

    try:
        for el in info_get:
            for ell in el:
                info.append(str(ell))
                info.append(", ")
            info.append("%")
        info.pop(-1)
    except:
        info.append("NA")

    SQLS.output_update_to_screen("Received a request for schedule . . . . . . . ")
    return info

def select_rooms():

    info = []
    info_get = SQLS.db_fetch("SELECT * from rooms ORDER BY roomName;")

    try:
        for el in info_get:
            for ell in el:
                info.append(str(ell))
                info.append("|")
            info.append("%")
        info.pop(-1)
    except :
        info.append("NA")

    SQLS.output_update_to_screen("Received a request for room names . . . . . . . ")
    return info


#      ----  SPECIFIC SELECTS ----


def select_reservation_by_id(data):

    info = []
    for el in SQLS.db_fetch("SELECT * FROM reservations WHERE resId = '%s';" % str(data))[0]:
        info.append(str(el))
        info.append("|")
    info.pop(-1)

    SQLS.output_update_to_screen("Received a request reservation by ID . . . . . . . ")
    return info


def select_reservations_by_date(date):

    info = []
    reservations = SQLS.db_fetch(
        "SELECT * FROM reservations WHERE DATE(resStart) = DATE('%s');" % date
    )

    try:
        for el in reservations:
            for ell in el:
                info.append(str(ell))
                info.append("|")
            info.append("%")
        info.pop(-1)

        if info[-1] == "|":
            info.pop(-1)
    except :
        # If there are no deliveries for the day, send this back :
        info.append("NA")

    return info