from .data import icons


import discord


from io import BytesIO


class Menu(discord.ui.View):
    def __init__(self, infos, embeds, options, map, selects: bool = True):
        super().__init__(timeout=None)
        self.infos = infos
        self.embeds = embeds
        self.options = options
        self.map = map

        with BytesIO() as image_binary:
            self.map.save(image_binary, 'PNG')
            image_binary.seek(0)
            self.ru_map = discord.File(fp=image_binary, filename=f'map.png')

        if selects:
            self.add_item(SelectMenu(self.infos, self.embeds, self.options, self.map))
        
        self.add_item(discord.ui.Button(emoji="<:icons_link:1005031799208026196>", label="M'y rendre", url=f"https://www.google.fr/maps/dir//{self.infos.coords.lat},{self.infos.coords.long}/@{self.infos.coords.lat},{self.infos.coords.long},18.04", row=1))


    @discord.ui.button(emoji="<:icons_info:1005031802114674760>", label="Informations", style=discord.ButtonStyle.gray, row=1)
    async def informations(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.infos.mail == "":
            mail = ""
        else:
            mail = f"\n**`•` Courriel**: `{self.infos.mail}`"
        
        if self.infos.acces.bus == []:
            bus = ""
        else:
            bus = f"\n╰ {icons['bus']} **Bus**: `{', '.join(self.infos.acces.bus)}`"

        if self.infos.acces.pmr == []:
            pmr = ""
        else:
            pmr = f"\n╰ {icons['pmr']} **PMR**: `Accessible aux personnes à mobilité réduite`"

        if self.infos.acces.tram == []:
            tram = ""
        else:
            tram = f"\n╰ 🚋 **Tram**: `{', '.join(self.infos.acces.tram)}`"

        if self.infos.wifi:
            wifi = f"\n**`•` {icons['wifi']} Wifi**: `Disponible`"
        else:
            wifi = ""

        if self.infos.paiement.izly:
            izly = f"\n**`•` {icons['izly']} IZLY**: `Disponible`"
        else:
            izly = ""

        if self.infos.paiement.cb:
            cb = f"\n**`•` {icons['cb']} Carte Bancaire**: `Disponible`"
        else:
            cb = ""
        
        if self.infos.horaires.midi_cafet != "":
            cafet = f"\n╰ **Cafétéria**: `{self.infos.horaires.midi_cafet}`"
        else:
            cafet = ""
        
        embed=discord.Embed(title=f"{self.infos.nom}", description=f"**`•` Campus**: `{self.infos.zone}`\n**`•` Adresse**: `{self.infos.adresse}, {self.infos.cp} {self.infos.ville}`{wifi}\n\n**`•` Téléphone**: `{self.infos.tel}`{mail}", color=interaction.client.color, url=self.infos.url)
        embed.add_field(name=f"Horraires:", value=f"╰ **Self**: `{self.infos.horaires.midi_self}`{cafet}")
        embed.add_field(name=f"Paiements:", value=f"{cb}{izly}", inline=False)
        embed.add_field(name=f"Accès:", value=f"{pmr}{bus}{tram}", inline=False)
        embed.set_thumbnail(url=interaction.client.avatar_url)
        embed.set_image(url=f"attachment://map.png")
        embed.set_footer(text=interaction.client.footer_text, icon_url=interaction.client.avatar_url)
        return await interaction.response.send_message(embed=embed, ephemeral=True, file=self.ru_map)


    @discord.ui.button(emoji="<:icons_question:1005033387226058803>", style=discord.ButtonStyle.gray, row=1)
    async def question(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed=discord.Embed(title=f"{self.infos.nom}", description=f"**`•` Le Menu peut changé à n'importe quel moment en fonction des stocks et due à des évènements imprévus!**\n\n\nCROUStillant - Programmer par `Polsulpicien#5020`. Serveur officiel: https://discord.gg/tFr2B6EezM.\n\n**Ce bot n'est pas affilié avec 'Crous' !**", color=interaction.client.color, url=self.infos.url)
        embed.set_footer(text=interaction.client.footer_text, icon_url=interaction.client.avatar_url)
        return await interaction.response.send_message(embed=embed, ephemeral=True)



class SelectMenu(discord.ui.Select):
    def __init__(self, infos, embeds, options, map):
        super().__init__(placeholder="Select a Date", min_values=1, max_values=1, options=options, row=0)
        self.infos = infos
        self.embeds = embeds
        self.options = options
        self.map = map

    async def callback(self, interaction: discord.Interaction):
        return await interaction.response.send_message(embed=self.embeds[int(interaction.data['values'][0])], ephemeral=True, view=Menu(self.infos, self.embeds, self.options, self.map, False))