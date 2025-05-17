# trasker_gui/supporting_view/single_document_view.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tempfile
import webbrowser
import io
import mimetypes
import sys

# We won’t use pdf2image here so we won’t rely on it.
# Instead, for PDFs, we’ll just offer the “open externally” option.

from PIL import Image, ImageTk

class SingleDocumentView(tk.Toplevel):
    def __init__(self, parent, controller, document_id, refresh_callback=None):
        """
        Opens a document in a new window.
        Depending on the MIME type, it will either allow inline editing,
        display a preview (for images), or simply offer a download option.
        For PDFs, it will only offer an external open.
        Additionally, the uploader’s username and team name are displayed.
        """
        super().__init__(parent)
        self.controller = controller
        self.document_id = document_id
        self.refresh_callback = refresh_callback
        self.title("Document Viewer")
        self.geometry("800x600")
        self.configure(bg="white")

        # Retrieve the document record from the database.
        doc = self.controller.trasker.get_document(document_id)
        if not doc:
            messagebox.showerror("Error", "Document not found.")
            self.destroy()
            return

        # Unpack document record:
        # Expected schema:
        # (id, note_id, filename, mimetype, document_blob, upload_date, user_id, team_id)
        try:
            (self.doc_id, self.note_id, self.filename, self.mimetype,
             self.document_blob, self.upload_date, self.user_id, self.team_id) = doc
        except Exception as e:
            messagebox.showerror("Error", f"Failed to unpack document data: {e}")
            self.destroy()
            return

        # Retrieve uploader username and team name.
        uploader = self.user_id if self.user_id else "Unknown"
        team_name = self.team_id if self.team_id else "N/A"

        # Create a metadata frame to display uploader and team information.
        metadata_frame = ttk.Frame(self, padding=10)
        metadata_frame.pack(fill=tk.X)
        metadata_label = ttk.Label(metadata_frame, text=f"Uploaded by: {uploader}    Team: {team_name}", font=("Arial", 10))
        metadata_label.pack(side=tk.LEFT)

        # Create a main content frame.
        self.content_frame = ttk.Frame(self, padding=20)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Choose the view based on MIME type.
        if self.mimetype == "text/plain":
            self.show_text_view()
        elif self.mimetype == "application/pdf":
            self.show_pdf_view()
        elif self.mimetype.startswith("image/"):
            self.show_image_view()
        else:
            self.show_download_view()

        # Add an "Upload New Version" button at the bottom.
        upload_btn = ttk.Button(self, text="Upload New Version", command=self.upload_new_version)
        upload_btn.pack(pady=10)

    def show_text_view(self):
        """Show a preview of a text document with options to edit inline or download."""
        prompt = ttk.Label(self.content_frame,
                           text="This is a text document. Would you like to edit it or download it?",
                           font=("Arial", 14))
        prompt.pack(pady=10)
        try:
            # Convert memoryview to bytes if needed and decode
            if isinstance(self.document_blob, memoryview):
                content = self.document_blob.tobytes().decode('utf-8')
            elif isinstance(self.document_blob, bytes):
                content = self.document_blob.decode('utf-8')
            else:
                content = str(self.document_blob)
        except Exception as e:
            content = "Error decoding document."
        snippet = content[:500] + ("..." if len(content) > 500 else "")
        snippet_label = ttk.Label(self.content_frame, text=snippet, wraplength=750)
        snippet_label.pack(pady=10)
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=20)
        edit_btn = ttk.Button(btn_frame, text="Edit Document", command=self.open_text_editor)
        edit_btn.grid(row=0, column=0, padx=10)
        download_btn = ttk.Button(btn_frame, text="Download Document", command=self.download_document)
        download_btn.grid(row=0, column=1, padx=10)

    def open_text_editor(self):
        """Open a text editor in a new window for inline editing of text documents."""
        editor = tk.Toplevel(self)
        editor.title("Edit Document")
        editor.geometry("800x600")
        text_widget = tk.Text(editor, wrap="word")
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        content = self.document_blob.decode('utf-8') if isinstance(self.document_blob, bytes) else self.document_blob
        text_widget.insert("1.0", content)
        def save_edits():
            new_content = text_widget.get("1.0", tk.END).rstrip()
            try:
                self.controller.trasker.update_document(self.document_id, new_content.encode('utf-8'))
                messagebox.showinfo("Saved", "Document updated successfully.")
                if self.refresh_callback:
                    self.refresh_callback()
                editor.destroy()
                self.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save document: {e}")
        save_btn = ttk.Button(editor, text="Save", command=save_edits)
        save_btn.pack(pady=10)

    def show_pdf_view(self):
        """For PDF documents, simply offer an 'Open Externally' and 'Download' option."""
        title_label = ttk.Label(self.content_frame, text="PDF Document", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        info_label = ttk.Label(self.content_frame, text="PDF preview is not available.\nClick 'Open Externally' to view in your default PDF viewer.", font=("Arial", 12))
        info_label.pack(pady=10)
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=20)
        open_ext_btn = ttk.Button(btn_frame, text="Open Externally", command=self.open_pdf_externally)
        open_ext_btn.grid(row=0, column=0, padx=10)
        download_btn = ttk.Button(btn_frame, text="Download Document", command=self.download_document)
        download_btn.grid(row=0, column=1, padx=10)

    def open_pdf_externally(self):
        """Save PDF temporarily and open it with the system default PDF viewer."""
        import os, sys, tempfile, subprocess, webbrowser
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, self.filename)
        try:
            with open(temp_path, "wb") as f:
                f.write(self.document_blob)
            if sys.platform == "darwin":
                subprocess.call(["open", temp_path])
            elif sys.platform == "win32":
                os.startfile(temp_path)
            else:
                file_url = "file://" + temp_path
                webbrowser.open(file_url)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF externally: {e}")

    def show_image_view(self):
        """Display an image document inside the app with options to edit (if supported) or download."""
        title_label = ttk.Label(self.content_frame, text="Image Preview", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        try:
            from PIL import Image
            image = Image.open(io.BytesIO(self.document_blob))
            image.thumbnail((750, 500))
            self.photo = ImageTk.PhotoImage(image)
            image_label = ttk.Label(self.content_frame, image=self.photo)
            image_label.pack(pady=10)
        except Exception as e:
            ttk.Label(self.content_frame, text=f"Error displaying image: {e}").pack(pady=10)
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=20)
        edit_btn = ttk.Button(btn_frame, text="Edit Image", command=self.open_image_editor)
        edit_btn.grid(row=0, column=0, padx=10)
        download_btn = ttk.Button(btn_frame, text="Download Document", command=self.download_document)
        download_btn.grid(row=0, column=1, padx=10)

    def open_image_editor(self):
        """Open a new window to display the image for editing.
           (In this example, we simply allow re-uploading the same image as a placeholder.)
        """
        editor = tk.Toplevel(self)
        editor.title("Edit Image Document")
        editor.geometry("800x600")
        try:
            from PIL import Image
            image = Image.open(io.BytesIO(self.document_blob))
            self.photo = ImageTk.PhotoImage(image)
            image_label = ttk.Label(editor, image=self.photo)
            image_label.pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Error opening image editor: {e}")
            editor.destroy()
            return
        def save_image_edits():
            try:
                self.controller.trasker.update_document(self.document_id, self.document_blob)
                messagebox.showinfo("Success", "Image updated successfully.")
                if self.refresh_callback:
                    self.refresh_callback()
                editor.destroy()
                self.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update image: {e}")
        save_button = ttk.Button(editor, text="Save", command=save_image_edits)
        save_button.pack(pady=10)

    def show_download_view(self):
        """Display a view for unsupported document types that only allows download."""
        frame = ttk.Frame(self.content_frame, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        label = ttk.Label(frame, text="This document type is not editable.\nClick the button below to download the file.", font=("Arial", 14))
        label.pack(pady=10)
        download_btn = ttk.Button(frame, text="Download Document", command=self.download_document)
        download_btn.pack(pady=10)

    def download_document(self):
        """Allow the user to download the document."""
        file_path = filedialog.asksaveasfilename(initialfile=self.filename)
        if file_path:
            try:
                with open(file_path, "wb") as f:
                    if isinstance(self.document_blob, str):
                        f.write(self.document_blob.encode('utf-8'))
                    else:
                        f.write(self.document_blob)
                messagebox.showinfo("Downloaded", "Document downloaded successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download document: {e}")

    def upload_new_version(self):
        """Allow the user to upload a new version of the document."""
        new_file = filedialog.askopenfilename(title="Select new version of document")
        if new_file:
            try:
                with open(new_file, "rb") as f:
                    new_blob = f.read()
                self.controller.trasker.update_document(self.document_id, new_blob)
                messagebox.showinfo("Updated", "Document updated successfully.")
                if self.refresh_callback:
                    self.refresh_callback()
                self.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload new version: {e}")
