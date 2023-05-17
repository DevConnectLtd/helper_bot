# type: ignore
# TODO: type and refactor

from datetime import datetime

import disnake
from disnake.ext import commands

from core.constants import ChannelID, RoleID, General
from core.utils import HelperCog

MODERATOR_ROLE_ID = RoleID.MODERATOR
TICKET_CHANNEL_ID = ChannelID.TICKET_CHANNEL_ID

class TicketSys:

    @staticmethod
    async def open_ticket(interaction:disnake.Interaction,reason : list):
            await interaction.response.edit_message(
                f"{interaction.author.mention},<@&{MODERATOR_ROLE_ID}>",
                embed=disnake.Embed(
                    title="Ticket opened", description=reason[0], color=disnake.Color.green(), timestamp=datetime.now()
                )
                .set_thumbnail(interaction.author.avatar.url)
                .set_author(name=interaction.author),
                view=TicketCloseButtons(interaction.channel, interaction.author, reason[0]),
            )
            await interaction.channel.edit(name=f"{reason[1]}-{str(interaction.author)}")
            await interaction.author.send(
                embed=disnake.Embed(
                title="Ticket opened",
                description=f"Your ticket has been opened in {interaction.guild.name}",
                color=disnake.Color.green(),
                timestamp=datetime.now()
                )
                 .set_thumbnail(interaction.guild.icon.url)
                 .add_field('Channel',interaction.channel.mention)
                 .add_field('Demand',reason[0])
                )

class Ticket(HelperCog):
    'Ticket System'

    hidden = True
    
    @commands.Cog.listener()
    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        username_before: str = str(before)
        username_after: str = str(after)
        if username_before != username_after:
            ticket_channel: disnake.TextChannel = self.bot.get_channel(
                TICKET_CHANNEL_ID
            ) or await self.bot.fetch_channel(TICKET_CHANNEL_ID)
            thread: disnake.Thread = [
                threads for threads in ticket_channel.threads if threads.name.split("-")[1] == username_before
            ][0]
            thread_name = thread.name.split("-")[0] + "-"
            if thread:
                await thread.edit(name=thread_name + username_after)
                await thread.send(
                    embed=disnake.Embed(
                        title="Changed thread name", color=disnake.Color.blurple(), timestamp=datetime.now()
                    )
                    .add_field("Before", thread_name + username_before)
                    .add_field("After", thread_name + username_after)
                )


    @commands.command()
    @commands.has_role(RoleID.MODERATOR)
    async def setupticket(self, ctx: commands.Context, channel: disnake.TextChannel = None):
        channel = channel or ctx.channel
        await ctx.reply(f"Created ticket system in {channel.mention}")
        await channel.send(
            embed=disnake.Embed(
                title="Ticket Support",
                description="Click on the button below for opening a ticket.",
                color=disnake.Color.blurple(),
            ),
            view=TicketButton(),
        )


class TicketButton(disnake.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @disnake.ui.button(label="Create ticket", style=disnake.ButtonStyle.blurple)
    async def create_button(self, button: disnake.ui.Button, interaction: disnake.Interaction) -> None:
        # Todo : db check if user already has a ticket or not
        # if (str(interaction.author) not in [name.name.split("-")[1] for name in interaction.channel.threads]):
            thread = await interaction.channel.create_thread(
                name=str(interaction.author), type=disnake.ChannelType.private_thread
            )

            await interaction.response.send_message(
                embed=disnake.Embed(
                    description=f"Created ur ticket {thread.mention}",
                    color=disnake.Color.green(),
                    timestamp=datetime.now(),
                ),
                ephemeral=True,
            )

            await thread.send(
                interaction.author.mention,
                embed=disnake.Embed(
                    description="Why are u creating a ticket? \n Kindly select an option below.",
                    color=disnake.Color.yellow(),
                ),
                view=ChoiceButtons(thread, interaction.author),
            )
            
        # else:
        #     await interaction.response.send_message(
        #         embed=disnake.Embed(description="You already have a ticket active", color=disnake.Color.red()),
        #         ephemeral=True,
        #     )


class ChoiceButtons(disnake.ui.View):
    def __init__(self, thread: disnake.Thread, author: disnake.Member) -> None:
        super().__init__(timeout=120)
        self.author: disnake.Member = author
        self.thread: disnake.Thread = thread
        self.activity: bool = False

    @disnake.ui.button(label="Report", style=disnake.ButtonStyle.blurple)
    async def report_button(self, button: disnake.ui.Button, interaction: disnake.Interaction) -> None:
        if self.author == interaction.author:
            await interaction.response.edit_message(
                interaction.author.mention,
                embed=disnake.Embed(
                    title="Report", description="What do u want a report?", color=disnake.Color.yellow()
                ),
                view=ReportButtons(self.thread, interaction.author),
            )
            self.activity = True

    @disnake.ui.button(label="Order", style=disnake.ButtonStyle.blurple)
    async def order_button(self, button: disnake.ui.Button, interaction: disnake.Interaction) -> None:
        if self.author == interaction.author:
            await interaction.response.edit_message(embed=disnake.Embed(title="What service do u want?",color=disnake.Color.yellow()),view=Order_DropdownView(self.thread))
            self.activity = True

    async def on_timeout(self):
        if not self.activity:
            await self.thread.delete()
            await self.author.send(embed=disnake.Embed(description="Your ticket has been closed due to inactivity",color=disnake.Color.red(),timestamp=datetime.now()))


class ReportButtons(disnake.ui.View):
    def __init__(self, thread, author) -> None:
        super().__init__(timeout=120)
        self.author: disnake.Member = author
        self.thread: disnake.Thread = thread
        self.activity: bool = False

    @disnake.ui.button(label="User", style=disnake.ButtonStyle.blurple)
    async def user_report_button(self, button: disnake.ui.Button, interaction: disnake.Interaction) -> None:
        if self.author == interaction.author:
            await TicketSys.open_ticket(interaction,['User Report','UR'])
            self.activity = True

    @disnake.ui.button(label="Issue", style=disnake.ButtonStyle.blurple)
    async def issue_report_button(self, button: disnake.ui.Button, interaction: disnake.Interaction) -> None:
        if self.author == interaction.author:
            await TicketSys.open_ticket(interaction,['Issue Report','IR'])
            self.activity = True

    async def on_timeout(self):
        if not self.activity:
            await self.thread.delete()
            await self.author.send(embed=disnake.Embed(description="Your ticket has been closed due to inactivity",color=disnake.Color.red(),timestamp=datetime.now()))

class Order_DropDown(disnake.ui.Select):
    def __init__(self):
        super().__init__(placeholder='Kindly choose the service u want', min_values=1, max_values=1, options=General.SERVICES)
    async def callback(self, interaction: disnake.Interaction):
        values = self.values[0]
        await TicketSys.open_ticket(interaction,[values,''.join([value[0].capitalize() for value in values.split(' ')])])

class Order_DropdownView(disnake.ui.View):
    def __init__(self,thread: disnake.Thread):
        self.thread: disnake.Thread = thread
        super().__init__(timeout=60)
        self.add_item(Order_DropDown())

class TicketCloseButtons(disnake.ui.View):
    def __init__(self, thread: disnake.Thread, author: disnake.Member, reason_created: str = None) -> None:
        super().__init__(timeout=604800)
        self.author: disnake.Member = author
        self.thread: disnake.Thread = thread
        self.reason: str = reason_created

    @disnake.ui.button(label="Close", style=disnake.ButtonStyle.blurple)
    async def ticket_close_button(self, button: disnake.ui.Button, interaction: disnake.Interaction) -> None:
        button.disabled = True ; button.style = disnake.ButtonStyle.red
        await interaction.response.edit_message(view=self)
        await interaction.send(
            f"<@&{MODERATOR_ROLE_ID}>",
            embed=disnake.Embed(
                title="Ticket Closed" ,description=self.reason ,colour=disnake.Color.red(), timestamp=datetime.now()
            )
            .set_footer(text=f"Closed by {interaction.author}", icon_url=interaction.author.avatar.url)
            .set_thumbnail(interaction.guild.icon.url),
        ); await self.thread.remove_user(self.author)
        await self.thread.edit(name=f"Closed-{str(self.author)}")
        await self.author.send(
            embed=disnake.Embed(
                title="Ticket Closed",
                description=f"Your ticket has been closed by {interaction.author.mention}",
                color=disnake.Color.red(),
                timestamp=datetime.now()
            ).set_thumbnail(interaction.guild.icon.url)
        )

    async def on_timeout(self):
        await self.thread.delete()
