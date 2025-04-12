import asyncio
from openai import OpenAI


async def get_openai_response(prompt: str) -> str:
    '''
    This function inference OpenAI using the prompt provided
    '''

    def call_openai():
        client = OpenAI()
        try:
            response = client.responses.create(
                model="gpt-4o-mini",
                input=prompt
            )
            return response.output_text.strip()
        except Exception as e:
            print("An error occurred:", e)
            raise e

    return await asyncio.to_thread(call_openai)
