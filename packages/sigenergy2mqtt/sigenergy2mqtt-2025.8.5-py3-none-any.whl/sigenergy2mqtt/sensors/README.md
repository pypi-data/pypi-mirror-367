# MQTT Topics

Topics prefixed with `homeassistant/` are used when the `home-assistant` configuration `enabled` option in the configuration file,
or the `SIGENERGY2MQTT_HASS_ENABLED` environment variable, are set to true, or the `--hass-enabled` command line option is specified
Otherwise, the topics prefixed with `sigenergy2mqtt/` are used.

You can also enable the `sigenergy2mqtt/` topics when Home Assistant discovery is enabled by setting the `SIGENERGY2MQTT_HASS_USE_SIMPLIFIED_TOPICS` environment variable to true,
or by specifying the `--hass-use-simplified-topics` command line option.

The number after the `sigen_` prefix represents the host index from the configuration file, starting from 0. (Home Assistant configuration may change the `sigen` topic prefix.)
Inverter, AC Charger and DC Charger indexes use the device ID as specified in the configuration file.

Default Scan Intervals are shown in seconds, but may be overridden via configuration. Intervals for derived sensors are dependent on the source sensors.

## Published Topics

### Plant
| Sensor Class | Interval | Unit | Gain | State Topic | Source | Applicable To |
|--------------|---------:|------|-----:|-------------|--------|---------------|
| Active Power | 5s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_active_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_active_power/state |Modbus Register 30031 ||
| Active Power Fixed Adjustment Target Value | 60s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_active_power_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_active_power_fixed_adjustment_target_value/state |Modbus Register 40001 ||
| Active Power Percentage Adjustment Target Value | 60s | % | 100 | sigenergy2mqtt/sigen_0_plant_active_power_percentage_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_active_power_percentage_adjustment_target_value/state |Modbus Register 40005 ||
| Available Max Active Power | 600s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_available_max_active_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_available_max_active_power/state |Modbus Register 30039 ||
| Available Max Charging Capacity | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_plant_available_max_charging_capacity/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_available_max_charging_capacity/state |Modbus Register 30064 ||
| Available Max Charging Power | 600s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_available_max_charging_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_available_max_charging_power/state |Modbus Register 30047 ||
| Available Max Discharging Capacity | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_plant_available_max_discharging_capacity/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_available_max_discharging_capacity/state |Modbus Register 30066 ||
| Available Max Discharging Power | 600s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_available_max_discharging_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_available_max_discharging_power/state |Modbus Register 30049 ||
| Available Max Reactive Power | 600s | kvar | 1000 | sigenergy2mqtt/sigen_0_plant_available_max_reactive_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_available_max_reactive_power/state |Modbus Register 30043 ||
| Available Min Active Power | 600s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_available_min_active_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_available_min_active_power/state |Modbus Register 30041 ||
| Available Min Reactive Power | 600s | kvar | 1000 | sigenergy2mqtt/sigen_0_plant_available_min_reactive_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_available_min_reactive_power/state |Modbus Register 30045 ||
| Backup SoC | 60s | % | 10 | sigenergy2mqtt/sigen_0_plant_ess_backup_soc/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_ess_backup_soc/state |Modbus Register 40046 ||
| Battery Charging Power || W | 1 | sigenergy2mqtt/sigen_0_battery_charging_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_battery_charging_power/state |BatteryPower &gt; 0||
| Battery Discharging Power || W | 1 | sigenergy2mqtt/sigen_0_battery_discharging_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_battery_discharging_power/state |BatteryPower &lt; 0||
| Battery Power | 5s | W | 1 | sigenergy2mqtt/sigen_0_plant_battery_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_battery_power/state |Modbus Register 30037 ||
| Battery SoC | 60s | % | 10 | sigenergy2mqtt/sigen_0_plant_battery_soc/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_battery_soc/state |Modbus Register 30014 ||
| Battery SoH | 60s | % | 10 | sigenergy2mqtt/sigen_0_plant_battery_soh/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_battery_soh/state |Modbus Register 30087 ||
| Charge Cut-Off SoC | 60s | % | 10 | sigenergy2mqtt/sigen_0_plant_charge_cut_off_soc/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_charge_cut_off_soc/state |Modbus Register 30085 ||
| Charge Cut-Off SoC | 60s | % | 10 | sigenergy2mqtt/sigen_0_plant_ess_charge_cut_off_soc/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_ess_charge_cut_off_soc/state |Modbus Register 40047 ||
| Consumed Power || W | 1 | sigenergy2mqtt/sigen_0_consumed_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_consumed_power/state |TotalPVPower &plus; GridSensorActivePower &minus; BatteryPower||
| DC Charger Alarms | 10s |  | 1 | sigenergy2mqtt/sigen_0_general_alarm_5/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_general_alarm_5/state |Modbus Register 30072 ||
| Daily Charge Energy || kWh | 100 | sigenergy2mqtt/sigen_0_daily_charge_energy/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_daily_charge_energy/state |&sum; of DailyChargeEnergy across all Inverters associated with the Plant||
| Daily Consumption | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_daily_consumed_energy/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_daily_consumed_energy/state |Modbus Register 30092 ||
| Daily Discharge Energy || kWh | 100 | sigenergy2mqtt/sigen_0_daily_discharge_energy/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_daily_discharge_energy/state |&sum; of DailyDischargeEnergy across all Inverters associated with the Plant||
| Daily PV Production || kWh | 100 | sigenergy2mqtt/sigen_0_daily_pv_energy/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_daily_pv_energy/state |PlantLifetimePVEnergy &minus; PlantLifetimePVEnergy at last midnight||
| Daily Total PV Production || kWh | 100 | sigenergy2mqtt/sigen_0_total_daily_pv_energy/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_total_daily_pv_energy/state |TotalLifetimePVEnergy &minus; TotalLifetimePVEnergy at last midnight||
| Discharge Cut-Off SoC | 60s | % | 10 | sigenergy2mqtt/sigen_0_plant_discharge_cut_off_soc/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_discharge_cut_off_soc/state |Modbus Register 30086 ||
| Discharge Cut-Off SoC | 60s | % | 10 | sigenergy2mqtt/sigen_0_plant_ess_discharge_cut_off_soc/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_ess_discharge_cut_off_soc/state |Modbus Register 40048 ||
| EMS Work Mode | 10s |  | 1 | sigenergy2mqtt/sigen_0_plant_ems_work_mode/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_ems_work_mode/state |Modbus Register 30003 ||
| ESS Alarms | 10s |  | 1 | sigenergy2mqtt/sigen_0_general_alarm_3/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_general_alarm_3/state |Modbus Register 30029 ||
| Gateway Alarms | 10s |  | 1 | sigenergy2mqtt/sigen_0_general_alarm_4/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_general_alarm_4/state |Modbus Register 30030 ||
| Grid Max Export Limit | 10s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_grid_max_export_limit/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_grid_max_export_limit/state |Modbus Register 40038 ||
| Grid Max Import Limit | 10s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_grid_max_import_limit/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_grid_max_import_limit/state |Modbus Register 40040 ||
| Independent Phase Power Control | 60s |  | 1 | sigenergy2mqtt/sigen_0_plant_independent_phase_power_control/state <br/> homeassistant/switch/sigen_0_247_powerplant/sigen_0_plant_independent_phase_power_control/state |Modbus Register 40030 ||
| Lifetime Charge Energy | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_accumulated_charge_energy/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_accumulated_charge_energy/state |Modbus Register 30200 ||
| Lifetime Consumption | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_lifetime_consumed_energy/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_lifetime_consumed_energy/state |Modbus Register 30094 ||
| Lifetime DC EV Charge Energy | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_evdc_total_charge_energy/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_evdc_total_charge_energy/state |Modbus Register 30208 ||
| Lifetime DC EV Discharge Energy | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_evdc_total_discharge_energy/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_evdc_total_discharge_energy/state |Modbus Register 30212 ||
| Lifetime Discharge Energy | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_accumulated_discharge_energy/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_accumulated_discharge_energy/state |Modbus Register 30204 ||
| Lifetime Generator Output Energy | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_plant_total_generator_output_energy/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_total_generator_output_energy/state |Modbus Register 30224 ||
| Lifetime PV Production | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_plant_lifetime_pv_energy/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_lifetime_pv_energy/state |Modbus Register 30088 ||
| Lifetime Third-Party PV Production | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_third_party_pv_lifetime_production/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_third_party_pv_lifetime_production/state |Modbus Register 30196 ||
| Lifetime Total PV Production || kWh | 100 | sigenergy2mqtt/sigen_0_lifetime_pv_energy/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_lifetime_pv_energy/state |&sum; of PlantPVTotalGeneration and ThirdPartyLifetimePVEnergy||
| Max Active Power | 600s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_max_active_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_max_active_power/state |Modbus Register 30010 ||
| Max Apparent Power | 600s | kvar | 1000 | sigenergy2mqtt/sigen_0_plant_max_apparent_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_max_apparent_power/state |Modbus Register 30012 ||
| Max Charging Limit | 10s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_max_charging_limit/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_max_charging_limit/state |Modbus Register 40032 ||
| Max Discharging Limit | 10s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_max_discharging_limit/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_max_discharging_limit/state |Modbus Register 40034 ||
| PCS Alarms | 10s |  | 1 | sigenergy2mqtt/sigen_0_general_pcs_alarm/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_general_pcs_alarm/state |Modbus Registers 30027 and 30028||
| PCS Max Export Limit | 10s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_pcs_max_export_limit/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_pcs_max_export_limit/state |Modbus Register 40042 ||
| PCS Max Import Limit | 10s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_pcs_max_import_limit/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_pcs_max_import_limit/state |Modbus Register 40044 ||
| PV Max Power Limit | 10s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_pv_max_power_limit/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_pv_max_power_limit/state |Modbus Register 40036 ||
| PV Power | 5s | W | 1 | sigenergy2mqtt/sigen_0_plant_pv_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_pv_power/state |Modbus Register 30035 ||
| Phase A Active Power | 10s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_phase_a_active_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_phase_a_active_power/state |Modbus Register 30015 ||
| Phase A Active Power Fixed Adjustment Target Value | 60s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_phase_a_active_power_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_a_active_power_fixed_adjustment_target_value/state |Modbus Register 40008 ||
| Phase A Active Power Percentage Adjustment Target Value | 60s | % | 100 | sigenergy2mqtt/sigen_0_plant_phase_a_active_power_percentage_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_a_active_power_percentage_adjustment_target_value/state |Modbus Register 40020 ||
| Phase A Q/S Fixed Adjustment Target Value | 60s | % | 100 | sigenergy2mqtt/sigen_0_plant_phase_a_q_s_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_a_q_s_fixed_adjustment_target_value/state |Modbus Register 40023 ||
| Phase A Reactive Power | 10s | kvar | 1000 | sigenergy2mqtt/sigen_0_plant_phase_a_reactive_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_phase_a_reactive_power/state |Modbus Register 30021 ||
| Phase A Reactive Power Fixed Adjustment Target Value | 60s | kvar | 1000 | sigenergy2mqtt/sigen_0_plant_phase_a_reactive_power_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_a_reactive_power_fixed_adjustment_target_value/state |Modbus Register 40014 ||
| Phase B Active Power | 10s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_phase_b_active_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_phase_b_active_power/state |Modbus Register 30017 ||
| Phase B Active Power Fixed Adjustment Target Value | 60s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_phase_b_active_power_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_b_active_power_fixed_adjustment_target_value/state |Modbus Register 40010 ||
| Phase B Active Power Percentage Adjustment Target Value | 60s | % | 100 | sigenergy2mqtt/sigen_0_plant_phase_b_active_power_percentage_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_b_active_power_percentage_adjustment_target_value/state |Modbus Register 40021 ||
| Phase B Q/S Fixed Adjustment Target Value | 60s | % | 100 | sigenergy2mqtt/sigen_0_plant_phase_b_q_s_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_b_q_s_fixed_adjustment_target_value/state |Modbus Register 40024 ||
| Phase B Reactive Power | 10s | kvar | 1000 | sigenergy2mqtt/sigen_0_plant_phase_b_reactive_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_phase_b_reactive_power/state |Modbus Register 30023 ||
| Phase B Reactive Power Fixed Adjustment Target Value | 60s | kvar | 1000 | sigenergy2mqtt/sigen_0_plant_phase_b_reactive_power_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_b_reactive_power_fixed_adjustment_target_value/state |Modbus Register 40016 ||
| Phase C Active Power | 10s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_phase_c_active_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_phase_c_active_power/state |Modbus Register 30019 ||
| Phase C Active Power Fixed Adjustment Target Value | 60s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_phase_c_active_power_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_c_active_power_fixed_adjustment_target_value/state |Modbus Register 40012 ||
| Phase C Active Power Percentage Adjustment Target Value | 60s | % | 100 | sigenergy2mqtt/sigen_0_plant_phase_c_active_power_percentage_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_c_active_power_percentage_adjustment_target_value/state |Modbus Register 40022 ||
| Phase C Q/S Fixed Adjustment Target Value | 60s | % | 100 | sigenergy2mqtt/sigen_0_plant_phase_c_q_s_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_c_q_s_fixed_adjustment_target_value/state |Modbus Register 40025 ||
| Phase C Reactive Power | 10s | kvar | 1000 | sigenergy2mqtt/sigen_0_plant_phase_c_reactive_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_phase_c_reactive_power/state |Modbus Register 30025 ||
| Phase C Reactive Power Fixed Adjustment Target Value | 60s | kvar | 1000 | sigenergy2mqtt/sigen_0_plant_phase_c_reactive_power_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_c_reactive_power_fixed_adjustment_target_value/state |Modbus Register 40018 ||
| Power Factor Adjustment Target Value | 60s |  | 1000 | sigenergy2mqtt/sigen_0_plant_power_factor_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_power_factor_adjustment_target_value/state |Modbus Register 40007 ||
| Q/S Adjustment Target Value | 60s | % | 100 | sigenergy2mqtt/sigen_0_plant_q_s_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_q_s_adjustment_target_value/state |Modbus Register 40006 ||
| Rated Charging Power | 600s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_rated_charging_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_rated_charging_power/state |Modbus Register 30068 ||
| Rated Discharging Power | 600s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_rated_discharging_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_rated_discharging_power/state |Modbus Register 30070 ||
| Rated Energy Capacity | 600s | kWh | 100 | sigenergy2mqtt/sigen_0_plant_rated_energy_capacity/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_rated_energy_capacity/state |Modbus Register 30083 ||
| Reactive Power | 10s | kvar | 1000 | sigenergy2mqtt/sigen_0_plant_reactive_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_reactive_power/state |Modbus Register 30033 ||
| Reactive Power Fixed Adjustment Target Value | 60s | kvar | 1000 | sigenergy2mqtt/sigen_0_plant_reactive_power_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_reactive_power_fixed_adjustment_target_value/state |Modbus Register 40003 ||
| Remote EMS | 10s |  | 1 | sigenergy2mqtt/sigen_0_plant_remote_ems/state <br/> homeassistant/switch/sigen_0_247_powerplant/sigen_0_plant_remote_ems/state |Modbus Register 40029 ||
| Remote EMS Control Mode | 60s |  | 1 | sigenergy2mqtt/sigen_0_plant_remote_ems_control_mode/state <br/> homeassistant/select/sigen_0_247_powerplant/sigen_0_plant_remote_ems_control_mode/state |Modbus Register 40031 ||
| Running State | 10s |  | 1 | sigenergy2mqtt/sigen_0_plant_running_state/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_running_state/state |Modbus Register 30051 ||
| Smart Load 01 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_01_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_01_power/state |Modbus Register 30146 ||
| Smart Load 01 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_01_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_01_total_consumption/state |Modbus Register 30098 ||
| Smart Load 02 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_02_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_02_power/state |Modbus Register 30148 ||
| Smart Load 02 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_02_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_02_total_consumption/state |Modbus Register 30100 ||
| Smart Load 03 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_03_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_03_power/state |Modbus Register 30150 ||
| Smart Load 03 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_03_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_03_total_consumption/state |Modbus Register 30102 ||
| Smart Load 04 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_04_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_04_power/state |Modbus Register 30152 ||
| Smart Load 04 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_04_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_04_total_consumption/state |Modbus Register 30104 ||
| Smart Load 05 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_05_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_05_power/state |Modbus Register 30154 ||
| Smart Load 05 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_05_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_05_total_consumption/state |Modbus Register 30106 ||
| Smart Load 06 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_06_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_06_power/state |Modbus Register 30156 ||
| Smart Load 06 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_06_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_06_total_consumption/state |Modbus Register 30108 ||
| Smart Load 07 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_07_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_07_power/state |Modbus Register 30158 ||
| Smart Load 07 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_07_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_07_total_consumption/state |Modbus Register 30110 ||
| Smart Load 08 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_08_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_08_power/state |Modbus Register 30160 ||
| Smart Load 08 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_08_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_08_total_consumption/state |Modbus Register 30112 ||
| Smart Load 09 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_09_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_09_power/state |Modbus Register 30162 ||
| Smart Load 09 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_09_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_09_total_consumption/state |Modbus Register 30114 ||
| Smart Load 10 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_10_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_10_power/state |Modbus Register 30164 ||
| Smart Load 10 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_10_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_10_total_consumption/state |Modbus Register 30116 ||
| Smart Load 11 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_11_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_11_power/state |Modbus Register 30166 ||
| Smart Load 11 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_11_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_11_total_consumption/state |Modbus Register 30118 ||
| Smart Load 12 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_12_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_12_power/state |Modbus Register 30168 ||
| Smart Load 12 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_12_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_12_total_consumption/state |Modbus Register 30120 ||
| Smart Load 13 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_13_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_13_power/state |Modbus Register 30170 ||
| Smart Load 13 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_13_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_13_total_consumption/state |Modbus Register 30122 ||
| Smart Load 14 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_14_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_14_power/state |Modbus Register 30172 ||
| Smart Load 14 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_14_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_14_total_consumption/state |Modbus Register 30124 ||
| Smart Load 15 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_15_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_15_power/state |Modbus Register 30174 ||
| Smart Load 15 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_15_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_15_total_consumption/state |Modbus Register 30126 ||
| Smart Load 16 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_16_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_16_power/state |Modbus Register 30176 ||
| Smart Load 16 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_16_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_16_total_consumption/state |Modbus Register 30128 ||
| Smart Load 17 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_17_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_17_power/state |Modbus Register 30178 ||
| Smart Load 17 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_17_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_17_total_consumption/state |Modbus Register 30130 ||
| Smart Load 18 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_18_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_18_power/state |Modbus Register 30180 ||
| Smart Load 18 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_18_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_18_total_consumption/state |Modbus Register 30132 ||
| Smart Load 19 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_19_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_19_power/state |Modbus Register 30182 ||
| Smart Load 19 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_19_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_19_total_consumption/state |Modbus Register 30134 ||
| Smart Load 20 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_20_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_20_power/state |Modbus Register 30184 ||
| Smart Load 20 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_20_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_20_total_consumption/state |Modbus Register 30136 ||
| Smart Load 21 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_21_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_21_power/state |Modbus Register 30186 ||
| Smart Load 21 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_21_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_21_total_consumption/state |Modbus Register 30138 ||
| Smart Load 22 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_22_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_22_power/state |Modbus Register 30188 ||
| Smart Load 22 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_22_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_22_total_consumption/state |Modbus Register 30140 ||
| Smart Load 23 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_23_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_23_power/state |Modbus Register 30190 ||
| Smart Load 23 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_23_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_23_total_consumption/state |Modbus Register 30142 ||
| Smart Load 24 Power | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_24_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_24_power/state |Modbus Register 30192 ||
| Smart Load 24 Total Consumption | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_smart_load_24_total_consumption/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_smart_load_24_total_consumption/state |Modbus Register 30144 ||
| System Time | 60s |  | 1 | sigenergy2mqtt/sigen_0_plant_system_time/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_system_time/state |Modbus Register 30000 ||
| System Time Zone | 600s |  | 1 | sigenergy2mqtt/sigen_0_plant_system_time_zone/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_plant_system_time_zone/state |Modbus Register 30002 ||
| Third-Party PV Power | 5s | W | 1 | sigenergy2mqtt/sigen_0_third_party_pv_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_third_party_pv_power/state |Modbus Register 30194 ||
| Total PV Power || W | 1 | sigenergy2mqtt/sigen_0_total_pv_power/state <br/> homeassistant/sensor/sigen_0_247_powerplant/sigen_0_total_pv_power/state |PlantPVPower &plus; (PlantThirdPartyPVPower _or_ &sum; of all configured SmartPort MQTT sources and SmartPort modules)||

#### Grid Sensor
| Sensor Class | Interval | Unit | Gain | State Topic | Source | Applicable To |
|--------------|---------:|------|-----:|-------------|--------|---------------|
| Active Power | 5s | W | 1 | sigenergy2mqtt/sigen_0_plant_grid_sensor_active_power/state <br/> homeassistant/sensor/sigen_0_247_gridsensor/sigen_0_plant_grid_sensor_active_power/state |Modbus Register 30005 ||
| Daily Exported Energy || kWh | 100 | sigenergy2mqtt/sigen_0_grid_sensor_daily_export_energy/state <br/> homeassistant/sensor/sigen_0_247_gridsensor/sigen_0_grid_sensor_daily_export_energy/state |GridSensorLifetimeExportEnergy &minus; GridSensorLifetimeExportEnergy at last midnight||
| Daily Imported Energy || kWh | 100 | sigenergy2mqtt/sigen_0_grid_sensor_daily_import_energy/state <br/> homeassistant/sensor/sigen_0_247_gridsensor/sigen_0_grid_sensor_daily_import_energy/state |GridSensorLifetimeImportEnergy &minus; GridSensorLifetimeImportEnergy at last midnight||
| Export Power || W | 1 | sigenergy2mqtt/sigen_0_grid_sensor_export_power/state <br/> homeassistant/sensor/sigen_0_247_gridsensor/sigen_0_grid_sensor_export_power/state |GridSensorActivePower &lt; 0 &times; -1||
| Grid Sensor Status | 10s |  | 1 | sigenergy2mqtt/sigen_0_plant_grid_sensor_status/state <br/> homeassistant/sensor/sigen_0_247_gridsensor/sigen_0_plant_grid_sensor_status/state |Modbus Register 30004 ||
| Grid Status | 10s |  | 1 | sigenergy2mqtt/sigen_0_plant_grid_status/state <br/> homeassistant/sensor/sigen_0_247_gridsensor/sigen_0_plant_grid_status/state |Modbus Register 30009 ||
| Import Power || W | 1 | sigenergy2mqtt/sigen_0_grid_sensor_import_power/state <br/> homeassistant/sensor/sigen_0_247_gridsensor/sigen_0_grid_sensor_import_power/state |GridSensorActivePower &gt; 0||
| Lifetime Exported Energy | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_grid_sensor_lifetime_export_energy/state <br/> homeassistant/sensor/sigen_0_247_gridsensor/sigen_0_grid_sensor_lifetime_export_energy/state |Modbus Register 30220 ||
| Lifetime Imported Energy | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_grid_sensor_lifetime_import_energy/state <br/> homeassistant/sensor/sigen_0_247_gridsensor/sigen_0_grid_sensor_lifetime_import_energy/state |Modbus Register 30216 ||
| Phase A Active Power | 10s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_grid_phase_a_active_power/state <br/> homeassistant/sensor/sigen_0_247_gridsensor/sigen_0_plant_grid_phase_a_active_power/state |Modbus Register 30052 ||
| Phase A Reactive Power | 10s | kvar | 1000 | sigenergy2mqtt/sigen_0_plant_grid_phase_a_reactive_power/state <br/> homeassistant/sensor/sigen_0_247_gridsensor/sigen_0_plant_grid_phase_a_reactive_power/state |Modbus Register 30058 ||
| Phase B Active Power | 10s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_grid_phase_b_active_power/state <br/> homeassistant/sensor/sigen_0_247_gridsensor/sigen_0_plant_grid_phase_b_active_power/state |Modbus Register 30054 ||
| Phase B Reactive Power | 10s | kvar | 1000 | sigenergy2mqtt/sigen_0_plant_grid_phase_b_reactive_power/state <br/> homeassistant/sensor/sigen_0_247_gridsensor/sigen_0_plant_grid_phase_b_reactive_power/state |Modbus Register 30060 ||
| Phase C Active Power | 10s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_grid_phase_c_active_power/state <br/> homeassistant/sensor/sigen_0_247_gridsensor/sigen_0_plant_grid_phase_c_active_power/state |Modbus Register 30056 ||
| Phase C Reactive Power | 10s | kvar | 1000 | sigenergy2mqtt/sigen_0_plant_grid_phase_c_reactive_power/state <br/> homeassistant/sensor/sigen_0_247_gridsensor/sigen_0_plant_grid_phase_c_reactive_power/state |Modbus Register 30062 ||
| Reactive Power | 10s | var | 1 | sigenergy2mqtt/sigen_0_plant_grid_sensor_reactive_power/state <br/> homeassistant/sensor/sigen_0_247_gridsensor/sigen_0_plant_grid_sensor_reactive_power/state |Modbus Register 30007 ||

#### Smart-Port (Enphase Envoy only)
| Sensor Class | Interval | Unit | Gain | State Topic | Source | Applicable To |
|--------------|---------:|------|-----:|-------------|--------|---------------|
| Current || A | 1 | sigenergy2mqtt/sigen_0_enphase_123456789012_current/state <br/> homeassistant/sensor/sigen_0_enphase_envoy_123456789012/sigen_0_enphase_123456789012_current/state |Enphase Envoy API when EnphasePVPower derived||
| Daily Production || kWh | 1000 | sigenergy2mqtt/sigen_0_enphase_123456789012_daily_pv_energy/state <br/> homeassistant/sensor/sigen_0_enphase_envoy_123456789012/sigen_0_enphase_123456789012_daily_pv_energy/state |Enphase Envoy API when EnphasePVPower derived||
| Frequency || Hz | 1 | sigenergy2mqtt/sigen_0_enphase_123456789012_frequency/state <br/> homeassistant/sensor/sigen_0_enphase_envoy_123456789012/sigen_0_enphase_123456789012_frequency/state |Enphase Envoy API when EnphasePVPower derived||
| Lifetime Production || kWh | 1000 | sigenergy2mqtt/sigen_0_enphase_123456789012_lifetime_pv_energy/state <br/> homeassistant/sensor/sigen_0_enphase_envoy_123456789012/sigen_0_enphase_123456789012_lifetime_pv_energy/state |Enphase Envoy API when EnphasePVPower derived||
| PV Power | 5s | W | 1 | sigenergy2mqtt/sigen_0_enphase_123456789012_active_power/state <br/> homeassistant/sensor/sigen_0_enphase_envoy_123456789012/sigen_0_enphase_123456789012_active_power/state |Enphase Envoy API||
| Power Factor ||  | 1 | sigenergy2mqtt/sigen_0_enphase_123456789012_power_factor/state <br/> homeassistant/sensor/sigen_0_enphase_envoy_123456789012/sigen_0_enphase_123456789012_power_factor/state |Enphase Envoy API when EnphasePVPower derived||
| Reactive Power || kvar | 1000 | sigenergy2mqtt/sigen_0_enphase_123456789012_reactive_power/state <br/> homeassistant/sensor/sigen_0_enphase_envoy_123456789012/sigen_0_enphase_123456789012_reactive_power/state |Enphase Envoy API when EnphasePVPower derived||
| Voltage || V | 1 | sigenergy2mqtt/sigen_0_enphase_123456789012_voltage/state <br/> homeassistant/sensor/sigen_0_enphase_envoy_123456789012/sigen_0_enphase_123456789012_voltage/state |Enphase Envoy API when EnphasePVPower derived||

#### Statistics

After upgrading the device firmware to support the new Statistics Interface, the register values will reset to 0 and start fresh counting _without_ inheriting historical data.
| Sensor Class | Interval | Unit | Gain | State Topic | Source | Applicable To |
|--------------|---------:|------|-----:|-------------|--------|---------------|
| Total AC EV Charge Energy | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_si_total_ev_ac_charged_energy/state <br/> homeassistant/sensor/sigen_0_247_plantstatistics/sigen_0_si_total_ev_ac_charged_energy/state |Modbus Register 30232 ||
| Total Charge Energy | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_si_total_charged_energy/state <br/> homeassistant/sensor/sigen_0_247_plantstatistics/sigen_0_si_total_charged_energy/state |Modbus Register 30244 ||
| Total Common Load Consumption | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_si_total_common_load_consumption/state <br/> homeassistant/sensor/sigen_0_247_plantstatistics/sigen_0_si_total_common_load_consumption/state |Modbus Register 30228 ||
| Total DC EV Charge Energy | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_si_evdc_total_charge_energy/state <br/> homeassistant/sensor/sigen_0_247_plantstatistics/sigen_0_si_evdc_total_charge_energy/state |Modbus Register 30252 ||
| Total DC EV Discharge Energy | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_si_evdc_total_discharge_energy/state <br/> homeassistant/sensor/sigen_0_247_plantstatistics/sigen_0_si_evdc_total_discharge_energy/state |Modbus Register 30256 ||
| Total Discharge Energy | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_si_total_discharged_energy/state <br/> homeassistant/sensor/sigen_0_247_plantstatistics/sigen_0_si_total_discharged_energy/state |Modbus Register 30248 ||
| Total Exported Energy | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_si_total_exported_energy/state <br/> homeassistant/sensor/sigen_0_247_plantstatistics/sigen_0_si_total_exported_energy/state |Modbus Register 30264 ||
| Total Generator Output Energy | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_si_total_generator_output_energy/state <br/> homeassistant/sensor/sigen_0_247_plantstatistics/sigen_0_si_total_generator_output_energy/state |Modbus Register 30268 ||
| Total Imported Energy | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_si_total_imported_energy/state <br/> homeassistant/sensor/sigen_0_247_plantstatistics/sigen_0_si_total_imported_energy/state |Modbus Register 30260 ||
| Total PV Production | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_si_total_self_pv_generation/state <br/> homeassistant/sensor/sigen_0_247_plantstatistics/sigen_0_si_total_self_pv_generation/state |Modbus Register 30236 ||
| Total Third-Party PV Production | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_si_total_third_party_pv_generation/state <br/> homeassistant/sensor/sigen_0_247_plantstatistics/sigen_0_si_total_third_party_pv_generation/state |Modbus Register 30240 ||

### Inverter
| Sensor Class | Interval | Unit | Gain | State Topic | Source | Applicable To |
|--------------|---------:|------|-----:|-------------|--------|---------------|
| A-B Line Voltage | 60s | V | 100 | sigenergy2mqtt/sigen_0_inverter_1_a_b_line_voltage/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_a_b_line_voltage/state |Modbus Register 31005 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Active Power | 5s | kW | 1000 | sigenergy2mqtt/sigen_0_inverter_1_active_power/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_active_power/state |Modbus Register 30587 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Active Power Fixed Value Adjustment | 60s | kW | 1000 | sigenergy2mqtt/sigen_0_inverter_1_active_power_fixed_value_adjustment/state <br/> homeassistant/number/sigen_0_001_inverter/sigen_0_inverter_1_active_power_fixed_value_adjustment/state |Modbus Register 41501 | PV&nbsp;Inverter |
| Active Power Fixed Value Adjustment Feedback | 60s | kW | 1000 | sigenergy2mqtt/sigen_0_inverter_1_active_power_fixed_value_adjustment_feedback/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_active_power_fixed_value_adjustment_feedback/state |Modbus Register 30613 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Active Power Percentage Adjustment | 60s | % | 100 | sigenergy2mqtt/sigen_0_inverter_1_active_power_percentage_adjustment/state <br/> homeassistant/number/sigen_0_001_inverter/sigen_0_inverter_1_active_power_percentage_adjustment/state |Modbus Register 41505 | PV&nbsp;Inverter |
| Active Power Percentage Adjustment Feedback | 60s | % | 100 | sigenergy2mqtt/sigen_0_inverter_1_active_power_percentage_adjustment_feedback/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_active_power_percentage_adjustment_feedback/state |Modbus Register 30617 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| B-C Line Voltage | 60s | V | 100 | sigenergy2mqtt/sigen_0_inverter_1_b_c_line_voltage/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_b_c_line_voltage/state |Modbus Register 31007 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| C-A Line Voltage | 60s | V | 100 | sigenergy2mqtt/sigen_0_inverter_1_c_a_line_voltage/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_c_a_line_voltage/state |Modbus Register 31009 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Daily Production | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_inverter_1_daily_pv_energy/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_daily_pv_energy/state |Modbus Register 31509 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Firmware Version | 600s |  |  | sigenergy2mqtt/sigen_0_inverter_1_firmware_version/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_firmware_version/state |Modbus Register 30525 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Gateway Alarms | 10s |  | 1 | sigenergy2mqtt/sigen_0_inverter_1_alarm_4/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_alarm_4/state |Modbus Register 30608 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Grid Frequency | 10s | Hz | 100 | sigenergy2mqtt/sigen_0_inverter_1_grid_frequency/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_grid_frequency/state |Modbus Register 31002 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Insulation Resistance | 60s | MΩ | 1000 | sigenergy2mqtt/sigen_0_inverter_1_insulation_resistance/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_insulation_resistance/state |Modbus Register 31037 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Lifetime Production | 60s | kWh | 100 | sigenergy2mqtt/sigen_0_inverter_1_lifetime_pv_energy/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_lifetime_pv_energy/state |Modbus Register 31511 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| MPTT Count | 600s |  | 1 | sigenergy2mqtt/sigen_0_inverter_1_mptt_count/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_mptt_count/state |Modbus Register 31026 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Max Absorption Power | 600s | kW | 1000 | sigenergy2mqtt/sigen_0_inverter_1_max_absorption_power/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_max_absorption_power/state |Modbus Register 30546 | Hybrid&nbsp;Inverter |
| Max Active Power | 600s | kW | 1000 | sigenergy2mqtt/sigen_0_inverter_1_max_active_power/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_max_active_power/state |Modbus Register 30544 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Max Active Power Adjustment | 600s | kW | 1000 | sigenergy2mqtt/sigen_0_inverter_1_max_active_power_adjustment/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_max_active_power_adjustment/state |Modbus Register 30579 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Max Rated Apparent Power | 600s | kVA | 1000 | sigenergy2mqtt/sigen_0_inverter_1_max_rated_apparent_power/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_max_rated_apparent_power/state |Modbus Register 30542 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Max Reactive Power Adjustment | 600s | kvar | 1000 | sigenergy2mqtt/sigen_0_inverter_1_max_reactive_power_adjustment/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_max_reactive_power_adjustment/state |Modbus Register 30583 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Min Active Power Adjustment | 600s | kW | 1000 | sigenergy2mqtt/sigen_0_inverter_1_min_active_power_adjustment/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_min_active_power_adjustment/state |Modbus Register 30581 | Hybrid&nbsp;Inverter |
| Min Reactive Power Adjustment | 600s | kvar | 1000 | sigenergy2mqtt/sigen_0_inverter_1_min_reactive_power_adjustment/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_min_reactive_power_adjustment/state |Modbus Register 30585 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Output Type | 600s |  | 1 | sigenergy2mqtt/sigen_0_inverter_1_output_type/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_output_type/state |Modbus Register 31004 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| PACK/BCU Count | 60s |  | 1 | sigenergy2mqtt/sigen_0_inverter_1_pack_bcu_count/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_pack_bcu_count/state |Modbus Register 31024 | Hybrid&nbsp;Inverter |
| PCS Alarms | 10s |  | 1 | sigenergy2mqtt/sigen_0_inverter_1_pcs_alarm/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_pcs_alarm/state |Modbus Registers 30605 and 30606| Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| PV Power | 10s | W | 1 | sigenergy2mqtt/sigen_0_inverter_1_pv_power/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_pv_power/state |Modbus Register 31035 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| PV String Count | 600s |  | 1 | sigenergy2mqtt/sigen_0_inverter_1_pv_string_count/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_pv_string_count/state |Modbus Register 31025 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Phase A Current | 60s | A | 100 | sigenergy2mqtt/sigen_0_inverter_1_phase_a_current/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_phase_a_current/state |Modbus Register 31017 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Phase A Voltage | 60s | V | 100 | sigenergy2mqtt/sigen_0_inverter_1_phase_a_voltage/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_phase_a_voltage/state |Modbus Register 31011 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Phase B Current | 60s | A | 100 | sigenergy2mqtt/sigen_0_inverter_1_phase_b_current/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_phase_b_current/state |Modbus Register 31019 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Phase B Voltage | 60s | V | 100 | sigenergy2mqtt/sigen_0_inverter_1_phase_b_voltage/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_phase_b_voltage/state |Modbus Register 31013 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Phase C Current | 60s | A | 100 | sigenergy2mqtt/sigen_0_inverter_1_phase_c_current/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_phase_c_current/state |Modbus Register 31021 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Phase C Voltage | 60s | V | 100 | sigenergy2mqtt/sigen_0_inverter_1_phase_c_voltage/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_phase_c_voltage/state |Modbus Register 31015 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Power Factor | 10s |  | 1000 | sigenergy2mqtt/sigen_0_inverter_1_power_factor/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_power_factor/state |Modbus Register 31023 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Power Factor Adjustment | 60s |  | 1000 | sigenergy2mqtt/sigen_0_inverter_1_power_factor_adjustment/state <br/> homeassistant/number/sigen_0_001_inverter/sigen_0_inverter_1_power_factor_adjustment/state |Modbus Register 41507 | PV&nbsp;Inverter |
| Rated Active Power | 600s | kW | 1000 | sigenergy2mqtt/sigen_0_inverter_1_rated_active_power/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_rated_active_power/state |Modbus Register 30540 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Rated Grid Frequency | 600s | Hz | 100 | sigenergy2mqtt/sigen_0_inverter_1_rated_grid_frequency/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_rated_grid_frequency/state |Modbus Register 31001 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Rated Grid Voltage | 600s | V | 10 | sigenergy2mqtt/sigen_0_inverter_1_rated_grid_voltage/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_rated_grid_voltage/state |Modbus Register 31000 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Reactive Power | 10s | kvar | 1000 | sigenergy2mqtt/sigen_0_inverter_1_reactive_power/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_reactive_power/state |Modbus Register 30589 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Reactive Power Fixed Value Adjustment | 60s | kvar | 1000 | sigenergy2mqtt/sigen_0_inverter_1_reactive_power_fixed_value_adjustment/state <br/> homeassistant/number/sigen_0_001_inverter/sigen_0_inverter_1_reactive_power_fixed_value_adjustment/state |Modbus Register 41503 | PV&nbsp;Inverter |
| Reactive Power Fixed Value Adjustment Feedback | 60s | kvar | 1000 | sigenergy2mqtt/sigen_0_inverter_1_reactive_power_fixed_value_adjustment_feedback/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_reactive_power_fixed_value_adjustment_feedback/state |Modbus Register 30615 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Reactive Power Percentage Adjustment Feedback | 60s | % | 100 | sigenergy2mqtt/sigen_0_inverter_1_reactive_power_percentage_adjustment_feedback/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_reactive_power_percentage_adjustment_feedback/state |Modbus Register 30618 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Reactive Power Q/S Adjustment | 60s | % | 100 | sigenergy2mqtt/sigen_0_inverter_1_reactive_power_q_s_adjustment/state <br/> homeassistant/number/sigen_0_001_inverter/sigen_0_inverter_1_reactive_power_q_s_adjustment/state |Modbus Register 41506 | PV&nbsp;Inverter |
| Remote EMS Dispatch | 10s |  | 1 | sigenergy2mqtt/sigen_0_inverter_1_remote_ems_dispatch/state <br/> homeassistant/switch/sigen_0_001_inverter/sigen_0_inverter_1_remote_ems_dispatch/state |Modbus Register 41500 | PV&nbsp;Inverter |
| Running State | 10s |  | 1 | sigenergy2mqtt/sigen_0_inverter_1_running_state/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_running_state/state |Modbus Register 30578 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Shutdown Time | 600s |  | 1 | sigenergy2mqtt/sigen_0_inverter_1_shutdown_time/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_shutdown_time/state |Modbus Register 31040 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Startup Time | 600s |  | 1 | sigenergy2mqtt/sigen_0_inverter_1_startup_time/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_startup_time/state |Modbus Register 31038 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Temperature | 60s | °C | 10 | sigenergy2mqtt/sigen_0_inverter_1_temperature/state <br/> homeassistant/sensor/sigen_0_001_inverter/sigen_0_inverter_1_temperature/state |Modbus Register 31003 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |

#### Energy Storage System
| Sensor Class | Interval | Unit | Gain | State Topic | Source | Applicable To |
|--------------|---------:|------|-----:|-------------|--------|---------------|
| Alarms | 10s |  | 1 | sigenergy2mqtt/sigen_0_inverter_1_alarm_3/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_alarm_3/state |Modbus Register 30607 | Hybrid&nbsp;Inverter |
| Available Charge Energy | 600s | kWh | 100 | sigenergy2mqtt/sigen_0_inverter_1_available_battery_charge_energy/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_available_battery_charge_energy/state |Modbus Register 30595 | Hybrid&nbsp;Inverter |
| Available Discharge Energy | 600s | kWh | 100 | sigenergy2mqtt/sigen_0_inverter_1_available_battery_discharge_energy/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_available_battery_discharge_energy/state |Modbus Register 30597 | Hybrid&nbsp;Inverter |
| Average Cell Temperature | 10s | °C | 10 | sigenergy2mqtt/sigen_0_inverter_1_average_cell_temperature/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_average_cell_temperature/state |Modbus Register 30603 | Hybrid&nbsp;Inverter |
| Average Cell Voltage | 10s | V | 1000 | sigenergy2mqtt/sigen_0_inverter_1_average_cell_voltage/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_average_cell_voltage/state |Modbus Register 30604 | Hybrid&nbsp;Inverter |
| Battery Charging Power || W | 1 | sigenergy2mqtt/sigen_0_inverter_1_battery_charging_power/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_battery_charging_power/state |ChargeDischargePower &gt; 0||
| Battery Discharging Power || W | 1 | sigenergy2mqtt/sigen_0_inverter_1_battery_discharging_power/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_battery_discharging_power/state |ChargeDischargePower &lt; 0 &times; -1||
| Battery Power | 5s | W | 1 | sigenergy2mqtt/sigen_0_inverter_1_charge_discharge_power/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_charge_discharge_power/state |Modbus Register 30599 | Hybrid&nbsp;Inverter |
| Battery SoC | 60s | % | 10 | sigenergy2mqtt/sigen_0_inverter_1_battery_soc/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_battery_soc/state |Modbus Register 30601 | Hybrid&nbsp;Inverter |
| Battery SoH | 60s | % | 10 | sigenergy2mqtt/sigen_0_inverter_1_battery_soh/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_battery_soh/state |Modbus Register 30602 | Hybrid&nbsp;Inverter |
| Daily Charge Energy | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_inverter_1_daily_charge_energy/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_daily_charge_energy/state |Modbus Register 30566 | Hybrid&nbsp;Inverter |
| Daily Discharge Energy | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_inverter_1_daily_discharge_energy/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_daily_discharge_energy/state |Modbus Register 30572 | Hybrid&nbsp;Inverter |
| Lifetime Charge Energy | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_inverter_1_accumulated_charge_energy/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_accumulated_charge_energy/state |Modbus Register 30568 | Hybrid&nbsp;Inverter |
| Lifetime Discharge Energy | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_inverter_1_accumulated_discharge_energy/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_accumulated_discharge_energy/state |Modbus Register 30574 | Hybrid&nbsp;Inverter |
| Max Battery Temperature | 60s | °C | 10 | sigenergy2mqtt/sigen_0_inverter_1_max_battery_temperature/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_max_battery_temperature/state |Modbus Register 30620 | Hybrid&nbsp;Inverter |
| Max Charge Power | 600s | kW | 1000 | sigenergy2mqtt/sigen_0_inverter_1_max_battery_charge_power/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_max_battery_charge_power/state |Modbus Register 30591 | Hybrid&nbsp;Inverter |
| Max Discharge Power | 600s | kW | 1000 | sigenergy2mqtt/sigen_0_inverter_1_max_battery_discharge_power/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_max_battery_discharge_power/state |Modbus Register 30593 | Hybrid&nbsp;Inverter |
| Min Battery Temperature | 60s | °C | 10 | sigenergy2mqtt/sigen_0_inverter_1_min_battery_temperature/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_min_battery_temperature/state |Modbus Register 30621 | Hybrid&nbsp;Inverter |
| Rated Battery Capacity | 600s | kWh | 100 | sigenergy2mqtt/sigen_0_inverter_1_rated_battery_capacity/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_rated_battery_capacity/state |Modbus Register 30548 | Hybrid&nbsp;Inverter |
| Rated Charging Power | 600s | kW | 1000 | sigenergy2mqtt/sigen_0_inverter_1_rated_charging_power/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_rated_charging_power/state |Modbus Register 30550 | Hybrid&nbsp;Inverter |
| Rated Discharging Power | 600s | kW | 1000 | sigenergy2mqtt/sigen_0_inverter_1_rated_discharging_power/state <br/> homeassistant/sensor/sigen_0_001_ess/sigen_0_inverter_1_rated_discharging_power/state |Modbus Register 30552 | Hybrid&nbsp;Inverter |

#### PV String
| Sensor Class | Interval | Unit | Gain | State Topic | Source | Applicable To |
|--------------|---------:|------|-----:|-------------|--------|---------------|
| Current | 10s | A | 100 | sigenergy2mqtt/sigen_0_inverter_1_pv1_current/state <br/> homeassistant/sensor/sigen_0_001_pvstring1/sigen_0_inverter_1_pv1_current/state |Modbus Register 31028 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Current | 10s | A | 100 | sigenergy2mqtt/sigen_0_inverter_1_pv2_current/state <br/> homeassistant/sensor/sigen_0_001_pvstring2/sigen_0_inverter_1_pv2_current/state |Modbus Register 31030 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Current | 10s | A | 100 | sigenergy2mqtt/sigen_0_inverter_1_pv3_current/state <br/> homeassistant/sensor/sigen_0_001_pvstring3/sigen_0_inverter_1_pv3_current/state |Modbus Register 31032 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Current | 10s | A | 100 | sigenergy2mqtt/sigen_0_inverter_1_pv4_current/state <br/> homeassistant/sensor/sigen_0_001_pvstring4/sigen_0_inverter_1_pv4_current/state |Modbus Register 31034 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Current | 10s | A | 100 | sigenergy2mqtt/sigen_0_inverter_1_pv5_current/state <br/> homeassistant/sensor/sigen_0_001_pvstring5/sigen_0_inverter_1_pv5_current/state |Modbus Register 31043 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Current | 10s | A | 100 | sigenergy2mqtt/sigen_0_inverter_1_pv6_current/state <br/> homeassistant/sensor/sigen_0_001_pvstring6/sigen_0_inverter_1_pv6_current/state |Modbus Register 31045 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Current | 10s | A | 100 | sigenergy2mqtt/sigen_0_inverter_1_pv7_current/state <br/> homeassistant/sensor/sigen_0_001_pvstring7/sigen_0_inverter_1_pv7_current/state |Modbus Register 31047 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Current | 10s | A | 100 | sigenergy2mqtt/sigen_0_inverter_1_pv8_current/state <br/> homeassistant/sensor/sigen_0_001_pvstring8/sigen_0_inverter_1_pv8_current/state |Modbus Register 31049 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Current | 10s | A | 100 | sigenergy2mqtt/sigen_0_inverter_1_pv9_current/state <br/> homeassistant/sensor/sigen_0_001_pvstring9/sigen_0_inverter_1_pv9_current/state |Modbus Register 31051 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Current | 10s | A | 100 | sigenergy2mqtt/sigen_0_inverter_1_pv10_current/state <br/> homeassistant/sensor/sigen_0_001_pvstring10/sigen_0_inverter_1_pv10_current/state |Modbus Register 31053 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Current | 10s | A | 100 | sigenergy2mqtt/sigen_0_inverter_1_pv11_current/state <br/> homeassistant/sensor/sigen_0_001_pvstring11/sigen_0_inverter_1_pv11_current/state |Modbus Register 31055 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Current | 10s | A | 100 | sigenergy2mqtt/sigen_0_inverter_1_pv12_current/state <br/> homeassistant/sensor/sigen_0_001_pvstring12/sigen_0_inverter_1_pv12_current/state |Modbus Register 31057 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Current | 10s | A | 100 | sigenergy2mqtt/sigen_0_inverter_1_pv13_current/state <br/> homeassistant/sensor/sigen_0_001_pvstring13/sigen_0_inverter_1_pv13_current/state |Modbus Register 31059 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Current | 10s | A | 100 | sigenergy2mqtt/sigen_0_inverter_1_pv14_current/state <br/> homeassistant/sensor/sigen_0_001_pvstring14/sigen_0_inverter_1_pv14_current/state |Modbus Register 31061 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Current | 10s | A | 100 | sigenergy2mqtt/sigen_0_inverter_1_pv15_current/state <br/> homeassistant/sensor/sigen_0_001_pvstring15/sigen_0_inverter_1_pv15_current/state |Modbus Register 31063 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Current | 10s | A | 100 | sigenergy2mqtt/sigen_0_inverter_1_pv16_current/state <br/> homeassistant/sensor/sigen_0_001_pvstring16/sigen_0_inverter_1_pv16_current/state |Modbus Register 31065 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Daily Production || kWh | 1000 | sigenergy2mqtt/sigen_0_inverter_1_pv1_daily_energy/state <br/> homeassistant/sensor/sigen_0_001_pvstring1/sigen_0_inverter_1_pv1_daily_energy/state |PVStringLifetimeEnergy &minus; PVStringLifetimeEnergy at last midnight||
| Lifetime Production || kWh | 1000 | sigenergy2mqtt/sigen_0_inverter_1_pv1_lifetime_energy/state <br/> homeassistant/sensor/sigen_0_001_pvstring1/sigen_0_inverter_1_pv1_lifetime_energy/state |Riemann &sum; of PVStringPower||
| Power || W | 1 | sigenergy2mqtt/sigen_0_inverter_1_pv1_power/state <br/> homeassistant/sensor/sigen_0_001_pvstring1/sigen_0_inverter_1_pv1_power/state |PVVoltageSensor &times; PVCurrentSensor||
| Voltage | 10s | V | 10 | sigenergy2mqtt/sigen_0_inverter_1_pv1_voltage/state <br/> homeassistant/sensor/sigen_0_001_pvstring1/sigen_0_inverter_1_pv1_voltage/state |Modbus Register 31027 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Voltage | 10s | V | 10 | sigenergy2mqtt/sigen_0_inverter_1_pv2_voltage/state <br/> homeassistant/sensor/sigen_0_001_pvstring2/sigen_0_inverter_1_pv2_voltage/state |Modbus Register 31029 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Voltage | 10s | V | 10 | sigenergy2mqtt/sigen_0_inverter_1_pv3_voltage/state <br/> homeassistant/sensor/sigen_0_001_pvstring3/sigen_0_inverter_1_pv3_voltage/state |Modbus Register 31031 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Voltage | 10s | V | 10 | sigenergy2mqtt/sigen_0_inverter_1_pv4_voltage/state <br/> homeassistant/sensor/sigen_0_001_pvstring4/sigen_0_inverter_1_pv4_voltage/state |Modbus Register 31033 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Voltage | 10s | V | 10 | sigenergy2mqtt/sigen_0_inverter_1_pv5_voltage/state <br/> homeassistant/sensor/sigen_0_001_pvstring5/sigen_0_inverter_1_pv5_voltage/state |Modbus Register 31042 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Voltage | 10s | V | 10 | sigenergy2mqtt/sigen_0_inverter_1_pv6_voltage/state <br/> homeassistant/sensor/sigen_0_001_pvstring6/sigen_0_inverter_1_pv6_voltage/state |Modbus Register 31044 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Voltage | 10s | V | 10 | sigenergy2mqtt/sigen_0_inverter_1_pv7_voltage/state <br/> homeassistant/sensor/sigen_0_001_pvstring7/sigen_0_inverter_1_pv7_voltage/state |Modbus Register 31046 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Voltage | 10s | V | 10 | sigenergy2mqtt/sigen_0_inverter_1_pv8_voltage/state <br/> homeassistant/sensor/sigen_0_001_pvstring8/sigen_0_inverter_1_pv8_voltage/state |Modbus Register 31048 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Voltage | 10s | V | 10 | sigenergy2mqtt/sigen_0_inverter_1_pv9_voltage/state <br/> homeassistant/sensor/sigen_0_001_pvstring9/sigen_0_inverter_1_pv9_voltage/state |Modbus Register 31050 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Voltage | 10s | V | 10 | sigenergy2mqtt/sigen_0_inverter_1_pv10_voltage/state <br/> homeassistant/sensor/sigen_0_001_pvstring10/sigen_0_inverter_1_pv10_voltage/state |Modbus Register 31052 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Voltage | 10s | V | 10 | sigenergy2mqtt/sigen_0_inverter_1_pv11_voltage/state <br/> homeassistant/sensor/sigen_0_001_pvstring11/sigen_0_inverter_1_pv11_voltage/state |Modbus Register 31054 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Voltage | 10s | V | 10 | sigenergy2mqtt/sigen_0_inverter_1_pv12_voltage/state <br/> homeassistant/sensor/sigen_0_001_pvstring12/sigen_0_inverter_1_pv12_voltage/state |Modbus Register 31056 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Voltage | 10s | V | 10 | sigenergy2mqtt/sigen_0_inverter_1_pv13_voltage/state <br/> homeassistant/sensor/sigen_0_001_pvstring13/sigen_0_inverter_1_pv13_voltage/state |Modbus Register 31058 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Voltage | 10s | V | 10 | sigenergy2mqtt/sigen_0_inverter_1_pv14_voltage/state <br/> homeassistant/sensor/sigen_0_001_pvstring14/sigen_0_inverter_1_pv14_voltage/state |Modbus Register 31060 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Voltage | 10s | V | 10 | sigenergy2mqtt/sigen_0_inverter_1_pv15_voltage/state <br/> homeassistant/sensor/sigen_0_001_pvstring15/sigen_0_inverter_1_pv15_voltage/state |Modbus Register 31062 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Voltage | 10s | V | 10 | sigenergy2mqtt/sigen_0_inverter_1_pv16_voltage/state <br/> homeassistant/sensor/sigen_0_001_pvstring16/sigen_0_inverter_1_pv16_voltage/state |Modbus Register 31064 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |

### AC Charger
| Sensor Class | Interval | Unit | Gain | State Topic | Source | Applicable To |
|--------------|---------:|------|-----:|-------------|--------|---------------|
| AC Charger Charging Power | 10s | kW | 1000 | sigenergy2mqtt/sigen_0_ac_charger_3_rated_charging_power/state <br/> homeassistant/sensor/sigen_0_003_accharger/sigen_0_ac_charger_3_rated_charging_power/state |Modbus Register 32003 ||
| AC Charger Input Breaker | 600s | A | 100 | sigenergy2mqtt/sigen_0_ac_charger_3_input_breaker/state <br/> homeassistant/sensor/sigen_0_003_accharger/sigen_0_ac_charger_3_input_breaker/state |Modbus Register 32010 ||
| AC Charger Rated Current | 600s | A | 100 | sigenergy2mqtt/sigen_0_ac_charger_3_rated_current/state <br/> homeassistant/sensor/sigen_0_003_accharger/sigen_0_ac_charger_3_rated_current/state |Modbus Register 32007 ||
| AC Charger Rated Power | 600s | kW | 1000 | sigenergy2mqtt/sigen_0_ac_charger_3_rated_power/state <br/> homeassistant/sensor/sigen_0_003_accharger/sigen_0_ac_charger_3_rated_power/state |Modbus Register 32005 ||
| AC Charger Rated Voltage | 600s | V | 10 | sigenergy2mqtt/sigen_0_ac_charger_3_rated_voltage/state <br/> homeassistant/sensor/sigen_0_003_accharger/sigen_0_ac_charger_3_rated_voltage/state |Modbus Register 32009 ||
| AC Charger Running State | 10s |  | 1 | sigenergy2mqtt/sigen_0_ac_charger_3_running_state/state <br/> homeassistant/sensor/sigen_0_003_accharger/sigen_0_ac_charger_3_running_state/state |Modbus Register 32000 ||
| AC Charger Total Energy Consumed | 10s | kWh | 100 | sigenergy2mqtt/sigen_0_ac_charger_3_total_energy_consumed/state <br/> homeassistant/sensor/sigen_0_003_accharger/sigen_0_ac_charger_3_total_energy_consumed/state |Modbus Register 32001 ||
| Alarms | 10s |  | 1 | sigenergy2mqtt/sigen_0_ac_charger_3_alarm/state <br/> homeassistant/sensor/sigen_0_003_accharger/sigen_0_ac_charger_3_alarm/state |Modbus Registers 32012, 32013, and 32014||
| Output Current | 60s | A | 100 | sigenergy2mqtt/sigen_0_ac_charger_3_output_current/state <br/> homeassistant/number/sigen_0_003_accharger/sigen_0_ac_charger_3_output_current/state |Modbus Register 42001 ||

### DC Charger
| Sensor Class | Interval | Unit | Gain | State Topic | Source | Applicable To |
|--------------|---------:|------|-----:|-------------|--------|---------------|
| Alarms | 10s |  | 1 | sigenergy2mqtt/sigen_0_inverter_2_alarm_5/state <br/> homeassistant/sensor/sigen_0_002_dccharger/sigen_0_inverter_2_alarm_5/state |Modbus Register 30609 ||
| DC Charger Current Charging Capacity | 600s | kWh | 100 | sigenergy2mqtt/sigen_0_plant_dc_charger_current_charging_capacity/state <br/> homeassistant/sensor/sigen_0_002_dccharger/sigen_0_plant_dc_charger_current_charging_capacity/state |Modbus Register 31505 ||
| DC Charger Current Charging Duration | 600s | s | 1 | sigenergy2mqtt/sigen_0_plant_dc_charger_current_charging_duration/state <br/> homeassistant/sensor/sigen_0_002_dccharger/sigen_0_plant_dc_charger_current_charging_duration/state |Modbus Register 31507 ||
| DC Charger Output Power | 10s | kW | 1000 | sigenergy2mqtt/sigen_0_plant_dc_charger_output_power/state <br/> homeassistant/sensor/sigen_0_002_dccharger/sigen_0_plant_dc_charger_output_power/state |Modbus Register 31502 ||
| Vehicle Battery Voltage | 10s | V | 10 | sigenergy2mqtt/sigen_0_plant_vehicle_battery_voltage/state <br/> homeassistant/sensor/sigen_0_002_dccharger/sigen_0_plant_vehicle_battery_voltage/state |Modbus Register 31500 ||
| Vehicle Charging Current | 10s | A | 10 | sigenergy2mqtt/sigen_0_plant_vehicle_charging_current/state <br/> homeassistant/sensor/sigen_0_002_dccharger/sigen_0_plant_vehicle_charging_current/state |Modbus Register 31501 ||
| Vehicle SoC | 60s | % | 10 | sigenergy2mqtt/sigen_0_plant_vehicle_soc/state <br/> homeassistant/sensor/sigen_0_002_dccharger/sigen_0_plant_vehicle_soc/state |Modbus Register 31504 ||

### Metrics

Metrics are _only_ published to the sigenergy2mqtt/metrics topics, even when Home Assistant discovery is enabled. The scan interval cannot be altered.
| Metric | Interval | Unit | State Topic |
|--------|---------:|------|-------------|
| Modbus Active Locks | 1 |  | sigenergy2mqtt/metrics/modbus_locks |
| Modbus Read Errors | 1 |  | sigenergy2mqtt/metrics/modbus_read_errors |
| Modbus Read Max | 1 | ms | sigenergy2mqtt/metrics/modbus_read_max |
| Modbus Read Mean | 1 | ms | sigenergy2mqtt/metrics/modbus_read_mean |
| Modbus Read Min | 1 | ms | sigenergy2mqtt/metrics/modbus_read_min |
| Modbus Reads/second | 1 |  | sigenergy2mqtt/metrics/modbus_reads_sec |
| Modbus Write Errors | 1 |  | sigenergy2mqtt/metrics/modbus_write_errors |
| Modbus Write Max | 1 | ms | sigenergy2mqtt/metrics/modbus_write_max |
| Modbus Write Mean | 1 | ms | sigenergy2mqtt/metrics/modbus_write_mean |
| Modbus Write Min | 1 | ms | sigenergy2mqtt/metrics/modbus_write_min |
| Protocol Published | 1 |  | sigenergy2mqtt/metrics/modbus_protocol_published |
| Protocol Version | 1 |  | sigenergy2mqtt/metrics/modbus_protocol |
| Started | 1 |  | sigenergy2mqtt/metrics/started |

## Subscribed Topics

### Plant
| Sensor Class | Command Topic | Target | Applicable To |
|--------------|---------------|--------|---------------|
| Active Power Fixed Adjustment Target Value | sigenergy2mqtt/sigen_0_plant_active_power_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_active_power_fixed_adjustment_target_value/set | Modbus Register 40001 ||
| Active Power Percentage Adjustment Target Value | sigenergy2mqtt/sigen_0_plant_active_power_percentage_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_active_power_percentage_adjustment_target_value/set | Modbus Register 40005 ||
| Backup SoC | sigenergy2mqtt/sigen_0_plant_ess_backup_soc/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_ess_backup_soc/set | Modbus Register 40046 ||
| Charge Cut-Off SoC | sigenergy2mqtt/sigen_0_plant_ess_charge_cut_off_soc/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_ess_charge_cut_off_soc/set | Modbus Register 40047 ||
| Discharge Cut-Off SoC | sigenergy2mqtt/sigen_0_plant_ess_discharge_cut_off_soc/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_ess_discharge_cut_off_soc/set | Modbus Register 40048 ||
| Grid Max Export Limit | sigenergy2mqtt/sigen_0_plant_grid_max_export_limit/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_grid_max_export_limit/set | Modbus Register 40038 ||
| Grid Max Import Limit | sigenergy2mqtt/sigen_0_plant_grid_max_import_limit/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_grid_max_import_limit/set | Modbus Register 40040 ||
| Independent Phase Power Control | sigenergy2mqtt/sigen_0_plant_independent_phase_power_control/state <br/> homeassistant/switch/sigen_0_247_powerplant/sigen_0_plant_independent_phase_power_control/set | Modbus Register 40030 ||
| Max Charging Limit | sigenergy2mqtt/sigen_0_plant_max_charging_limit/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_max_charging_limit/set | Modbus Register 40032 ||
| Max Discharging Limit | sigenergy2mqtt/sigen_0_plant_max_discharging_limit/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_max_discharging_limit/set | Modbus Register 40034 ||
| PCS Max Export Limit | sigenergy2mqtt/sigen_0_plant_pcs_max_export_limit/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_pcs_max_export_limit/set | Modbus Register 40042 ||
| PCS Max Import Limit | sigenergy2mqtt/sigen_0_plant_pcs_max_import_limit/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_pcs_max_import_limit/set | Modbus Register 40044 ||
| PV Max Power Limit | sigenergy2mqtt/sigen_0_plant_pv_max_power_limit/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_pv_max_power_limit/set | Modbus Register 40036 ||
| Phase A Active Power Fixed Adjustment Target Value | sigenergy2mqtt/sigen_0_plant_phase_a_active_power_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_a_active_power_fixed_adjustment_target_value/set | Modbus Register 40008 ||
| Phase A Active Power Percentage Adjustment Target Value | sigenergy2mqtt/sigen_0_plant_phase_a_active_power_percentage_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_a_active_power_percentage_adjustment_target_value/set | Modbus Register 40020 ||
| Phase A Q/S Fixed Adjustment Target Value | sigenergy2mqtt/sigen_0_plant_phase_a_q_s_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_a_q_s_fixed_adjustment_target_value/set | Modbus Register 40023 ||
| Phase A Reactive Power Fixed Adjustment Target Value | sigenergy2mqtt/sigen_0_plant_phase_a_reactive_power_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_a_reactive_power_fixed_adjustment_target_value/set | Modbus Register 40014 ||
| Phase B Active Power Fixed Adjustment Target Value | sigenergy2mqtt/sigen_0_plant_phase_b_active_power_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_b_active_power_fixed_adjustment_target_value/set | Modbus Register 40010 ||
| Phase B Active Power Percentage Adjustment Target Value | sigenergy2mqtt/sigen_0_plant_phase_b_active_power_percentage_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_b_active_power_percentage_adjustment_target_value/set | Modbus Register 40021 ||
| Phase B Q/S Fixed Adjustment Target Value | sigenergy2mqtt/sigen_0_plant_phase_b_q_s_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_b_q_s_fixed_adjustment_target_value/set | Modbus Register 40024 ||
| Phase B Reactive Power Fixed Adjustment Target Value | sigenergy2mqtt/sigen_0_plant_phase_b_reactive_power_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_b_reactive_power_fixed_adjustment_target_value/set | Modbus Register 40016 ||
| Phase C Active Power Fixed Adjustment Target Value | sigenergy2mqtt/sigen_0_plant_phase_c_active_power_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_c_active_power_fixed_adjustment_target_value/set | Modbus Register 40012 ||
| Phase C Active Power Percentage Adjustment Target Value | sigenergy2mqtt/sigen_0_plant_phase_c_active_power_percentage_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_c_active_power_percentage_adjustment_target_value/set | Modbus Register 40022 ||
| Phase C Q/S Fixed Adjustment Target Value | sigenergy2mqtt/sigen_0_plant_phase_c_q_s_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_c_q_s_fixed_adjustment_target_value/set | Modbus Register 40025 ||
| Phase C Reactive Power Fixed Adjustment Target Value | sigenergy2mqtt/sigen_0_plant_phase_c_reactive_power_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_phase_c_reactive_power_fixed_adjustment_target_value/set | Modbus Register 40018 ||
| Power On/Off | sigenergy2mqtt/sigen_0_plant_status/state <br/> homeassistant/button/sigen_0_247_powerplant/sigen_0_plant_status/set | Modbus Register 40000 ||
| Power Factor Adjustment Target Value | sigenergy2mqtt/sigen_0_plant_power_factor_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_power_factor_adjustment_target_value/set | Modbus Register 40007 ||
| Q/S Adjustment Target Value | sigenergy2mqtt/sigen_0_plant_q_s_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_q_s_adjustment_target_value/set | Modbus Register 40006 ||
| Reactive Power Fixed Adjustment Target Value | sigenergy2mqtt/sigen_0_plant_reactive_power_fixed_adjustment_target_value/state <br/> homeassistant/number/sigen_0_247_powerplant/sigen_0_plant_reactive_power_fixed_adjustment_target_value/set | Modbus Register 40003 ||
| Remote EMS | sigenergy2mqtt/sigen_0_plant_remote_ems/state <br/> homeassistant/switch/sigen_0_247_powerplant/sigen_0_plant_remote_ems/set | Modbus Register 40029 ||
| Remote EMS Control Mode | sigenergy2mqtt/sigen_0_plant_remote_ems_control_mode/state <br/> homeassistant/select/sigen_0_247_powerplant/sigen_0_plant_remote_ems_control_mode/set | Modbus Register 40031 ||

### Inverter
| Sensor Class | Command Topic | Target | Applicable To |
|--------------|---------------|--------|---------------|
| Active Power Fixed Value Adjustment | sigenergy2mqtt/sigen_0_inverter_1_active_power_fixed_value_adjustment/state <br/> homeassistant/number/sigen_0_001_inverter/sigen_0_inverter_1_active_power_fixed_value_adjustment/set | Modbus Register 41501 | PV&nbsp;Inverter |
| Active Power Percentage Adjustment | sigenergy2mqtt/sigen_0_inverter_1_active_power_percentage_adjustment/state <br/> homeassistant/number/sigen_0_001_inverter/sigen_0_inverter_1_active_power_percentage_adjustment/set | Modbus Register 41505 | PV&nbsp;Inverter |
| Power On/Off | sigenergy2mqtt/sigen_0_inverter_1_status/state <br/> homeassistant/button/sigen_0_001_inverter/sigen_0_inverter_1_status/set | Modbus Register 40500 | Hybrid&nbsp;Inverter <br/> PV&nbsp;Inverter |
| Power Factor Adjustment | sigenergy2mqtt/sigen_0_inverter_1_power_factor_adjustment/state <br/> homeassistant/number/sigen_0_001_inverter/sigen_0_inverter_1_power_factor_adjustment/set | Modbus Register 41507 | PV&nbsp;Inverter |
| Reactive Power Fixed Value Adjustment | sigenergy2mqtt/sigen_0_inverter_1_reactive_power_fixed_value_adjustment/state <br/> homeassistant/number/sigen_0_001_inverter/sigen_0_inverter_1_reactive_power_fixed_value_adjustment/set | Modbus Register 41503 | PV&nbsp;Inverter |
| Reactive Power Q/S Adjustment | sigenergy2mqtt/sigen_0_inverter_1_reactive_power_q_s_adjustment/state <br/> homeassistant/number/sigen_0_001_inverter/sigen_0_inverter_1_reactive_power_q_s_adjustment/set | Modbus Register 41506 | PV&nbsp;Inverter |
| Remote EMS Dispatch | sigenergy2mqtt/sigen_0_inverter_1_remote_ems_dispatch/state <br/> homeassistant/switch/sigen_0_001_inverter/sigen_0_inverter_1_remote_ems_dispatch/set | Modbus Register 41500 | PV&nbsp;Inverter |

### AC Charger
| Sensor Class | Command Topic | Target | Applicable To |
|--------------|---------------|--------|---------------|
| Output Current | sigenergy2mqtt/sigen_0_ac_charger_3_output_current/state <br/> homeassistant/number/sigen_0_003_accharger/sigen_0_ac_charger_3_output_current/set | Modbus Register 42001 ||
| Power On/Off | sigenergy2mqtt/sigen_0_ac_charger_3_status/state <br/> homeassistant/button/sigen_0_003_accharger/sigen_0_ac_charger_3_status/set | Modbus Register 42000 ||

### DC Charger
| Sensor Class | Command Topic | Target | Applicable To |
|--------------|---------------|--------|---------------|
| DC Charger Status | sigenergy2mqtt/sigen_0_dc_charger_2_status/state <br/> homeassistant/button/sigen_0_002_dccharger/sigen_0_dc_charger_2_status/set | Modbus Register 41000 ||
