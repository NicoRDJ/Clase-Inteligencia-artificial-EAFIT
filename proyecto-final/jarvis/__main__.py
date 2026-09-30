"""Chat por terminal:  python -m jarvis"""
from jarvis.assistant import Jarvis


def main():
    j = Jarvis()
    print("JARVIS en línea. Escribe 'salir' para terminar.\n")
    while True:
        try:
            text = input("Tú › ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text.lower() in {"salir", "exit", "quit"}:
            break
        if not text:
            continue
        r = j.ask(text, session="terminal")
        print(f"\nJARVIS [{r.brain} · {r.latency:.1f}s · ${r.cost:.4f} · {r.reason}] ›\n{r.text}\n")


if __name__ == "__main__":
    main()
