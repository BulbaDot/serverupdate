from flask import Flask, request, send_file
import azure.cognitiveservices.speech as speechsdk
import openai
from azure.storage.blob import BlobServiceClient
import json
import os
from io import BytesIO

app = Flask(__name__)

# Azure and OpenAI configuration
openai.api_key = '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'
speech_key = '198fc642bfcc4720b79d62a6f9aab480'
service_region = 'eastasia'
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_synthesis_voice_name = "en-GB-MaisieNeural"

blob_service_client = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;AccountName=cuppy98ec;AccountKey=JURxIoh1YNltN4WEzhcmFwclcrWbUaN9M+yu9+uCnaicC/Ayv87sy9OMjD/pyiaSM4ZhJqVWpxp1+AStDXw3oA==;EndpointSuffix=core.windows.net")
container_name = 'dot-blob'

@app.route('/process_audio', methods=['POST'])
def process_audio():
    # Save the received audio file
    audio_file = request.files['audio']
    audio_file_path = 'input_audio.wav'
    audio_file.save(audio_file_path)

    # Speech to text conversion
    audio_input = speechsdk.audio.AudioConfig(filename=audio_file_path)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)
    result = speech_recognizer.recognize_once()

    # Retrieve conversation history
 #   user_id = 'user_specific_identifier'  # Replace with actual logic to identify users
 #   blob_client = blob_service_client.get_blob_client(container=container_name, blob=user_id)
 #  try:
 #       history = json.loads(blob_client.download_blob().readall())
 #   except Exception:
 #       history = []

    # Generate response using ChatGPT
    user_input = result.text
    history.append({"role": "user", "content": user_input})
    response = openai.chat.completions.create(model="gpt-3.5-turbo", messages=history)
    response_text = response.choices[0].message.content

    # Text to speech conversion
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
    result = synthesizer.speak_text_async(response_text).get()
    stream = BytesIO(result.audio_data)
    output_audio_path = 'response_audio.wav'
    with open(output_audio_path, 'wb') as audio_file:
        audio_file.write(stream.read())

    # Update conversation history
    history.append({"role": "assistant", "content": response_text})
    blob_client.upload_blob(json.dumps(history), overwrite=True)

    # Return audio response
    return send_file(output_audio_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
