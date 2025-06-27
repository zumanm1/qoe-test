import os
import time
import tempfile
import shutil
from flask import Blueprint, current_app, send_from_directory, flash, redirect, url_for
from flask_login import login_required, current_user
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image

# Note: We do not need to import User, as the test_client works within the app context

docs_bp = Blueprint('docs', __name__)

def setup_driver():
    """Sets up the headless Chrome WebDriver."""
    current_app.logger.info("Setting up Selenium WebDriver...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        current_app.logger.info("WebDriver setup successful.")
        return driver
    except Exception as e:
        current_app.logger.error(f"Failed to set up WebDriver: {e}", exc_info=True)
        raise

def generate_pdf_brilliantly():
    """
    Generates a PDF of key application pages without causing server deadlocks.
    This is achieved by using Flask's test client to render pages to local
    HTML files, which are then screenshotted by Selenium.
    """
    current_app.logger.info("Starting brilliant PDF generation process...")
    
    # Note: URLs now have trailing slashes to match the routes
    PAGES_TO_CAPTURE = [
        ("Dashboard", "/dashboard/"),
        ("QoE_Simulation", "/simulation/"),
        ("Reports", "/reports/"),
        ("Troubleshooting", "/troubleshooting/"),
        ("QoE_Impact_Dashboard", "/feature04/qoe_impact_dashboard"),
        ("Technical_Deep_Dive", "/feature04/technical-deep-dive"),
    ]
    
    driver = None
    temp_dir = tempfile.mkdtemp()
    current_app.logger.info(f"Created temporary directory for screenshots: {temp_dir}")

    try:
        driver = setup_driver()
        app = current_app._get_current_object()
        
        screenshot_files = []

        # Use the test_client with proper session context
        with app.test_client() as client:
            # Manually set up the session for the current user
            with client.session_transaction() as sess:
                sess['_user_id'] = current_user.id
            for i, (page_name, page_url) in enumerate(PAGES_TO_CAPTURE):
                current_app.logger.info(f"Capturing page: {page_name} ({page_url})")
                
                # Use the test client to get the page content internally
                response = client.get(page_url)
                if response.status_code != 200:
                    current_app.logger.warning(f"Skipping page {page_url} due to status code {response.status_code}")
                    continue

                # Save the rendered HTML to a temporary local file
                html_content = response.data
                temp_html_path = os.path.join(temp_dir, f"page_{i}_{page_name}.html")
                with open(temp_html_path, 'wb') as f:
                    f.write(html_content)

                # Have Selenium open the local file to take a screenshot
                driver.get(f"file://{temp_html_path}")
                time.sleep(1)  # Allow time for rendering complex elements
                
                screenshot_path = os.path.join(temp_dir, f"screenshot_{i}.png")
                driver.save_screenshot(screenshot_path)
                screenshot_files.append(screenshot_path)
                current_app.logger.info(f"Successfully captured screenshot for {page_name}")

        if not screenshot_files:
            current_app.logger.error("No screenshots were captured. Aborting PDF generation.")
            return None

        current_app.logger.info("Compiling screenshots into PDF...")
        image_list = [Image.open(f).convert('RGB') for f in screenshot_files]
        
        docs_dir = os.path.join(app.root_path, 'static', 'docs')
        os.makedirs(docs_dir, exist_ok=True)
        
        pdf_filename = f"Mobile_QoE_Tool_Documentation_{int(time.time())}.pdf"
        pdf_path = os.path.join(docs_dir, pdf_filename)
        
        image_list[0].save(
            pdf_path, "PDF", resolution=100.0, save_all=True, append_images=image_list[1:]
        )
        current_app.logger.info(f"Successfully created PDF: {pdf_filename}")
        return pdf_filename
            
    except Exception as e:
        current_app.logger.error(f"Brilliant PDF generation failed: {e}", exc_info=True)
        return None
    finally:
        if driver:
            driver.quit()
            current_app.logger.info("Selenium WebDriver has been shut down.")
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            current_app.logger.info(f"Cleaned up temporary directory: {temp_dir}")

@docs_bp.route('/download-docs')
@login_required
def download_docs():
    """Generate and serve the documentation PDF directly."""
    current_app.logger.info(f"User '{current_user.username}' initiated documentation download.")
    try:
        pdf_filename = generate_pdf_brilliantly()
        if pdf_filename:
            docs_dir = os.path.join(current_app.root_path, 'static', 'docs')
            return send_from_directory(docs_dir, pdf_filename, as_attachment=True)
        else:
            flash('Failed to generate documentation PDF. Please check the server logs for details.', 'danger')
            return redirect(url_for('dashboard.index'))
    except Exception as e:
        current_app.logger.error(f"Documentation download route failed: {e}", exc_info=True)
        flash('A critical error occurred while generating the documentation. Please contact an administrator.', 'danger')
        return redirect(url_for('dashboard.index'))
