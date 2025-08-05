def gemeniresponse(prompt, subprompt, model):
    from google import genai

    client = genai.Client(api_key="YOUR_API_KEY_HERE")

    response = client.models.generate_content(
        model=model,
        contents=subprompt + prompt,
    )

    return response.text