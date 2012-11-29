#!/usr/bin/python
# encoding=utf-8

import os
import os.path
import codecs

import lqfm.util
from lqfm.player import Player

cmdpipe = lqfm.util.expand(lqfm.util.cmdpipe)
infopipe = lqfm.util.expand(lqfm.util.infopipe)

def start(play=True):

    try:
        player = Player()
        if (play):
            player.play()
        player.start()

        mkpipe()

        cmdreader = open(cmdpipe, 'r')
        while True:
            cmd = cmdreader.read(1)
            if not cmd:
                cmdreader.close()
                cmdreader = open(cmdpipe, 'r')
            elif cmd == 'n':
                index = cmdreader.read(1)
                index = ord(index)
                player.next(index=index)
            elif cmd == 'p':
                if not player.playing:
                    player.play()
            elif cmd == 'P':
                if player.playing:
                    player.pause()
            elif cmd == 'G':
                if player.playing:
                    player.pause()
                else:
                    player.play()
            elif cmd == 'f':
                if not player.song.like:
                    player.like()
            elif cmd == 'u':
                if player.song.like:
                    player.unlike()
            elif cmd == 'F':
                if player.song.like:
                    player.unlike()
                else:
                    player.like()
            elif cmd == 'x':
                player.close()
                clearpipe()
                return
            elif cmd == 'i':
                song = player.song
                with codecs.open(infopipe, 'w', 'utf-8') as infowriter:
                    if song:
                        infowriter.write(song.info())
            elif cmd == 'l':
                songs = player.list()
                with codecs.open(infopipe, 'w', 'utf-8') as listwriter:
                    for s in songs:
                        print >>listwriter, s.oneline()
    except:
        lqfm.util.logerror()
        raise
    finally:
        clearpipe()
        player.close()

def clearpipe():
    for pipe in [cmdpipe, infopipe]:
        if os.path.exists(pipe):
            os.remove(pipe)

def mkpipe():
    for pipe in [cmdpipe, infopipe]:
        lqfm.util.initParent(pipe)
        if os.path.exists(pipe):
            os.remove(pipe)
        os.mkfifo(pipe, 0600)
        

if __name__ == "__main__":
    start()