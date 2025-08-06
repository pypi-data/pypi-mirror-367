from shadow4.beamline.s4_beamline import S4Beamline

beamline = S4Beamline()

#
#
#
from shadow4.sources.source_geometrical.source_geometrical import SourceGeometrical

light_source = SourceGeometrical(name='SourceGeometrical', nrays=5000, seed=5676561)
light_source.set_spatial_type_gaussian(sigma_h=0.000279, sigma_v=0.000015)
light_source.set_depth_distribution_off()
light_source.set_angular_distribution_gaussian(sigdix=0.000021, sigdiz=0.000018)
light_source.set_energy_distribution_uniform(value_min=999.800000, value_max=1000.200000, unit='eV')
light_source.set_polarization(polarization_degree=1.000000, phase_diff=0.000000, coherent_beam=0)
beam = light_source.get_beam()

beamline.set_light_source(light_source)

# optical element number XX
boundary_shape = None

from shadow4.beamline.optical_elements.mirrors.s4_plane_mirror import S4PlaneMirror

optical_element = S4PlaneMirror(name='Plane Mirror', boundary_shape=boundary_shape,
                                f_reflec=0, f_refl=0, file_refl='<none>', refraction_index=0.99999 + 0.001j,
                                coating_material='Si', coating_density=2.33, coating_roughness=0)

from syned.beamline.element_coordinates import ElementCoordinates

coordinates = ElementCoordinates(p=1, q=1, angle_radial=1.54985, angle_azimuthal=0, angle_radial_out=1.54985)
movements = None
from shadow4.beamline.optical_elements.mirrors.s4_plane_mirror import S4PlaneMirrorElement

beamline_element = S4PlaneMirrorElement(optical_element=optical_element, coordinates=coordinates, movements=movements,
                                        input_beam=beam)

beam, mirr = beamline_element.trace_beam()

beamline.append_beamline_element(beamline_element)

# optical element number XX
boundary_shape = None
from shadow4.beamline.optical_elements.gratings.s4_plane_grating import S4PlaneGrating

optical_element = S4PlaneGrating(name='Plane Grating',
                                 boundary_shape=None, f_ruling=1, order=1,
                                 ruling=800000.0, ruling_coeff_linear=0.0,
                                 ruling_coeff_quadratic=0.0, ruling_coeff_cubic=0.0,
                                 ruling_coeff_quartic=0.0,
                                 )
from syned.beamline.element_coordinates import ElementCoordinates

coordinates = ElementCoordinates(p=30, q=9.93427, angle_radial=1.52359, angle_azimuthal=0, angle_radial_out=1.55517)
from shadow4.beamline.s4_beamline_element_movements import S4BeamlineElementMovements

movements = S4BeamlineElementMovements(f_move=1, offset_x=0, offset_y=0, offset_z=0, rotation_x=0, rotation_y=0,
                                       rotation_z=0)
from shadow4.beamline.optical_elements.gratings.s4_plane_grating import S4PlaneGratingElement

beamline_element = S4PlaneGratingElement(optical_element=optical_element, coordinates=coordinates, movements=movements,
                                         input_beam=beam)

beam, footprint = beamline_element.trace_beam()

beamline.append_beamline_element(beamline_element)

# optical element number XX
from shadow4.beamline.optical_elements.crystals.s4_plane_crystal import S4PlaneCrystal

optical_element = S4PlaneCrystal(name='Plane Crystal',
                                 boundary_shape=None, material='Si',
                                 miller_index_h=1, miller_index_k=1, miller_index_l=1,
                                 f_bragg_a=False, asymmetry_angle=0.0,
                                 is_thick=1, thickness=0.001,
                                 f_central=1, f_phot_cent=0, phot_cent=5000.0,
                                 file_refl='bragg.dat',
                                 f_ext=0,
                                 material_constants_library_flag=0,
                                 # 0=xraylib,1=dabax,2=preprocessor v1,3=preprocessor v2
                                 )
from syned.beamline.element_coordinates import ElementCoordinates

coordinates = ElementCoordinates(p=1, q=1, angle_radial=1.54985, angle_azimuthal=0, angle_radial_out=1.48353)
movements = None
from shadow4.beamline.optical_elements.crystals.s4_plane_crystal import S4PlaneCrystalElement

beamline_element = S4PlaneCrystalElement(optical_element=optical_element, coordinates=coordinates, movements=movements,
                                         input_beam=beam)

beam, mirr = beamline_element.trace_beam()

beamline.append_beamline_element(beamline_element)

# test plot
if 0:
    from srxraylib.plot.gol import plot_scatter

    plot_scatter(beam.get_photon_energy_eV(nolost=1), beam.get_column(23, nolost=1), title='(Intensity,Photon Energy)',
                 plot_histograms=0)
    plot_scatter(1e6 * beam.get_column(1, nolost=1), 1e6 * beam.get_column(3, nolost=1), title='(X,Z) in microns')

print(">>>>>>>>>>>>>>>>", optical_element.get_surface_shape(), optical_element.get_surface_shape_instance())
print(beamline.oeinfo())