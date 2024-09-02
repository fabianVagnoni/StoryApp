""""This file generates images from the story text"""

class ImageGenerator:
    def __call__(self, context , client , verbose):
        """This method returns the url of an image inspired in the story"""
        summary = self.summarizer(context , client)
        if verbose:
            print(f'\nSummary: {summary}\n\n')
        image_url = self.drawer(summary , client)
        return image_url

    def summarizer(self, context, client):
        """This method summarizes the story"""
        message = (f'This is the start of an interactive story for which the reader has already taken some choices:\n'
                   f'{context}\n'
                   f'Please, summarize the text in the story in minimum 5 lines and a maximum of 5.')
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": message
                }
            ]
        )
        return str(completion.choices[0].message.content)Remove-Item -Recurse -Force .git


    def drawer(self , context, client):
        message = (f'This is the summary of the beginning of an interactive story:\n'
                   f'{context}\n'
                   f'Please, generate an image that represents this scene.')
        response = client.images.generate(
            model="dall-e-3",
            prompt=message,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return image_url
