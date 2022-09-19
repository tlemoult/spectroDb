#!/bin/bash
echo emulate serial port thru MOXA server tcp

killall socat

HOME=~


NEWTTY=$HOME/.local/dev/ttyAstrosib
SERVER=moxa1:4001
echo Create $NEWTTY as $SERVER
socat  pty,link=$NEWTTY,group-late=dialout,mode=660  tcp:$SERVER &

NEWTTY=$HOME/.local/dev/ttyPowerControl
SERVER=moxa1:4002
echo Create $NEWTTY as $SERVER
socat  pty,link=$NEWTTY,group-late=dialout,mode=660  tcp:$SERVER &

NEWTTY=$HOME/.local/dev/ttyMount
SERVER=moxa1:4004
echo Create $NEWTTY as $SERVER
socat  pty,link=$NEWTTY,group-late=dialout,mode=660  tcp:$SERVER &

NEWTTY=$HOME/.local/dev/ttyEshel
SERVER=moxaEshel:4001
echo Create $NEWTTY as $SERVER
socat  pty,link=$NEWTTY,group-late=dialout,mode=660  tcp:$SERVER &

NEWTTY=$HOME/.local/dev/ttyDome
SERVER=moxaDome:4001
echo Create $NEWTTY as $SERVER
socat  pty,link=$NEWTTY,group-late=dialout,mode=660  tcp:$SERVER &

