from openai import OpenAI
import tkinter as tk
from tkinter import ttk

# Set your OpenAI API key here
# api_key = "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"
api_key=''
client = OpenAI(api_key=api_key)


# Function to start the chatbot
def chatbot():
    # Create a list to store all the messages for context
    messages = [{"role": "system", "content": "You are a helpful assistant."}]

    def send_message(event=None):
        user_input = user_entry.get()
        user_entry.delete(0, tk.END)
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=messages)

        chat_message = response.choices[0].message.content
        conversation_text.insert(tk.END, f"User: {user_input}\nBot: {chat_message}\n")
        messages.append({"role": "assistant", "content": chat_message})

        if user_input.lower() == "quit":
            user_entry.config(state=tk.DISABLED)

    conversation_text = tk.Text(root, wrap=tk.WORD, bg="white")
    conversation_text.pack(expand=True, fill="both")
    conversation_text.insert(tk.END, "Start chatting with the bot (type 'quit' to stop)!\n")

    user_entry = tk.Entry(root, width=50)
    user_entry.pack(pady=10)
    user_entry.bind("<Return>", send_message)

    send_button = tk.Button(root, text="Send", command=send_message, bg="green", fg="white", width=30)
    send_button.pack(pady=10)

# Function to generate questions
def chat_with_bot():
    # Create a list to store all the messages for context
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    questions_to_generate = 5
    current_question = 0

    def generate_question():
        nonlocal current_question
        if current_question < questions_to_generate:
            job_title = job_title_entry.get()
            job_title_entry.config(state=tk.DISABLED)

            user_response_label.config(text="User's Response:")
            user_response_entry.config(state=tk.NORMAL, width=70, font=("Arial", 12))
            generate_button.config(command=evaluate_answer)
            generate_button.config(text="Evaluate Answer")
            generate_button.config(bg="red", fg="white")

            messages.append({"role": "user", "content": f"User: generate a question on {job_title}."})
            response = client.chat.completions.create(model="gpt-3.5-turbo",
            messages=messages)

            question = response.choices[0].message.content
            conversation_text.insert(tk.END, f"Bot: {question}\n")
            current_question += 1
        else:
            conversation_text.insert(tk.END, "You've completed 5 questions. Please enter a new job title.\n")
            job_title_entry.config(state=tk.NORMAL)
            current_question = 0

    def evaluate_answer():
        user_response = user_response_entry.get()
        user_response_entry.delete(0, tk.END)
        messages.append({"role": "user", "content": user_response})

        # Add the rating prompt
        rating_prompt = "Evaluate the user's answer based on your knowledge on a scale from 1 to 5: "
        messages.append({"role": "assistant", "content": rating_prompt})

        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=messages)

        bot_rating = response.choices[0].message.content
        conversation_text.insert(tk.END, f"Bot's Rating: {bot_rating}\n")

        generate_question()

    conversation_text = tk.Text(root, wrap=tk.WORD, bg="white")
    conversation_text.pack(expand=True, fill="both")
    conversation_text.insert(tk.END, "Start chatting with the bot (type 'quit' to stop)!\n")

    job_title_label = tk.Label(root, text="Enter job title:", bg='lightgray')
    job_title_label.pack()
    job_title_entry = tk.Entry(root, width=50, font=("Arial", 12))
    job_title_entry.pack(pady=10)

    user_response_label = tk.Label(root, text="User's Response:", bg='lightgray')
    user_response_label.pack()
    user_response_entry = tk.Entry(root, state=tk.DISABLED, width=50, font=("Arial", 12), bg='lightgray')
    user_response_entry.pack(pady=10)

    generate_button = tk.Button(root, text="Generate Question", command=generate_question, bg="blue", fg="white", width=30)
    generate_button.pack(pady=10)

root = tk.Tk()
root.title("Chatbot and Questions Generator")
root.geometry("800x600")

# Create a frame for the buttons
button_frame = tk.Frame(root, bg="white")

# Function to create styled buttons
def create_styled_button(frame, text, command, width, height):
    button = tk.Button(frame, text=text, command=command, width=width, height=height)
    button.config(relief="flat", background="darkblue", foreground="white", font=("Times New Roman", 12, "bold"))
    return button

# Create styled buttons for Chatbot and Generate Questions
chatbot_button = create_styled_button(button_frame, "Open Chatbot", chatbot, width=30, height=3)
generate_questions_button = create_styled_button(button_frame, "Generate Questions", chat_with_bot, width=30, height=3)

# Pack the buttons in the frame
chatbot_button.pack(pady=10)
generate_questions_button.pack(pady=10)

# Place the button_frame at the center of the window
button_frame.place(relx=0.5, rely=0.5, anchor="center")

root.mainloop()




