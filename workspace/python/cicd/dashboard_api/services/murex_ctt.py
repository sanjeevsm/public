import io
import zipfile
import shutil  # used by delete_item / list helpers
from pathlib import Path
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class MurexCTTService:
    """Service for handling Murex CTT (Configuration Transfer Tool) files"""

    def __init__(self, workspace_dir: str = "data/murex_workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    # ── private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _extract_zip_recursive(zip_source, dest_dir: Path, extracted_files: list,
                               nested_zips: list, errors: list):
        """Extract a zip (path or bytes), recursively expanding any nested zips in-memory."""
        try:
            if isinstance(zip_source, (str, Path)):
                zf = zipfile.ZipFile(zip_source, 'r')
            else:
                zf = zipfile.ZipFile(io.BytesIO(zip_source), 'r')
        except zipfile.BadZipFile as e:
            errors.append(f"Bad zip file: {e}")
            return

        with zf:
            for entry in zf.infolist():
                name = entry.filename
                data = zf.read(name)

                if name.lower().endswith('.zip'):
                    nested_zips.append(name)
                    sub_dir = dest_dir / Path(name).parent / Path(name).stem
                    sub_dir.mkdir(parents=True, exist_ok=True)
                    MurexCTTService._extract_zip_recursive(
                        data, sub_dir, extracted_files, nested_zips, errors
                    )
                else:
                    out_path = dest_dir / name
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    out_path.write_bytes(data)
                    extracted_files.append(str(out_path))

    @staticmethod
    def _pack_dir_as_zip(folder: Path, zipped_files: list, errors: list) -> bytes:
        """Pack a directory tree into zip bytes (used for nested zip objects)."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(folder.rglob('*')):
                if path.is_file():
                    zf.write(path, path.relative_to(folder).as_posix())
                    zipped_files.append(str(path))
        return buf.getvalue()

    @staticmethod
    def _add_to_zip(folder: Path, zf, prefix: str, zipped_files: list,
                    nested_zips: list, errors: list):
        """
        Smart add: folders with direct files → recurse as folder entries.
        Folders with only subdirs → each subdir becomes a nested zip.
        """
        items = list(folder.iterdir())
        has_direct_files = any(item.is_file() for item in items)
        for item in sorted(items):
            arcname = f"{prefix}{item.name}"
            if item.is_file():
                zf.write(item, arcname)
                zipped_files.append(str(item))
            elif item.is_dir():
                if has_direct_files:
                    MurexCTTService._add_to_zip(
                        item, zf, arcname + '/', zipped_files, nested_zips, errors
                    )
                else:
                    nested_data = MurexCTTService._pack_dir_as_zip(item, zipped_files, errors)
                    zip_entry = arcname + '.zip'
                    zf.writestr(zip_entry, nested_data)
                    nested_zips.append(zip_entry)

    # ── public API ────────────────────────────────────────────────────────────

    def extract_ctt(self, zip_path: Path, output_dir: Path) -> Dict:
        """
        Extract a CTT zip file, recursively expanding nested zips in-memory.

        Returns a dict with keys: success, extracted_files, nested_zips, errors.
        """
        extracted_files: list = []
        nested_zips: list = []
        errors: list = []
        try:
            dest = output_dir / zip_path.stem
            dest.mkdir(parents=True, exist_ok=True)
            self._extract_zip_recursive(zip_path, dest, extracted_files, nested_zips, errors)
            return {"success": True, "extracted_files": extracted_files,
                    "nested_zips": nested_zips, "errors": errors}
        except Exception as e:
            errors.append(str(e))
            return {"success": False, "extracted_files": extracted_files,
                    "nested_zips": nested_zips, "errors": errors}

    def create_ctt(self, source_dir: Path, output_zip: Path) -> Dict:
        """
        Create a CTT zip from a folder, converting subdirs to nested zips where appropriate.

        Returns a dict with keys: success, zipped_files, nested_zips, errors.
        """
        zipped_files: list = []
        nested_zips: list = []
        errors: list = []
        try:
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
                self._add_to_zip(source_dir, zf, '', zipped_files, nested_zips, errors)
            output_zip.write_bytes(buf.getvalue())
            return {"success": True, "zipped_files": zipped_files,
                    "nested_zips": nested_zips, "errors": errors}
        except Exception as e:
            errors.append(str(e))
            return {"success": False, "zipped_files": zipped_files,
                    "nested_zips": nested_zips, "errors": errors}

    def list_workspace_items(self) -> List[Dict]:
        """List all items in workspace directory"""
        items = []
        
        if not self.workspace_dir.exists():
            return items
        
        for item in self.workspace_dir.iterdir():
            item_info = {
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size": self._get_size(item),
                "modified": item.stat().st_mtime
            }
            items.append(item_info)
        
        return sorted(items, key=lambda x: x["name"])

    def _get_size(self, path: Path) -> int:
        """Get size of file or directory in bytes"""
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        return 0

    def delete_item(self, item_name: str) -> Dict:
        """Delete a file or directory from workspace"""
        item_path = self.workspace_dir / item_name
        
        try:
            if item_path.exists():
                if item_path.is_dir():
                    shutil.rmtree(item_path)
                else:
                    item_path.unlink()
                
                logger.info(f"Deleted: {item_name}")
                return {"success": True, "message": f"Deleted {item_name}"}
            else:
                return {"success": False, "message": f"Item not found: {item_name}"}
        except Exception as e:
            error_msg = f"Error deleting {item_name}: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    def get_directory_tree(self, dir_name: str, max_depth: int = 5) -> Dict:
        """Get directory tree structure"""
        dir_path = self.workspace_dir / dir_name
        
        if not dir_path.exists() or not dir_path.is_dir():
            return {"error": "Directory not found"}
        
        def build_tree(path: Path, depth: int = 0) -> Dict:
            if depth > max_depth:
                return {"name": "...", "type": "truncated"}
            
            tree = {
                "name": path.name,
                "type": "directory" if path.is_dir() else "file",
                "size": path.stat().st_size if path.is_file() else 0
            }
            
            if path.is_dir():
                children = []
                try:
                    for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name)):
                        children.append(build_tree(item, depth + 1))
                    tree["children"] = children
                except PermissionError:
                    tree["error"] = "Permission denied"
            
            return tree
        
        return build_tree(dir_path)
