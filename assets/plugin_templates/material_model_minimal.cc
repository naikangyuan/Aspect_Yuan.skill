// Minimal ASPECT material model plugin template.
// Geological meaning: define how a rock or material domain converts temperature,
// pressure, and composition into density, viscosity, and thermal properties.

#include <aspect/material_model/interface.h>

#include <deal.II/base/parameter_handler.h>

namespace aspect
{
  namespace MaterialModel
  {
    template <int dim>
    class GeologistMinimalMaterial : public Interface<dim>
    {
      public:
        void evaluate (const MaterialModelInputs<dim> &in,
                       MaterialModelOutputs<dim> &out) const override
        {
          for (unsigned int i = 0; i < in.n_evaluation_points(); ++i)
            {
              out.viscosities[i] = viscosity;
              out.densities[i] = reference_density;
              out.thermal_expansion_coefficients[i] = thermal_expansivity;
              out.specific_heat[i] = specific_heat;
              out.thermal_conductivities[i] = thermal_conductivity;
              out.compressibilities[i] = 0.0;

              for (unsigned int c = 0; c < in.composition[i].size(); ++c)
                out.reaction_terms[i][c] = 0.0;
            }
        }

        bool is_compressible () const override
        {
          return false;
        }

        static void declare_parameters (ParameterHandler &prm)
        {
          prm.enter_subsection("Material model");
          {
            prm.enter_subsection("Geologist minimal material");
            {
              prm.declare_entry("Reference density", "3300",
                                Patterns::Double(0),
                                "Density of the geological material in kg/m^3.");
              prm.declare_entry("Viscosity", "1e21",
                                Patterns::Double(0),
                                "Viscosity of the geological material in Pa s.");
              prm.declare_entry("Thermal expansivity", "3e-5",
                                Patterns::Double(0),
                                "Thermal expansivity in 1/K.");
              prm.declare_entry("Specific heat", "1250",
                                Patterns::Double(0),
                                "Specific heat capacity in J/(kg K).");
              prm.declare_entry("Thermal conductivity", "4.7",
                                Patterns::Double(0),
                                "Thermal conductivity in W/(m K).");
            }
            prm.leave_subsection();
          }
          prm.leave_subsection();
        }

        void parse_parameters (ParameterHandler &prm) override
        {
          prm.enter_subsection("Material model");
          {
            prm.enter_subsection("Geologist minimal material");
            {
              reference_density = prm.get_double("Reference density");
              viscosity = prm.get_double("Viscosity");
              thermal_expansivity = prm.get_double("Thermal expansivity");
              specific_heat = prm.get_double("Specific heat");
              thermal_conductivity = prm.get_double("Thermal conductivity");
            }
            prm.leave_subsection();
          }
          prm.leave_subsection();

          this->model_dependence.viscosity = NonlinearDependence::none;
          this->model_dependence.density = NonlinearDependence::none;
          this->model_dependence.compressibility = NonlinearDependence::none;
          this->model_dependence.specific_heat = NonlinearDependence::none;
          this->model_dependence.thermal_conductivity = NonlinearDependence::none;
        }

      private:
        double reference_density = 3300.0;
        double viscosity = 1e21;
        double thermal_expansivity = 3e-5;
        double specific_heat = 1250.0;
        double thermal_conductivity = 4.7;
    };
  }
}

namespace aspect
{
  namespace MaterialModel
  {
    ASPECT_REGISTER_MATERIAL_MODEL(GeologistMinimalMaterial,
                                   "geologist minimal material",
                                   "Minimal external material model template for geologist-defined "
                                   "constant density, viscosity, and thermal properties. "
                                   "TODO: verify with ASPECT 3.0.0 API before using in production.")
  }
}
