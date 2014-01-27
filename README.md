### Overview

This fabric script is meant to automate the various steps involved in installing
kuali rice standalone server. Ideally this would be a puppet module or chef 
recipe, but I don't have the time and I don't have a puppet master server.

## Getting Started

1. Get a copy of rice-config.xml. You can get this from config/rice-middleware/web/src/main/config/example-config/rice-config.xml
in the standalone download. Make any modifications to the configuration file

2. Copy config.sample.py to config.py and modify settings
    cp config.sample.py config.py

3. Run the install task
    fab install
