from plumbum import cli, colors
from pyfiglet import Figlet
import questionary
import csv
import random
from datetime import datetime

import base64
from email.message import EmailMessage

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.compose']
creds = Credentials.from_authorized_user_file('token.json', SCOPES)

all_questions = []
with open('questions.csv', "r", encoding = "cp1251", errors='ignore') as f:
    freader = csv.reader(f)
    for row in freader:
        all_questions.append(row)

def print_banner(color, text):
    with colors[color]:
        print(Figlet(font='slant').renderText(text))

def few_trivia_questions(number):
    
    questions_to_ask = []
    for i in range(number):
        question_to_add = all_questions.pop(random.randint(1, len(all_questions)-1))
        questions_to_ask.append(question_to_add)
    score = 0
    user_answers_list = []
    for question_and_answer in questions_to_ask:
        choices = []
        for i in range(3):
            choices.append(all_questions[random.randint(1, len(all_questions)-1)][1])
        choices.insert(random.randint(0,3), question_and_answer[1]) 
        choice = questionary.select(question_and_answer[0], choices = choices).ask()
        user_answers_list.append(choice)
        if choice == question_and_answer[1]:
            score+=1
            print(f"Correct! Current score is {score}")
        elif choice != question_and_answer[1]:
            print(f"Oops! Wrong answer. The right answer is {question_and_answer[1]}. Current score is {score}")
    
    print_banner("LIGHT_SEA_GREEN", "Final score")
    print(f"out of {number} is:")
    percentage = score/number
    if percentage >= 0.7:
        print_banner("GREEN", str(score))
    elif percentage >= 0.4:
        print_banner("YELLOW", str(score))
    else:
        print_banner("RED", str(score))
    choice = questionary.select(
    "Would you like a copy of your responses emailed to you?",
    choices=[
        "Yes",
        "No"
    ]).ask()
    if choice == "Yes":
        receiver = input("Enter your email ID: ")
        user = receiver.partition("@")[0]
        content = f"Hello {user}. Today, you scored {score} out of {number} on my trivia quiz.\nHere's a list of the questions, thier correct answers and your responses:\n\n"
        for index, question_and_answer in enumerate(questions_to_ask):
            content += f"\nQuestion #{index+1}:\t{question_and_answer[0]}\n"
            content += f"Correct answer = {question_and_answer[1]}\n"
            content += f"Your answer = {user_answers_list[index]}\n"
        send_email(receiver, content)
    elif choice == "No":
        print("Okay. Have a nice day!")

def all_trivia_questions():
    score = 0
    user_answers_list = []
    for question_and_answer in all_questions[1:]:
        choices = []
        for i in range(3):
            choices.append(all_questions[random.randint(1, len(all_questions)-1)][1])
        choices.insert(random.randint(0,3), question_and_answer[1]) 
        choice = questionary.select(question_and_answer[0], choices = choices).ask()
        user_answers_list.append(choice)
        if choice == question_and_answer[1]:
            score+=1
            print(f"Correct! Current score is {score}")
        elif choice != question_and_answer[1]:
            print(f"Oops! Wrong answer. The right answer is {question_and_answer[1]}. Current score is {score}")
    
    print_banner("LIGHT_SEA_GREEN", "Final score")
    print(f"out of {len(all_questions)-1} is:")
    percentage = score/(len(all_questions)-1)
    if percentage >= 0.7:
        print_banner("GREEN", str(score))
    elif percentage >= 0.4:
        print_banner("YELLOW", str(score))
    else:
        print_banner("RED", str(score))
    choice = questionary.select(
    "Would you like a copy of your responses emailed to you?",
    choices=[
        "Yes",
        "No"
    ]).ask()
    if choice == "Yes":
        receiver = input("Enter your email ID: ")
        user = receiver.partition("@")[0]
        content = f"Hello {user}. Today, you scored {score} out of {len(all_questions)-1} on my trivia quiz.\nHere's a list of the questions, thier correct answers and your responses:\n\n"
        for index, question_and_answer in enumerate(all_questions[1:]):
            content += f"\nQuestion #{index+1}:\t{question_and_answer[0]}\n"
            content += f"Correct answer = {question_and_answer[1]}\n"
            content += f"Your answer = {user_answers_list[index]}\n"
        send_email(receiver, content)
    elif choice == "No":
        print("Okay. Have a nice day!")

    
def send_email(receiver, content):
    """Create and send an email message
    Print the returned  message id
    Returns: Message object, including message id

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """

    try:
        service = build('gmail', 'v1', credentials=creds)
        message = EmailMessage()

        message.set_content(content)

        message['To'] = receiver
        message['From'] = 'bezbakri@gmail.com'
        message['Subject'] = f"Trivia quiz results for quiz taken on {datetime.today().strftime('%Y-%m-%d')} at {datetime.today().strftime('%H:%M')}"

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
            .decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')
    except:
        print(F'An error occurred. You sure you had the right email?')
        send_message = None
    return send_message   


class quiz(cli.Application):
    def main(self):
        print_banner("MAGENTA", "Welcome to My Trivia Quiz")
        choice = questionary.select(
        "How many questions would you like to answer?",
        choices=[
            '5',
            '15',
            'All of the saved ones'
        ]).ask()
        if choice == '5':
            few_trivia_questions(5)
        elif choice == '15':
            few_trivia_questions(15)
        elif choice == "All of the saved ones":
            all_trivia_questions()



if __name__ == '__main__':
    quiz()