#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "operations.hpp"

namespace py = pybind11;

PYBIND11_MODULE(pyfunc_native, m) {
    m.doc() = "PyFunc C++ backend for high-performance operations";
    
    // Map operations
    m.def("map_operation", &pyfunc::Operations::map_operation,
          "Apply a map operation to numeric data",
          py::arg("data"), py::arg("op_code"));
    
    m.def("map_add", &pyfunc::Operations::map_add,
          "Add a constant to all elements",
          py::arg("data"), py::arg("operand"));
    
    m.def("map_mul", &pyfunc::Operations::map_mul,
          "Multiply all elements by a constant",
          py::arg("data"), py::arg("operand"));
    
    m.def("map_sub", &pyfunc::Operations::map_sub,
          "Subtract a constant from all elements",
          py::arg("data"), py::arg("operand"));
    
    m.def("map_div", &pyfunc::Operations::map_div,
          "Divide all elements by a constant",
          py::arg("data"), py::arg("operand"));
    
    // Filter operations
    m.def("filter_operation", &pyfunc::Operations::filter_operation,
          "Apply a filter operation to numeric data",
          py::arg("data"), py::arg("op_code"));
    
    m.def("filter_gt", &pyfunc::Operations::filter_gt,
          "Filter elements greater than threshold",
          py::arg("data"), py::arg("threshold"));
    
    m.def("filter_lt", &pyfunc::Operations::filter_lt,
          "Filter elements less than threshold",
          py::arg("data"), py::arg("threshold"));
    
    m.def("filter_ge", &pyfunc::Operations::filter_ge,
          "Filter elements greater than or equal to threshold",
          py::arg("data"), py::arg("threshold"));
    
    m.def("filter_le", &pyfunc::Operations::filter_le,
          "Filter elements less than or equal to threshold",
          py::arg("data"), py::arg("threshold"));
    
    m.def("filter_eq", &pyfunc::Operations::filter_eq,
          "Filter elements equal to value",
          py::arg("data"), py::arg("value"));
    
    m.def("filter_ne", &pyfunc::Operations::filter_ne,
          "Filter elements not equal to value",
          py::arg("data"), py::arg("value"));
    
    // Reduce operations
    m.def("reduce_operation", &pyfunc::Operations::reduce_operation,
          "Apply a reduce operation to numeric data",
          py::arg("data"), py::arg("op_code"));
    
    m.def("reduce_operation_with_init", &pyfunc::Operations::reduce_operation_with_init,
          "Apply a reduce operation with initial value",
          py::arg("data"), py::arg("op_code"), py::arg("initializer"));
    
    m.def("reduce_add", &pyfunc::Operations::reduce_add,
          "Sum all elements",
          py::arg("data"));
    
    m.def("reduce_add_with_init", &pyfunc::Operations::reduce_add_with_init,
          "Sum all elements with initial value",
          py::arg("data"), py::arg("init"));
    
    m.def("reduce_mul", &pyfunc::Operations::reduce_mul,
          "Multiply all elements",
          py::arg("data"));
    
    m.def("reduce_mul_with_init", &pyfunc::Operations::reduce_mul_with_init,
          "Multiply all elements with initial value",
          py::arg("data"), py::arg("init"));
    
    // Aggregation operations
    m.def("sum_operation", &pyfunc::Operations::sum_operation,
          "Sum all elements in the data",
          py::arg("data"));
    
    m.def("min_operation", &pyfunc::Operations::min_operation,
          "Find minimum element in the data",
          py::arg("data"));
    
    m.def("max_operation", &pyfunc::Operations::max_operation,
          "Find maximum element in the data",
          py::arg("data"));
    
    m.def("count_operation", &pyfunc::Operations::count_operation,
          "Count elements in the data",
          py::arg("data"));
}