from .data import icons


import discord


class Menu(discord.ui.View):
    def __init__(self, infos, embeds, options, selects: bool = True):
        super().__init__(timeout=None)
        self.infos = infos
        self.embeds = embeds
        self.options = options

        if selects:
            self.add_item(SelectMenu(self.infos, self.embeds, self.options))
        
        self.add_item(discord.ui.Button(emoji="<:icons_link:1005031799208026196>", label="M'y rendre", url=f"https://www.google.fr/maps/dir//{self.infos.coords.lat},{self.infos.coords.long}/@{self.infos.coords.lat},{self.infos.coords.long},18.04", row=1))


    @discord.ui.button(emoji="<:icons_info:1005031802114674760>", label="A propos de CROUStillant", style=discord.ButtonStyle.gray, row=1)
    async def question(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed=discord.Embed(title=f"{self.infos.nom}", description=f"**`•` Le Menu peut changé à n'importe quel moment en fonction des stocks et due à des évènements imprévus!**\n\n\nCROUStillant - Programmer par `Polsulpicien#5020`. Serveur officiel: https://discord.gg/tFr2B6EezM.\n\n**Ce bot n'est pas affilié avec 'Crous' !**", color=interaction.client.color, url=self.infos.url)
        embed.set_footer(text=interaction.client.footer_text, icon_url=interaction.client.avatar_url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)



class SelectMenu(discord.ui.Select):
    def __init__(self, infos, embeds, options):
        super().__init__(placeholder="Select a Date", min_values=1, max_values=1, options=options, row=0)
        self.infos = infos
        self.embeds = embeds
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        return await interaction.response.send_message(embed=self.embeds[int(interaction.data['values'][0])], ephemeral=True, view=Menu(self.infos, self.embeds, self.options, False))