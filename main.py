import asyncio
import os
import sys
import time  # Imported for benchmarking
import auth
import database
import chunker
import uploader

async def main_uploader(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return
        
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    file_size_mb = file_size / (1024 * 1024)
    print(f"Target File: {file_name} ({file_size_mb:.2f} MB)")

    print("Fetching Google Credentials...")
    try:
        creds = auth.get_gdrive_credentials()
        auth_token = creds.token
    except Exception as e:
        print(f"Authentication step failed: {e}")
        return

    print("Initializing upload session with Google Drive...")
    try:
        session_uri = await uploader.initiate_resumable_session(auth_token, file_name, file_size)
        print("Session established successfully!")
    except Exception as e:
        print(e)
        return

    print("Calculating chunk map...")
    chunks_plan = chunker.plan_chunks(file_path)
    database.register_chunks(file_path, session_uri, chunks_plan)
    print(f"Total chunks registered: {len(chunks_plan)}")

    print("\nStarting stream pipeline...")
    
    # ⏱️ START THE TIMER right before network activity begins
    start_time = time.time()
    
    success = await uploader.upload_file_sequentially(file_path, auth_token, file_size)
    
    # ⏱️ STOP THE TIMER as soon as the network loop finishes
    end_time = time.time()
    
    if success:
        # Calculate performance metrics
        total_duration = end_time - start_time
        upload_speed = file_size_mb / total_duration if total_duration > 0 else 0
        
        print("\n" + "="*40)
        print("🎉 UPLOAD PERFORMANCE REPORT")
        print("="*40)
        print(f"📁 File Name:      {file_name}")
        print(f"⚖️  File Size:      {file_size_mb:.2f} MB")
        print(f"⏱️  Total Time:     {total_duration:.2f} seconds")
        print(f"⚡ Average Speed:   {upload_speed:.2f} MB/s")
        print("="*40)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_file>")
        sys.exit(1)
        
    target_file = sys.argv[1]
    asyncio.run(main_uploader(target_file))