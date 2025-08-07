import os
import subprocess
from setuptools import setup, find_packages, Extension

def pkgconfig_flags(package, flag_type):
    """ Get output of pkg-config --cflags/--libs [package] """
    try:
        command = ['pkg-config', f'--{flag_type}', package]
        output = subprocess.check_output(command).decode('utf-8').strip()
        return output.split()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"WARNING: Could not found pkg-config or '{package}' packages.")
        return []

opt_cflags = ["-Werror=format-security"]
# GTK 2.0
gtk2_cflags = pkgconfig_flags('gtk+-2.0', 'cflags')
gtk2_libs = pkgconfig_flags('gtk+-2.0', 'libs')
# GTK 3.0
gtk3_cflags = pkgconfig_flags('gtk+-3.0', 'cflags')
gtk3_libs = pkgconfig_flags('gtk+-3.0', 'libs')
# GLib 2.0
glib2_cflags = pkgconfig_flags('glib-2.0', 'cflags')
glib2_libs = pkgconfig_flags('glib-2.0', 'libs')
# (!) ALL
all2_cflags = gtk2_cflags + glib2_cflags + opt_cflags
all3_cflags = gtk3_cflags + glib2_cflags + opt_cflags
all2_libs = gtk2_libs + glib2_libs + opt_cflags
all3_libs = gtk3_libs + glib2_libs + opt_cflags
# Ignore Duplicated
all2_cflags = list(dict.fromkeys(all2_cflags))
all3_cflags = list(dict.fromkeys(all3_cflags))
all2_libs = list(dict.fromkeys(all2_libs))
all3_libs = list(dict.fromkeys(all3_libs))
# 2? 3?
if gtk3_cflags == '' and gtk2_cflags:
    all_cflags = all2_cflags
    all_libs = all2_libs
else:
    all_cflags = all3_cflags
    all_libs = all3_libs

gtk_dialog_module = Extension(
    'gdialog.dialog',                 # Module name
    sources=['src/gdialog/dialog.c'],  # C sourtce file
    extra_compile_args=all_cflags,     # cflags is there
    extra_link_args=all_libs,          # libs is there
)

gtk2_dialog_module = Extension(
    'gdialog.dialog',                 # Module name
    sources=['src/gdialog/dialog.c'],  # C sourtce file
    extra_compile_args=all2_cflags,     # cflags is there
    extra_link_args=all2_libs,          # libs is there
)

gtk3_dialog_module = Extension(
    'gdialog.dialog',                 # Module name
    sources=['src/gdialog/dialog.c'],  # C sourtce file
    extra_compile_args=all3_cflags,     # cflags is there
    extra_link_args=all3_libs,          # libs is there
)

setup(
    name='gdialog',
    version='0.50.0',
    packages=find_packages(exclude=['tests']),
    ext_modules=[
        gtk_dialog_module,
        #gtk2_dialog_module,
        #gtk3_dialog_module,
    ],
    entry_points={
        'console_scripts': [
            'my_command = sdgp.module:main_func',
        ],
    },
    # ... 他のメタデータ ...
)
