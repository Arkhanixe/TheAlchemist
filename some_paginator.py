import asyncio
import discord

class Paginator:
    """
    A custom built paginator for Requiem. Converts input text to embed pages
    """
    def __init__(self, bot):
        self.bot = bot
        self.color = 0

    async def embed_page_generator(self, text, lines: int=10, title=None, allign=None, field=None, description=None):
        """
        Generates pages. Requires a context argument and a string
        """
        pages = []

        def create_page(output, description):
            """
            A page function that embeds the string and adds it to the list of strings
            """

            if allign:
                # if allign is true, the bot will put the text in codeblocks so the text becomes
                # lined up in the final output

                output = f"```{output}```"

            if field:
                # if field is true, the bot will put the text in an embed field
                # this requires the text also be provided a field name
                # optionally, a description can be provided

                embed = discord.Embed(
                    title=title,
                    description=description,
                    color=self.color
                )
                embed.add_field(name=field, value=output)

            else:
                # if field is not True, the bot will put the text into the embed description.
                # this removes the ability to put any header text in the description

                embed = discord.Embed(
                    title=title,
                    description=output,
                    color=self.color
                )

            # the embed object is added to the pages
            pages.append(embed)

        out = ""

        lines = lines + 1

        # separates the input string into lines and
        # creates pages from them
        for line in text.split("\n"):
            if len(out.split("\n")) <= lines:
                out = out + line + "\n"
            else:
                create_page(out, description)
                out = ""
                out = out + line + "\n"

        if len(out) > 1:
            create_page(out, description)

        # automatically sends the pages after they have been created
        return pages

    async def embed_generator_send(self, target, text, lines: int=10, title=None, allign=None, field=None, description=None):
        """
        Generates embed pages and automatically sends when finished
        """

        # runs paginator.embedPageGenerator
        pages = await self.embed_page_generator(text, lines, title, allign, field, description)

        # runs paginator.send_embed_pages
        await self.send_embed_pages(target, pages)

    async def send_embed_pages(self, target, pages: list):
        """
        Pagniates a message. Requires context argument and a list of pages.
        """

        # sends the starting message and holds onto this message object so that
        # it may be edited later
        message = await target.send(embed=pages[0])

        # it will only add the page selector if the number of pages is greater than 1
        if len(pages) > 1:

            # adds page selectors to message
            await message.add_reaction('◀')
            await asyncio.sleep(1)
            await message.add_reaction('▶')
            await asyncio.sleep(1)

            pag = 0

            for _ in range(200):
                # runs the paginator for 300 seconds
                try:
                    # waits for a reaction, times out after 2 seconds
                    embed = pages[pag]
                    try:
                        author = target.author.id
                    except AttributeError:
                        author = target.id
                    reaction, user = await self.bot.wait_for(
                        "reaction_add",
                        check=lambda r, u: r.message.id == message.id and u.id == author,
                        timeout=2
                    )

                    # checks for reactions, changes page depending on the reaction
                    if reaction.emoji == '◀':
                        if pag == 0:
                            pag = len(pages) - 1
                        else:
                            pag = pag - 1
                        embed = pages[pag]
                    elif reaction.emoji == '▶':
                        if pag == len(pages) - 1:
                            pag = 0
                        else:
                            pag = pag + 1
                        embed = pages[pag]

                    # updates the message with the new page if a reaction is received
                    # raises an exception if no reaction is received
                    await message.edit(embed=embed)

                    # removes the users reaction
                    await message.remove_reaction(reaction.emoji, user)
                except asyncio.TimeoutError:
                    # the bot will ignore timeout errors caused by the "wait for" event
                    pass
                except discord.errors.Forbidden:
                    continue

            # clears reactions when finished
            try:
                await message.clear_reactions()
            except discord.errors.Forbidden:
                pass

            return
