## Pneuma ![alt text](https://github.com/[lorenzyme]/[PneumaBot]/blob/[main]/pneuma.jpg?raw=true)

Pneuma is a Discord bot that plays music in voice channels. It supports playing music from YouTube by either providing a URL or searching by song title.
    
## Features

    Plays music from YouTube by URL or song title
    Joins and leaves voice channels
    Pauses, resumes, and stops music playback
    Automatically disconnects from voice channel after 5 minutes of inactivity to save resources

## !Commands

    !join: Make the bot join your current voice channel.
    !play <URL or song title>: Play a song by URL or search query.
    !pause: Pause the currently playing song.
    !resume: Resume the currently paused song.
    !stop: Stop the currently playing song.
    !leave: Make the bot leave the voice channel.



## Examples

Play Music by URL:

!play https://www.youtube.com/watch?v=dQw4w9WgXcQ

Play Music by song title:

!play Never Gonna Give You Up

Stop Music and Leave the Channel:

    !stop
    !leave

## Requirements

    Python 3.6+
    discord.py library
    yt-dlp library
    youtube-search-python library
    PyNaCl library
    ffmpeg installed and available in your PATH
    An .env file in the project directory for the bot token:

## Troubleshooting

If you encounter any issues, ensure that all required libraries are installed and that your .env file is correctly configured. You can also check the bot.log file for any error messages.

Contributions are welcome! Feel free to open an issue or submit a pull request. :)

## License

This project is licensed under the MIT License.
