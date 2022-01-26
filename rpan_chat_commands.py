import obspython as obs
import ctypes, sys, os, re, requests, time, asyncio, websockets, json, praw, sqlite3
from gtts import gTTS
from playsound import playsound
from threading import Thread


#gives the ability to make directory / remove files
if not ctypes.windll.shell32.IsUserAnAdmin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()


class manage_db():
    def generate_points_db():
        points_db = sqlite3.connect("rpan_chat_commands\\points.db")
        cursor = points_db.cursor()
        if not cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='POINTS_DB'").fetchone()[0]:
            points_db.execute("""CREATE TABLE POINTS_DB (
                                author TEXT,
                                comment_count INTEGER,
                                award_value INTEGER,
                                points INTEGER,
                                last_comment_time INTEGER);""")
            points_db.commit()
            points_db.close()

    def create_db_entry(redditor):
        points_db = sqlite3.connect("rpan_chat_commands\\points.db")
        cursor = points_db.cursor()
        value = cursor.execute("SELECT 1 author FROM POINTS_DB WHERE author = ?", tuple([redditor])).fetchone()
        if not value:
            cursor.execute("INSERT INTO POINTS_DB VALUES (?, 0, 0, 0, 0)", tuple([redditor]))
        points_db.commit()
        points_db.close()
            
    def increment_db_value(increment, value_name, redditor):
        points_db = sqlite3.connect("rpan_chat_commands\\points.db")
        cursor = points_db.cursor()
        db_int = cursor.execute("SELECT %s FROM POINTS_DB WHERE author = ?" % value_name, tuple([redditor])).fetchone()[0]
        db_int += increment                     
        cursor.execute("UPDATE POINTS_DB SET %s = ? WHERE author = ?" % value_name, tuple([db_int, redditor]))
        points_db.commit()
        points_db.close()

    def set_db_value(value, value_name, redditor):
        points_db = sqlite3.connect("rpan_chat_commands\\points.db")
        cursor = points_db.cursor()                    
        cursor.execute("UPDATE POINTS_DB SET %s = ? WHERE author = ?" % value_name, tuple([value, redditor]))
        points_db.commit()
        points_db.close()
        
    def get_db_value(value_name, redditor):
        points_db = sqlite3.connect("rpan_chat_commands\\points.db")
        cursor = points_db.cursor()
        value = cursor.execute("SELECT %s FROM POINTS_DB WHERE author = ?" % value_name, tuple([redditor])).fetchone()[0]
        points_db.commit()
        points_db.close()
        return value

    def update_db(redditor, award_value, comment_time):
        if award_value:
            manage_db.increment_db_value(award_value, "award_value", redditor)
            manage_db.increment_db_value(round((award_value / 10), 0), "points", redditor)
        else:
            manage_db.increment_db_value(1 , "comment_count", redditor)

        last_comment_time = manage_db.get_db_value("last_comment_time", redditor)
        
        if last_comment_time < websocket_stuff.STREAM_START_TIME:
            if last_comment_time == 0: #if this is a users first time commenting, give them 2 points
                manage_db.increment_db_value(2, "points", redditor)
                manage_db.set_db_value(comment_time , "last_comment_time", redditor)
            else:  #if this user is returning from a prev stream, give them 50 points
                manage_db.increment_db_value(50, "points", redditor)
                manage_db.set_db_value(comment_time , "last_comment_time", redditor)
            
        elif comment_time - last_comment_time > 120: #check if two minutes have passed since last comment
            if comment_time - last_comment_time < 600: #check if over 10 minutes have passed since last comment
                points_gained = round((comment_time - last_comment_time) / 60) * 2 #give comment 2 points for every minute passed since last comment, up to 20 points / 10 mins
            else:
                points_gained = 20

            manage_db.increment_db_value(points_gained, "points", redditor)
            manage_db.set_db_value(comment_time , "last_comment_time", redditor)
            
        #print(redditor + " has " + str(manage_db.get_db_value("points", redditor)) + " points")


#directory initilization
if not os.path.isdir("rpan_chat_commands"):
    os.makedirs("rpan_chat_commands\\temp_files")
if not os.path.isfile("rpan_chat_commands\\points.db"):
    manage_db.generate_points_db()
if not os.path.isfile("rpan_chat_commands\\mod_list.json"):   
    with open("rpan_chat_commands\\mod_list.json", "w") as mod_list_json:
        json.dump([], mod_list_json)
    

class websocket_stuff():
    REDDIT_BASE_URL = "https://strapi.reddit.com/videos/"
    STREAM_ID = None
    STREAM_URL = None
    WEBSOCKET_URI = None

    STREAM_START_TIME = None

    async def get_comments():
        websocket_stuff.url_to_websocket(websocket_stuff.STREAM_URL)

        async with websockets.connect(websocket_stuff.WEBSOCKET_URI) as websocket:
            while True:
                try:
                    comment_info = json.loads(await websocket.recv())
                except: #catches both communication errors and asyncio.CancelledError
                    break

                if comment_info["type"] == "new_comment":
                    author = comment_info["payload"]["author"]
                    comment_id = comment_info["payload"]["_id36"]
                    award = comment_info["payload"]["associated_award"]
                    comment_time = comment_info["payload"]["created_utc"]
                    
                    if process_comments.ENABLE_POINTS: #and author != process_comments.REDDIT_USERNAME:
                        manage_db.create_db_entry(author)
                    
                    if not award:
                        award_value = None
                        comment = comment_info["payload"]["body"]
                        process_comments.sort_commands(author, comment, comment_id)
                    else:
                        award_value = comment_info["payload"]["associated_award"]["coin_price"]
                        if process_comments.ENABLE_ANNOUNCE_AWARD:
                            process_comments.announce_award(author, award["name"], comment_id)

                    if process_comments.ENABLE_POINTS: #and author != process_comments.REDDIT_USERNAME:   
                        manage_db.update_db(author, award_value, comment_time)
    
                        
        process_comments.AUTO_MSG_COUNTER = 0
        if process_comments.ENABLE_COMMENT_DISPLAY:
            process_comments.update_source(process_comments.COMMENT_DISPLAY_NAME, "text", "your tts messages will appear here")
            
        obs_threading.task = None
        obs_threading.comment_stream_thread = None
        print("successfully stopped processing comments")

    def url_to_websocket(URL):
        websocket_stuff.STREAM_ID = URL[URL.rfind("/")+1:]
        if "?" in websocket_stuff.STREAM_ID: #checks for "?related=home" in URL
            websocket_stuff.STREAM_ID = websocket_stuff.STREAM_ID[0:6]

        while True:
            r = requests.get(websocket_stuff.REDDIT_BASE_URL + websocket_stuff.STREAM_ID).json()
            if r["status"] == "success":
                print("connected to comment stream successfully")
                break
            else:
                print("connecting to comment stream...")
            time.sleep(1)

        websocket_stuff.WEBSOCKET_URI = r["data"]["post"]["liveCommentsWebsocket"]
        websocket_stuff.STREAM_START_TIME = round(r["data"]["stream"]["publish_at"] / 1000, 0)

class process_comments():
    CUSTOM_COMMAND = None
    CUSTOM_TEXT = None
    REDDIT_USERNAME = None
    REDDIT_PASSWORD = None
    REDDIT_CLIENT_ID = None
    REDDIT_SECRET_ID = None
    
    ENABLE_TTS = None
    ENABLE_TTS_COMMAND = None
    ENABLE_TTS_COMMAND_COST = None
    ENABLE_COMMENT_DISPLAY = None
    COMMENT_DISPLAY_NAME = None
    
    ENABLE_CUSTOM_MESSAGES = None
    CUSTOM_MSG_OPT = None
    AUTO_MSG_COUNTER = 0
    AUTO_MSG_VALUE = None

    ENABLE_POINTS = None
    ENABLE_POINTS_COMMAND = None

    ENABLE_ANNOUNCE_AWARD = None
    ENABLE_MODS = None

    def sort_commands(author, comment, comment_id):

        #custom message
        if process_comments.ENABLE_CUSTOM_MESSAGES and process_comments.CUSTOM_TEXT: #check for custom commands
            if process_comments.CUSTOM_MSG_OPT == "auto custom messages": #checks which option is selected
                if author != process_comments.REDDIT_USERNAME:
                    process_comments.AUTO_MSG_COUNTER += 1
                    if process_comments.AUTO_MSG_COUNTER >= process_comments.AUTO_MSG_VALUE:
                        process_comments.AUTO_MSG_COUNTER = 0
                        process_comments.comment_response(process_comments.CUSTOM_TEXT)
            elif comment == process_comments.CUSTOM_COMMAND:
                process_comments.comment_response(process_comments.CUSTOM_TEXT)

        #tts commands            
        if process_comments.ENABLE_TTS and author != process_comments.REDDIT_USERNAME: #and not comment.find("!") == 0:  #check if tts is enabled and dont tts comments from the account responding to everyone 
            if process_comments.ENABLE_TTS_COMMAND: #check if tts command enabled
                if comment.find("!tts ") == 0: #checks if tts command conditions are met
                    if process_comments.ENABLE_POINTS and process_comments.ENABLE_TTS_COMMAND_COST: #checks it tts command cost enabled
                        if manage_db.get_db_value("points", author) - 20 >= 0: #checks if commenter has enough points to use command
                            manage_db.increment_db_value(-20, "points", author)
                            comment = comment[5:len(comment)]
                            tts = True
                        else:
                            tts = False
                    else: #if points disabled, tts the text after tts command
                        comment = comment[5:len(comment)]
                        tts = True
                else:
                    tts = False
            else:
                if not comment.find("!") == 0: #dont tts comments that contain commands
                    tts = True
                else:
                    tts = False
            if tts:
                if process_comments.ENABLE_COMMENT_DISPLAY: 
                    process_comments.update_source(process_comments.COMMENT_DISPLAY_NAME, "text", author + ": " + comment)
                tts_thread = Thread(target=process_comments.tts(comment, comment_id))
                tts_thread.start()

        #points commands
        if (process_comments.ENABLE_POINTS and process_comments.ENABLE_POINTS_COMMAND) and comment == "!points": #check to see if point system is enabled and if the author exists in the points db yet
            process_comments.comment_response("u/" + author + ", you have: " + str(manage_db.get_db_value("points", author)) + " points")

        #mod commands
        if process_comments.ENABLE_MODS:
            #load mod list stored in json file
            with open("rpan_chat_commands\\mod_list.json", "r") as mod_list_json:
                mod_list = json.load(mod_list_json)
                
            if comment.find('!mod ') == 0 and author == process_comments.REDDIT_USERNAME: #create a new mod
                new_mod = comment[5:len(comment)]
                
                if new_mod not in mod_list:
                    reddit = process_comments.reddit_login()
                    if reddit:
                        try:
                            reddit.redditor(new_mod).id
                        except NotFound:
                            print("Reddit user not found")
                            pass
                        else:
                            with open("rpan_chat_commands\\mod_list.json", "w") as mod_list_json:
                                mod_list.append(new_mod)
                                json.dump(mod_list, mod_list_json)    
                            print(new_mod + " is now a mod!")

            if comment.find('!ban ') == 0 and author in mod_list: #if a mod uses this command, bans user from stream
                reddit = process_comments.reddit_login()
                if reddit:    
                    banned_viewer = comment[5:len(comment)]
                    try:
                        reddit.redditor(banned_viewer).id
                    except NotFound:
                        pass
                    else:
                        print(banned_viewer + " has been banned!")
                        reddit.redditor(banned_viewer).block()
            
    def reddit_login():
        reddit = praw.Reddit(client_id=process_comments.REDDIT_CLIENT_ID, 
                             client_secret=process_comments.REDDIT_SECRET_ID, 
                             user_agent="rpan chat commands by tech it apart",
                             username=process_comments.REDDIT_USERNAME,
                             password=process_comments.REDDIT_PASSWORD,
                             check_for_async=False)

        try:
            reddit.user.me()
        except:
            print("reddit login failed, please make sure your login information is correct")
            return None
        else:
            return reddit

    def comment_response(message):
        reddit = process_comments.reddit_login()
        if reddit:
            submission = reddit.submission(id=websocket_stuff.STREAM_ID)
            submission.reply(message)

    def announce_award(author, award_name, comment_id):
        announcement = author + " gave " + award_name
        tts_thread = Thread(target=process_comments.tts(announcement, comment_id))
        tts_thread.start() 

    def tts(tts_msg, filename):
        try:
            tts = gTTS(tts_msg, lang="en", slow=False)
            tts.save("rpan_chat_commands\\temp_files" + "\\" + filename.lower() + "_temp.mp3")
            playsound("rpan_chat_commands\\temp_files" + "\\" + filename.lower() + "_temp.mp3", False)
            os.remove("rpan_chat_commands\\temp_files" + "\\" + filename.lower() + "_temp.mp3")
        except:
            if os.path.isfile("rpan_chat_commands\\temp_files" + "\\" + filename.lower() + "_temp.mp3"):
                os.remove("rpan_chat_commands\\temp_files" + "\\" + filename.lower() + "_temp.mp3")
            print('tts failed')

    def update_source(source_name, setting_name, data):
        source = obs.obs_get_source_by_name(source_name)
        settings = obs.obs_data_create()
        if setting_name == "text" or setting_name == "file":
            obs.obs_data_set_string(settings, setting_name, data)
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)   


class update_ui():
    def change_menu(props, prop, settings):
        menu = obs.obs_data_get_string(settings, "current_menu")
        
        tts_enabled = obs.obs_data_get_bool(settings, "enable_tts")
        comment_display_visible = obs.obs_data_get_bool(settings, "enable_comment_display")

        custom_message_enabled = obs.obs_data_get_bool(settings, "enable_custom_messages")
        custom_message_option = obs.obs_data_get_string(settings, "custom_msg_opt")

        points_enabled = obs.obs_data_get_bool(settings, "enable_points")
        points_command_enabled = obs.obs_data_get_bool(settings, "enable_points_command")
        
        mods_enabled = obs.obs_data_get_bool(settings, "enable_mods")

        if menu == "main menu":
            hide_list = ["enable_custom_messages", "enable_tts", "enable_tts_command",
                         "enable_tts_command_cost", "enable_comment_display", "comment_display",
                         "enable_announce_award", "custom_msg_opt", "enable_points",
                         "enable_mods", "enable_points_command"]
            for prop_name in hide_list:
                prop = obs.obs_properties_get(props, prop_name)
                obs.obs_property_set_visible(prop, False)
            
            show_list = ["url_text", "comment_button"]
            if custom_message_enabled or (points_enabled and points_command_enabled) or mods_enabled:
                show_list += ["reddit_username", "reddit_password", "reddit_client_id", "reddit_secret_id"]

                if custom_message_enabled:
                    show_list += ["custom_text"]
                    if custom_message_option == "auto custom messages":
                        show_list += ["custom_msg_freq"]
                    else:
                        show_list += ["custom_command"]
            for prop_name in show_list:
                prop = obs.obs_properties_get(props, prop_name)
                obs.obs_property_set_visible(prop, True)
                
        else: #menu == "options"
            hide_list = ["reddit_username", "reddit_password", "reddit_client_id",
                         "reddit_secret_id", "custom_text", "custom_command",
                         "custom_msg_freq", "url_text", "comment_button"]
            for prop_name in hide_list:
                prop = obs.obs_properties_get(props, prop_name)
                obs.obs_property_set_visible(prop, False)
                
            show_list = ["enable_custom_messages", "enable_tts", "enable_announce_award",
                         "enable_points", "enable_mods"]
            if custom_message_enabled:
                show_list += ["custom_msg_opt"]
            if tts_enabled:
                show_list += ["enable_tts_command", "enable_comment_display"]
                if points_enabled:
                    show_list += ["enable_tts_command_cost"]
                if comment_display_visible:
                    show_list += ["comment_display"]
            if points_enabled:
                show_list += ["enable_points_command"]
                
            for prop_name in show_list:
                prop = obs.obs_properties_get(props, prop_name)
                obs.obs_property_set_visible(prop, True)
                
        return True 

    def change_button(props, prop):
        prop = obs.obs_properties_get(props, "comment_button")
        desc = obs.obs_property_description(prop)

        if process_comments.ENABLE_CUSTOM_MESSAGES or (process_comments.ENABLE_POINTS and process_comments.ENABLE_POINTS_COMMAND) or process_comments.ENABLE_MODS:
            if process_comments.reddit_login():
                process = True
            else:
                process = False
        else:
            process = True
        
        if desc == "start" and process:
            if websocket_stuff.STREAM_URL[0:30] == "https://www.reddit.com/rpan/r/":
                if not obs_threading.task:
                    obs_threading.comments_thread()
                    obs.obs_property_set_description(prop, "stop")
                else:
                    print("please wait for processing to finish first")
            else:
                print("improper URL entered")
                
        else: #if stop
            if obs_threading.task:
                obs_threading.task.cancel()
            obs.obs_property_set_description(prop, "start")

        return True
    
    def add_points_options(props, prop, settings):
        opt_list = ["enable_points_command"]
        if obs.obs_data_get_bool(settings, "enable_tts_command"):
            opt_list += ["enable_tts_command_cost"]
        for prop_name in opt_list:
            prop = obs.obs_properties_get(props, prop_name)
            obs.obs_property_set_visible(prop, obs.obs_data_get_bool(settings, "enable_points"))
        return True

    def add_custom_msg_opt(props, prop, settings):
        prop = obs.obs_properties_get(props, "custom_msg_opt")
        obs.obs_property_set_visible(prop, obs.obs_data_get_bool(settings, "enable_custom_messages"))
        return True

    def add_tts_options(props, prop, settings):
        opt_list = ["enable_tts_command", "enable_comment_display"]
        if obs.obs_data_get_bool(settings, "enable_tts_command") and obs.obs_data_get_bool(settings, "enable_points"):
            opt_list += ["enable_tts_command_cost"]
        if obs.obs_data_get_bool(settings, "enable_comment_display"):
            opt_list += ["comment_display"]
        for prop_name in opt_list:
            prop = obs.obs_properties_get(props, prop_name)
            obs.obs_property_set_visible(prop, obs.obs_data_get_bool(settings, "enable_tts"))
        return True

    def add_tts_command_opt(props, prop, settings):
        if obs.obs_data_get_bool(settings, "enable_points"):
            prop = obs.obs_properties_get(props, "enable_tts_command_cost")
            obs.obs_property_set_visible(prop, obs.obs_data_get_bool(settings, "enable_tts_command"))
        return True
    
    def add_comment_display(props, prop, settings):
        prop = obs.obs_properties_get(props, "comment_display")
        obs.obs_property_set_visible(prop, obs.obs_data_get_bool(settings, "enable_comment_display"))
        return True


class obs_threading:       
    comment_stream_thread = None
    task = None

    def run_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        obs_threading.task = loop.create_task(websocket_stuff.get_comments())
        loop.run_until_complete(obs_threading.task)
        loop.close()
        
    def comments_thread(): 
        if not obs_threading.comment_stream_thread and not obs_threading.task:
            obs_threading.comment_stream_thread = Thread(target=obs_threading.run_loop)
            obs_threading.comment_stream_thread.start()


def script_load(settings):
    obs.obs_data_set_string(settings, "current_menu", "main menu")
    obs.obs_data_set_string(settings, "url_text", None)

    reset_options = ["enable_custom_messages", "enable_tts", "enable_tts_command",
                     "enable_comment_display", "enable_points", "enable_points_command",
                     "enable_tts_command_cost", "enable_mods", "enable_announce_award"]
    for option in reset_options:
        obs.obs_data_set_bool(settings, option, False)

def script_description():
    description = """<html>
    <center><h3>r/pan Chat Commands v2.0</h3></center>
    <br>If you have any issues please let me know on <a href="https://github.com/techitapart/rpan_chat_commands">Github</a></center>
    </html>"""

    return description 

def script_update(settings):
    websocket_stuff.STREAM_URL = obs.obs_data_get_string(settings, "url_text")

    process_comments.ENABLE_CUSTOM_MESSAGES = obs.obs_data_get_bool(settings, "enable_custom_messages")
    process_comments.CUSTOM_TEXT = obs.obs_data_get_string(settings, "custom_text")
    process_comments.CUSTOM_MSG_OPT = obs.obs_data_get_string(settings, "custom_msg_opt")
    process_comments.AUTO_MSG_VALUE = obs.obs_data_get_int(settings, "custom_msg_freq")
    process_comments.CUSTOM_COMMAND = obs.obs_data_get_string(settings, "custom_command")
    
    process_comments.REDDIT_USERNAME = obs.obs_data_get_string(settings, "reddit_username")
    process_comments.REDDIT_PASSWORD = obs.obs_data_get_string(settings, "reddit_password")
    process_comments.REDDIT_CLIENT_ID = obs.obs_data_get_string(settings, "reddit_client_id")
    process_comments.REDDIT_SECRET_ID = obs.obs_data_get_string(settings, "reddit_secret_id")

    process_comments.ENABLE_TTS = obs.obs_data_get_bool(settings, "enable_tts")
    process_comments.ENABLE_TTS_COMMAND = obs.obs_data_get_bool(settings, "enable_tts_command")
    process_comments.ENABLE_TTS_COMMAND_COST = obs.obs_data_get_bool(settings, "enable_tts_command_cost")
    process_comments.ENABLE_COMMENT_DISPLAY = obs.obs_data_get_bool(settings, "enable_comment_display")
    process_comments.COMMENT_DISPLAY_NAME = obs.obs_data_get_string(settings, "comment_display")
    
    process_comments.ENABLE_POINTS = obs.obs_data_get_bool(settings, "enable_points")
    process_comments.ENABLE_POINTS_COMMAND = obs.obs_data_get_bool(settings, "enable_points_command")
    
    process_comments.ENABLE_ANNOUNCE_AWARD = obs.obs_data_get_bool(settings, "enable_announce_award")
    process_comments.ENABLE_MODS = obs.obs_data_get_bool(settings, "enable_mods")
    
def script_properties():
    props = obs.obs_properties_create()
    
    #create all menu options
    menus = obs.obs_properties_add_list(props, "current_menu", "", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    menu_list = ["main menu", "options"]
    for menu in menu_list:
        obs.obs_property_list_add_string(menus, menu, menu)
    obs.obs_property_set_modified_callback(menus, update_ui.change_menu)
    
    #create main menu properties
    obs.obs_properties_add_text(props, "reddit_username", "Reddit Username", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "reddit_password", "Reddit Password", obs.OBS_TEXT_PASSWORD)
    obs.obs_properties_add_text(props, "reddit_client_id", "Reddit Client ID", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "reddit_secret_id", "Reddit Secret ID", obs.OBS_TEXT_DEFAULT)
    
    obs.obs_properties_add_text(props, "custom_text", "custom messsage", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "custom_command", "custom command", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int_slider(props, "custom_msg_freq", "message frequency", 5, 30, 1)
    
    obs.obs_properties_add_text(props, "url_text", "stream URL", obs.OBS_TEXT_DEFAULT)
        
    button = obs.obs_properties_add_button(props, "comment_button", "start", update_ui.change_button)

    #create option menu properties
    enable_points = obs.obs_properties_add_bool(props, "enable_points", "enable points")
    obs.obs_property_set_modified_callback(enable_points, update_ui.add_points_options)

    obs.obs_properties_add_bool(props, "enable_points_command", "enable !points command")

    enable_custom_messages = obs.obs_properties_add_bool(props, "enable_custom_messages", "enable custom messages")
    obs.obs_property_set_modified_callback(enable_custom_messages, update_ui.add_custom_msg_opt)
    
    custom_msg_opt = obs.obs_properties_add_list(props, "custom_msg_opt", "", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    custom_msg_opt_list = ["auto custom messages", "use custom command"]
    for option in custom_msg_opt_list:
        obs.obs_property_list_add_string(custom_msg_opt, option, option)
    
    enable_tts = obs.obs_properties_add_bool(props, "enable_tts", "enable tts")
    obs.obs_property_set_modified_callback(enable_tts, update_ui.add_tts_options)
    
    enable_tts_command = obs.obs_properties_add_bool(props, "enable_tts_command", "enable !tts command")
    obs.obs_property_set_modified_callback(enable_tts_command, update_ui.add_tts_command_opt)
    obs.obs_properties_add_bool(props, "enable_tts_command_cost", "make !tts command cost 20 points")

    enable_comment_display = obs.obs_properties_add_bool(props, "enable_comment_display", "enable comment display")
    obs.obs_property_set_modified_callback(enable_comment_display, update_ui.add_comment_display)

    comment_display = obs.obs_properties_add_list(props, "comment_display", "", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "text_gdiplus":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(comment_display, name, name)
        obs.source_list_release(sources)
    
    obs.obs_properties_add_bool(props, "enable_announce_award", "enable award announcing")
    obs.obs_properties_add_bool(props, "enable_mods", "enable mods")
    

    #set descriptions
    obs.obs_property_set_long_description(obs.obs_properties_get(props, "enable_custom_messages"), "enable / disable custom messages")
    obs.obs_property_set_long_description(obs.obs_properties_get(props, "custom_text"), "your custom message that you will message automatically or when someone uses your custom command")
    obs.obs_property_set_long_description(obs.obs_properties_get(props, "custom_msg_freq"), "set how many comments will need to be sent before your automatic custom message is sent again")
    obs.obs_property_set_long_description(obs.obs_properties_get(props, "reddit_username"), "the username of the account you want to use to respond with your custom message")
    obs.obs_property_set_long_description(obs.obs_properties_get(props, "reddit_password"), "the password of the account you want to use to respond with your custom message")
    obs.obs_property_set_long_description(obs.obs_properties_get(props, "reddit_client_id"), "the client ID of the account you want to use to respond with your custom message")
    obs.obs_property_set_long_description(obs.obs_properties_get(props, "reddit_secret_id"), "the secret ID of the account you want to use to respond with your custom message")    
    obs.obs_property_set_long_description(obs.obs_properties_get(props, "enable_tts_command"), "only tts comments with !tts before them (disabling will tts all comments)")
    obs.obs_property_set_long_description(obs.obs_properties_get(props, "enable_tts_command_cost"), "enabling this will make !tts cost 20 points to use")
    obs.obs_property_set_long_description(obs.obs_properties_get(props, "enable_tts"), "enable / disable tts")
    obs.obs_property_set_long_description(obs.obs_properties_get(props, "enable_announce_award"), "enabling this will tts all awards given, as well as who gave the award")
    obs.obs_property_set_long_description(obs.obs_properties_get(props, "enable_points"), "viewers can gain points by commenting and awarding your stream")
    obs.obs_property_set_long_description(obs.obs_properties_get(props, "enable_points_command"), "viewers can use !points to check their points balance")
    obs.obs_property_set_long_description(obs.obs_properties_get(props, "enable_mods"), "streamer can use !mod to appoint mods who can then use !ban to ban people")

    #hide most options for initial UI loading
    hide_list = ["reddit_username", "reddit_password", "reddit_client_id",
                 "reddit_secret_id", "custom_text", "custom_command",
                 "comment_display", "enable_custom_messages", "enable_tts",
                 "enable_tts_command", "enable_comment_display", "enable_announce_award",
                 "custom_msg_opt", "custom_msg_freq", "enable_points",
                 "enable_points_command", "enable_tts_command_cost", "enable_mods"]
    for prop_name in hide_list:
        prop = obs.obs_properties_get(props, prop_name)
        obs.obs_property_set_visible(prop, False)
        
    return props

def script_unload():
    if obs_threading.task: #if you close RPAN Studio and the comment processing thread is still alive, this will kill it after a short delay
        obs_threading.task.cancel()
