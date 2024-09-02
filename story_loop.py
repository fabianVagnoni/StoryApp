""""This file generates a story"""

import openai
import json
import random
from image_gen import ImageGenerator

client = openai.OpenAI()

# Parameters
story = {}
time = 1000
genre = 'fantasy'
n_choices = 4
temp = 0.69
max_tks = 200
index = 0
samples = 3

# Main class
class StoryLoop:
    def __init__(self , max_tks , genre , temp , n_choices , samples , verbose=False):
        # Definition of the parameters
        self.story = {} # Dict that will contain the outputs of each GPT call
        self.genre = genre
        self.max_tks = max_tks
        self.temp = temp
        self.index = 0 # Keep track of how many iterations we have done
        self.n_choices = n_choices
        self.samples = samples
        self.choices = [] # List of the choices made by user
        self.story_text = [] # All the text of the story
        self.image_generator = ImageGenerator()
        self.verbose = verbose

    def __call__(self, *args, **kwargs):
        """This is the main function of the class. It implements the loop"""
        message = (f"Write the beginning of a interactive story of genre {self.genre}."
                           f"Give the reader {self.n_choices} possible actions to take to continue the story. "
                           f"Format the response as a JSON object with 'storyText' for the narrative introduction, "
                           f"'options' as an array of {self.n_choices} distinct choices for the user, and 'end' as a boolean indicating"
                           f" whether the story is concluded. The JSON should be well-formed and it should NOT be enveloped with three "
                           f"''' on each end and NOT include the word json NOR any ``` and it should be a SINGLE long string with "
                           f"NO escape characters. Please, limit your response to NO MORE THAN {self.max_tks-50} tokens. \n\nStart the story:")
        # Loop
        for i in range(self.samples):
            if self.verbose:
                print(f"Iteration: {i}\n")
            # Call GPT, give message and extract json with story & options
            json_string = self.gpt_call(message)
            # Update data given the json, get user's response & get new message for GPT
            message = self.update_data(json_string,i)
        # Generate image
        cn = self.generate_image()
        return self.story_text

    def gpt_call(self , message):
        """This function takes a message and returns the GPT answer for it as a json file"""
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=self.temp,
            max_tokens=self.max_tks
        )
        json_string = str(completion.choices[0].message.content)
        if self.verbose:
            print(f"Returned response by GPT\n")
            print(f"{json_string}\n\n\n")
        return json_string

    def update_data(self , json_string , i):
        """This function updates the data attributes of the class"""
        self.story[self.index] = json.loads(json_string) # New story data inserted into the dictionary
        self.index += 1 # Update index
        chosen_option = random.choice(range(n_choices)) # User's choice (provisional)
        self.choices.append(chosen_option) # Update choices taken

        if self.verbose:
            print(f"Story Text\n")
            print(self.story[self.index - 1]['storyText'])
            if i < samples - 1:
                print(f"{self.story[self.index - 1]['options']}\n")
                print(f"User chose: {self.story[self.index - 1]['options'][chosen_option]}\n\n\n")
            else:
                print(f"The End.")

        # Update story text depending on if there are more choices to take or the story is finished
        if i < samples - 1:
            self.story_text.extend(
                [self.story[self.index - 1]['storyText'], self.story[self.index - 1]['options'][chosen_option]])
        else:
            self.story_text.append(self.story[self.index - 1]['storyText'])

        # Update message depending on if it is going to be the final message or not
        if i < self.samples - 2:
            message = (f"Consider an interactive story that starts by '{self.story_text}'. It is an "
                       f"story for which the reader has chosen already some alternatives. "
                       f"Please, continue the story and give the reader {self.n_choices} possible actions to take to continue the story. "
                       f"Format the response as a JSON object with 'storyText' for the narrative introduction, 'options' as an array "
                       f"of {self.n_choices} distinct choices for the user, and 'end' as a boolean indicating whether the story is concluded. The "
                       f"JSON should be well-formed and it should NOT be enveloped with three ''' on each end and NOT include the word "
                       f"json NOR any ``` and it should be a SINGLE long string with NO escape characters. Ensure that the quotation marks"
                       f"are well placed for the string to be convertible into a json file directly. Please, limit your response to"
                       f"NO MORE THAN {self.max_tks - 50} tokens")
        else:
            if self.verbose and i == self.samples - 2:
                print(f"End of the story is being constructed")
            message = (f"Consider an interactive story that starts by '{self.story_text}'. It is an "
                       f"interactive story for which the reader has chosen already some alternatives. "
                       f"Please, write a definitive ending to the story in accordance to all the previous events and include no new options. "
                       f"Format the response as a JSON object with 'storyText' for the narrative introduction, 'options' as an array "
                       f"empty array, and 'end' as a boolean indicating whether the story is concluded, in this case yes. The "
                       f"JSON should be well-formed and it should NOT be enveloped with three ''' on each end and NOT include the word "
                       f"json NOR any ``` and it should be a SINGLE long string with NO escape characters. Ensure that the quotation marks"
                       f"are well placed for the string to be convertible into a json file directly. Please, limit your response to"
                       f"NO MORE THAN {self.max_tks - 50} tokens")
        return message

    def generate_image(self):
        """This method generates an image based on the story"""
        context = "".join(self.story_text)
        image_url = self.image_generator(context=context , client=client , verbose=self.verbose)
        if self.verbose:
            print(f'\nImage URL: {image_url}\n\n')
        return image_url



sg = StoryLoop(max_tks=max_tks,genre=genre,n_choices=n_choices,temp=temp,samples=samples,verbose=True)
st = sg()
print(f'This is the story text: \n{st}')
