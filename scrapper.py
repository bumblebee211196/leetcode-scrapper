import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

options = Options()
options.add_argument("--headless")
options.add_argument("--log-level=3")
driver = webdriver.Firefox(executable_path="/usr/local/bin/geckodriver", options=options)

ALGORITHMS_ENDPOINT_URL = "https://leetcode.com/api/problems/algorithms/"
ALGORITHMS_BASE_URL = "https://leetcode.com/problems/"

# NOTE: Configure your path for storing the problems
BASE_PROBLEMS_PATH = ""


def download(url: str, question_id: int, question_title_slug: str):
    """Download the URL content using geckodriver and create file(s) based on needs

    Args:
        url (str): The URL to scrap.
        question_id (int): The question ID.
        question_title_slug (str): The question title slug.
    """
    try:
        l = len(f"{question_id}")
        folder_name = f'_{"0" * (4 - l)}{question_id}_{question_title_slug.replace("-", "_")}'
        Path(f"{BASE_PROBLEMS_PATH}/{folder_name}").mkdir(parents=True, exist_ok=True)

        driver.get(url)
        _ = WebDriverWait(driver, 20).until(EC.invisibility_of_element_located((By.ID, "initial-loading")))
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Modify the content as per your needs
        content = (
            str(soup.find("div", {"class": "content_u3I1 question-content_JfgR"}).div)
            .replace("<div>", "")
            .replace("</div>", "")
        )

        with open(f"{BASE_PROBLEMS_PATH}/{folder_name}/README.md", "w") as fp:
            fp.write(content)

    except Exception as exception:
        print(f"Error: {exception}")


def main():
    """Collects the list of problems from leetcode and scraps each problem from the list in the order of question ID."""
    all_problem_json = requests.get(ALGORITHMS_ENDPOINT_URL).content
    all_problem_json = json.loads(all_problem_json)

    links = []
    for child in all_problem_json["stat_status_pairs"]:
        if not child["paid_only"]:
            question_title_slug = child["stat"]["question_title_slug"]
            question_article_slug = child["stat"]["question_article_slug"]
            question_title = child["stat"]["question_title"]
            frontend_question_id = child["stat"]["frontend_question_id"]
            links.append((question_title_slug, frontend_question_id, question_title, question_article_slug))

    links = sorted(links, key=lambda x: (x[1]))

    try:
        with open("track.conf", "r") as f:
            start = int(f.readline())
        start = 0 if start < 0 else start
        for i in range(start, len(links)):
            question_title_slug, frontend_question_id, question_title, question_article_slug = links[i]
            url = ALGORITHMS_BASE_URL + question_title_slug
            download(url, frontend_question_id, question_title_slug)
            print(f'Question "{frontend_question_id} {question_title}" done')
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
