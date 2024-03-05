# Spotify-like graphical display for MPD

Note that this is not a full MPD client, as it only *displays* data.
Eventually I want to rewrite it in *anything* that isn't pygame.

This will probably only work on linux.
Requires MPC.

## Features
- Toggleable fullscreen with the `f` or `F11` key
- Fully resizable window, all screen elements will be properly scaled/positioned
- Artist-specific background art (See more [here](https://github.com/allylikesu/mpd-display#obtaining-and-using-artist-background-images))
- Design basically fully ripped off of the Spotify desktop client's fullscreen mode
- Extremely poorly optimized
- Click or press space to play/pause
- "Up Next" display when current song hits 90% completion
- Easy to quit with `Esc` or `q`

## Screenshots
It is 2am. I will add screenshots later.

## Installation/Usage
I provide no packaging solutions. Clone the repo and run main.py.

The `-f` flag will make the app launch in fullscreen.

A portable launch script can be made and put in $PATH using this template:
`#!/usr/bin/env bash

cd <PATH TO CLONED REPO> || exit 1

python3 main.py [-f]`

## Obtaining and using artist background images
For Spotify's fullscreen mode, it uses a slightly darkened version of the main artist's profile banner as a background. 
This behaviour is replicated by this program, but the images need to be manually obtained.
If you don't care about Spotify and have your own images you want to use, that is totally cool!
The format of the file should be `<artist name>.jpg`.
The file name should be in **ALL LOWERCASE!**
