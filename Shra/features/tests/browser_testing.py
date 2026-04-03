from AIVA.Shra.brain.llm.llm_client import LLMClient
from AIVA.Shra.brain.llm.prompt_builder import PromptBuilder
from AIVA.Shra.brain.llm.response_parser import ResponseParser
from AIVA.Shra.brain.llm.memory import Memory
from AIVA.Shra.brain.router import Router
from AIVA.Shra.brain.simple_command_parser import SimpleCommandParser
from AIVA.Shra.features.browser.controller import BrowserController


# Initialize components
llm = LLMClient()
prompt_builder = PromptBuilder()
parser = ResponseParser()
memory = Memory()
router = Router()
browser = BrowserController()
simple_parser = SimpleCommandParser()

while True:

    command = input("You: ")

    if command.lower() in ["exit", "quit"]:
        break

    # 🔥 EMAIL FLOW FIRST
    if browser.pending_email:
        result = browser.handle({
            "action": "continue_email",
            "query": command
        })

        print("Assistant:", result["response"])
        continue

    # ---------------- NORMAL FLOW ----------------
    simple_result = simple_parser.parse(command)

    if simple_result:
        structured = simple_result
    else:
        prompt = prompt_builder.build(command, memory.get_context())
        raw_response = llm.generate(prompt)

        print("\n===== RAW LLM OUTPUT =====")
        print(raw_response)
        print("==========================\n")

        parsed = parser.parse(raw_response)
        structured = router.route(parsed)

    structured["original_command"] = command

    # 🔥 THIS WAS MISSING / WRONG IN YOUR CODE
    result = browser.handle(structured)

    print("Assistant:", result["response"])