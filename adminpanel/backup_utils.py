"""
adminpanel/backup_utils.py
Dropbox backup manager for EduTrellis database backups.
Uses the Dropbox OAuth2 credentials already configured in settings.
"""
from __future__ import annotations

import os
import logging
from datetime import datetime
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

BACKUP_FOLDER = "/edutrellis-educational-backup"
DB_PATH = str(Path(settings.BASE_DIR) / "db.sqlite3")


def _get_dbx():
    """Return an authenticated Dropbox client, auto-refreshing the token."""
    try:
        import dropbox  # type: ignore
        dbx = dropbox.Dropbox(
            oauth2_refresh_token=settings.DROPBOX_REFRESH_TOKEN,
            app_key=settings.DROPBOX_APP_KEY,
            app_secret=settings.DROPBOX_APP_SECRET,
        )
        dbx.users_get_current_account()  # validates credentials
        return dbx
    except ImportError:
        raise RuntimeError("dropbox SDK not installed. Run: pip install dropbox")
    except Exception as exc:
        raise RuntimeError(f"Cannot authenticate with Dropbox: {exc}")


def _ensure_folder(dbx) -> None:
    """Create the backup folder on Dropbox if it does not already exist."""
    try:
        import dropbox  # type: ignore
        dbx.files_get_metadata(BACKUP_FOLDER)
    except Exception:
        try:
            import dropbox  # type: ignore
            dbx.files_create_folder_v2(BACKUP_FOLDER)
            logger.info("Created Dropbox folder: %s", BACKUP_FOLDER)
        except Exception as exc:
            # Folder may have been created concurrently – ignore
            logger.warning("Could not create Dropbox folder: %s", exc)


def _human_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 ** 2):.2f} MB"


class DropboxBackupManager:
    """High-level helper for database backup operations on Dropbox."""

    # ------------------------------------------------------------------ #
    #  CREATE                                                              #
    # ------------------------------------------------------------------ #
    @staticmethod
    def create_backup() -> dict:
        """
        Upload db.sqlite3 to Dropbox with a timestamped filename.
        Returns a dict with keys: success, filename, message.
        """
        if not os.path.exists(DB_PATH):
            return {"success": False, "message": f"Database file not found: {DB_PATH}"}

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"edutrellis_backup_{timestamp}.sqlite3"
        dropbox_path = f"{BACKUP_FOLDER}/{filename}"

        try:
            dbx = _get_dbx()
            _ensure_folder(dbx)

            with open(DB_PATH, "rb") as fh:
                data = fh.read()

            import dropbox  # type: ignore
            dbx.files_upload(
                data,
                dropbox_path,
                mode=dropbox.files.WriteMode("overwrite"),
            )
            file_size = _human_size(len(data))
            logger.info("Backup uploaded: %s (%s)", dropbox_path, file_size)
            return {
                "success": True,
                "filename": filename,
                "message": f"Backup '{filename}' ({file_size}) uploaded successfully.",
            }
        except Exception as exc:
            logger.error("Backup failed: %s", exc)
            return {"success": False, "message": str(exc)}

    # ------------------------------------------------------------------ #
    #  LIST                                                                #
    # ------------------------------------------------------------------ #
    @staticmethod
    def list_backups() -> list[dict]:
        """
        Return a list of backup dicts sorted newest-first.
        Each dict: filename, path, size_bytes, size_human, modified (datetime).
        """
        try:
            dbx = _get_dbx()
            _ensure_folder(dbx)
            result = dbx.files_list_folder(BACKUP_FOLDER)
            backups = []
            while True:
                for entry in result.entries:
                    import dropbox  # type: ignore
                    if isinstance(entry, dropbox.files.FileMetadata):
                        backups.append({
                            "filename": entry.name,
                            "path": entry.path_lower,
                            "size_bytes": entry.size,
                            "size_human": _human_size(entry.size),
                            "modified": entry.server_modified,
                        })
                if not result.has_more:
                    break
                result = dbx.files_list_folder_continue(result.cursor)

            backups.sort(key=lambda x: x["modified"], reverse=True)
            return backups
        except Exception as exc:
            logger.error("Failed to list backups: %s", exc)
            return []

    # ------------------------------------------------------------------ #
    #  RESTORE                                                             #
    # ------------------------------------------------------------------ #
    @staticmethod
    def restore_backup(filename: str) -> dict:
        """
        Download the specified backup from Dropbox and replace db.sqlite3.
        Returns dict with keys: success, message.
        """
        dropbox_path = f"{BACKUP_FOLDER}/{filename}"
        try:
            dbx = _get_dbx()
            _, response = dbx.files_download(dropbox_path)
            data = response.content

            # Write atomically: write to temp then rename
            tmp_path = DB_PATH + ".tmp_restore"
            with open(tmp_path, "wb") as fh:
                fh.write(data)
            os.replace(tmp_path, DB_PATH)

            logger.info("Database restored from: %s", dropbox_path)
            return {"success": True, "message": f"Database restored from '{filename}' successfully."}
        except Exception as exc:
            logger.error("Restore failed: %s", exc)
            return {"success": False, "message": str(exc)}

    # ------------------------------------------------------------------ #
    #  DOWNLOAD URL (temporary link)                                      #
    # ------------------------------------------------------------------ #
    @staticmethod
    def get_download_url(filename: str) -> dict:
        """
        Return a temporary direct download link (4 hour expiry).
        Returns dict with keys: success, url / message.
        """
        dropbox_path = f"{BACKUP_FOLDER}/{filename}"
        try:
            dbx = _get_dbx()
            link = dbx.files_get_temporary_link(dropbox_path)
            return {"success": True, "url": link.link}
        except Exception as exc:
            logger.error("get_download_url failed: %s", exc)
            return {"success": False, "message": str(exc)}

    # ------------------------------------------------------------------ #
    #  DELETE                                                              #
    # ------------------------------------------------------------------ #
    @staticmethod
    def delete_backup(filename: str) -> dict:
        """
        Permanently delete a backup file from Dropbox.
        Returns dict with keys: success, message.
        """
        dropbox_path = f"{BACKUP_FOLDER}/{filename}"
        try:
            dbx = _get_dbx()
            dbx.files_delete_v2(dropbox_path)
            logger.info("Deleted Dropbox backup: %s", dropbox_path)
            return {"success": True, "message": f"Backup '{filename}' deleted successfully."}
        except Exception as exc:
            logger.error("Delete backup failed: %s", exc)
            return {"success": False, "message": str(exc)}
