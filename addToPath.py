import os

# Directory you want to add
directory = "C://Users/ext.andre.santos/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0/LocalCache/local-packages/Python313/Scripts"
# Add the directory to the PATH environment variable
os.environ["PATH"] += os.pathsep + directory

# Verify the directory has been added
print(os.environ["PATH"])