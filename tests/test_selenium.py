"""Selenium end-to-end test for the Student Task Tracker.

Usage:
    pip install -r tests/requirements.txt
    python tests/test_selenium.py http://<ALB-DNS-or-EC2-IP>
    python tests/test_selenium.py http://<ALB-DNS-or-EC2-IP> --headless
"""
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    url = sys.argv[1].rstrip("/")

    options = webdriver.ChromeOptions()
    if "--headless" in sys.argv:
        options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)  # Selenium Manager downloads chromedriver automatically
    wait = WebDriverWait(driver, 10)
    passed = 0

    try:
        # Test 1: page loads with the correct title
        driver.get(url)
        assert driver.title == "Student Task Tracker", f"Wrong page title: {driver.title!r}"
        print("PASS 1: page title is 'Student Task Tracker'")
        passed += 1

        # Test 2: verify a web element (heading) is visible
        heading = wait.until(EC.visibility_of_element_located((By.ID, "app-title")))
        assert heading.text == "Student Task Tracker"
        server = driver.find_element(By.ID, "server-name").text
        print(f"PASS 2: heading visible, served by {server}")
        passed += 1

        # Test 3: add a task through the form and verify it appears in the list
        title = f"Selenium task {int(time.time())}"
        driver.find_element(By.ID, "task-title").send_keys(title)
        Select(driver.find_element(By.ID, "task-priority")).select_by_visible_text("High")
        driver.find_element(By.ID, "add-task-btn").click()
        task = wait.until(EC.presence_of_element_located(
            (By.XPATH, f"//li[contains(@class,'task')][span[@class='task-title' and text()='{title}']]")))
        print(f"PASS 3: task '{title}' added and visible")
        passed += 1

        # Test 4: mark it done
        task.find_element(By.CLASS_NAME, "toggle-btn").click()
        task = wait.until(EC.presence_of_element_located(
            (By.XPATH, f"//li[contains(@class,'done')][span[text()='{title}']]")))
        print("PASS 4: task marked as done")
        passed += 1

        # Test 5: delete it (clean up after ourselves)
        task.find_element(By.CLASS_NAME, "delete-btn").click()
        wait.until(EC.staleness_of(task))  # page reloaded after the POST
        assert title not in driver.find_element(By.ID, "task-list").text, "Task still listed"
        print("PASS 5: task deleted")
        passed += 1

        print(f"\nALL {passed} TESTS PASSED")
    except Exception as e:
        print(f"\nFAILED after {passed} passing test(s): {e!r}")
        driver.save_screenshot("selenium-failure.png")
        sys.exit(1)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
