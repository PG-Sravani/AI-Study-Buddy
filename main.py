import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import openai
import re

# Load environment variables from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

app = FastAPI()

# Homepage with login and chatbot
@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <html>
      <head>
        <title>AI Study Buddy - Student Chatbot</title>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
        <style>
          body {{
            margin: 0;
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #74ebd5 0%, #ACB6E5 100%);
            color: #333;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
          }}
          .container {{
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 500px;
            transition: all 0.3s ease;
          }}
          .container:hover {{
            transform: scale(1.02);
          }}
          .main-heading {{
            text-align: center;
            font-size: 2.8rem;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 20px;
            letter-spacing: 2px;
          }}
          h2 {{
            text-align: center;
            color: #2c3e50;
            margin-top: 0;
          }}
          label {{
            font-weight: 600;
            display: block;
            margin-bottom: 10px;
            color: #2c3e50;
          }}
          input[type="text"] {{
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            margin-bottom: 15px;
            font-size: 16px;
            transition: all 0.3s ease;
          }}
          input[type="text"]:focus {{
            border-color: #4CAF50;
            outline: none;
          }}
          button {{
            padding: 12px 30px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s ease;
          }}
          button:hover {{
            background-color: #45a049;
          }}
          #answer {{
            margin-top: 20px;
            background: #f1f1f1;
            padding: 15px;
            border-radius: 8px;
            color: #222;
            white-space: pre-wrap;
            font-weight: bold;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <div class="main-heading">AI Study Buddy</div>
         

          <label for="question">Ask the Chatbot:</label>
          <input type="text" id="question" placeholder="Type your question"/>
          <button onclick="askQuestion()">Ask</button>
          <div id="answer"></div>
        </div>

        <script>
          async function askQuestion() {{
            let q = document.getElementById("question").value;
            let res = await fetch("/chatbot?question=" + encodeURIComponent(q));
            let data = await res.json();
            document.getElementById("answer").innerText = data.answer;
          }}
        </script>
      </body>
    </html>
    """


@app.get("/chatbot")
def chatbot(question: str):
    question_lower = question.lower()

    # 1️⃣ Try to detect and solve math expressions
    math_match = re.fullmatch(r"\s*(\d+)\s*([\+\-\*/])\s*(\d+)\s*", question_lower)
    if math_match:
        try:
            num1 = int(math_match.group(1))
            op = math_match.group(2)
            num2 = int(math_match.group(3))

            if op == "+":
                result = num1 + num2
            elif op == "-":
                result = num1 - num2
            elif op == "*":
                result = num1 * num2
            elif op == "/":
                result = num1 / num2 if num2 != 0 else "undefined (division by zero)"

            return {"answer": f"The answer is {result}."}
        except Exception:
            return {"answer": "Oops! I couldn't calculate that math problem."}

    # 2️⃣ Fallback keywords for common questions
    if "hi" in question_lower:
        answer = "Hello! How can I assist you today?"
    elif "python" in question_lower:
        answer = "Python is a popular programming language, known for its simplicity and versatility in fields like AI, web development, and data science."
    elif "ai" in question_lower:
        answer = "AI stands for Artificial Intelligence, where machines are trained to mimic human-like tasks and decision-making."
    elif "exam" in question_lower:
        answer = "Stay calm, focus on your revision, and don't forget to practice past exam papers! You've got this! 💪"
    elif "what is your name" in question_lower:
        answer = "I am AI Study Buddy, here to help you with your learning!"
    elif "bye" in question_lower:
        answer = "Goodbye! See you next time!"
    else:
        # 3️⃣ Fallback to OpenAI API if no match for math or keyword
        try:
            # Call OpenAI API for dynamic answers (GPT-3.5)
            response = openai.Completion.create(
                model="gpt-3.5-turbo",  # Ensure you're using the correct model
                prompt=question,  # Use the user's question as the prompt
                max_tokens=100,
                temperature=0.7
            )
            return {"answer": response.choices[0].text.strip()}
        except openai.error.OpenAIError as e:
            return {"answer": f"OpenAI API error: {str(e)}"}
        except Exception as e:
            return {"answer": f"Connection error: {str(e)}"}

    return {"answer": answer}


# Example dashboard route
@app.get("/dashboard")
def dashboard(request: Request):
    return {"message": "Welcome to your dashboard!", "user": "test_user"}
