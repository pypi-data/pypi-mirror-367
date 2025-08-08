"""
Graphical user interface for DocxMD Converter.
"""

import logging
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Optional

from .core import ConversionError, DocxMdConverter


class LogHandler(logging.Handler):
    """Custom logging handler to redirect logs to GUI."""

    def __init__(self, text_widget: tk.Text) -> None:
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        # Use after() to ensure thread safety
        self.text_widget.after(0, self._append_text, msg + "\n")

    def _append_text(self, text: str) -> None:
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)


class DocxMdConverterGUI:
    """GUI application for DocxMD Converter."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("DocxMD Converter")
        self.root.geometry("800x600")

        # Variables
        self.src_dir = tk.StringVar()
        self.dst_dir = tk.StringVar()
        self.template_path = tk.StringVar()
        self.direction = tk.StringVar(value="docx2md")
        self.verbose = tk.BooleanVar()

        self.converter: Optional[DocxMdConverter] = None
        self.conversion_thread: Optional[threading.Thread] = None

        self._create_widgets()
        self._setup_layout()
        self._setup_logging()

        # Center window on screen
        self.root.after(100, self._center_window)

    def _center_window(self) -> None:
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self) -> None:
        """Create all GUI widgets."""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")

        # Title
        self.title_label = ttk.Label(
            self.main_frame, text="DocxMD Converter", font=("Arial", 16, "bold")
        )

        # Source directory
        self.src_frame = ttk.LabelFrame(
            self.main_frame, text="Source Directory", padding="5"
        )
        self.src_entry = ttk.Entry(self.src_frame, textvariable=self.src_dir, width=60)
        self.src_button = ttk.Button(
            self.src_frame, text="Browse...", command=self._browse_source_dir
        )

        # Destination directory
        self.dst_frame = ttk.LabelFrame(
            self.main_frame, text="Destination Directory", padding="5"
        )
        self.dst_entry = ttk.Entry(self.dst_frame, textvariable=self.dst_dir, width=60)
        self.dst_button = ttk.Button(
            self.dst_frame, text="Browse...", command=self._browse_dest_dir
        )

        # Conversion direction
        self.direction_frame = ttk.LabelFrame(
            self.main_frame, text="Conversion Direction", padding="5"
        )
        self.direction_docx2md = ttk.Radiobutton(
            self.direction_frame,
            text="DOCX → Markdown",
            variable=self.direction,
            value="docx2md",
            command=self._on_direction_change,
        )
        self.direction_md2docx = ttk.Radiobutton(
            self.direction_frame,
            text="Markdown → DOCX",
            variable=self.direction,
            value="md2docx",
            command=self._on_direction_change,
        )

        # Template
        self.template_frame = ttk.LabelFrame(
            self.main_frame, text="Template (Optional)", padding="5"
        )
        self.template_entry = ttk.Entry(
            self.template_frame, textvariable=self.template_path, width=60
        )
        self.template_button = ttk.Button(
            self.template_frame, text="Browse...", command=self._browse_template
        )

        # Options
        self.options_frame = ttk.LabelFrame(
            self.main_frame, text="Options", padding="5"
        )
        self.verbose_check = ttk.Checkbutton(
            self.options_frame, text="Verbose logging", variable=self.verbose
        )

        # Buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.convert_button = ttk.Button(
            self.button_frame,
            text="Start Conversion",
            command=self._start_conversion,
            style="Accent.TButton",
        )
        self.clear_button = ttk.Button(
            self.button_frame, text="Clear Log", command=self._clear_log
        )

        # Log output
        self.log_frame = ttk.LabelFrame(
            self.main_frame, text="Conversion Log", padding="5"
        )
        self.log_text = scrolledtext.ScrolledText(
            self.log_frame, height=15, width=80, state=tk.DISABLED
        )

        # Progress bar
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress = ttk.Progressbar(self.progress_frame, mode="indeterminate")
        self.status_label = ttk.Label(self.progress_frame, text="Ready")

    def _setup_layout(self) -> None:
        """Setup widget layout."""
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        self.title_label.pack(pady=(0, 20))

        # Source directory
        self.src_frame.pack(fill=tk.X, pady=5)
        self.src_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.src_button.pack(side=tk.RIGHT, padx=(10, 0))

        # Destination directory
        self.dst_frame.pack(fill=tk.X, pady=5)
        self.dst_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.dst_button.pack(side=tk.RIGHT, padx=(10, 0))

        # Direction
        self.direction_frame.pack(fill=tk.X, pady=5)
        self.direction_docx2md.pack(side=tk.LEFT, padx=(0, 20))
        self.direction_md2docx.pack(side=tk.LEFT)

        # Template
        self.template_frame.pack(fill=tk.X, pady=5)
        self.template_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.template_button.pack(side=tk.RIGHT, padx=(10, 0))

        # Options
        self.options_frame.pack(fill=tk.X, pady=5)
        self.verbose_check.pack(side=tk.LEFT)

        # Buttons
        self.button_frame.pack(fill=tk.X, pady=10)
        self.convert_button.pack(side=tk.LEFT)
        self.clear_button.pack(side=tk.LEFT, padx=(10, 0))

        # Progress
        self.progress_frame.pack(fill=tk.X, pady=5)
        self.progress.pack(fill=tk.X)
        self.status_label.pack(pady=5)

        # Log
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Initially disable template controls
        self._on_direction_change()

    def _setup_logging(self) -> None:
        """Setup logging to display in GUI."""
        # Create a custom handler that writes to our text widget
        self.log_handler = LogHandler(self.log_text)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        self.log_handler.setFormatter(formatter)

        # Initially setup with INFO level
        self._update_logging()

    def _update_logging(self) -> None:
        """Update logging configuration based on verbose setting."""
        # Remove existing handler if present
        logger = logging.getLogger("docxmd_converter.core")
        logger.handlers = [h for h in logger.handlers if not isinstance(h, LogHandler)]

        # Set level and add handler
        level = logging.DEBUG if self.verbose.get() else logging.INFO
        logger.setLevel(level)
        self.log_handler.setLevel(level)
        logger.addHandler(self.log_handler)

    def _browse_source_dir(self) -> None:
        """Browse for source directory."""
        directory = filedialog.askdirectory(title="Select Source Directory")
        if directory:
            self.src_dir.set(directory)

    def _browse_dest_dir(self) -> None:
        """Browse for destination directory."""
        directory = filedialog.askdirectory(title="Select Destination Directory")
        if directory:
            self.dst_dir.set(directory)

    def _browse_template(self) -> None:
        """Browse for template file."""
        filename = filedialog.askopenfilename(
            title="Select Template File",
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")],
        )
        if filename:
            self.template_path.set(filename)

    def _on_direction_change(self) -> None:
        """Handle direction change."""
        if self.direction.get() == "md2docx":
            # Enable template controls
            self.template_entry.config(state="normal")
            self.template_button.config(state="normal")
        else:
            # Disable template controls
            self.template_entry.config(state="disabled")
            self.template_button.config(state="disabled")
            self.template_path.set("")

    def _clear_log(self) -> None:
        """Clear the log text."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _log_message(self, message: str, level: str = "INFO") -> None:
        """Add a message to the log."""
        self.log_text.config(state=tk.NORMAL)
        timestamp = __import__("datetime").datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {level}: {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _validate_inputs(self) -> None:
        """Validate user inputs."""
        if not self.src_dir.get():
            raise ConversionError("Please select a source directory")

        if not self.dst_dir.get():
            raise ConversionError("Please select a destination directory")

        src_path = Path(self.src_dir.get())
        if not src_path.exists() or not src_path.is_dir():
            raise ConversionError(
                f"Source directory does not exist: {self.src_dir.get()}"
            )

        # Validate template if provided
        template = self.template_path.get().strip()
        if template:
            if self.direction.get() != "md2docx":
                raise ConversionError(
                    "Template can only be used with Markdown → DOCX conversion"
                )

            template_path = Path(template)
            if not template_path.exists():
                raise ConversionError(f"Template file does not exist: {template}")

            if template_path.suffix.lower() != ".docx":
                raise ConversionError("Template must be a .docx file")

    def _start_conversion(self) -> None:
        """Start the conversion process in a separate thread."""
        if self.conversion_thread and self.conversion_thread.is_alive():
            messagebox.showwarning("Warning", "Conversion is already in progress!")
            return

        try:
            self._validate_inputs()
        except ConversionError as e:
            messagebox.showerror("Validation Error", str(e))
            return

        # Update UI state
        self.convert_button.config(state="disabled", text="Converting...")
        self.progress.start(10)
        self.status_label.config(text="Converting files...")

        # Clear log and update logging
        self._clear_log()
        self._update_logging()

        # Start conversion in separate thread
        self.conversion_thread = threading.Thread(target=self._run_conversion)
        self.conversion_thread.daemon = True
        self.conversion_thread.start()

    def _run_conversion(self) -> None:
        """Run the actual conversion (in separate thread)."""
        try:
            # Initialize converter
            log_level = "DEBUG" if self.verbose.get() else "INFO"
            self.converter = DocxMdConverter(log_level=log_level)

            # Get template path
            template = (
                self.template_path.get().strip()
                if self.template_path.get().strip()
                else None
            )

            # Run conversion
            successful, total = self.converter.convert_directory(
                src_dir=self.src_dir.get(),
                dst_dir=self.dst_dir.get(),
                direction=self.direction.get(),
                template_path=template,
            )

            # Update UI in main thread
            self.root.after(0, self._conversion_complete, successful, total, None)

        except Exception as e:
            # Update UI in main thread
            self.root.after(0, self._conversion_complete, 0, 0, str(e))

    def _conversion_complete(
        self, successful: int, total: int, error: Optional[str]
    ) -> None:
        """Handle conversion completion (runs in main thread)."""
        # Update UI state
        self.convert_button.config(state="normal", text="Start Conversion")
        self.progress.stop()

        if error:
            self.status_label.config(text=f"Error: {error}")
            self._log_message(f"Conversion failed: {error}", "ERROR")
            messagebox.showerror("Conversion Error", error)
        else:
            if successful == total:
                self.status_label.config(
                    text=f"✅ Successfully converted all {total} files"
                )
                self._log_message(f"Successfully converted all {total} files", "INFO")
                messagebox.showinfo(
                    "Success", f"Successfully converted all {total} files!"
                )
            else:
                self.status_label.config(text=f"⚠️ Done {successful}/{total} files")
                self._log_message(
                    f"Converted {successful}/{total} files (some errors occurred)",
                    "WARNING",
                )
                messagebox.showwarning(
                    "Partial Success",
                    f"Converted {successful}/{total} files. Check log for details.",
                )

    def run(self) -> None:
        """Start the GUI application."""
        try:
            # Check if pandoc is available
            DocxMdConverter()._check_pandoc()
        except ConversionError as e:
            messagebox.showerror("Dependency Error", str(e))
            return

        self.root.mainloop()


def run() -> None:
    """Entry point for GUI application."""
    try:
        app = DocxMdConverterGUI()
        app.run()
    except Exception as e:
        try:
            messagebox.showerror("Error", f"Failed to start application: {e}")
        except Exception:
            print(f"Failed to start GUI application: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    run()
