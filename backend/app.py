from flask import Flask, request, jsonify
import os
from flask_cors import CORS
from langchain.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import google.generativeai as genai
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecret")
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.unauthorized_handler
def unauthorized_callback():
    print("🚫 Unauthorized access blocked by @login_required.")
    return jsonify({"error": "Unauthorized"}), 401

app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False
)

CORS(app, supports_credentials=True, origins=["http://127.0.0.1:3000"])

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

genai.configure(api_key=API_KEY)
embed = GoogleGenerativeAIEmbeddings(google_api_key=API_KEY, model="models/embedding-001")
USER_DATA_FILE = "user_data.txt"
folder_name = "store"

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/', methods=['GET'])
def root():
    return "Flask is running", 200


@app.route('/login', methods=['POST'])
def login():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    user = User(user_id)
    login_user(user)
    return jsonify({"message": "Logged in"}), 200

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"}), 200

@app.route('/current_user', methods=['GET'])
def whoami():
    if current_user.is_authenticated:
        return jsonify({"user_id": current_user.id})
    return jsonify({"user_id": None})


# --- Define Tool Functions ---
def financial_education(user_id, question):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-002")
        response = model.generate_content(question)
        if response and response.text:
            return response.text
        return "I'm unable to provide a response right now."
    except Exception as e:
        return f"Error: {str(e)}"

def personal_budgeting(user_id, question):
    try:
        user_folder = os.path.join(folder_name, user_id)
        vs = FAISS.load_local(str(user_folder), embeddings=embed, allow_dangerous_deserialization=True)
        all_docs = vs.docstore._dict.values()
        all_docs_data = "\n".join([doc.page_content for doc in all_docs]) if all_docs else ""

        prompt = f"{question}\n{all_docs_data}\nUse the above data to answer the question. If not relevant, generate an appropriate response."
        model = genai.GenerativeModel("gemini-1.5-flash-002")
        response = model.generate_content(prompt)

        return response.text if response and response.text else "No response from model."
    except Exception as e:
        return f"Error: {str(e)}"

# --- Routes ---
@app.route('/get_transactions', methods=['GET'])
@login_required
def get_transactions():
    user_id = current_user.id
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    user_folder = os.path.join(folder_name, user_id)
    file_path = os.path.join(user_folder, USER_DATA_FILE)
    if not os.path.exists(file_path):
        return jsonify({'transactions': []})

    with open(file_path, "r") as f:
        transactions = [eval(line.strip()) for line in f]
    return jsonify({'transactions': transactions}), 200


@app.route('/update_user', methods=['POST'])
@login_required
def update_user():
    try:
        data = request.get_json()
        user_id = current_user.id  
        print(">>> Is authenticated:", current_user.is_authenticated)
        print(">>> User ID:", getattr(current_user, "id", "Anonymous"))
        user_folder = os.path.join(folder_name, user_id)
        os.makedirs(user_folder, exist_ok=True)
        vector_store_path = os.path.join(user_folder)
        index_file_path = Path(vector_store_path) / "index.faiss"

        required_fields = ["amount", "transaction_type", "category", "description","date"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        date = data.get("date")  # 🟡 This will be a string like "2025-06-07T18:33:00.000Z"
        transaction_text = f"{data['amount']} {data['transaction_type']} {data['category']} {data['description']} on {date}"
        embedding = embed.embed_query(transaction_text)

        if not index_file_path.exists():
            print("⚠️ No FAISS index found — creating a new one.")
            vector_store = FAISS.from_texts(texts=[transaction_text], embedding=embed)
        else:
            print("✅ FAISS index exists — loading and updating it.")
            vector_store = FAISS.load_local(vector_store_path, embeddings=embed, allow_dangerous_deserialization=True)
            vector_store.add_texts([transaction_text], embeddings=[embedding])

        vector_store.save_local(vector_store_path)

        with open(os.path.join(user_folder, USER_DATA_FILE), "a") as f:
            f.write(str(data) + "\n")

        return jsonify({"message": "User data updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/agentic_query', methods=['POST'])
@login_required
def agentic_query():
    data = request.get_json()
    user_id = current_user.id
    question = data.get("question")

    if not question or not user_id:
        return jsonify({"error": "Missing user_id or question"}), 400

    # Create tools dynamically based on user_id
    tools = [
        Tool(name="PersonalBudgeting", func=lambda q: personal_budgeting(user_id, q), description="Analyze personal budget questions"),
        Tool(name="FinancialEducation", func=lambda q: financial_education(user_id, q), description="Answer financial education questions")
    ]

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-002", google_api_key=API_KEY)
    memory = ConversationBufferMemory(memory_key="chat_history")
    agent = initialize_agent(tools=tools, llm=llm, memory=memory, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

    try:
        response = agent.run(question)
        return jsonify({"response": response}), 200
    except Exception as e:
        return jsonify({"error": f"Agent error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
