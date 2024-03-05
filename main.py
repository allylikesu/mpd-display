import pygame
import pygame.freetype
import argparse
import os
import subprocess
import time

os.system("bash -e gen-album-file.sh -k")

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--fullscreen", help="Run in fullscreen mode", action='store_true')
args = parser.parse_args()

pygame.init()

FLAGS = pygame.RESIZABLE
init_flags = FLAGS
if args.fullscreen:
    init_flags = FLAGS | pygame.FULLSCREEN
FULLSCREEN = args.fullscreen
PREVIOUS_RESOLUTION = (0,0)
LAST_TRACK_TITLE = ""
ART_DELAY = 0
FRAMERATE = 60

runningfile = open("running", "w")
runningfile.close()
os.system("bash -e gen-album-file.sh &")

#FONT = pygame.freetype.SysFont("ubuntu", 128)

screen = pygame.display.set_mode((0, 0), init_flags) 
clock = pygame.time.Clock()
running = True

def handle_keys(pygame):
    global FULLSCREEN
    global PREVIOUS_RESOLUTION
    global FLAGS
    keys = pygame.key.get_pressed()
    if keys[pygame.K_F11] or keys[pygame.K_f]:
        print("Fullscreen: " + str(FULLSCREEN))
        if FULLSCREEN:
            pygame.display.set_mode(PREVIOUS_RESOLUTION, FLAGS)
        else:
            PREVIOUS_RESOLUTION = pygame.display.get_window_size()
            pygame.display.set_mode((0,0), FLAGS | pygame.FULLSCREEN)
        FULLSCREEN = not FULLSCREEN

def draw_background(background_file, cover_file, pygame, screen):
    window_width = screen.get_width()
    window_height = screen.get_height()

    if background_file == None:
        cover_surface = pygame.image.load(cover_file)
        average_color = pygame.transform.average_color(cover_surface)
        color_rect = pygame.Surface((2,2))
        pygame.draw.line(color_rect, (50,50,50), (0,0),(1,0))
        pygame.draw.line(color_rect, average_color, (0,1),(1,1))
        color_rect = pygame.transform.smoothscale(color_rect, (window_width,window_height))
        screen.blit(color_rect, (0,0))
        return

    bgsurface = pygame.image.load(background_file)
    pygame.Surface.convert_alpha(bgsurface)
    image_width = bgsurface.get_width()
    image_height = bgsurface.get_height()

    x_offset = 0
    y_offset = 0
    scale = window_width/image_width
    if image_height*scale < window_height:
        scale = window_height/image_height
        x_offset = window_width/-2 + (image_width*scale/2)
    else:
        y_offset = window_height/-2 + (image_height*scale/2)

    bgsurface = pygame.transform.smoothscale_by(bgsurface, scale)
    bgsurface.fill((75,75,75,0), special_flags=pygame.BLEND_MULT)

    screen.blit(bgsurface, (-x_offset,-y_offset))

    #pygame.draw.rect(screen, (255,0,0,200), screen.get_rect().copy())

def draw_info(file, title, artist, pygame, screen):
    #global FONT
    window_width = screen.get_width()
    window_height = screen.get_height()

    imagesurface = pygame.image.load(file)
    pygame.Surface.convert_alpha(imagesurface)

    resize_value = min(window_height, window_width)/3
    image_y_offset = window_height/6*5 - resize_value
    image_x_offset = window_width/16

    imagesurface = pygame.transform.smoothscale(imagesurface, (resize_value, resize_value))

    screen.blit(imagesurface, (image_x_offset, image_y_offset))

    fontsize = resize_value/3
    FONT = pygame.freetype.Font("font/CircularStd-Bold.otf", fontsize)
    #print(fontsize)

    title_text_surface, title_text_rect = FONT.render(title, (255,255,255))
    title_text_x_offset = image_x_offset+resize_value*1.1
    title_text_y_offset = image_y_offset+resize_value*0.4
    while title_text_x_offset + title_text_rect.width > window_width - window_width/100:
        fontsize = fontsize*0.9
        FONT = pygame.freetype.Font("font/CircularStd-Bold.otf", fontsize)
        title_text_surface, title_text_rect = FONT.render(title, (255,255,255))

    screen.blit(title_text_surface, (title_text_x_offset, title_text_y_offset))

    artist_text_surface, artist_text_rect = FONT.render(artist, (195,195,195))#(224,224,244))#(156, 156, 156))
    artist_text_surface = pygame.transform.smoothscale_by(artist_text_surface, 0.5)
    artist_text_x_offset = title_text_x_offset
    artist_text_y_offset = title_text_y_offset + title_text_rect.height + resize_value*0.1

    screen.blit(artist_text_surface, (artist_text_x_offset, artist_text_y_offset))

def draw_watermark(pygame, screen):
    window_width = screen.get_width()
    window_height = screen.get_height()

    imagesurface = pygame.image.load("logo2.png")
    pygame.Surface.convert_alpha(imagesurface)
    #imagealpha = pygame.Surface(imagesurface.get_size(), pygame.SRCALPHA)
    #imagealpha.fill((255,255,255,90))
    #imagesurface.blit(imagealpha, (0,0), special_flags=pygame.BLEND_MULT)
    #imagesurface.fill((50,50,50,0), special_flags=pygame.BLEND_MULT)
    image_width = imagesurface.get_width()
    image_height = imagesurface.get_height()
    resize_scale = (window_height/9)/image_height
    imagesurface = pygame.transform.smoothscale_by(imagesurface, resize_scale)

    image_x_offset = window_width/20
    image_y_offset = window_height/20

    screen.blit(imagesurface, (image_x_offset, image_y_offset))

    fontsize = imagesurface.get_height()/4
    TEXTFONT = pygame.freetype.Font("font/CircularStd-Book.otf", fontsize*6/8)
    ALBUMFONT = pygame.freetype.Font("font/CircularStd-Bold.otf", fontsize)

    image_width = imagesurface.get_width()
    image_height = imagesurface.get_height()
    text, text_rect = TEXTFONT.render("PLAYING FROM MPD QUEUE", (156, 156, 156))
    text_x_offset = image_x_offset + image_width + imagesurface.get_height()/4
    text_y_offset = image_y_offset + text.get_height()*1.8#+image_height/4
    screen.blit(text, (text_x_offset, text_y_offset))

    get_queue_length = subprocess.run(["mpc", "status", "%length%"], stdout=subprocess.PIPE, text=True)
    queue_length = get_queue_length.stdout[:-1]

    albumtext, ablum_rect = ALBUMFONT.render(f"{queue_length} tracks left", (156,156,156))
    album_x_offset = text_x_offset
    album_y_offset = text_y_offset + albumtext.get_height()*1.4
    screen.blit(albumtext, (album_x_offset, album_y_offset))

def draw_progressbar(pygame, screen):
    window_width = screen.get_width()
    window_height = screen.get_height()

    col_base = (156,156,156, 128)#(185,185,185)
    col_progress = (255,255,255)
    col_text = col_progress
    col_progress_circle = col_progress

    bar_length = window_width*0.85
    bar_offset_x = int((window_width-bar_length)*0.5)
    bar_height = int(window_height*0.006)
    bar_offset_y = int(window_height*0.9)

    bar_hover = False
    (mouse_x, mouse_y) = pygame.mouse.get_pos()
    if mouse_y > bar_offset_y - bar_height*4 and mouse_y < bar_offset_y+bar_height*5:
        bar_hover = True
        col_progress = (29, 185, 84)

    #bar_rect = pygame.Rect(int(bar_offset_x), int(bar_offset_y), int(bar_length), int(bar_height))
    bar_rect = pygame.Surface((int(bar_length), int(bar_height)))
    bar_rect.set_alpha(128)
    bar_rect.fill(col_base)
    screen.blit(bar_rect, (int(bar_offset_x), int(bar_offset_y)))
    #pygame.draw.rect(screen, col_base, bar_rect)

    circle_radius = int(bar_height/2)
    circle_y_offset = bar_offset_y + circle_radius
    l_circle_offset = bar_offset_x
    r_circle_offset = bar_offset_x+bar_length

    #circle_l = pygame.Surface((circle_radius*2, circle_radius*2), pygame.SRCALPHA)
    #pygame.draw.circle(circle_l, col_progress, (circle_radius, circle_radius), circle_lradius)#(l_circle_offset, circle_y_offset), circle_radius)
    #screen.blit(circle_l )
    pygame.draw.circle(screen, col_progress, (l_circle_offset, circle_y_offset), circle_radius)

    #pygame.draw.circle(screen, col_base, (r_circle_offset, circle_y_offset), circle_radius)
    circle_r = pygame.Surface((circle_radius*2, circle_radius*2), pygame.SRCALPHA)
    pygame.draw.circle(circle_r, col_base, (circle_radius, circle_radius), circle_radius)#(l_circle_offset, circle_y_offset), circle_radius)
    circle_r.scroll(-circle_radius, 0)
    screen.blit(circle_r, (r_circle_offset, circle_y_offset-circle_radius), (circle_radius, 0, circle_radius, circle_radius*2))

    #bar_end = bar_length + bar_offset_x
    #print(f"Bar ends: {bar_end} Circle starts: {r_circle_offset}")

    get_song_percentage = subprocess.run(["mpc", "status", "%percenttime%"], stdout=subprocess.PIPE, text=True)
    song_percentage = get_song_percentage.stdout.strip()[:-1]
    get_times = subprocess.run(["mpc", "status", "%currenttime% %totaltime%"], stdout=subprocess.PIPE, text=True)
    times = get_times.stdout.strip().split(" ")
    current_time = times[0].split(":")
    total_time = times[1].split(":")
    current_second = int(current_time[0])*60 + int(current_time[1])
    total_seconds = int(total_time[0])*60 + int(total_time[1])

    #song_ratio = int(song_percentage)/100
    if total_seconds == 0:
        song_ratio = 0
    else:
        if total_seconds > 100:
            song_ratio = current_second/total_seconds
        else:
            song_ratio = int(song_percentage)/100
        #percentage_ratio = int(song_percentage)/100
        #song_ratio = current_second/total_seconds
        #if percentage_ratio - PREVIOUS_SONG_RATIO < song_ratio - PREVIOUS_SONG_RATIO:
            #song_ratio = percentage_ratio
    if song_ratio > 0.9:
        get_next = subprocess.run(["mpc", "queued"], stdout=subprocess.PIPE, text=True)
        next_song = get_next.stdout[:-1]
        fontsize = window_height/30
        BOLDFONT = pygame.freetype.Font("font/CircularStd-Bold.otf", fontsize*1.1)
        FONT = pygame.freetype.Font("font/CircularStd-Book.otf", fontsize)
        upnext, upnext_rect = BOLDFONT.render("Up next:", col_text)
        nextsong, nextsong_rect = FONT.render(next_song, col_text)
        next_offset_y = window_height/20
        next_offset_x = window_width - max(nextsong.get_width(), upnext.get_width()) - window_width/30
        #padding = fontsize/2
        #next_rect = pygame.Rect(next_offset_x - padding, next_offset_y - padding, max(upnext.get_width(), nextsong.get_width()) + padding*2, nextsong.get_height()+upnext.get_height()+padding*2)
        #pygame.draw.rect(screen, (0,0,0,255), next_rect)

        barratio = song_ratio*10-9
        baroffset = (window_width - next_offset_x)*barratio
        barrect = pygame.Rect(next_offset_x+baroffset, next_offset_y+upnext.get_height()+nextsong.get_height()+fontsize/2, window_width*0.5, bar_height)
        pygame.draw.rect(screen, col_text, barrect)
        screen.blit(upnext, (next_offset_x, next_offset_y))
        screen.blit(nextsong, (next_offset_x, next_offset_y+upnext.get_height()))

        

    progress_circle_x_offset = bar_offset_x + (bar_length*song_ratio)

    prog_bar_length = progress_circle_x_offset - bar_offset_x
    prog_bar_rect = pygame.Rect(int(bar_offset_x), int(bar_offset_y), int(prog_bar_length), int(bar_height))
    pygame.draw.rect(screen, col_progress, prog_bar_rect)

    progress_circle_radius = circle_radius
    if bar_hover:
        progress_circle_radius = circle_radius*2
    pygame.draw.circle(screen, col_progress_circle, (progress_circle_x_offset, circle_y_offset), progress_circle_radius)

    fontsize = bar_height*3
    FONT = pygame.freetype.Font("font/CircularStd-Book.otf", fontsize)

    l_text, l_text_rect = FONT.render(times[0], col_text)
    l_text_x_offset = bar_offset_x - l_text.get_width() - circle_radius*3# - window_width*0.01
    text_y_offset = bar_offset_y - l_text.get_height()/4
    screen.blit(l_text, (l_text_x_offset, text_y_offset))

    r_text, r_text_rect = FONT.render(times[1], col_text)
    r_text_x_offset = bar_offset_x + bar_length + circle_radius*3# + window_width*0.01
    screen.blit(r_text, (r_text_x_offset, text_y_offset))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                os.system("mpc toggle -q")
        if event.type == pygame.KEYDOWN:
            if event.key == 27 or event.key == 113:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            if event.key == 32:
                os.system("mpc toggle -q")

    #screen.fill("purple")
    handle_keys(pygame)

    # render screen
    get_artist = subprocess.run(["mpc", "-f", "%artist%", "current"], stdout=subprocess.PIPE, text=True)
    artist_name = get_artist.stdout[:-1]
    main_artist = artist_name.split(", ")[0].split("/")[0].split(" & ")[0].split("; ")[0].lower()
    get_title = subprocess.run(["mpc", "-f", "%title%", "current"], stdout=subprocess.PIPE, text=True)
    track_title = get_title.stdout[:-1]
    if track_title != LAST_TRACK_TITLE:
        print("Detected change")
        LAST_TRACK_TITLE = track_title
        ART_DELAY = 15

    bgfile = os.path.join('artists', main_artist + ".jpg")
    if not os.path.isfile(bgfile):
        bgfile = None
    #if ART_DELAY > 0:
        #albumfile = "art_backup"
        #ART_DELAY-=1
    #else:
        #print("Reading art from file...")
    albumfile = "art"

    try:
        draw_background(bgfile, albumfile, pygame, screen)
        draw_info(albumfile, track_title, artist_name, pygame, screen)
    except:
        albumfile = "art_backup"
        draw_background(bgfile, albumfile, pygame, screen)
        draw_info(albumfile, track_title, artist_name, pygame, screen)

    draw_watermark(pygame, screen)
    draw_progressbar(pygame, screen)

    pygame.display.flip()

    clock.tick(FRAMERATE)

os.remove("running")
pygame.quit()
