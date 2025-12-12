"""Desktop GUI for QR code transformation using Tkinter."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.transformer import QRTransformer
from src.visualizer import QRVisualizer
from src.insights import generate_insights


class QRTransformationGUI:
    """Main GUI application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Transformation Tool")
        self.root.geometry("1000x800")
        
        self.transformer = None
        self.result = None
        self.comparison_image = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Left panel - Input
        input_frame = ttk.LabelFrame(main_frame, text="Input", padding="10")
        input_frame.grid(row=0, column=0, rowspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Input type selection
        ttk.Label(input_frame, text="Input Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_type = ttk.Combobox(input_frame, values=["Messages", "Image + Message"], 
                                       state="readonly", width=20)
        self.input_type.current(0)
        self.input_type.grid(row=0, column=1, pady=5, sticky=(tk.W, tk.E))
        self.input_type.bind("<<ComboboxSelected>>", self.on_input_type_change)
        
        # Messages input
        self.messages_frame = ttk.Frame(input_frame)
        self.messages_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(self.messages_frame, text="Message A:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.message_a_entry = ttk.Entry(self.messages_frame, width=30)
        self.message_a_entry.grid(row=0, column=1, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(self.messages_frame, text="Message B:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.message_b_entry = ttk.Entry(self.messages_frame, width=30)
        self.message_b_entry.grid(row=1, column=1, pady=5, sticky=(tk.W, tk.E))
        
        # Image input
        self.image_frame = ttk.Frame(input_frame)
        self.image_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        self.image_frame.grid_remove()
        
        ttk.Label(self.image_frame, text="QR Image:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.image_path_var = tk.StringVar()
        ttk.Entry(self.image_frame, textvariable=self.image_path_var, width=25, state="readonly").grid(
            row=0, column=1, pady=5, sticky=(tk.W, tk.E)
        )
        ttk.Button(self.image_frame, text="Browse", command=self.browse_image).grid(
            row=0, column=2, pady=5, padx=(5, 0)
        )
        
        ttk.Label(self.image_frame, text="Target Message:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.message_b_image_entry = ttk.Entry(self.image_frame, width=30)
        self.message_b_image_entry.grid(row=1, column=1, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # ECC level
        ttk.Label(input_frame, text="ECC Level:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.ecc_level = ttk.Combobox(input_frame, values=["L", "M", "Q", "H"], 
                                      state="readonly", width=20)
        self.ecc_level.current(1)  # Default to M
        self.ecc_level.grid(row=2, column=1, pady=5, sticky=(tk.W, tk.E))
        
        # Options
        self.use_exact_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(input_frame, text="Use Exact Algorithm", 
                       variable=self.use_exact_var).grid(row=3, column=0, columnspan=2, 
                                                         sticky=tk.W, pady=5)
        
        self.respect_ecc_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(input_frame, text="Respect ECC Capacity", 
                       variable=self.respect_ecc_var).grid(row=4, column=0, columnspan=2, 
                                                           sticky=tk.W, pady=5)
        
        # Transform button
        ttk.Button(input_frame, text="Transform", command=self.transform).grid(
            row=5, column=0, columnspan=2, pady=20, sticky=(tk.W, tk.E)
        )
        
        # Right panel - Results
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Stats
        stats_frame = ttk.Frame(results_frame)
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(stats_frame, text="Module Squares:").grid(row=0, column=0, padx=5)
        self.min_flips_label = ttk.Label(stats_frame, text="-", font=("Arial", 12, "bold"))
        self.min_flips_label.grid(row=0, column=1, padx=5)
        
        ttk.Label(stats_frame, text="Within ECC:").grid(row=0, column=2, padx=5)
        self.within_ecc_label = ttk.Label(stats_frame, text="-", font=("Arial", 12))
        self.within_ecc_label.grid(row=0, column=3, padx=5)
        
        # Image display
        self.image_label = ttk.Label(results_frame, text="No transformation yet")
        self.image_label.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Insights
        insights_frame = ttk.LabelFrame(results_frame, text="Insights", padding="10")
        insights_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        insights_frame.columnconfigure(0, weight=1)
        
        self.insights_text = tk.Text(insights_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.insights_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        insights_scroll = ttk.Scrollbar(insights_frame, orient=tk.VERTICAL, command=self.insights_text.yview)
        insights_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.insights_text.configure(yscrollcommand=insights_scroll.set)
        
        # Save button
        ttk.Button(results_frame, text="Save Result", command=self.save_result).grid(
            row=3, column=0, pady=10, sticky=(tk.W, tk.E)
        )
    
    def on_input_type_change(self, event=None):
        """Handle input type change."""
        if self.input_type.get() == "Messages":
            self.messages_frame.grid()
            self.image_frame.grid_remove()
        else:
            self.messages_frame.grid_remove()
            self.image_frame.grid()
    
    def browse_image(self):
        """Browse for QR code image."""
        filename = filedialog.askopenfilename(
            title="Select QR Code Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
        )
        if filename:
            self.image_path_var.set(filename)
    
    def transform(self):
        """Perform transformation."""
        try:
            input_type = self.input_type.get()
            ecc_level = self.ecc_level.get()
            use_exact = self.use_exact_var.get()
            respect_ecc = self.respect_ecc_var.get()
            
            self.transformer = QRTransformer(ecc_level=ecc_level)
            visualizer = QRVisualizer(module_size=8)
            
            if input_type == "Messages":
                message_a = self.message_a_entry.get()
                message_b = self.message_b_entry.get()
                
                if not message_b:
                    messagebox.showerror("Error", "Message B is required")
                    return
                
                if not message_a:
                    messagebox.showerror("Error", "Message A is required")
                    return
                
                self.result = self.transformer.transform(
                    message_a, message_b, use_exact=use_exact, respect_ecc=respect_ecc
                )
                
                qr_a = self.transformer.encoder.encode(message_a)
                matrix_a = qr_a.module_matrix
            else:
                image_path = self.image_path_var.get()
                message_b = self.message_b_image_entry.get()
                
                if not image_path:
                    messagebox.showerror("Error", "Please select a QR code image")
                    return
                
                if not message_b:
                    messagebox.showerror("Error", "Target message is required")
                    return
                
                self.result = self.transformer.transform_from_image(
                    image_path, message_b, use_exact=use_exact, respect_ecc=respect_ecc
                )
                
                from src.utils import image_to_matrix
                from PIL import Image
                img = Image.open(image_path)
                matrix_a = image_to_matrix(img)
            
            # Get target matrix
            qr_b = self.transformer.encoder.encode(self.result.message_b)
            matrix_b = qr_b.module_matrix
            
            # Ensure same dimensions
            if matrix_a.shape != matrix_b.shape:
                min_h = min(matrix_a.shape[0], matrix_b.shape[0])
                min_w = min(matrix_a.shape[1], matrix_b.shape[1])
                matrix_a = matrix_a[:min_h, :min_w]
                matrix_b = matrix_b[:min_h, :min_w]
                if self.result.transformed_matrix is not None:
                    self.result.transformed_matrix = self.result.transformed_matrix[:min_h, :min_w]
            
            # Generate visualization
            self.comparison_image = visualizer.create_comparison_grid(
                matrix_a, matrix_b, self.result.transformed_matrix, self.result.flip_positions
            )
            
            # Display results
            self.display_results()
            
        except Exception as e:
            messagebox.showerror("Error", f"Transformation failed: {str(e)}")
    
    def display_results(self):
        """Display transformation results."""
        if not self.result:
            return
        
        # Update stats
        self.min_flips_label.config(text=str(self.result.min_flips))
        self.within_ecc_label.config(
            text="Yes" if self.result.within_ecc else "No",
            foreground="green" if self.result.within_ecc else "red"
        )
        
        # Display image
        if self.comparison_image:
            # Resize to fit
            max_size = 600
            img = self.comparison_image.copy()
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo  # Keep a reference
        
        # Display insights
        insights = generate_insights(
            self.result, self.transformer.encoder, 
            self.result.transformed_matrix if self.result.transformed_matrix is not None 
            else np.zeros((1, 1)), 
            self.transformer.encoder.encode(self.result.message_b).module_matrix
        )
        
        self.insights_text.config(state=tk.NORMAL)
        self.insights_text.delete(1.0, tk.END)
        
        insights_text = f"""Transformation Summary:
  Module squares to change: {insights['transformation_summary']['min_flips']}
  Within ECC: {insights['transformation_summary']['within_ecc']}
  Success: {insights['transformation_summary']['success']}

ECC Information:
  Level: {insights['ecc_info']['level']}
  Capacity: {insights['ecc_info']['capacity']} codewords
  Utilization: {insights['ecc_info']['utilization']:.1f}%

Matrix Information:
  Size: {insights['matrix_info']['size']}
  Total modules: {insights['matrix_info']['total_modules']}
  Change percentage: {insights['matrix_info']['change_percentage']:.2f}%

Messages:
  Original: "{insights['messages']['original']}"
  Target: "{insights['messages']['target']}"
"""
        
        if insights.get('recommendations'):
            insights_text += "\nRecommendations:\n"
            for rec in insights['recommendations']:
                insights_text += f"  • {rec}\n"
        
        self.insights_text.insert(1.0, insights_text)
        self.insights_text.config(state=tk.DISABLED)
    
    def save_result(self):
        """Save the result image."""
        if not self.comparison_image:
            messagebox.showwarning("Warning", "No result to save")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Result",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if filename:
            self.comparison_image.save(filename)
            messagebox.showinfo("Success", f"Result saved to {filename}")


def main():
    """Main entry point."""
    root = tk.Tk()
    app = QRTransformationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

