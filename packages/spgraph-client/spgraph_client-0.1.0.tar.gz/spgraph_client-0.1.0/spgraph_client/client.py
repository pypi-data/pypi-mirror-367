import os
import requests
import pandas as pd


class SharePointClient:
    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        site_domain: str,
        site_name: str,
        drive_name: str = "Documents",
    ):
        """
        Initialize SharePointClient with authentication and site details.
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.site_domain = site_domain
        self.site_name = site_name
        self.drive_name = drive_name
        self.token = None
        self.site_id = None
        self.drive_id = None

    def get_access_token(self) -> str:
        """Retrieve OAuth2 access token for Microsoft Graph API."""
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": self.client_id,
            "scope": "https://graph.microsoft.com/.default",
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        self.token = response.json().get("access_token")
        return self.token

    def get_headers(self) -> dict:
        """Return authorization headers for Graph API requests."""
        token = self.token or self.get_access_token()
        return {"Authorization": f"Bearer {token}"}

    def get_site_id(self) -> str:
        """Get the SharePoint site ID."""
        url = f"https://graph.microsoft.com/v1.0/sites/{self.site_domain}:/sites/{self.site_name}"
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        self.site_id = response.json().get("id")
        return self.site_id

    def get_drive_id(self) -> str:
        """Get the document library drive ID."""
        if not self.site_id:
            self.get_site_id()
        url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives"
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        for drive in response.json()["value"]:
            if drive["name"] == self.drive_name:
                self.drive_id = drive["id"]
                return self.drive_id
        raise Exception("Drive not found")

    def create_folder(self, folder_name: str) -> dict:
        """Create a folder in the document library."""
        if not self.drive_id:
            self.get_drive_id()
        url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/root/children"
        folder_data = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename",
        }
        response = requests.post(url, headers=self.get_headers(), json=folder_data)
        response.raise_for_status()
        return response.json()

    def upload_file(self, folder_path: str, local_file_path: str) -> tuple:
        """Upload a single file to SharePoint."""
        if not self.drive_id:
            self.get_drive_id()
        file_name = os.path.basename(local_file_path)
        url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/root:/{folder_path}/{file_name}:/content"
        with open(local_file_path, "rb") as file_data:
            response = requests.put(url, headers=self.get_headers(), data=file_data)
        return response.status_code, response.json()

    def upload_multiple_files(self, folder_path: str, file_paths: list) -> list:
        """Upload multiple files to SharePoint."""
        return [(fp, *self.upload_file(folder_path, fp)) for fp in file_paths]

    def download_file(self, sp_file_path: str, local_path: str) -> str:
        """Download a file from SharePoint."""
        if not self.drive_id:
            self.get_drive_id()
        url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/root:/{sp_file_path}:/content"
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(response.content)
        return local_path

    def download_all_files(self, sp_folder_path: str, local_dir: str) -> str:
        """Download all files from a SharePoint folder."""
        if not self.drive_id:
            self.get_drive_id()
        os.makedirs(local_dir, exist_ok=True)
        url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/root:/{sp_folder_path}:/children"
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        for item in response.json().get("value", []):
            if "file" in item:
                file_data = requests.get(item["@microsoft.graph.downloadUrl"])
                with open(os.path.join(local_dir, item["name"]), "wb") as f:
                    f.write(file_data.content)
        return local_dir

    def download_files_with_keyword(self, sp_folder_path: str, keyword: str, local_dir: str) -> str:
        """Download files containing a keyword."""
        if not self.drive_id:
            self.get_drive_id()
        os.makedirs(local_dir, exist_ok=True)
        url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/root:/{sp_folder_path}:/children"
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        for item in response.json().get("value", []):
            if "file" in item and keyword.lower() in item["name"].lower():
                file_data = requests.get(item["@microsoft.graph.downloadUrl"])
                with open(os.path.join(local_dir, item["name"]), "wb") as f:
                    f.write(file_data.content)
        return local_dir

    def download_list(self, list_name: str) -> list:
        """Download all items from a SharePoint list."""
        if not self.site_id:
            self.get_site_id()
        url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/lists/{list_name}/items?expand=fields"
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        return [item["fields"] for item in response.json().get("value", [])]

    def download_list_to_csv(self, list_name: str, csv_path: str) -> str:
        """Download SharePoint list as CSV."""
        df = pd.DataFrame(self.download_list(list_name))
        df.to_csv(csv_path, index=False)
        return csv_path
