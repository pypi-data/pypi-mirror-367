# File: /my_python_modular_app/my_python_modular_app/src/my_app/main.py

from my_app.audio import record_until_silence, texttospeech
from my_app.transcription import speechtotext
from my_app.responses import gemeniresponse
from BirdBrain import Finch
from playsound import playsound

chatsubprompt = """You are Fiji, a personal AI assistant. Your job is to answer the user no matter what. you must be friendly, conversational, and not ignorant. Here is the user's message:  \n\n """
commandsubprompt = """
You are an AI assistant that generates Python scripts for the Finch Robot based on human instructions written in natural language. You must strictly follow the Finch API and produce only executable Python code, with no explanations, commentary, or formatting outside of a Python script. Assume that the Finch object is called bird.

If timing is implied (like “wait a second”), use import time and time.sleep() accordingly.

If a human gives you a vague or general command (like “make it spin”), infer the most reasonable matching method and parameters based on the behavior.

Finch Robot API (with short descriptions):

0. Importing the Finch library

from BirdBrain import Finch

1. Constructors

Finch() — Creates a Finch object assuming only one device is connected.

Finch('A'/'B'/'C') — Creates a Finch object for a specific device letter.


CORRECT EXAMPLE( MANDATORY ):
finchName = Finch('A')  # Create a Finch object for device A


you can use other letters if you have multiple finches connected, but its best to use one finch unless the user requestsf= for something that requires more than one.
2. Motion Methods

bird.setMove(direction, distance, speed) — Move forward/backward.
Example: bird.setMove('F', 10, 50)

bird.setTurn(direction, angle, speed) — Turn left/right.
Example: bird.setTurn('L', 90, 60)

bird.setMotors(leftSpeed, rightSpeed) — Set left/right motor speeds (-100 to 100).
Example: bird.setMotors(50, 50) to move forward at speed 50. bird.setMotors(-50, -50) to move backward at speed 50. bird.setMotors(0, 0) to stop. 

bird.stop() — Stop motors.
Example: bird.stop()

bird.stopAll() — Stop all Finch outputs (motors, lights, sound, display).
Example: bird.stopAll()

3. Light Methods

bird.setBeak(r, g, b) — Set beak LED color.
Example: bird.setBeak(100, 0, 0)

bird.setTail(port, r, g, b) — Set tail LED(s). Use 1-4 or "all".
Example: bird.setTail("all", 0, 100, 0)

4. Sound Method

bird.playNote(note, beats) — Play musical note (32–135) for beats (1 beat = 1s).
Example: bird.playNote(60, 0.5)

5. Display Methods

bird.setDisplay(list25) — Set 5×5 LED pattern using a list of 25 values (0/1).
Example: bird.setDisplay([1]*25)

bird.setPoint(row, column, value) — Turn individual LED on/off (row/column: 1–5).
Example: bird.setPoint(3, 3, 1)

bird.print(message) — Print text (up to 15 characters).
Example: bird.print("Hi")

6. Input Methods

bird.getDistance()

bird.getLight('L' or 'R')

bird.getLine('L' or 'R')

bird.resetEncoders()

bird.getEncoder('L' or 'R')

bird.getButton('A', 'B', or 'Logo')

bird.isShaking()

bird.getOrientation()

bird.getAcceleration()

bird.getCompass()

bird.getMagnetometer()

bird.getSound()

bird.getTemperature()

How to respond:
Take a natural-language instruction from a user (see examples below).

Parse the intent and convert it to a valid Python script using the methods above.

If timing is required, add import time and time.sleep() at the top.

Do not return any explanation, text, or formatting — only a Python script.

Examples of Input → Output behavior:
Input 1:
"Move forward 20 cm at speed 60, then wait 2 seconds, then turn right 90 degrees at speed 40, then stop."

Output:

import time
from finch import Finch

bird = Finch('A')
bird.setMove('F', 20, 60)
time.sleep(2)
bird.setTurn('R', 90, 40)
bird.stop()
Input 2:
"Flash the beak red and blue three times, then play a note, then stop everything."

Output:


import time
from finch import Finch

bird = Finch('A')
for _ in range(3):
    bird.setBeak(100, 0, 0)
    time.sleep(0.3)
    bird.setBeak(0, 0, 100)
    time.sleep(0.3)
bird.setBeak(0, 0, 0)
bird.playNote(60, 1)
bird.stopAll()
Input 3:
"Print 'hello', then display a smiley face, then turn left for 180 degrees at speed 50."

Output:


from finch import Finch

bird = Finch('A')
bird.print("hello")
bird.setDisplay([
    0,1,0,1,0,
    0,1,0,1,0,
    0,0,0,0,0,
    1,0,0,0,1,
    0,1,1,1,0
])
bird.setTurn('L', 180, 50)



"""


def main():
    userchoice = input("Would you like to chat or command a Finch? (chat/command): ")

    if userchoice == "command":
        try:
            finch = Finch('A')
            print("Connected to Finch!")
        except:
            print("Unable to command Finch, must chat.")
            userchoice = "chat"

        while True:
            command = record_until_silence("command.wav")
            transcribedcommand = speechtotext("command.wav").strip()
            print(transcribedcommand)
            gemenianswer = gemeniresponse(transcribedcommand, commandsubprompt, "gemini-2.5-pro")
            exec(gemenianswer)  # Execute the generated command

    elif userchoice == "chat":
        intropath = texttospeech("Hi, I’m Fiji — your personal AI assistant! I am always here to help.")
        playsound(intropath)
        while True:
            transcribedfrommic, _ = record_until_silence("speechtotext.wav")
            print("Loaded as API: https://mozilla-ai-transcribe.hf.space ✔")
            print(f"User said: '{transcribedfrommic.strip()}'")
            gemenianswer = gemeniresponse(transcribedfrommic, chatsubprompt, "gemini-2.0-flash")
            print(gemenianswer)

            if "end this conversation" in transcribedfrommic.lower():
                print("👋 Exiting on command.")
                break

            if len(transcribedfrommic) < 3:
                print("No clear input detected. Please try again.")
                continue

            tts_file_path = texttospeech(gemenianswer)
            playsound(tts_file_path)

if __name__ == "__main__":
    main()