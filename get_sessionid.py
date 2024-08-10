import re
import time
import requests

# Function to perform a GET request with default headers
def GET(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0',
        'Accept': 'application/json, text/javascript',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    return requests.get(url, headers=headers)

# Function to perform a GET request with custom headers including cookies
def GET_h(url, ttwid, passport_csrf_token):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0',
        'Accept': 'application/json, text/javascript',
        'Content-Type': 'application/x-www-form-urlencoded',
        'cookie': f'ttwid={ttwid}; passport_csrf_token={passport_csrf_token};',
        'x-tt-passport-csrf-token': f'{passport_csrf_token}'
    }
    return requests.get(url, headers=headers)

# Function to decode escape sequences in a URL
def convert_escape_sequence(s):
    return s.encode().decode('unicode_escape')

# Function to shorten a URL using TikTok's URL shortening service
def short_url(url_to_short):
    url = "https://www.tiktok.com/shorten/?aid=1988"
    payload = {
        'targets': url_to_short,
        'belong': 'tiktok-webapp-qrcode'
    }
    response = requests.post(url, data=payload)
    url_shorten_list = re.findall(r'"short_url":"(.*?)"', response.text)
    url_shorten = url_shorten_list[0] if url_shorten_list else None
    return url_shorten

# Function to retrieve the QR code URL and related tokens
def get_qrcode_url():
    url = "https://www.tiktok.com/passport/web/get_qrcode/?next=https://www.tiktok.com&aid=1459"
    response = requests.post(url)
    cookies = response.cookies

    passport_csrf_token = cookies.get('passport_csrf_token')
    ttwid = GET('https://www.tiktok.com/login/qrcode')
    ttwid = ttwid.cookies.get('ttwid')

    token_match = re.search(r'"token":"(.*?)"', response.text)
    qrcode_index_url_match = re.search(r'"qrcode_index_url":"(.*?)"', response.text)

    token = token_match.group(1) if token_match else None
    qrcode_index_url = qrcode_index_url_match.group(1) if qrcode_index_url_match else None
    qrcode_index_url = convert_escape_sequence(qrcode_index_url)

    shorten_url = short_url(qrcode_index_url)
    print("Enter URL from your phone:", shorten_url)
    return token, ttwid, passport_csrf_token, shorten_url

# Function to continuously check for QR code scan and confirmation, and retrieve session ID
def get_session_id():
    try:
        token, ttwid, passport_csrf_token, shorten_url = get_qrcode_url()
        while True:
            qr_check = GET_h(f'https://web-va.tiktok.com/passport/web/check_qrconnect/?next=https%3A%2F%2Fwww.tiktok.com&token={token}&aid=1459', ttwid, passport_csrf_token)
            if "scanned" in qr_check.text:
                print("Waiting for your confirmation!")
            elif "confirmed" in qr_check.text:
                sessionid = qr_check.cookies.get('sessionid')
                break
            elif "expired" in qr_check.text:
                token, ttwid, passport_csrf_token, shorten_url = get_qrcode_url()
                print("URL has been updated!")
            time.sleep(0.7)

        if sessionid:
            print(f"Session ID: {sessionid}")
            print("\nCoded By Hex")
        else:
            print("Failed to retrieve session ID.")
    except Exception as error:
        print(f"ERROR: {error}")

# Main function to start the process
def main():
    get_session_id()

# Entry point of the script
if __name__ == '__main__':
    main()
