import asyncio
import aiohttp
import config
import chunker
import database

async def initiate_resumable_session(auth_token, file_name, file_size):
    """Tells Google Drive we want to start a resumable upload."""
    url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Upload-Content-Length": str(file_size)
    }
    metadata = {"name": file_name}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=metadata) as response:
            if response.status == 200:
                return response.headers.get("Location")
            else:
                text = await response.text()
                raise Exception(f"Failed to initiate Google session: {response.status} - {text}")

async def upload_file_sequentially(file_path, auth_token, file_size):
    """
    Uploads chunks for a single file one-by-one to respect Google's sequential requirements,
    but utilizes async network I/O to maximize pipeline speed.
    """
    async with aiohttp.ClientSession() as session:
        while True:
            # Pull the next chunk. database.py will give them in order of chunk_index
            task = database.get_next_pending_chunk(file_path)
            if not task:
                break # All chunks for this file are done!
                
            chunk_id, session_uri, chunk_index, start_byte, end_byte = task
            print(f"🚀 Pushing chunk {chunk_index + 1} / Sequential Pipeline ({start_byte} to {end_byte})...")
            
            data = chunker.get_chunk_bytes(file_path, start_byte, end_byte)
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Range": f"bytes {start_byte}-{end_byte}/{file_size}",
                "Content-Length": str(len(data))
            }
            
            attempt = 0
            success = False
            backoff = 1
            
            while attempt < 3 and not success:
                try:
                    async with session.put(session_uri, headers=headers, data=data) as response:
                        # 308 Resume Incomplete or 200/201 OK means Google accepted it!
                        if response.status in [200, 201, 308]:
                            database.update_chunk_status(chunk_id, "COMPLETED")
                            success = True
                        elif response.status == 429:
                            await asyncio.sleep(backoff)
                            backoff *= 2
                            attempt += 1
                        else:
                            text = await response.text()
                            print(f"❌ Error {response.status} on chunk {chunk_index}: {text}")
                            attempt += 1
                except Exception as e:
                    print(f"⚠️ Network glitch on chunk {chunk_index}: {e}")
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    attempt += 1
            
            if not success:
                database.update_chunk_status(chunk_id, "FAILED")
                print(f"🛑 Chunk {chunk_index} failed permanently. Run the script again to resume.")
                return False
    return True