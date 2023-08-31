import requests
import discord
from bs4 import BeautifulSoup
from discord.ext import commands

intents = discord.Intents.all()
intents.message_content = True
intents.typing = False
intents.presences = False

client = commands.Bot(command_prefix="?", intents=intents)

@client.command()
async def manga(ctx):
    global count

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    await ctx.reply("Enter the manga")
    while True:
        msg = await client.wait_for("message", check=check)
        msg = msg.content.replace(" ", "+")
        req = requests.get(f"https://mangapanda.in/search?q={msg}")
        soup = BeautifulSoup(req.content, "html.parser")

        mangas = soup.find("div", attrs={"class": "cate-manga"})
        anchor = mangas.find_all('a')
        keyword = "chapter"
        list = []
        for element in anchor:
            if keyword not in element.get('title', '').lower():
                list.append(element)

        href_values = [tag['href'] for tag in list[::2]]
        title = [tag['title'] for tag in list[::2]]
        if len(title) <= 0:
            await ctx.send("There is no manga with this name.")
            break
        elif len(title) == 1:
            count = 0
        else:
            for index, item in enumerate(title, start=1):
                await ctx.send(f"{index}.) {item.capitalize()}")
            await ctx.reply(f"Enter a number between 1 and {len(title)}")
            try:
                count = await client.wait_for("message", check=check)
                if int(count.content) == 0:
                    await ctx.send(f"Enter a number between 1 and {len(title)}")
                    break
                count = int(count.content)
                count -= 1
            except IndexError:
                await ctx.send(f"Please choose a number between 1 and {len(title)}")
                break
            except ValueError:
                await ctx.send("Invalid input. Please provide an integer.")
                break
        website = href_values[count]
        req2 = requests.get(f"{str(website)}")
        soup2 = BeautifulSoup(req2.content, "html.parser")
        chapter = soup2.findAll("div", attrs={"class": "col-xs-12 chapter"})
        list2 = []
        for x in chapter:
            chapter_links = x.find_all('a')
            list2.extend(chapter_links)

        href_values2 = [title['href'] for title in list2]
        try:
            ending_chapter = href_values2[0]
            ending_chapter = ending_chapter.split('-')
            ending_chapter = ending_chapter[-1]
            decimal_chapter_number = []
            for x in href_values2:
                chapter_numbers = x.split('-')[-1]
                if "." in chapter_numbers:
                    decimal_chapter_number.append(chapter_numbers)
            decimal_chapter_number = ', '.join(decimal_chapter_number[::-1])
            await ctx.send(f"Please choose a chapter between 1 and {ending_chapter}")
            if len(decimal_chapter_number) >= 1:
                await ctx.send(f"Please note there are some chapters that have decimals such as {decimal_chapter_number}")
            index_value = await client.wait_for("message", check=check)
            index_content = index_value.content
            try:
                number = index_content
                if "." in number:
                    if len(decimal_chapter_number) >= 1:
                        if str(float(number)) not in decimal_chapter_number:
                            await ctx.send("This isn't a chapter that is in this manga.")
                            break
                elif not number.isdigit():
                    await ctx.send("Please enter a valid number.")
                    break
                elif (float(number) > float(ending_chapter)) or (float(number) < 1):
                    await ctx.send("This number is not between the range given.")
                    break
            except ValueError:
                await ctx.send("Please enter a valid number.")
                break
            index_value = str(index_value.content)
            chz = href_values2[0]
            chz = chz.split('-')
            chz.pop()
            chz.append(str(index_value))
            chz = '-'.join(chz)
            await ctx.send(chz)
            try:
                html_page_req = requests.get(chz)
                html_page = BeautifulSoup(html_page_req.content, "html.parser")
                file_path = 'index.html'
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(str(html_page))
                file_to_send = discord.File(file_path)
                await ctx.send(file=file_to_send)
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")
                break
            finally:
                if file_to_send:
                    file_to_send.close()
                    break
        except IndexError:
            await ctx.send(f"Please choose a number between 1 and {len(href_values2)}")
            continue
        except ValueError:
            await ctx.send("Invalid input. Please provide an integer.")
            continue

client.run("MTEyODA3OTgzOTM0NjMxNTI3NA.GtT9L7.qtqfm271oip8cwyHEk_A-Hd8EMnJbTgvlzmA0M")
