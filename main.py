import csv
import requests
from typing import Any, Dict, List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

z_event_website = "https://zevent.fr/"

streamer_button_path = "/html/body/div/div/div[1]/div/button"
streamer_elements_path = '/html/body/div[3]/div[3]/a'


def download_image(url: str, filename: str) -> None:
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)


def write_data_to_csv(data: List[Dict[str, Any]], filename: str = 'streamers.csv') -> None:
    keys = data[0].keys() if data else []
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    actions = ActionChains(driver)


    try:
        driver.get(z_event_website)

        wait = WebDriverWait(driver, 60)

        streamers_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, streamer_button_path)
            )
        )
        streamers_button.click()

        streamer_elements = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, streamer_elements_path)
            )
        )

        streamers_data = []

        for index, element in enumerate(streamer_elements):
            try:
                twitch_url = element.get_attribute('href')

                img_element = element.find_element(By.TAG_NAME, 'img')
                avatar_online_url = img_element.get_attribute('src')

                username = img_element.get_attribute('alt')

                if not username:
                    username_span = element.find_element(By.CSS_SELECTOR, 'span.truncate')
                    username = username_span.text

                try:
                    donation_element = element.find_element(By.CSS_SELECTOR, 'span.bg-primary-900')
                    donation = donation_element.text.replace(' ', '').replace('€', '').strip()
                except:
                    donation = "N/A"


                try:
                    box_element = element.find_element(By.CSS_SELECTOR, 'div.group.relative')
                    location_element = box_element.find_element(By.CSS_SELECTOR, 'span.hidden')
                    driver.execute_script("arguments[0].classList.remove('hidden');", location_element)
                    location = location_element.text
                    driver.execute_script("arguments[0].classList.add('hidden');", location_element)
                except (NoSuchElementException, TimeoutException):
                    location = "N/A"

                streamer_info = {
                    'username': username,
                    'donation': donation,
                    'location': location,
                    'twitch_url': twitch_url,
                    'avatar': f"avatars/{username}.png",
                    'avatar_online_url': avatar_online_url,
                }

                streamers_data.append(streamer_info)

                # if avatar_online_url and username:
                #     download_image(avatar_online_url, f"avatars/{username}.png")

            except Exception as e:
                print(f"Error parsing streamer element: {e}")

            write_data_to_csv(streamers_data)
            

        print(f"Found {len(streamer_elements)} streamer elements.")
    except TimeoutException:
        print("Could not find element")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
