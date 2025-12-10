import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestSmoke:
    """
    Selenium smoke tests for the Teton Idaho Chamber of Commerce site (v1.6).
    These tests correspond to the W06 Automated User Interface Testing assignment.
    """

    def setup_method(self, method):
        options = Options()
        options.add_argument("--headless=new")
        # Create Chrome driver in headless mode
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(5)
        # Base URL for the local Live Server instance
        self.base_url = "http://127.0.0.1:5500/teton/1.6"

    def teardown_method(self, method):
        # Close the browser after each test
        self.driver.quit()

    # Helper to navigate using a relative path
    def go(self, path: str):
        self.driver.get(f"{self.base_url}/{path}")

    # -------------------------
    # 1) Home page basic checks
    # -------------------------
    def test_home_logo_heading_title(self):
        d = self.driver
        self.go("index.html")

        # Verify the site logo is displayed
        logo = d.find_element(By.CSS_SELECTOR, ".header-logo img")
        assert logo.is_displayed()

        # Verify the heading "Teton Idaho" and "Chamber of Commerce" are visible
        h1 = d.find_element(By.CSS_SELECTOR, ".header-title h1")
        h2 = d.find_element(By.CSS_SELECTOR, ".header-title h2")
        assert h1.text.strip() == "Teton Idaho"
        assert h2.text.strip() == "Chamber of Commerce"

        # Verify the browser tab title
        assert d.title == "Teton Idaho CoC"

    # ---------------------------------
    # 2) Home: spotlights and Join link
    # ---------------------------------
    def test_home_spotlights_and_join_link(self):
        d = self.driver
        self.go("index.html")
        d.set_window_size(1200, 900)
        wait = WebDriverWait(d, 10)

        # Verify that at least two spotlight items are present
        def at_least_two_spotlights(driver):
            container = driver.find_element(By.CSS_SELECTOR, ".main-spotlight")
            divs = container.find_elements(By.TAG_NAME, "div")
            return len(divs) >= 2

        wait.until(at_least_two_spotlights)
        container = d.find_element(By.CSS_SELECTOR, ".main-spotlight")
        spotlights = container.find_elements(By.TAG_NAME, "div")
        assert len(spotlights) >= 2

        # Verify the "Join Us" link is present and goes to the join page
        join_link = d.find_element(By.LINK_TEXT, "Join Us!")
        assert join_link.is_displayed()
        join_link.click()

        # After clicking, we should be on the join page
        wait.until(EC.url_contains("join.html"))
        assert "join.html" in d.current_url

    # ------------------------------------------------
    # 3) Directory: grid/list view and specific member
    # ------------------------------------------------
    def test_directory_grid_list_teton_turf(self):
        d = self.driver
        self.go("directory.html")
        wait = WebDriverWait(d, 10)

        grid_btn = d.find_element(By.ID, "directory-grid")
        list_btn = d.find_element(By.ID, "directory-list")

        # Click GRID view and verify "Teton Turf and Tree" appears
        grid_btn.click()

        def teton_turf_present(driver):
            return "Teton Turf and Tree" in driver.page_source

        wait.until(teton_turf_present)
        assert "Teton Turf and Tree" in d.page_source

        # Click LIST view and verify "Teton Turf and Tree" still appears
        list_btn.click()
        wait.until(teton_turf_present)
        assert "Teton Turf and Tree" in d.page_source

    # ---------------------------------------------
    # 4) Join wizard: first page and email on step 2
    # ---------------------------------------------
    def test_join_first_name_and_email_step(self):
        d = self.driver
        self.go("join.html")
        wait = WebDriverWait(d, 10)

        # First Name input box
        first_name = d.find_element(By.NAME, "fname")
        assert first_name.is_displayed()

        # Fill required fields on the first step
        first_name.send_keys("Test")
        d.find_element(By.NAME, "lname").send_keys("User")
        d.find_element(By.NAME, "bizname").send_keys("Test Business")
        d.find_element(By.NAME, "biztitle").send_keys("Owner")

        # Click "Next Step" button
        next_btn = d.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Next Step']")
        next_btn.click()

        # On step 2, the Email input should be present
        wait.until(EC.url_contains("join-step2.html"))
        email_input = wait.until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        assert email_input.is_displayed()

    # -----------------------------------------
    # 5) Admin login: invalid credentials error
    # -----------------------------------------
    def test_admin_invalid_login_shows_error(self):
        d = self.driver
        self.go("admin.html")
        wait = WebDriverWait(d, 10)

        # Username input box is present
        username_input = d.find_element(By.ID, "username")
        password_input = d.find_element(By.ID, "password")
        assert username_input.is_displayed()

        # Fill invalid credentials
        username_input.send_keys("wronguser")
        password_input.send_keys("wrongpass")

        # Click Login button
        login_btn = d.find_element(
            By.CSS_SELECTOR,
            "input[type='button'][value='Login']"
        )
        login_btn.click()

        # Ensure the appropriate error message is displayed
        error_span = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".errorMessage"))
        )
        wait.until(lambda drv: error_span.text != "")
        assert "Invalid username and password." in error_span.text
