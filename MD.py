import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pymatgen.core.structure import Structure
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


class MolecularDynamicsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Molecular Dynamics Tool")

        # Variables
        self.xdatcar_file = None
        self.output_dir = None
        self.results = []
        self.atom_pair = None
        self.neighbor_distance = None
        self.condition = None

        # Create GUI Layout
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="XDATCAR File:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.file_entry = tk.Entry(self.root, width=50)
        self.file_entry.grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.browse_xdatcar).grid(row=0, column=2, padx=10, pady=10)

        tk.Label(self.root, text="Output Directory:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.dir_entry = tk.Entry(self.root, width=50)
        self.dir_entry.grid(row=1, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.browse_output_dir).grid(row=1, column=2, padx=10, pady=10)

        tk.Label(self.root, text="Atom Pair (e.g., C-Br):").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.atom_pair_entry = tk.Entry(self.root, width=50)
        self.atom_pair_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Neighbor Distance (Å):").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.distance_entry = tk.Entry(self.root, width=50)
        self.distance_entry.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Condition (less/greater):").grid(row=4, column=0, padx=10, pady=10, sticky="e")
        self.condition_entry = tk.Entry(self.root, width=50)
        self.condition_entry.grid(row=4, column=1, padx=10, pady=10)

        tk.Button(self.root, text="Analyze Distances", command=self.analyze_distances).grid(
            row=5, column=0, columnspan=3, pady=20
        )

    def browse_xdatcar(self):
        self.xdatcar_file = filedialog.askopenfilename(filetypes=[("XDATCAR Files", "*.XDATCAR"), ("All Files", "*.*")])
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, self.xdatcar_file)

    def browse_output_dir(self):
        self.output_dir = filedialog.askdirectory()
        self.dir_entry.delete(0, tk.END)
        self.dir_entry.insert(0, self.output_dir)

    def analyze_distances(self):
        if not self.xdatcar_file or not self.output_dir:
            messagebox.showerror("Error", "Please select an XDATCAR file and output directory.")
            return

        # Get user input for atom pair, neighbor distance, and condition
        self.atom_pair = self.atom_pair_entry.get()
        try:
            self.neighbor_distance = float(self.distance_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please provide a valid neighbor distance.")
            return

        self.condition = self.condition_entry.get().strip().lower()
        if not self.atom_pair or self.neighbor_distance <= 0 or self.condition not in ["less", "greater"]:
            messagebox.showerror("Error", "Please provide valid inputs for analysis.")
            return

        heatmap_dir = os.path.join(self.output_dir, f"Heatmaps_{self.atom_pair}_Distances")
        specific_dir = os.path.join(self.output_dir, f"Specific_{self.atom_pair}_Distances")
        all_dir = os.path.join(self.output_dir, "All_POSCARS")
        os.makedirs(specific_dir, exist_ok=True)
        os.makedirs(all_dir, exist_ok=True)
        os.makedirs(heatmap_dir, exist_ok=True)

        with open(self.xdatcar_file, 'r') as f:
            xdat = f.read()

        poscars_raw = xdat.split("Direct")
        self.results = []

        for i in range(1, len(poscars_raw)):
            poscar_content = poscars_raw[0] + "Direct" + poscars_raw[i]
            poscar_path = os.path.join(all_dir, f"POSCAR_{i}")
            with open(poscar_path, 'w') as f:
                f.write(poscar_content)

            structure = Structure.from_file(poscar_path)
            num_atoms = len(structure)
            specific_entries = []

            for atom1 in range(num_atoms):
                for atom2 in range(atom1 + 1, num_atoms):
                    distance = structure[atom1].distance(structure[atom2])
                    element1 = structure[atom1].species_string
                    element2 = structure[atom2].species_string

                    if (
                        f"{element1}-{element2}" == self.atom_pair
                        or f"{element2}-{element1}" == self.atom_pair
                    ):
                        if (self.condition == "less" and distance <= self.neighbor_distance) or (
                            self.condition == "greater" and distance >= self.neighbor_distance
                        ):
                            result_entry = (f"POSCAR_{i}", element1, atom1 + 1, element2, atom2 + 1, distance)
                            self.results.append(result_entry)
                            specific_entries.append(result_entry)

            if specific_entries:
                specific_poscar_path = os.path.join(specific_dir, f"POSCAR_{i}")
                with open(specific_poscar_path, 'w') as f:
                    f.write(poscar_content)

                self.save_heatmap(structure, heatmap_dir, i, title=f"Heatmap - {self.atom_pair} Distances")

        self.write_results()
        self.plot_overall_results()
        messagebox.showinfo("Success", f"Analysis complete. Results saved in {self.output_dir}.")

    def save_heatmap(self, structure, directory, poscar_index, title):
        num_atoms = len(structure)
        matrix = np.zeros((num_atoms, num_atoms))

        for atom1 in range(num_atoms):
            for atom2 in range(atom1 + 1, num_atoms):
                distance = structure[atom1].distance(structure[atom2])
                matrix[atom1, atom2] = matrix[atom2, atom1] = distance

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(matrix, cmap="viridis", ax=ax)
        ax.set_title(f"{title} (POSCAR_{poscar_index})")
        ax.set_xlabel("Atom Index")
        ax.set_ylabel("Atom Index")
        plt.savefig(os.path.join(directory, f"Heatmap_POSCAR_{poscar_index}.png"))
        plt.close(fig)

    def write_results(self):
        results_file = os.path.join(self.output_dir, "specific_distance_results.txt")

        with open(results_file, 'w') as rf:
            rf.write(
                f"Specific Distance Results for {self.atom_pair} (Neighbor Distance {self.condition} {self.neighbor_distance} Å)\n"
            )
            rf.write("=" * 50 + "\n\n")
            for entry in sorted(self.results, key=lambda x: int(x[0].split('_')[1])):
                rf.write(
                    f"POSCAR: {entry[0]}, Atoms: {entry[1]}-{entry[2]} and {entry[3]}-{entry[4]}, Distance: {entry[5]:.4f} Å\n"
                )

# Main Application Loop
if __name__ == "__main__":
    root = tk.Tk()
    app = MolecularDynamicsApp(root)
    root.mainloop()


