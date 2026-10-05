from llm.llm_file_assistant import ask_llm

while True:

    query = input("\nYou: ")

    if query.lower() == "exit":
        break

    answer = ask_llm(query)

    print("\nAssistant:", answer)