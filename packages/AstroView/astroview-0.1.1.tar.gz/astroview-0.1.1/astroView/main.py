from skyfield.api import load, Loader
from astroquery.jplhorizons import Horizons
from astropy.time import Time
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt

class AsteroidVisualizer:
    def __init__(self):
        self.loader = Loader('./skyfield_data')
        self.eph = self.loader('de421.bsp')
        self.sun = self.eph['sun']
        self.earth = self.eph['earth']
        self.ts = self.loader.timescale()

    def get_heliocentric_position(self, target_name, dates_utc, id_type='smallbody'):
      jd_times = [Time(f"{y}-{m:02d}-{d:02d}", format='iso', scale='utc').jd for (y, m, d) in dates_utc]
      obj = Horizons(id=target_name, location='500', epochs=jd_times, id_type=id_type)
      eph = obj.vectors()
      return eph['x'], eph['y'], eph['z']

    def plot_heliocentric_orbits_3D(self, object_id='Ceres', start='2025-01-01', stop='2025-12-31', step='1d'):
      # Query Horizons for object ephemerides
      obj = Horizons(id=object_id, location='@sun',
                    epochs={'start': start, 'stop': stop, 'step': step})
      obj_vectors = obj.vectors()
      
      # Load ephemeris and timescale
      eph = load('de421.bsp')
      earth = eph['earth']
      sun = eph['sun']
      ts = load.timescale()

      # Generate time range
      start_year = int(start[:4])
      start_month = int(start[5:7])
      start_day = int(start[8:10])
      num_days = len(obj_vectors)  # based on queried data
      days = ts.utc(start_year, start_month, range(start_day, start_day + num_days))

      # Earth's heliocentric orbit (reverse vector)
      pos = earth.at(days).observe(sun).apparent().position.au
      x, y, z = -pos[0], -pos[1], -pos[2]
      x0, y0, z0 = x[0], y[0], z[0]

      # Object heliocentric orbit (reverse vector)
      x2, y2, z2 = -obj_vectors['x'], -obj_vectors['y'], -obj_vectors['z']
      x02, y02, z02 = x2[0], y2[0], z2[0]

      # Plot
      fig = go.Figure()

      fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', name='Earth Orbit'))
      fig.add_trace(go.Scatter3d(x=x2, y=y2, z=z2, mode='lines', name=f'{object_id} Orbit'))

      fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0],
                                mode='markers',
                                marker=dict(size=6, color='yellow'),
                                name='Sun'))

      fig.add_trace(go.Scatter3d(x=[x0], y=[y0], z=[z0],
                                mode='markers',
                                marker=dict(size=6, color='blue', symbol='circle'),
                                name='Earth (Start of Year)'))

      fig.add_trace(go.Scatter3d(x=[x02], y=[y02], z=[z02],
                                mode='markers',
                                marker=dict(size=6, color='red', symbol='circle'),
                                name=f'{object_id} (Start of Year)'))

      fig.update_layout(
          scene=dict(
              xaxis_title='X (AU)',
              yaxis_title='Y (AU)',
              zaxis_title='Z (AU)',
              aspectmode='data'
          ),
          title=f'Orbit Around the Sun: Earth and {object_id}',
          margin=dict(l=0, r=0, b=0, t=30)
      )

      #fig.show()
      return fig

    def visualize_skyview(self, objects, obs_code='500', obs_time_utc='2025-08-05 10:00'):
        t_astropy = Time(obs_time_utc)
        epoch_jd = t_astropy.jd

        positions = {}
        for obj in objects:
            horizons_obj = Horizons(id=obj, location=obs_code, epochs=epoch_jd)
            eph = horizons_obj.ephemerides()
            positions[obj] = (eph['EL'][0], eph['AZ'][0])  # Altitude, Azimuth

        fig, (ax_sky, ax_ground) = plt.subplots(1, 2, figsize=(12, 6), subplot_kw=dict(polar=True))
        fig.suptitle(f"Sky View from Observatory {obs_code} – {t_astropy.iso}", fontsize=14)

        for ax, title, bgcolor in zip([ax_sky, ax_ground], ["Above Horizon", "Below Horizon"], ['#f5faff', '#eaeaea']):
            ax.set_theta_zero_location('N')
            ax.set_theta_direction(-1)
            ax.set_rlim(0, 90)
            ax.set_title(title)
            ax.set_facecolor(bgcolor)
            ax.plot(np.linspace(0, 2 * np.pi, 500), [90]*500, color='gray', linestyle='--', linewidth=0.5)
            ax.set_rlabel_position(135)

        colors = {'Sun': 'orange', '301': 'gray'}
        for obj, (alt, az) in positions.items():
            az_rad = np.deg2rad(az)
            radius = 90 - abs(alt)
            color = colors.get(obj, 'red')  # Default: red
            if alt >= 0:
                ax_sky.plot(az_rad, radius, 'o', color=color, label=obj)
            else:
                ax_ground.plot(az_rad, radius, 'o', color=color, label=obj)

        ax_sky.legend(loc='lower left')
        ax_ground.legend(loc='lower left')
        plt.tight_layout()
        plt.show()