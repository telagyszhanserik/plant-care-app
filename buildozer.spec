[app]
title = PlantCareApp
package.name = plantcareapp
package.domain = org.plantcare
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,tflite,txt,json
version = 1.0
requirements = python3,kivy==2.3.0,pillow,numpy,tflite-runtime
orientation = portrait
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
