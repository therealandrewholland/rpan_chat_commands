# RPAN Chat Commands
## What is this?
This is a side project I've been working on so RPAN Studio streamers can interact with their viewers in a more immersive way.

Using the script, you can:
- text-to-speech comments (either choose to tts all comments or only comments which contain `!tts` before them)
- display tts-ed comments on one of your current text sources in RPAN Studio
- automatically respond with custom messages whenever someone comments `!help`

I've done my best to design this project so even not-so-tech-savvy people can use it too. There is a very detailed guide on how to set everything up down below. <sub> I apologize in advance to any developers who might be disgusted by my code; I am not a developer, just a professional Googler. </sub> 

If you have the time, I would appreciate if you could check out my [Youtube Channel](https://www.youtube.com/channel/UCa5z0aFw8hzpEl7qhMr0w7g/) where I build robots. Other than that, please enjoy the script and let me know if you have any trouble.

## Setup Guide
### Install Python
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

### Download the code
Download the code from Github and unzip the folder to wherever you to plan to store it

### Run "run_first.py"
Double click "run_first.py" to run the file. Allow it to make changes to your device. If all goes right, it will automatically install the needed Python libraries for the main Python script.

### Setup RPAN Studio
Open RPAN Studio and follow the instructions below:
1. Click on Tools -> Scripts from the main options
2. Click "Python Settings" and paste `C:/Program Files/Python36` into the python install path
3. Click "Scripts", click the "+" sign to add a new script, and then add "rpan_chat_commands.py" from wherever you stored it
4. You will get an error that says something like `TypeError: change_button() takes 2 positional arguments but 3 were given`. This only shows when you first add the script, so just ignore it and restart RPAN Studio.
5. The script is now ready to use

## Using RPAN Chat Commands
### The basics
There are two menus, `main menu` and `options`.
| `main menu` | `options` |
|---|---|
| <p align="middle">  <img src="/images/how_to_rpan_chat_commands/01.PNG" width="99%" /></p> | <p align="middle">  <img src="/images/how_to_rpan_chat_commands/02.PNG" width="99%" /></p> |

Checking certain settings under `options` will change the layout of `main menu`

| checking `enable !help` | checking `enable comment display` |
|---|---|
|<p align="middle">  <img src="/images/how_to_rpan_chat_commands/03.PNG" width="99%" /></p>|<p align="middle">  <img src="/images/how_to_rpan_chat_commands/04.PNG" width="99%" /></p>|

### Processing comments
To start processing comments, you need to:
<ol>
<li>Start a stream</li>
<li>Copy the stream URL by clicking the "Copy Link to Stream" button (found near the bottom right of the main RPAN Studio screen)
<p align="middle">  <img src="/images/how_to_rpan_chat_commands/05.PNG" width="25%" /></p></li>
<li>Paste the stream URL into RPAN Chat Commands and then press the "start" button</li>
<li>The "start" button will switch to say "stop". After a short second, the script will begin processing the comments</li>
</ol>

You can press the "stop" button to stop processing the comments. It is important to do this if you are exiting RPAN Studio, otherwise the script will continue to process comments in the background (you'll have to task manager it to end it).

<p align="middle">  <img src="/images/how_to_rpan_chat_commands/06.PNG" width="48%" /></p>

When you press the "stop" button, there is a 5-10 second delay before the script stops processing comments, so make sure the `script log` says `successfully stopped processing comments` before you start processing comments again / exit the application.

<p align="middle">  <img src="/images/how_to_rpan_chat_commands/07.PNG" width="60%" /></p>

### Using `!help`
After checking off `enable !help` in `options`, new options will appear under `main menu`.

There will be an area to enter the login information of a Reddit account.

The Reddit account you enter will automatically respond with the text entered in `!help response` whenever someone comments the `!help` command. This can be useful to link socials, give info about the stream, or any other information you might want to give your viewers.

There is currently no limit to the number of times this command can be used by an individual, so this command will likely be prone to spam. To prevent this, I'm going to add an alternate feature where the `!help response` will automatically be commented every X comments in the stream. This will make it so your viewers can still see that information as frequently as you want them to, but without them being able to spam the chat.

### Enabling the comment display
After checking off `enable comment display` under `options`, a drop down list containing all the current text sources will be added under `main menu`.

The text source you set as the comment display will constantly be updated with the most recent text-to-speeched comment. It's shown in the format: `[reddit_username]: [comment]`

If you aren't currently processing comments but still have `enable comment display` checked off, the text source will be updated to say `your tts messages will appear here` until you start processing comments.

### Enabling `!tts`
Checking off `enable !tts command` under `options` causes the script to only text-to-speech comments which have the command `!tts` before them (as opposed to the every comment default)
