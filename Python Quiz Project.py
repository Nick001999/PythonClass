import tkinter as tk
import requests
import html
from random import shuffle
from tkinter import messagebox


def get_questions(amount=10, question_type=None):
    url = "https://opentdb.com/api.php"
    params = {
        "amount": amount,
        "type": question_type
    }
    response = requests.get(url, params=params)
    return response.json()["results"]


class QuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Quiz Application")
        self.master.geometry("400x300")

        # Получить и объединить вопросы двух типов
        multiple_choice_questions = get_questions(amount=5, question_type='multiple')
        true_false_questions = get_questions(amount=5, question_type='boolean')
        self.questions = multiple_choice_questions + true_false_questions
        shuffle(self.questions)  # перемешать вопросы

        self.current_question = 0
        self.score = 0

        self.question_label = tk.Label(self.master, text="", wraplength=300, justify="center")
        self.question_label.pack(pady=10)

        self.options_frame = tk.Frame(self.master)
        self.options_frame.pack(pady=5)

        self.option_buttons = []
        for i in range(4):
            button = tk.Button(self.options_frame, text="", command=lambda i=i: self.check_answer(i), width=20)
            button.grid(row=i // 2, column=i % 2, padx=5, pady=5)
            self.option_buttons.append(button)

        self.update_question()

    def update_question(self):
        question_data = self.questions[self.current_question]
        question_text = html.unescape(question_data["question"])
        correct_answer = question_data["correct_answer"]
        options = question_data["incorrect_answers"] + [correct_answer]
        shuffle(options)

        self.correct_option = options.index(correct_answer)
        self.question_label.config(text=f"{self.current_question + 1}. {question_text}")

        if question_data["type"] == "boolean":
            self.option_buttons[0].config(text="True")
            self.option_buttons[1].config(text="False")
            self.option_buttons[2].config(text="", state=tk.DISABLED)
            self.option_buttons[3].config(text="", state=tk.DISABLED)
        else:
            for i, option in enumerate(options):
                self.option_buttons[i].config(text=html.unescape(option), state=tk.NORMAL)

    def check_answer(self, chosen_option):
        if chosen_option == self.correct_option:
            self.score += 1

        self.current_question += 1

        if self.current_question < len(self.questions):
            self.update_question()
        else:
            messagebox.showinfo("Quiz Completed", f"Your score is {self.score}/{len(self.questions)}")
            self.master.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()