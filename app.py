#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This script provides a GTK 4 and Libadwaita interface for managing 
# Web App launchers that use Firefox Kiosk mode.
#
#
# Copyright (C) 2026 steve.rock@wheelhouser.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# --- Setup Instructions ---
# Activate the venv:
# source .venv/bin/activate
# pip install -r requirements.txt
#
# Run the application:
# ./launch.sh
#
#===========================================================================================

import os
import gi
import manager

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Adw, Gdk, GdkPixbuf, Gtk  # noqa: E402

#===============================================================================================
# GUI Application
#===============================================================================================
class WebAppRow(Adw.ActionRow):
    def __init__(self, app, on_delete_callback):
        super().__init__(title=app['name'], subtitle=app['url'])
        self.app = app
        
        # Icon
        icon_image = Gtk.Image()
        if app['icon'] and os.path.exists(app['icon']):
            try:
                # GTK4 uses GIcon or paintables
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(app['icon'], 32, 32)
                texture = Gdk.Texture.new_for_pixbuf(pixbuf)
                icon_image.set_from_paintable(texture)
            except Exception:
                icon_image.set_from_icon_name("web-browser-symbolic")
        else:
            icon_image.set_from_icon_name("web-browser-symbolic")
        
        self.add_prefix(icon_image)
        
        # Delete Button
        delete_btn = Gtk.Button(icon_name="user-trash-symbolic")
        delete_btn.set_valign(Gtk.Align.CENTER)
        delete_btn.add_css_class("destructive-action")
        delete_btn.connect("clicked", lambda x: on_delete_callback(self.app))
        self.add_suffix(delete_btn)

#===============================================================================================
# Main Application
#===============================================================================================
class WebAppLauncherApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.example.WebAppLauncher",
                         flags=0)

    def do_activate(self):
        self.win = Adw.ApplicationWindow(application=self)
        self.win.set_title("Web App Manager")
        self.win.set_default_size(500, 600)

        # Toolbar / HeaderBar
        header_bar = Adw.HeaderBar()

        # Add Button
        add_btn = Gtk.Button(icon_name="list-add-symbolic")
        add_btn.set_tooltip_text("Add New Web App")
        add_btn.connect("clicked", self.on_add_clicked)
        header_bar.pack_start(add_btn)

        # Main Layout using ToolbarView
        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(header_bar)
        self.win.set_content(toolbar_view)

        # Content Page
        self.clamp = Adw.Clamp()
        toolbar_view.set_content(self.clamp)
        
        self.list_box = Gtk.ListBox()
        self.list_box.add_css_class("boxed-list")
        self.list_box.set_margin_top(12)
        self.list_box.set_margin_bottom(12)
        self.list_box.set_margin_start(12)
        self.list_box.set_margin_end(12)
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.clamp.set_child(self.list_box)

        self.refresh_list()
        self.win.present()

    def refresh_list(self):
        # Clear existing
        child = self.list_box.get_first_child()
        while child:
            self.list_box.remove(child)
            child = self.list_box.get_first_child()

        apps = manager.get_installed_apps()
        if not apps:
            empty_row = Adw.ActionRow(title="No web apps installed")
            self.list_box.append(empty_row)
        else:
            for app in apps:
                row = WebAppRow(app, self.on_uninstall_requested)
                self.list_box.append(row)

    def on_uninstall_requested(self, app):
        dialog = Adw.MessageDialog(
            transient_for=self.win,
            heading=f"Uninstall {app['name']}?",
            body=f"This will remove the desktop entry and icon for {app['url']}.",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("uninstall", "Uninstall")
        dialog.set_response_appearance("uninstall", Adw.ResponseAppearance.DESTRUCTIVE)
        
        dialog.connect("response", self.on_uninstall_dialog_response, app)
        dialog.present()

    def on_uninstall_dialog_response(self, dialog, response, app):
        if response == "uninstall":
            manager.uninstall_app(app['id'])
            self.refresh_list()

    def on_add_clicked(self, btn):
        self.add_dialog = AddAppDialog(self.win, self.on_app_added)
        self.add_dialog.present()

    def on_app_added(self, name, url, icon):
        if name and url:
            manager.install_app(name, url, icon)
            self.refresh_list()

#===============================================================================================
# Add App Dialog
#===============================================================================================
class AddAppDialog(Gtk.Window):
    def __init__(self, parent, callback):
        super().__init__(title="Add New Web App", transient_for=parent, modal=True)
        self.callback = callback
        self.set_default_size(500, -1)
        self.icon_path = None

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(18)
        main_box.set_margin_bottom(18)
        main_box.set_margin_start(18)
        main_box.set_margin_end(18)
        self.set_child(main_box)

        # Form Group
        group = Adw.PreferencesGroup()
        main_box.append(group)

        self.name_entry = Adw.EntryRow(title="App Name")
        self.name_entry.set_text("My Web App")
        # placeholder-text was added in Libadwaita 1.2, so we set it safely
        if hasattr(self.name_entry, "set_placeholder_text"):
            self.name_entry.set_placeholder_text("e.g. Netflix")
        group.add(self.name_entry)

        self.url_entry = Adw.EntryRow(title="URL")
        self.url_entry.set_text("https://example.com")
        if hasattr(self.url_entry, "set_placeholder_text"):
            self.url_entry.set_placeholder_text("https://...")
        group.add(self.url_entry)

        self.icon_btn = Gtk.Button(label="Choose Icon...")
        self.icon_btn.set_valign(Gtk.Align.CENTER)
        self.icon_btn.connect("clicked", self.on_choose_icon)
        icon_row = Adw.ActionRow(title="Icon")
        icon_row.add_suffix(self.icon_btn)
        group.add(icon_row)

        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        buttons_box.set_halign(Gtk.Align.END)
        main_box.append(buttons_box)

        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda x: self.destroy())
        buttons_box.append(cancel_btn)

        add_btn = Gtk.Button(label="Add")
        add_btn.add_css_class("suggested-action")
        add_btn.connect("clicked", self.on_add_pressed)
        buttons_box.append(add_btn)

    def on_choose_icon(self, btn):
        dialog = Gtk.FileChooserDialog(title="Select Icon", transient_for=self, action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Open", Gtk.ResponseType.OK)
        
        filter_img = Gtk.FileFilter()
        filter_img.set_name("Images")
        filter_img.add_mime_type("image/png")
        filter_img.add_mime_type("image/jpeg")
        filter_img.add_mime_type("image/svg+xml")
        dialog.add_filter(filter_img)

        dialog.connect("response", self.on_icon_response)
        dialog.present()

    def on_icon_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            self.icon_path = dialog.get_file().get_path()
            self.icon_btn.set_label(os.path.basename(self.icon_path))
        dialog.destroy()

    def on_add_pressed(self, btn):
        self.callback(self.name_entry.get_text(), self.url_entry.get_text(), self.icon_path)
        self.destroy()

#===============================================================================================
# Main Entry Point
#===============================================================================================
if __name__ == "__main__":
    app = WebAppLauncherApp()
    app.run(None)
