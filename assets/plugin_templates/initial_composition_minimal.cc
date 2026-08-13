// Minimal ASPECT initial composition plugin template.
// Geological meaning: place a simple rock unit, slab, craton, or weak zone at time zero.

#include <aspect/initial_composition/interface.h>

#include <deal.II/base/parameter_handler.h>

namespace aspect
{
  namespace InitialComposition
  {
    template <int dim>
    class GeologistMinimalInitialComposition : public Interface<dim>
    {
      public:
        double initial_composition (const Point<dim> &position,
                                    const unsigned int n_comp) const override
        {
          // TODO: replace this box-shaped marker with the intended geology.
          if (n_comp != compositional_field_index)
            return 0.0;

          const bool inside_x = position[0] >= min_x && position[0] <= max_x;
          const bool inside_y = (dim < 2) || (position[1] >= min_y && position[1] <= max_y);
          const bool inside_z = (dim < 3) || (position[2] >= min_z && position[2] <= max_z);
          return (inside_x && inside_y && inside_z) ? inside_value : outside_value;
        }

        static void declare_parameters (ParameterHandler &prm)
        {
          prm.enter_subsection("Initial composition model");
          {
            prm.enter_subsection("Geologist minimal initial composition");
            {
              prm.declare_entry("Compositional field index", "0",
                                Patterns::Integer(0),
                                "Zero-based compositional field index this plugin initializes.");
              prm.declare_entry("Inside value", "1",
                                Patterns::Double(),
                                "Composition value inside the geological domain.");
              prm.declare_entry("Outside value", "0",
                                Patterns::Double(),
                                "Composition value outside the geological domain.");
              prm.declare_entry("Minimum x", "0", Patterns::Double(), "Minimum x coordinate.");
              prm.declare_entry("Maximum x", "1e5", Patterns::Double(), "Maximum x coordinate.");
              prm.declare_entry("Minimum y", "0", Patterns::Double(), "Minimum y coordinate.");
              prm.declare_entry("Maximum y", "1e5", Patterns::Double(), "Maximum y coordinate.");
              prm.declare_entry("Minimum z", "0", Patterns::Double(), "Minimum z coordinate.");
              prm.declare_entry("Maximum z", "1e5", Patterns::Double(), "Maximum z coordinate.");
            }
            prm.leave_subsection();
          }
          prm.leave_subsection();
        }

        void parse_parameters (ParameterHandler &prm) override
        {
          prm.enter_subsection("Initial composition model");
          {
            prm.enter_subsection("Geologist minimal initial composition");
            {
              compositional_field_index = prm.get_integer("Compositional field index");
              inside_value = prm.get_double("Inside value");
              outside_value = prm.get_double("Outside value");
              min_x = prm.get_double("Minimum x");
              max_x = prm.get_double("Maximum x");
              min_y = prm.get_double("Minimum y");
              max_y = prm.get_double("Maximum y");
              min_z = prm.get_double("Minimum z");
              max_z = prm.get_double("Maximum z");
            }
            prm.leave_subsection();
          }
          prm.leave_subsection();
        }

      private:
        unsigned int compositional_field_index = 0;
        double inside_value = 1.0;
        double outside_value = 0.0;
        double min_x = 0.0, max_x = 1e5;
        double min_y = 0.0, max_y = 1e5;
        double min_z = 0.0, max_z = 1e5;
    };
  }
}

namespace aspect
{
  namespace InitialComposition
  {
    ASPECT_REGISTER_INITIAL_COMPOSITION_MODEL(GeologistMinimalInitialComposition,
                                              "geologist minimal initial composition",
                                              "Minimal external initial composition model template. "
                                              "TODO: verify field indexing and ASPECT 3.0.0 API.")
  }
}
