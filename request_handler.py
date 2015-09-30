__author__ = 'jbosley2'
__author__ = 'Josh Allen Bosley'

import sql_settings as SQLS
import sql_selects as SELECT
import sql_inserts as INSERT
import sql_updates as UPDATE
import sql_admin as ADMIN

import urllib2

def internet_on():
    try:
        response=urllib2.urlopen('http://10.1.0.83',timeout=1)
        return True
    except urllib2.URLError as err: pass
    return False

def request_handler(request):

    info = []

    if internet_on():

        # ===================[ CONNECTION INQUIRIES] =============
        if request[0] == 'ci':

            # Ask if api connected to 10. network
            if request[1] == 'inet':
                print "\n\tRequest to test server connection\n"
                if internet_on():
                    info.append("y")
                else:
                    info.append("n")

            # Ask if api running at all
            if request[1] == 'ira':
                print "\n\tRequest to rest api connection\n"
                info.append("y")

        # ===================[ SELECT QUERIES ]===================
        if request[0] == 's':

            # Select All future deliveries
            if request[1] == 'fd':
                info = SELECT.select_future_deliveries()

            if request[1] == 'pd':
                info = SELECT.select_past_deliveries()

            if request[1] == 'lnks':
                info = SELECT.select_links()

            if request[1] == 'inv':
                info = SELECT.select_inventory()

            if request[1] == 'sch':
                info = SELECT.select_schedule()

            if request[1] == 'rms':
                info = SELECT.select_rooms()

            if request[1] == 'rbi':
                info = SELECT.select_reservation_by_id(request[2])


        # ===================[ UPDATE QUERIES ]===================
        if request[0] == 'u':

            if request[1] == "rls":
                SQLS.output_update_to_screen("URLS")

            if request[1] == "spe":
                info = UPDATE.update_reservation_for_pickup(request)

            if request[1] == "sde":
                info = UPDATE.update_delivery_set_delivered(request)

            if request[1] == "eds":
                info = UPDATE.update_delivery_series(request)

        # ===================[ INSERT QUERIES ]===================
        if request[0] == 'i':

            if request[1] == "rn":
                info = INSERT.insert_new_delivery_location(request[2])

            if request[1] == "newr":
                info = INSERT.insert_new_delivery(request)

            # Update existing record
            SQLS.output_update_to_screen("Insert Requested")


        # ====================[ ADMIN QUERIES ]====================
        if request[0] == 'a':

            if request[1] == 'lgn':

                info = ADMIN.admin_check_login(request)

            if request[1] == 'udbi':

                info = ADMIN.admin_edit_device_by_id(request[2])

            if request[1] == 'add':

                info = ADMIN.admin_add_device(request[2])

            if request[1] == 'rem':

                info = ADMIN.admin_remove_device(request[2])

            if request[1] == 'frem':

                info = ADMIN.admin_do_remove_device(request[2])

            if request[1] == 'chng':

                info = ADMIN.change_user_password(request)

            if request[1] == "fdel":

                info = ADMIN.proxy_select_future_reservations(request[2])

        # Used to show the end of transfer

        reply = ''.join(info).replace('\n', ' ')
        reply += '\n'
        return reply

    else:
        print "NOT ABLE TO CONTACT SQL"
        return "NC\n"









