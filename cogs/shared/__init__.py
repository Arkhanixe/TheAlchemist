#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Shared pieces of code between cogs and the bot engine itself.

===

MIT License

Copyright (c) 2018 Neko404NotFound

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import functools


def broken_api(f):
    @functools.wraps(f)
    async def replacement(self, ctx, *args, **kwargs):
        return await ctx.send(
            "This command is currently decomissioned pending "
            "fixes to external APIs that this bot is dependent on."
        )

    return replacement


def broken_command(f):
    @functools.wraps(f)
    async def replacement(self, ctx, *args, **kwargs):
        return await ctx.send("This command is currently in an unusable state.")

    return replacement
