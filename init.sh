mkdir -p src/{api,ui,services,utils} tests docs resources
touch src/{api,ui,services,utils}/__init__.py

# In your project directory
claude "Read claude.md and create the data models (VideoFile and DownloadTask) 
       in src/api/models.py with proper parsing of dashcam filenames"

# Or
claude "Set up the basic GTK4 application structure with MainWindow class 
       in src/ui/main_window.py. Include header bar, grid layout, and status bar"

# Or
claude "Implement the CacheManager class that stores thumbnails on disk with 
       proper cache invalidation"