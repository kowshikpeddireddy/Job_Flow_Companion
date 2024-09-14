import cv2
from deepface import DeepFace
from openai import OpenAI
import speech_recognition as sr
import pyttsx3
import threading
import tkinter as tk
from tkinter import ttk

# Global variables
emotion_frequencies = {}

api_key=''
# Initialize OpenAI client
client = OpenAI(api_key=api_key)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice and Webcam Interaction")
        self.root.geometry("800x600")

        self.start_button = ttk.Button(root, text="Start Interaction", command=self.start_interaction, style='TButton',
                                       padding=(20, 30))

        self.start_button.pack(pady=20)

        self.info_label = tk.Label(root, text="")
        self.info_label.pack()

        self.emotion_label = tk.Label(root, text="")
        self.emotion_label.pack()

        # Variable to track thread status
        self.voice_thread_running = False
        self.webcam_thread_running = False

    def start_interaction(self):
        self.clear_labels()
        self.display_info("Please introduce yourself:")

        # Start a thread for voice interaction
        self.voice_thread_running = True
        voice_thread = threading.Thread(target=self.voice_interaction)
        voice_thread.start()

        # Start a thread for webcam
        self.webcam_thread_running = True
        webcam_thread = threading.Thread(target=self.run_webcam)
        webcam_thread.start()

        # Periodically check thread status without blocking the main loop
        self.root.after(100, self.check_thread_status)

    def check_thread_status(self):
        if self.voice_thread_running or self.webcam_thread_running:
            self.root.after(100, self.check_thread_status)
        else:
            # Threads have finished, continue with the rest of the logic
            self.print_most_frequent_emotion()
            self.print_emotion_frequencies()


    def clear_labels(self):
        self.info_label.config(text="")
        self.emotion_label.config(text="")

    def display_info(self, info):
        self.info_label.config(text=info)
        self.root.update()

    def get_user_voice_answer(self):
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            self.display_info("Speak now...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            user_answer = recognizer.recognize_google(audio)
            self.display_info(f"User's Answer: {user_answer}")
            return user_answer
        except sr.UnknownValueError:
            self.display_info("Sorry, I couldn't understand the voice. Please try again.")
            return self.get_user_voice_answer()
        except sr.RequestError as e:
            self.display_info(f"Error connecting to Google Speech Recognition service: {e}")
            return None

    def get_gpt35turbo_suggestions(self, question, user_answer):
        prompt = f"{question}\nPlease provide creative suggestions on how to improve the response and any grammar corrections if needed:\n{user_answer}"
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}],
        max_tokens=150)
        return response.choices[0].message.content.strip()

    def text_to_speech(self, text, rate=150):
        engine = pyttsx3.init()
        engine.setProperty('rate', rate)
        engine.say(text)
        engine.runAndWait()

    def voice_interaction(self):
        introduction_question = "Please introduce yourself:"
        user_answer = self.get_user_voice_answer()
        suggestions = self.get_gpt35turbo_suggestions(introduction_question, user_answer)
        self.display_info(f"\nSuggestions for improving the user's sentence:\n{suggestions}")
        self.text_to_speech(suggestions)
        self.voice_thread_running = False  # Indicate that the voice thread has finished

    def run_webcam(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            self.display_info("Error: Could not open webcam.")
            return

        while True:
            ret, frame = cap.read()

            if not ret:
                self.display_info("Error: Can't receive frame (stream end?). Exiting ...")
                break

            emotion = self.recognize_expression_from_frame(frame)

            cv2.putText(frame, emotion, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow('Facial Expression Recognition', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        self.webcam_thread_running = False  # Indicate that the webcam thread has finished

    def recognize_expression_from_frame(self, frame):
        try:
            results = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            if isinstance(results, list):
                for result in results:
                    emotion = result['dominant_emotion']
                    if emotion == "neutral":
                        emotion = "confident"
                    emotion_frequencies[emotion] = emotion_frequencies.get(emotion, 0) + 1
            else:
                emotion = results['dominant_emotion']
                if emotion == "neutral":
                    emotion = "confident"
                emotion_frequencies[emotion] = emotion_frequencies.get(emotion, 0) + 1

        except Exception as e:
            self.display_info(f"Error in emotion detection: {e}")

        return emotion

    def print_most_frequent_emotion(self):
        if not emotion_frequencies:
            self.display_info("No emotions were detected.")
            return

        most_frequent_emotion = max(emotion_frequencies, key=emotion_frequencies.get)
        self.emotion_label.config(text=f"The most frequent emotion detected was: {most_frequent_emotion}")
        self.root.update()

    def print_emotion_frequencies(self):
        self.display_info(emotion_frequencies)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()