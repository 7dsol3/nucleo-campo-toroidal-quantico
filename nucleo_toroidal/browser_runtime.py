"""Seleção portátil do navegador para QA; não acessa perfis pessoais."""
import os,shutil
from pathlib import Path

def launch_browser(playwright, **options):
    options={'headless':True,**options}
    explicit=os.environ.get('NUCLEO_BROWSER_PATH')
    if explicit:
        path=Path(explicit).expanduser()
        if not path.is_file():raise FileNotFoundError('NUCLEO_BROWSER_PATH não aponta para um executável')
        return playwright.chromium.launch(executable_path=str(path),**options)
    candidates=[r'C:\Program Files\Google\Chrome\Application\chrome.exe',r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe','/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    candidates += [shutil.which(name) for name in ['google-chrome','google-chrome-stable','chromium','chromium-browser','chrome']]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():return playwright.chromium.launch(executable_path=candidate,**options)
    return playwright.chromium.launch(**options)
