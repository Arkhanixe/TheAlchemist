#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Music cog. Enables the streaming of audio from sites such as YouTube
to a voice channel; one per guild.
"""


def __bootstrap():
    import os
    import discord
    from neko2.shared import scribe, morefunctools

    class NekoOpus(scribe.Scribe, metaclass=morefunctools.SingletonMeta):
        pass

    if not discord.opus.is_loaded():
        if os.name == "winnt":
            discord.opus.load_opus("libopus-0.dll")
            NekoOpus.logger.info("Loaded libopus-0.dll successfully.")
        else:
            discord.opus.load_opus("libopus.so")
            NekoOpus.logger.info("Loaded libopus.so successfully.")
    else:
        # noinspection PyProtectedMember
        NekoOpus.logger.info(f"Opus was already loaded as {discord.opus._lib}")


__bootstrap()
del __bootstrap

# Once opus is loaded, we can load the cog into the namespace.
from . import cog


def setup(bot):
    bot.add_cog(cog.MusicCog())
