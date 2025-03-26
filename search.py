import socket
import ssl
import sys
import webbrowser
from urllib.parse import urlencode, urlparse, urljoin
from bs4 import BeautifulSoup


def fetch_search_results(query, max_results=10):
    base_url = "https://html.duckduckgo.com/html"
    search_url = f"{base_url}?{urlencode({'q': query})}"
    parsed_url = urlparse(search_url)
    host = parsed_url.netloc
    path = parsed_url.path + '?' + parsed_url.query
    port = 443  # HTTPS default port

    request = f"GET {path} HTTP/1.1\r\n" \
              f"Host: {host}\r\n" \
              f"User-Agent: Mozilla/5.0\r\n" \
              f"Connection: close\r\n\r\n"

    try:
        # Create a socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.create_default_context()
        sock = context.wrap_socket(sock, server_hostname=host)
        sock.connect((host, port))

        # Send the request
        sock.sendall(request.encode())
        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
        sock.close()

        # Extract HTML content
        response_text = response.decode(errors="ignore")
        headers, body = response_text.split("\r\n\r\n", 1)
        return extract_results(body, max_results, base_url)
    except Exception as e:
        return [("Error fetching search results", "")]


def extract_results(html, max_results, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    
    for idx, link in enumerate(soup.select(".result__title a"), start=1):
        title = link.get_text(strip=True)
        href = link["href"]
        
        # Ensure full URL
        full_url = urljoin(base_url, href)
        
        results.append((title, full_url))

        if len(results) >= max_results:
            break
    
    return results


def open_link_in_browser(link):
    print(f"Opening: {link}")
    try:
        webbrowser.open(link)
    except Exception as e:
        print(f"Failed to open link: {e}")


def main():
    if len(sys.argv) < 3 or sys.argv[1] != "-s":
        print("Usage: search.py -s <search term>")
        sys.exit(1)

    search_term = " ".join(sys.argv[2:])
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


if __name__ == "__main__":
    main()

