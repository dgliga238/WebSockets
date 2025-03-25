import socket
import ssl
import sys
from urllib.parse import urlencode, urlparse
from bs4 import BeautifulSoup


def fetch_search_results(query, max_results=10):
    search_url = f"https://html.duckduckgo.com/html?{urlencode({'q': query})}"
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
        return extract_results(body, max_results)
    except Exception as e:
        return [f"Error fetching search results: {e}"]


def extract_results(html, max_results):
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    for link in soup.select(".result__title a"):
        title = link.get_text(strip=True)
        href = link["href"]
        results.append(f"{title}\n{href}\n")
        if len(results) >= max_results:
            break
    return results if results else ["No results found."]


def main():
    if len(sys.argv) != 3 or sys.argv[1] != "-s":
        print("Usage: search.py -s <search term>")
        sys.exit(1)

    search_term = sys.argv[2]
    results = fetch_search_results(search_term)

    print("\n".join(results))


if __name__ == "__main__":
    main()
