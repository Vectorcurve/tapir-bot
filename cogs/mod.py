from discord.ext import commands
from .utils import config, checks
from collections import Counter
import re
import discord
import asyncio

class Mod:
    """Moderation related commands."""

    def __init__(self, bot):
        self.bot = bot
        self.config = config.Config('mod.json', loop=bot.loop)

    def bot_user(self, message):
        return message.server.me if message.channel.is_private else self.bot.user

    @commands.group(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_channels=True)
    async def ignore(self, ctx):
        """Handles the bot's ignore lists.
        To use these commands, you must have the Bot Admin role or have
        Manage Channels permissions. These commands are not allowed to be used
        in a private message context.
        Users with Manage Roles or Bot Admin role can still invoke the bot
        in ignored channels.
        """
        if ctx.invoked_subcommand is None:
            await self.bot.say('Invalid subcommand passed: {0.subcommand_passed}'.format(ctx))
            
    @ignore.command(name='list', pass_context=True)
    async def ignore_list(self, ctx):
        """Tells you what channels are currently ignored in this server."""

        ignored = self.config.get('ignored', [])
        channel_ids = set(c.id for c in ctx.message.server.channels)
        result = []
        for channel in ignored:
            if channel in channel_ids:
                result.append('<#{}>'.format(channel))

        if result:
            await self.bot.say('The following channels are ignored:\n\n{}'.format(', '.join(result)))
        else:
            await self.bot.say('I am not ignoring any channels here.')
            
    @ignore.command(name='channel', pass_context=True)
    async def channel_cmd(self, ctx, *, channel : discord.Channel = None):
        """Ignores a specific channel from being processed.
        If no channel is specified, the current channel is ignored.
        If a channel is ignored then the bot does not process commands in that
        channel until it is unignored.
        """

        if channel is None:
            channel = ctx.message.channel

        ignored = self.config.get('ignored', [])
        if channel.id in ignored:
            await self.bot.say('That channel is already ignored.')
            return

        ignored.append(channel.id)
        await self.config.put('ignored', ignored)
        await self.bot.say('\U0001f44c')
        
    @ignore.command(name='all', pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _all(self, ctx):
        """Ignores every channel in the server from being processed.
        This works by adding every channel that the server currently has into
        the ignore list. If more channels are added then they will have to be
        ignored by using the ignore command.
        To use this command you must have Manage Server permissions along with
        Manage Channels permissions. You could also have the Bot Admin role.
        """

        ignored = self.config.get('ignored', [])
        channels = ctx.message.server.channels
        ignored.extend(c.id for c in channels if c.type == discord.ChannelType.text)
        await self.config.put('ignored', list(set(ignored))) # make unique
        await self.bot.say('\U0001f44c')
        
    @commands.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_channels=True)
    async def unignore(self, ctx, *, channel : discord.Channel = None):
        """Unignores a specific channel from being processed.
        If no channel is specified, it unignores the current channel.
        To use this command you must have the Manage Channels permission or have the
        Bot Admin role.
        """

        if channel is None:
            channel = ctx.message.channel

        # a set is the proper data type for the ignore list
        # however, JSON only supports arrays and objects not sets.
        ignored = self.config.get('ignored', [])
        try:
            ignored.remove(channel.id)
        except ValueError:
            await self.bot.say('Channel was not ignored in the first place.')
        else:
            await self.bot.say('\U0001f44c')
            
def setup(bot):
    bot.add_cog(Mod(bot))