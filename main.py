import sys
from go2web import fetch_url
from search import fetch_search_results


def main():
    command = sys.argv[1]

    if command == '-h':
        print("Usage:")
        print("  python3 main.py -h           # Available options")
        print("  python main.py -u <URL>      # Fetch a specific URL")
        print("  python main.py -s <search>   # Perform a search")
        sys.exit(1)

    arg = sys.argv[2]

    if command == "-u":
        # URL fetching functionality
        if not arg.startswith("http"):
            arg = "http://" + arg
        print("Fetching URL content:")
        result = fetch_url(arg)
        print(result)

    elif command == "-s":
        # Search functionality
        print(f"Searching for: {arg}")
        results = fetch_search_results(arg)
        print("\n".join(results))

    else:
        print("Invalid command. Use -h to see available options.")
        sys.exit(1)


if __name__ == "__main__":
    main()