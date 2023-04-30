
import disnake
from disnake.ext import commands
from datetime import datetime
from core.utils import HelperCog
from core.constants import RoleID , ChannelID
MODERATOR_ROLE_ID = RoleID.MODERATOR
TICKET_CHANNEL_ID = ChannelID.TICKET_CHANNEL_ID
class ticket(HelperCog):
    """tickets"""

    # Update ticket name when user changes name
    @commands.Cog.listener()
    async def on_member_update(self , before : disnake.Member , after : disnake.Member):
        username_before : str = str(before)
        username_after : str = str(after)
        if username_before != username_after:
            ticket_channel : disnake.TextChannel = self.bot.get_channel(TICKET_CHANNEL_ID) or await self.bot.fetch_channel(TICKET_CHANNEL_ID)
            thread : disnake.Thread = [threads for threads in ticket_channel.threads if threads.name.split("-")[1] == username_before][0]
            thread_name = thread.name.split("-")[0]+'-'
            if thread:
             await thread.edit(name=thread_name+username_after)
             await thread.send(
                 embed = disnake.Embed(
                 title = "Changed thread name",
                 color = disnake.Color.blurple(),
                 timestamp = datetime.now()
                 ).add_field("Before",thread_name+username_before).add_field("After",thread_name+username_after)
             )
    #Gen ticket system
    @commands.command()
    @commands.has_role(RoleID.MODERATOR)
    async def setupticket(self, ctx:commands.Context , channel : disnake.TextChannel):

        await ctx.reply(f"Created ticket system in {channel.mention}")
        await channel.send(
            embed= disnake.Embed(
            title = "Open ticket",
            description = "Click on the button below for opening a ticket.",
            color = disnake.Color.blurple()
            ),
            view=TicketButton())


class TicketButton(disnake.ui.View):

    def __init__(self)  -> None:
        super().__init__(timeout = None)
        

    @disnake.ui.button(label="Create ticket", style=disnake.ButtonStyle.blurple)
    async def create_button(
       self, 
       button: disnake.ui.Button, 
       interaction: disnake.Interaction
       ) -> None:
      
      if str(interaction.author) not in [name.name.split('-')[1] for name in interaction.channel.threads]:

        thread = await interaction.channel.create_thread(
           name = str(interaction.author),
           type = disnake.ChannelType.private_thread
           )
        
        await interaction.response.send_message(
           
           embed=disnake.Embed(
           description=f"Created ur ticket {thread.mention}",
           color=disnake.Color.green(),
           timestamp=datetime.now()),
           ephemeral=True)
        
        await thread.send(
           interaction.author.mention,
           embed = disnake.Embed(
            description= "Why are u creating a ticket? \n Kindly select any option below.",
            color = disnake.Color.yellow()
           ),
           view = ChoiceButtons(thread,interaction.author)
           )

      else:
         await interaction.response.send_message(
            embed = disnake.Embed(
             description = "You already have a ticket active",
             color = disnake.Color.red()
            ),
            ephemeral=True
            )
         



         
class ChoiceButtons(disnake.ui.View):

    def __init__(self , thread , author)  -> None:
        super().__init__(timeout = 120)
        self.author : disnake.Member = author
        self.thread : disnake.Thread = thread
        self.activity : bool = False
    @disnake.ui.button(label="Report", style=disnake.ButtonStyle.blurple)
    async def report_button(
       self, 
       button: disnake.ui.Button, 
       interaction: disnake.Interaction
       ) -> None: 
        if self.author == interaction.author:
         await interaction.response.edit_message(
            interaction.author.mention,
            embed = disnake.Embed(
            title = "Report",
            description="What do u want a report?",
            color = disnake.Color.yellow()
            ),
            view = ReportButtons(self.thread,interaction.author)
            )
         self.activity = True
        
    @disnake.ui.button(label="Order", style=disnake.ButtonStyle.blurple)
    async def order_button(
       self, 
       button: disnake.ui.Button, 
       interaction: disnake.Interaction
       ) -> None: 
           if self.author == interaction.author:
            await interaction.response.edit_message(
                f"{interaction.author.mention},<@&{MODERATOR_ROLE_ID}>",
                embed = disnake.Embed(
                title = "Ticket opened",
                description = "Order",
                color = disnake.Color.green(),
                timestamp = datetime.now()
                ).set_thumbnail(interaction.author.avatar.url).set_author(name=interaction.author),
                view = TicketCloseButtons(self.thread,interaction.author)
                
            )
            await self.thread.edit(name=f"O-{str(interaction.author)}")
            self.activity = True
    async def on_timeout(self):
       if not self.activity:
        await self.thread.delete()




class ReportButtons(disnake.ui.View):

    def __init__(self , thread , author)  -> None:
        super().__init__(timeout = 120)
        self.author : disnake.Member = author
        self.thread : disnake.Thread = thread
        self.activity : bool = False

    async def edit_thread(self , content):

        await self.thread.edit(name=content+self.thread.name)
        self.activity = True

    @disnake.ui.button(label="User", style=disnake.ButtonStyle.blurple)
    async def report_button(
       self, 
       button: disnake.ui.Button, 
       interaction: disnake.Interaction
       ) -> None: 
           if self.author == interaction.author:
            await interaction.response.edit_message(
                f"{interaction.author.mention},<@&{MODERATOR_ROLE_ID}>",
                embed = disnake.Embed(
                title = "Ticket opened",
                description = "User Report",
                color = disnake.Color.green(),
                timestamp = datetime.now()
                ).set_thumbnail(interaction.author.avatar.url).set_author(name=interaction.author),
                view = TicketCloseButtons(self.thread,interaction.author)
                )
            await self.edit_thread("UR-")



    @disnake.ui.button(label="Issue", style=disnake.ButtonStyle.blurple)
    async def order_button(
       self, 
       button: disnake.ui.Button, 
       interaction: disnake.Interaction
       ) -> None: 
           if self.author == interaction.author:
            await interaction.response.edit_message(
                f"{interaction.author.mention},<@&{MODERATOR_ROLE_ID}>",
                embed = disnake.Embed(
                title = "Ticket opened",
                description = "Issue Report",
                color = disnake.Color.green(),
                timestamp = datetime.now()
                ).set_thumbnail(interaction.author.avatar.url).set_author(name=interaction.author),
                view = TicketCloseButtons(self.thread,interaction.author)
                )
            await self.edit_thread("IR-")
    async def on_timeout(self):
      if not self.activity:
        await self.thread.delete()


class TicketCloseButtons(disnake.ui.View):

    def __init__(self , thread, author)  -> None:
        super().__init__(timeout = 604800)
        self.author : disnake.Member = author
        self.thread : disnake.Thread = thread

    @disnake.ui.button(label="Close", style=disnake.ButtonStyle.blurple)
    async def ticket_close_button(
       self, 
       button: disnake.ui.Button, 
       interaction: disnake.Interaction
       ) -> None: 
            await interaction.edit_original_message(view=None)
            await interaction.response.send_message(
                f"<@&{MODERATOR_ROLE_ID}>",
                embed = disnake.Embed(
                title = "Ticket Closed",
                color = disnake.Color.blurple(),
                timestamp = datetime.now()
                ).set_footer(text=f"Closed by {interaction.author}",icon_url=interaction.author.avatar.url),
                )
            await self.thread.remove_user(self.author)
            await self.thread.edit(name=f"Closed-{str(interaction.author)}")
    async def on_timeout(self):
        await self.thread.delete()
