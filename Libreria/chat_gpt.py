import openai

API_KEY = "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"


def chat_with_gpt(prompt):
    client = openai.OpenAI(api_key=API_KEY)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content


#chat_with_gpt('cual es el numero de la empresa Celerix en la ciudad de itagui')