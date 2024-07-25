<div align="center">
<img width="60px" src="https://pts-project.org/android-chrome-512x512.png">
<h1>PiRogue evidence collector</h1>
<p>
A set of tools to collect digital evidence from mobile devices.
</p>
<p>
Licenses: GPLv3, MIT
</p><p>
<a href="https://pts-project.org">Website</a> | 
<a href="https://pts-project.org/docs/">Documentation</a> | 
<a href="https://discord.gg/qGX73GYNdp">Support</a>
</p>
</div>

# Overview
This package defines and installs a set of commands to collect digital evidence from mobile devices. 
It defines the following commands:

* `pirogue-android` to interact with an Android device and run commands on it.
* `pirogue-file-drop` to expose a web server allowing the user can upload files from their device to the PiRogue.
* `pirogue-extract-metadata` to extract metadata of a file and save it in a separate file `[original file name].metadata.json`.
* `pirogue-timestamp` to time stamp files using a 3rd-party RFC3161 service.
* `pirogue-intercept-[gated|single]` to instrument an Android application to analyze its network traffic.

# Licensing
This work is licensed under multiple licences. Here is a summary that's reflect 
the file `debian/copyright`. 

* All the code in this repository is licensed under the GPLv3 license.
  * Copyright: 2024   U+039b <hello@pts-project.org>  
  * Copyright: 2024   Defensive Lab Agency <contact@defensive-lab.agency>
* The file `frida-scripts/dynamic_hook_injector.js` is licensed under the MIT license.
  * Copyright: 2024   2024 Pôle d'Expertise de la Régulation Numérique - PEReN <contact@peren.gouv.fr>

