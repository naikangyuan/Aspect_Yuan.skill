# Common PRM Mistakes

Use this reference to diagnose `.prm` files for ordinary geologists. The lint script can catch some structural issues, but ASPECT itself is still required to verify legal parameter names and plugin APIs.

## Boundary Names Do Not Match Geometry

Boundary indicators depend on the selected geometry. A box commonly uses names such as left/right/top/bottom/front/back, while spherical or chunk models use different indicators. If a boundary name is wrong, ASPECT may reject the file or impose a condition somewhere unintended.

Check:

- `Geometry model > Model name`
- `Boundary velocity model` indicators
- `Boundary temperature model` indicators
- `Boundary composition model` indicators
- `Mesh deformation boundary indicators`

## Dimensional And Nondimensional Values Are Mixed

Some benchmark setups use nondimensional units, while many cookbook-style geologic models use SI units and years in output. Mixing meters, kilometers, seconds, years, Celsius, and Kelvin changes the physics.

Check:

- `Use years in output instead of seconds`
- geometry extents
- velocities
- `End time`, timestep limits
- thermal and material constants

## Output Is Missing

A model can run successfully but produce too little information to answer the geological question.

Check:

- `Postprocess > List of postprocessors`
- `Postprocess > Visualization > List of output variables`
- `Time between graphical output`
- `Output directory`

## Composition Field Counts Do Not Match Material Lists

If `Compositional fields > Number of fields` and `Names of fields` do not match material parameter lists, geological units may be missing, misnamed, or assigned the wrong rheology.

Check:

- `Compositional fields > Number of fields`
- `Compositional fields > Names of fields`
- `Initial composition model`
- material model lists such as densities, viscosities, friction angles, cohesions, prefactors, or thermal properties

## Viscosity Bounds Dominate The Result

Very narrow or extreme `Minimum viscosity` and `Maximum viscosity` values can turn a geologic rheology into a clipped numerical model. This may hide weak zones or exaggerate strong lithosphere.

Check:

- `Material model` name
- viscosity law parameters
- `Minimum viscosity`
- `Maximum viscosity`
- `Viscosity averaging scheme`

## Time Step Is Too Large

Large timesteps can skip transient events, destabilize advection, or make nonlinear solves fail. This is common when geological time is entered in years but ASPECT expects seconds for a parameter.

Check:

- `CFL number`
- `Maximum time step`
- `End time`
- output interval
- mesh resolution near fast deformation or thermal gradients

## Temperature Boundary Does Not Match The Geological Problem

Surface, basal, side, inner, and outer temperatures encode the thermal regime. A plume, slab, rift, or lithosphere model can be scientifically wrong if the thermal boundary conditions are copied from a generic convection example.

Check:

- `Boundary temperature model`
- `Initial temperature model`
- `Top temperature`, `Bottom temperature`, `Inner temperature`, `Outer temperature`
- whether the initial geotherm is consistent with boundary values

## Plugin Library Or Plugin Name Is Missing

Custom cookbook and benchmark plugins often require compiled shared libraries.

Check:

- `Additional shared libraries`
- plugin `Model name` or `List of model names`
- whether the `.so` file exists after building
- whether the run log confirms loading the plugin

## Subsection Spelling Or Nesting Is Wrong

ASPECT parameter names and subsection names are exact. A misplaced `end` can put parameters in the wrong path.

Check:

- `subsection` and `end` balance
- duplicate subsection paths
- whether a `set` appears under the intended subsection
- local examples or `aspect --help` for spelling

## Numerical Fixes Change The Geology

Reducing viscosity contrast, changing boundary velocities, removing compositions, changing geometry, or switching rheology can make a run converge while invalidating the science.

Always report these as scientific changes, not just numerical fixes.
