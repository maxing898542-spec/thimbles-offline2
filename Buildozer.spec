[app]
title = Напёрстки Offline
package.name = thimblesoffline
package.domain = org.vanyalgrw.thimbles
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt
version = 1.0.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0

android.archs = arm64-v8a
android.api = 33
android.minapi = 21
android.ndk = 25b
android.build_tools_version = 33.0.2
android.accept_sdk_license = True
android.allow_backup = True
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
