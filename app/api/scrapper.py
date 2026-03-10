import requests
from bs4 import BeautifulSoup

def scrape_profile(name, dept):
    # Send a request to the website
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = "https://bmsce.ac.in/home/" + str(dept).replace(" ", "-").replace("(","-").replace(")","-") + "Faculty"
    response = requests.get(url, headers=headers)
    data = {"name": str(name), "department": str(dept)}

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve page. Status code: {response.status_code}")
        return None

    # Parse the content of the page
    soup = BeautifulSoup(response.text, 'html.parser')
    containers = soup.find_all('div', class_='row py-2 mb-0')

    for container in containers:
        if name in str(container):
            data['link'] = str(container.find('a')['href'])
            data['image'] = str(container.find('img')['src'])

            details = container.find_all('div', class_='overflow-hidden mb-1')
            d = ['title', 'degrees', 'email', 'interests']
            for i in range(len(details)):
                data[d[i]] = str(details[i].find('p').get_text(strip=True))
            return data
    return None