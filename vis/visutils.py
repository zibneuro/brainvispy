import vtk
import math

def map_to_blue_red_rgb(value):
  tanh_value = math.tanh(value)
    
  # Compute the hue
  if tanh_value <= 0.0:
    hue = 0.6 # blue
  else:
    hue = 0.0 # red
  # Compute the saturation
  sat = abs(tanh_value)

  # Convert to RGB
  return vtk.vtkMath.HSVToRGB((hue, sat, 1.0))
