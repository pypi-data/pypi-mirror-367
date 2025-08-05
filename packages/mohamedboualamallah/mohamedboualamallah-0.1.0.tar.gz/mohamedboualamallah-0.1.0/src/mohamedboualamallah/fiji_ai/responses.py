def ai_response(prompt, subprompt, model):
    from google import genai

    if model == 1:
        model = "gemini-2.0-flash"
    elif model == 2:
        model = "gemini-2.5-pro"
    else:
        raise ValueError("Invalid model specified. Use 1 for lightweight(best for chats) or 2 for heavyweight(best for commands).")

    client = genai.Client(api_key="AIzaSyB95OrULLI8fes0mdSxlYDoH5IECwNJ5Ak")

    response = client.models.generate_content(
        model=model,
        contents=subprompt + prompt,
    )

    return response.text