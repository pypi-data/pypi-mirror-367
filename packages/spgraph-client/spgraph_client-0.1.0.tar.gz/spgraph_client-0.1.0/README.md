# spgraph-client

A Python client for performing SharePoint actions via Microsoft Graph API like download files, SharePoint List or upload files.

## Installation
```bash
pip install spgraph-client
```

## Usage
```python
from spgraph_client import SharePointClient

client = SharePointClient(
    tenant_id="YOUR_TENANT_ID",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    site_domain="example.sharepoint.com",
    site_name="MySite"
)

client.create_folder("Reports")
client.upload_file("Reports", "local_report.pdf")
client.get_file("Reports", "local_report.pdf")
client.get_all_files("Reports", "local_report.pdf")

```
