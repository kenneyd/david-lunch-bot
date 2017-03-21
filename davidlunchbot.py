import os
import time
import random
from maps import mapsClient
from yaml import load
from slackclient import SlackClient


class LunchBot:
    """For using google maps to get lunch reccomendations over slack"""

    def __init__(self):
        """Setup slack client, etc."""

        # starterbot's ID as an environment variable
        self.BOT_ID = os.environ.get("BOT_ID")
        self.BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')

        self.AT_BOT = "<@" + self.BOT_ID + ">"

        # instantiate Slack client
        self.slack_client = SlackClient(self.BOT_TOKEN)

        self.EXAMPLE_COMMAND = "lunch?"

        # 1 second delay beterrn reading from firehouse
        self.READ_WEBSOCKET_DELAY = 1

        foods_file = "food_options.yaml"
        self.food_choices = load(open(foods_file, 'r'))

    def runBot(self):
        """"""

        # 1 second delay beterrn reading from firehouse
        if self.slack_client.rtm_connect():
            print("Lunchbot connected and running!")
            while True:
                command, channel = self.parse_slack_output(self.slack_client.rtm_read())
                if command and channel:
                    self.handle_command(command, channel)
                time.sleep(self.READ_WEBSOCKET_DELAY)
        else:
            print("Can't connect to slack, have you set up environment variables for BOT_ID and SLACK_BOT_TOKEN ?")

    def getRandomRecomendation(self):

        choice = random.choice(self.food_choices)
        response = """I'm thinking %s Here's some nearby places""" % choice['name']

        places = mapsClient().placesSearch(keyword=choice['search_term'])
        for place in places:
            response += "\n<%s|%s> - %s away" % (place['url'], place['name'], place['distance'])

        return response

    def handle_command(self, command, channel):

        if self.AT_BOT.lower() in command:
            # parse text here for keywords

            # We seperate the @bot, and then take the first work given
            command = command.split(self.AT_BOT.lower())[1].split()[0]
            if command:
                places = mapsClient().placesSearch(keyword=command)
                if places:
                    response = "I found these restaurants for %s " % command
                    for place in places:
                        response += "\n<%s|%s> - %s away" % (place['url'], place['name'],
                                                             place['distance'])
                else:
                    response = "I couldn't find anything nearby for %s" % command
            else:
                response = self.getRandomRecomendation()

        elif self.EXAMPLE_COMMAND in command:
            response = self.getRandomRecomendation()

        self.slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

    def parse_slack_output(self, slack_rtm_output):
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and (self.EXAMPLE_COMMAND in output['text']
                                                    or self.AT_BOT in output['text']):
                    return output['text'].lower(), output['channel']
        return None, None


if __name__ == "__main__":

    LunchBot().runBot()
