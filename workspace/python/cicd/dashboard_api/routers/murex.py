import os
import sys
import subprocess
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import shutil
import logging
from datetime import datetime
from services.murex_ctt import MurexCTTService

router = APIRouter(prefix="/murex", tags=["murex"])
logger = logging.getLogger(__name__)

# Initialize Murex CTT service
murex_service = MurexCTTService()


@router.get("/workspace")
async def list_workspace():
    """List all items in Murex workspace"""
    try:
        items = murex_service.list_workspace_items()
        return {
            "success": True,
            "items": items,
            "workspace_path": str(murex_service.workspace_dir.resolve())
        }
    except Exception as e:
        logger.error(f"Error listing workspace: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract")
async def extract_ctt(file: UploadFile = File(...), extract_to: str = Form(None)):
    """
    Extract Murex CTT zip file to folder structure.
    Automatically handles nested zip files.
    Optional extract_to form field specifies the output directory.
    """
    try:
        # Validate file type
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="Only .zip files are supported")

        # Resolve output directory
        if extract_to and extract_to.strip():
            output_dir = Path(extract_to.strip())
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = murex_service.workspace_dir

        # Save uploaded file temporarily in workspace
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_zip = murex_service.workspace_dir / f"temp_{timestamp}_{file.filename}"

        with temp_zip.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Received file: {file.filename} ({temp_zip.stat().st_size} bytes)")

        # Extract the CTT
        results = murex_service.extract_ctt(temp_zip, output_dir)

        # Remove temporary zip file
        temp_zip.unlink()

        return {
            "success": results["success"],
            "message": f"Successfully extracted {file.filename}",
            "extract_path": str(output_dir),
            "details": {
                "total_files": len(results["extracted_files"]),
                "nested_zips_found": len(results["nested_zips"]),
                "errors": results["errors"]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting CTT: {e}")
        if 'temp_zip' in locals() and temp_zip.exists():
            temp_zip.unlink()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create")
async def create_ctt(folder_path: str):
    """
    Create Murex CTT zip file from folder structure.
    folder_path can be an absolute path or a folder name within the workspace.
    Automatically creates nested zips for subdirectories.
    """
    try:
        path = Path(folder_path)
        source_dir = path if path.is_absolute() else murex_service.workspace_dir / folder_path

        if not source_dir.exists():
            raise HTTPException(status_code=404, detail=f"Folder not found: {folder_path}")

        if not source_dir.is_dir():
            raise HTTPException(status_code=400, detail=f"{folder_path} is not a directory")

        # Create output zip in workspace
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_zip = murex_service.workspace_dir / f"{source_dir.name}_{timestamp}.zip"

        logger.info(f"Creating CTT from folder: {source_dir}")

        results = murex_service.create_ctt(source_dir, output_zip)

        if not results["success"]:
            raise HTTPException(status_code=500, detail="; ".join(results["errors"]))

        return {
            "success": True,
            "message": f"Successfully created CTT: {output_zip.name}",
            "filename": output_zip.name,
            "details": {
                "total_files": len(results["zipped_files"]),
                "nested_zips_created": len(results["nested_zips"]),
                "size_bytes": output_zip.stat().st_size
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating CTT: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/browse")
async def browse_directories(path: str = ""):
    """Browse filesystem directories for folder selection"""
    try:
        if not path:
            # On Windows list available drives; elsewhere start from home
            if os.name == 'nt':
                drives = []
                for d in range(65, 91):
                    drive = f"{chr(d)}:\\"
                    if os.path.exists(drive):
                        drives.append({"name": drive, "path": drive})
                return {"success": True, "path": "", "dirs": drives, "parent": None}
            else:
                browse_path = Path.home()
        else:
            browse_path = Path(path)

        if not browse_path.exists() or not browse_path.is_dir():
            raise HTTPException(status_code=404, detail=f"Path not found: {path}")

        dirs = []
        try:
            for item in sorted(browse_path.iterdir(), key=lambda x: x.name.lower()):
                if item.is_dir() and not item.name.startswith('.'):
                    dirs.append({"name": item.name, "path": str(item)})
        except PermissionError:
            pass

        parent_path = browse_path.parent
        parent = str(parent_path) if str(parent_path) != str(browse_path) else None

        return {
            "success": True,
            "path": str(browse_path),
            "dirs": dirs,
            "parent": parent
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error browsing directory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{filename}")
async def download_file(filename: str):
    """Download a file from workspace"""
    try:
        file_path = murex_service.workspace_dir / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")

        if not file_path.is_file():
            raise HTTPException(status_code=400, detail=f"{filename} is not a file")

        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/zip"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{item_name}")
async def delete_item(item_name: str):
    """Delete a file or folder from workspace"""
    try:
        result = murex_service.delete_item(item_name)

        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/open-folder")
async def open_folder(path: str):
    """Open a folder in the system file explorer"""
    try:
        folder_path = Path(path).resolve()

        if not folder_path.exists():
            raise HTTPException(status_code=404, detail=f"Path not found: {path}")

        if folder_path.is_file():
            folder_path = folder_path.parent

        if os.name == 'nt':
            subprocess.Popen(['explorer', str(folder_path)])
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', str(folder_path)])
        else:
            subprocess.Popen(['xdg-open', str(folder_path)])

        return {"success": True, "message": f"Opened folder: {folder_path}"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error opening folder: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tree/{dir_name}")
async def get_directory_tree(dir_name: str):
    """Get directory tree structure"""
    try:
        tree = murex_service.get_directory_tree(dir_name)

        if "error" in tree:
            raise HTTPException(status_code=404, detail=tree["error"])

        return {
            "success": True,
            "tree": tree
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting directory tree: {e}")
        raise HTTPException(status_code=500, detail=str(e))
