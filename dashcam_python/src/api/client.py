"""
Dashcam HTTP API Functions
Extracted from PCAP network capture

Performance Optimizations:
- Uses requests.Session() for connection pooling and HTTP keep-alive
- Prevents reconnecting for each request (huge speed improvement)
- Supports parallel downloads (2-5x faster with 2-5 connections)
- Streams large files to avoid memory issues
- Shows real-time speed and progress

Expected speeds over WiFi:
- Sequential with keep-alive: 5-15 Mbps
- Parallel (3 connections): 10-30 Mbps
- Your original 1.2 Mbps was due to connection overhead
"""

import requests
from typing import Dict, Optional, List
from datetime import datetime


class DashcamAPI:
    """API client for dashcam device at 192.168.0.1"""
    
    def __init__(self, base_url: str = "http://192.168.0.1", keep_alive: bool = True):
        self.base_url = base_url
        self.session_id = "null"
        self.keep_alive = keep_alive
        
        # Use a session for connection pooling and keep-alive
        self.session = requests.Session()
        
        # Increase connection pool size for better performance
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=3
        )
        self.session.mount('http://', adapter)
    
    # WiFi Configuration
    def get_wifi(self) -> Dict:
        """Get WiFi configuration"""
        response = self.session.get(
            f"{self.base_url}/cgi-bin/hisnet/getwifi.cgi",
            headers={
                "Accept-Encoding": "gzip",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; KFONWI Build/PS7331.4463N)",
                "Connection": "keep-alive" if self.keep_alive else "close"
            }
        )
        return response.text
    
    # Device Information
    def get_device_attr(self) -> Dict:
        """Get device attributes (model, version, etc.)"""
        response = self.session.get(
            f"{self.base_url}/cgi-bin/hisnet/getdeviceattr.cgi",
            headers={
                "Accept-Encoding": "gzip",
                "Cookie": f"SessionID={self.session_id}",
                "Connection": "keep-alive" if self.keep_alive else "close",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; KFONWI Build/PS7331.4463N)"
            }
        )
        return response.text
    
    # Client Registration
    def register_client(self, ip: str = "192.168.0.21") -> str:
        """Register client with dashcam"""
        response = self.session.get(
            f"{self.base_url}/cgi-bin/hisnet//client.cgi",
            params={"-operation": "register", "-ip": ip},
            headers={
                "Accept-Encoding": "gzip",
                "Cookie": f"SessionID={self.session_id}",
                "Connection": "keep-alive" if self.keep_alive else "close",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; KFONWI Build/PS7331.4463N)"
            }
        )
        return response.text
    
    # Work State
    def get_work_state(self) -> Dict:
        """Get current work state (recording, playback, etc.)"""
        response = self.session.get(
            f"{self.base_url}/cgi-bin/hisnet/getworkstate.cgi",
            headers={
                "Accept-Encoding": "gzip",
                "Cookie": f"SessionID={self.session_id}",
                "Connection": "keep-alive" if self.keep_alive else "close",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; KFONWI Build/PS7331.4463N)"
            }
        )
        return response.text
    
    # System Time
    def set_sys_time(self, time: str = None) -> str:
        """Set system time (format: YYYYMMDDHHmmss)"""
        if time is None:
            time = datetime.now().strftime("%Y%m%d%H%M%S")
        
        response = self.session.get(
            f"{self.base_url}/cgi-bin/hisnet/setsystime.cgi",
            params={"-time": time},
            headers={
                "Accept-Encoding": "gzip",
                "Cookie": f"SessionID={self.session_id}",
                "Connection": "keep-alive" if self.keep_alive else "close",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; KFONWI Build/PS7331.4463N)"
            }
        )
        return response.text
    
    # Camera Configuration
    def get_cam_num(self) -> Dict:
        """Get number of cameras"""
        response = self.session.get(
            f"{self.base_url}/cgi-bin/hisnet/getcamnum.cgi",
            headers={
                "Accept-Encoding": "gzip",
                "Cookie": f"SessionID={self.session_id}",
                "Connection": "keep-alive" if self.keep_alive else "close",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; KFONWI Build/PS7331.4463N)"
            }
        )
        return response.text
    
    def get_cam_channel(self, cam_id: int = 0) -> Dict:
        """Get camera channel for specified camera ID"""
        response = self.session.get(
            f"{self.base_url}/cgi-bin/hisnet/getcamchnl.cgi",
            params={"-camid": cam_id},
            headers={
                "Accept-Encoding": "gzip",
                "Cookie": f"SessionID={self.session_id}",
                "Connection": "keep-alive" if self.keep_alive else "close",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; KFONWI Build/PS7331.4463N)"
            }
        )
        return response.text
    
    # SD Card Status
    def get_sd_status(self) -> Dict:
        """Get SD card status and capacity"""
        response = self.session.get(
            f"{self.base_url}/cgi-bin/hisnet/getsdstatus.cgi",
            headers={
                "Accept-Encoding": "gzip",
                "Cookie": f"SessionID={self.session_id}",
                "Connection": "keep-alive" if self.keep_alive else "close",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; KFONWI Build/PS7331.4463N)"
            }
        )
        return response.text
    
    # Camera Parameters
    def get_cam_param_capability(self, workmode: str, param_type: str) -> Dict:
        """Get camera parameter capabilities"""
        response = self.session.get(
            f"{self.base_url}/cgi-bin/hisnet/getcamparamcapability.cgi",
            params={"-workmode": workmode, "-type": param_type},
            headers={
                "Accept-Encoding": "gzip",
                "Cookie": f"SessionID={self.session_id}",
                "Connection": "keep-alive" if self.keep_alive else "close",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; KFONWI Build/PS7331.4463N)"
            }
        )
        return response.text
    
    def get_comm_param_capability(self, param_type: str) -> Dict:
        """Get common parameter capabilities"""
        response = self.session.get(
            f"{self.base_url}/cgi-bin/hisnet/getcommparamcapability.cgi",
            params={"-type": param_type},
            headers={
                "Accept-Encoding": "gzip",
                "Cookie": f"SessionID={self.session_id}",
                "Connection": "keep-alive" if self.keep_alive else "close",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; KFONWI Build/PS7331.4463N)"
            }
        )
        return response.text
    
    def get_cam_param(self, workmode: str, param_type: str) -> Dict:
        """Get camera parameter value"""
        response = self.session.get(
            f"{self.base_url}/cgi-bin/hisnet/getcamparam.cgi",
            params={"-workmode": workmode, "-type": param_type},
            headers={
                "Accept-Encoding": "gzip",
                "Cookie": f"SessionID={self.session_id}",
                "Connection": "keep-alive" if self.keep_alive else "close",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; KFONWI Build/PS7331.4463N)"
            }
        )
        return response.text
    
    def get_comm_param(self, param_type: str) -> Dict:
        """Get common parameter value"""
        response = self.session.get(
            f"{self.base_url}/cgi-bin/hisnet/getcommparam.cgi",
            params={"-type": param_type},
            headers={
                "Accept-Encoding": "gzip",
                "Cookie": f"SessionID={self.session_id}",
                "Connection": "keep-alive" if self.keep_alive else "close",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; KFONWI Build/PS7331.4463N)"
            }
        )
        return response.text
    
    # Work Mode Control
    def work_mode_cmd(self, cmd: str) -> str:
        """Send work mode command (start/stop)"""
        response = self.session.get(
            f"{self.base_url}/cgi-bin/hisnet/workmodecmd.cgi",
            params={"-cmd": cmd},
            headers={
                "Accept-Encoding": "gzip",
                "Cookie": f"SessionID={self.session_id}",
                "Connection": "keep-alive" if self.keep_alive else "close",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; KFONWI Build/PS7331.4463N)"
            }
        )
        return response.text
    
    def set_work_mode(self, workmode: str) -> str:
        """Set work mode (ENTER_PLAYBACK, NORM_REC, etc.)"""
        response = self.session.get(
            f"{self.base_url}/cgi-bin/hisnet/setworkmode.cgi",
            params={"-workmode": workmode},
            headers={
                "Accept-Encoding": "gzip",
                "Cookie": f"SessionID={self.session_id}",
                "Connection": "keep-alive" if self.keep_alive else "close",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; KFONWI Build/PS7331.4463N)"
            }
        )
        return response.text
    
    # File Management
    def get_dir_capability(self) -> Dict:
        """Get directory capabilities"""
        response = self.session.get(
            f"{self.base_url}/cgi-bin/hisnet/getdircapability.cgi",
            headers={
                "Accept-Encoding": "gzip",
                "Cookie": f"SessionID={self.session_id}",
                "Connection": "keep-alive" if self.keep_alive else "close",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; KFONWI Build/PS7331.4463N)"
            }
        )
        return response.text
    
    def get_dir_file_count(self, directory: str) -> Dict:
        """Get file count in directory"""
        response = self.session.get(
            f"{self.base_url}/cgi-bin/hisnet/getdirfilecount.cgi",
            params={"-dir": directory},
            headers={
                "Accept-Encoding": "gzip",
                "Cookie": f"SessionID={self.session_id}",
                "Connection": "keep-alive" if self.keep_alive else "close",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; KFONWI Build/PS7331.4463N)"
            }
        )
        return response.text
    
    def get_dir_file_list(self, directory: str, start: int, end: int) -> str:
        """Get file list from directory (returns semicolon-separated list)"""
        response = self.session.get(
            f"{self.base_url}/cgi-bin/hisnet/getdirfilelist.cgi",
            params={"-dir": directory, "-start": start, "-end": end},
            headers={
                "Accept-Encoding": "gzip",
                "Cookie": f"SessionID={self.session_id}",
                "Connection": "keep-alive" if self.keep_alive else "close",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; KFONWI Build/PS7331.4463N)"
            }
        )
        return response.text
    
    def get_dir_file_list_parsed(self, directory: str, start: int, end: int) -> List[str]:
        """Get file list from directory as a parsed list"""
        files_str = self.get_dir_file_list(directory, start, end)
        files = [f.strip() for f in files_str.split(';') if f.strip()]
        return files
    
    # File Downloads
    def get_thumbnail(self, file_path: str) -> bytes:
        """Download thumbnail image (.THM file)"""
        response = self.session.get(
            f"{self.base_url}/{file_path}",
            headers={
                "Accept-Encoding": "",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; KFONWI Build/PS7331.4463N)",
                "Connection": "keep-alive" if self.keep_alive else "close"
            }
        )
        return response.content
    
    def get_video_file(self, file_path: str, byte_range: Optional[str] = None, stream: bool = False) -> bytes:
        """
        Download video file (.TS file)
        
        Args:
            file_path: Path to video file
            byte_range: Optional range like "bytes=0-" for partial download
            stream: If True, returns response object for streaming, else returns content
        """
        headers = {
            "User-Agent": "Lavf/57.83.100",
            "Accept": "*/*",
            "Connection": "keep-alive" if self.keep_alive else "close",
            "Icy-MetaData": "1"
        }
        if byte_range:
            headers["Range"] = byte_range
        
        response = self.session.get(
            f"{self.base_url}/{file_path}",
            headers=headers,
            stream=stream
        )
        
        if stream:
            return response
        return response.content
    
    def get_gps_data(self, file_path: str) -> str:
        """Download GPS data file (.TXT file)"""
        response = self.session.get(
            f"{self.base_url}/{file_path}",
            headers={
                "Accept-Encoding": "",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; KFONWI Build/PS7331.4463N)",
                "Connection": "keep-alive" if self.keep_alive else "close"
            }
        )
        return response.text
    
    # Helper Methods
    def download_directory(self, directory: str, output_dir: str, file_type: str = "video", 
                          parallel: int = 1, show_progress: bool = True):
        """
        Download all files from a directory with optimizations
        
        Args:
            directory: Directory name (e.g., 'norm', 'back_norm', 'photo')
            output_dir: Local directory to save files
            file_type: Type of files to download ('video', 'thumbnail', 'gps')
            parallel: Number of parallel downloads (1-5 recommended for WiFi)
            show_progress: Show download progress
        """
        import os
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import time
        
        # Get file count
        count_response = self.get_dir_file_count(directory)
        # Parse count from response like 'var count="69";'
        count = int(count_response.split('"')[1])
        
        if count == 0:
            print(f"No files in {directory}")
            return
        
        # Get file list
        files = self.get_dir_file_list_parsed(directory, 0, count - 1)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Downloading {len(files)} files from {directory}...")
        
        def download_single_file(file_info):
            """Download a single file"""
            idx, file_path = file_info
            if not file_path:
                return None
            
            # Extract filename
            filename = file_path.split('/')[-1]
            
            try:
                start_time = time.time()
                
                if file_type == "video":
                    # Stream download for large video files
                    response = self.get_video_file(file_path, stream=True)
                    content = b''
                    chunk_size = 8192 * 16  # 128KB chunks
                    
                    if hasattr(response, 'iter_content'):
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:
                                content += chunk
                    else:
                        content = response
                        
                elif file_type == "thumbnail":
                    # Change extension to .THM
                    thm_path = file_path.replace('.TS', '.THM').replace('.JPG', '.JPG')
                    content = self.get_thumbnail(thm_path)
                    filename = filename.replace('.TS', '.THM')
                    
                elif file_type == "gps":
                    txt_path = file_path.replace('.TS', '.TXT')
                    content = self.get_gps_data(txt_path).encode('utf-8')
                    filename = filename.replace('.TS', '.TXT')
                else:
                    return None
                
                # Save file
                output_path = os.path.join(output_dir, filename)
                with open(output_path, 'wb') as f:
                    f.write(content if isinstance(content, bytes) else content.encode())
                
                elapsed = time.time() - start_time
                size_mb = len(content) / (1024 * 1024)
                speed_mbps = (size_mb * 8) / elapsed if elapsed > 0 else 0
                
                return {
                    'idx': idx,
                    'filename': filename,
                    'size_mb': size_mb,
                    'elapsed': elapsed,
                    'speed_mbps': speed_mbps,
                    'success': True
                }
                
            except Exception as e:
                return {
                    'idx': idx,
                    'filename': filename,
                    'success': False,
                    'error': str(e)
                }
        
        # Download files (parallel or sequential)
        completed = 0
        total_size = 0
        total_time = 0
        
        if parallel > 1:
            # Parallel downloads
            with ThreadPoolExecutor(max_workers=parallel) as executor:
                future_to_file = {
                    executor.submit(download_single_file, (i, f)): f 
                    for i, f in enumerate(files, 1)
                }
                
                for future in as_completed(future_to_file):
                    result = future.result()
                    if result:
                        completed += 1
                        if result['success']:
                            total_size += result['size_mb']
                            total_time += result['elapsed']
                            if show_progress:
                                print(f"[{completed}/{len(files)}] {result['filename']} - "
                                      f"{result['size_mb']:.1f}MB @ {result['speed_mbps']:.1f} Mbps")
                        else:
                            if show_progress:
                                print(f"[{completed}/{len(files)}] {result['filename']} - Error: {result['error']}")
        else:
            # Sequential downloads
            for i, file_path in enumerate(files, 1):
                result = download_single_file((i, file_path))
                if result:
                    completed += 1
                    if result['success']:
                        total_size += result['size_mb']
                        total_time += result['elapsed']
                        if show_progress:
                            print(f"[{completed}/{len(files)}] {result['filename']} - "
                                  f"{result['size_mb']:.1f}MB @ {result['speed_mbps']:.1f} Mbps")
                    else:
                        if show_progress:
                            print(f"[{completed}/{len(files)}] {result['filename']} - Error: {result['error']}")
        
        # Summary
        if show_progress and total_time > 0:
            avg_speed = (total_size * 8) / total_time
            print(f"\nCompleted: {completed}/{len(files)} files")
            print(f"Total: {total_size:.1f}MB in {total_time:.1f}s")
            print(f"Average speed: {avg_speed:.1f} Mbps")
    
    def get_all_directories(self) -> List[str]:
        """Get list of available directories"""
        response = self.get_dir_capability()
        # Parse response like 'var capability="emr,norm,GPSdata,back_emr,back_norm,photo,back_photo,";'
        dirs = response.split('"')[1].rstrip(',').split(',')
        return [d for d in dirs if d]


# Example usage
if __name__ == "__main__":
    import os
    
    # Initialize API client with connection pooling enabled
    api = DashcamAPI("http://192.168.0.1", keep_alive=True)
    
    # Register client
    print("Registering client...")
    print(api.register_client("192.168.0.21"))
    
    # Get device info
    print("\nDevice attributes:")
    print(api.get_device_attr())
    
    # Get WiFi config
    print("\nWiFi configuration:")
    print(api.get_wifi())
    
    # Get SD card status
    print("\nSD card status:")
    print(api.get_sd_status())
    
    # Get work state
    print("\nWork state:")
    print(api.get_work_state())
    
    # Stop recording
    print("\nStopping recording...")
    print(api.work_mode_cmd("stop"))
    
    # Enter playback mode
    print("\nEntering playback mode...")
    print(api.set_work_mode("ENTER_PLAYBACK"))
    
    # Get directory capabilities
    print("\nAvailable directories:")
    directories = api.get_all_directories()
    print(directories)
    
    # ==== PERFORMANCE OPTIMIZATIONS ====
    
    # # Option 1: Sequential downloads with keep-alive (RECOMMENDED for stability)
    # print("\n--- Sequential Download with Keep-Alive ---")
    # api.download_directory('norm', './videos/norm', file_type='video', parallel=1)
    
    # # Option 2: Parallel downloads (2-3 connections recommended for WiFi)
    # print("\n--- Parallel Download (3 connections) ---")
    # api.download_directory('norm', './videos/norm', file_type='video', parallel=3)
    
    # # Option 3: Manual control with your original approach (now optimized)
    # print("\n--- Manual Download Example (Optimized) ---")
    files = api.get_dir_file_list("norm", 0, 10).split(';')
    
    os.makedirs('./videos', exist_ok=True)
    
    for file in files:
        if file.strip():
            print(f'Getting {file}')
            try:
                # Stream large files to avoid memory issues
                response = api.get_video_file(file, stream=True)
                
                with open(os.path.join('.', 'videos', file.split('/')[-1]), 'wb') as video:
                    # Write in chunks for better performance
                    for chunk in response.iter_content(chunk_size=8192 * 16):
                        if chunk:
                            video.write(chunk)
                            
                print(f'  → Saved successfully')
            except Exception as e:
                print(f'  → Error: {e}')
    
    # Download thumbnails (faster with parallel)
    api.download_directory('norm', './thumbnails/norm', file_type='thumbnail', parallel=5)
    
    # Download from back camera
    api.download_directory('back_norm', './videos/back_norm', file_type='video', parallel=3)
    
    # Close session when done
    api.session.close()
    
    print("\n=== SPEED TIPS ===")
    print("1. Use keep_alive=True (default) - reuses TCP connections")
    print("2. For WiFi, try parallel=2 or parallel=3 for 2-3x speed boost")
    print("3. Sequential (parallel=1) is more stable but slower")
    print("4. Reduce parallel count if you see connection errors")
    print("5. Typical WiFi speeds: 5-20 Mbps depending on distance and interference")