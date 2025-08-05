import numpy as np
from pynwb import NWBHDF5IO
from pynwb.testing.mock.file import mock_NWBFile
from pynwb.testing.mock.base import mock_TimeSeries
from unittest import TestCase

from ndx_franklab_novela import FrankLabOptogeneticEpochsTable, CameraDevice


class TestFrankLabOptogeneticsEpochsTable(TestCase):

    def test_roundtrip(self):
        nwbfile = mock_NWBFile()

        stimulus = mock_TimeSeries()
        nwbfile.add_stimulus(stimulus)

        camera1 = CameraDevice(
            name="overhead_run_camera 1",
            description="Camera used for tracking running",
            meters_per_pixel=0.20,
            camera_name="test name",
            model="ndx2000",
            lens="500dpt",
            manufacturer="sony",
            frame_rate=30.0,
        )
        nwbfile.add_device(camera1)

        camera2 = CameraDevice(
            name="overhead_run_camera 2",
            description="Camera used for tracking running",
            meters_per_pixel=0.20,
            camera_name="test name",
            model="ndx2000",
            lens="500dpt",
            manufacturer="sony",
            frame_rate=30.0,
        )
        nwbfile.add_device(camera2)

        opto_epochs = FrankLabOptogeneticEpochsTable(
            name="optogenetic_epochs",
            description="Metadata about the optogenetic stimulation parameters that change per epoch.",
        )

        # test add one epoch
        opto_epochs.add_row(
            start_time=0.0,
            stop_time=100.0,
            stimulation_on=True,
            power_in_mW=100.0,
            pulse_length_in_ms=40.0,
            period_in_ms=250.0,
            number_pulses_per_pulse_train=100,
            number_trains=1,
            intertrain_interval_in_ms=0.0,
            epoch_name="20220911_Wallie_01_sleep",
            epoch_number=1,
            convenience_code="a1",
            epoch_type="sleep",
            theta_filter_on=True,
            theta_filter_lockout_period_in_samples=10,
            theta_filter_phase_in_deg=180.0,
            theta_filter_reference_ntrode=1,
            spatial_filter_on=True,
            spatial_filter_lockout_period_in_samples=10,
            spatial_filter_region_node_coordinates_in_pixels=((260, 920), (800, 1050)),
            spatial_filter_cameras=[camera1, camera2],
            spatial_filter_cameras_cm_per_pixel=[0.3, 0.18],
            ripple_filter_on=True,
            ripple_filter_lockout_period_in_samples=10,
            ripple_filter_threshold_sd=5.0,
            ripple_filter_num_above_threshold=4,
            speed_filter_on=True,
            speed_filter_threshold_in_cm_per_s=10.0,
            speed_filter_on_above_threshold=True,
            stimulus_signal=stimulus,
        )
        nwbfile.add_time_intervals(opto_epochs)

        # write the NWBFile to disk
        path = "test_optogenetics.nwb"
        with NWBHDF5IO(path, mode="w") as io:
            io.write(nwbfile)

        # read the NWBFile from disk
        with NWBHDF5IO(path, mode="r") as io:
            read_nwbfile = io.read()

            read_camera1 = read_nwbfile.devices["overhead_run_camera 1"]
            read_camera2 = read_nwbfile.devices["overhead_run_camera 2"]

            read_epochs = read_nwbfile.intervals["optogenetic_epochs"]
            assert read_epochs[0, "start_time"] == 0.0
            assert read_epochs[0, "stop_time"] == 100.0
            assert read_epochs[0, "stimulation_on"]
            assert read_epochs[0, "power_in_mW"] == 100.0
            assert read_epochs[0, "pulse_length_in_ms"] == 40.0
            assert read_epochs[0, "period_in_ms"] == 250.0
            assert read_epochs[0, "number_pulses_per_pulse_train"] == 100
            assert read_epochs[0, "number_trains"] == 1
            assert read_epochs[0, "intertrain_interval_in_ms"] == 0.0
            assert read_epochs[0, "epoch_name"] == "20220911_Wallie_01_sleep"
            assert read_epochs[0, "epoch_number"] == 1
            assert read_epochs[0, "convenience_code"] == "a1"
            assert read_epochs[0, "epoch_type"] == "sleep"
            assert read_epochs[0, "theta_filter_on"]
            assert read_epochs[0, "theta_filter_lockout_period_in_samples"] == 10
            assert read_epochs[0, "theta_filter_phase_in_deg"] == 180.0
            assert read_epochs[0, "theta_filter_reference_ntrode"] == 1
            assert read_epochs[0, "spatial_filter_on"]
            assert read_epochs[0, "spatial_filter_lockout_period_in_samples"] == 10
            assert np.array_equal(
                read_epochs[0, "spatial_filter_region_node_coordinates_in_pixels"],
                np.array([[260, 920], [800, 1050]]),
            )
            assert read_epochs[0, "spatial_filter_cameras"] == [read_camera1, read_camera2]
            assert all(read_epochs[0, "spatial_filter_cameras_cm_per_pixel"] == [0.3, 0.18])
            assert read_epochs[0, "ripple_filter_on"]
            assert read_epochs[0, "ripple_filter_lockout_period_in_samples"] == 10
            assert read_epochs[0, "ripple_filter_threshold_sd"] == 5.0
            assert read_epochs[0, "ripple_filter_num_above_threshold"] == 4
            assert read_epochs[0, "speed_filter_on"]
            assert read_epochs[0, "speed_filter_threshold_in_cm_per_s"] == 10.0
            assert read_epochs[0, "speed_filter_on_above_threshold"]
            assert read_epochs[0, "stimulus_signal"].object_id == stimulus.object_id
