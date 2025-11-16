# 🤖 AI Quiz Agent  
An interactive quiz application powered by OpenAI, Streamlit, and automated AI explanations.  

---

## 🎯 Project Overview  
The AI Quiz Agent is a web app that:

- Fetches multiple-choice quiz questions from the Open Trivia API  
- Allows the user to answer each question interactively  
- Uses OpenAI models to explain answers in simple terms  
- Tracks user score, history, and performance metrics  
- Stores quiz logs locally  

This project demonstrates:
- Agentic reasoning (answer checking + explanation)  
- Tool-use (API calls)  
- State management (session memory)  
- Automated workflows (question → answer → explanation → next question)  

---

## 🧠 Features

### ✔️ Dynamic Quiz Generation  
Questions are pulled live from the Open Trivia Database API.

### ✔️ AI-Generated Explanations  
Each answer is explained using an OpenAI model with simple-language logic.

### ✔️ Auto-Progressing Quiz  
After answering, the app waits 20 seconds before moving to the next question.

### ✔️ Score Tracking  
Keeps count of correct / wrong answers and shows completion metrics.

### ✔️ Quiz History  
All questions, answers, and AI explanations are saved to `quiz_log.json`.

### ✔️ Fully Deployable  
Runs on Streamlit Cloud or Kaggle Notebook with minimal setup.

---
