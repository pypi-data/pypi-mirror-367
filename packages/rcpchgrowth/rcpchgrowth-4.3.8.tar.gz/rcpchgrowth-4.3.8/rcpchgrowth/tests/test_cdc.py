# standard imports
from datetime import datetime
import json
import os
# from pprint import pprint

# third-party imports
import pytest

# rcpch imports
from rcpchgrowth import Measurement

# the ACCURACY constant defines the accuracy of the test comparisons
# owing to variations in statistical calculations it's impossible to get exact
# agreement between R and Python, so our statistician feels we can set a tolerance
# within which we will accept a result as correct.

ACCURACY = 1e-3


def load_valid_data_set():
    """
    Loads in the testing data from JSON file
    """
    with open(os.path.abspath(os.path.dirname(__file__)) + "/cdc/bmi_height_weight_validation.json") as f:
        return json.load(f)


@pytest.mark.parametrize("line", load_valid_data_set())
def test_measurement_class_cdc_data(line):
    """
    Test which iterates through a JSON file of 4000 fictional children and known calculated (TC via R)
      correct SDS values. Compares the output of the Measurement.measurement method with the known
      correct value.
    """

    measurement_object = Measurement(
        sex=str(line["sex"]),
        birth_date=datetime.strptime(line["birth_date"], "%Y-%m-%d"),
        observation_date=datetime.strptime(
            line["observation_date"], "%Y-%m-%d"),
        measurement_method=str(line["measurement_method"]),
        observation_value=float(line["observation_value"]),
        gestation_weeks=40,
        gestation_days=0,
        reference="cdc"
    )

    # pprint(vars(measurement_object))
    # pprint(line)

    # all comparisons using absolute tolerance (not relative)

    # this conditional guards against failure of pytest.approx with NoneTypes
    # if line["corrected_sds"] is None:
    #     assert measurement_object.measurement[
    #         "measurement_calculated_values"]['corrected_sds'] is None
    # else:
    #     assert measurement_object.measurement[
    #         "measurement_calculated_values"]['corrected_sds'] == pytest.approx(
    #         line["corrected_sds"], abs=ACCURACY)

    # this conditional guards against failure of pytest.approx with NoneTypes
    if line["z_score"] is None:
        assert measurement_object.measurement[
            "measurement_calculated_values"]['chronological_sds'] is None
    else:
        assert measurement_object.measurement[
            "measurement_calculated_values"]['chronological_sds'] == pytest.approx(
            line["z_score"], abs=ACCURACY)
