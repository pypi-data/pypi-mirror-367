#pragma once

#include <vector>
#include <string>
#include <functional>

namespace pyfunc {

// Type aliases for cleaner code
using NumberVector = std::vector<double>;
using NumberList = std::vector<double>;

// Operation types
enum class OpType {
    ADD,
    SUB, 
    MUL,
    DIV,
    GT,
    LT,
    GE,
    LE,
    EQ,
    NE,
    IDENTITY
};

// Parse operation string to OpType and operand
struct Operation {
    OpType type;
    double operand;
    
    Operation(const std::string& op_code);
};

// Core operations
class Operations {
public:
    // Map operations
    static NumberVector map_add(const NumberVector& data, double operand);
    static NumberVector map_mul(const NumberVector& data, double operand);
    static NumberVector map_sub(const NumberVector& data, double operand);
    static NumberVector map_div(const NumberVector& data, double operand);
    
    // Generic map with operation
    static NumberVector map_operation(const NumberVector& data, const std::string& op_code);
    
    // Filter operations
    static NumberVector filter_gt(const NumberVector& data, double threshold);
    static NumberVector filter_lt(const NumberVector& data, double threshold);
    static NumberVector filter_ge(const NumberVector& data, double threshold);
    static NumberVector filter_le(const NumberVector& data, double threshold);
    static NumberVector filter_eq(const NumberVector& data, double value);
    static NumberVector filter_ne(const NumberVector& data, double value);
    
    // Generic filter with operation
    static NumberVector filter_operation(const NumberVector& data, const std::string& op_code);
    
    // Reduce operations
    static double reduce_add(const NumberVector& data);
    static double reduce_add_with_init(const NumberVector& data, double init);
    static double reduce_mul(const NumberVector& data);
    static double reduce_mul_with_init(const NumberVector& data, double init);
    
    // Generic reduce with operation
    static double reduce_operation(const NumberVector& data, const std::string& op_code);
    static double reduce_operation_with_init(const NumberVector& data, const std::string& op_code, double init);
    
    // Aggregation operations
    static double sum_operation(const NumberVector& data);
    static double min_operation(const NumberVector& data);
    static double max_operation(const NumberVector& data);
    static size_t count_operation(const NumberVector& data);
    
private:
    // Helper functions
    static std::function<double(double)> create_map_function(const Operation& op);
    static std::function<bool(double)> create_filter_function(const Operation& op);
    static std::function<double(double, double)> create_reduce_function(const Operation& op);
};

} // namespace pyfunc