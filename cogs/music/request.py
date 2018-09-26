#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Dataclasses to represent a request from a user.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

import discord
import libneko
from libneko.aggregates import MutableOrderedSet


@dataclass(repr=False)
class Request:
    title: str
    id: str
    # Referral description. Might be the term used to search for the video,
    # or it might be the actual URL if that was given instead.
    referral: str
    user: discord.Member
    url: str
    thumbnail: str
    length: timedelta
    author: str
    author_url: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __str__(self):
        frag = self.title[:50]
        if len(self.title) > 50:
            return frag + "..."
        else:
            return frag

    def __repr__(self):
        return f"<Request title={self.title} url={self.youtube_url} user={self.user} created_at={self.created_at}"

    @property
    def youtube_url(self) -> str:
        return f"https://youtube.com/watch?v={self.id}"

    def __hash__(self):
        return hash(self.youtube_url)

    def full_str(self):
        return f'"{self.title}"\n\u2003 -- requested by @{self.user}'

    def make_embeds(self, title=None):
        embed = libneko.Embed(
            title=self.title,
            url=self.youtube_url,
            description=(
                f"Requested by: {self.user}\n"
                f"Length: {self.length}\n"
                f"Author: [{self.author}]({self.author_url})"
            ),
        )

        if title:
            embed.set_author(name=title, url=self.youtube_url)

        embed.timestamp = self.created_at
        embed.set_thumbnail(url=self.thumbnail)

        return [embed]


@dataclass(repr=True)
class Mix:
    referral: str
    user: discord.Member
    tracks: MutableOrderedSet[Request]
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def title(self) -> str:
        return self.referral

    @property
    def length(self):
        return timedelta(seconds=sum(t.length.total_seconds() for t in self))

    def __str__(self):
        return (
            f'"{self.title}" mix requested by @{self.user} with {len(self)} track'
            f'{"s" if len(self) - 1 else ""}'
        )

    def __iter__(self):
        return iter(self.tracks)

    def __getitem__(self, item):
        return self.tracks[item]

    def __len__(self):
        return len(self.tracks)

    def shift(self):
        track = self.tracks[0]
        self.tracks.discard(track)
        return track

    @property
    def thumbnail(self):
        if self.tracks:
            return self.tracks[0].thumbnail
        else:
            # https://www.reddit.com/r/discordapp/comments/4ksmrc
            #     /is_there_a_way_to_access_the_default_discord_user/
            return "https://discordapp.com/assets/dd4dbc0016779df1378e7812eabaa04d.png"

    def make_embeds(self, title=None):
        def new_embed():
            embed = libneko.Embed(
                title=self.title,
                url=self.referral,
                description=(
                    f"Requested by: {self.user}\n" f"Total length: {self.length}\n"
                ),
            )

            if title:
                embed.set_author(name=title, url=self.referral)

            embed.timestamp = self.created_at
            return embed

        embeds = []

        for i, track in enumerate(self):
            embed = new_embed()

            subtitle = f"[{i + 1}/{len(self)}] {track.title}"
            body = (
                f"**[Listen on YouTube]({track.url})**\n"
                f"Length: {track.length}\n"
                f"Author: [{track.author}]({track.author_url})"
            )

            embed.add_field(name=subtitle, value=body)
            embed.set_thumbnail(url=track.thumbnail)

            embeds.append(embed)

        if not embeds:
            embed = new_embed()
            embed.add_field(
                name="Loading data...", value="Please try again in a minute or two."
            )
            embeds.append(embed)

        return embeds
