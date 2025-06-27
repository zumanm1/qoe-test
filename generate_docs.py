import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fpdf import FPDF

# --- Configuration ---
BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin123!"
SCREENSHOTS_DIR = "screenshots"
PDF_FILENAME = "MTN_QoE_Tool_Documentation.pdf"

PAGES_TO_CAPTURE = [
    ("Dashboard", "/dashboard"),
    ("QoE Simulation", "/simulation"),
    ("Reports", "/reports"),
    ("Troubleshooting", "/troubleshooting"),
    ("QoE Impact Dashboard", "/feature04/qoe_impact_dashboard"),
    ("Technical Deep Dive", "/feature04/technical-deep-dive"),
]

def setup_driver():
    """Set up the Chrome WebDriver."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def login(driver):
    """Log into the application."""
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 10)
    
    # Wait for the login form elements to be present and interactable
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")))
    
    username_field.send_keys(ADMIN_USERNAME)
    password_field.send_keys(ADMIN_PASSWORD)
    submit_button.click()
    
    # Wait for the dashboard to load after login, indicating a successful login
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.h2"))) # Assumes dashboard has a <h1> element

def capture_screenshots(driver):
    """Capture screenshots of all specified pages."""
    if not os.path.exists(SCREENSHOTS_DIR):
        os.makedirs(SCREENSHOTS_DIR)

    wait = WebDriverWait(driver, 10)

    for i, (page_name, page_url) in enumerate(PAGES_TO_CAPTURE):
        print(f"Capturing {page_name}...")
        driver.get(f"{BASE_URL}{page_url}")
        # Wait for the footer to be present to ensure the page is loaded
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "footer")))
        # A small extra delay for any dynamic content like charts to render
        time.sleep(1)
        # Use a more descriptive filename
        safe_page_name = page_name.replace(' ', '_').lower()
        driver.save_screenshot(os.path.join(SCREENSHOTS_DIR, f"screenshot_{i}_{safe_page_name}.png"))

def create_pdf():
    """Create a PDF from the captured screenshots."""
    pdf = FPDF(orientation='P', unit='mm', format='a4')
    # Get screenshots in the order they were taken
    screenshot_files = sorted(
        [f for f in os.listdir(SCREENSHOTS_DIR) if f.startswith('screenshot_') and f.endswith('.png')],
        key=lambda f: int(f.split('_')[1])
    )

    for i, filename in enumerate(screenshot_files):
        page_title = PAGES_TO_CAPTURE[i][0]
        print(f"Adding {filename} ({page_title}) to PDF...")
        pdf.add_page()
        
        # Add a title
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, page_title, 0, 1, 'C')
        pdf.ln(5)

        image_path = os.path.join(SCREENSHOTS_DIR, filename)
        # A4 size is 210x297mm. Place image below title.
        pdf.image(image_path, x=10, y=25, w=190)

    print(f"Saving PDF to {PDF_FILENAME}...")
    pdf.output(PDF_FILENAME)

def main():
    """Main function to generate the documentation PDF."""
    driver = setup_driver()
    try:
        login(driver)
        capture_screenshots(driver)
        create_pdf()
        print("\nDocumentation PDF generated successfully!")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
