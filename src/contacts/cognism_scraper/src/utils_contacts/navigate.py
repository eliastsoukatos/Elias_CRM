import time
from config import TAB_LOAD_TIME, get_random_batch_size  # ✅ Import dynamic batch size

def open_new_tabs(driver, urls):
    """
    Opens URLs in new tabs in batches and ensures proper navigation.
    Each batch will have a dynamically randomized number of tabs.
    """
    i = 0
    while i < len(urls):
        batch_size = get_random_batch_size()  # ✅ Get a new batch size each time
        batch = urls[i:i + batch_size]  # ✅ Each batch has a different number of tabs
        opened_tabs = []  # Track opened tabs

        for url in batch:
            if not url.startswith("http"):
                print(f"⚠️ Skipping invalid URL: {url}")
                continue

            driver.execute_script("window.open('', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])  
            driver.get(url)
            time.sleep(TAB_LOAD_TIME)
            opened_tabs.append(driver.window_handles[-1])  # Store new tab handles

        yield opened_tabs  # Return only the new tabs opened in this batch
        i += batch_size  # ✅ Move to the next batch
