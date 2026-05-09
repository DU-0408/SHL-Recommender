from playwright.sync_api import sync_playwright
import csv

def scrape_shl_catalog_all_pages(start_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # context = browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36")
        page = browser.new_page()
        page.goto(start_url, timeout=90000, wait_until="domcontentloaded")

        # Wait for the table in the active tab to load
        page.wait_for_selector('.custom__table-responsive table')

        all_results = []

        while True:
            # print(f"Scraping page: {page.url}")

            # Select rows from the table in the active tab
            rows = page.query_selector_all('.custom__table-responsive table tbody tr')

            for row in rows:
                cells = row.query_selector_all('td')
                if len(cells) < 4:
                    continue

                # Extract test name and URL
                name_tag = cells[0].query_selector('a')
                test_name = name_tag.inner_text().strip() if name_tag else "N/A"
                test_url = "https://www.shl.com" + name_tag.get_attribute('href') if name_tag else "N/A"

                # Remote Testing
                remote_circle = cells[1].query_selector('.catalogue__circle')
                remote = 'Yes' if remote_circle and '-yes' in remote_circle.get_attribute('class') else 'No'

                # Adaptive/IRT
                adaptive_circle = cells[2].query_selector('.catalogue__circle')
                adaptive = 'Yes' if adaptive_circle and '-yes' in adaptive_circle.get_attribute('class') else 'No'

                # Test Types
                type_tags = cells[3].query_selector_all('.product-catalogue__key')
                test_types = [t.inner_text().strip() for t in type_tags]

                all_results.append({
                    "Test Name": test_name,
                    "URL": test_url,
                    "Remote Testing": remote,
                    "Adaptive/IRT": adaptive,
                    "Test Types": ', '.join(test_types)
                })

            # Handle pagination
            next_button = page.query_selector('.pagination__item.-arrow.-next a')

            if next_button:
                next_href = next_button.get_attribute('href')
                if not next_href:
                    break  # No more pages
                next_url = "https://www.shl.com" + next_href
                page.goto(next_url, timeout=10000)
                page.wait_for_selector('.custom__table-responsive table')
            else:
                break

        browser.close()
        return all_results

# Start URL
start_url = 'https://www.shl.com/en/solutions/products/product-catalog/'

# Scrape all paginated results
catalog_data = scrape_shl_catalog_all_pages(start_url)

# Save to CSV
if catalog_data:
    with open('../data/raw_data.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=catalog_data[0].keys())
        writer.writeheader()
        writer.writerows(catalog_data)

    print("✅ All pages scraped successfully!")
else:
    print("❌ No data found.")