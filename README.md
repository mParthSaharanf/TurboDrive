# TurboDrive

A fast, lightweight command-line tool to upload large files to Google Drive without browser slowdowns. It splits files into chunks and tracks progress in a local database so uploads can automatically resume if your internet drops.

## Features

* Resumable Uploads: If the network fails mid-upload, the script picks up right where it left off instead of restarting from 0%.
* Zero-RAM Chunking: Streams files from your drive in 8MB chunks without loading the entire file into system memory.
* No UI Bottlenecks: Runs entirely in the terminal, bypassing browser main-thread lag and background tab throttling.

## Performance Benchmark

Tested against the standard Google Drive web interface using a 910.34 MB file:

* Total Duration: 386.14 seconds (~6.4 minutes)
* Average Speed: 2.36 MB/s
* Reliability: Successfully recovered from manual network disconnections during testing without losing progress.

## Setup & Installation

1. Clone the repository:
   git clone https://github.com/mParthSaharanf/TurboDrive.git
   cd TurboDrive

2. Install dependencies:
   pip install aiohttp

3. Add API Credentials:
   Place your Google OAuth credentials.json file in the root directory.

4. Run the tool:
   python main.py /path/to/your/large/file.mkv
