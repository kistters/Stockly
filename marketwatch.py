from selenium import webdriver

options = webdriver.FirefoxOptions()

driver = webdriver.Remote(
    command_executor="http://127.0.0.1:4444",
    options=options
)

driver.get('https://www.marketwatch.com/investing/stock/aapl')

screenshot_path = '01-marketwatch-aapl-screenshot.png'
driver.save_screenshot(screenshot_path)
with open('01-marketwatch.aapl.selenium.html', 'w', encoding='utf-8') as file:
    file.write(driver.page_source)

driver.quit()
