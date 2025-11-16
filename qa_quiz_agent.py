# IMPORT LIBRARIES (Tools we need)
import streamlit as st          # Creates the web interface - makes buttons, text, etc.
import requests                 # Gets data from internet - like downloading files
import json                     # Handles data storage - saves and loads information
import os                       # Works with files - checks if files exist
import time                     # Adds delays - like waiting between questions
from dotenv import load_dotenv  # Loads secret keys - reads password files
from openai import OpenAI       # AI for explanations - connects to ChatGPT

# SETUP: Get API Key for AI
load_dotenv()  # Look for .env file and load secrets from it

# Try to get the API key from two places: .env file OR Streamlit secrets
api_key = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# Check if we have the key - if not, show error and stop
if not api_key:
    st.error("Missing API Key! Add OPENAI_API_KEY to .env file")  # Show error message
    st.stop()  # Stop the program - can't continue without key

# Create connection to OpenAI (ChatGPT) using the API key
client = OpenAI(api_key=api_key)

# FUNCTION: Get Quiz Questions
def fetch_questions(how_many=5):  # Function to download questions from internet
    """
    This function gets quiz questions from the internet
    - how_many: Number of questions to get (default is 5)
    """
    # Build the web address (URL) to get questions from Open Trivia Database
    url = f"https://opentdb.com/api.php?amount={how_many}&type=multiple"
    
    # Send request to website and get response
    response = requests.get(url)
    
    # Convert response to JSON format (like a dictionary)
    data = response.json()
    
    # Create empty list to store our organized questions
    question_list = []
    
    # Loop through each question in the results
    for item in data["results"]:
        # Add organized question to our list
        question_list.append({
            "question": item["question"],              # The question text
            "correct": item["correct_answer"],         # The right answer
            "options": item["incorrect_answers"] + [item["correct_answer"]],  # All choices mixed
            "category": item["category"],              # Topic like "History" or "Science"
            "difficulty": item["difficulty"]           # Easy, Medium, or Hard
        })
    
    # Return the list of questions
    return question_list

# SETUP: Quiz History File
LOG_FILE = "quiz_log.json"  # Name of file where we save quiz history

# Check if the history file already exists on computer
if os.path.exists(LOG_FILE):
    # File exists - open it and read the data
    with open(LOG_FILE, "r") as file:  # "r" means read mode
        quiz_history = json.load(file)  # Load existing history into memory
else:
    # File doesn't exist - create new empty list
    quiz_history = []

# PAGE TITLE AND DESCRIPTION
st.title("AI Quiz Master")  # Big title at top of page
st.write("Test your knowledge and get AI-powered explanations!")  # Description text

# INITIALIZE: Start New Quiz
# session_state remembers information even when page refreshes
# Check if "questions" exists in session_state
if "questions" not in st.session_state:
    # First time running - initialize everything
    st.session_state.questions = fetch_questions(5)  # Download 5 questions
    st.session_state.current_question = 0            # Start at first question (0 = first)
    st.session_state.points = 0                      # Start with zero points
    st.session_state.user_answers = []               # Empty list to save user's answers

# FUNCTION: Get AI Explanation
def get_explanation(question_text, correct_answer):  # Function to ask AI for explanation
    """
    Ask AI to explain why an answer is correct
    - question_text: The quiz question
    - correct_answer: The right answer
    """
    # Create a message (prompt) for the AI to explain the answer
    prompt = f"Explain in simple terms why '{correct_answer}' is the correct answer for: '{question_text}'."
    
    # Send prompt to OpenAI and get response
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Which AI model to use (this is fast and cheap)
        messages=[{"role": "user", "content": prompt}]  # Send our prompt as user message
    )
    
    # Extract the text from AI's response and return it
    return response.choices[0].message.content

# QUIZ GAME LOGIC
# Get total number of questions in the quiz
total_questions = len(st.session_state.questions)

# Get current question number (which question we're on)
current = st.session_state.current_question

# Check if quiz is still running (haven't answered all questions yet)
if current < total_questions:
    # Get the current question from our list
    question = st.session_state.questions[current]
    
    # Display question number (add 1 because we count from 0)
    st.subheader(f"Question {current + 1} of {total_questions}")
    
    # Display the actual question text in bold
    st.write(f"**{question['question']}**")
    
    # Show category and difficulty in small gray text
    st.caption(f"{question['category']} | {question['difficulty']}")
    
    # Show radio buttons (circles to choose one answer)
    user_choice = st.radio(
        "Choose your answer:",           # Label above the choices
        question["options"],              # List of answer choices
        key=f"question_{current}"         # Unique ID for this question
    )
    
    # Create a submit button
    if st.button("Submit Answer", type="primary"):  # When button is clicked:
        # Get the correct answer for this question
        correct_answer = question["correct"]
        
        # Check if user's answer is correct
        if user_choice == correct_answer:  # User got it right!
            st.success("Correct! Great job!")  # Show success message in green
            st.session_state.points += 1              # Add 1 point to score
        else:  # User got it wrong
            st.error(f"Wrong! The correct answer was: **{correct_answer}**")  # Show error in red
        
        # Save the user's answer to the list
        st.session_state.user_answers.append(user_choice)
        
        # Get AI explanation
        with st.spinner("AI is thinking..."):  # Show loading spinner
            # Call function to get explanation from AI
            explanation = get_explanation(question["question"], correct_answer)
            # Display explanation in blue info box
            st.info(f"**AI Explanation:**\n\n{explanation}")
        
        # Save to history
        # Add this question's data to history list
        quiz_history.append({
            "question": question["question"],      # The question text
            "your_answer": user_choice,            # What user chose
            "correct_answer": correct_answer,      # The right answer
            "explanation": explanation             # AI's explanation
        })
        
        # Write updated history to file (save it permanently)
        with open(LOG_FILE, "w") as file:  # "w" means write mode
            json.dump(quiz_history, file, indent=2)  # Convert to JSON and save nicely formatted
        
        # Wait before next question
        st.info("Next question in 20 seconds...")  # Tell user to wait
        time.sleep(20)  # Pause for 20 seconds
        
        # Move to next question
        st.session_state.current_question += 1  # Add 1 to question number
        st.rerun()  # Refresh page to show next question

else:  # Quiz is finished (answered all questions)
    # QUIZ FINISHED - SHOW RESULTS
    st.balloons()  # Show celebration animation
    st.success(f"Quiz Complete!")  # Show completion message
    
    # Get final score
    score = st.session_state.points
    
    # Display score in large metric box
    st.metric("Your Score", f"{score} / {total_questions}")
    
    # Calculate percentage score
    percentage = (score / total_questions) * 100
    
    # Show progress bar (percentage / 100 to get value between 0 and 1)
    st.progress(percentage / 100)
    
    # Show percentage as text
    st.write(f"**{percentage:.0f}%** Correct")
    
    # Create button to start new quiz
    if st.button("Start New Quiz", type="primary"):  # When clicked:
        st.session_state.questions = fetch_questions(5)  # Get new questions
        st.session_state.current_question = 0            # Reset to first question
        st.session_state.points = 0                      # Reset score to zero
        st.session_state.user_answers = []               # Clear previous answers
        st.rerun()  # Refresh page to start new quiz

# SHOW QUIZ HISTORY
# Create expandable section (collapsed by default)
with st.expander("View Quiz History"):
    # Check if there's any history
    if quiz_history:
        st.json(quiz_history)  # Display history in JSON format
    else:
        st.write("No quiz history yet!")  # Show message if empty

# SHOW STATISTICS
st.divider()  # Add horizontal line separator

# Create 3 columns for statistics
col1, col2, col3 = st.columns(3)

# Column 1: Show total questions
with col1:
    st.metric("Questions", total_questions)  # Display as metric card

# Column 2: Show correct answers
with col2:
    st.metric("Correct", st.session_state.points)  # Display points

# Column 3: Calculate and show wrong answers
with col3:
    # Calculate wrong answers (current question number minus points)
    # Use if/else to handle case when quiz is complete vs in progress
    if current <= total_questions:
        wrong = current - st.session_state.points
    else:
        wrong = total_questions - st.session_state.points
    st.metric("Wrong", wrong)  # Display wrong count