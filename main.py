"""
MPS Information Science Chatbot
A RAG-powered conversational assistant for Cornell's MPS in Information Science program
"""

import os
from pathlib import Path
from shiny import App, ui, reactive
from chatlas import ChatOpenAI

# Load knowledge base files
def load_knowledge_base():
    """Load all knowledge base documents into a single context string"""
    knowledge_dir = Path("knowledge")
    knowledge_content = []

    # Get all markdown files in knowledge directory
    if knowledge_dir.exists():
        for filepath in sorted(knowledge_dir.glob("*.md")):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                knowledge_content.append(f"## {filepath.name}\n\n{content}\n\n")

    return "\n".join(knowledge_content)

# Load knowledge base at startup
KNOWLEDGE_BASE = load_knowledge_base()

# System prompt for the chatbot
SYSTEM_PROMPT = f"""You are a helpful conversational assistant for Cornell University's Master of Professional Studies (MPS) in Information Science program.

Your role is to help prospective and current students with:
- Understanding the MPS in Information Science program structure and requirements
- Explaining the curriculum, including core courses, electives, and concentration options (User Experience, Data Science, Interactive Technologies, Networks, Crowds, and Markets)
- Answering questions about admissions requirements and application process
- Providing information about degree requirements (minimum 30 credits, IS and HSS course distribution)
- Explaining the MPS Project requirement (INFO 5900) and Professional Career Development course (INFO 5905)
- Sharing career outcomes and employment statistics
- Clarifying differences between this program and other graduate programs in Bowers CIS
- Answering questions about tuition, financial support, scholarships, and GTRS positions
- Helping international students understand requirements (TOEFL/IELTS scores, visa information)

Guidelines:
1. Be helpful, encouraging, and patient with all users
2. Provide clear, accurate information based on official Cornell sources
3. Ground all responses in the verified content from the knowledge base
4. When citing information, reference the source when possible
5. If you don't know something or the information isn't in your knowledge base, be honest and direct users to official Cornell resources
6. Be inclusive and avoid language that might favor certain applicant backgrounds
7. Remind users to verify critical information (deadlines, requirements) on official Cornell websites
8. Do not include hyperlinks or URLs in your responses - provide information in plain text format only

What you should NOT do:
- Do not make up information about program policies, requirements, or deadlines
- Do not provide opinions on applicant competitiveness or chances of admission
- Do not give immigration or visa advice beyond general program information
- Do not store or request personally identifiable information
- Do not provide information that may be outdated without noting the data collection date

Important disclaimer: This chatbot provides information based on publicly available Cornell content. Program requirements and policies may change. Always verify important details on official Cornell University websites.

You have access to the following official Cornell program information:

{KNOWLEDGE_BASE}

Use this information to provide accurate, helpful responses grounded in official Cornell content.
"""

# Create the Shiny UI
app_ui = ui.page_fluid(
    ui.head_content(
        ui.tags.style("""
            .app-title {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .app-title h2 {
                margin: 0;
                font-weight: 600;
            }
            .app-title p {
                margin: 5px 0 0 0;
                opacity: 0.9;
            }
            .info-box {
                background-color: #f0f4f8;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 5px;
            }
            .chat-container {
                max-width: 900px;
                margin: 0 auto;
            }
            .example-questions {
                margin-bottom: 20px;
            }
            .example-questions h4 {
                color: #4a5568;
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .example-btn {
                background-color: white;
                border: 1px solid #e2e8f0;
                color: #718096;
                padding: 10px 15px;
                margin: 5px 5px 5px 0;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s ease;
                font-size: 14px;
                display: inline-block;
            }
            .example-btn:hover {
                background-color: #f7fafc;
                border-color: #667eea;
                color: #667eea;
                transform: translateY(-1px);
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        """)
    ),
    ui.div(
        {"class": "chat-container"},
        ui.div(
            {"class": "app-title"},
            ui.h2("🎓 Cornell MPS in Information Science"),
            ui.p("Your AI assistant for exploring the MPS-IS program")
        ),
        ui.div(
            {"class": "info-box"},
            ui.markdown("""
            **Welcome!** I'm here to help you with:
            - 📋 Program structure, requirements, and concentrations
            - 📝 Admissions process and application requirements
            - 📚 Curriculum, courses, and the MPS Project
            - 💼 Career outcomes and employment statistics
            - 💰 Tuition, financial support, and scholarships

            Feel free to ask me anything about the MPS in Information Science program!

            *Note: Always verify important details on official Cornell websites.*
            """)
        ),
        ui.div(
            {"class": "example-questions"},
            ui.h4("Try these example questions:"),
            ui.input_action_button(
                "example1",
                "What are the prerequisites for the MPS program?",
                class_="example-btn"
            ),
            ui.input_action_button(
                "example2",
                "How many credits are required to graduate?",
                class_="example-btn"
            ),
        ),
        ui.chat_ui("chat")
    )
)

def server(input, output, session):
    """Server function with chat integration"""

    # Initialize the OpenAI chat client with system prompt
    chat_client = ChatOpenAI(
        model="gpt-4.1",
        system_prompt=SYSTEM_PROMPT,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # Create chat instance
    chat = ui.Chat(id="chat")

    # Handle user messages with streaming responses
    @chat.on_user_submit
    async def handle_user_input(user_input: str):
        # Stream the response from the LLM
        response = await chat_client.stream_async(user_input)

        # Append the streaming response to the chat
        await chat.append_message_stream(response)

    # Handle example question button clicks
    @reactive.effect
    @reactive.event(input.example1)
    async def _():
        question = "What are the prerequisites for the MPS program?"
        await chat.append_message({"role": "user", "content": question})
        response = await chat_client.stream_async(question)
        await chat.append_message_stream(response)

    @reactive.effect
    @reactive.event(input.example2)
    async def _():
        question = "How many credits are required to graduate?"
        await chat.append_message({"role": "user", "content": question})
        response = await chat_client.stream_async(question)
        await chat.append_message_stream(response)



# Create the Shiny app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
