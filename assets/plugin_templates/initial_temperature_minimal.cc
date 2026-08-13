// Minimal ASPECT initial temperature plugin template.
// Geological meaning: define a simple initial geotherm or thermal anomaly.

#include <aspect/initial_temperature/interface.h>

#include <deal.II/base/parameter_handler.h>

namespace aspect
{
  namespace InitialTemperature
  {
    template <int dim>
    class GeologistMinimalInitialTemperature : public Interface<dim>
    {
      public:
        double initial_temperature (const Point<dim> &position) const override
        {
          // TODO: replace this with the intended geological geotherm.
          // This default uses a linear vertical gradient with coordinate dim-1.
          return surface_temperature + vertical_gradient * position[dim-1];
        }

        static void declare_parameters (ParameterHandler &prm)
        {
          prm.enter_subsection("Initial temperature model");
          {
            prm.enter_subsection("Geologist minimal initial temperature");
            {
              prm.declare_entry("Surface temperature", "273",
                                Patterns::Double(0),
                                "Reference surface temperature in K.");
              prm.declare_entry("Vertical temperature gradient", "0.0005",
                                Patterns::Double(),
                                "Linear temperature gradient in K/m along the last coordinate.");
            }
            prm.leave_subsection();
          }
          prm.leave_subsection();
        }

        void parse_parameters (ParameterHandler &prm) override
        {
          prm.enter_subsection("Initial temperature model");
          {
            prm.enter_subsection("Geologist minimal initial temperature");
            {
              surface_temperature = prm.get_double("Surface temperature");
              vertical_gradient = prm.get_double("Vertical temperature gradient");
            }
            prm.leave_subsection();
          }
          prm.leave_subsection();
        }

      private:
        double surface_temperature = 273.0;
        double vertical_gradient = 5e-4;
    };
  }
}

namespace aspect
{
  namespace InitialTemperature
  {
    ASPECT_REGISTER_INITIAL_TEMPERATURE_MODEL(GeologistMinimalInitialTemperature,
                                              "geologist minimal initial temperature",
                                              "Minimal external initial temperature model template. "
                                              "TODO: verify coordinate convention and ASPECT 3.0.0 API.")
  }
}
