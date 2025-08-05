import os
import psutil
import zipfile
import xml.etree.ElementTree as ET

def read_xlsx_full_content(filepath, max_memory_mb=2048):
    content = []
    try:
        with zipfile.ZipFile(filepath) as archive:
            if 'xl/sharedStrings.xml' in archive.namelist():
                shared_strings = []
                tree = ET.parse(archive.open('xl/sharedStrings.xml'))
                root = tree.getroot()
                for si in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'):
                    shared_strings.append(si.text or "")
            else:
                shared_strings = None

            for name in archive.namelist():
                if name.startswith('xl/worksheets/sheet') and name.endswith('.xml'):
                    tree = ET.parse(archive.open(name))
                    root = tree.getroot()
                    for cell in root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v'):
                        if shared_strings:
                            index = int(cell.text)
                            content.append(shared_strings[index])
                        else:
                            content.append(cell.text or "")
                        if psutil.Process(os.getpid()).memory_info().rss > max_memory_mb * 1024 * 1024:
                            return ' '.join(content)
    except Exception as e:
        return f"Error: {e}"
    return ' '.join(content)

def read_xlsx_preview_3000_chars(filepath, char_limit=3000):
    data = read_xlsx_full_content(filepath)
    return data[:char_limit]
