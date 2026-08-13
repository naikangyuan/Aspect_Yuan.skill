# Model Family Version Map

Use this reference when the user describes a geology problem but not a specific paper.

## Selection Logic

First identify the model family, then choose the best starting point and version strategy. Do not assume every problem should use the latest checkout.

| User problem | Model family | First local references | Version strategy |
|---|---|---|---|
| mantle convection, thermal convection, Rayleigh number | mantle convection | `model_wizards/mantle_convection_wizard.md`, `assets/prm_templates/beginner_2d_box_convection.prm`, `cookbooks/convection-box/convection-box.prm` | Use local ASPECT first; only pin old versions for paper reproduction. |
| deep-shallow coupling, global mantle driving regional lithosphere | global-regional coupling | `references/aspect300_case_map.md`, `cookbooks/global_regional_coupling/global_regional_coupling.prm` | Version-sensitive; check required ascii boundary data format and local/global coupling scripts. |
| subduction, slab, trench migration, kinematic slab | subduction | `model_wizards/subduction_wizard.md`, `cookbooks/kinematically_driven_subduction_2d/kinematically_driven_subduction_2d_case1.prm`, `cookbooks/vankeken_subduction/vankeken_corner_flow.prm` | Pin to paper version if reproducing a published slab model; plugin/API drift is common. |
| continental rift, extension, breakup, lithosphere thinning | rift/extension | `model_wizards/rift_wizard.md`, `assets/prm_templates/beginner_rift.prm`, `cookbooks/continental_extension/continental_extension.prm` | Use local cookbook for new models; use paper code version for published rift cases. |
| lithosphere shortening, crustal thickening, collision | shortening | `model_wizards/lithosphere_shortening_wizard.md`, `assets/prm_templates/beginner_lithosphere_shortening.prm` | Often rheology-sensitive; verify visco-plastic parameter names against target ASPECT version. |
| weak zone, shear band, inherited fault, suture | weak zone | `model_wizards/weak_zone_wizard.md`, `assets/prm_templates/beginner_weak_zone.prm`, `benchmarks/finite_strain/simple_shear.prm`, `benchmarks/shear_bands/shear_bands.prm` | Start from local simple-shear benchmark; use paper version for nonlinear shear-band or melt cases. |
| plume, hot anomaly, plume-lithosphere interaction | plume | `model_wizards/plume_wizard.md`, `assets/prm_templates/beginner_plume.prm` | Check geometry: box/chunk/spherical; check temperature boundary and gravity model compatibility. |
| craton edge, keel, margin erosion, breakup interaction | craton edge | `model_wizards/craton_edge_wizard.md` | Usually research-level; likely needs paper-specific code, compositions, and rheology. |

## Response Rule

For a user geology request, return:

1. model family;
2. likely starting `.prm` or wizard;
3. version risk level: low, medium, high;
4. whether to search/download paper code;
5. minimum smoke test command.
