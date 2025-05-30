import socket
import ssl
import sys
import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def clean_html(text):
    """Removes scripts and styles from HTML and returns clean text."""
    soup = BeautifulSoup(text, 'html.parser')
    for script_or_style in soup(["style", "script"]):
        script_or_style.decompose()  # Remove tag
    return soup.get_text(separator='\n', strip=True)

def get_redirect_location(headers: str, base_uri: str) -> str | None:
    """Extracts and resolves the redirect location from headers."""
    location_match = re.search(r"Location: (.+)", headers, re.IGNORECASE)
    if location_match:
        redirect_url = location_match.group(1).strip()
        if not redirect_url.startswith("http"):
            redirect_url = urljoin(base_uri, redirect_url)
        return redirect_url
    return None

def fetch_url(url, max_redirects=5):
    """
    Fetches the given URL and follows redirects if necessary.
    Limits the number of redirects to prevent infinite loops.
    """
    for _ in range(max_redirects):
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

            # Convert response to string
            response_text = response.decode(errors="ignore")
            headers, body = response_text.split("\r\n\r\n", 1)

            # Check for redirection using the get_redirect_location function
            redirect_url = get_redirect_location(headers, url)
            if redirect_url:
                print(f"Redirecting to: {redirect_url}")
                url = redirect_url  # Follow the redirect
            else:
                return clean_html(body)  # Return cleaned HTML text

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return f"Error fetching {url}: {e}"

    return "Too many redirects, stopping."

def main():
    if len(sys.argv) != 3 or sys.argv[1] != "-u":
        print("Usage: go2web -u <URL>")
        sys.exit(1)

    url = sys.argv[2]
    if not url.startswith("http"):
        url = "https://" + url

    print(fetch_url(url))

if __name__ == "__main__":
    main()
