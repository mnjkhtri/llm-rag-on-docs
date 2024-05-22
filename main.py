import argparse

from src.qa import QA

def parse_arguments():
    parser = argparse.ArgumentParser(description="Ask questions to your documents.")
    parser.add_argument("--no-rag", action='store_true', help="Get your answer without RAG")
    return parser.parse_args()

def main():
    args = parse_arguments()
    qa = QA(args)

    while True:
        query = input("Query?: ")
        if args.no_rag: qa._ask_non_rag(query)
        else: qa._ask_rag(query)
        print("\n")

if __name__ == "__main__": main()