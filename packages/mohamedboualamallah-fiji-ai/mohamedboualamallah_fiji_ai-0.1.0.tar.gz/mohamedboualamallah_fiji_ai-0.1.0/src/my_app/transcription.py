def speechtotext(audiopath):
    from gradio_client import Client, handle_file

    client = Client("mozilla-ai/transcribe")
    result = client.predict(
        dropdown_model_id="openai/whisper-tiny (Multilingual)",
        hf_model_id="",
        local_model_id="",
        audio=handle_file(audiopath),
        show_timestamps=False,
        api_name="/transcribe"
    )

    return result