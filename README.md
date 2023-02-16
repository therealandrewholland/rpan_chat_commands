# r/pan Chat Commands v2.0
r/pan (Reddit livestreaming) has been [shutdown](https://www.reddit.com/r/pan/comments/yl5zzd/update_on_the_future_of_live_video_broadcasting/). This project no longer works and will not be receiving any new updates.

## What is this?
This is an RPAN Studio python script that adds a ton of features r/pan streamers can use to interact with their chat

Using the script, you can:
- enable a points system that gives viewers points for commenting / awarding your stream
- text-to-speech comments (you can choose to tts all comments or only comments which contain `!tts` before them)
- automatically comment a custom message (either every X number of comments or whenever someone uses your custom command)
- set mods using `!mod`, who can "ban" people in chat using `!ban`
- text-to-speech awards given in the format `[redditor] gave [award name]`

## Quick Links
1. [ Installing Python ](#python)
2. [ Downloading the code ](#code)
3. [ Running "run_first.py" ](#run_first)
4. [ Setting up the script ](#setup)
5. [ Navigating the script ](#nav)
6. [ Processing comments ](#processing)
7. [ Getting your secret / client IDs ](#IDs)
8. [ Using custom messages ](#custom_messages)
9. [ Using the points system ](#points)
10. [ Using the database sorter ](#db_sorter)
11. [ Using mods system ](#mods)
12. [ Using the `!tts` command ](#tts_command)
13. [ Using the comment display ](#comment_display)

## Setup Guide
<a name="python"></a>
### Installing Python
Because OBS Studio does not support newer versions of Python, you'll have to install Python 3.6.1.

You can install it using this link -> https://www.python.org/downloads/release/python-361/

Run the exe file and follow the steps below:

<ol>
<li>Check off "Install launcher for all users (recommended)"
<p align="middle">
  <img src="/images/setting_up_python/01.PNG" width="48%" />
  <img src="/images/setting_up_python/02.PNG" width="48%" /> 
</p></li>

<li>Click "Custom installation" to continue to the next screen
<p align="middle">
  <img src="/images/setting_up_python/03.PNG" width="48%" />
</p></li>

<li>You shouldn't need to change anything on this screen, just click "next" in the bottom right corner to continue to the next screen
<p align="middle">
  <img src="/images/setting_up_python/04.PNG" width="48%" />
</p></li>

<li>On this screen, you want to check off "Install for all users"
<p align="middle">
  <img src="/images/setting_up_python/05.PNG" width="48%" />
  <img src="/images/setting_up_python/06.PNG" width="48%" />
</p></li>

<li>Click "Install". Python should be good to go after it finishes loading
<p align="middle">
  <img src="/images/setting_up_python/07.PNG" width="48%" />
</p></li>
</ol>

<a name="code"></a>
### Downloading the code
Download the code from Github and unzip the folder to wherever you to plan to store it

<a name="run_first"></a>
### Running "run_first.py"
Double click "run_first.py" to run the file. Allow it to make changes to your device. If all goes right, this script will automatically install the Python libraries needed for the main script.

If you are having issues with "run_first.py", the needed libraries are listed in "requirements.txt". You can install those manually however you normally install Python libraries.

<a name="setup"></a>
### Setting up the script
Open RPAN Studio and follow the instructions below:
1. Click on Tools -> Scripts from the main options
2. Click "Python Settings" and paste `C:/Program Files/Python36` into the python install path
3. Click "Scripts", click the "+" sign to add a new script, and then add "rpan_chat_commands.py" from wherever you stored it
4. RPAN Studio will restart and request admin privileges. After it does this, you will need to add the script again. It will only do this when you first add the script.
5. The script is now ready to use

## Using r/pan Chat Commands
<a name="nav"></a>
### Navigating the script
There are two menus, `main menu` and `options`.
| `main menu` | `options` |
|---|---|
| <p align="middle">  <img src="/images/how_to_rpan_chat_commands/01.PNG" width="99%" /></p> | <p align="middle">  <img src="/images/how_to_rpan_chat_commands/02.PNG" width="99%" /></p> |

Checking certain settings under `options` will change the layout of both `options` and `main menu`

| `main menu` with most options selected | `options` with most options selected |
|---|---|
|<p align="middle">  <img src="/images/how_to_rpan_chat_commands/03a.PNG" width="99%" /></p>|<p align="middle">  <img src="/images/how_to_rpan_chat_commands/04.PNG" width="99%" /></p>|

<a name="processing"></a>
### Processing comments
To start processing comments, you need to:
<ol>
<li>Start a stream</li>
<li>Copy the stream URL by clicking the "Copy Link to Stream" button (found near the bottom right of the main RPAN Studio screen)
<p align="middle">  <img src="/images/how_to_rpan_chat_commands/05.PNG" width="25%" /></p></li>
<li>Paste the stream URL into r/pan chat commands and then press the "start" button</li>
<li>The "start" button will switch to say "stop". After a short second, the script will begin processing the comments</li>
</ol>

<p align="middle">  <img src="/images/how_to_rpan_chat_commands/06.PNG" width="48%" /></p>

After pressing the "stop" button, there's a 5-10 second delay before the script stops processing comments. Make sure the `script log` says `successfully stopped processing comments` before you start processing comments again / exit the application.

<p align="middle">  <img src="/images/how_to_rpan_chat_commands/07.PNG" width="60%" /></p>

<a name="IDs"></a>
### Getting your secret / client IDs for the Reddit API
After checking off `enable custom messages`, `enable !points command`, or `enable mods` in `options`, a new section will appear under `main menu`.

You will need to enter the login information for your Reddit account and a client / secret ID for the Reddit API.

To retrieve your client / secret IDs, please visit https://www.reddit.com/prefs/apps and log into your reddit account.

1. You will need to create a new app. You only need to change three things when creating your app. Set the name of the app to whatever you want, set the app type to `script`, and then paste `http://localhost:8080` under `redirect uri`. <p align="middle">  <img src="/images/how_to_rpan_chat_commands/08.PNG" width="48%" /></p>
2. After creating your app, it will display two different IDs in the app's settings. You need to copy and paste both of them into their respective areas under `main menu`. The first ID is your client ID, the second being your secret ID. <p align="middle">  <img src="/images/how_to_rpan_chat_commands/09.PNG" width="48%" /></p>

<a name="custom_messages"></a>
### Using custom messages (requires secret / client IDs)
Enabling `enable custom messages` will add new things under both `options` and `main menu`. 

In `options`, you can use the new dropdown list to select between two modes, `auto custom messages` or `use custom command`. Setting this to `auto custom messages` will make it so your custom message is commented automatically every X number of comments. Setting it to `use custom command` will make it so your custom message is automatically commented whenever someone uses your custom command. Both options are useful to link socials, give info about the stream, or any other information you might want to give your viewers. 

Regardless of what is set, `custom message` will appear under `main menu`. The text entered here is what your account will comment whenever your custom message is triggered.

If set to `use custom command`, whenever the text entered in `custom command` is commented, your Reddit account will automatically comment your `custom message`. This command can be set to anything with no restrictions (i.e. `!twitch`, `hairy dog`, `!!! test`, `?help?`). The script just looks for comments that match the text entered in `custom command` exactly.
<p align="middle">  <img src="/images/how_to_rpan_chat_commands/03a.PNG" width="48%" /></p>

If set to `auto custom messages`, changing the `message frequency` slider will effect how many comments need to be commented before your custom message is sent again.
<p align="middle">  <img src="/images/how_to_rpan_chat_commands/03b.PNG" width="48%" /></p>

<a name="points"></a>
### Using the points system
Enabling `enable points` allows viewers to gain points for commenting, awarding the stream, or interacting in consectutive streams.

<ul type = "circle">
<li>Viewers can gain points by commenting over time (every 2 mins, they can gain 2 points for commenting, stacking up to 20 points for 10 mins. They have to comment once to start this timer). This system is designed to discourage spam but still reward viewers who actively engage in the chat. </li>
  
<li>Viewers gain 1/10 reddit coin value in points for awards given (i.e. reddit gold gives 50 points).</li>

<li>Viewers can also gain 20 points for participating in a current stream after being in a previous one.</li>
</ul> 

The only way to spend points at the moment is through the `!tts` command. The entire points system was basically designed as an anti-spam system for that command. Please see [Enabling `!tts` command](#tts_command) for more information. If you have ideas for other ways to redeem points, feel free to let me know

Checking off `enable !points command` makes it so your reddit account comments the points balance of anyone that uses the `!points` command (this feature requires secret / client IDs).

<a name="db_sorter"></a>
### Using the database sorter
After having points enabled for a stream, you can sort throught the information collected with the "rcc_db_sorter.py" script. Add it to RPAN Studio the same way you added the main script.

You can sort through 3 different categories: most frequent commenters (in total number of comments across all streams), top award donaters (in reddit coin value for awards given across all streams), or by whoever has the most points (in total points across all streams). 

<p align="middle">  <img src="/images/how_to_rcc_db_sorter/01.PNG" width="48%" /></p>

After selecting what you want to sort by and clicking "start", the results show up in the `script log`. It will show the top 5 redditors for the category you sorted by, starting with the largest value. There will be a key to help you understand the information shown.

<p align="middle">  <img src="/images/how_to_rcc_db_sorter/02.PNG" width="60%" /></p>

<a name="mods"></a>
### Using the mods system (requires secret / client IDs)
Checking off `enable mods` in options will allow you to appoint mods in chat using `!mod [reddit username]`. You will have to mod yourself if you want to be able to use the `!ban` command. Mods are saved from stream to stream. If you need to edit your mod list, you can find it here: `C:\Program Files\RPAN Studio\bin\64bit\rpan_chat_commands\mod_list.json`.

While the script is active, mods are able to "ban" people using `!ban [reddit username]`. This will block the  "banned" person through your reddit account, preventing them from commenting on your streams. Because the mods are able to block people through your reddit account, please only mod people you trust. If you want to reverse a "ban", just unblock the viewer from your reddit account. 

<a name="tts_command"></a>
### Enabling the `!tts` command
After checking off `enable tts` and `enable !tts command` in `options`, the script will only text-to-speech comments that have the `!tts` command before them (as opposed to every comment).

Enabling `enable tts`, `enable !tts command`, and `enable points`, causes the option `enable tts command cost` to appear. This will make the `!tts` command cost 20 points to use. This means viewers will have to interact with your stream before they are able to text-to-speech any messages. This system is designed to prevent spam. This is currently the only way for viewers to spend points! If you have ideas for other ways to redeem points, please let me know

<a name="comment_display"></a>
### Enabling the comment display
After checking off `enable tts` and `enable comment display` in `options`, a drop down list containing all the current text sources will appear.

The text source you set as the comment display will constantly be updated with the most recent text-to-speeched comment. It's shown in the format: `[reddit username]: [comment]`

If you aren't currently processing comments but still have `enable comment display` checked off, the text source will be updated to say `your tts messages will appear here` until you start processing comments.
