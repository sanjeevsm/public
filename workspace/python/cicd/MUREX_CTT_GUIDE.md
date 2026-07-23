# Murex CTT Import/Export Guide

## Overview

The CI/CD Dashboard now includes functionality to handle Murex Configuration Transfer Tool (CTT) files with automatic extraction and creation of nested zip structures.

## Features

### 1. Extract CTT
- Upload a Murex CTT zip file
- Automatically extracts nested zip files recursively
- Creates folder structure matching zip file names (without .zip extension)
- Handles any depth of nested zips

### 2. Create CTT
- Select a folder from workspace
- Creates a CTT zip file with nested zips for subdirectories
- Maintains original Murex CTT structure
- Generates timestamped output files

### 3. Workspace Management
- View all extracted folders and created CTT files
- Download created CTT zip files
- Delete files and folders
- See file sizes and modification dates

## Getting Started

### Prerequisites

1. **Start the Dashboard**
   ```powershell
   cd python/cicd
   .\scripts\start.ps1
   ```

2. **Access the Dashboard**
   Open browser: http://localhost:8090

3. **Navigate to Murex CTT Tab**
   Click on "Murex CTT" in the navigation bar

## Usage Instructions

### Extract a CTT File

1. **Upload Method 1: Click to Select**
   - Click on the upload zone
   - Select your .zip file (e.g., DM_CTT.zip)
   - Maximum file size: 500MB

2. **Upload Method 2: Drag & Drop**
   - Drag your .zip file over the upload zone
   - Drop when the zone is highlighted

3. **Extract**
   - Click the "Extract CTT" button
   - Wait for the extraction to complete
   - Check the workspace section for extracted folders

### Example: DM_CTT.zip Structure

**Original Zip:**
```
DM_CTT.zip
├── datamart/
│   ├── CM.408.zip      (nested zip)
│   ├── CM.417.zip      (nested zip)
│   └── CM.1517.zip     (nested zip)
├── cmf_templates/
│   └── DM_CTT.xml
└── version.properties
```

**After Extraction:**
```
DM_CTT/                 (folder created from zip name)
├── datamart/
│   ├── CM.408/         (extracted from CM.408.zip)
│   │   └── [files]
│   ├── CM.417/         (extracted from CM.417.zip)
│   │   └── [files]
│   └── CM.1517/        (extracted from CM.1517.zip)
│       └── [files]
├── cmf_templates/
│   └── DM_CTT.xml
└── version.properties
```

**Key Points:**
- Nested zips are automatically detected and extracted
- Folder names match zip names (without .zip extension)
- Original nested zip files are removed after extraction
- All directory structures are preserved

### Create a CTT File

1. **Select Folder**
   - Use the dropdown to select an extracted folder
   - Click the refresh icon to update the folder list

2. **Create CTT**
   - Click "Create CTT" button
   - Wait for the creation process to complete
   - A new zip file will appear in the workspace with timestamp

3. **Download**
   - Click the "Download" button next to the created zip file
   - File will be downloaded to your browser's download folder

### Example: Creating CTT from Folder

**Folder Structure:**
```
DM_CTT/
├── datamart/
│   ├── CM.408/
│   ├── CM.417/
│   └── CM.1517/
├── cmf_templates/
│   └── DM_CTT.xml
└── version.properties
```

**Created CTT (DM_CTT_20260108_153045.zip):**
```
DM_CTT_20260108_153045.zip
├── datamart/
│   ├── CM.408.zip      (created from CM.408 folder)
│   ├── CM.417.zip      (created from CM.417 folder)
│   └── CM.1517.zip     (created from CM.1517 folder)
├── cmf_templates/
│   └── DM_CTT.xml
└── version.properties
```

**Key Points:**
- Subdirectories are automatically converted to nested zips
- Files in the root folder are added directly to the zip
- Timestamp is added to prevent filename conflicts
- Original folder structure is preserved

## Workspace Management

### View Items
- All files and folders appear in the Workspace section
- 📁 icon = folder
- 📦 icon = zip file
- Size and modification date shown for each item

### Download Files
- Available for .zip files only
- Click "Download" button
- File opens in browser or downloads based on browser settings

### Delete Items
- Click "Delete" button for any file or folder
- Confirm deletion in the dialog
- Deleted items are permanently removed

### Refresh Workspace
- Click the "🔄 Refresh" button in workspace header
- Updates the list of files and folders
- Useful after external changes to workspace directory

## API Endpoints

The Murex CTT functionality exposes the following REST APIs:

### GET /api/murex/workspace
Lists all items in the Murex workspace

**Response:**
```json
{
  "success": true,
  "items": [
    {
      "name": "DM_CTT",
      "type": "directory",
      "size": 1524288,
      "modified": 1704723045.123
    },
    {
      "name": "DM_CTT_20260108_153045.zip",
      "type": "file",
      "size": 524288,
      "modified": 1704723145.456
    }
  ],
  "workspace_path": "C:/Users/.../workspace/python/cicd/data/murex_workspace"
}
```

### POST /api/murex/extract
Extracts CTT zip file with nested zip handling

**Request:** multipart/form-data with file upload

**Response:**
```json
{
  "success": true,
  "message": "Successfully extracted DM_CTT.zip",
  "details": {
    "total_files": 15,
    "nested_zips_found": 3,
    "errors": []
  }
}
```

### POST /api/murex/create?folder_name={folder}
Creates CTT zip from folder structure

**Response:**
```json
{
  "success": true,
  "message": "Successfully created CTT: DM_CTT_20260108_153045.zip",
  "filename": "DM_CTT_20260108_153045.zip",
  "details": {
    "total_files": 15,
    "nested_zips_created": 3,
    "size_bytes": 524288
  }
}
```

### GET /api/murex/download/{filename}
Downloads a file from workspace

**Response:** File download (application/zip)

### DELETE /api/murex/delete/{item_name}
Deletes a file or folder from workspace

**Response:**
```json
{
  "success": true,
  "message": "Deleted DM_CTT"
}
```

### GET /api/murex/tree/{dir_name}
Gets directory tree structure (up to 5 levels deep)

**Response:**
```json
{
  "success": true,
  "tree": {
    "name": "DM_CTT",
    "type": "directory",
    "children": [
      {
        "name": "datamart",
        "type": "directory",
        "children": [...]
      }
    ]
  }
}
```

## Technical Details

### File Processing

**Extraction Algorithm:**
1. Create folder named after zip file (without .zip)
2. Extract all contents to the folder
3. Scan for nested .zip files
4. Recursively extract each nested zip
5. Remove nested zip files after extraction
6. Return statistics (total files, nested zips, errors)

**Creation Algorithm:**
1. Create temporary directory for intermediate zips
2. For each subdirectory, create a nested zip recursively
3. Add all files and nested zips to main zip
4. Clean up temporary files
5. Return created zip with timestamp

### Workspace Location
- Default: `python/cicd/data/murex_workspace/`
- Configurable via `MurexCTTService` initialization
- Automatically created if doesn't exist

### File Size Limits
- Upload: 500MB maximum
- No limit on extraction size (limited by disk space)
- Progress indicators shown during operations

### Error Handling
- Invalid zip files: Clear error messages
- Corrupt nested zips: Logs error, continues with others
- Permission errors: Displayed to user
- Network errors: Automatic retry with timeout

## Troubleshooting

### Dashboard Not Loading

**Problem:** Browser shows "Connection refused" or blank page

**Solution:**
```powershell
# Check if services are running
Get-Process | Where-Object {$_.ProcessName -like "*uvicorn*"}

# If not running, start the dashboard
cd python/cicd
.\scripts\start.ps1

# Check logs for errors
Get-Content data/api.log -Tail 50
Get-Content data/api-error.log -Tail 50
```

### Upload Fails

**Problem:** File upload shows error or hangs

**Possible Causes & Solutions:**

1. **File too large (>500MB)**
   - Split the CTT into smaller parts
   - Or increase limit in code (services/murex_ctt.py)

2. **Invalid zip file**
   - Verify zip file is not corrupted
   - Try opening it with WinZip/7-Zip first

3. **Permissions issue**
   - Check workspace directory permissions
   - Run PowerShell as Administrator if needed

### Extraction Fails

**Problem:** Extraction starts but shows errors

**Possible Causes & Solutions:**

1. **Nested zip is corrupted**
   - Check error details in response
   - Extract main zip manually to identify bad file
   - Fix or remove corrupted nested zip

2. **Disk space full**
   - Check available disk space
   - Clean up old extractions from workspace

3. **Special characters in filenames**
   - Rename zip file to use only alphanumeric characters
   - Avoid spaces and special characters

### Create CTT Fails

**Problem:** CTT creation shows error

**Possible Causes & Solutions:**

1. **Folder not found**
   - Refresh folder list
   - Check if folder was deleted externally

2. **Permission denied**
   - Close any programs using files in the folder
   - Check folder is not read-only

3. **Empty folder**
   - Ensure folder has at least one file
   - Empty folders are skipped

### Murex Tab Not Visible

**Problem:** "Murex CTT" tab doesn't appear in navigation

**Solution:**
```powershell
# Check if Murex router is registered
cd python/cicd/dashboard_api
# Verify main.py includes:
# from routers import murex
# app.include_router(murex.router, prefix="/api")

# Restart the dashboard
cd ..
.\scripts\stop.ps1
.\scripts\start.ps1
```

### Workspace Empty After Extraction

**Problem:** Files extracted but workspace shows empty

**Solution:**
```powershell
# Check workspace directory
dir data/murex_workspace

# If files are there, refresh the page
# Click "🔄 Refresh" button in workspace

# Check for JavaScript errors in browser console (F12)
```

## Best Practices

### 1. File Naming
- Use descriptive names for CTT files
- Avoid spaces and special characters
- Keep names under 255 characters

### 2. Workspace Organization
- Regularly clean up old extractions
- Use meaningful folder names
- Keep related CTTs together

### 3. Performance
- Extract large CTTs during off-peak hours
- Close other applications during processing
- Monitor disk space usage

### 4. Security
- Do not upload sensitive data without proper authorization
- Clean up workspace after each session
- Use strong GitLab tokens with limited scope

### 5. Backup
- Keep original CTT files in a safe location
- Test extraction before deleting originals
- Verify created CTTs before deploying

## Advanced Usage

### Programmatic Access

You can use the API endpoints directly with curl or any HTTP client:

```powershell
# List workspace
curl http://localhost:8090/api/murex/workspace

# Extract CTT
curl -X POST -F "file=@DM_CTT.zip" http://localhost:8090/api/murex/extract

# Create CTT
curl -X POST http://localhost:8090/api/murex/create?folder_name=DM_CTT

# Download CTT
curl -O http://localhost:8090/api/murex/download/DM_CTT_20260108_153045.zip

# Delete item
curl -X DELETE http://localhost:8090/api/murex/delete/DM_CTT
```

### Batch Processing

Extract multiple CTTs:
```python
import requests

ctt_files = ['CTT1.zip', 'CTT2.zip', 'CTT3.zip']

for ctt_file in ctt_files:
    with open(ctt_file, 'rb') as f:
        response = requests.post(
            'http://localhost:8090/api/murex/extract',
            files={'file': f}
        )
        print(f"{ctt_file}: {response.json()}")
```

Create multiple CTTs:
```python
import requests

folders = ['DM_CTT', 'PM_CTT', 'RM_CTT']

for folder in folders:
    response = requests.post(
        f'http://localhost:8090/api/murex/create',
        params={'folder_name': folder}
    )
    result = response.json()
    print(f"{folder}: {result['filename']}")
```

## Support

For issues or questions:
1. Check this guide first
2. Review error messages in browser console (F12)
3. Check log files in `python/cicd/data/` directory
4. Contact the development team

## Version History

**v1.0.0** (2026-01-08)
- Initial release
- Extract CTT with nested zip handling
- Create CTT from folder structure
- Workspace management
- Drag & drop file upload
- Progress indicators
- Error handling and validation
