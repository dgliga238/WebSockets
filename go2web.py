import socket
import ssl
import sys
from urllib.parse import urlparse
from bs4 import BeautifulSoup

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

def main():
    if len(sys.argv) != 3 or sys.argv[1] != "-u":
        print("Usage: go2web -u <URL>")
        sys.exit(1)

    url = sys.argv[2]
    if not url.startswith("http"):
        url = "http://" + url

    print(fetch_url(url))

if __name__ == "__main__":
    main()


