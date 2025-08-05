"""This is an integration test for the QuantityValue functionality"""

import json
from typing import List, Optional

from scipy.stats import linregress

from opensemantic import OswBaseModel
from opensemantic.characteristics.quantitative import (
    Area,
    AreaUnit,
    Diameter,
    DimensionlessUnit,
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

# Do we have to adapt VSCode settings to include the package index?
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


def test_quantityvalue_magic_methods():

    l1 = Length(value=10, unit=LengthUnit.meter)
    l2 = Length(value=3, unit=LengthUnit.meter)
    # __neg__
    neg = -l1
    assert isinstance(neg, Length)
    assert neg.value == -10
    # __pos__
    pos = +l1
    assert isinstance(pos, Length)
    assert pos.value == 10
    # __abs__
    absval = abs(Length(value=-5, unit=LengthUnit.meter))
    assert isinstance(absval, Length)
    assert absval.value == 5
    # __add__
    add = l1 + l2
    assert isinstance(add, Length)
    assert add.value == 13
    # __sub__
    sub = l1 - l2
    assert isinstance(sub, Length)
    assert sub.value == 7
    # __mul__
    mul = l1 * l2
    assert isinstance(mul, Area)
    # __truediv__
    truediv = l1 / l2
    assert isinstance(truediv, QuantityValue)
    assert truediv.unit == DimensionlessUnit.dimensionless
    # __floordiv__
    floordiv = l1 // l2
    assert isinstance(floordiv, QuantityValue)
    assert floordiv.value == 3.0
    # __mod__
    mod = l1 % l2
    assert isinstance(mod, QuantityValue)
    assert mod.value == 1.0
    # __pow__
    pow_result = l1**2
    assert isinstance(pow_result, Area)
    # __eq__
    eq = l1 == Length(value=10, unit=LengthUnit.meter)
    assert eq is True
    # __ne__
    ne = l1 != l2
    assert ne is True
    # __ge__
    ge = l1 >= l2
    assert ge is True
    # __gt__
    gt = l1 > l2
    assert gt is True
    # __le__
    le = l1 <= Length(value=10, unit=LengthUnit.meter)
    assert le is True
    # __lt__
    lt = l1 < Length(value=11, unit=LengthUnit.meter)
    assert lt is True


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

    a3 = Area(value=4.0, unit=AreaUnit.meter_squared)
    a4 = a3.to_unit(AreaUnit.centi_meter_squared)
    assert a4.unit == AreaUnit.centi_meter_squared
    assert a4.value == 100**2 * a3.value
    assert a3 == a4

    json_dict4 = a4.dict(exclude_none=True, exclude_defaults=True)
    print(json_dict4)
    assert json_dict4["value"] == 40000
    assert json_dict4["unit"] == (
        "Item:OSWd10e5841c68e5aad94b481b58ef9dfb9#OSWe36916dd7a34557b8a52c38d6dd7b832"
    )
    assert len(json_dict4.keys()) == 2


def test_pandas():

    class Measurement(OswBaseModel):
        length: Length
        width: Width
        area: Optional[Area] = None

    class MeasurementData(TabularData):
        rows: List[Measurement]

    measurement_data = MeasurementData(
        rows=[
            Measurement(length=Length(value=1.0), width=Width(value=2.0)),
            Measurement(length=Length(value=3.0), width=Width(value=4.0)),
        ]
    )
    df = measurement_data.to_df()
    print(df)
    df["area"] = df["length"] * df["width"]
    print(df)
    measurement_data2 = MeasurementData.from_df(df)
    print(measurement_data2)
    measurement_data3 = TabularData.from_df(df)
    print(measurement_data3.json(exclude_none=True, exclude_defaults=True, indent=2))
    # print(measurement_data3.__class__.schema_json(indent=2))


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


def test_init():
    # Overload 1: __init__(self, value: float, unit: Optional[UnitEnum])
    l1 = Length(value=5.0, unit=LengthUnit.meter)
    assert isinstance(l1, Length)
    assert l1.value == 5.0
    assert l1.unit == LengthUnit.meter

    # Overload 2: __init__(self, v: float, u: Optional[UnitEnum])
    l2 = Length(v=10.0, u=LengthUnit.milli_meter)
    assert isinstance(l2, Length)
    assert l2.value == 10.0
    assert l2.unit == LengthUnit.milli_meter

    # Overload 3: __init__(self, quantity_value: "QuantityValue")
    d3 = Diameter(quantity_value=l1)
    assert isinstance(d3, Diameter)
    assert d3.value == l1.value
    assert d3.unit == l1.unit

    # Overload 4: __init__(self, pint_quantity: pint.Quantity,
    #                      quantity_type: Type[QuantityValue])
    import pint

    ureg = pint.get_application_registry()
    pq = 2.5 * ureg.meter
    l4 = Length(pint_quantity=pq, quantity_type=Length)
    assert isinstance(l4, Length)
    assert l4.value == 2.5
    assert l4.unit == LengthUnit.meter

    # Overload 5: __init__(self, **data: Any)
    l5 = Length(**{"value": 7.0, "unit": LengthUnit.meter})
    assert isinstance(l5, Length)
    assert l5.value == 7.0
    assert l5.unit == LengthUnit.meter


def test_to_unit():
    # Test conversion from meters to millimeters
    length = Length(value=1.0, unit=LengthUnit.meter)
    l_mm = length.to_unit(LengthUnit.milli_meter)
    assert isinstance(l_mm, Length)
    assert l_mm.unit == LengthUnit.milli_meter
    assert l_mm.value == 1000.0

    # Test conversion using string
    l_cm = length.to_unit("centi_meter")
    assert isinstance(l_cm, Length)
    assert l_cm.unit.name == "centi_meter"
    assert l_cm.value == 100.0


if __name__ == "__main__":
    test_pint()
    test_export()
    test_pandas()
    test_tensile_test()
    test_quantityvalue_magic_methods()
    test_init()
