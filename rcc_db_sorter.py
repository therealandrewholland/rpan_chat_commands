import obspython as obs
import os, sqlite3

class sorting():
    CURRENT_OPTION = None
        
    def sort(props, prop):
        points_db = sqlite3.connect("rpan_chat_commands\\points.db")
        cursor = points_db.cursor()
        option = sorting.CURRENT_OPTION

        if option == "most active commenters":
            sql_q = "SELECT * FROM POINTS_DB ORDER BY comment_count DESC"
        elif option == "highest donaters":
            sql_q = "SELECT * FROM POINTS_DB ORDER BY award_value DESC"
        elif option == "most points":
            sql_q = "SELECT * FROM POINTS_DB ORDER BY points DESC"
            
        results = cursor.execute(sql_q).fetchall()

        print("redditor, total comments, total award value (in reddit coins), points")
        for result in results[0:5]:
            print(result[0:4])

        points_db.close()

def script_description():
    description = """<html>
    <center><h3>r/pan Chat Commands Database Sorter</h3></center>
    <br>If you have any issues please let me know on <a href="https://github.com/techitapart/rpan_chat_commands">Github</a></center>
    </html>"""
    return description

def script_update(settings):
    sorting.CURRENT_OPTION = obs.obs_data_get_string(settings, "sorting_option")
    
def script_properties():
    props = obs.obs_properties_create()

    sorting_options = obs.obs_properties_add_list(props, "sorting_option", "sort by", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    sorting_list = ["most active commenters", "highest donaters", "most points"]
    for option in sorting_list:
        obs.obs_property_list_add_string(sorting_options, option, option)
    #obs.obs_property_set_modified_callback(sorting_options, update_ui.change_menu)

    button = obs.obs_properties_add_button(props, "run", "start", sorting.sort)

    return props
