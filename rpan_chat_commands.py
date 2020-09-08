import obspython as obs
import ctypes, sys, os, re, requests, time, asyncio, websockets, json, praw
from gtts import gTTS
from playsound import playsound
from threading import Thread
   
#gives the ability to make directory / remove files
if not ctypes.windll.shell32.IsUserAnAdmin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

#directory initilization
if not os.path.isdir("stream_data"):
    os.mkdir("stream_data")
if not os.path.isdir("temp_files"):
    os.mkdir("temp_files")

class websocket_stuff():
    REDDIT_BASE_URL = "https://strapi.reddit.com/videos/"
    STREAM_ID = None
    STREAM_URL = None
    WEBSOCKET_URI = None
    LIVESTREAM_DICT = None
    CUSTOM_TEXT = None
    REDDIT_USERNAME = None
    REDDIT_PASSWORD = None
    ENABLE_TTS_COMMAND = None
    ENABLE_HELP_COMMAND = None
    ENABLE_COMMENT_DISPLAY = None
    COMMENT_DISPLAY_NAME = None

    async def read_comments():
        websocket_stuff.url_to_websocket(websocket_stuff.STREAM_URL)

        if os.path.exists("stream_data\\%s.json" % websocket_stuff.STREAM_TITLE):
            websocket_stuff.LIVESTREAM_DICT = json.load(open("stream_data\\%s.json" % websocket_stuff.STREAM_TITLE))
        else:
            websocket_stuff.LIVESTREAM_DICT = {"redditors":{}}
        
        async with websockets.connect(websocket_stuff.WEBSOCKET_URI) as websocket:
            while True:
                try:
                    comment_info = json.loads(await websocket.recv())
                except asyncio.CancelledError:
                    break

                if comment_info["type"] == "new_comment":
                    author = comment_info["payload"]["author"]
                    comment_id = comment_info["payload"]["_id36"]
                    award = comment_info["payload"]["associated_award"]

                    if author not in websocket_stuff.LIVESTREAM_DICT["redditors"]:
                        websocket_stuff.LIVESTREAM_DICT["redditors"][author] = {}
                        websocket_stuff.LIVESTREAM_DICT["redditors"][author]["comments"] = {}
                        websocket_stuff.LIVESTREAM_DICT["redditors"][author]["awards"] = {}
                        websocket_stuff.LIVESTREAM_DICT["redditors"][author]["points"] = 0
                    if not award:
                        comment = comment_info["payload"]["body"]
                        websocket_stuff.add_to_dict(author, comment, comment_id)
                    else:
                        award_name = comment_info["payload"]["associated_award"]["name"]
                        websocket_stuff.add_to_dict(author, award_name, comment_id, award=True)
        obs_threading.task = None
        obs_threading.comment_stream_thread = None
        if websocket_stuff.ENABLE_COMMENT_DISPLAY:
            websocket_stuff.update_source(websocket_stuff.COMMENT_DISPLAY_NAME, "text", "your tts messages will appear here")
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
            time.sleep(.75)

        websocket_stuff.STREAM_TITLE = re.sub("[^A-Za-z0-9]+", "", r["data"]["post"]["title"]).lower() #creates a string with the streams title, formatted to be an acceptable file name
        websocket_stuff.WEBSOCKET_URI = r["data"]["post"]["liveCommentsWebsocket"]

    def add_to_dict(author, comment, commentid, award=False):  
        if not award:                   
            if websocket_stuff.ENABLE_HELP_COMMAND and websocket_stuff.CUSTOM_TEXT and comment.find("!help") == 0 and len(comment) == 5:
                reddit = praw.Reddit(client_id="H6wDyGXL9wiBXw",
                                     client_secret="zhSZQfSCJS8Doc2XHlOOnIY_H10",
                                     user_agent="rpan chat commands by tech it apart",
                                     username=websocket_stuff.REDDIT_USERNAME,
                                     password=websocket_stuff.REDDIT_PASSWORD)
                try:
                    reddit.user.me()
                except:
                    print("reddit login failed, please make sure your login information is correct")
                else:
                    submission = reddit.submission(id=websocket_stuff.STREAM_ID)
                    submission.reply(websocket_stuff.CUSTOM_TEXT)
                
            if websocket_stuff.ENABLE_TTS_COMMAND:
                if comment.find("!tts ") == 0 and len(comment[5:len(comment)]) <= 100:
                    tts_thread = Thread(target=websocket_stuff.tts_comment(author, comment[5:len(comment)], commentid))
                    tts_thread.start()
                        
            elif not comment.find("!help") == 0 and comment != websocket_stuff.CUSTOM_TEXT:
                tts_thread = Thread(target=websocket_stuff.tts_comment(author, comment, commentid))
                tts_thread.start() 
                                                                      
            websocket_stuff.LIVESTREAM_DICT["redditors"][author]["comments"][commentid] = comment
        else:
            websocket_stuff.LIVESTREAM_DICT["redditors"][author]["awards"][commentid] = comment

        json.dump(websocket_stuff.LIVESTREAM_DICT, open("stream_data\\%s.json" % websocket_stuff.STREAM_TITLE, "w"))

    def tts_comment(author, comment, filename):
        try:
            tts = gTTS(comment, lang="en", slow=False)
            tts.save("temp_files" + "\\" + filename.lower() + "_temp.mp3")
            if websocket_stuff.ENABLE_COMMENT_DISPLAY:
                websocket_stuff.update_source(websocket_stuff.COMMENT_DISPLAY_NAME, "text", author + ": " + comment)
            playsound("temp_files" + "\\" + filename.lower() + "_temp.mp3", False)
            os.remove("temp_files" + "\\" + filename.lower() + "_temp.mp3")
        except:
            if os.path.isfile("temp_files" + "\\" + filename.lower() + "_temp.mp3"):
                os.remove("temp_files" + "\\" + filename.lower() + "_temp.mp3")
            print('tts failed')

    def update_source(source_name, setting_name, data):
        source = obs.obs_get_source_by_name(source_name)
        settings = obs.obs_data_create()
        if setting_name == "text" or setting_name == "file":
            obs.obs_data_set_string(settings, setting_name, data)
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)   

class obs_threading:       
    comment_stream_thread = None
    task = None

    def run_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        obs_threading.task = loop.create_task(websocket_stuff.read_comments())
        loop.run_until_complete(obs_threading.task)
        loop.close()
        
    def comments_thread(): 
        if not obs_threading.comment_stream_thread and not obs_threading.task:
            obs_threading.comment_stream_thread = Thread(target=obs_threading.run_loop)
            obs_threading.comment_stream_thread.start()

def script_load(settings):
    obs.obs_data_set_string(settings, "current_menu", "main menu")
    obs.obs_data_set_string(settings, "url_text", None)

    reset_options = ["enable_help_command", "enable_tts_command", "enable_comment_display"]
    for option in reset_options:
        obs.obs_data_set_bool(settings, option, False)

def script_description():
    return "r/pan Chat Commands"

def script_update(settings):
    websocket_stuff.COMMENT_DISPLAY_NAME = obs.obs_data_get_string(settings, "comment_display")
    websocket_stuff.STREAM_URL = obs.obs_data_get_string(settings, "url_text")
    websocket_stuff.CUSTOM_TEXT = obs.obs_data_get_string(settings, "custom_text")
    websocket_stuff.REDDIT_USERNAME = obs.obs_data_get_string(settings, "reddit_username")
    websocket_stuff.REDDIT_PASSWORD = obs.obs_data_get_string(settings, "reddit_password")
    websocket_stuff.ENABLE_TTS_COMMAND = obs.obs_data_get_bool(settings, "enable_tts_command")
    websocket_stuff.ENABLE_HELP_COMMAND = obs.obs_data_get_bool(settings, "enable_help_command")
    websocket_stuff.ENABLE_COMMENT_DISPLAY = obs.obs_data_get_bool(settings, "enable_comment_display")

def change_menu(props, prop, settings):
    menu = obs.obs_data_get_string(settings, "current_menu")
    
    comment_display_visible = obs.obs_data_get_bool(settings, "enable_comment_display")
    help_command_visible = obs.obs_data_get_bool(settings, "enable_help_command")

    if menu == "main menu":
        hide_list = ["enable_help_command", "enable_tts_command", "enable_comment_display"] 
        for prop_name in hide_list:
            prop = obs.obs_properties_get(props, prop_name)
            obs.obs_property_set_visible(prop, False)
        
        show_list = ["url_text", "comment_button"]
        if comment_display_visible:
            show_list = show_list + ["comment_display"]
        else:
            websocket_stuff.update_source(websocket_stuff.COMMENT_DISPLAY_NAME, "text", "your tts messages will appear here")
        if help_command_visible:
            show_list = show_list + ["reddit_username", "reddit_password", "custom_text"]
        for prop_name in show_list:
            prop = obs.obs_properties_get(props, prop_name)
            obs.obs_property_set_visible(prop, True)
    elif menu == "options":
        hide_list = ["reddit_username", "reddit_password", "custom_text", "url_text", "comment_button", "comment_display"]
        for prop_name in hide_list:
            prop = obs.obs_properties_get(props, prop_name)
            obs.obs_property_set_visible(prop, False)
            
        show_list = ["enable_help_command", "enable_tts_command", "enable_comment_display"]
        for prop_name in show_list:
            prop = obs.obs_properties_get(props, prop_name)
            obs.obs_property_set_visible(prop, True)
            
    return True 

def change_button(props, prop):
    prop = obs.obs_properties_get(props, "comment_button")
    desc = obs.obs_property_description(prop)

    if desc == "start":
        if websocket_stuff.STREAM_URL[0:30] == "https://www.reddit.com/rpan/r/":
            if obs_threading.task == None:
                obs_threading.comments_thread()
                obs.obs_property_set_description(prop, "stop")
            else:
                print("please wait for processing to finish first")
        else:
            print("improper URL entered")
    elif obs_threading.task:
        obs_threading.task.cancel()
        print("cancelling comment processing...")
        obs.obs_property_set_description(prop, "start")
        
    return True

def script_properties():
    props = obs.obs_properties_create()
    
    #create all menu options
    menus = obs.obs_properties_add_list(props, "current_menu", "current menu", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    menu_list = ["main menu", "options"]
    for menu in menu_list:
        obs.obs_property_list_add_string(menus, menu, menu)
    obs.obs_property_set_modified_callback(menus, change_menu)
    
    #create main menu properties
    obs.obs_properties_add_text(props, "reddit_username", "Reddit Username", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "reddit_password", "Reddit Password", obs.OBS_TEXT_PASSWORD)
    obs.obs_properties_add_text(props, "custom_text", "!help response", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "url_text", "Paste stream URL here", obs.OBS_TEXT_DEFAULT)
    comment_display = obs.obs_properties_add_list(props, "comment_display", "text source to display comments", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "text_gdiplus":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(comment_display, name, name)
        obs.source_list_release(sources)
    button = obs.obs_properties_add_button(props, "comment_button", "start", lambda *props: None)
    obs.obs_property_set_modified_callback(button, change_button)

    #create option menu properties
    obs.obs_properties_add_bool(props, "enable_help_command", "enable !help")
    obs.obs_properties_add_bool(props, "enable_tts_command", "enable !tts command")
    obs.obs_properties_add_bool(props, "enable_comment_display", "enable comment display")     

    #set descriptions
    obs.obs_property_set_long_description(obs.obs_properties_get(props, "enable_help_command"), "enable / disable !help command")
    obs.obs_property_set_long_description(obs.obs_properties_get(props, "reddit_username"), "the username of the account you want to use to respond to the !help command")
    obs.obs_property_set_long_description(obs.obs_properties_get(props, "reddit_password"), "the password of the account you want to use to respond to the !help command")
    obs.obs_property_set_long_description(obs.obs_properties_get(props, "custom_text"), "what you will comment in response when someone uses !help")
    obs.obs_property_set_long_description(obs.obs_properties_get(props, "enable_tts_command"), "only tts comments with !tts before them (disabling will tts all comments)")

    #hide most options for initial UI loading
    hide_list = ["reddit_username", "reddit_password", "custom_text", "comment_display", "enable_help_command", "enable_tts_command", "enable_comment_display"]
    for prop_name in hide_list:
        prop = obs.obs_properties_get(props, prop_name)
        obs.obs_property_set_visible(prop, False)

    return props
