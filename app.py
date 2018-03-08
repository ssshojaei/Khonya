#!/bin/python3
import gi, requests, os, time, vlc,threading
from multiprocessing import Process
from pygame import mixer
# import urllib.request, urllib.parse, urllib.error
import urllib.request
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Pango, GLib, Gtk, GObject
count = 0
s = 8
kill_thread = False
#
def status (text):
    status_lbl.set_label (str(text))
    global time
    time.sleep(1)
    status_lbl.set_label ("")

def set_music():
    print("count is ",count)
    global name
    name2 = str(name.get_text())
    name2.replace(" ", "%20")
    r = requests.get(url='http://api.mostafa-am.ir/radio-javan/'+name2)

    print(r.json()['OK'])
    if r.json()['OK'] == False:
        alert.show()
        name.set_text("")

    if (len(r.json()['Musics']) == 1):
        next_btn.hide()
        prev_btn.hide()

    music.set_label(r.json()['Musics'][count]['Song'])
    artist.set_label(r.json()['Musics'][count]['Artist'])
    # music.modify_font(Pango.FontDescription('Sans Bold 14'))
    # artist.modify_font(Pango.FontDescription('Sans Bold 14'))
    # progress_bar.modify_bg(Gtk.STATE_PRELIGHT, Gtk.Gdk.color_parse("purple"))
    filename = r.json()['Musics'][count]['D_T']+'.jpg'

    if (os.path.isfile("/tmp/"+filename)):
        print ("File is exist!!!")
    else:
        print("download is started")
        urllib.request.urlretrieve(r.json()['Musics'][count]['Photo'], "/tmp/"+filename)

    # print ("/tmp/"+filename)
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename="/tmp/"+filename,
            width=300,
            height=300,
            preserve_aspect_ratio=True)
    image.set_from_pixbuf(pixbuf)

class Handler:
    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)

    def on_search_clicked(self, entry, data=None):
        if len(name.get_text()) > 0:
            set_music()
            window.hide()
            main.show()
    def play(self, button, data=None):
        global kill_thread
        kill_thread = False
        progress.pulse()
        progress.set_fraction(0)
        progress.set_text("0:00:00")
        global name
        name2 = str(name.get_text())
        name2.replace(" ", "%20")
        r = requests.get(url='http://api.mostafa-am.ir/radio-javan/'+name2)
        filename = r.json()['Musics'][count]['D_T']+'.mp3'

        if (os.path.isfile("/tmp/"+filename)):
            print ("File is exist!!!")
            status("File is exist!!!")
        else:
            print("download is started")
            status("download is started")
            # url = 'https://instagram.fevn1-1.fna.fbcdn.net/vp/2d2132b9947c64bd817eedd55eba26e5/5B13F258/t51.2885-15/e35/27580432_1610917395665371_4104660374605791232_n.jpg'
            # urllib.request.urlretrieve(url, 'cat.jpg')
            urllib.request.urlretrieve(r.json()['Musics'][count]['Url'], "/tmp/"+filename)

        print("start played music")
        global player
        player = vlc.MediaPlayer("file:///tmp/"+filename)
        player.play()
        from tinytag import TinyTag
        tag = TinyTag.get("/tmp/"+filename)
        print(tag.duration/60)

        global s
        s = int(tag.duration)
        global thread
        thread = threading.Thread(target=timer_set)
        thread.daemon = False
        thread.start()

    def pause (self, button, data=None):
        global player
        player.pause()
        global s
        s = 0
        global kill_thread
        kill_thread = True
        progress.pulse()
        progress.set_fraction(0)
        progress.set_text("0:00:00")

        print("pause music")
        # global thread
        # # thread.wait(timeout=None)
        # # thread.clear()
        # thread.cancel()
        # thread.stop()

    def next (self, button, data=None):
        global count
        count += 1
        set_music()

    def prev (self, button, data=None):
        global count
        count -= 1
        set_music()

    def end_music(self, progress, data=None):
        print ("end")

    def download(self, *args):
        print ("download")

    def playlist(self, *args):
        print ("download")

builder = Gtk.Builder()
builder.add_from_file("/media/SourceCode/python/khonya/app.glade")
cssProvider = Gtk.CssProvider()
cssProvider.load_from_path('/media/SourceCode/python/khonya/style.css')
screen = Gdk.Screen.get_default()
styleContext = Gtk.StyleContext()
styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

builder.connect_signals(Handler())

window = builder.get_object("window")
alert = builder.get_object("alert")
main = builder.get_object("main")
global name
name = builder.get_object("name")
artist = builder.get_object("artist")
music = builder.get_object("music")
image = builder.get_object("image")
next_btn = builder.get_object("next")
prev_btn = builder.get_object("prev")
progress = builder.get_object("progress")
status_lbl = builder.get_object("status")

def update_progess(i):
    global s
    progress.pulse()
    progress.set_fraction(float(i)/s)
    m, ss = divmod(i, 60)
    h, m = divmod(m, 60)
    progress.set_text("%d:%02d:%02d" % (h, m, ss))
    return False

def timer_set():
    global s
    for i in range(0,s+1):
        global kill_thread
        if kill_thread == True:
            break

        GLib.idle_add(update_progess, i)
        global time
        time.sleep(1)
        print(i)
    print("-> Next music ->")
    global count
    count += 1
    set_music()
    print("play music")
    obj = Handler()
    obj.play ('button')

window.show_all()

settings = Gtk.Settings.get_default()
settings.set_property("gtk-application-prefer-dark-theme", True)
Gtk.main()
