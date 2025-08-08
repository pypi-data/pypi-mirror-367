import unittest
from unittest.mock import patch, MagicMock, call
import numpy as np
import plotly.graph_objects as go
from astropy.table import Table
from astropy.time import Time

# make sure to put in root directory
from astroView.main import AsteroidVisualizer

# fake data production
def get_mock_horizons_vectors():
    """Returns a mock data table for Horizons vectors call."""
    return Table({
        'x': np.array([-1.5, -1.4]),
        'y': np.array([2.5, 2.6]),
        'z': np.array([0.5, 0.4]),
        'targetname': ['1 Ceres', '1 Ceres'],
        'datetime_jd': [2460676.5, 2460677.5]
    })

def get_mock_horizons_ephemerides_sun():
    """Returns a mock data table for Horizons ephemerides call for the Sun."""
    return Table({
        'EL': np.array([30.0]),  # Altitude
        'AZ': np.array([120.0]), # Azimuth
        'targetname': ['Sun (Sol)'],
        'datetime_str': ['2025-Aug-05 10:00']
    })

def get_mock_horizons_ephemerides_moon():
    """Returns a mock data table for Horizons ephemerides call for the Moon."""
    return Table({
        'EL': np.array([-15.0]), # Altitude (below horizon)
        'AZ': np.array([280.0]), # Azimuth
        'targetname': ['Moon'],
        'datetime_str': ['2025-Aug-05 10:00']
    })


class TestAsteroidVisualizerUnit(unittest.TestCase):
    """
    Unit tests for the AsteroidVisualizer class.
    These tests use mocking to isolate the class from external dependencies
    like file I/O and network requests.
    """

    @patch('astroView.main.Loader')
    def setUp(self, MockLoader):
        """
        Set up a fresh instance of AsteroidVisualizer for each test.
        This method is called before every single test function in this class.
        """
        # We mock the Loader to avoid actual file system access during unit tests
        self.mock_loader_instance = MockLoader.return_value
        self.mock_loader_instance.timescale.return_value = "mock_timescale"
        self.visualizer = AsteroidVisualizer()

    @patch('astroView.main.Horizons')
    def test_get_heliocentric_position(self, MockHorizons):
        """
        Unit test for the get_heliocentric_position method.
        """
        print("\nRunning test: test_get_heliocentric_position")
        # Arrange: Configure the mock to return our fake data
        mock_horizons_instance = MockHorizons.return_value
        mock_horizons_instance.vectors.return_value = get_mock_horizons_vectors()

        # Act: Call the method we are testing
        dates_utc = [(2025, 1, 1), (2025, 1, 2)]
        x, y, z = self.visualizer.get_heliocentric_position('Ceres', dates_utc)

        # Assert: Check that the results are what we expect
        self.assertIsInstance(x, np.ndarray)
        self.assertEqual(len(x), 2)
        np.testing.assert_array_equal(x, np.array([-1.5, -1.4]))
        np.testing.assert_array_equal(y, np.array([2.5, 2.6]))
        np.testing.assert_array_equal(z, np.array([0.5, 0.4]))
        print("... PASSED")

    @patch('astroView.main.load')
    @patch('astroView.main.Horizons')
    def test_plot_heliocentric_orbits_3d(self, MockHorizons, mock_skyfield_load):
        """
        Unit test for the plot_heliocentric_orbits_3D method.
        It checks if the Plotly figure is generated correctly.
        """
        print("\nRunning test: test_plot_heliocentric_orbits_3d")
        # Arrange: Set up mocks for both Horizons and Skyfield
        mock_horizons_instance = MockHorizons.return_value
        mock_horizons_instance.vectors.return_value = get_mock_horizons_vectors()

        # Act: Call the method
        fig = self.visualizer.plot_heliocentric_orbits_3D(object_id='Ceres')

        # Assert: Check the generated figure object
        self.assertIsInstance(fig, go.Figure)
        # We expect 5 traces: Earth Orbit, Ceres Orbit, Sun, Earth Start, Ceres Start
        self.assertEqual(len(fig.data), 5)
        trace_names = [trace.name for trace in fig.data]
        self.assertIn('Earth Orbit', trace_names)
        self.assertIn('Ceres Orbit', trace_names)
        self.assertIn('Sun', trace_names)
        self.assertIn('Earth (Start of Year)', trace_names)
        self.assertIn('Ceres (Start of Year)', trace_names)
        
        # Check that the Sun is plotted at the origin
        sun_trace = fig.data[2]
        self.assertEqual(sun_trace.x[0], 0)
        self.assertEqual(sun_trace.y[0], 0)
        self.assertEqual(sun_trace.z[0], 0)
        print("... PASSED")

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.subplots')
    @patch('astroView.main.Horizons')
    def test_visualize_skyview(self, MockHorizons, mock_subplots, mock_plt_show):
        """
        Unit test for the visualize_skyview method.
        It checks if the plotting logic correctly separates objects
        above and below the horizon.
        """
        print("\nRunning test: test_visualize_skyview")
        # Arrange: We need to return different mock data depending on the object
        # being queried. We use `side_effect` for this.
        def horizons_side_effect(*args, **kwargs):
            mock_instance = MagicMock()
            if kwargs.get('id') == 'Sun':
                mock_instance.ephemerides.return_value = get_mock_horizons_ephemerides_sun()
            elif kwargs.get('id') == 'Moon':
                mock_instance.ephemerides.return_value = get_mock_horizons_ephemerides_moon()
            return mock_instance

        MockHorizons.side_effect = horizons_side_effect

        # Arrange: Mock the subplot to capture plot calls
        mock_ax_sky = MagicMock()
        mock_ax_ground = MagicMock()
        mock_subplots.return_value = (MagicMock(), (mock_ax_sky, mock_ax_ground))

        # Act: Call the method
        self.visualizer.visualize_skyview(['Sun', 'Moon'])

        # Assert: Check that the correct plot calls were made
        # The Sun (altitude > 0) should be plotted on the 'sky' axis
        mock_ax_sky.plot.assert_called_once()
        # The Moon (altitude < 0) should be plotted on the 'ground' axis
        mock_ax_ground.plot.assert_called_once()
        
        # We can even check the arguments of the plot call for the Sun
        args, kwargs = mock_ax_sky.plot.call_args
        az_rad_sun = np.deg2rad(120.0)
        radius_sun = 90 - 30.0
        self.assertAlmostEqual(args[0], az_rad_sun)
        self.assertAlmostEqual(args[1], radius_sun)
        self.assertEqual(kwargs['label'], 'Sun')
        
        # And for the Moon
        args, kwargs = mock_ax_ground.plot.call_args
        az_rad_moon = np.deg2rad(280.0)
        radius_moon = 90 - abs(-15.0)
        self.assertAlmostEqual(args[0], az_rad_moon)
        self.assertAlmostEqual(args[1], radius_moon)
        self.assertEqual(kwargs['label'], 'Moon')
        
        # Assert that plt.show() was called to display the plot
        mock_plt_show.assert_called_once()
        print("... PASSED")


# The 'skip' decorator is used to prevent these tests from running by default.


@unittest.skip("Skipping End-to-End tests. Uncomment to run.")
class TestAsteroidVisualizerE2E(unittest.TestCase):
    """
    End-to-End (E2E) tests for the AsteroidVisualizer.
    These tests make REAL network calls to JPL Horizons to ensure
    the full workflow is functioning correctly.
    """
    def setUp(self):
        """Set up a real instance of the visualizer."""
        self.visualizer = AsteroidVisualizer()

    def test_e2e_plot_heliocentric_orbits_3d(self):
        """
        E2E test that fetches real data for Ceres and generates a plot.
        This test will fail if there is no internet connection or if the
        JPL Horizons service is unavailable.
        """
        print("\nRunning E2E test: test_e2e_plot_heliocentric_orbits_3d")
        try:
            # We use a very short time range to make the test faster.
            fig = self.visualizer.plot_heliocentric_orbits_3D(
                object_id='Ceres',
                start='2025-01-01',
                stop='2025-01-10',
                step='1d'
            )
            self.assertIsInstance(fig, go.Figure)
            self.assertEqual(len(fig.data), 5)
            print("... PASSED")
        except Exception as e:
            self.fail(f"E2E test for plotting failed with exception: {e}")

    @patch('matplotlib.pyplot.show')
    def test_e2e_visualize_skyview(self, mock_plt_show):
        """
        E2E test that fetches real sky positions for the Sun and Moon.
        """
        print("\nRunning E2E test: test_e2e_visualize_skyview")
        try:
            # We call the function and just check that it runs without error.
            self.visualizer.visualize_skyview(
                objects=['Sun', 'Moon'],
                obs_time_utc='2025-08-05 10:00'
            )
            # Check that show was called, indicating the plot was generated.
            mock_plt_show.assert_called_once()
            print("... PASSED")
        except Exception as e:
            self.fail(f"E2E test for sky view failed with exception: {e}")


if __name__ == '__main__':
    # This allows you to run the tests by executing the script directly
    # e.g., python test_asteroid_visualizer.py
    unittest.main()

