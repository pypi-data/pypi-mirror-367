<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/<USER>/opensemantic.characteristics.quantitative.svg?branch=main)](https://cirrus-ci.com/github/<USER>/opensemantic.characteristics.quantitative)
[![ReadTheDocs](https://readthedocs.org/projects/opensemantic.characteristics.quantitative/badge/?version=latest)](https://opensemantic.characteristics.quantitative.readthedocs.io/en/stable/)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/opensemantic.characteristics.quantitative.svg)](https://anaconda.org/conda-forge/opensemantic.characteristics.quantitative)
[![Monthly Downloads](https://pepy.tech/badge/opensemantic.characteristics.quantitative/month)](https://pepy.tech/project/opensemantic.characteristics.quantitative)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/opensemantic.characteristics.quantitative)
-->

[![PyPI-Server](https://img.shields.io/pypi/v/opensemantic.characteristics.quantitative.svg)](https://pypi.org/project/opensemantic.characteristics.quantitative/)
[![Coveralls](https://img.shields.io/coveralls/github/OpenSemanticWorld-Packages/opensemantic.characteristics.quantitative/main.svg)](https://coveralls.io/r/OpenSemanticWorld-Packages/opensemantic.characteristics.quantitative)
[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)

# opensemantic.characteristics.quantitative

> Library with Python models derived from the page package world.opensemantic.characteristics.quantitative

Quantities and units generated from [QUDT](https://www.qudt.org). [pint](https://pypi.org/project/ucumvert/) mapping was done with support from [ucumvert](https://pypi.org/project/ucumvert/)

## Status

<details>
<summary>pint roundtrip test: 359 successful, 105 errors and 485 warnings (444 critical)</summary>

```
Error: Missing unit MobilityUnit.centi_meter_squared_per_second_per_volt in unit_registry
Critical Warning: MolarFluxDensity and PhotosyntheticPhotonFluxDensity have the same unit MolarFluxDensityUnit.mole_per_meter_squared_per_second
Critical Warning: MolarFluxDensity and PhotosyntheticPhotonFluxDensity have the same unit MolarFluxDensityUnit.milli_mole_per_meter_squared_per_second
Critical Warning: MolarFluxDensity and PhotosyntheticPhotonFluxDensity have the same unit MolarFluxDensityUnit.micro_mole_per_meter_squared_per_second
Error: Missing unit ElectricCurrentPerTemperatureUnit.ampere_per_Celsius in pint
Critical Warning: Inductance and Permeance have the same unit InductanceUnit.henry
Critical Warning: Inductance and Acidity have the same unit InductanceUnit.pico_henry
Critical Warning: Inductance and Permeance have the same unit InductanceUnit.micro_henry
Critical Warning: Inductance and Permeance have the same unit InductanceUnit.milli_henry
Critical Warning: Inductance and Permeance have the same unit InductanceUnit.nano_henry
Critical Warning: VaporPermeability and WaterVapourDiffusionCoefficient have the same unit VaporPermeabilityUnit.kilo_gram_per_meter_per_pascal_per_second
Critical Warning: DiffusionCoefficient and ThermalDiffusionCoefficient have the same unit DiffusionCoefficientUnit.meter_squared_per_second
Critical Warning: DiffusionCoefficient and ThermalDiffusionCoefficient have the same unit DiffusionCoefficientUnit.milli_meter_squared_per_second
Critical Warning: DiffusionCoefficient and ThermalDiffusionCoefficient have the same unit DiffusionCoefficientUnit.centi_meter_squared_per_second
Critical Warning: SurfaceCoefficientOfHeatTransfer and CoefficientOfHeatTransfer have the same unit SurfaceCoefficientOfHeatTransferUnit.watt_per_kelvin_per_meter_squared
Error: Missing unit ExposureRateUnit.coulomb_per_kilo_gram_per_second in unit_registry
Critical Warning: Conductivity and ElectrolyticConductivity have the same unit ConductivityUnit.siemens_per_meter
Critical Warning: Conductivity and ElectrolyticConductivity have the same unit ConductivityUnit.pico_siemens_per_meter
Critical Warning: Conductivity and ElectrolyticConductivity have the same unit ConductivityUnit.milli_siemens_per_meter
Critical Warning: Conductivity and ElectrolyticConductivity have the same unit ConductivityUnit.nano_siemens_per_meter
Critical Warning: Conductivity and ElectrolyticConductivity have the same unit ConductivityUnit.mega_siemens_per_meter
Critical Warning: Conductivity and ElectrolyticConductivity have the same unit ConductivityUnit.micro_siemens_per_meter
Critical Warning: Conductivity and ElectrolyticConductivity have the same unit ConductivityUnit.siemens_per_centi_meter
Critical Warning: Conductivity and ElectrolyticConductivity have the same unit ConductivityUnit.kilo_siemens_per_meter
Critical Warning: Conductivity and ElectrolyticConductivity have the same unit ConductivityUnit.deci_siemens_per_meter
Critical Warning: MassPerLength and LinearDensity have the same unit MassPerLengthUnit.kilo_gram_per_meter
Critical Warning: RotationalMass and MomentOfInertia have the same unit RotationalMassUnit.kilo_gram_meter_squared
Critical Warning: Basicity and Acidity have the same unit BasicityUnit.pico_henry
Critical Warning: Energy and LevelWidth have the same unit EnergyUnit.joule
Critical Warning: Energy and LevelWidth have the same unit EnergyUnit.peta_joule
Critical Warning: Energy and LevelWidth have the same unit EnergyUnit.kilo_joule
Critical Warning: Energy and LevelWidth have the same unit EnergyUnit.milli_joule
Critical Warning: Energy and LevelWidth have the same unit EnergyUnit.femto_joule
Critical Warning: Energy and LevelWidth have the same unit EnergyUnit.tera_joule
Critical Warning: Energy and LevelWidth have the same unit EnergyUnit.exa_joule
Critical Warning: Energy and LevelWidth have the same unit EnergyUnit.giga_joule
Critical Warning: Energy and LevelWidth have the same unit EnergyUnit.mega_joule
Critical Warning: Energy and LevelWidth have the same unit EnergyUnit.atto_joule
Critical Warning: ResidualResistivity and Resistivity have the same unit ResidualResistivityUnit.meter_ohm
Critical Warning: LinearEnergyTransfer and TotalLinearStoppingPower have the same unit LinearEnergyTransferUnit.joule_per_meter
Error: Missing unit SectionAreaIntegralUnit.field_5 in pint
Error: Missing unit NEONUnit.Celsius_squared in pint
Critical Warning: ElectricChargeLinearDensity and ElectricChargeLineDensity have the same unit ElectricChargeLinearDensityUnit.coulomb_per_meter
Critical Warning: ElectricPolarizability and ChemicalAffinity have the same unit ElectricPolarizabilityUnit.joule_per_mole
Critical Warning: ElectricPolarizability and ChemicalAffinity have the same unit ElectricPolarizabilityUnit.kilo_joule_per_mole
Error: Missing unit NonActivePowerUnit.volt_ampere in unit_registry
Error: Missing unit NonActivePowerUnit.mega_volt_ampere in unit_registry
Error: Missing unit NonActivePowerUnit.kilo_volt_ampere in unit_registry
Critical Warning: SlowingDownDensity and ParticleSourceDensity have the same unit SlowingDownDensityUnit.per_meter_cubed_per_second
Critical Warning: ParticleFluenceRate and Flux have the same unit ParticleFluenceRateUnit.per_meter_squared_per_second
Critical Warning: PhaseCoefficient and LinearAbsorptionCoefficient have the same unit PhaseCoefficientUnit.per_meter
Critical Warning: PhaseCoefficient and LinearAbsorptionCoefficient have the same unit PhaseCoefficientUnit.per_milli_meter
Critical Warning: PhaseCoefficient and LinearAbsorptionCoefficient have the same unit PhaseCoefficientUnit.per_nano_meter
Critical Warning: PhaseCoefficient and LinearAbsorptionCoefficient have the same unit PhaseCoefficientUnit.per_centi_meter
Critical Warning: PhaseCoefficient and LinearAbsorptionCoefficient have the same unit PhaseCoefficientUnit.per_kilo_meter
Critical Warning: PhaseCoefficient and LinearAbsorptionCoefficient have the same unit PhaseCoefficientUnit.per_micro_meter
Critical Warning: PhaseCoefficient and LinearAbsorptionCoefficient have the same unit PhaseCoefficientUnit.per_pico_meter
Critical Warning: NuclearQuadrupoleMoment and Area have the same unit NuclearQuadrupoleMomentUnit.meter_squared
Critical Warning: NuclearQuadrupoleMoment and Area have the same unit NuclearQuadrupoleMomentUnit.centi_meter_squared
Critical Warning: NuclearQuadrupoleMoment and Area have the same unit NuclearQuadrupoleMomentUnit.milli_meter_squared
Critical Warning: NuclearQuadrupoleMoment and Area have the same unit NuclearQuadrupoleMomentUnit.micro_meter_squared
Critical Warning: NuclearQuadrupoleMoment and Area have the same unit NuclearQuadrupoleMomentUnit.nano_meter_squared
Critical Warning: NuclearQuadrupoleMoment and Area have the same unit NuclearQuadrupoleMomentUnit.deci_meter_squared
Error: Missing unit SecondPolarMomentOfAreaUnit.field_4 in pint
Error: Missing unit SecondPolarMomentOfAreaUnit.field_4_1 in pint
Error: Missing unit SecondPolarMomentOfAreaUnit.field_4_2 in pint
Critical Warning: SpecificImpulseByWeight and Period have the same unit SpecificImpulseByWeightUnit.second
Critical Warning: SpecificImpulseByWeight and Period have the same unit SpecificImpulseByWeightUnit.deci_second
Critical Warning: SpecificImpulseByWeight and Period have the same unit SpecificImpulseByWeightUnit.micro_second
Critical Warning: SpecificImpulseByWeight and Period have the same unit SpecificImpulseByWeightUnit.atto_second
Critical Warning: SpecificImpulseByWeight and Period have the same unit SpecificImpulseByWeightUnit.pico_second
Critical Warning: SpecificImpulseByWeight and Period have the same unit SpecificImpulseByWeightUnit.milli_second
Critical Warning: SpecificImpulseByWeight and Period have the same unit SpecificImpulseByWeightUnit.femto_second
Critical Warning: SpecificImpulseByWeight and Period have the same unit SpecificImpulseByWeightUnit.nano_second
Critical Warning: SpecificImpulseByWeight and Period have the same unit SpecificImpulseByWeightUnit.kilo_second
Critical Warning: EnergyPerElectricCharge and ElectricPotentialDifference have the same unit EnergyPerElectricChargeUnit.volt
Critical Warning: EnergyPerElectricCharge and ElectricPotentialDifference have the same unit EnergyPerElectricChargeUnit.milli_volt
Critical Warning: EnergyPerElectricCharge and ElectricPotentialDifference have the same unit EnergyPerElectricChargeUnit.micro_volt
Critical Warning: EnergyPerElectricCharge and ElectricPotentialDifference have the same unit EnergyPerElectricChargeUnit.kilo_volt
Critical Warning: EnergyPerElectricCharge and ElectricPotentialDifference have the same unit EnergyPerElectricChargeUnit.mega_volt
Critical Warning: EnergyPerTemperature and Entropy have the same unit EnergyPerTemperatureUnit.joule_per_kelvin
Critical Warning: EnergyPerTemperature and Entropy have the same unit EnergyPerTemperatureUnit.kilo_joule_per_kelvin
Critical Warning: EnergyPerTemperature and Entropy have the same unit EnergyPerTemperatureUnit.mega_joule_per_kelvin
Critical Warning: Time and Period have the same unit TimeUnit.second
Critical Warning: Time and Period have the same unit TimeUnit.deci_second
Critical Warning: Time and Period have the same unit TimeUnit.micro_second
Critical Warning: Time and Period have the same unit TimeUnit.atto_second
Critical Warning: Time and Period have the same unit TimeUnit.pico_second
Critical Warning: Time and Period have the same unit TimeUnit.milli_second
Critical Warning: Time and Period have the same unit TimeUnit.femto_second
Critical Warning: Time and Period have the same unit TimeUnit.nano_second
Critical Warning: Time and Period have the same unit TimeUnit.kilo_second
Critical Warning: ThomsonCoefficient and SeebeckCoefficient have the same unit ThomsonCoefficientUnit.volt_per_kelvin
Error: Missing unit SpectralRadiantEnergyDensityUnit.field_4 in pint
Critical Warning: AngularReciprocalLatticeVector and LinearAbsorptionCoefficient have the same unit AngularReciprocalLatticeVectorUnit.per_meter
Critical Warning: AngularReciprocalLatticeVector and LinearAbsorptionCoefficient have the same unit AngularReciprocalLatticeVectorUnit.per_milli_meter
Critical Warning: AngularReciprocalLatticeVector and LinearAbsorptionCoefficient have the same unit AngularReciprocalLatticeVectorUnit.per_nano_meter
Critical Warning: AngularReciprocalLatticeVector and LinearAbsorptionCoefficient have the same unit AngularReciprocalLatticeVectorUnit.per_centi_meter
Critical Warning: AngularReciprocalLatticeVector and LinearAbsorptionCoefficient have the same unit AngularReciprocalLatticeVectorUnit.per_kilo_meter
Critical Warning: AngularReciprocalLatticeVector and LinearAbsorptionCoefficient have the same unit AngularReciprocalLatticeVectorUnit.per_micro_meter
Critical Warning: AngularReciprocalLatticeVector and LinearAbsorptionCoefficient have the same unit AngularReciprocalLatticeVectorUnit.per_pico_meter
Critical Warning: VolumicElectromagneticEnergy and ElectromagneticEnergyDensity have the same unit VolumicElectromagneticEnergyUnit.joule_per_meter_cubed
Critical Warning: VolumicElectromagneticEnergy and ElectromagneticEnergyDensity have the same unit VolumicElectromagneticEnergyUnit.mega_joule_per_meter_cubed
Critical Warning: Permeance and Acidity have the same unit PermeanceUnit.pico_henry
Critical Warning: Density and MassDensity have the same unit DensityUnit.gram_per_liter
Critical Warning: Density and MassDensity have the same unit DensityUnit.milli_gram_per_liter
Critical Warning: Density and MassDensity have the same unit DensityUnit.micro_gram_per_liter
Critical Warning: Density and MassDensity have the same unit DensityUnit.gram_per_milli_liter
Critical Warning: Density and MassDensity have the same unit DensityUnit.kilo_gram_per_liter
Critical Warning: Density and MassDensity have the same unit DensityUnit.pico_gram_per_liter
Critical Warning: Density and MassDensity have the same unit DensityUnit.milli_gram_per_milli_liter
Critical Warning: Density and MassDensity have the same unit DensityUnit.gram_per_deci_liter
Critical Warning: Density and MassDensity have the same unit DensityUnit.femto_gram_per_liter
Critical Warning: Density and MassDensity have the same unit DensityUnit.nano_gram_per_liter
Error: Missing unit SpecificVolumeUnit.meter_cubed_per_kilo_gram in unit_registry
Error: Missing unit SpecificVolumeUnit.milli_meter_cubed_per_kilo_gram in unit_registry
Critical Warning: MagneticTension and MagnetomotiveForce have the same unit MagneticTensionUnit.ampere
Critical Warning: MagneticTension and MagnetomotiveForce have the same unit MagneticTensionUnit.pico_ampere
Critical Warning: MagneticTension and MagnetomotiveForce have the same unit MagneticTensionUnit.mega_ampere
Critical Warning: MagneticTension and MagnetomotiveForce have the same unit MagneticTensionUnit.kilo_ampere
Critical Warning: MagneticTension and MagnetomotiveForce have the same unit MagneticTensionUnit.micro_ampere
Critical Warning: MagneticTension and MagnetomotiveForce have the same unit MagneticTensionUnit.milli_ampere
Error: Missing unit MassicActivityUnit.becquerel_per_kilo_gram in unit_registry
Error: Missing unit MassicActivityUnit.milli_becquerel_per_kilo_gram in unit_registry
Error: Missing unit MassicActivityUnit.micro_becquerel_per_kilo_gram in unit_registry
Error: Missing unit SpecificOpticalRotatoryPowerUnit.meter_squared_radian_per_kilo_gram in unit_registry
Critical Warning: SurfaceDensity and BodyMassIndex have the same unit SurfaceDensityUnit.kilo_gram_per_meter_squared
Critical Warning: Volume1 and SectionModulus have the same unit VolumeUnit.meter_cubed
Critical Warning: Volume1 and SectionModulus have the same unit VolumeUnit.milli_meter_cubed
Critical Warning: Volume1 and SectionModulus have the same unit VolumeUnit.deca_meter_cubed
Critical Warning: Volume1 and SectionModulus have the same unit VolumeUnit.micro_meter_cubed
Critical Warning: Volume1 and SectionModulus have the same unit VolumeUnit.centi_meter_cubed
Critical Warning: Volume1 and SectionModulus have the same unit VolumeUnit.deci_meter_cubed
Critical Warning: VolumePerUnitArea and Length have the same unit VolumePerUnitAreaUnit.meter
Critical Warning: PhotonIntensity and TemporalSummationFunction have the same unit PhotonIntensityUnit.per_second_per_steradian
Critical Warning: KermaRate and AbsorbedDoseRate have the same unit KermaRateUnit.gray_per_second
Critical Warning: AttenuationCoefficient and LinearAbsorptionCoefficient have the same unit AttenuationCoefficientUnit.per_meter
Critical Warning: AttenuationCoefficient and LinearAbsorptionCoefficient have the same unit AttenuationCoefficientUnit.per_milli_meter
Critical Warning: AttenuationCoefficient and LinearAbsorptionCoefficient have the same unit AttenuationCoefficientUnit.per_nano_meter
Critical Warning: AttenuationCoefficient and LinearAbsorptionCoefficient have the same unit AttenuationCoefficientUnit.per_centi_meter
Critical Warning: AttenuationCoefficient and LinearAbsorptionCoefficient have the same unit AttenuationCoefficientUnit.per_kilo_meter
Critical Warning: AttenuationCoefficient and LinearAbsorptionCoefficient have the same unit AttenuationCoefficientUnit.per_micro_meter
Critical Warning: AttenuationCoefficient and LinearAbsorptionCoefficient have the same unit AttenuationCoefficientUnit.per_pico_meter
Critical Warning: LinearVelocity and Speed have the same unit LinearVelocityUnit.meter_per_second
Critical Warning: LinearVelocity and Speed have the same unit LinearVelocityUnit.centi_meter_per_second
Critical Warning: LinearVelocity and Speed have the same unit LinearVelocityUnit.micro_meter_per_second
Critical Warning: LinearVelocity and Speed have the same unit LinearVelocityUnit.milli_meter_per_second
Critical Warning: LinearVelocity and Speed have the same unit LinearVelocityUnit.kilo_meter_per_second
Critical Warning: Momentum and LinearMomentum have the same unit MomentumUnit.newton_second
Error: Missing unit TemperaturePerTimeUnit.Celsius_per_second in pint
Critical Warning: ModulusOfElasticity and ShearModulus have the same unit ModulusOfElasticityUnit.pascal
Critical Warning: ModulusOfElasticity and ShearModulus have the same unit ModulusOfElasticityUnit.giga_pascal
Critical Warning: ModulusOfElasticity and ShearModulus have the same unit ModulusOfElasticityUnit.deca_pascal
Critical Warning: ModulusOfElasticity and ShearModulus have the same unit ModulusOfElasticityUnit.milli_pascal
Critical Warning: ModulusOfElasticity and ShearModulus have the same unit ModulusOfElasticityUnit.mega_pascal
Critical Warning: ModulusOfElasticity and ShearModulus have the same unit ModulusOfElasticityUnit.kilo_pascal
Critical Warning: ModulusOfElasticity and ShearModulus have the same unit ModulusOfElasticityUnit.hecto_pascal
Critical Warning: ModulusOfElasticity and ShearModulus have the same unit ModulusOfElasticityUnit.micro_pascal
Critical Warning: HydraulicPermeability and Area have the same unit HydraulicPermeabilityUnit.meter_squared
Critical Warning: HydraulicPermeability and Area have the same unit HydraulicPermeabilityUnit.centi_meter_squared
Critical Warning: HydraulicPermeability and Area have the same unit HydraulicPermeabilityUnit.milli_meter_squared
Critical Warning: HydraulicPermeability and Area have the same unit HydraulicPermeabilityUnit.micro_meter_squared
Critical Warning: HydraulicPermeability and Area have the same unit HydraulicPermeabilityUnit.nano_meter_squared
Critical Warning: HydraulicPermeability and Area have the same unit HydraulicPermeabilityUnit.deci_meter_squared
Critical Warning: ElectricPotential and ElectricPotentialDifference have the same unit ElectricPotentialUnit.volt
Critical Warning: ElectricPotential and ElectricPotentialDifference have the same unit ElectricPotentialUnit.milli_volt
Critical Warning: ElectricPotential and ElectricPotentialDifference have the same unit ElectricPotentialUnit.micro_volt
Critical Warning: ElectricPotential and ElectricPotentialDifference have the same unit ElectricPotentialUnit.kilo_volt
Critical Warning: ElectricPotential and ElectricPotentialDifference have the same unit ElectricPotentialUnit.mega_volt
Critical Warning: ModulusOfSubgradeReaction and SpecificWeight have the same unit ModulusOfSubgradeReactionUnit.newton_per_meter_cubed
Critical Warning: ModulusOfSubgradeReaction and SpecificWeight have the same unit ModulusOfSubgradeReactionUnit.kilo_newton_per_meter_cubed
Critical Warning: IsothermalCompressibility and StressOpticCoefficient have the same unit IsothermalCompressibilityUnit.per_pascal
Error: Missing unit TemperatureAmountOfSubstanceUnit.Celsius_mole in pint
Critical Warning: ElectricChargeDensity and ElectricChargeVolumeDensity have the same unit ElectricChargeDensityUnit.coulomb_per_meter_cubed
Critical Warning: ElectricChargeDensity and ElectricChargeVolumeDensity have the same unit ElectricChargeDensityUnit.giga_coulomb_per_meter_cubed
Critical Warning: ElectricChargeDensity and ElectricChargeVolumeDensity have the same unit ElectricChargeDensityUnit.mega_coulomb_per_meter_cubed
Critical Warning: ElectricChargeDensity and ElectricChargeVolumeDensity have the same unit ElectricChargeDensityUnit.micro_coulomb_per_meter_cubed
Critical Warning: ElectricChargeDensity and ElectricChargeVolumeDensity have the same unit ElectricChargeDensityUnit.coulomb_per_milli_meter_cubed
Critical Warning: ElectricChargeDensity and ElectricChargeVolumeDensity have the same unit ElectricChargeDensityUnit.coulomb_per_centi_meter_cubed
Critical Warning: ElectricChargeDensity and ElectricChargeVolumeDensity have the same unit ElectricChargeDensityUnit.kilo_coulomb_per_meter_cubed
Critical Warning: ElectricChargeDensity and ElectricChargeVolumeDensity have the same unit ElectricChargeDensityUnit.milli_coulomb_per_meter_cubed
Critical Warning: MeanMassRange and BodyMassIndex have the same unit MeanMassRangeUnit.kilo_gram_per_meter_squared
Critical Warning: LinearAcceleration and Acceleration have the same unit LinearAccelerationUnit.meter_per_second_squared
Error: Missing unit LinearAccelerationUnit.centi_meter_per_second_squared in unit_registry
Critical Warning: MolarAbsorptionCoefficient and MolarAttenuationCoefficient have the same unit MolarAbsorptionCoefficientUnit.meter_squared_per_mole
Warning: AreaUnit.centi_meter_squared was normalized to AreaUnit.milli_meter_squared
Warning: AreaUnit.deci_meter_squared was normalized to AreaUnit.milli_meter_squared
Critical Warning: ElectricCurrentPhasor and MagnetomotiveForce have the same unit ElectricCurrentPhasorUnit.ampere
Critical Warning: ElectricCurrentPhasor and MagnetomotiveForce have the same unit ElectricCurrentPhasorUnit.pico_ampere
Critical Warning: ElectricCurrentPhasor and MagnetomotiveForce have the same unit ElectricCurrentPhasorUnit.mega_ampere
Critical Warning: ElectricCurrentPhasor and MagnetomotiveForce have the same unit ElectricCurrentPhasorUnit.kilo_ampere
Critical Warning: ElectricCurrentPhasor and MagnetomotiveForce have the same unit ElectricCurrentPhasorUnit.micro_ampere
Critical Warning: ElectricCurrentPhasor and MagnetomotiveForce have the same unit ElectricCurrentPhasorUnit.milli_ampere
Warning: LinearThermalExpansionUnit.centi_meter_per_kelvin was normalized to LinearThermalExpansionUnit.milli_meter_per_kelvin
Error: Missing unit TotalMassStoppingPowerUnit.joule_meter_squared_per_kilo_gram in unit_registry
Warning: ElectricChargeVolumeDensityUnit.coulomb_per_milli_meter_cubed was normalized to ElectricChargeVolumeDensityUnit.giga_coulomb_per_meter_cubed
Warning: ElectricChargeVolumeDensityUnit.coulomb_per_centi_meter_cubed was normalized to ElectricChargeVolumeDensityUnit.mega_coulomb_per_meter_cubed
Critical Warning: CombinedNonEvaporativeHeatTransferCoefficient and CoefficientOfHeatTransfer have the same unit CombinedNonEvaporativeHeatTransferCoefficientUnit.watt_per_kelvin_per_meter_squared
Warning: InverseVolumeUnit.per_centi_meter_cubed was normalized to InverseVolumeUnit.per_meter_cubed
Warning: PressureCoefficientUnit.hecto_pascal_per_kelvin was normalized to PressureCoefficientUnit.pascal_per_kelvin
Critical Warning: Action and AngularImpulse have the same unit ActionUnit.joule_second
Critical Warning: Action and AngularImpulse have the same unit ActionUnit.atto_joule_second
Critical Warning: SoundPowerLevel and SoundReductionIndex have the same unit SoundPowerLevelUnit.byte
Critical Warning: Torque and MomentOfForce have the same unit TorqueUnit.meter_newton
Critical Warning: Torque and MomentOfForce have the same unit TorqueUnit.deci_newton_meter
Critical Warning: Torque and MomentOfForce have the same unit TorqueUnit.centi_newton_meter
Error: Missing unit TorqueUnit.meter_milli_newton in unit_registry
Critical Warning: Torque and MomentOfForce have the same unit TorqueUnit.kilo_newton_meter
Error: Missing unit TorqueUnit.meter_micro_newton in unit_registry
Critical Warning: Torque and MomentOfForce have the same unit TorqueUnit.mega_newton_meter
Error: Missing unit TorqueUnit.centi_meter_newton in unit_registry
Critical Warning: LagrangeFunction and LevelWidth have the same unit LagrangeFunctionUnit.joule
Critical Warning: LagrangeFunction and LevelWidth have the same unit LagrangeFunctionUnit.peta_joule
Critical Warning: LagrangeFunction and LevelWidth have the same unit LagrangeFunctionUnit.kilo_joule
Critical Warning: LagrangeFunction and LevelWidth have the same unit LagrangeFunctionUnit.milli_joule
Critical Warning: LagrangeFunction and LevelWidth have the same unit LagrangeFunctionUnit.femto_joule
Critical Warning: LagrangeFunction and LevelWidth have the same unit LagrangeFunctionUnit.tera_joule
Critical Warning: LagrangeFunction and LevelWidth have the same unit LagrangeFunctionUnit.exa_joule
Critical Warning: LagrangeFunction and LevelWidth have the same unit LagrangeFunctionUnit.giga_joule
Critical Warning: LagrangeFunction and LevelWidth have the same unit LagrangeFunctionUnit.mega_joule
Critical Warning: LagrangeFunction and LevelWidth have the same unit LagrangeFunctionUnit.atto_joule
Warning: SectionModulusUnit.deca_meter_cubed was normalized to SectionModulusUnit.meter_cubed
Warning: SectionModulusUnit.centi_meter_cubed was normalized to SectionModulusUnit.milli_meter_cubed
Warning: SectionModulusUnit.deci_meter_cubed was normalized to SectionModulusUnit.milli_meter_cubed
Critical Warning: Viscosity and DynamicViscosity have the same unit ViscosityUnit.pascal_second
Critical Warning: Viscosity and DynamicViscosity have the same unit ViscosityUnit.milli_pascal_second
Critical Warning: InversePressure and StressOpticCoefficient have the same unit InversePressureUnit.per_pascal
Critical Warning: BulkModulus and ShearModulus have the same unit BulkModulusUnit.pascal
Critical Warning: BulkModulus and ShearModulus have the same unit BulkModulusUnit.giga_pascal
Critical Warning: BulkModulus and ShearModulus have the same unit BulkModulusUnit.deca_pascal
Critical Warning: BulkModulus and ShearModulus have the same unit BulkModulusUnit.milli_pascal
Critical Warning: BulkModulus and ShearModulus have the same unit BulkModulusUnit.mega_pascal
Critical Warning: BulkModulus and ShearModulus have the same unit BulkModulusUnit.kilo_pascal
Critical Warning: BulkModulus and ShearModulus have the same unit BulkModulusUnit.hecto_pascal
Critical Warning: BulkModulus and ShearModulus have the same unit BulkModulusUnit.micro_pascal
Critical Warning: MolarEnergy and ChemicalAffinity have the same unit MolarEnergyUnit.joule_per_mole
Critical Warning: MolarEnergy and ChemicalAffinity have the same unit MolarEnergyUnit.kilo_joule_per_mole
Critical Warning: ElectromagneticWavePhaseSpeed and Speed have the same unit ElectromagneticWavePhaseSpeedUnit.meter_per_second
Critical Warning: ElectromagneticWavePhaseSpeed and Speed have the same unit ElectromagneticWavePhaseSpeedUnit.centi_meter_per_second
Critical Warning: ElectromagneticWavePhaseSpeed and Speed have the same unit ElectromagneticWavePhaseSpeedUnit.micro_meter_per_second
Critical Warning: ElectromagneticWavePhaseSpeed and Speed have the same unit ElectromagneticWavePhaseSpeedUnit.milli_meter_per_second
Critical Warning: ElectromagneticWavePhaseSpeed and Speed have the same unit ElectromagneticWavePhaseSpeedUnit.kilo_meter_per_second
Critical Warning: ModulusOfImpedance and Impedance have the same unit ModulusOfImpedanceUnit.ohm
Critical Warning: ModulusOfImpedance and Impedance have the same unit ModulusOfImpedanceUnit.kilo_ohm
Critical Warning: ModulusOfImpedance and Impedance have the same unit ModulusOfImpedanceUnit.milli_ohm
Critical Warning: ModulusOfImpedance and Impedance have the same unit ModulusOfImpedanceUnit.tera_ohm
Critical Warning: ModulusOfImpedance and Impedance have the same unit ModulusOfImpedanceUnit.giga_ohm
Critical Warning: ModulusOfImpedance and Impedance have the same unit ModulusOfImpedanceUnit.mega_ohm
Critical Warning: ModulusOfImpedance and Impedance have the same unit ModulusOfImpedanceUnit.micro_ohm
Error: Missing unit VolumetricHeatCapacityUnit.joule_per_centi_meter_cubed_per_kelvin in unit_registry
Critical Warning: ExtentOfReaction and AmountOfSubstance have the same unit ExtentOfReactionUnit.mole
Critical Warning: ExtentOfReaction and AmountOfSubstance have the same unit ExtentOfReactionUnit.milli_mole
Critical Warning: ExtentOfReaction and AmountOfSubstance have the same unit ExtentOfReactionUnit.kilo_mole
Critical Warning: ExtentOfReaction and AmountOfSubstance have the same unit ExtentOfReactionUnit.femto_mole
Critical Warning: ExtentOfReaction and AmountOfSubstance have the same unit ExtentOfReactionUnit.micro_mole
Critical Warning: ExchangeIntegral and LevelWidth have the same unit ExchangeIntegralUnit.joule
Critical Warning: ExchangeIntegral and LevelWidth have the same unit ExchangeIntegralUnit.peta_joule
Critical Warning: ExchangeIntegral and LevelWidth have the same unit ExchangeIntegralUnit.kilo_joule
Critical Warning: ExchangeIntegral and LevelWidth have the same unit ExchangeIntegralUnit.milli_joule
Critical Warning: ExchangeIntegral and LevelWidth have the same unit ExchangeIntegralUnit.femto_joule
Critical Warning: ExchangeIntegral and LevelWidth have the same unit ExchangeIntegralUnit.tera_joule
Critical Warning: ExchangeIntegral and LevelWidth have the same unit ExchangeIntegralUnit.exa_joule
Critical Warning: ExchangeIntegral and LevelWidth have the same unit ExchangeIntegralUnit.giga_joule
Critical Warning: ExchangeIntegral and LevelWidth have the same unit ExchangeIntegralUnit.mega_joule
Critical Warning: ExchangeIntegral and LevelWidth have the same unit ExchangeIntegralUnit.atto_joule
Critical Warning: InverseLength and LinearAbsorptionCoefficient have the same unit InverseLengthUnit.per_meter
Critical Warning: InverseLength and LinearAbsorptionCoefficient have the same unit InverseLengthUnit.per_milli_meter
Critical Warning: InverseLength and LinearAbsorptionCoefficient have the same unit InverseLengthUnit.per_nano_meter
Critical Warning: InverseLength and LinearAbsorptionCoefficient have the same unit InverseLengthUnit.per_centi_meter
Critical Warning: InverseLength and LinearAbsorptionCoefficient have the same unit InverseLengthUnit.per_kilo_meter
Critical Warning: InverseLength and LinearAbsorptionCoefficient have the same unit InverseLengthUnit.per_micro_meter
Critical Warning: InverseLength and LinearAbsorptionCoefficient have the same unit InverseLengthUnit.per_pico_meter
Error: Missing unit VolumeThermalExpansionUnit.centi_meter_cubed_per_kelvin in unit_registry
Critical Warning: SoundPressureLevel and SoundReductionIndex have the same unit SoundPressureLevelUnit.byte
Critical Warning: PhotosyntheticPhotonFlux and MolarFlowRate have the same unit PhotosyntheticPhotonFluxUnit.mole_per_second
Critical Warning: PhotosyntheticPhotonFlux and MolarFlowRate have the same unit PhotosyntheticPhotonFluxUnit.micro_mole_per_second
Critical Warning: PhotosyntheticPhotonFlux and MolarFlowRate have the same unit PhotosyntheticPhotonFluxUnit.kilo_mole_per_second
Error: Missing unit SecondMomentOfAreaUnit.field_4 in pint
Error: Missing unit SecondMomentOfAreaUnit.field_4_1 in pint
Error: Missing unit SecondMomentOfAreaUnit.field_4_2 in pint
Critical Warning: Voltage and ElectricPotentialDifference have the same unit VoltageUnit.volt
Critical Warning: Voltage and ElectricPotentialDifference have the same unit VoltageUnit.milli_volt
Critical Warning: Voltage and ElectricPotentialDifference have the same unit VoltageUnit.micro_volt
Critical Warning: Voltage and ElectricPotentialDifference have the same unit VoltageUnit.kilo_volt
Critical Warning: Voltage and ElectricPotentialDifference have the same unit VoltageUnit.mega_volt
Error: Missing unit PermittivityUnit.farad_per_kilo_meter in unit_registry
Error: Missing unit AreaPerHeatingLoadUnit.meter_squared_per_kilo_watt in unit_registry
Critical Warning: DisplacementCurrent and MagnetomotiveForce have the same unit DisplacementCurrentUnit.ampere
Critical Warning: DisplacementCurrent and MagnetomotiveForce have the same unit DisplacementCurrentUnit.pico_ampere
Critical Warning: DisplacementCurrent and MagnetomotiveForce have the same unit DisplacementCurrentUnit.mega_ampere
Critical Warning: DisplacementCurrent and MagnetomotiveForce have the same unit DisplacementCurrentUnit.kilo_ampere
Critical Warning: DisplacementCurrent and MagnetomotiveForce have the same unit DisplacementCurrentUnit.micro_ampere
Critical Warning: DisplacementCurrent and MagnetomotiveForce have the same unit DisplacementCurrentUnit.milli_ampere
Error: Missing unit ReactionRateConstantUnit.centi_meter_cubed_per_mole_per_second in unit_registry
Critical Warning: PowerPerArea and PoyntingVector have the same unit PowerPerAreaUnit.watt_per_meter_squared
Error: Missing unit PowerPerAreaUnit.watt_per_centi_meter_squared in unit_registry
Critical Warning: PowerPerArea and PoyntingVector have the same unit PowerPerAreaUnit.micro_watt_per_meter_squared
Critical Warning: PowerPerArea and PoyntingVector have the same unit PowerPerAreaUnit.milli_watt_per_meter_squared
Critical Warning: PowerPerArea and PoyntingVector have the same unit PowerPerAreaUnit.pico_watt_per_meter_squared
Error: Missing unit MassEnergyTransferCoefficientUnit.meter_squared_per_kilo_gram in unit_registry
Critical Warning: InverseTemperature and ExpansionRatio have the same unit InverseTemperatureUnit.per_kelvin
Critical Warning: AngularMomentum and AngularImpulse have the same unit AngularMomentumUnit.joule_second
Critical Warning: AngularMomentum and AngularImpulse have the same unit AngularMomentumUnit.atto_joule_second
Critical Warning: EnergyFluence and RadiantFluence have the same unit EnergyFluenceUnit.joule_per_meter_squared
Critical Warning: EnergyFluence and RadiantFluence have the same unit EnergyFluenceUnit.mega_joule_per_meter_squared
Critical Warning: EnergyFluence and RadiantFluence have the same unit EnergyFluenceUnit.milli_joule_per_meter_squared
Error: Missing unit EnergyFluenceUnit.joule_per_centi_meter_squared in unit_registry
Critical Warning: EnergyFluence and RadiantFluence have the same unit EnergyFluenceUnit.giga_joule_per_meter_squared
Warning: ConcentrationUnit.mole_per_deci_meter_cubed was normalized to ConcentrationUnit.kilo_mole_per_meter_cubed
Error: Missing unit IonConcentrationUnit.candela_per_kilo_lumen in unit_registry
Critical Warning: AngularVelocity and AngularFrequency have the same unit AngularVelocityUnit.radian_per_second
Critical Warning: ElectricCurrent and MagnetomotiveForce have the same unit ElectricCurrentUnit.ampere
Critical Warning: ElectricCurrent and MagnetomotiveForce have the same unit ElectricCurrentUnit.pico_ampere
Critical Warning: ElectricCurrent and MagnetomotiveForce have the same unit ElectricCurrentUnit.mega_ampere
Critical Warning: ElectricCurrent and MagnetomotiveForce have the same unit ElectricCurrentUnit.kilo_ampere
Critical Warning: ElectricCurrent and MagnetomotiveForce have the same unit ElectricCurrentUnit.micro_ampere
Critical Warning: ElectricCurrent and MagnetomotiveForce have the same unit ElectricCurrentUnit.milli_ampere
Critical Warning: DisplacementCurrentDensity and TotalCurrentDensity have the same unit DisplacementCurrentDensityUnit.ampere_per_meter_squared
Critical Warning: DisplacementCurrentDensity and TotalCurrentDensity have the same unit DisplacementCurrentDensityUnit.mega_ampere_per_meter_squared
Critical Warning: DisplacementCurrentDensity and TotalCurrentDensity have the same unit DisplacementCurrentDensityUnit.kilo_ampere_per_meter_squared
Critical Warning: DisplacementCurrentDensity and TotalCurrentDensity have the same unit DisplacementCurrentDensityUnit.ampere_per_milli_meter_squared
Critical Warning: DisplacementCurrentDensity and TotalCurrentDensity have the same unit DisplacementCurrentDensityUnit.ampere_per_centi_meter_squared
Error: Missing unit SpecificHeatCapacityAtConstantPressureUnit.joule_per_Celsius_per_kilo_gram in pint
Critical Warning: ElectricFieldStrength and ElectricField have the same unit ElectricFieldStrengthUnit.volt_per_meter
Critical Warning: ElectricFieldStrength and ElectricField have the same unit ElectricFieldStrengthUnit.micro_volt_per_meter
Critical Warning: ElectricFieldStrength and ElectricField have the same unit ElectricFieldStrengthUnit.volt_per_milli_meter
Critical Warning: ElectricFieldStrength and ElectricField have the same unit ElectricFieldStrengthUnit.volt_per_centi_meter
Critical Warning: ElectricFieldStrength and ElectricField have the same unit ElectricFieldStrengthUnit.kilo_volt_per_meter
Critical Warning: ElectricFieldStrength and ElectricField have the same unit ElectricFieldStrengthUnit.mega_volt_per_meter
Critical Warning: ElectricFieldStrength and ElectricField have the same unit ElectricFieldStrengthUnit.milli_volt_per_meter
Critical Warning: RadiantEnergyDensity and ElectromagneticEnergyDensity have the same unit RadiantEnergyDensityUnit.joule_per_meter_cubed
Critical Warning: RadiantEnergyDensity and ElectromagneticEnergyDensity have the same unit RadiantEnergyDensityUnit.mega_joule_per_meter_cubed
Critical Warning: EnergyDensity and ElectromagneticEnergyDensity have the same unit EnergyDensityUnit.joule_per_meter_cubed
Critical Warning: EnergyDensity and ElectromagneticEnergyDensity have the same unit EnergyDensityUnit.mega_joule_per_meter_cubed
Warning: ElectricFieldUnit.volt_per_milli_meter was normalized to ElectricFieldUnit.kilo_volt_per_meter
Warning: ElectricFieldUnit.volt_per_centi_meter was normalized to ElectricFieldUnit.volt_per_meter
Critical Warning: EnergyPerArea and RadiantFluence have the same unit EnergyPerAreaUnit.joule_per_meter_squared
Critical Warning: EnergyPerArea and RadiantFluence have the same unit EnergyPerAreaUnit.mega_joule_per_meter_squared
Critical Warning: EnergyPerArea and RadiantFluence have the same unit EnergyPerAreaUnit.milli_joule_per_meter_squared
Error: Missing unit EnergyPerAreaUnit.joule_per_centi_meter_squared in unit_registry
Critical Warning: EnergyPerArea and RadiantFluence have the same unit EnergyPerAreaUnit.giga_joule_per_meter_squared
Warning: PeriodUnit.deci_second was normalized to PeriodUnit.milli_second
Error: Missing unit RadiantFluenceUnit.joule_per_centi_meter_squared in unit_registry
Error: Missing unit IonicStrengthUnit.mole_per_kilo_gram in unit_registry
Error: Missing unit IonicStrengthUnit.centi_mole_per_kilo_gram in unit_registry
Error: Missing unit IonicStrengthUnit.micro_mole_per_kilo_gram in unit_registry
Error: Missing unit IonicStrengthUnit.femto_mole_per_kilo_gram in unit_registry
Error: Missing unit IonicStrengthUnit.pico_mole_per_kilo_gram in unit_registry
Error: Missing unit IonicStrengthUnit.milli_mole_per_kilo_gram in unit_registry
Error: Missing unit IonicStrengthUnit.nano_mole_per_kilo_gram in unit_registry
Error: Missing unit IonicStrengthUnit.kilo_mole_per_kilo_gram in unit_registry
Critical Warning: SoundExposureLevel and SoundReductionIndex have the same unit SoundExposureLevelUnit.byte
Critical Warning: TotalCurrent and MagnetomotiveForce have the same unit TotalCurrentUnit.ampere
Critical Warning: TotalCurrent and MagnetomotiveForce have the same unit TotalCurrentUnit.pico_ampere
Critical Warning: TotalCurrent and MagnetomotiveForce have the same unit TotalCurrentUnit.mega_ampere
Critical Warning: TotalCurrent and MagnetomotiveForce have the same unit TotalCurrentUnit.kilo_ampere
Critical Warning: TotalCurrent and MagnetomotiveForce have the same unit TotalCurrentUnit.micro_ampere
Critical Warning: TotalCurrent and MagnetomotiveForce have the same unit TotalCurrentUnit.milli_ampere
Critical Warning: SpecificPower and AbsorbedDoseRate have the same unit SpecificPowerUnit.gray_per_second
Error: Missing unit MassTemperatureUnit.kelvin_kilo_gram in unit_registry
Critical Warning: MolarHeatCapacity and MolarEntropy have the same unit MolarHeatCapacityUnit.joule_per_kelvin_per_mole
Critical Warning: MassPerArea and BodyMassIndex have the same unit MassPerAreaUnit.kilo_gram_per_meter_squared
Critical Warning: PropagationCoefficient and LinearAbsorptionCoefficient have the same unit PropagationCoefficientUnit.per_meter
Critical Warning: PropagationCoefficient and LinearAbsorptionCoefficient have the same unit PropagationCoefficientUnit.per_milli_meter
Critical Warning: PropagationCoefficient and LinearAbsorptionCoefficient have the same unit PropagationCoefficientUnit.per_nano_meter
Critical Warning: PropagationCoefficient and LinearAbsorptionCoefficient have the same unit PropagationCoefficientUnit.per_centi_meter
Critical Warning: PropagationCoefficient and LinearAbsorptionCoefficient have the same unit PropagationCoefficientUnit.per_kilo_meter
Critical Warning: PropagationCoefficient and LinearAbsorptionCoefficient have the same unit PropagationCoefficientUnit.per_micro_meter
Critical Warning: PropagationCoefficient and LinearAbsorptionCoefficient have the same unit PropagationCoefficientUnit.per_pico_meter
Error: Missing unit LengthEnergyUnit.fermi_mega_electron_volt in pint
Critical Warning: RelativePressureCoefficient and ExpansionRatio have the same unit RelativePressureCoefficientUnit.per_kelvin
Critical Warning: IsentropicCompressibility and StressOpticCoefficient have the same unit IsentropicCompressibilityUnit.per_pascal
Critical Warning: MassConcentration and MassDensity have the same unit MassConcentrationUnit.gram_per_liter
Critical Warning: MassConcentration and MassDensity have the same unit MassConcentrationUnit.milli_gram_per_liter
Critical Warning: MassConcentration and MassDensity have the same unit MassConcentrationUnit.micro_gram_per_liter
Critical Warning: MassConcentration and MassDensity have the same unit MassConcentrationUnit.gram_per_milli_liter
Critical Warning: MassConcentration and MassDensity have the same unit MassConcentrationUnit.kilo_gram_per_liter
Critical Warning: MassConcentration and MassDensity have the same unit MassConcentrationUnit.pico_gram_per_liter
Critical Warning: MassConcentration and MassDensity have the same unit MassConcentrationUnit.milli_gram_per_milli_liter
Critical Warning: MassConcentration and MassDensity have the same unit MassConcentrationUnit.gram_per_deci_liter
Critical Warning: MassConcentration and MassDensity have the same unit MassConcentrationUnit.femto_gram_per_liter
Critical Warning: MassConcentration and MassDensity have the same unit MassConcentrationUnit.nano_gram_per_liter
Critical Warning: MolarVolume and MolarRefractivity have the same unit MolarVolumeUnit.meter_cubed_per_mole
Error: Missing unit MolarVolumeUnit.deci_meter_cubed_per_mole in unit_registry
Error: Missing unit MolarVolumeUnit.centi_meter_cubed_per_mole in unit_registry
Critical Warning: Resistance and Impedance have the same unit ResistanceUnit.ohm
Critical Warning: Resistance and Impedance have the same unit ResistanceUnit.kilo_ohm
Critical Warning: Resistance and Impedance have the same unit ResistanceUnit.milli_ohm
Critical Warning: Resistance and Impedance have the same unit ResistanceUnit.tera_ohm
Critical Warning: Resistance and Impedance have the same unit ResistanceUnit.giga_ohm
Critical Warning: Resistance and Impedance have the same unit ResistanceUnit.mega_ohm
Critical Warning: Resistance and Impedance have the same unit ResistanceUnit.micro_ohm
Critical Warning: BloodGlucoseLevelByMass and MassDensity have the same unit BloodGlucoseLevelByMassUnit.gram_per_liter
Critical Warning: BloodGlucoseLevelByMass and MassDensity have the same unit BloodGlucoseLevelByMassUnit.milli_gram_per_liter
Critical Warning: BloodGlucoseLevelByMass and MassDensity have the same unit BloodGlucoseLevelByMassUnit.micro_gram_per_liter
Critical Warning: BloodGlucoseLevelByMass and MassDensity have the same unit BloodGlucoseLevelByMassUnit.gram_per_milli_liter
Critical Warning: BloodGlucoseLevelByMass and MassDensity have the same unit BloodGlucoseLevelByMassUnit.kilo_gram_per_liter
Critical Warning: BloodGlucoseLevelByMass and MassDensity have the same unit BloodGlucoseLevelByMassUnit.pico_gram_per_liter
Critical Warning: BloodGlucoseLevelByMass and MassDensity have the same unit BloodGlucoseLevelByMassUnit.milli_gram_per_milli_liter
Critical Warning: BloodGlucoseLevelByMass and MassDensity have the same unit BloodGlucoseLevelByMassUnit.gram_per_deci_liter
Critical Warning: BloodGlucoseLevelByMass and MassDensity have the same unit BloodGlucoseLevelByMassUnit.femto_gram_per_liter
Critical Warning: BloodGlucoseLevelByMass and MassDensity have the same unit BloodGlucoseLevelByMassUnit.nano_gram_per_liter
Critical Warning: LinearAttenuationCoefficient and LinearAbsorptionCoefficient have the same unit LinearAttenuationCoefficientUnit.per_meter
Critical Warning: LinearAttenuationCoefficient and LinearAbsorptionCoefficient have the same unit LinearAttenuationCoefficientUnit.per_milli_meter
Critical Warning: LinearAttenuationCoefficient and LinearAbsorptionCoefficient have the same unit LinearAttenuationCoefficientUnit.per_nano_meter
Critical Warning: LinearAttenuationCoefficient and LinearAbsorptionCoefficient have the same unit LinearAttenuationCoefficientUnit.per_centi_meter
Critical Warning: LinearAttenuationCoefficient and LinearAbsorptionCoefficient have the same unit LinearAttenuationCoefficientUnit.per_kilo_meter
Critical Warning: LinearAttenuationCoefficient and LinearAbsorptionCoefficient have the same unit LinearAttenuationCoefficientUnit.per_micro_meter
Critical Warning: LinearAttenuationCoefficient and LinearAbsorptionCoefficient have the same unit LinearAttenuationCoefficientUnit.per_pico_meter
Critical Warning: Velocity and Speed have the same unit VelocityUnit.meter_per_second
Critical Warning: Velocity and Speed have the same unit VelocityUnit.centi_meter_per_second
Critical Warning: Velocity and Speed have the same unit VelocityUnit.micro_meter_per_second
Critical Warning: Velocity and Speed have the same unit VelocityUnit.milli_meter_per_second
Critical Warning: Velocity and Speed have the same unit VelocityUnit.kilo_meter_per_second
Critical Warning: LinearElectricCurrentDensity and Coercivity have the same unit LinearElectricCurrentDensityUnit.ampere_per_meter
Critical Warning: LinearElectricCurrentDensity and Coercivity have the same unit LinearElectricCurrentDensityUnit.ampere_per_milli_meter
Critical Warning: LinearElectricCurrentDensity and Coercivity have the same unit LinearElectricCurrentDensityUnit.milli_ampere_per_milli_meter
Critical Warning: LinearElectricCurrentDensity and Coercivity have the same unit LinearElectricCurrentDensityUnit.kilo_ampere_per_meter
Critical Warning: LinearElectricCurrentDensity and Coercivity have the same unit LinearElectricCurrentDensityUnit.ampere_per_centi_meter
Critical Warning: AreaPerTime and ThermalDiffusionCoefficient have the same unit AreaPerTimeUnit.meter_squared_per_second
Critical Warning: AreaPerTime and ThermalDiffusionCoefficient have the same unit AreaPerTimeUnit.milli_meter_squared_per_second
Critical Warning: AreaPerTime and ThermalDiffusionCoefficient have the same unit AreaPerTimeUnit.centi_meter_squared_per_second
Critical Warning: MagneticFluxDensity and MagneticField have the same unit MagneticFluxDensityUnit.tesla
Critical Warning: MagneticFluxDensity and MagneticField have the same unit MagneticFluxDensityUnit.micro_tesla
Critical Warning: MagneticFluxDensity and MagneticField have the same unit MagneticFluxDensityUnit.milli_tesla
Critical Warning: MagneticFluxDensity and MagneticField have the same unit MagneticFluxDensityUnit.nano_tesla
Error: Missing unit WarpingConstantUnit.field_6 in pint
Error: Missing unit WarpingConstantUnit.field_6_1 in pint
Critical Warning: Force and TorquePerLength have the same unit ForceUnit.newton
Critical Warning: Force and TorquePerLength have the same unit ForceUnit.kilo_newton
Warning: ThermalDiffusionCoefficientUnit.centi_meter_squared_per_second was normalized to ThermalDiffusionCoefficientUnit.milli_meter_squared_per_second
Critical Warning: MagneticMoment and MagneticAreaMoment have the same unit MagneticMomentUnit.joule_per_tesla
Critical Warning: TorquePerAngle and TorsionalSpringConstant have the same unit TorquePerAngleUnit.meter_newton_per_radian
Critical Warning: ElectricCurrentDensity and TotalCurrentDensity have the same unit ElectricCurrentDensityUnit.ampere_per_meter_squared
Critical Warning: ElectricCurrentDensity and TotalCurrentDensity have the same unit ElectricCurrentDensityUnit.mega_ampere_per_meter_squared
Critical Warning: ElectricCurrentDensity and TotalCurrentDensity have the same unit ElectricCurrentDensityUnit.kilo_ampere_per_meter_squared
Critical Warning: ElectricCurrentDensity and TotalCurrentDensity have the same unit ElectricCurrentDensityUnit.ampere_per_milli_meter_squared
Critical Warning: ElectricCurrentDensity and TotalCurrentDensity have the same unit ElectricCurrentDensityUnit.ampere_per_centi_meter_squared
Error: Missing unit SpecificHeatCapacityAtConstantVolumeUnit.joule_per_Celsius_per_kilo_gram in pint
Warning: SpeedUnit.centi_meter_per_second was normalized to SpeedUnit.milli_meter_per_second
Error: Missing unit SpecificActivityUnit.becquerel_per_kilo_gram in unit_registry
Error: Missing unit SpecificActivityUnit.milli_becquerel_per_kilo_gram in unit_registry
Error: Missing unit SpecificActivityUnit.micro_becquerel_per_kilo_gram in unit_registry
Critical Warning: ElectricChargePerArea and ElectricPolarization have the same unit ElectricChargePerAreaUnit.coulomb_per_meter_squared
Critical Warning: ElectricChargePerArea and ElectricPolarization have the same unit ElectricChargePerAreaUnit.mega_coulomb_per_meter_squared
Critical Warning: ElectricChargePerArea and ElectricPolarization have the same unit ElectricChargePerAreaUnit.coulomb_per_milli_meter_squared
Critical Warning: ElectricChargePerArea and ElectricPolarization have the same unit ElectricChargePerAreaUnit.micro_coulomb_per_meter_squared
Critical Warning: ElectricChargePerArea and ElectricPolarization have the same unit ElectricChargePerAreaUnit.coulomb_per_centi_meter_squared
Critical Warning: ElectricChargePerArea and ElectricPolarization have the same unit ElectricChargePerAreaUnit.kilo_coulomb_per_meter_squared
Critical Warning: ElectricChargePerArea and ElectricPolarization have the same unit ElectricChargePerAreaUnit.milli_coulomb_per_meter_squared
Error: Missing unit MassAbsorptionCoefficientUnit.meter_squared_per_kilo_gram in unit_registry
Warning: CoercivityUnit.ampere_per_milli_meter was normalized to CoercivityUnit.kilo_ampere_per_meter
Warning: CoercivityUnit.milli_ampere_per_milli_meter was normalized to CoercivityUnit.ampere_per_meter
Warning: CoercivityUnit.ampere_per_centi_meter was normalized to CoercivityUnit.ampere_per_meter
Warning: ElectricPolarizationUnit.coulomb_per_milli_meter_squared was normalized to ElectricPolarizationUnit.mega_coulomb_per_meter_squared
Warning: ElectricPolarizationUnit.coulomb_per_centi_meter_squared was normalized to ElectricPolarizationUnit.kilo_coulomb_per_meter_squared
Critical Warning: RecombinationCoefficient and SoundVolumeVelocity have the same unit RecombinationCoefficientUnit.meter_cubed_per_second
Error: Missing unit RecombinationCoefficientUnit.centi_meter_cubed_per_second in unit_registry
Error: Missing unit RecombinationCoefficientUnit.deci_meter_cubed_per_second in unit_registry
Error: Missing unit SpecificEntropyUnit.joule_per_Celsius_per_kilo_gram in pint
Warning: MomentOfForceUnit.deci_newton_meter was normalized to MomentOfForceUnit.meter_milli_newton
Warning: MomentOfForceUnit.centi_newton_meter was normalized to MomentOfForceUnit.meter_milli_newton
Error: Missing unit MomentOfForceUnit.meter_milli_newton in unit_registry
Error: Missing unit MomentOfForceUnit.meter_micro_newton in unit_registry
Error: Missing unit MomentOfForceUnit.centi_meter_newton in unit_registry
Critical Warning: Conductance and Admittance have the same unit ConductanceUnit.siemens
Critical Warning: Conductance and Admittance have the same unit ConductanceUnit.milli_siemens
Critical Warning: Conductance and Admittance have the same unit ConductanceUnit.kilo_siemens
Critical Warning: Conductance and Admittance have the same unit ConductanceUnit.micro_siemens
Critical Warning: CurrentLinkage and MagnetomotiveForce have the same unit CurrentLinkageUnit.ampere
Critical Warning: CurrentLinkage and MagnetomotiveForce have the same unit CurrentLinkageUnit.pico_ampere
Critical Warning: CurrentLinkage and MagnetomotiveForce have the same unit CurrentLinkageUnit.mega_ampere
Critical Warning: CurrentLinkage and MagnetomotiveForce have the same unit CurrentLinkageUnit.kilo_ampere
Critical Warning: CurrentLinkage and MagnetomotiveForce have the same unit CurrentLinkageUnit.micro_ampere
Critical Warning: CurrentLinkage and MagnetomotiveForce have the same unit CurrentLinkageUnit.milli_ampere
Critical Warning: MassConcentrationOfWater and MassConcentrationOfWaterVapour have the same unit MassConcentrationOfWaterUnit.kilo_gram_per_meter_cubed
Error: Missing unit SpecificHeatCapacityAtSaturationUnit.joule_per_Celsius_per_kilo_gram in pint
Critical Warning: RotationalFrequency and Frequency have the same unit RotationalFrequencyUnit.hertz
Critical Warning: RotationalFrequency and Frequency have the same unit RotationalFrequencyUnit.mega_hertz
Critical Warning: RotationalFrequency and Frequency have the same unit RotationalFrequencyUnit.kilo_hertz
Critical Warning: RotationalFrequency and Frequency have the same unit RotationalFrequencyUnit.giga_hertz
Critical Warning: RotationalFrequency and Frequency have the same unit RotationalFrequencyUnit.tera_hertz
Critical Warning: ScalarMagneticPotential and MagneticVectorPotential have the same unit ScalarMagneticPotentialUnit.second_volt_per_meter
Warning: ElectricChargeUnit.deci_coulomb was normalized to ElectricChargeUnit.milli_coulomb
Warning: ElectricChargeUnit.deca_coulomb was normalized to ElectricChargeUnit.coulomb
Warning: ElectricChargeUnit.hecto_coulomb was normalized to ElectricChargeUnit.coulomb
Warning: ElectricChargeUnit.centi_coulomb was normalized to ElectricChargeUnit.milli_coulomb
Error: Missing unit InverseEnergyUnit.per_hour_per_kilo_volt_ampere in pint
Error: Missing unit SpecificSurfaceAreaUnit.meter_squared_per_kilo_gram in unit_registry
Error: Missing unit LengthTemperatureTimeUnit.centi_meter_Celsius_second in pint
Error: Missing unit VolumetricFluxUnit.milli_liter_per_centi_meter_squared_per_minute in unit_registry
Error: Missing unit SpecificHeatVolumeUnit.joule_per_kelvin_per_kilo_gram_per_meter_cubed in unit_registry
Critical Warning: AreaPerLength and Length have the same unit AreaPerLengthUnit.meter
Critical Warning: VolumeFlowRate and SoundVolumeVelocity have the same unit VolumeFlowRateUnit.meter_cubed_per_second
Error: Missing unit VolumeFlowRateUnit.centi_meter_cubed_per_second in unit_registry
Error: Missing unit VolumeFlowRateUnit.deci_meter_cubed_per_second in unit_registry
Error: Missing unit MolarRefractivityUnit.deci_meter_cubed_per_mole in unit_registry
Error: Missing unit MolarRefractivityUnit.centi_meter_cubed_per_mole in unit_registry
Error: Missing unit MassAttenuationCoefficientUnit.meter_squared_per_kilo_gram in unit_registry
Critical Warning: ForcePerArea and ShearModulus have the same unit ForcePerAreaUnit.pascal
Critical Warning: ForcePerArea and ShearModulus have the same unit ForcePerAreaUnit.giga_pascal
Critical Warning: ForcePerArea and ShearModulus have the same unit ForcePerAreaUnit.deca_pascal
Critical Warning: ForcePerArea and ShearModulus have the same unit ForcePerAreaUnit.milli_pascal
Critical Warning: ForcePerArea and ShearModulus have the same unit ForcePerAreaUnit.mega_pascal
Critical Warning: ForcePerArea and ShearModulus have the same unit ForcePerAreaUnit.kilo_pascal
Critical Warning: ForcePerArea and ShearModulus have the same unit ForcePerAreaUnit.hecto_pascal
Critical Warning: ForcePerArea and ShearModulus have the same unit ForcePerAreaUnit.micro_pascal
Error: Missing unit PowerPerElectricChargeUnit.volt_per_micro_second in unit_registry
Critical Warning: VolumePerTime and SoundVolumeVelocity have the same unit VolumePerTimeUnit.meter_cubed_per_second
Error: Missing unit VolumePerTimeUnit.centi_meter_cubed_per_second in unit_registry
Error: Missing unit VolumePerTimeUnit.deci_meter_cubed_per_second in unit_registry
Critical Warning: Fugacity and ShearModulus have the same unit FugacityUnit.pascal
Critical Warning: Fugacity and ShearModulus have the same unit FugacityUnit.giga_pascal
Critical Warning: Fugacity and ShearModulus have the same unit FugacityUnit.deca_pascal
Critical Warning: Fugacity and ShearModulus have the same unit FugacityUnit.milli_pascal
Critical Warning: Fugacity and ShearModulus have the same unit FugacityUnit.mega_pascal
Critical Warning: Fugacity and ShearModulus have the same unit FugacityUnit.kilo_pascal
Critical Warning: Fugacity and ShearModulus have the same unit FugacityUnit.hecto_pascal
Critical Warning: Fugacity and ShearModulus have the same unit FugacityUnit.micro_pascal
Error: Missing unit PoyntingVectorUnit.watt_per_centi_meter_squared in unit_registry
Error: Missing unit QuarticElectricDipoleMomentPerCubicEnergyUnit.field_4_per_joule_cubed in pint
Error: Missing unit SoundVolumeVelocityUnit.centi_meter_cubed_per_second in unit_registry
Error: Missing unit SoundVolumeVelocityUnit.deci_meter_cubed_per_second in unit_registry
Critical Warning: HamiltonFunction and LevelWidth have the same unit HamiltonFunctionUnit.joule
Critical Warning: HamiltonFunction and LevelWidth have the same unit HamiltonFunctionUnit.peta_joule
Critical Warning: HamiltonFunction and LevelWidth have the same unit HamiltonFunctionUnit.kilo_joule
Critical Warning: HamiltonFunction and LevelWidth have the same unit HamiltonFunctionUnit.milli_joule
Critical Warning: HamiltonFunction and LevelWidth have the same unit HamiltonFunctionUnit.femto_joule
Critical Warning: HamiltonFunction and LevelWidth have the same unit HamiltonFunctionUnit.tera_joule
Critical Warning: HamiltonFunction and LevelWidth have the same unit HamiltonFunctionUnit.exa_joule
Critical Warning: HamiltonFunction and LevelWidth have the same unit HamiltonFunctionUnit.giga_joule
Critical Warning: HamiltonFunction and LevelWidth have the same unit HamiltonFunctionUnit.mega_joule
Critical Warning: HamiltonFunction and LevelWidth have the same unit HamiltonFunctionUnit.atto_joule
Critical Warning: Curvature and LinearAbsorptionCoefficient have the same unit CurvatureUnit.per_meter
Critical Warning: Curvature and LinearAbsorptionCoefficient have the same unit CurvatureUnit.per_milli_meter
Critical Warning: Curvature and LinearAbsorptionCoefficient have the same unit CurvatureUnit.per_nano_meter
Critical Warning: Curvature and LinearAbsorptionCoefficient have the same unit CurvatureUnit.per_centi_meter
Critical Warning: Curvature and LinearAbsorptionCoefficient have the same unit CurvatureUnit.per_kilo_meter
Critical Warning: Curvature and LinearAbsorptionCoefficient have the same unit CurvatureUnit.per_micro_meter
Critical Warning: Curvature and LinearAbsorptionCoefficient have the same unit CurvatureUnit.per_pico_meter
Critical Warning: Reactance and Impedance have the same unit ReactanceUnit.ohm
Critical Warning: Reactance and Impedance have the same unit ReactanceUnit.kilo_ohm
Critical Warning: Reactance and Impedance have the same unit ReactanceUnit.milli_ohm
Critical Warning: Reactance and Impedance have the same unit ReactanceUnit.tera_ohm
Critical Warning: Reactance and Impedance have the same unit ReactanceUnit.giga_ohm
Critical Warning: Reactance and Impedance have the same unit ReactanceUnit.mega_ohm
Critical Warning: Reactance and Impedance have the same unit ReactanceUnit.micro_ohm
Error: Missing unit SecondAxialMomentOfAreaUnit.field_4 in pint
Error: Missing unit SecondAxialMomentOfAreaUnit.field_4_1 in pint
Error: Missing unit SecondAxialMomentOfAreaUnit.field_4_2 in pint
Warning: LengthUnit.centi_meter was normalized to LengthUnit.milli_meter
Warning: LengthUnit.hecto_meter was normalized to LengthUnit.meter
Warning: LengthUnit.deci_meter was normalized to LengthUnit.milli_meter
Warning: LengthUnit.deca_meter was normalized to LengthUnit.meter
Warning: MassDensityUnit.gram_per_milli_liter was normalized to MassDensityUnit.kilo_gram_per_liter
Warning: MassDensityUnit.milli_gram_per_milli_liter was normalized to MassDensityUnit.gram_per_liter
Warning: MassDensityUnit.gram_per_deci_liter was normalized to MassDensityUnit.gram_per_liter
Error: Missing unit PowerPerAreaQuarticTemperatureUnit.field_4_per_meter_squared in pint
Error: Missing unit AmountOfSubstancePerMassUnit.mole_per_kilo_gram in unit_registry
Error: Missing unit AmountOfSubstancePerMassUnit.centi_mole_per_kilo_gram in unit_registry
Error: Missing unit AmountOfSubstancePerMassUnit.micro_mole_per_kilo_gram in unit_registry
Error: Missing unit AmountOfSubstancePerMassUnit.femto_mole_per_kilo_gram in unit_registry
Error: Missing unit AmountOfSubstancePerMassUnit.pico_mole_per_kilo_gram in unit_registry
Error: Missing unit AmountOfSubstancePerMassUnit.milli_mole_per_kilo_gram in unit_registry
Error: Missing unit AmountOfSubstancePerMassUnit.nano_mole_per_kilo_gram in unit_registry
Error: Missing unit AmountOfSubstancePerMassUnit.kilo_mole_per_kilo_gram in unit_registry
Error: Missing unit DimensionlessUnit.field_ in pint
Critical Warning: LinearIonization and LinearAbsorptionCoefficient have the same unit LinearIonizationUnit.per_meter
Critical Warning: LinearIonization and LinearAbsorptionCoefficient have the same unit LinearIonizationUnit.per_milli_meter
Critical Warning: LinearIonization and LinearAbsorptionCoefficient have the same unit LinearIonizationUnit.per_nano_meter
Critical Warning: LinearIonization and LinearAbsorptionCoefficient have the same unit LinearIonizationUnit.per_centi_meter
Critical Warning: LinearIonization and LinearAbsorptionCoefficient have the same unit LinearIonizationUnit.per_kilo_meter
Critical Warning: LinearIonization and LinearAbsorptionCoefficient have the same unit LinearIonizationUnit.per_micro_meter
Critical Warning: LinearIonization and LinearAbsorptionCoefficient have the same unit LinearIonizationUnit.per_pico_meter
Error: Missing unit SpecificHeatPressureUnit.joule_per_kelvin_per_kilo_gram_per_pascal in unit_registry
Warning: ElectrolyticConductivityUnit.siemens_per_centi_meter was normalized to ElectrolyticConductivityUnit.siemens_per_meter
Warning: ElectrolyticConductivityUnit.deci_siemens_per_meter was normalized to ElectrolyticConductivityUnit.milli_siemens_per_meter
Error: Missing unit AccelerationUnit.centi_meter_per_second_squared in unit_registry
Error: Missing unit TemperatureGradientUnit.Celsius_per_meter in pint
Warning: TotalCurrentDensityUnit.ampere_per_milli_meter_squared was normalized to TotalCurrentDensityUnit.mega_ampere_per_meter_squared
Warning: TotalCurrentDensityUnit.ampere_per_centi_meter_squared was normalized to TotalCurrentDensityUnit.kilo_ampere_per_meter_squared
Error: Missing unit MolarMassVariationDueToPressureUnit.mole_per_kilo_gram_per_pascal in unit_registry
Warning: ShearModulusUnit.deca_pascal was normalized to ShearModulusUnit.pascal
Warning: ShearModulusUnit.hecto_pascal was normalized to ShearModulusUnit.pascal
Error: Missing unit AreaTimeUnit.centi_meter_squared_minute in unit_registry
Error: Missing unit MassSpecificBiogeochemicalRateUnit.micro_gram_per_day_per_gram in unit_registry
Error: Missing unit UnknownUnit.Celsius_squared_per_second in pint
Error: Missing unit MassRatioUnit.field_ in pint
Error: Missing unit MassRatioUnit.field__1 in pint
Warning: LinearAbsorptionCoefficientUnit.per_centi_meter was normalized to LinearAbsorptionCoefficientUnit.per_meter
```

</details>


<!-- pyscaffold-notes -->

## Note

This project has been set up using PyScaffold 4.6. For details and usage
information on PyScaffold see https://pyscaffold.org/.
