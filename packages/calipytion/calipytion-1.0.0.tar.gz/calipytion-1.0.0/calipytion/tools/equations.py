from calipytion.model import CalibrationModel

lower_bound = -1
upper_bound = 1e6


linear_model = CalibrationModel(
    name="linear",
    signal_law="a * concentration",
)
linear_model.add_to_parameters(
    symbol="a", init_value=1, lower_bound=lower_bound, upper_bound=upper_bound
)

quadratic_model = CalibrationModel(
    name="quadratic",
    signal_law="a * concentration + b * concentration**2 + c",
)
quadratic_model.add_to_parameters(
    symbol="a", init_value=1, lower_bound=lower_bound, upper_bound=upper_bound
)
quadratic_model.add_to_parameters(
    symbol="b", init_value=1, lower_bound=lower_bound, upper_bound=upper_bound
)
quadratic_model.add_to_parameters(
    symbol="c", init_value=1, lower_bound=lower_bound, upper_bound=upper_bound
)

cubic_model = CalibrationModel(
    name="cubic",
    signal_law="a * concentration + b * concentration**2 + c * concentration**3",
)
cubic_model.add_to_parameters(
    symbol="a", init_value=1, lower_bound=lower_bound, upper_bound=upper_bound
)
cubic_model.add_to_parameters(
    symbol="b", init_value=1, lower_bound=lower_bound, upper_bound=upper_bound
)
cubic_model.add_to_parameters(
    symbol="c", init_value=1, lower_bound=lower_bound, upper_bound=upper_bound
)
