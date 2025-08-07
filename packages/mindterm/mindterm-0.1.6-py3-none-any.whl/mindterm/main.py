import os

from loguru import logger
from openai import OpenAI
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter

_completer = WordCompleter(["\\chat", "\\bye"], ignore_case=True)


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv(
        "OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
    ),
)


def completion(content: str) -> str:
    completion = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "qwen-plus"),
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": content},
        ],
    )
    return completion.choices[0].message.content


def run() -> None:
    logger.info("start!")
    session = PromptSession(completer=_completer)

    while True:
        try:
            text = session.prompt("> ")
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        else:
            if text == "\\bye":
                break
            print("You entered:", completion(text))
    print("GoodBye!")


def main() -> None:
    run()


if __name__ == "__main__":
    main()
