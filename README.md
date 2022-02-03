# py-ews
Interacts with the REST interface of the Emergent Web Server (projectdana.com) to allow interaction with python code.
The EWS can be installed via Docker, instructions can be found at https://github.com/robertovrf/emergent_web_server

# Installation
Built version can be found in the dist/ directory. You can install this using pip install dist/&lt;filename>

# Usage
Python Interface to the emergent_web_server
1. Ensure the Emergent Web Server is running.

2. Make sure to set the IP of the EWS using the settings dictionary found in global_vars.py

3. Use the initialize_server function found in the server_interface.py prior at the beginning of any scripts using this package. Unless the EWS is already initialized.

# Example script
A demo Python script demonstrating functionality and implementing an epsilon-greedy algorithm is included in examples/


