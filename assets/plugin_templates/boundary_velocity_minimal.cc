// Minimal ASPECT boundary velocity plugin template.
// Geological meaning: impose a simple plate or wall velocity on selected boundaries.

#include <aspect/boundary_velocity/interface.h>

#include <deal.II/base/parameter_handler.h>

namespace aspect
{
  namespace BoundaryVelocity
  {
    template <int dim>
    class GeologistMinimalBoundaryVelocity : public Interface<dim>
    {
      public:
        Tensor<1,dim>
        boundary_velocity (const types::boundary_id,
                           const Point<dim> &) const override
        {
          Tensor<1,dim> velocity;
          velocity[0] = x_velocity;
          if (dim > 1)
            velocity[1] = y_velocity;
          if (dim > 2)
            velocity[2] = z_velocity;
          return velocity;
        }

        static void declare_parameters (ParameterHandler &prm)
        {
          prm.enter_subsection("Boundary velocity model");
          {
            prm.enter_subsection("Geologist minimal boundary velocity");
            {
              prm.declare_entry("X velocity", "0",
                                Patterns::Double(),
                                "Boundary velocity x component in m/s unless the selected ASPECT model interprets values otherwise.");
              prm.declare_entry("Y velocity", "0",
                                Patterns::Double(),
                                "Boundary velocity y component in m/s.");
              prm.declare_entry("Z velocity", "0",
                                Patterns::Double(),
                                "Boundary velocity z component in m/s for 3-D models.");
            }
            prm.leave_subsection();
          }
          prm.leave_subsection();
        }

        void parse_parameters (ParameterHandler &prm) override
        {
          prm.enter_subsection("Boundary velocity model");
          {
            prm.enter_subsection("Geologist minimal boundary velocity");
            {
              x_velocity = prm.get_double("X velocity");
              y_velocity = prm.get_double("Y velocity");
              z_velocity = prm.get_double("Z velocity");
            }
            prm.leave_subsection();
          }
          prm.leave_subsection();
        }

      private:
        double x_velocity = 0.0;
        double y_velocity = 0.0;
        double z_velocity = 0.0;
    };
  }
}

namespace aspect
{
  namespace BoundaryVelocity
  {
    ASPECT_REGISTER_BOUNDARY_VELOCITY_MODEL(GeologistMinimalBoundaryVelocity,
                                            "geologist minimal boundary velocity",
                                            "Minimal external boundary velocity model template. "
                                            "TODO: verify boundary indicator syntax and ASPECT 3.0.0 API.")
  }
}
