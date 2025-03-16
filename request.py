import socket
import ssl
import sys
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import urllib.parse


def clean_html(text):
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(text, 'html.parser')
    for script_or_style in soup(["style", "script"]):
        script_or_style.decompose()  # Remove tag
    return soup.get_text(separator='\n', strip=True)


def fetch_url(url):
    parsed_url = urlparse(url)
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
    # Search Google with the term and fetch top 10 results
    query = urllib.parse.urlencode({"q": search_term})
    url = f"https://www.google.com/search?{query}"

    print(f"Searching for: {search_term}")
    response = fetch_url(url)

    # Extract links from the response (Google search result links are inside <a> tags)
    soup = BeautifulSoup(response, 'html.parser')
    results = []

    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('/url?q='):
            parsed_link = urllib.parse.unquote(href.split('/url?q=')[1].split('&')[0])
            results.append(parsed_link)

    # Print the top 10 results (or fewer if there are less)
    for i, result in enumerate(results[:10]):
        print(f"{i + 1}. {result}")

def main():
    command = sys.argv[1]
    if command == 'go2web' and sys.argv[2] == '-u':
        if len(sys.argv) != 4:
            print("Usage: go2web -u <URL>")
            sys.exit(1)

        url = sys.argv[3]
        if not url.startswith("http"):
            url = "http://" + url
        print(fetch_url(url))


if __name__ == "__main__":
    main()
