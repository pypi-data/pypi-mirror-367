## Method and Theory

Three atoms are placed in an otherwise empty system.  The relative positions of the atoms are determined by the following three coordinates

- r_ij is the radial distance between atoms i and j,
- r_ik is the radial distance between atoms i and k, and
- theta_ijk is the angle formed between the i-j and i-k vectors.

Based on these three bond coordinates, the full positions of the three atoms in the system are determined as follows

- Atom i is positioned at the system's origin, [0, 0, 0]
- Atom j is placed r_ij away from atom i along the x coordinate, [r_ij, 0.0, 0.0]
- Atom k is placed in the xy plane based on r_ik and theta_ijk, [r_ik cos(theta_ijk), r_ik sin(theta_ijk), 0.0]

Values of r_ij, r_ik and theta_ijk are iterated over. The potential energy of the three atoms is evaluated for each configuration corresponding to the different coordinate sets.
