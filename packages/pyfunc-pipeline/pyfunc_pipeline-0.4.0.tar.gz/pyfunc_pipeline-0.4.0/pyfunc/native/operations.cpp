#include "operations.hpp"
#include <algorithm>
#include <numeric>
#include <stdexcept>
#include <sstream>

namespace pyfunc {

// Parse operation string like "add_5", "mul_2.5", "gt_10"
Operation::Operation(const std::string& op_code) {
    size_t underscore_pos = op_code.find('_');
    if (underscore_pos == std::string::npos) {
        type = OpType::IDENTITY;
        operand = 0.0;
        return;
    }
    
    std::string op_name = op_code.substr(0, underscore_pos);
    std::string operand_str = op_code.substr(underscore_pos + 1);
    
    // Parse operand
    try {
        operand = std::stod(operand_str);
    } catch (const std::exception&) {
        operand = 0.0;
    }
    
    // Parse operation type
    if (op_name == "add") type = OpType::ADD;
    else if (op_name == "sub") type = OpType::SUB;
    else if (op_name == "mul") type = OpType::MUL;
    else if (op_name == "div") type = OpType::DIV;
    else if (op_name == "gt") type = OpType::GT;
    else if (op_name == "lt") type = OpType::LT;
    else if (op_name == "ge") type = OpType::GE;
    else if (op_name == "le") type = OpType::LE;
    else if (op_name == "eq") type = OpType::EQ;
    else if (op_name == "ne") type = OpType::NE;
    else type = OpType::IDENTITY;
}

// Map operations
NumberVector Operations::map_add(const NumberVector& data, double operand) {
    NumberVector result;
    result.reserve(data.size());
    
    for (double value : data) {
        result.push_back(value + operand);
    }
    
    return result;
}

NumberVector Operations::map_mul(const NumberVector& data, double operand) {
    NumberVector result;
    result.reserve(data.size());
    
    for (double value : data) {
        result.push_back(value * operand);
    }
    
    return result;
}

NumberVector Operations::map_sub(const NumberVector& data, double operand) {
    NumberVector result;
    result.reserve(data.size());
    
    for (double value : data) {
        result.push_back(value - operand);
    }
    
    return result;
}

NumberVector Operations::map_div(const NumberVector& data, double operand) {
    if (operand == 0.0) {
        throw std::runtime_error("Division by zero");
    }
    
    NumberVector result;
    result.reserve(data.size());
    
    for (double value : data) {
        result.push_back(value / operand);
    }
    
    return result;
}

NumberVector Operations::map_operation(const NumberVector& data, const std::string& op_code) {
    Operation op(op_code);
    auto map_func = create_map_function(op);
    
    NumberVector result;
    result.reserve(data.size());
    
    for (double value : data) {
        result.push_back(map_func(value));
    }
    
    return result;
}

// Filter operations
NumberVector Operations::filter_gt(const NumberVector& data, double threshold) {
    NumberVector result;
    
    for (double value : data) {
        if (value > threshold) {
            result.push_back(value);
        }
    }
    
    return result;
}

NumberVector Operations::filter_lt(const NumberVector& data, double threshold) {
    NumberVector result;
    
    for (double value : data) {
        if (value < threshold) {
            result.push_back(value);
        }
    }
    
    return result;
}

NumberVector Operations::filter_ge(const NumberVector& data, double threshold) {
    NumberVector result;
    
    for (double value : data) {
        if (value >= threshold) {
            result.push_back(value);
        }
    }
    
    return result;
}

NumberVector Operations::filter_le(const NumberVector& data, double threshold) {
    NumberVector result;
    
    for (double value : data) {
        if (value <= threshold) {
            result.push_back(value);
        }
    }
    
    return result;
}

NumberVector Operations::filter_eq(const NumberVector& data, double value) {
    NumberVector result;
    
    for (double item : data) {
        if (item == value) {
            result.push_back(item);
        }
    }
    
    return result;
}

NumberVector Operations::filter_ne(const NumberVector& data, double value) {
    NumberVector result;
    
    for (double item : data) {
        if (item != value) {
            result.push_back(item);
        }
    }
    
    return result;
}

NumberVector Operations::filter_operation(const NumberVector& data, const std::string& op_code) {
    Operation op(op_code);
    auto filter_func = create_filter_function(op);
    
    NumberVector result;
    
    for (double value : data) {
        if (filter_func(value)) {
            result.push_back(value);
        }
    }
    
    return result;
}

// Reduce operations
double Operations::reduce_add(const NumberVector& data) {
    return std::accumulate(data.begin(), data.end(), 0.0);
}

double Operations::reduce_add_with_init(const NumberVector& data, double init) {
    return std::accumulate(data.begin(), data.end(), init);
}

double Operations::reduce_mul(const NumberVector& data) {
    return std::accumulate(data.begin(), data.end(), 1.0, std::multiplies<double>());
}

double Operations::reduce_mul_with_init(const NumberVector& data, double init) {
    return std::accumulate(data.begin(), data.end(), init, std::multiplies<double>());
}

double Operations::reduce_operation(const NumberVector& data, const std::string& op_code) {
    if (data.empty()) {
        throw std::runtime_error("Cannot reduce empty sequence");
    }
    
    Operation op(op_code);
    auto reduce_func = create_reduce_function(op);
    
    double result = data[0];
    for (size_t i = 1; i < data.size(); ++i) {
        result = reduce_func(result, data[i]);
    }
    
    return result;
}

double Operations::reduce_operation_with_init(const NumberVector& data, const std::string& op_code, double init) {
    Operation op(op_code);
    auto reduce_func = create_reduce_function(op);
    
    double result = init;
    for (double value : data) {
        result = reduce_func(result, value);
    }
    
    return result;
}

// Aggregation operations
double Operations::sum_operation(const NumberVector& data) {
    return std::accumulate(data.begin(), data.end(), 0.0);
}

double Operations::min_operation(const NumberVector& data) {
    if (data.empty()) {
        throw std::runtime_error("Cannot find min of empty sequence");
    }
    return *std::min_element(data.begin(), data.end());
}

double Operations::max_operation(const NumberVector& data) {
    if (data.empty()) {
        throw std::runtime_error("Cannot find max of empty sequence");
    }
    return *std::max_element(data.begin(), data.end());
}

size_t Operations::count_operation(const NumberVector& data) {
    return data.size();
}

// Helper functions
std::function<double(double)> Operations::create_map_function(const Operation& op) {
    switch (op.type) {
        case OpType::ADD:
            return [operand = op.operand](double x) { return x + operand; };
        case OpType::SUB:
            return [operand = op.operand](double x) { return x - operand; };
        case OpType::MUL:
            return [operand = op.operand](double x) { return x * operand; };
        case OpType::DIV:
            return [operand = op.operand](double x) { 
                if (operand == 0.0) throw std::runtime_error("Division by zero");
                return x / operand; 
            };
        case OpType::IDENTITY:
        default:
            return [](double x) { return x; };
    }
}

std::function<bool(double)> Operations::create_filter_function(const Operation& op) {
    switch (op.type) {
        case OpType::GT:
            return [operand = op.operand](double x) { return x > operand; };
        case OpType::LT:
            return [operand = op.operand](double x) { return x < operand; };
        case OpType::GE:
            return [operand = op.operand](double x) { return x >= operand; };
        case OpType::LE:
            return [operand = op.operand](double x) { return x <= operand; };
        case OpType::EQ:
            return [operand = op.operand](double x) { return x == operand; };
        case OpType::NE:
            return [operand = op.operand](double x) { return x != operand; };
        default:
            return [](double x) { return true; };
    }
}

std::function<double(double, double)> Operations::create_reduce_function(const Operation& op) {
    switch (op.type) {
        case OpType::ADD:
            return [](double a, double b) { return a + b; };
        case OpType::SUB:
            return [](double a, double b) { return a - b; };
        case OpType::MUL:
            return [](double a, double b) { return a * b; };
        case OpType::DIV:
            return [](double a, double b) { 
                if (b == 0.0) throw std::runtime_error("Division by zero");
                return a / b; 
            };
        default:
            return [](double a, double b) { return a + b; }; // Default to addition
    }
}

} // namespace pyfunc