import socket
import ssl
import sys
import urllib.parse
from bs4 import BeautifulSoup


def clean_html(text):
    # Parse the HTML with BeautifulSoup and make the content human-readable
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text(separator='\n', strip=True)


def fetch_url(url):
    parsed_url = urllib.parse.urlparse(url)
    host = parsed_url.netloc or parsed_url.path
    path = parsed_url.path if parsed_url.path else "/"
    port = 443 if parsed_url.scheme == "https" else 80

    request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\nUser-Agent: go2web/1.0\r\n\r\n"

    try:
        # Create socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Handle HTTPS (SSL/TLS)
        if parsed_url.scheme == "https":
            context = ssl.create_default_context()
            sock = context.wrap_socket(sock, server_hostname=host)

        sock.connect((host, port))
        sock.sendall(request.encode())

        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk

        sock.close()

        # Convert response to string and extract body
        response_text = response.decode(errors="ignore")
        body = response_text.split("\r\n\r\n", 1)[-1]  # Extract HTML body

        return clean_html(body)  # Clean and return readable text

    except Exception as e:
        return f"Error fetching {url}: {e}"


def search_term(search_term):
    # Encode search term and make a request to Google search
    query = urllib.parse.urlencode({"q": search_term})
    url = f"https://www.google.com/search?{query}"

    print(f"Searching for: {search_term}")
    response = fetch_url(url)

    # Parse the response using BeautifulSoup for human readability
    soup = BeautifulSoup(response, 'html.parser')

    # Extract links from Google search result page
    results = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('/url?q='):
            parsed_link = urllib.parse.unquote(href.split('/url?q=')[1].split('&')[0])
            results.append(parsed_link)

    # Display the top 10 results (or fewer if less than 10)
    print("\nTop 10 Results:\n")
    for i, result in enumerate(results[:10]):
        print(f"{i + 1}. {result}")


def main():
    if len(sys.argv) < 3:
        print("Usage: go2web -s <search-term>")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'go2web' and sys.argv[2] == '-s':
        if len(sys.argv) != 4:
            print("Usage: go2web -s <search-term>")
            sys.exit(1)

        search_term_input = sys.argv[3]
        search_term(search_term_input)

    else:
        print("Invalid command.")
        sys.exit(1)


if __name__ == "__main__":
    main()
