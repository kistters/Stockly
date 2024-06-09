# Stockly

## Introduction
API to retrieve and aggregate stock data from external sources and purchase.

### Prerequisites
- docker & docker-compose

### Start & Test Steps
1. **Clone and Navigate to the project:**
    ```bash
    git clone git@github.com:kistters/Stockly.git
    cd Stockly
    ```
2. **Environments:**
    ```bash
    cp .env.example .env # check if you have credential to replace 
    
    ```
3. **Build & Run the project:**
    ```bash
    make start
    ```

## Step-by-Step Guide to Check the API
A step-by-step guide to help you interact and test the Stockly API.

1. **Ensure the server is running:**
    Navigate to `http://127.0.0.1:8000/` in your web browser. Not Found page expected.
2. **Consulting first stock:**
    Navigate to `http://127.0.0.1:8000/stock/AMZN/` in your web browser or use a tool like Postman.
3. **Make a stock purchase**
    Open another terminal, then run:
    ```bash
    make new-purchased-amount AMOUNT=185.9 # will make a request using curl
    ```

## Useful
- **Run Test:**
    ```bash
    make test
    ```
- **interact with containers:**
    ```bash
    make backend-bash
    make redis-cli
    ```

## Access Selenium Grid
With the docker image `selenium/standalone-chrome:4.13.0` is possible use VNC to monitor the browser.
1. **Selenium Grid overview:**
    Navigate to `http://0.0.0.0:4444/` in your web browser.
2. **VNC connection:**
    Navigate to `http://0.0.0.0:7900/` in your web browser. The password is "secret". :D


## Troubleshooting
- **Marketwatch CAPTCHA issue:**
    I was randomly required to solve a CAPTCHA during the Selenium scraper. 
    After some testing and initial failures, I discovered a cookie within the `.marketwatch.com` domain called 'datadome'. 
    Here’s how to update it:

1. Open your usual Chrome browser and navigate to `https://www.marketwatch.com/investing/stock/AAPL`.
2. Open the Developer Tools (F12 or right-click and select "Inspect"), go to the "Application" tab on the left bar, and then search through the cookies under the `https://www.marketwatch.com` domain.
3. Find the cookie named "datadome" and copy the Cookie Value.
4. Go back to the base folder of the repository and locate a file called `cookies.json`.
5. Inside the JSON file, search for the "datadome" entry and replace its value with the one you copied.
6. Try `http://127.0.0.1:8000/stock/AMZN/` again.

This should help you bypass the CAPTCHA issue.


## Technology Choices
Explanation of why Django and Selenium were chosen for the project.

### Why Django?
- **Scalability:** Django’s design encourages clean, pragmatic design and rapid development.
- **Security:** Django includes built-in protection against many common security threats.
- **Knowledge :** I'm use to Django and love the features.

### Why Selenium?
- **Browser:** Selenium is a powerful tool for controlling a web browser, in the project case, Chrome.
- **Javascript:** Scraper on MarketWatch is possible, `requests.get` do not execute javascript.

## Future Improvements
List future improvements and features you plan to implement.

1. **Include DRF for Authentication and API Layer:**
    - Implement Django Rest Framework (DRF) to provide a robust API layer with token-based authentication.
    - Potentially add OAuth or JWT for more secure authentication.

2. **Include Logged-in User to StockRecord:**
    - Modify the StockRecord model to associate each record with the currently logged-in user.
    - Update views, serializers, and forms to handle the new relationship.
