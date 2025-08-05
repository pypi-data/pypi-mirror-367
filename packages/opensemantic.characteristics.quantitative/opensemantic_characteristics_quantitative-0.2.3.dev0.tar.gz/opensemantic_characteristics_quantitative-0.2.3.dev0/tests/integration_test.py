import json
from typing import List, Optional

from scipy.stats import linregress

from opensemantic import OswBaseModel
from opensemantic.characteristics.quantitative import (
    Area,
    AreaUnit,
    Force,
    ForcePerAreaUnit,
    ForceUnit,
    Length,
    LengthUnit,
    LinearStrain,
    ModulusOfElasticity,
    QuantityValue,
    Stress,
    TabularData,
    Thickness,
    Width,
)

# to we have to adapt VSCode settings to include the package index?
# "python.analysis.packageIndexDepths": [
#       {"name": "opensemantic.characteristics.quantitative",
#       "depth": 4, "includeAllSymbols": true}
# ]


def test_pint():

    q = Length(value=1.0, unit=LengthUnit.milli_meter)
    # transform to pint
    q_pint = q.to_pint()
    # transform back to QuantityValue
    q_ = QuantityValue.from_pint(q_pint)
    assert q == q_

    q2 = Length(value=1.0, unit=LengthUnit.meter)
    q3 = q + q2
    assert q3 == Length(value=1.001, unit=LengthUnit.meter)

    q31 = q * q2
    assert q31 == Area(value=1000.0, unit=AreaUnit.milli_meter_squared)

    q41 = Area(value=1.0, unit=AreaUnit.meter_squared)
    q42 = Area(value=1.0, unit=AreaUnit.milli_meter_squared)
    # 'square_meter' is not a valid unit for pint, but 'square_meter' is
    q43 = q41 + q42
    assert q43 == Area(value=1.000001, unit=AreaUnit.meter_squared)


def test_export():

    q = Length(value=1.0, unit=LengthUnit.milli_meter)

    q_json = json.loads(q.json(exclude_none=True))
    print(q_json)
    assert q_json == {
        "type": ["Category:OSWee9c7e5c343e542cb5a8b4648315902f"],
        "value": 1.0,
        "unit": str(
            "Item:OSWf101d25e944856e3bd4b4c9863db7de2"
            "#OSW322dec469be75aedb008b3ebff29db86"
        ),
    }

    q = Length(value=1.0, unit=LengthUnit.meter)

    q_json = json.loads(q.json(exclude_none=True))
    print(q_json)
    assert q_json == {
        "type": ["Category:OSWee9c7e5c343e542cb5a8b4648315902f"],
        "value": 1.0,
        "unit": "Item:OSWf101d25e944856e3bd4b4c9863db7de2",
    }

    q_json = json.loads(q.json(exclude_none=True, exclude_defaults=True))
    print(q_json)
    assert q_json == {"value": 1.0}

    ln = Length(value=0.1)
    w = Width(value=200, unit=LengthUnit.milli_meter)
    a = ln * w
    print(a)

    json_dict = a.dict()
    print(json_dict)
    assert json_dict["type"] == ["Category:OSW1fcf1694712e5684885071efdf775bd9"]
    assert json_dict["value"] == 20000.0
    assert json_dict["unit"] == (
        "Item:OSWd10e5841c68e5aad94b481b58ef9dfb9"
        "#OSWeca22bf4270853038ef3395bd6dd797b"
    )

    # _a = QuantityValue(**json_dict)

    _a = a.to_base()
    json_dict = _a.dict(exclude_none=True, exclude_defaults=True)
    print(json_dict)
    assert json_dict["value"] == 0.02
    assert len(json_dict.keys()) == 1

    __a = Area(**json_dict)
    assert __a == _a

    # not supported yet
    # jsonld_dict = a.to_jsonld()
    # print(json.dumps(jsonld_dict, indent=2))

    # a2 = QuantityValue.from_jsonld(jsonld_dict)
    # print(a2)


def test_pandas():

    class Measurement(OswBaseModel):
        length: Length
        width: Width
        area: Optional[Area] = None

    class MeasurementData(TabularData):
        rows: List[Measurement]

    measurement = MeasurementData(
        rows=[
            Measurement(length=Length(value=1.0), width=Width(value=2.0)),
            Measurement(length=Length(value=3.0), width=Width(value=4.0)),
        ]
    )
    df = measurement.to_df()
    print(df)
    df["area"] = df["length"] * df["width"]
    print(df)
    measurement2 = MeasurementData.from_df(df)
    print(measurement2)
    measurement3 = TabularData.from_df(df)
    print(measurement3.json(exclude_none=True, exclude_defaults=True, indent=2))
    # print(measurement3.__class__.schema_json(indent=2))


def test_tensile_test():

    class TensileTestSpecimen(OswBaseModel):
        length: Length
        width: Width
        thickness: Length
        cross_section_area: Optional[Area] = None
        e_mod: Optional[ModulusOfElasticity] = None

    class TensileTestResultRow(OswBaseModel):
        elongation: Length
        force: Force
        strain: Optional[LinearStrain] = None
        stress: Optional[Stress] = None

    class TensileTestResult(TabularData):
        rows: List[TensileTestResultRow]
        linear_region: Optional[LinearStrain] = LinearStrain(value=0.002)

    class TensileTestDataset(OswBaseModel):
        specimen: TensileTestSpecimen
        result: TensileTestResult

    def tensile_test_analysis(dataset: TensileTestDataset):
        # Calculate cross section area if not provided
        if dataset.specimen.cross_section_area is None:
            dataset.specimen.cross_section_area = (
                dataset.specimen.width * dataset.specimen.thickness
            )

        # Calculate stress and strain - slow iteration
        # for row in dataset.result.rows:
        #     #row.stress = Stress(value=row.force.value / dataset.specimen.cross_section_area.value, unit=row.force.unit)   # noqa: E501
        #     #row.strain = LinearStrain(value=row.force.value / (dataset.specimen.e_mod.value * dataset.specimen.cross_section_area.value), unit=row.force.unit)   # noqa: E501
        #     row.stress = row.force / dataset.specimen.cross_section_area   # noqa: E501

        # Calculate stress and strain - fast as pandas DataFrame operation
        df = dataset.result.to_df()
        df["strain"] = df["elongation"] / dataset.specimen.length.to_pint()
        df["stress"] = df["force"] / dataset.specimen.cross_section_area.to_pint()

        # make a linear fit on the linear region of the stress-strain curve
        # to find the modulus of elasticity
        linear_region = df[df["strain"] <= dataset.result.linear_region.to_pint()]

        slope, intercept, r_value, p_value, std_err = linregress(
            linear_region["strain"].pint.to_base_units().pint.magnitude,
            linear_region["stress"].pint.to_base_units().pint.magnitude,
        )

        slope = (
            slope
            * linear_region["stress"].pint.to_base_units().pint.units
            / linear_region["strain"].pint.to_base_units().pint.units
        )  # noqa: E501
        dataset.specimen.e_mod = ModulusOfElasticity.from_pint(slope.to("Pa"))

        dataset.result = TensileTestResult.from_df(df)

        return dataset

    # Example usage
    specimen = TensileTestSpecimen(
        length=Length(value=100, unit=LengthUnit.milli_meter),
        width=Width(value=10, unit=LengthUnit.milli_meter),
        thickness=Thickness(value=10, unit=LengthUnit.milli_meter),
    )
    result = TensileTestResult(
        rows=[
            TensileTestResultRow(
                force=Force(value=1.0000, unit=ForceUnit.kilo_newton),
                elongation=Length(value=0.10, unit=LengthUnit.milli_meter),
            ),  # noqa: E501
            TensileTestResultRow(
                force=Force(value=1.5050, unit=ForceUnit.kilo_newton),
                elongation=Length(value=0.15, unit=LengthUnit.milli_meter),
            ),  # noqa: E501
            TensileTestResultRow(
                force=Force(value=2.0000, unit=ForceUnit.kilo_newton),
                elongation=Length(value=0.20, unit=LengthUnit.milli_meter),
            ),  # noqa: E501
        ]
    )
    dataset = TensileTestDataset(specimen=specimen, result=result)
    analyzed_dataset = tensile_test_analysis(dataset)
    # print(analyzed_dataset.json(exclude_none=True, indent=2))
    assert analyzed_dataset.specimen.e_mod == ModulusOfElasticity(
        value=10.0, unit=ForcePerAreaUnit.giga_pascal
    )


if __name__ == "__main__":
    test_pint()
    test_export()
    test_pandas()
    test_tensile_test()
