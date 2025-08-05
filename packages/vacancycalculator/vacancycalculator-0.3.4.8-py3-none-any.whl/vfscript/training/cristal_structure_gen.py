import os
import numpy as np
from pathlib import Path
from typing import Tuple

class CrystalStructureGenerator:
    """
    Genera una estructura BCC o FCC perfecta alineada a la caja del dump defectuoso.
    Escribe un dump LAMMPS con los mismos límites y sin vacancias.
    """
    def __init__(self, config: dict, out_dir: Path):
        self.config = config
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

        # Ruta al dump defectuoso
        defect_cfg = config.get('defect') or (config.get('CONFIG')[0].get('defect') if config.get('CONFIG') else None)
        if not defect_cfg:
            raise ValueError("No se encontró la clave 'defect' en la configuración")
        self.path_defect = Path(defect_cfg[0] if isinstance(defect_cfg, list) else defect_cfg)
        if not self.path_defect.exists():
            raise FileNotFoundError(f"No se encontró el dump defectuoso: {self.path_defect}")

        # Tipo de red y parámetro de red (a)
        self.structure_type = config['generate_relax'][0].lower()
        self.lattice = float(config['generate_relax'][1])
        if self.structure_type not in ('bcc','fcc'):
            raise ValueError("generate_relax debe indicar 'bcc' o 'fcc' como primer elemento")

        # Leer límites de caja del dump defectuoso
        self._read_defect_box()

    def _read_defect_box(self):
        lines = self.path_defect.read_text().splitlines()
        idx = next((i for i,l in enumerate(lines) if 'BOX BOUNDS' in l), None)
        if idx is None or idx+3>len(lines):
            raise ValueError("No se encontró 'BOX BOUNDS' en el dump")
        bounds = []
        for line in lines[idx+1:idx+4]:
            lo, hi = map(float, line.split()[:2])
            bounds.append((lo,hi))
        (self.xlo,self.xhi), (self.ylo,self.yhi), (self.zlo,self.zhi) = bounds

    def generate(self) -> Path:
        # Bases unitarias
        if self.structure_type == 'fcc':
            basis = np.array([[0,0,0],[0.5,0.5,0],[0.5,0,0.5],[0,0.5,0.5]]) * self.lattice
        else:  # bcc
            basis = np.array([[0,0,0],[0.5,0.5,0.5]]) * self.lattice

        # Número de repeticiones para cubrir la caja
        nx = int(np.ceil((self.xhi - self.xlo) / self.lattice))
        ny = int(np.ceil((self.yhi - self.ylo) / self.lattice))
        nz = int(np.ceil((self.zhi - self.zlo) / self.lattice))

        coords = []
        origin = np.array([self.xlo, self.ylo, self.zlo])
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    shift = np.array([i,j,k]) * self.lattice
                    for v in basis:
                        pos = origin + shift + v
                        if (self.xlo <= pos[0] < self.xhi and
                            self.ylo <= pos[1] < self.yhi and
                            self.zlo <= pos[2] < self.zhi):
                            coords.append(pos)
        # Eliminar duplicados con tolerancia
        coords = np.unique(np.round(np.array(coords),6), axis=0)

        # Escribir dump
        out_file = self.out_dir / 'relax_structure.dump'
        self._write_dump(coords, out_file)
        return out_file

    def _write_dump(self, coords: np.ndarray, out_file: Path):
        xlo,xhi,ylo,yhi,zlo,zhi = self.xlo, self.xhi, self.ylo, self.yhi, self.zlo, self.zhi
        with out_file.open('w') as f:
            f.write("ITEM: TIMESTEP\n0\n")
            f.write(f"ITEM: NUMBER OF ATOMS\n{len(coords)}\n")
            f.write("ITEM: BOX BOUNDS pp pp pp\n")
            f.write(f"{xlo} {xhi}\n{ylo} {yhi}\n{zlo} {zhi}\n")
            f.write("ITEM: ATOMS id type x y z\n")
            for idx,(x,y,z) in enumerate(coords, start=1):
                f.write(f"{idx} 1 {x:.6f} {y:.6f} {z:.6f}\n")
