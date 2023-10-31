import discord
from discord.ext import commands
import requests
import asyncio
from fuzzywuzzy import fuzz
import json

class guesser(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        with open('episodes.json', 'r') as file:
            self.episodes_data = json.load(file)

    @commands.hybrid_command(name='ponyguesser', description="Play Some Pony Guesser")
    async def guess_image(self, ctx):
        try:
            api_url = 'https://ponyguessr.com/api/resource/gen?runId&subtitles=false&audioLength=10&resourceType=frame'

            response = requests.get(api_url)
            data = response.json()

            if 'id' in data:
                image_id = data['id']
                image_url = f'https://ponyguessr.com/api/resource/get/{image_id}.png'
                await ctx.send(image_url)
                await ctx.send(f'Guess the episode by typing the episode name or something similar!')

                def check(msg):
                    return msg.author == ctx.author and msg.channel == ctx.channel

                try:
                    user_guess = await self.bot.wait_for('message', check=check, timeout=500)
                    user_input = user_guess.content

                    max_ratio = 0
                    matched_episode = ""
                    matched_season = ""
                    matched_episode_number = ""

                    for episode_name, episode_code in self.episodes_data['episodes'].items():
                        ratio = fuzz.token_set_ratio(user_input, episode_name)
                        if ratio > max_ratio:
                            max_ratio = ratio
                            matched_episode = episode_code
                            matched_season, matched_episode_number = episode_code.split('E')
                            trash, matched_season_number = matched_season.split('S')

                    if max_ratio > 90:  # Adjust the similarity threshold as needed # but 90 seems to be perfect :D
                        check_url = f'https://ponyguessr.com/api/resource/{image_id}/check?season={matched_season_number}&episode={matched_episode_number}'
                        check_response = requests.get(check_url)
                        check_data = check_response.json()

                        if check_data['correct']:
                            await ctx.send(f'Congratulations! You guessed correctly. It is from Season {matched_season}, Episode {matched_episode_number}.')
                        else:
                            await ctx.send(f'Sorry, your guess was incorrect.(Season: {matched_season_number}, Episode: {matched_episode_number})')
                            await ctx.send(f'The correct episode is from Season {check_data["season"]}, Episode {check_data["episode"]}.')
                    else:
                        await ctx.send("Sorry, couldn't find a matching episode. Please try again.")

                except asyncio.TimeoutError:
                    await ctx.send('Time is up! Please try again.')

            else:
                await ctx.send('Unable to fetch image ID')

        except Exception as e:
            print(f'Error occurred: {e}')
            await ctx.send('Error fetching image')


def setup(bot):
    bot.add_cog(guesser(bot))
