import requests
from bs4 import BeautifulSoup

def scrape_profile(name, dept):
    base_url = "https://bmsce.ac.in"

    # Clean URL formatting
    dept_slug = (
        str(dept)
        .replace(" (", "-")
        .replace(" ", "-")
        .replace(")", "")
    )

    url = f"{base_url}/home/{dept_slug}-Faculty"

    # Strong headers (important for deployment)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    # Debug (optional, remove later)
    print("URL:", url)
    print("Status Code:", response.status_code)

    if response.status_code != 200:
        print("Failed to retrieve page")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    containers = soup.find_all("div", class_="row py-2 mb-0")

    data = {
        "name": name,
        "department": dept
    }

    for container in containers:
        text = container.get_text(" ", strip=True).lower()

        # Safer name match
        if name.lower() in text:
            try:
                link = container.find("a")["href"]
                img = container.find("img")["src"]

                # Fix relative URLs
                data["link"] = base_url + link if link.startswith("/") else link
                data["image"] = base_url + img if img.startswith("/") else img

                details = container.find_all("div", class_="overflow-hidden mb-1")
                keys = ["title", "degrees", "email", "interests"]

                for i in range(min(len(details), len(keys))):
                    p = details[i].find("p")
                    if p:
                        data[keys[i]] = p.get_text(strip=True)

                return data

            except Exception as e:
                print("Parsing error:", e)
                return None

    return None
