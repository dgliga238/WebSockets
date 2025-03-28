import sys
from go2web import fetch_url
from search import fetch_search_results, open_link_in_browser


def main():


    command = sys.argv[1]

    if command == '-h':
        print("Usage:")
        print("  go2web -h           # Available options")
        print("  go2web -u <URL>      # Fetch a specific URL")
        print("  go2web -s <search>   # Perform a search")
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
        search_term = " ".join(sys.argv[2:])
        print(f"Searching for: {search_term}")
        results = fetch_search_results(search_term)

        if not results:
            print("No results found.")
            sys.exit(1)

        print("\nSearch Results:")
        for idx, (title, link) in enumerate(results, start=1):
            print(f"{idx}. {title}\n   {link}")

        try:
            choice = int(input("\nEnter the number of the link to open (0 to exit): "))
            if 1 <= choice <= len(results):
                open_link_in_browser(results[choice - 1][1])
            elif choice == 0:
                print("Exiting...")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a valid number.")

    else:
        print("Invalid command. Use -h to see available options.")
        sys.exit(1)


if __name__ == "__main__":
    main()
