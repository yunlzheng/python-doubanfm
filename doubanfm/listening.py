#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import os.path
import socket
import logging
import logging.handlers

from util import initParent, readCmdLine, socketfile, \
        encode, inline, EOFflag
from player import Player
import config

logger = logging.getLogger(__name__)

closed = False
player = None

def init():
    config.init()
    config.load()
    global player
    player = Player()
    player.start()

def start():

    try:
        init()

        logger.info('启动服务')
        s = socket.socket(socket.AF_UNIX)
        initParent(socketfile)
        s.bind(socketfile)
        s.listen(1)

        while not closed:
            con, add = s.accept()
            handler(con)
    except:
        logger.exception('处理命令时发生异常')
        raise
    finally:
        s.close()
        close()

def close():
    if os.path.exists(socketfile):
        os.remove(socketfile)
    if player:
        player.close()

def handler(con):
    try:
        f = con.makefile('rw')
        while not closed:
            cmd, args = readCmdLine(f)
            if not cmd:
                con.close()
                return
            logger.info(u'处理命令 %s %s', cmd, args)
            if hasattr(cmdHandler, cmd):
                m = getattr(cmdHandler, cmd)
                try:
                    result, message = m(*args)
                    if result:
                        if not message:
                            f.write('OK\n')
                        else:
                            f.write('VALUE %s\n' % EOFflag)
                            f.write(encode(message))
                            f.write('\n')
                            f.write(EOFflag)
                            f.write('\n')
                    else:
                        f.write('FAIL %s\n' % inline(encode(message)))
                except Exception as e:
                    logger.exception(u'处理命令异常 %s %s', cmd, args)
                    f.write('ERROR %s\n' % inline(encode(e)))
            else:
                f.write('ERROR unknow cmd %s\n' % cmd)
            f.flush()
    except socket.error as e:
        if e.errno == 32:
            # Broken pipe
            # 连接断开
            pass
        else:
            raise
    finally:
        con.close()

class CmdHander(object):

    def next(self, *args):
        index = 0
        if args:
            index = int(args[0])
        player.next(index=index)
        return True, ''

    def play(self, *args):
        if not player.playing:
            player.play()
        return True, ''

    def pause(self, *args):
        if player.playing:
            player.pause()
        return True, ''

    def togglePause(self, *args):
        if player.playing:
            player.pause()
        else:
            player.play()
        return True, ''

    def favourite(self, *args):
        player.like()
        return True, ''

    def unFavourite(self, *args):
        player.unlike()
        return True, ''

    def info(self, *args):
        song = player.song
        message = None
        if song:
            message = song.info()
        if message:
            return True, message
        else:
            return True, '没有歌曲正在播放'

    def list(self, *args):
        songs = player.list()
        message = '\n'.join([song.oneline() for song in songs])
        if message:
            return True, message
        else:
            return True, '歌曲列表为空'

    def exit(self, *args):
        global closed
        closed = True
        player.close()
        return True, ''

cmdHandler = CmdHander()

if __name__ == "__main__":
    start()
