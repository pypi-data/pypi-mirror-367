import os

def sanitize_output_dir(output_dir):
    # Replace backslashes with forward slashes for cross-platform compatibility
    output_dir = output_dir.replace("\\", "/")
    # Remove leading slashes to prevent absolute paths
    output_dir = output_dir.lstrip("/")
    # Remove drive letters (Windows)
    if os.name == "nt" and len(output_dir) > 1 and output_dir[1] == ":":
        output_dir = output_dir[2:]
    # Normalize path (removes redundant separators, etc.)
    output_dir = os.path.normpath(output_dir)
    return output_dir

def has_column(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns