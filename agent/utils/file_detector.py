"""
File type detection utility
"""

def detect_file_type(file_data: bytes) -> str:
    """Detect file type from file content using magic bytes"""
    if not file_data or len(file_data) < 10:
        return "pdf"  # Default
    
    # Check magic bytes
    magic_bytes = {
        b'%PDF': "pdf",
        b'\x89PNG': "png",
        b'\xFF\xD8\xFF': "jpeg",
        b'GIF87a': "gif",
        b'GIF89a': "gif",
        b'BM': "bmp"
    }
    
    for magic, file_type in magic_bytes.items():
        if file_data.startswith(magic):
            return file_type
    
    # Check for Office formats (ZIP-based)
    if file_data.startswith(b'PK'):
        if b'word/' in file_data[:1000]:
            return "docs"
        elif b'xl/' in file_data[:1000]:
            return "sheets"
        elif b'ppt/' in file_data[:1000]:
            return "slides"
        else:
            return "docs"
    
    return "pdf"  # Default