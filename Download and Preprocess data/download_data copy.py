import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
from urllib.parse import urljoin
import concurrent.futures
from tqdm import tqdm


START_DATE = "2010-05-13"
END_DATE = "2025-01-01"
DOWNLOAD_DIR = "D:/aia_synoptic_data"
WAVELENGTH = "0193"
MAX_WORKERS = 20


def find_files_in_directory(url):
    """Find files ending with specified wavelength in the directory."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        target_suffix = f"_{WAVELENGTH}.fits"
        files = []
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if href.endswith(target_suffix):
                files.append(href)
        return sorted(files)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return []
        print(f"Error accessing {url}: {e}")
        return []
    except Exception as e:
        print(f"Error accessing {url}: {e}")
        return []


def download_file(file_url, local_path):
    """Download a file with retries and error handling."""
    if os.path.exists(local_path):
        return "exists"
    try:
        with requests.get(file_url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return "success"
    except Exception as e:
        return f"error: {e}"


def generate_file_urls():
    """Generate list of file URLs based on hardcoded dates with parallel processing."""
    file_urls = []
    start_date = datetime.strptime(START_DATE, "%Y-%m-%d")
    end_date = datetime.strptime(END_DATE, "%Y-%m-%d")

    def process_hour(date, hour):
        """Process a specific date and hour to find and prepare file URLs."""
        # Generate expected filename based on the date pattern
        # Format: AIA20140505_0500_0193.fits
        expected_filename = f"AIA{date.strftime('%Y%m%d')}_{hour:02d}00_{WAVELENGTH}.fits"
        local_path = os.path.join(DOWNLOAD_DIR, expected_filename)

        # Skip network request if file already exists
        if os.path.exists(local_path):
            return []

        # Only if file doesn't exist, proceed to check online
        year, month, day = date.year, date.month, date.day
        dir_url = f"https://jsoc1.stanford.edu/data/aia/synoptic/{year:04d}/{month:02d}/{day:02d}/H{hour:02d}10/"
        files = find_files_in_directory(dir_url)
        results = []
        if files:
            selected_file = files[0]
            file_url = urljoin(dir_url, selected_file)
            local_filename = os.path.join(DOWNLOAD_DIR, selected_file)
            results.append((file_url, local_filename))
        return results

    # Calculate total tasks for progress tracking
    total_days = (end_date - start_date).days + 1
    total_tasks = total_days * 24  # 24 hours per day

    tasks = []
    current_date = start_date
    while current_date <= end_date:
        for hour in range(24):
            tasks.append((current_date, hour))
        current_date += timedelta(days=1)

    with tqdm(total=total_tasks, desc="Generating URLs") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(process_hour, date, hour): (date, hour)
                       for date, hour in tasks}

            for future in concurrent.futures.as_completed(futures):
                date, hour = futures[future]
                try:
                    results = future.result()
                    file_urls.extend(results)
                except Exception as e:
                    print(
                        f"Error processing {date.isoformat()} hour {hour}: {e}")
                pbar.update(1)

    return file_urls


def main():
    """Main download execution with progress tracking."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    print("Generating file URLs...")
    file_urls = generate_file_urls()

    print(f"Total files to download: {len(file_urls)}")
    print(f"Saving to: {os.path.abspath(DOWNLOAD_DIR)}")

    with tqdm(total=len(file_urls), desc="Downloading") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(download_file, url, path): (
                url, path) for url, path in file_urls}

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                url, path = futures[future]
                filename = os.path.basename(path)

                if result == "exists":
                    pbar.set_postfix_str(f"Skipped: {filename}", refresh=False)
                elif "error" in result:
                    pbar.set_postfix_str(f"Failed: {filename}", refresh=False)
                else:
                    pbar.set_postfix_str(f"Done: {filename}", refresh=False)

                pbar.update(1)


if __name__ == "__main__":
    main()
