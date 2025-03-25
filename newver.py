import os
import requests
import zipfile
import shutil


class Updater:
    def __init__(self, config):
        self.local_version = "0.0.0"
        # Replace with your GitHub repo details
        self.remote_version_url = "https://raw.githubusercontent.com/your-username/your-repo/main/version.txt"
        # Replace with your GitHub repo details
        self.update_url = "https://github.com/your-username/your-repo/releases/latest/download/update.zip"
        self.update_dir = "update_temp"

    def get_remote_version(self):
        """Fetch the remote version from the server."""
        response = requests.get(self.remote_version_url)
        if response.status_code == 200:
            return response.text.strip()
        raise Exception("Failed to fetch remote version.")

    def download_update(self):
        """Download the update file from the server."""
        response = requests.get(self.update_url, stream=True)
        if response.status_code == 200:
            os.makedirs(self.update_dir, exist_ok=True)
            update_file = os.path.join(self.update_dir, "update.zip")
            with open(update_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            return update_file
        raise Exception("Failed to download update.")

    def apply_update(self, update_file):
        """Extract the update and replace existing files."""
        with zipfile.ZipFile(update_file, "r") as zip_ref:
            zip_ref.extractall(self.update_dir)

        # Replace files in the current directory
        for item in os.listdir(self.update_dir):
            s = os.path.join(self.update_dir, item)
            d = os.path.join(os.getcwd(), item)
            if os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

        # Clean up
        shutil.rmtree(self.update_dir)

    def check_for_updates(self):
        """Check for updates and apply them if available."""
        try:
            local_version = self.local_version()
            remote_version = self.get_remote_version()
            print(
                f"Local version: {local_version}, Remote version: {remote_version}")

            if local_version != remote_version:
                print("Update available. Downloading...")
                update_file = self.download_update()
                print("Applying update...")
                self.apply_update(update_file)
                print("Update applied successfully.")
                # Optionally restart the application
                os.execl(sys.executable, sys.executable, *sys.argv)
            else:
                print("No updates available.")
        except Exception as e:
            print(f"Update failed: {e}")
