// Minimal ASPECT postprocessor plugin template.
// Geological meaning: write one custom diagnostic to the statistics file.

#include <aspect/postprocess/interface.h>
#include <aspect/simulator_access.h>

#include <deal.II/base/parameter_handler.h>
#include <deal.II/base/table_handler.h>

namespace aspect
{
  namespace Postprocess
  {
    template <int dim>
    class GeologistMinimalPostprocessor : public Interface<dim>, public SimulatorAccess<dim>
    {
      public:
        std::pair<std::string,std::string>
        execute (TableHandler &statistics) override
        {
          // TODO: replace with a geological diagnostic such as trench position,
          // integrated weak-zone strain, plume flux, or lithosphere thickness.
          const double model_time = this->get_time();
          statistics.add_value("Geologist minimal diagnostic time", model_time);
          return std::make_pair("Geologist diagnostic time", std::to_string(model_time));
        }

        static void declare_parameters (ParameterHandler &prm)
        {
          prm.enter_subsection("Postprocess");
          {
            prm.enter_subsection("Geologist minimal postprocessor");
            {
              prm.declare_entry("Diagnostic name", "geologist diagnostic",
                                Patterns::Anything(),
                                "Name of the custom geological diagnostic.");
            }
            prm.leave_subsection();
          }
          prm.leave_subsection();
        }

        void parse_parameters (ParameterHandler &prm) override
        {
          prm.enter_subsection("Postprocess");
          {
            prm.enter_subsection("Geologist minimal postprocessor");
            {
              diagnostic_name = prm.get("Diagnostic name");
            }
            prm.leave_subsection();
          }
          prm.leave_subsection();
        }

      private:
        std::string diagnostic_name = "geologist diagnostic";
    };
  }
}

namespace aspect
{
  namespace Postprocess
  {
    ASPECT_REGISTER_POSTPROCESSOR(GeologistMinimalPostprocessor,
                                  "geologist minimal postprocessor",
                                  "Minimal external postprocessor template. "
                                  "TODO: verify ASPECT 3.0.0 API for the intended diagnostic.")
  }
}
