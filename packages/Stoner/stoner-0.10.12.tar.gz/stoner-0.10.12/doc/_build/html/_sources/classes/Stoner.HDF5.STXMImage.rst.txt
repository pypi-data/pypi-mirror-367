STXMImage
=========

.. currentmodule:: Stoner.HDF5

.. autoclass:: STXMImage
   :show-inheritance:

   .. rubric:: Attributes Summary

   .. autosummary::

      ~STXMImage.CCW
      ~STXMImage.CW
      ~STXMImage.T
      ~STXMImage.aspect
      ~STXMImage.base
      ~STXMImage.baseclass
      ~STXMImage.centre
      ~STXMImage.clone
      ~STXMImage.ctypes
      ~STXMImage.data
      ~STXMImage.debug
      ~STXMImage.device
      ~STXMImage.draw
      ~STXMImage.dtype
      ~STXMImage.filename
      ~STXMImage.fill_value
      ~STXMImage.flags
      ~STXMImage.flat
      ~STXMImage.flip_h
      ~STXMImage.flip_v
      ~STXMImage.fmts
      ~STXMImage.hardmask
      ~STXMImage.imag
      ~STXMImage.image
      ~STXMImage.itemset
      ~STXMImage.itemsize
      ~STXMImage.mT
      ~STXMImage.mask
      ~STXMImage.max_box
      ~STXMImage.metadata
      ~STXMImage.mime_type
      ~STXMImage.nbytes
      ~STXMImage.ndim
      ~STXMImage.newbyteorder
      ~STXMImage.polarization
      ~STXMImage.priority
      ~STXMImage.real
      ~STXMImage.recordmask
      ~STXMImage.shape
      ~STXMImage.sharedmask
      ~STXMImage.size
      ~STXMImage.strides
      ~STXMImage.title

   .. rubric:: Methods Summary

   .. autosummary::

      ~STXMImage.AffineTransform
      ~STXMImage.BRIEF
      ~STXMImage.CENSURE
      ~STXMImage.Cascade
      ~STXMImage.CircleModel
      ~STXMImage.EllipseModel
      ~STXMImage.EssentialMatrixTransform
      ~STXMImage.EuclideanTransform
      ~STXMImage.FundamentalMatrixTransform
      ~STXMImage.ImageCollection
      ~STXMImage.LPIFilter2D
      ~STXMImage.LineModelND
      ~STXMImage.MCP
      ~STXMImage.MCP_Connect
      ~STXMImage.MCP_Flexible
      ~STXMImage.MCP_Geometric
      ~STXMImage.MultiImage
      ~STXMImage.ORB
      ~STXMImage.PiecewiseAffineTransform
      ~STXMImage.PolynomialTransform
      ~STXMImage.ProjectiveTransform
      ~STXMImage.RAG
      ~STXMImage.SIFT
      ~STXMImage.SimilarityTransform
      ~STXMImage.Stoner__Image__imagefuncs__adjust_contrast
      ~STXMImage.Stoner__Image__imagefuncs__align
      ~STXMImage.Stoner__Image__imagefuncs__asarray
      ~STXMImage.Stoner__Image__imagefuncs__asfloat
      ~STXMImage.Stoner__Image__imagefuncs__asint
      ~STXMImage.Stoner__Image__imagefuncs__clip_intensity
      ~STXMImage.Stoner__Image__imagefuncs__clip_neg
      ~STXMImage.Stoner__Image__imagefuncs__convert
      ~STXMImage.Stoner__Image__imagefuncs__correct_drift
      ~STXMImage.Stoner__Image__imagefuncs__crop
      ~STXMImage.Stoner__Image__imagefuncs__denoise
      ~STXMImage.Stoner__Image__imagefuncs__do_nothing
      ~STXMImage.Stoner__Image__imagefuncs__dtype_limits
      ~STXMImage.Stoner__Image__imagefuncs__fft
      ~STXMImage.Stoner__Image__imagefuncs__filter_image
      ~STXMImage.Stoner__Image__imagefuncs__gridimage
      ~STXMImage.Stoner__Image__imagefuncs__hist
      ~STXMImage.Stoner__Image__imagefuncs__imshow
      ~STXMImage.Stoner__Image__imagefuncs__level_image
      ~STXMImage.Stoner__Image__imagefuncs__normalise
      ~STXMImage.Stoner__Image__imagefuncs__plot_histogram
      ~STXMImage.Stoner__Image__imagefuncs__profile_line
      ~STXMImage.Stoner__Image__imagefuncs__quantize
      ~STXMImage.Stoner__Image__imagefuncs__radial_coordinates
      ~STXMImage.Stoner__Image__imagefuncs__radial_profile
      ~STXMImage.Stoner__Image__imagefuncs__remove_outliers
      ~STXMImage.Stoner__Image__imagefuncs__rotate
      ~STXMImage.Stoner__Image__imagefuncs__save
      ~STXMImage.Stoner__Image__imagefuncs__save_npy
      ~STXMImage.Stoner__Image__imagefuncs__save_png
      ~STXMImage.Stoner__Image__imagefuncs__save_tiff
      ~STXMImage.Stoner__Image__imagefuncs__sgolay2d
      ~STXMImage.Stoner__Image__imagefuncs__span
      ~STXMImage.Stoner__Image__imagefuncs__subtract_image
      ~STXMImage.Stoner__Image__imagefuncs__threshold_minmax
      ~STXMImage.Stoner__Image__imagefuncs__translate
      ~STXMImage.Stoner__Image__imagefuncs__translate_limits
      ~STXMImage.ThinPlateSplineTransform
      ~STXMImage.active_contour
      ~STXMImage.adjust_contrast
      ~STXMImage.adjust_gamma
      ~STXMImage.adjust_log
      ~STXMImage.adjust_sigmoid
      ~STXMImage.affine_transform
      ~STXMImage.align
      ~STXMImage.all
      ~STXMImage.anom
      ~STXMImage.any
      ~STXMImage.apply_hysteresis_threshold
      ~STXMImage.apply_parallel
      ~STXMImage.approximate_polygon
      ~STXMImage.area_closing
      ~STXMImage.area_opening
      ~STXMImage.argmax
      ~STXMImage.argmin
      ~STXMImage.argpartition
      ~STXMImage.argsort
      ~STXMImage.asarray
      ~STXMImage.asfloat
      ~STXMImage.asint
      ~STXMImage.astype
      ~STXMImage.autolevel
      ~STXMImage.autolevel_percentile
      ~STXMImage.ball
      ~STXMImage.ball_kernel
      ~STXMImage.binary_closing
      ~STXMImage.binary_dilation
      ~STXMImage.binary_erosion
      ~STXMImage.binary_fill_holes
      ~STXMImage.binary_hit_or_miss
      ~STXMImage.binary_opening
      ~STXMImage.binary_propagation
      ~STXMImage.black_tophat
      ~STXMImage.blob_dog
      ~STXMImage.blob_doh
      ~STXMImage.blob_log
      ~STXMImage.block_reduce
      ~STXMImage.blur_effect
      ~STXMImage.butterworth
      ~STXMImage.byteswap
      ~STXMImage.calibrate_denoiser
      ~STXMImage.call_plugin
      ~STXMImage.canny
      ~STXMImage.center_of_mass
      ~STXMImage.central_pixel
      ~STXMImage.centroid
      ~STXMImage.chan_vese
      ~STXMImage.checkerboard_level_set
      ~STXMImage.choose
      ~STXMImage.clear
      ~STXMImage.clear_border
      ~STXMImage.clip
      ~STXMImage.clip_intensity
      ~STXMImage.clip_neg
      ~STXMImage.closing
      ~STXMImage.combine_stains
      ~STXMImage.compare_images
      ~STXMImage.compress
      ~STXMImage.compressed
      ~STXMImage.concatenate_images
      ~STXMImage.conj
      ~STXMImage.conjugate
      ~STXMImage.convert
      ~STXMImage.convert_colorspace
      ~STXMImage.convex_hull_image
      ~STXMImage.convex_hull_object
      ~STXMImage.convolve
      ~STXMImage.convolve1d
      ~STXMImage.copy
      ~STXMImage.corner_fast
      ~STXMImage.corner_foerstner
      ~STXMImage.corner_harris
      ~STXMImage.corner_kitchen_rosenfeld
      ~STXMImage.corner_moravec
      ~STXMImage.corner_orientations
      ~STXMImage.corner_peaks
      ~STXMImage.corner_shi_tomasi
      ~STXMImage.corner_subpix
      ~STXMImage.correct_drift
      ~STXMImage.correlate
      ~STXMImage.correlate1d
      ~STXMImage.correlate_sparse
      ~STXMImage.count
      ~STXMImage.crop
      ~STXMImage.cube
      ~STXMImage.cumprod
      ~STXMImage.cumsum
      ~STXMImage.cumulative_distribution
      ~STXMImage.cut_normalized
      ~STXMImage.cut_threshold
      ~STXMImage.cycle_spin
      ~STXMImage.daisy
      ~STXMImage.deltaE_cie76
      ~STXMImage.deltaE_ciede2000
      ~STXMImage.deltaE_ciede94
      ~STXMImage.deltaE_cmc
      ~STXMImage.denoise
      ~STXMImage.denoise_bilateral
      ~STXMImage.denoise_invariant
      ~STXMImage.denoise_nl_means
      ~STXMImage.denoise_tv_bregman
      ~STXMImage.denoise_tv_chambolle
      ~STXMImage.denoise_wavelet
      ~STXMImage.diagonal
      ~STXMImage.diameter_closing
      ~STXMImage.diameter_opening
      ~STXMImage.diamond
      ~STXMImage.difference_of_gaussians
      ~STXMImage.dilation
      ~STXMImage.disk
      ~STXMImage.disk_level_set
      ~STXMImage.distance_transform_bf
      ~STXMImage.distance_transform_cdt
      ~STXMImage.distance_transform_edt
      ~STXMImage.do_nothing
      ~STXMImage.dot
      ~STXMImage.downscale_local_mean
      ~STXMImage.draw_haar_like_feature
      ~STXMImage.draw_multiblock_lbp
      ~STXMImage.dtype_limits
      ~STXMImage.dump
      ~STXMImage.dumps
      ~STXMImage.ellipse
      ~STXMImage.ellipsoid_kernel
      ~STXMImage.enhance_contrast
      ~STXMImage.enhance_contrast_percentile
      ~STXMImage.entropy
      ~STXMImage.equalize
      ~STXMImage.equalize_adapthist
      ~STXMImage.equalize_hist
      ~STXMImage.erosion
      ~STXMImage.estimate_sigma
      ~STXMImage.estimate_transform
      ~STXMImage.euler_number
      ~STXMImage.expand_labels
      ~STXMImage.extrema
      ~STXMImage.farid
      ~STXMImage.farid_h
      ~STXMImage.farid_v
      ~STXMImage.felzenszwalb
      ~STXMImage.fft
      ~STXMImage.fill
      ~STXMImage.filled
      ~STXMImage.filter_forward
      ~STXMImage.filter_image
      ~STXMImage.filter_inverse
      ~STXMImage.find_available_plugins
      ~STXMImage.find_boundaries
      ~STXMImage.find_contours
      ~STXMImage.find_objects
      ~STXMImage.fisher_vector
      ~STXMImage.flatten
      ~STXMImage.flood
      ~STXMImage.flood_fill
      ~STXMImage.footprint_from_sequence
      ~STXMImage.footprint_rectangle
      ~STXMImage.fourier_ellipsoid
      ~STXMImage.fourier_gaussian
      ~STXMImage.fourier_shift
      ~STXMImage.fourier_uniform
      ~STXMImage.frangi
      ~STXMImage.frt2
      ~STXMImage.gabor
      ~STXMImage.gabor_kernel
      ~STXMImage.gaussian
      ~STXMImage.gaussian_filter
      ~STXMImage.gaussian_filter1d
      ~STXMImage.gaussian_gradient_magnitude
      ~STXMImage.gaussian_laplace
      ~STXMImage.generate_binary_structure
      ~STXMImage.generic_filter
      ~STXMImage.generic_filter1d
      ~STXMImage.generic_gradient_magnitude
      ~STXMImage.generic_laplace
      ~STXMImage.geometric_mean
      ~STXMImage.geometric_transform
      ~STXMImage.get
      ~STXMImage.get_filename
      ~STXMImage.get_fill_value
      ~STXMImage.get_imag
      ~STXMImage.get_real
      ~STXMImage.getfield
      ~STXMImage.gradient
      ~STXMImage.gradient_percentile
      ~STXMImage.gray2rgb
      ~STXMImage.gray2rgba
      ~STXMImage.graycomatrix
      ~STXMImage.graycoprops
      ~STXMImage.grey_closing
      ~STXMImage.grey_dilation
      ~STXMImage.grey_erosion
      ~STXMImage.grey_opening
      ~STXMImage.grid_points_in_poly
      ~STXMImage.gridimage
      ~STXMImage.h_maxima
      ~STXMImage.h_minima
      ~STXMImage.haar_like_feature
      ~STXMImage.haar_like_feature_coord
      ~STXMImage.harden_mask
      ~STXMImage.hed2rgb
      ~STXMImage.hessian
      ~STXMImage.hessian_matrix
      ~STXMImage.hessian_matrix_det
      ~STXMImage.hessian_matrix_eigvals
      ~STXMImage.hist
      ~STXMImage.histogram
      ~STXMImage.hog
      ~STXMImage.hough_circle
      ~STXMImage.hough_circle_peaks
      ~STXMImage.hough_ellipse
      ~STXMImage.hough_line
      ~STXMImage.hough_line_peaks
      ~STXMImage.hsv2rgb
      ~STXMImage.ids
      ~STXMImage.ifrt2
      ~STXMImage.img_as_bool
      ~STXMImage.img_as_float
      ~STXMImage.img_as_float32
      ~STXMImage.img_as_float64
      ~STXMImage.img_as_int
      ~STXMImage.img_as_ubyte
      ~STXMImage.img_as_uint
      ~STXMImage.imread
      ~STXMImage.imread_collection
      ~STXMImage.imread_collection_wrapper
      ~STXMImage.imsave
      ~STXMImage.imshow
      ~STXMImage.imshow_collection
      ~STXMImage.inertia_tensor
      ~STXMImage.inertia_tensor_eigvals
      ~STXMImage.inpaint_biharmonic
      ~STXMImage.integral_image
      ~STXMImage.integrate
      ~STXMImage.intersection_coeff
      ~STXMImage.inverse_gaussian_gradient
      ~STXMImage.invert
      ~STXMImage.iradon
      ~STXMImage.iradon_sart
      ~STXMImage.is_low_contrast
      ~STXMImage.iscontiguous
      ~STXMImage.isotropic_closing
      ~STXMImage.isotropic_dilation
      ~STXMImage.isotropic_erosion
      ~STXMImage.isotropic_opening
      ~STXMImage.item
      ~STXMImage.items
      ~STXMImage.iterate_structure
      ~STXMImage.join_segmentations
      ~STXMImage.keys
      ~STXMImage.lab2lch
      ~STXMImage.lab2rgb
      ~STXMImage.lab2xyz
      ~STXMImage.label
      ~STXMImage.label2rgb
      ~STXMImage.label_points
      ~STXMImage.labeled_comprehension
      ~STXMImage.laplace
      ~STXMImage.lch2lab
      ~STXMImage.learn_gmm
      ~STXMImage.level_image
      ~STXMImage.load
      ~STXMImage.load_sift
      ~STXMImage.load_surf
      ~STXMImage.local_binary_pattern
      ~STXMImage.local_maxima
      ~STXMImage.local_minima
      ~STXMImage.lookfor
      ~STXMImage.luv2rgb
      ~STXMImage.luv2xyz
      ~STXMImage.majority
      ~STXMImage.manders_coloc_coeff
      ~STXMImage.manders_overlap_coeff
      ~STXMImage.map_array
      ~STXMImage.map_coordinates
      ~STXMImage.marching_cubes
      ~STXMImage.mark_boundaries
      ~STXMImage.match_descriptors
      ~STXMImage.match_histograms
      ~STXMImage.match_template
      ~STXMImage.matrix_transform
      ~STXMImage.max
      ~STXMImage.max_tree
      ~STXMImage.max_tree_local_maxima
      ~STXMImage.maximum
      ~STXMImage.maximum_filter
      ~STXMImage.maximum_filter1d
      ~STXMImage.maximum_position
      ~STXMImage.mean
      ~STXMImage.mean_bilateral
      ~STXMImage.mean_percentile
      ~STXMImage.medial_axis
      ~STXMImage.median
      ~STXMImage.median_filter
      ~STXMImage.meijering
      ~STXMImage.merge_hierarchical
      ~STXMImage.mesh_surface_area
      ~STXMImage.min
      ~STXMImage.minimum
      ~STXMImage.minimum_filter
      ~STXMImage.minimum_filter1d
      ~STXMImage.minimum_position
      ~STXMImage.mirror_footprint
      ~STXMImage.modal
      ~STXMImage.moments
      ~STXMImage.moments_central
      ~STXMImage.moments_coords
      ~STXMImage.moments_coords_central
      ~STXMImage.moments_hu
      ~STXMImage.moments_normalized
      ~STXMImage.montage
      ~STXMImage.morphological_chan_vese
      ~STXMImage.morphological_geodesic_active_contour
      ~STXMImage.morphological_gradient
      ~STXMImage.morphological_laplace
      ~STXMImage.multiblock_lbp
      ~STXMImage.multiscale_basic_features
      ~STXMImage.noise_filter
      ~STXMImage.nonzero
      ~STXMImage.normalise
      ~STXMImage.octagon
      ~STXMImage.octahedron
      ~STXMImage.opening
      ~STXMImage.order_angles_golden_ratio
      ~STXMImage.otsu
      ~STXMImage.pad_footprint
      ~STXMImage.partition
      ~STXMImage.peak_local_max
      ~STXMImage.pearson_corr_coeff
      ~STXMImage.percentile
      ~STXMImage.percentile_filter
      ~STXMImage.perimeter
      ~STXMImage.perimeter_crofton
      ~STXMImage.pixel_graph
      ~STXMImage.plot_histogram
      ~STXMImage.plot_matched_features
      ~STXMImage.plugin_info
      ~STXMImage.plugin_order
      ~STXMImage.points_in_poly
      ~STXMImage.pop
      ~STXMImage.pop_bilateral
      ~STXMImage.pop_percentile
      ~STXMImage.popitem
      ~STXMImage.prewitt
      ~STXMImage.prewitt_h
      ~STXMImage.prewitt_v
      ~STXMImage.probabilistic_hough_line
      ~STXMImage.prod
      ~STXMImage.product
      ~STXMImage.profile_line
      ~STXMImage.ptp
      ~STXMImage.push
      ~STXMImage.put
      ~STXMImage.pyramid_expand
      ~STXMImage.pyramid_gaussian
      ~STXMImage.pyramid_laplacian
      ~STXMImage.pyramid_reduce
      ~STXMImage.quantize
      ~STXMImage.quickshift
      ~STXMImage.radial_coordinates
      ~STXMImage.radial_profile
      ~STXMImage.radon
      ~STXMImage.rag_boundary
      ~STXMImage.rag_mean_color
      ~STXMImage.random_noise
      ~STXMImage.random_walker
      ~STXMImage.rank_filter
      ~STXMImage.rank_order
      ~STXMImage.ransac
      ~STXMImage.ravel
      ~STXMImage.reconstruction
      ~STXMImage.rectangle
      ~STXMImage.regionprops
      ~STXMImage.regionprops_table
      ~STXMImage.regular_grid
      ~STXMImage.regular_seeds
      ~STXMImage.relabel_sequential
      ~STXMImage.remove_objects_by_distance
      ~STXMImage.remove_outliers
      ~STXMImage.remove_small_holes
      ~STXMImage.remove_small_objects
      ~STXMImage.repeat
      ~STXMImage.rescale
      ~STXMImage.rescale_intensity
      ~STXMImage.reset_plugins
      ~STXMImage.reshape
      ~STXMImage.resize
      ~STXMImage.resize_local_mean
      ~STXMImage.rgb2gray
      ~STXMImage.rgb2hed
      ~STXMImage.rgb2hsv
      ~STXMImage.rgb2lab
      ~STXMImage.rgb2luv
      ~STXMImage.rgb2rgbcie
      ~STXMImage.rgb2xyz
      ~STXMImage.rgb2ycbcr
      ~STXMImage.rgb2ydbdr
      ~STXMImage.rgb2yiq
      ~STXMImage.rgb2ypbpr
      ~STXMImage.rgb2yuv
      ~STXMImage.rgba2rgb
      ~STXMImage.rgbcie2rgb
      ~STXMImage.richardson_lucy
      ~STXMImage.roberts
      ~STXMImage.roberts_neg_diag
      ~STXMImage.roberts_pos_diag
      ~STXMImage.rolling_ball
      ~STXMImage.rotate
      ~STXMImage.round
      ~STXMImage.route_through_array
      ~STXMImage.sato
      ~STXMImage.save
      ~STXMImage.save_npy
      ~STXMImage.save_png
      ~STXMImage.save_tiff
      ~STXMImage.scharr
      ~STXMImage.scharr_h
      ~STXMImage.scharr_v
      ~STXMImage.scipy__ndimage___filters__convolve
      ~STXMImage.scipy__ndimage___filters__convolve1d
      ~STXMImage.scipy__ndimage___filters__correlate
      ~STXMImage.scipy__ndimage___filters__correlate1d
      ~STXMImage.scipy__ndimage___filters__gaussian_filter
      ~STXMImage.scipy__ndimage___filters__gaussian_filter1d
      ~STXMImage.scipy__ndimage___filters__gaussian_gradient_magnitude
      ~STXMImage.scipy__ndimage___filters__gaussian_laplace
      ~STXMImage.scipy__ndimage___filters__generic_filter
      ~STXMImage.scipy__ndimage___filters__generic_filter1d
      ~STXMImage.scipy__ndimage___filters__generic_gradient_magnitude
      ~STXMImage.scipy__ndimage___filters__generic_laplace
      ~STXMImage.scipy__ndimage___filters__laplace
      ~STXMImage.scipy__ndimage___filters__maximum_filter
      ~STXMImage.scipy__ndimage___filters__maximum_filter1d
      ~STXMImage.scipy__ndimage___filters__median_filter
      ~STXMImage.scipy__ndimage___filters__minimum_filter
      ~STXMImage.scipy__ndimage___filters__minimum_filter1d
      ~STXMImage.scipy__ndimage___filters__percentile_filter
      ~STXMImage.scipy__ndimage___filters__prewitt
      ~STXMImage.scipy__ndimage___filters__rank_filter
      ~STXMImage.scipy__ndimage___filters__sobel
      ~STXMImage.scipy__ndimage___filters__uniform_filter
      ~STXMImage.scipy__ndimage___filters__uniform_filter1d
      ~STXMImage.scipy__ndimage___fourier__fourier_ellipsoid
      ~STXMImage.scipy__ndimage___fourier__fourier_gaussian
      ~STXMImage.scipy__ndimage___fourier__fourier_shift
      ~STXMImage.scipy__ndimage___fourier__fourier_uniform
      ~STXMImage.scipy__ndimage___interpolation__affine_transform
      ~STXMImage.scipy__ndimage___interpolation__geometric_transform
      ~STXMImage.scipy__ndimage___interpolation__map_coordinates
      ~STXMImage.scipy__ndimage___interpolation__rotate
      ~STXMImage.scipy__ndimage___interpolation__shift
      ~STXMImage.scipy__ndimage___interpolation__spline_filter
      ~STXMImage.scipy__ndimage___interpolation__spline_filter1d
      ~STXMImage.scipy__ndimage___interpolation__zoom
      ~STXMImage.scipy__ndimage___measurements__center_of_mass
      ~STXMImage.scipy__ndimage___measurements__extrema
      ~STXMImage.scipy__ndimage___measurements__find_objects
      ~STXMImage.scipy__ndimage___measurements__histogram
      ~STXMImage.scipy__ndimage___measurements__label
      ~STXMImage.scipy__ndimage___measurements__labeled_comprehension
      ~STXMImage.scipy__ndimage___measurements__maximum
      ~STXMImage.scipy__ndimage___measurements__maximum_position
      ~STXMImage.scipy__ndimage___measurements__mean
      ~STXMImage.scipy__ndimage___measurements__median
      ~STXMImage.scipy__ndimage___measurements__minimum
      ~STXMImage.scipy__ndimage___measurements__minimum_position
      ~STXMImage.scipy__ndimage___measurements__standard_deviation
      ~STXMImage.scipy__ndimage___measurements__sum
      ~STXMImage.scipy__ndimage___measurements__sum_labels
      ~STXMImage.scipy__ndimage___measurements__value_indices
      ~STXMImage.scipy__ndimage___measurements__variance
      ~STXMImage.scipy__ndimage___measurements__watershed_ift
      ~STXMImage.scipy__ndimage___morphology__binary_closing
      ~STXMImage.scipy__ndimage___morphology__binary_dilation
      ~STXMImage.scipy__ndimage___morphology__binary_erosion
      ~STXMImage.scipy__ndimage___morphology__binary_fill_holes
      ~STXMImage.scipy__ndimage___morphology__binary_hit_or_miss
      ~STXMImage.scipy__ndimage___morphology__binary_opening
      ~STXMImage.scipy__ndimage___morphology__binary_propagation
      ~STXMImage.scipy__ndimage___morphology__black_tophat
      ~STXMImage.scipy__ndimage___morphology__distance_transform_bf
      ~STXMImage.scipy__ndimage___morphology__distance_transform_cdt
      ~STXMImage.scipy__ndimage___morphology__distance_transform_edt
      ~STXMImage.scipy__ndimage___morphology__generate_binary_structure
      ~STXMImage.scipy__ndimage___morphology__grey_closing
      ~STXMImage.scipy__ndimage___morphology__grey_dilation
      ~STXMImage.scipy__ndimage___morphology__grey_erosion
      ~STXMImage.scipy__ndimage___morphology__grey_opening
      ~STXMImage.scipy__ndimage___morphology__iterate_structure
      ~STXMImage.scipy__ndimage___morphology__morphological_gradient
      ~STXMImage.scipy__ndimage___morphology__morphological_laplace
      ~STXMImage.scipy__ndimage___morphology__white_tophat
      ~STXMImage.searchsorted
      ~STXMImage.separate_stains
      ~STXMImage.set_fill_value
      ~STXMImage.setdefault
      ~STXMImage.setfield
      ~STXMImage.setflags
      ~STXMImage.sgolay2d
      ~STXMImage.shannon_entropy
      ~STXMImage.shape_index
      ~STXMImage.shift
      ~STXMImage.shortest_path
      ~STXMImage.show
      ~STXMImage.show_rag
      ~STXMImage.shrink_mask
      ~STXMImage.skeletonize
      ~STXMImage.skimage___shared__filters__gaussian
      ~STXMImage.skimage__color__colorconv__combine_stains
      ~STXMImage.skimage__color__colorconv__convert_colorspace
      ~STXMImage.skimage__color__colorconv__gray2rgb
      ~STXMImage.skimage__color__colorconv__gray2rgba
      ~STXMImage.skimage__color__colorconv__hed2rgb
      ~STXMImage.skimage__color__colorconv__hsv2rgb
      ~STXMImage.skimage__color__colorconv__lab2lch
      ~STXMImage.skimage__color__colorconv__lab2rgb
      ~STXMImage.skimage__color__colorconv__lab2xyz
      ~STXMImage.skimage__color__colorconv__lch2lab
      ~STXMImage.skimage__color__colorconv__luv2rgb
      ~STXMImage.skimage__color__colorconv__luv2xyz
      ~STXMImage.skimage__color__colorconv__rgb2gray
      ~STXMImage.skimage__color__colorconv__rgb2hed
      ~STXMImage.skimage__color__colorconv__rgb2hsv
      ~STXMImage.skimage__color__colorconv__rgb2lab
      ~STXMImage.skimage__color__colorconv__rgb2luv
      ~STXMImage.skimage__color__colorconv__rgb2rgbcie
      ~STXMImage.skimage__color__colorconv__rgb2xyz
      ~STXMImage.skimage__color__colorconv__rgb2ycbcr
      ~STXMImage.skimage__color__colorconv__rgb2ydbdr
      ~STXMImage.skimage__color__colorconv__rgb2yiq
      ~STXMImage.skimage__color__colorconv__rgb2ypbpr
      ~STXMImage.skimage__color__colorconv__rgb2yuv
      ~STXMImage.skimage__color__colorconv__rgba2rgb
      ~STXMImage.skimage__color__colorconv__rgbcie2rgb
      ~STXMImage.skimage__color__colorconv__separate_stains
      ~STXMImage.skimage__color__colorconv__xyz2lab
      ~STXMImage.skimage__color__colorconv__xyz2luv
      ~STXMImage.skimage__color__colorconv__xyz2rgb
      ~STXMImage.skimage__color__colorconv__xyz_tristimulus_values
      ~STXMImage.skimage__color__colorconv__ycbcr2rgb
      ~STXMImage.skimage__color__colorconv__ydbdr2rgb
      ~STXMImage.skimage__color__colorconv__yiq2rgb
      ~STXMImage.skimage__color__colorconv__ypbpr2rgb
      ~STXMImage.skimage__color__colorconv__yuv2rgb
      ~STXMImage.skimage__color__colorlabel__label2rgb
      ~STXMImage.skimage__color__delta_e__deltaE_cie76
      ~STXMImage.skimage__color__delta_e__deltaE_ciede2000
      ~STXMImage.skimage__color__delta_e__deltaE_ciede94
      ~STXMImage.skimage__color__delta_e__deltaE_cmc
      ~STXMImage.skimage__exposure___adapthist__equalize_adapthist
      ~STXMImage.skimage__exposure__exposure__adjust_gamma
      ~STXMImage.skimage__exposure__exposure__adjust_log
      ~STXMImage.skimage__exposure__exposure__adjust_sigmoid
      ~STXMImage.skimage__exposure__exposure__cumulative_distribution
      ~STXMImage.skimage__exposure__exposure__equalize_hist
      ~STXMImage.skimage__exposure__exposure__histogram
      ~STXMImage.skimage__exposure__exposure__is_low_contrast
      ~STXMImage.skimage__exposure__exposure__rescale_intensity
      ~STXMImage.skimage__exposure__histogram_matching__match_histograms
      ~STXMImage.skimage__feature___basic_features__multiscale_basic_features
      ~STXMImage.skimage__feature___canny__canny
      ~STXMImage.skimage__feature___cascade__Cascade
      ~STXMImage.skimage__feature___daisy__daisy
      ~STXMImage.skimage__feature___fisher_vector__fisher_vector
      ~STXMImage.skimage__feature___fisher_vector__learn_gmm
      ~STXMImage.skimage__feature___hog__hog
      ~STXMImage.skimage__feature__blob__blob_dog
      ~STXMImage.skimage__feature__blob__blob_doh
      ~STXMImage.skimage__feature__blob__blob_log
      ~STXMImage.skimage__feature__brief__BRIEF
      ~STXMImage.skimage__feature__censure__CENSURE
      ~STXMImage.skimage__feature__corner__corner_fast
      ~STXMImage.skimage__feature__corner__corner_foerstner
      ~STXMImage.skimage__feature__corner__corner_harris
      ~STXMImage.skimage__feature__corner__corner_kitchen_rosenfeld
      ~STXMImage.skimage__feature__corner__corner_moravec
      ~STXMImage.skimage__feature__corner__corner_orientations
      ~STXMImage.skimage__feature__corner__corner_peaks
      ~STXMImage.skimage__feature__corner__corner_shi_tomasi
      ~STXMImage.skimage__feature__corner__corner_subpix
      ~STXMImage.skimage__feature__corner__hessian_matrix
      ~STXMImage.skimage__feature__corner__hessian_matrix_det
      ~STXMImage.skimage__feature__corner__hessian_matrix_eigvals
      ~STXMImage.skimage__feature__corner__shape_index
      ~STXMImage.skimage__feature__corner__structure_tensor
      ~STXMImage.skimage__feature__corner__structure_tensor_eigenvalues
      ~STXMImage.skimage__feature__haar__draw_haar_like_feature
      ~STXMImage.skimage__feature__haar__haar_like_feature
      ~STXMImage.skimage__feature__haar__haar_like_feature_coord
      ~STXMImage.skimage__feature__match__match_descriptors
      ~STXMImage.skimage__feature__orb__ORB
      ~STXMImage.skimage__feature__peak__peak_local_max
      ~STXMImage.skimage__feature__sift__SIFT
      ~STXMImage.skimage__feature__template__match_template
      ~STXMImage.skimage__feature__texture__draw_multiblock_lbp
      ~STXMImage.skimage__feature__texture__graycomatrix
      ~STXMImage.skimage__feature__texture__graycoprops
      ~STXMImage.skimage__feature__texture__local_binary_pattern
      ~STXMImage.skimage__feature__texture__multiblock_lbp
      ~STXMImage.skimage__feature__util__plot_matched_features
      ~STXMImage.skimage__filters___fft_based__butterworth
      ~STXMImage.skimage__filters___gabor__gabor
      ~STXMImage.skimage__filters___gabor__gabor_kernel
      ~STXMImage.skimage__filters___gaussian__difference_of_gaussians
      ~STXMImage.skimage__filters___median__median
      ~STXMImage.skimage__filters___rank_order__rank_order
      ~STXMImage.skimage__filters___sparse__correlate_sparse
      ~STXMImage.skimage__filters___unsharp_mask__unsharp_mask
      ~STXMImage.skimage__filters___window__window
      ~STXMImage.skimage__filters__edges__farid
      ~STXMImage.skimage__filters__edges__farid_h
      ~STXMImage.skimage__filters__edges__farid_v
      ~STXMImage.skimage__filters__edges__laplace
      ~STXMImage.skimage__filters__edges__prewitt
      ~STXMImage.skimage__filters__edges__prewitt_h
      ~STXMImage.skimage__filters__edges__prewitt_v
      ~STXMImage.skimage__filters__edges__roberts
      ~STXMImage.skimage__filters__edges__roberts_neg_diag
      ~STXMImage.skimage__filters__edges__roberts_pos_diag
      ~STXMImage.skimage__filters__edges__scharr
      ~STXMImage.skimage__filters__edges__scharr_h
      ~STXMImage.skimage__filters__edges__scharr_v
      ~STXMImage.skimage__filters__edges__sobel
      ~STXMImage.skimage__filters__edges__sobel_h
      ~STXMImage.skimage__filters__edges__sobel_v
      ~STXMImage.skimage__filters__lpi_filter__LPIFilter2D
      ~STXMImage.skimage__filters__lpi_filter__filter_forward
      ~STXMImage.skimage__filters__lpi_filter__filter_inverse
      ~STXMImage.skimage__filters__lpi_filter__wiener
      ~STXMImage.skimage__filters__rank___percentile__autolevel_percentile
      ~STXMImage.skimage__filters__rank___percentile__enhance_contrast_percentile
      ~STXMImage.skimage__filters__rank___percentile__gradient_percentile
      ~STXMImage.skimage__filters__rank___percentile__mean_percentile
      ~STXMImage.skimage__filters__rank___percentile__percentile
      ~STXMImage.skimage__filters__rank___percentile__pop_percentile
      ~STXMImage.skimage__filters__rank___percentile__subtract_mean_percentile
      ~STXMImage.skimage__filters__rank___percentile__sum_percentile
      ~STXMImage.skimage__filters__rank___percentile__threshold_percentile
      ~STXMImage.skimage__filters__rank__bilateral__mean_bilateral
      ~STXMImage.skimage__filters__rank__bilateral__pop_bilateral
      ~STXMImage.skimage__filters__rank__bilateral__sum_bilateral
      ~STXMImage.skimage__filters__rank__generic__autolevel
      ~STXMImage.skimage__filters__rank__generic__enhance_contrast
      ~STXMImage.skimage__filters__rank__generic__entropy
      ~STXMImage.skimage__filters__rank__generic__equalize
      ~STXMImage.skimage__filters__rank__generic__geometric_mean
      ~STXMImage.skimage__filters__rank__generic__gradient
      ~STXMImage.skimage__filters__rank__generic__majority
      ~STXMImage.skimage__filters__rank__generic__maximum
      ~STXMImage.skimage__filters__rank__generic__mean
      ~STXMImage.skimage__filters__rank__generic__median
      ~STXMImage.skimage__filters__rank__generic__minimum
      ~STXMImage.skimage__filters__rank__generic__modal
      ~STXMImage.skimage__filters__rank__generic__noise_filter
      ~STXMImage.skimage__filters__rank__generic__otsu
      ~STXMImage.skimage__filters__rank__generic__pop
      ~STXMImage.skimage__filters__rank__generic__subtract_mean
      ~STXMImage.skimage__filters__rank__generic__sum
      ~STXMImage.skimage__filters__rank__generic__threshold
      ~STXMImage.skimage__filters__rank__generic__windowed_histogram
      ~STXMImage.skimage__filters__ridges__frangi
      ~STXMImage.skimage__filters__ridges__hessian
      ~STXMImage.skimage__filters__ridges__meijering
      ~STXMImage.skimage__filters__ridges__sato
      ~STXMImage.skimage__filters__thresholding__apply_hysteresis_threshold
      ~STXMImage.skimage__filters__thresholding__threshold_isodata
      ~STXMImage.skimage__filters__thresholding__threshold_li
      ~STXMImage.skimage__filters__thresholding__threshold_local
      ~STXMImage.skimage__filters__thresholding__threshold_mean
      ~STXMImage.skimage__filters__thresholding__threshold_minimum
      ~STXMImage.skimage__filters__thresholding__threshold_multiotsu
      ~STXMImage.skimage__filters__thresholding__threshold_niblack
      ~STXMImage.skimage__filters__thresholding__threshold_otsu
      ~STXMImage.skimage__filters__thresholding__threshold_sauvola
      ~STXMImage.skimage__filters__thresholding__threshold_triangle
      ~STXMImage.skimage__filters__thresholding__threshold_yen
      ~STXMImage.skimage__filters__thresholding__try_all_threshold
      ~STXMImage.skimage__graph___graph__central_pixel
      ~STXMImage.skimage__graph___graph__pixel_graph
      ~STXMImage.skimage__graph___graph_cut__cut_normalized
      ~STXMImage.skimage__graph___graph_cut__cut_threshold
      ~STXMImage.skimage__graph___graph_merge__merge_hierarchical
      ~STXMImage.skimage__graph___mcp__MCP
      ~STXMImage.skimage__graph___mcp__MCP_Connect
      ~STXMImage.skimage__graph___mcp__MCP_Flexible
      ~STXMImage.skimage__graph___mcp__MCP_Geometric
      ~STXMImage.skimage__graph___rag__RAG
      ~STXMImage.skimage__graph___rag__rag_boundary
      ~STXMImage.skimage__graph___rag__rag_mean_color
      ~STXMImage.skimage__graph___rag__show_rag
      ~STXMImage.skimage__graph__mcp__route_through_array
      ~STXMImage.skimage__graph__spath__shortest_path
      ~STXMImage.skimage__io___image_stack__pop
      ~STXMImage.skimage__io___image_stack__push
      ~STXMImage.skimage__io___io__imread
      ~STXMImage.skimage__io___io__imread_collection
      ~STXMImage.skimage__io___io__imsave
      ~STXMImage.skimage__io___io__imshow
      ~STXMImage.skimage__io___io__imshow_collection
      ~STXMImage.skimage__io___io__show
      ~STXMImage.skimage__io__collection__ImageCollection
      ~STXMImage.skimage__io__collection__MultiImage
      ~STXMImage.skimage__io__collection__concatenate_images
      ~STXMImage.skimage__io__collection__imread_collection_wrapper
      ~STXMImage.skimage__io__manage_plugins__call_plugin
      ~STXMImage.skimage__io__manage_plugins__find_available_plugins
      ~STXMImage.skimage__io__manage_plugins__plugin_info
      ~STXMImage.skimage__io__manage_plugins__plugin_order
      ~STXMImage.skimage__io__manage_plugins__reset_plugins
      ~STXMImage.skimage__io__manage_plugins__use_plugin
      ~STXMImage.skimage__io__sift__load_sift
      ~STXMImage.skimage__io__sift__load_surf
      ~STXMImage.skimage__measure___blur_effect__blur_effect
      ~STXMImage.skimage__measure___colocalization__intersection_coeff
      ~STXMImage.skimage__measure___colocalization__manders_coloc_coeff
      ~STXMImage.skimage__measure___colocalization__manders_overlap_coeff
      ~STXMImage.skimage__measure___colocalization__pearson_corr_coeff
      ~STXMImage.skimage__measure___find_contours__find_contours
      ~STXMImage.skimage__measure___label__label
      ~STXMImage.skimage__measure___marching_cubes_lewiner__marching_cubes
      ~STXMImage.skimage__measure___marching_cubes_lewiner__mesh_surface_area
      ~STXMImage.skimage__measure___moments__centroid
      ~STXMImage.skimage__measure___moments__inertia_tensor
      ~STXMImage.skimage__measure___moments__inertia_tensor_eigvals
      ~STXMImage.skimage__measure___moments__moments
      ~STXMImage.skimage__measure___moments__moments_central
      ~STXMImage.skimage__measure___moments__moments_coords
      ~STXMImage.skimage__measure___moments__moments_coords_central
      ~STXMImage.skimage__measure___moments__moments_hu
      ~STXMImage.skimage__measure___moments__moments_normalized
      ~STXMImage.skimage__measure___polygon__approximate_polygon
      ~STXMImage.skimage__measure___polygon__subdivide_polygon
      ~STXMImage.skimage__measure___regionprops__regionprops
      ~STXMImage.skimage__measure___regionprops__regionprops_table
      ~STXMImage.skimage__measure___regionprops_utils__euler_number
      ~STXMImage.skimage__measure___regionprops_utils__perimeter
      ~STXMImage.skimage__measure___regionprops_utils__perimeter_crofton
      ~STXMImage.skimage__measure__block__block_reduce
      ~STXMImage.skimage__measure__entropy__shannon_entropy
      ~STXMImage.skimage__measure__fit__CircleModel
      ~STXMImage.skimage__measure__fit__EllipseModel
      ~STXMImage.skimage__measure__fit__LineModelND
      ~STXMImage.skimage__measure__fit__ransac
      ~STXMImage.skimage__measure__pnpoly__grid_points_in_poly
      ~STXMImage.skimage__measure__pnpoly__points_in_poly
      ~STXMImage.skimage__measure__profile__profile_line
      ~STXMImage.skimage__morphology___flood_fill__flood
      ~STXMImage.skimage__morphology___flood_fill__flood_fill
      ~STXMImage.skimage__morphology___skeletonize__medial_axis
      ~STXMImage.skimage__morphology___skeletonize__skeletonize
      ~STXMImage.skimage__morphology___skeletonize__thin
      ~STXMImage.skimage__morphology__binary__binary_closing
      ~STXMImage.skimage__morphology__binary__binary_dilation
      ~STXMImage.skimage__morphology__binary__binary_erosion
      ~STXMImage.skimage__morphology__binary__binary_opening
      ~STXMImage.skimage__morphology__convex_hull__convex_hull_image
      ~STXMImage.skimage__morphology__convex_hull__convex_hull_object
      ~STXMImage.skimage__morphology__extrema__h_maxima
      ~STXMImage.skimage__morphology__extrema__h_minima
      ~STXMImage.skimage__morphology__extrema__local_maxima
      ~STXMImage.skimage__morphology__extrema__local_minima
      ~STXMImage.skimage__morphology__footprints__ball
      ~STXMImage.skimage__morphology__footprints__cube
      ~STXMImage.skimage__morphology__footprints__diamond
      ~STXMImage.skimage__morphology__footprints__disk
      ~STXMImage.skimage__morphology__footprints__ellipse
      ~STXMImage.skimage__morphology__footprints__footprint_from_sequence
      ~STXMImage.skimage__morphology__footprints__footprint_rectangle
      ~STXMImage.skimage__morphology__footprints__mirror_footprint
      ~STXMImage.skimage__morphology__footprints__octagon
      ~STXMImage.skimage__morphology__footprints__octahedron
      ~STXMImage.skimage__morphology__footprints__pad_footprint
      ~STXMImage.skimage__morphology__footprints__rectangle
      ~STXMImage.skimage__morphology__footprints__square
      ~STXMImage.skimage__morphology__footprints__star
      ~STXMImage.skimage__morphology__gray__black_tophat
      ~STXMImage.skimage__morphology__gray__closing
      ~STXMImage.skimage__morphology__gray__dilation
      ~STXMImage.skimage__morphology__gray__erosion
      ~STXMImage.skimage__morphology__gray__opening
      ~STXMImage.skimage__morphology__gray__white_tophat
      ~STXMImage.skimage__morphology__grayreconstruct__reconstruction
      ~STXMImage.skimage__morphology__isotropic__isotropic_closing
      ~STXMImage.skimage__morphology__isotropic__isotropic_dilation
      ~STXMImage.skimage__morphology__isotropic__isotropic_erosion
      ~STXMImage.skimage__morphology__isotropic__isotropic_opening
      ~STXMImage.skimage__morphology__max_tree__area_closing
      ~STXMImage.skimage__morphology__max_tree__area_opening
      ~STXMImage.skimage__morphology__max_tree__diameter_closing
      ~STXMImage.skimage__morphology__max_tree__diameter_opening
      ~STXMImage.skimage__morphology__max_tree__max_tree
      ~STXMImage.skimage__morphology__max_tree__max_tree_local_maxima
      ~STXMImage.skimage__morphology__misc__remove_objects_by_distance
      ~STXMImage.skimage__morphology__misc__remove_small_holes
      ~STXMImage.skimage__morphology__misc__remove_small_objects
      ~STXMImage.skimage__restoration___cycle_spin__cycle_spin
      ~STXMImage.skimage__restoration___denoise__denoise_bilateral
      ~STXMImage.skimage__restoration___denoise__denoise_tv_bregman
      ~STXMImage.skimage__restoration___denoise__denoise_tv_chambolle
      ~STXMImage.skimage__restoration___denoise__denoise_wavelet
      ~STXMImage.skimage__restoration___denoise__estimate_sigma
      ~STXMImage.skimage__restoration___rolling_ball__ball_kernel
      ~STXMImage.skimage__restoration___rolling_ball__ellipsoid_kernel
      ~STXMImage.skimage__restoration___rolling_ball__rolling_ball
      ~STXMImage.skimage__restoration__deconvolution__richardson_lucy
      ~STXMImage.skimage__restoration__deconvolution__unsupervised_wiener
      ~STXMImage.skimage__restoration__deconvolution__wiener
      ~STXMImage.skimage__restoration__inpaint__inpaint_biharmonic
      ~STXMImage.skimage__restoration__j_invariant__calibrate_denoiser
      ~STXMImage.skimage__restoration__j_invariant__denoise_invariant
      ~STXMImage.skimage__restoration__non_local_means__denoise_nl_means
      ~STXMImage.skimage__restoration__unwrap__unwrap_phase
      ~STXMImage.skimage__segmentation___chan_vese__chan_vese
      ~STXMImage.skimage__segmentation___clear_border__clear_border
      ~STXMImage.skimage__segmentation___expand_labels__expand_labels
      ~STXMImage.skimage__segmentation___felzenszwalb__felzenszwalb
      ~STXMImage.skimage__segmentation___join__join_segmentations
      ~STXMImage.skimage__segmentation___join__relabel_sequential
      ~STXMImage.skimage__segmentation___quickshift__quickshift
      ~STXMImage.skimage__segmentation___watershed__watershed
      ~STXMImage.skimage__segmentation__active_contour_model__active_contour
      ~STXMImage.skimage__segmentation__boundaries__find_boundaries
      ~STXMImage.skimage__segmentation__boundaries__mark_boundaries
      ~STXMImage.skimage__segmentation__morphsnakes__checkerboard_level_set
      ~STXMImage.skimage__segmentation__morphsnakes__disk_level_set
      ~STXMImage.skimage__segmentation__morphsnakes__inverse_gaussian_gradient
      ~STXMImage.skimage__segmentation__morphsnakes__morphological_chan_vese
      ~STXMImage.skimage__segmentation__morphsnakes__morphological_geodesic_active_contour
      ~STXMImage.skimage__segmentation__random_walker_segmentation__random_walker
      ~STXMImage.skimage__segmentation__slic_superpixels__slic
      ~STXMImage.skimage__transform___geometric__AffineTransform
      ~STXMImage.skimage__transform___geometric__EssentialMatrixTransform
      ~STXMImage.skimage__transform___geometric__EuclideanTransform
      ~STXMImage.skimage__transform___geometric__FundamentalMatrixTransform
      ~STXMImage.skimage__transform___geometric__PiecewiseAffineTransform
      ~STXMImage.skimage__transform___geometric__PolynomialTransform
      ~STXMImage.skimage__transform___geometric__ProjectiveTransform
      ~STXMImage.skimage__transform___geometric__SimilarityTransform
      ~STXMImage.skimage__transform___geometric__estimate_transform
      ~STXMImage.skimage__transform___geometric__matrix_transform
      ~STXMImage.skimage__transform___thin_plate_splines__ThinPlateSplineTransform
      ~STXMImage.skimage__transform___warps__downscale_local_mean
      ~STXMImage.skimage__transform___warps__rescale
      ~STXMImage.skimage__transform___warps__resize
      ~STXMImage.skimage__transform___warps__resize_local_mean
      ~STXMImage.skimage__transform___warps__rotate
      ~STXMImage.skimage__transform___warps__swirl
      ~STXMImage.skimage__transform___warps__warp
      ~STXMImage.skimage__transform___warps__warp_coords
      ~STXMImage.skimage__transform___warps__warp_polar
      ~STXMImage.skimage__transform__finite_radon_transform__frt2
      ~STXMImage.skimage__transform__finite_radon_transform__ifrt2
      ~STXMImage.skimage__transform__hough_transform__hough_circle
      ~STXMImage.skimage__transform__hough_transform__hough_circle_peaks
      ~STXMImage.skimage__transform__hough_transform__hough_ellipse
      ~STXMImage.skimage__transform__hough_transform__hough_line
      ~STXMImage.skimage__transform__hough_transform__hough_line_peaks
      ~STXMImage.skimage__transform__hough_transform__probabilistic_hough_line
      ~STXMImage.skimage__transform__integral__integral_image
      ~STXMImage.skimage__transform__integral__integrate
      ~STXMImage.skimage__transform__pyramids__pyramid_expand
      ~STXMImage.skimage__transform__pyramids__pyramid_gaussian
      ~STXMImage.skimage__transform__pyramids__pyramid_laplacian
      ~STXMImage.skimage__transform__pyramids__pyramid_reduce
      ~STXMImage.skimage__transform__radon_transform__iradon
      ~STXMImage.skimage__transform__radon_transform__iradon_sart
      ~STXMImage.skimage__transform__radon_transform__order_angles_golden_ratio
      ~STXMImage.skimage__transform__radon_transform__radon
      ~STXMImage.skimage__util___invert__invert
      ~STXMImage.skimage__util___label__label_points
      ~STXMImage.skimage__util___map_array__map_array
      ~STXMImage.skimage__util___montage__montage
      ~STXMImage.skimage__util___regular_grid__regular_grid
      ~STXMImage.skimage__util___regular_grid__regular_seeds
      ~STXMImage.skimage__util___slice_along_axes__slice_along_axes
      ~STXMImage.skimage__util__apply_parallel__apply_parallel
      ~STXMImage.skimage__util__arraycrop__crop
      ~STXMImage.skimage__util__compare__compare_images
      ~STXMImage.skimage__util__dtype__dtype_limits
      ~STXMImage.skimage__util__dtype__img_as_bool
      ~STXMImage.skimage__util__dtype__img_as_float
      ~STXMImage.skimage__util__dtype__img_as_float32
      ~STXMImage.skimage__util__dtype__img_as_float64
      ~STXMImage.skimage__util__dtype__img_as_int
      ~STXMImage.skimage__util__dtype__img_as_ubyte
      ~STXMImage.skimage__util__dtype__img_as_uint
      ~STXMImage.skimage__util__lookfor__lookfor
      ~STXMImage.skimage__util__noise__random_noise
      ~STXMImage.skimage__util__shape__view_as_blocks
      ~STXMImage.skimage__util__shape__view_as_windows
      ~STXMImage.skimage__util__unique__unique_rows
      ~STXMImage.slic
      ~STXMImage.slice_along_axes
      ~STXMImage.sobel
      ~STXMImage.sobel_h
      ~STXMImage.sobel_v
      ~STXMImage.soften_mask
      ~STXMImage.sort
      ~STXMImage.span
      ~STXMImage.spline_filter
      ~STXMImage.spline_filter1d
      ~STXMImage.square
      ~STXMImage.squeeze
      ~STXMImage.standard_deviation
      ~STXMImage.star
      ~STXMImage.std
      ~STXMImage.structure_tensor
      ~STXMImage.structure_tensor_eigenvalues
      ~STXMImage.subdivide_polygon
      ~STXMImage.subtract_image
      ~STXMImage.subtract_mean
      ~STXMImage.subtract_mean_percentile
      ~STXMImage.sum
      ~STXMImage.sum_bilateral
      ~STXMImage.sum_labels
      ~STXMImage.sum_percentile
      ~STXMImage.swapaxes
      ~STXMImage.swirl
      ~STXMImage.take
      ~STXMImage.thin
      ~STXMImage.threshold
      ~STXMImage.threshold_isodata
      ~STXMImage.threshold_li
      ~STXMImage.threshold_local
      ~STXMImage.threshold_mean
      ~STXMImage.threshold_minimum
      ~STXMImage.threshold_minmax
      ~STXMImage.threshold_multiotsu
      ~STXMImage.threshold_niblack
      ~STXMImage.threshold_otsu
      ~STXMImage.threshold_percentile
      ~STXMImage.threshold_sauvola
      ~STXMImage.threshold_triangle
      ~STXMImage.threshold_yen
      ~STXMImage.to_device
      ~STXMImage.tobytes
      ~STXMImage.tofile
      ~STXMImage.toflex
      ~STXMImage.tolist
      ~STXMImage.torecords
      ~STXMImage.tostring
      ~STXMImage.trace
      ~STXMImage.translate
      ~STXMImage.translate_limits
      ~STXMImage.transpose
      ~STXMImage.try_all_threshold
      ~STXMImage.uniform_filter
      ~STXMImage.uniform_filter1d
      ~STXMImage.unique_rows
      ~STXMImage.unshare_mask
      ~STXMImage.unsharp_mask
      ~STXMImage.unsupervised_wiener
      ~STXMImage.unwrap_phase
      ~STXMImage.update
      ~STXMImage.use_plugin
      ~STXMImage.value_indices
      ~STXMImage.values
      ~STXMImage.var
      ~STXMImage.variance
      ~STXMImage.view
      ~STXMImage.view_as_blocks
      ~STXMImage.view_as_windows
      ~STXMImage.warp
      ~STXMImage.warp_coords
      ~STXMImage.warp_polar
      ~STXMImage.watershed
      ~STXMImage.watershed_ift
      ~STXMImage.white_tophat
      ~STXMImage.wiener
      ~STXMImage.window
      ~STXMImage.windowed_histogram
      ~STXMImage.xyz2lab
      ~STXMImage.xyz2luv
      ~STXMImage.xyz2rgb
      ~STXMImage.xyz_tristimulus_values
      ~STXMImage.ycbcr2rgb
      ~STXMImage.ydbdr2rgb
      ~STXMImage.yiq2rgb
      ~STXMImage.ypbpr2rgb
      ~STXMImage.yuv2rgb
      ~STXMImage.zoom

   .. rubric:: Attributes Documentation

   .. autoattribute:: CCW
   .. autoattribute:: CW
   .. autoattribute:: T
   .. autoattribute:: aspect
   .. autoattribute:: base
   .. autoattribute:: baseclass
   .. autoattribute:: centre
   .. autoattribute:: clone
   .. autoattribute:: ctypes
   .. autoattribute:: data
   .. autoattribute:: debug
   .. autoattribute:: device
   .. autoattribute:: draw
   .. autoattribute:: dtype
   .. autoattribute:: filename
   .. autoattribute:: fill_value
   .. autoattribute:: flags
   .. autoattribute:: flat
   .. autoattribute:: flip_h
   .. autoattribute:: flip_v
   .. autoattribute:: fmts
   .. autoattribute:: hardmask
   .. autoattribute:: imag
   .. autoattribute:: image
   .. autoattribute:: itemset
   .. autoattribute:: itemsize
   .. autoattribute:: mT
   .. autoattribute:: mask
   .. autoattribute:: max_box
   .. autoattribute:: metadata
   .. autoattribute:: mime_type
   .. autoattribute:: nbytes
   .. autoattribute:: ndim
   .. autoattribute:: newbyteorder
   .. autoattribute:: polarization
   .. autoattribute:: priority
   .. autoattribute:: real
   .. autoattribute:: recordmask
   .. autoattribute:: shape
   .. autoattribute:: sharedmask
   .. autoattribute:: size
   .. autoattribute:: strides
   .. autoattribute:: title

   .. rubric:: Methods Documentation

   .. automethod:: AffineTransform
   .. automethod:: BRIEF
   .. automethod:: CENSURE
   .. automethod:: Cascade
   .. automethod:: CircleModel
   .. automethod:: EllipseModel
   .. automethod:: EssentialMatrixTransform
   .. automethod:: EuclideanTransform
   .. automethod:: FundamentalMatrixTransform
   .. automethod:: ImageCollection
   .. automethod:: LPIFilter2D
   .. automethod:: LineModelND
   .. automethod:: MCP
   .. automethod:: MCP_Connect
   .. automethod:: MCP_Flexible
   .. automethod:: MCP_Geometric
   .. automethod:: MultiImage
   .. automethod:: ORB
   .. automethod:: PiecewiseAffineTransform
   .. automethod:: PolynomialTransform
   .. automethod:: ProjectiveTransform
   .. automethod:: RAG
   .. automethod:: SIFT
   .. automethod:: SimilarityTransform
   .. automethod:: Stoner__Image__imagefuncs__adjust_contrast
   .. automethod:: Stoner__Image__imagefuncs__align
   .. automethod:: Stoner__Image__imagefuncs__asarray
   .. automethod:: Stoner__Image__imagefuncs__asfloat
   .. automethod:: Stoner__Image__imagefuncs__asint
   .. automethod:: Stoner__Image__imagefuncs__clip_intensity
   .. automethod:: Stoner__Image__imagefuncs__clip_neg
   .. automethod:: Stoner__Image__imagefuncs__convert
   .. automethod:: Stoner__Image__imagefuncs__correct_drift
   .. automethod:: Stoner__Image__imagefuncs__crop
   .. automethod:: Stoner__Image__imagefuncs__denoise
   .. automethod:: Stoner__Image__imagefuncs__do_nothing
   .. automethod:: Stoner__Image__imagefuncs__dtype_limits
   .. automethod:: Stoner__Image__imagefuncs__fft
   .. automethod:: Stoner__Image__imagefuncs__filter_image
   .. automethod:: Stoner__Image__imagefuncs__gridimage
   .. automethod:: Stoner__Image__imagefuncs__hist
   .. automethod:: Stoner__Image__imagefuncs__imshow
   .. automethod:: Stoner__Image__imagefuncs__level_image
   .. automethod:: Stoner__Image__imagefuncs__normalise
   .. automethod:: Stoner__Image__imagefuncs__plot_histogram
   .. automethod:: Stoner__Image__imagefuncs__profile_line
   .. automethod:: Stoner__Image__imagefuncs__quantize
   .. automethod:: Stoner__Image__imagefuncs__radial_coordinates
   .. automethod:: Stoner__Image__imagefuncs__radial_profile
   .. automethod:: Stoner__Image__imagefuncs__remove_outliers
   .. automethod:: Stoner__Image__imagefuncs__rotate
   .. automethod:: Stoner__Image__imagefuncs__save
   .. automethod:: Stoner__Image__imagefuncs__save_npy
   .. automethod:: Stoner__Image__imagefuncs__save_png
   .. automethod:: Stoner__Image__imagefuncs__save_tiff
   .. automethod:: Stoner__Image__imagefuncs__sgolay2d
   .. automethod:: Stoner__Image__imagefuncs__span
   .. automethod:: Stoner__Image__imagefuncs__subtract_image
   .. automethod:: Stoner__Image__imagefuncs__threshold_minmax
   .. automethod:: Stoner__Image__imagefuncs__translate
   .. automethod:: Stoner__Image__imagefuncs__translate_limits
   .. automethod:: ThinPlateSplineTransform
   .. automethod:: active_contour
   .. automethod:: adjust_contrast
   .. automethod:: adjust_gamma
   .. automethod:: adjust_log
   .. automethod:: adjust_sigmoid
   .. automethod:: affine_transform
   .. automethod:: align
   .. automethod:: all
   .. automethod:: anom
   .. automethod:: any
   .. automethod:: apply_hysteresis_threshold
   .. automethod:: apply_parallel
   .. automethod:: approximate_polygon
   .. automethod:: area_closing
   .. automethod:: area_opening
   .. automethod:: argmax
   .. automethod:: argmin
   .. automethod:: argpartition
   .. automethod:: argsort
   .. automethod:: asarray
   .. automethod:: asfloat
   .. automethod:: asint
   .. automethod:: astype
   .. automethod:: autolevel
   .. automethod:: autolevel_percentile
   .. automethod:: ball
   .. automethod:: ball_kernel
   .. automethod:: binary_closing
   .. automethod:: binary_dilation
   .. automethod:: binary_erosion
   .. automethod:: binary_fill_holes
   .. automethod:: binary_hit_or_miss
   .. automethod:: binary_opening
   .. automethod:: binary_propagation
   .. automethod:: black_tophat
   .. automethod:: blob_dog
   .. automethod:: blob_doh
   .. automethod:: blob_log
   .. automethod:: block_reduce
   .. automethod:: blur_effect
   .. automethod:: butterworth
   .. automethod:: byteswap
   .. automethod:: calibrate_denoiser
   .. automethod:: call_plugin
   .. automethod:: canny
   .. automethod:: center_of_mass
   .. automethod:: central_pixel
   .. automethod:: centroid
   .. automethod:: chan_vese
   .. automethod:: checkerboard_level_set
   .. automethod:: choose
   .. automethod:: clear
   .. automethod:: clear_border
   .. automethod:: clip
   .. automethod:: clip_intensity
   .. automethod:: clip_neg
   .. automethod:: closing
   .. automethod:: combine_stains
   .. automethod:: compare_images
   .. automethod:: compress
   .. automethod:: compressed
   .. automethod:: concatenate_images
   .. automethod:: conj
   .. automethod:: conjugate
   .. automethod:: convert
   .. automethod:: convert_colorspace
   .. automethod:: convex_hull_image
   .. automethod:: convex_hull_object
   .. automethod:: convolve
   .. automethod:: convolve1d
   .. automethod:: copy
   .. automethod:: corner_fast
   .. automethod:: corner_foerstner
   .. automethod:: corner_harris
   .. automethod:: corner_kitchen_rosenfeld
   .. automethod:: corner_moravec
   .. automethod:: corner_orientations
   .. automethod:: corner_peaks
   .. automethod:: corner_shi_tomasi
   .. automethod:: corner_subpix
   .. automethod:: correct_drift
   .. automethod:: correlate
   .. automethod:: correlate1d
   .. automethod:: correlate_sparse
   .. automethod:: count
   .. automethod:: crop
   .. automethod:: cube
   .. automethod:: cumprod
   .. automethod:: cumsum
   .. automethod:: cumulative_distribution
   .. automethod:: cut_normalized
   .. automethod:: cut_threshold
   .. automethod:: cycle_spin
   .. automethod:: daisy
   .. automethod:: deltaE_cie76
   .. automethod:: deltaE_ciede2000
   .. automethod:: deltaE_ciede94
   .. automethod:: deltaE_cmc
   .. automethod:: denoise
   .. automethod:: denoise_bilateral
   .. automethod:: denoise_invariant
   .. automethod:: denoise_nl_means
   .. automethod:: denoise_tv_bregman
   .. automethod:: denoise_tv_chambolle
   .. automethod:: denoise_wavelet
   .. automethod:: diagonal
   .. automethod:: diameter_closing
   .. automethod:: diameter_opening
   .. automethod:: diamond
   .. automethod:: difference_of_gaussians
   .. automethod:: dilation
   .. automethod:: disk
   .. automethod:: disk_level_set
   .. automethod:: distance_transform_bf
   .. automethod:: distance_transform_cdt
   .. automethod:: distance_transform_edt
   .. automethod:: do_nothing
   .. automethod:: dot
   .. automethod:: downscale_local_mean
   .. automethod:: draw_haar_like_feature
   .. automethod:: draw_multiblock_lbp
   .. automethod:: dtype_limits
   .. automethod:: dump
   .. automethod:: dumps
   .. automethod:: ellipse
   .. automethod:: ellipsoid_kernel
   .. automethod:: enhance_contrast
   .. automethod:: enhance_contrast_percentile
   .. automethod:: entropy
   .. automethod:: equalize
   .. automethod:: equalize_adapthist
   .. automethod:: equalize_hist
   .. automethod:: erosion
   .. automethod:: estimate_sigma
   .. automethod:: estimate_transform
   .. automethod:: euler_number
   .. automethod:: expand_labels
   .. automethod:: extrema
   .. automethod:: farid
   .. automethod:: farid_h
   .. automethod:: farid_v
   .. automethod:: felzenszwalb
   .. automethod:: fft
   .. automethod:: fill
   .. automethod:: filled
   .. automethod:: filter_forward
   .. automethod:: filter_image
   .. automethod:: filter_inverse
   .. automethod:: find_available_plugins
   .. automethod:: find_boundaries
   .. automethod:: find_contours
   .. automethod:: find_objects
   .. automethod:: fisher_vector
   .. automethod:: flatten
   .. automethod:: flood
   .. automethod:: flood_fill
   .. automethod:: footprint_from_sequence
   .. automethod:: footprint_rectangle
   .. automethod:: fourier_ellipsoid
   .. automethod:: fourier_gaussian
   .. automethod:: fourier_shift
   .. automethod:: fourier_uniform
   .. automethod:: frangi
   .. automethod:: frt2
   .. automethod:: gabor
   .. automethod:: gabor_kernel
   .. automethod:: gaussian
   .. automethod:: gaussian_filter
   .. automethod:: gaussian_filter1d
   .. automethod:: gaussian_gradient_magnitude
   .. automethod:: gaussian_laplace
   .. automethod:: generate_binary_structure
   .. automethod:: generic_filter
   .. automethod:: generic_filter1d
   .. automethod:: generic_gradient_magnitude
   .. automethod:: generic_laplace
   .. automethod:: geometric_mean
   .. automethod:: geometric_transform
   .. automethod:: get
   .. automethod:: get_filename
   .. automethod:: get_fill_value
   .. automethod:: get_imag
   .. automethod:: get_real
   .. automethod:: getfield
   .. automethod:: gradient
   .. automethod:: gradient_percentile
   .. automethod:: gray2rgb
   .. automethod:: gray2rgba
   .. automethod:: graycomatrix
   .. automethod:: graycoprops
   .. automethod:: grey_closing
   .. automethod:: grey_dilation
   .. automethod:: grey_erosion
   .. automethod:: grey_opening
   .. automethod:: grid_points_in_poly
   .. automethod:: gridimage
   .. automethod:: h_maxima
   .. automethod:: h_minima
   .. automethod:: haar_like_feature
   .. automethod:: haar_like_feature_coord
   .. automethod:: harden_mask
   .. automethod:: hed2rgb
   .. automethod:: hessian
   .. automethod:: hessian_matrix
   .. automethod:: hessian_matrix_det
   .. automethod:: hessian_matrix_eigvals
   .. automethod:: hist
   .. automethod:: histogram
   .. automethod:: hog
   .. automethod:: hough_circle
   .. automethod:: hough_circle_peaks
   .. automethod:: hough_ellipse
   .. automethod:: hough_line
   .. automethod:: hough_line_peaks
   .. automethod:: hsv2rgb
   .. automethod:: ids
   .. automethod:: ifrt2
   .. automethod:: img_as_bool
   .. automethod:: img_as_float
   .. automethod:: img_as_float32
   .. automethod:: img_as_float64
   .. automethod:: img_as_int
   .. automethod:: img_as_ubyte
   .. automethod:: img_as_uint
   .. automethod:: imread
   .. automethod:: imread_collection
   .. automethod:: imread_collection_wrapper
   .. automethod:: imsave
   .. automethod:: imshow
   .. automethod:: imshow_collection
   .. automethod:: inertia_tensor
   .. automethod:: inertia_tensor_eigvals
   .. automethod:: inpaint_biharmonic
   .. automethod:: integral_image
   .. automethod:: integrate
   .. automethod:: intersection_coeff
   .. automethod:: inverse_gaussian_gradient
   .. automethod:: invert
   .. automethod:: iradon
   .. automethod:: iradon_sart
   .. automethod:: is_low_contrast
   .. automethod:: iscontiguous
   .. automethod:: isotropic_closing
   .. automethod:: isotropic_dilation
   .. automethod:: isotropic_erosion
   .. automethod:: isotropic_opening
   .. automethod:: item
   .. automethod:: items
   .. automethod:: iterate_structure
   .. automethod:: join_segmentations
   .. automethod:: keys
   .. automethod:: lab2lch
   .. automethod:: lab2rgb
   .. automethod:: lab2xyz
   .. automethod:: label
   .. automethod:: label2rgb
   .. automethod:: label_points
   .. automethod:: labeled_comprehension
   .. automethod:: laplace
   .. automethod:: lch2lab
   .. automethod:: learn_gmm
   .. automethod:: level_image
   .. automethod:: load
   .. automethod:: load_sift
   .. automethod:: load_surf
   .. automethod:: local_binary_pattern
   .. automethod:: local_maxima
   .. automethod:: local_minima
   .. automethod:: lookfor
   .. automethod:: luv2rgb
   .. automethod:: luv2xyz
   .. automethod:: majority
   .. automethod:: manders_coloc_coeff
   .. automethod:: manders_overlap_coeff
   .. automethod:: map_array
   .. automethod:: map_coordinates
   .. automethod:: marching_cubes
   .. automethod:: mark_boundaries
   .. automethod:: match_descriptors
   .. automethod:: match_histograms
   .. automethod:: match_template
   .. automethod:: matrix_transform
   .. automethod:: max
   .. automethod:: max_tree
   .. automethod:: max_tree_local_maxima
   .. automethod:: maximum
   .. automethod:: maximum_filter
   .. automethod:: maximum_filter1d
   .. automethod:: maximum_position
   .. automethod:: mean
   .. automethod:: mean_bilateral
   .. automethod:: mean_percentile
   .. automethod:: medial_axis
   .. automethod:: median
   .. automethod:: median_filter
   .. automethod:: meijering
   .. automethod:: merge_hierarchical
   .. automethod:: mesh_surface_area
   .. automethod:: min
   .. automethod:: minimum
   .. automethod:: minimum_filter
   .. automethod:: minimum_filter1d
   .. automethod:: minimum_position
   .. automethod:: mirror_footprint
   .. automethod:: modal
   .. automethod:: moments
   .. automethod:: moments_central
   .. automethod:: moments_coords
   .. automethod:: moments_coords_central
   .. automethod:: moments_hu
   .. automethod:: moments_normalized
   .. automethod:: montage
   .. automethod:: morphological_chan_vese
   .. automethod:: morphological_geodesic_active_contour
   .. automethod:: morphological_gradient
   .. automethod:: morphological_laplace
   .. automethod:: multiblock_lbp
   .. automethod:: multiscale_basic_features
   .. automethod:: noise_filter
   .. automethod:: nonzero
   .. automethod:: normalise
   .. automethod:: octagon
   .. automethod:: octahedron
   .. automethod:: opening
   .. automethod:: order_angles_golden_ratio
   .. automethod:: otsu
   .. automethod:: pad_footprint
   .. automethod:: partition
   .. automethod:: peak_local_max
   .. automethod:: pearson_corr_coeff
   .. automethod:: percentile
   .. automethod:: percentile_filter
   .. automethod:: perimeter
   .. automethod:: perimeter_crofton
   .. automethod:: pixel_graph
   .. automethod:: plot_histogram
   .. automethod:: plot_matched_features
   .. automethod:: plugin_info
   .. automethod:: plugin_order
   .. automethod:: points_in_poly
   .. automethod:: pop
   .. automethod:: pop_bilateral
   .. automethod:: pop_percentile
   .. automethod:: popitem
   .. automethod:: prewitt
   .. automethod:: prewitt_h
   .. automethod:: prewitt_v
   .. automethod:: probabilistic_hough_line
   .. automethod:: prod
   .. automethod:: product
   .. automethod:: profile_line
   .. automethod:: ptp
   .. automethod:: push
   .. automethod:: put
   .. automethod:: pyramid_expand
   .. automethod:: pyramid_gaussian
   .. automethod:: pyramid_laplacian
   .. automethod:: pyramid_reduce
   .. automethod:: quantize
   .. automethod:: quickshift
   .. automethod:: radial_coordinates
   .. automethod:: radial_profile
   .. automethod:: radon
   .. automethod:: rag_boundary
   .. automethod:: rag_mean_color
   .. automethod:: random_noise
   .. automethod:: random_walker
   .. automethod:: rank_filter
   .. automethod:: rank_order
   .. automethod:: ransac
   .. automethod:: ravel
   .. automethod:: reconstruction
   .. automethod:: rectangle
   .. automethod:: regionprops
   .. automethod:: regionprops_table
   .. automethod:: regular_grid
   .. automethod:: regular_seeds
   .. automethod:: relabel_sequential
   .. automethod:: remove_objects_by_distance
   .. automethod:: remove_outliers
   .. automethod:: remove_small_holes
   .. automethod:: remove_small_objects
   .. automethod:: repeat
   .. automethod:: rescale
   .. automethod:: rescale_intensity
   .. automethod:: reset_plugins
   .. automethod:: reshape
   .. automethod:: resize
   .. automethod:: resize_local_mean
   .. automethod:: rgb2gray
   .. automethod:: rgb2hed
   .. automethod:: rgb2hsv
   .. automethod:: rgb2lab
   .. automethod:: rgb2luv
   .. automethod:: rgb2rgbcie
   .. automethod:: rgb2xyz
   .. automethod:: rgb2ycbcr
   .. automethod:: rgb2ydbdr
   .. automethod:: rgb2yiq
   .. automethod:: rgb2ypbpr
   .. automethod:: rgb2yuv
   .. automethod:: rgba2rgb
   .. automethod:: rgbcie2rgb
   .. automethod:: richardson_lucy
   .. automethod:: roberts
   .. automethod:: roberts_neg_diag
   .. automethod:: roberts_pos_diag
   .. automethod:: rolling_ball
   .. automethod:: rotate
   .. automethod:: round
   .. automethod:: route_through_array
   .. automethod:: sato
   .. automethod:: save
   .. automethod:: save_npy
   .. automethod:: save_png
   .. automethod:: save_tiff
   .. automethod:: scharr
   .. automethod:: scharr_h
   .. automethod:: scharr_v
   .. automethod:: scipy__ndimage___filters__convolve
   .. automethod:: scipy__ndimage___filters__convolve1d
   .. automethod:: scipy__ndimage___filters__correlate
   .. automethod:: scipy__ndimage___filters__correlate1d
   .. automethod:: scipy__ndimage___filters__gaussian_filter
   .. automethod:: scipy__ndimage___filters__gaussian_filter1d
   .. automethod:: scipy__ndimage___filters__gaussian_gradient_magnitude
   .. automethod:: scipy__ndimage___filters__gaussian_laplace
   .. automethod:: scipy__ndimage___filters__generic_filter
   .. automethod:: scipy__ndimage___filters__generic_filter1d
   .. automethod:: scipy__ndimage___filters__generic_gradient_magnitude
   .. automethod:: scipy__ndimage___filters__generic_laplace
   .. automethod:: scipy__ndimage___filters__laplace
   .. automethod:: scipy__ndimage___filters__maximum_filter
   .. automethod:: scipy__ndimage___filters__maximum_filter1d
   .. automethod:: scipy__ndimage___filters__median_filter
   .. automethod:: scipy__ndimage___filters__minimum_filter
   .. automethod:: scipy__ndimage___filters__minimum_filter1d
   .. automethod:: scipy__ndimage___filters__percentile_filter
   .. automethod:: scipy__ndimage___filters__prewitt
   .. automethod:: scipy__ndimage___filters__rank_filter
   .. automethod:: scipy__ndimage___filters__sobel
   .. automethod:: scipy__ndimage___filters__uniform_filter
   .. automethod:: scipy__ndimage___filters__uniform_filter1d
   .. automethod:: scipy__ndimage___fourier__fourier_ellipsoid
   .. automethod:: scipy__ndimage___fourier__fourier_gaussian
   .. automethod:: scipy__ndimage___fourier__fourier_shift
   .. automethod:: scipy__ndimage___fourier__fourier_uniform
   .. automethod:: scipy__ndimage___interpolation__affine_transform
   .. automethod:: scipy__ndimage___interpolation__geometric_transform
   .. automethod:: scipy__ndimage___interpolation__map_coordinates
   .. automethod:: scipy__ndimage___interpolation__rotate
   .. automethod:: scipy__ndimage___interpolation__shift
   .. automethod:: scipy__ndimage___interpolation__spline_filter
   .. automethod:: scipy__ndimage___interpolation__spline_filter1d
   .. automethod:: scipy__ndimage___interpolation__zoom
   .. automethod:: scipy__ndimage___measurements__center_of_mass
   .. automethod:: scipy__ndimage___measurements__extrema
   .. automethod:: scipy__ndimage___measurements__find_objects
   .. automethod:: scipy__ndimage___measurements__histogram
   .. automethod:: scipy__ndimage___measurements__label
   .. automethod:: scipy__ndimage___measurements__labeled_comprehension
   .. automethod:: scipy__ndimage___measurements__maximum
   .. automethod:: scipy__ndimage___measurements__maximum_position
   .. automethod:: scipy__ndimage___measurements__mean
   .. automethod:: scipy__ndimage___measurements__median
   .. automethod:: scipy__ndimage___measurements__minimum
   .. automethod:: scipy__ndimage___measurements__minimum_position
   .. automethod:: scipy__ndimage___measurements__standard_deviation
   .. automethod:: scipy__ndimage___measurements__sum
   .. automethod:: scipy__ndimage___measurements__sum_labels
   .. automethod:: scipy__ndimage___measurements__value_indices
   .. automethod:: scipy__ndimage___measurements__variance
   .. automethod:: scipy__ndimage___measurements__watershed_ift
   .. automethod:: scipy__ndimage___morphology__binary_closing
   .. automethod:: scipy__ndimage___morphology__binary_dilation
   .. automethod:: scipy__ndimage___morphology__binary_erosion
   .. automethod:: scipy__ndimage___morphology__binary_fill_holes
   .. automethod:: scipy__ndimage___morphology__binary_hit_or_miss
   .. automethod:: scipy__ndimage___morphology__binary_opening
   .. automethod:: scipy__ndimage___morphology__binary_propagation
   .. automethod:: scipy__ndimage___morphology__black_tophat
   .. automethod:: scipy__ndimage___morphology__distance_transform_bf
   .. automethod:: scipy__ndimage___morphology__distance_transform_cdt
   .. automethod:: scipy__ndimage___morphology__distance_transform_edt
   .. automethod:: scipy__ndimage___morphology__generate_binary_structure
   .. automethod:: scipy__ndimage___morphology__grey_closing
   .. automethod:: scipy__ndimage___morphology__grey_dilation
   .. automethod:: scipy__ndimage___morphology__grey_erosion
   .. automethod:: scipy__ndimage___morphology__grey_opening
   .. automethod:: scipy__ndimage___morphology__iterate_structure
   .. automethod:: scipy__ndimage___morphology__morphological_gradient
   .. automethod:: scipy__ndimage___morphology__morphological_laplace
   .. automethod:: scipy__ndimage___morphology__white_tophat
   .. automethod:: searchsorted
   .. automethod:: separate_stains
   .. automethod:: set_fill_value
   .. automethod:: setdefault
   .. automethod:: setfield
   .. automethod:: setflags
   .. automethod:: sgolay2d
   .. automethod:: shannon_entropy
   .. automethod:: shape_index
   .. automethod:: shift
   .. automethod:: shortest_path
   .. automethod:: show
   .. automethod:: show_rag
   .. automethod:: shrink_mask
   .. automethod:: skeletonize
   .. automethod:: skimage___shared__filters__gaussian
   .. automethod:: skimage__color__colorconv__combine_stains
   .. automethod:: skimage__color__colorconv__convert_colorspace
   .. automethod:: skimage__color__colorconv__gray2rgb
   .. automethod:: skimage__color__colorconv__gray2rgba
   .. automethod:: skimage__color__colorconv__hed2rgb
   .. automethod:: skimage__color__colorconv__hsv2rgb
   .. automethod:: skimage__color__colorconv__lab2lch
   .. automethod:: skimage__color__colorconv__lab2rgb
   .. automethod:: skimage__color__colorconv__lab2xyz
   .. automethod:: skimage__color__colorconv__lch2lab
   .. automethod:: skimage__color__colorconv__luv2rgb
   .. automethod:: skimage__color__colorconv__luv2xyz
   .. automethod:: skimage__color__colorconv__rgb2gray
   .. automethod:: skimage__color__colorconv__rgb2hed
   .. automethod:: skimage__color__colorconv__rgb2hsv
   .. automethod:: skimage__color__colorconv__rgb2lab
   .. automethod:: skimage__color__colorconv__rgb2luv
   .. automethod:: skimage__color__colorconv__rgb2rgbcie
   .. automethod:: skimage__color__colorconv__rgb2xyz
   .. automethod:: skimage__color__colorconv__rgb2ycbcr
   .. automethod:: skimage__color__colorconv__rgb2ydbdr
   .. automethod:: skimage__color__colorconv__rgb2yiq
   .. automethod:: skimage__color__colorconv__rgb2ypbpr
   .. automethod:: skimage__color__colorconv__rgb2yuv
   .. automethod:: skimage__color__colorconv__rgba2rgb
   .. automethod:: skimage__color__colorconv__rgbcie2rgb
   .. automethod:: skimage__color__colorconv__separate_stains
   .. automethod:: skimage__color__colorconv__xyz2lab
   .. automethod:: skimage__color__colorconv__xyz2luv
   .. automethod:: skimage__color__colorconv__xyz2rgb
   .. automethod:: skimage__color__colorconv__xyz_tristimulus_values
   .. automethod:: skimage__color__colorconv__ycbcr2rgb
   .. automethod:: skimage__color__colorconv__ydbdr2rgb
   .. automethod:: skimage__color__colorconv__yiq2rgb
   .. automethod:: skimage__color__colorconv__ypbpr2rgb
   .. automethod:: skimage__color__colorconv__yuv2rgb
   .. automethod:: skimage__color__colorlabel__label2rgb
   .. automethod:: skimage__color__delta_e__deltaE_cie76
   .. automethod:: skimage__color__delta_e__deltaE_ciede2000
   .. automethod:: skimage__color__delta_e__deltaE_ciede94
   .. automethod:: skimage__color__delta_e__deltaE_cmc
   .. automethod:: skimage__exposure___adapthist__equalize_adapthist
   .. automethod:: skimage__exposure__exposure__adjust_gamma
   .. automethod:: skimage__exposure__exposure__adjust_log
   .. automethod:: skimage__exposure__exposure__adjust_sigmoid
   .. automethod:: skimage__exposure__exposure__cumulative_distribution
   .. automethod:: skimage__exposure__exposure__equalize_hist
   .. automethod:: skimage__exposure__exposure__histogram
   .. automethod:: skimage__exposure__exposure__is_low_contrast
   .. automethod:: skimage__exposure__exposure__rescale_intensity
   .. automethod:: skimage__exposure__histogram_matching__match_histograms
   .. automethod:: skimage__feature___basic_features__multiscale_basic_features
   .. automethod:: skimage__feature___canny__canny
   .. automethod:: skimage__feature___cascade__Cascade
   .. automethod:: skimage__feature___daisy__daisy
   .. automethod:: skimage__feature___fisher_vector__fisher_vector
   .. automethod:: skimage__feature___fisher_vector__learn_gmm
   .. automethod:: skimage__feature___hog__hog
   .. automethod:: skimage__feature__blob__blob_dog
   .. automethod:: skimage__feature__blob__blob_doh
   .. automethod:: skimage__feature__blob__blob_log
   .. automethod:: skimage__feature__brief__BRIEF
   .. automethod:: skimage__feature__censure__CENSURE
   .. automethod:: skimage__feature__corner__corner_fast
   .. automethod:: skimage__feature__corner__corner_foerstner
   .. automethod:: skimage__feature__corner__corner_harris
   .. automethod:: skimage__feature__corner__corner_kitchen_rosenfeld
   .. automethod:: skimage__feature__corner__corner_moravec
   .. automethod:: skimage__feature__corner__corner_orientations
   .. automethod:: skimage__feature__corner__corner_peaks
   .. automethod:: skimage__feature__corner__corner_shi_tomasi
   .. automethod:: skimage__feature__corner__corner_subpix
   .. automethod:: skimage__feature__corner__hessian_matrix
   .. automethod:: skimage__feature__corner__hessian_matrix_det
   .. automethod:: skimage__feature__corner__hessian_matrix_eigvals
   .. automethod:: skimage__feature__corner__shape_index
   .. automethod:: skimage__feature__corner__structure_tensor
   .. automethod:: skimage__feature__corner__structure_tensor_eigenvalues
   .. automethod:: skimage__feature__haar__draw_haar_like_feature
   .. automethod:: skimage__feature__haar__haar_like_feature
   .. automethod:: skimage__feature__haar__haar_like_feature_coord
   .. automethod:: skimage__feature__match__match_descriptors
   .. automethod:: skimage__feature__orb__ORB
   .. automethod:: skimage__feature__peak__peak_local_max
   .. automethod:: skimage__feature__sift__SIFT
   .. automethod:: skimage__feature__template__match_template
   .. automethod:: skimage__feature__texture__draw_multiblock_lbp
   .. automethod:: skimage__feature__texture__graycomatrix
   .. automethod:: skimage__feature__texture__graycoprops
   .. automethod:: skimage__feature__texture__local_binary_pattern
   .. automethod:: skimage__feature__texture__multiblock_lbp
   .. automethod:: skimage__feature__util__plot_matched_features
   .. automethod:: skimage__filters___fft_based__butterworth
   .. automethod:: skimage__filters___gabor__gabor
   .. automethod:: skimage__filters___gabor__gabor_kernel
   .. automethod:: skimage__filters___gaussian__difference_of_gaussians
   .. automethod:: skimage__filters___median__median
   .. automethod:: skimage__filters___rank_order__rank_order
   .. automethod:: skimage__filters___sparse__correlate_sparse
   .. automethod:: skimage__filters___unsharp_mask__unsharp_mask
   .. automethod:: skimage__filters___window__window
   .. automethod:: skimage__filters__edges__farid
   .. automethod:: skimage__filters__edges__farid_h
   .. automethod:: skimage__filters__edges__farid_v
   .. automethod:: skimage__filters__edges__laplace
   .. automethod:: skimage__filters__edges__prewitt
   .. automethod:: skimage__filters__edges__prewitt_h
   .. automethod:: skimage__filters__edges__prewitt_v
   .. automethod:: skimage__filters__edges__roberts
   .. automethod:: skimage__filters__edges__roberts_neg_diag
   .. automethod:: skimage__filters__edges__roberts_pos_diag
   .. automethod:: skimage__filters__edges__scharr
   .. automethod:: skimage__filters__edges__scharr_h
   .. automethod:: skimage__filters__edges__scharr_v
   .. automethod:: skimage__filters__edges__sobel
   .. automethod:: skimage__filters__edges__sobel_h
   .. automethod:: skimage__filters__edges__sobel_v
   .. automethod:: skimage__filters__lpi_filter__LPIFilter2D
   .. automethod:: skimage__filters__lpi_filter__filter_forward
   .. automethod:: skimage__filters__lpi_filter__filter_inverse
   .. automethod:: skimage__filters__lpi_filter__wiener
   .. automethod:: skimage__filters__rank___percentile__autolevel_percentile
   .. automethod:: skimage__filters__rank___percentile__enhance_contrast_percentile
   .. automethod:: skimage__filters__rank___percentile__gradient_percentile
   .. automethod:: skimage__filters__rank___percentile__mean_percentile
   .. automethod:: skimage__filters__rank___percentile__percentile
   .. automethod:: skimage__filters__rank___percentile__pop_percentile
   .. automethod:: skimage__filters__rank___percentile__subtract_mean_percentile
   .. automethod:: skimage__filters__rank___percentile__sum_percentile
   .. automethod:: skimage__filters__rank___percentile__threshold_percentile
   .. automethod:: skimage__filters__rank__bilateral__mean_bilateral
   .. automethod:: skimage__filters__rank__bilateral__pop_bilateral
   .. automethod:: skimage__filters__rank__bilateral__sum_bilateral
   .. automethod:: skimage__filters__rank__generic__autolevel
   .. automethod:: skimage__filters__rank__generic__enhance_contrast
   .. automethod:: skimage__filters__rank__generic__entropy
   .. automethod:: skimage__filters__rank__generic__equalize
   .. automethod:: skimage__filters__rank__generic__geometric_mean
   .. automethod:: skimage__filters__rank__generic__gradient
   .. automethod:: skimage__filters__rank__generic__majority
   .. automethod:: skimage__filters__rank__generic__maximum
   .. automethod:: skimage__filters__rank__generic__mean
   .. automethod:: skimage__filters__rank__generic__median
   .. automethod:: skimage__filters__rank__generic__minimum
   .. automethod:: skimage__filters__rank__generic__modal
   .. automethod:: skimage__filters__rank__generic__noise_filter
   .. automethod:: skimage__filters__rank__generic__otsu
   .. automethod:: skimage__filters__rank__generic__pop
   .. automethod:: skimage__filters__rank__generic__subtract_mean
   .. automethod:: skimage__filters__rank__generic__sum
   .. automethod:: skimage__filters__rank__generic__threshold
   .. automethod:: skimage__filters__rank__generic__windowed_histogram
   .. automethod:: skimage__filters__ridges__frangi
   .. automethod:: skimage__filters__ridges__hessian
   .. automethod:: skimage__filters__ridges__meijering
   .. automethod:: skimage__filters__ridges__sato
   .. automethod:: skimage__filters__thresholding__apply_hysteresis_threshold
   .. automethod:: skimage__filters__thresholding__threshold_isodata
   .. automethod:: skimage__filters__thresholding__threshold_li
   .. automethod:: skimage__filters__thresholding__threshold_local
   .. automethod:: skimage__filters__thresholding__threshold_mean
   .. automethod:: skimage__filters__thresholding__threshold_minimum
   .. automethod:: skimage__filters__thresholding__threshold_multiotsu
   .. automethod:: skimage__filters__thresholding__threshold_niblack
   .. automethod:: skimage__filters__thresholding__threshold_otsu
   .. automethod:: skimage__filters__thresholding__threshold_sauvola
   .. automethod:: skimage__filters__thresholding__threshold_triangle
   .. automethod:: skimage__filters__thresholding__threshold_yen
   .. automethod:: skimage__filters__thresholding__try_all_threshold
   .. automethod:: skimage__graph___graph__central_pixel
   .. automethod:: skimage__graph___graph__pixel_graph
   .. automethod:: skimage__graph___graph_cut__cut_normalized
   .. automethod:: skimage__graph___graph_cut__cut_threshold
   .. automethod:: skimage__graph___graph_merge__merge_hierarchical
   .. automethod:: skimage__graph___mcp__MCP
   .. automethod:: skimage__graph___mcp__MCP_Connect
   .. automethod:: skimage__graph___mcp__MCP_Flexible
   .. automethod:: skimage__graph___mcp__MCP_Geometric
   .. automethod:: skimage__graph___rag__RAG
   .. automethod:: skimage__graph___rag__rag_boundary
   .. automethod:: skimage__graph___rag__rag_mean_color
   .. automethod:: skimage__graph___rag__show_rag
   .. automethod:: skimage__graph__mcp__route_through_array
   .. automethod:: skimage__graph__spath__shortest_path
   .. automethod:: skimage__io___image_stack__pop
   .. automethod:: skimage__io___image_stack__push
   .. automethod:: skimage__io___io__imread
   .. automethod:: skimage__io___io__imread_collection
   .. automethod:: skimage__io___io__imsave
   .. automethod:: skimage__io___io__imshow
   .. automethod:: skimage__io___io__imshow_collection
   .. automethod:: skimage__io___io__show
   .. automethod:: skimage__io__collection__ImageCollection
   .. automethod:: skimage__io__collection__MultiImage
   .. automethod:: skimage__io__collection__concatenate_images
   .. automethod:: skimage__io__collection__imread_collection_wrapper
   .. automethod:: skimage__io__manage_plugins__call_plugin
   .. automethod:: skimage__io__manage_plugins__find_available_plugins
   .. automethod:: skimage__io__manage_plugins__plugin_info
   .. automethod:: skimage__io__manage_plugins__plugin_order
   .. automethod:: skimage__io__manage_plugins__reset_plugins
   .. automethod:: skimage__io__manage_plugins__use_plugin
   .. automethod:: skimage__io__sift__load_sift
   .. automethod:: skimage__io__sift__load_surf
   .. automethod:: skimage__measure___blur_effect__blur_effect
   .. automethod:: skimage__measure___colocalization__intersection_coeff
   .. automethod:: skimage__measure___colocalization__manders_coloc_coeff
   .. automethod:: skimage__measure___colocalization__manders_overlap_coeff
   .. automethod:: skimage__measure___colocalization__pearson_corr_coeff
   .. automethod:: skimage__measure___find_contours__find_contours
   .. automethod:: skimage__measure___label__label
   .. automethod:: skimage__measure___marching_cubes_lewiner__marching_cubes
   .. automethod:: skimage__measure___marching_cubes_lewiner__mesh_surface_area
   .. automethod:: skimage__measure___moments__centroid
   .. automethod:: skimage__measure___moments__inertia_tensor
   .. automethod:: skimage__measure___moments__inertia_tensor_eigvals
   .. automethod:: skimage__measure___moments__moments
   .. automethod:: skimage__measure___moments__moments_central
   .. automethod:: skimage__measure___moments__moments_coords
   .. automethod:: skimage__measure___moments__moments_coords_central
   .. automethod:: skimage__measure___moments__moments_hu
   .. automethod:: skimage__measure___moments__moments_normalized
   .. automethod:: skimage__measure___polygon__approximate_polygon
   .. automethod:: skimage__measure___polygon__subdivide_polygon
   .. automethod:: skimage__measure___regionprops__regionprops
   .. automethod:: skimage__measure___regionprops__regionprops_table
   .. automethod:: skimage__measure___regionprops_utils__euler_number
   .. automethod:: skimage__measure___regionprops_utils__perimeter
   .. automethod:: skimage__measure___regionprops_utils__perimeter_crofton
   .. automethod:: skimage__measure__block__block_reduce
   .. automethod:: skimage__measure__entropy__shannon_entropy
   .. automethod:: skimage__measure__fit__CircleModel
   .. automethod:: skimage__measure__fit__EllipseModel
   .. automethod:: skimage__measure__fit__LineModelND
   .. automethod:: skimage__measure__fit__ransac
   .. automethod:: skimage__measure__pnpoly__grid_points_in_poly
   .. automethod:: skimage__measure__pnpoly__points_in_poly
   .. automethod:: skimage__measure__profile__profile_line
   .. automethod:: skimage__morphology___flood_fill__flood
   .. automethod:: skimage__morphology___flood_fill__flood_fill
   .. automethod:: skimage__morphology___skeletonize__medial_axis
   .. automethod:: skimage__morphology___skeletonize__skeletonize
   .. automethod:: skimage__morphology___skeletonize__thin
   .. automethod:: skimage__morphology__binary__binary_closing
   .. automethod:: skimage__morphology__binary__binary_dilation
   .. automethod:: skimage__morphology__binary__binary_erosion
   .. automethod:: skimage__morphology__binary__binary_opening
   .. automethod:: skimage__morphology__convex_hull__convex_hull_image
   .. automethod:: skimage__morphology__convex_hull__convex_hull_object
   .. automethod:: skimage__morphology__extrema__h_maxima
   .. automethod:: skimage__morphology__extrema__h_minima
   .. automethod:: skimage__morphology__extrema__local_maxima
   .. automethod:: skimage__morphology__extrema__local_minima
   .. automethod:: skimage__morphology__footprints__ball
   .. automethod:: skimage__morphology__footprints__cube
   .. automethod:: skimage__morphology__footprints__diamond
   .. automethod:: skimage__morphology__footprints__disk
   .. automethod:: skimage__morphology__footprints__ellipse
   .. automethod:: skimage__morphology__footprints__footprint_from_sequence
   .. automethod:: skimage__morphology__footprints__footprint_rectangle
   .. automethod:: skimage__morphology__footprints__mirror_footprint
   .. automethod:: skimage__morphology__footprints__octagon
   .. automethod:: skimage__morphology__footprints__octahedron
   .. automethod:: skimage__morphology__footprints__pad_footprint
   .. automethod:: skimage__morphology__footprints__rectangle
   .. automethod:: skimage__morphology__footprints__square
   .. automethod:: skimage__morphology__footprints__star
   .. automethod:: skimage__morphology__gray__black_tophat
   .. automethod:: skimage__morphology__gray__closing
   .. automethod:: skimage__morphology__gray__dilation
   .. automethod:: skimage__morphology__gray__erosion
   .. automethod:: skimage__morphology__gray__opening
   .. automethod:: skimage__morphology__gray__white_tophat
   .. automethod:: skimage__morphology__grayreconstruct__reconstruction
   .. automethod:: skimage__morphology__isotropic__isotropic_closing
   .. automethod:: skimage__morphology__isotropic__isotropic_dilation
   .. automethod:: skimage__morphology__isotropic__isotropic_erosion
   .. automethod:: skimage__morphology__isotropic__isotropic_opening
   .. automethod:: skimage__morphology__max_tree__area_closing
   .. automethod:: skimage__morphology__max_tree__area_opening
   .. automethod:: skimage__morphology__max_tree__diameter_closing
   .. automethod:: skimage__morphology__max_tree__diameter_opening
   .. automethod:: skimage__morphology__max_tree__max_tree
   .. automethod:: skimage__morphology__max_tree__max_tree_local_maxima
   .. automethod:: skimage__morphology__misc__remove_objects_by_distance
   .. automethod:: skimage__morphology__misc__remove_small_holes
   .. automethod:: skimage__morphology__misc__remove_small_objects
   .. automethod:: skimage__restoration___cycle_spin__cycle_spin
   .. automethod:: skimage__restoration___denoise__denoise_bilateral
   .. automethod:: skimage__restoration___denoise__denoise_tv_bregman
   .. automethod:: skimage__restoration___denoise__denoise_tv_chambolle
   .. automethod:: skimage__restoration___denoise__denoise_wavelet
   .. automethod:: skimage__restoration___denoise__estimate_sigma
   .. automethod:: skimage__restoration___rolling_ball__ball_kernel
   .. automethod:: skimage__restoration___rolling_ball__ellipsoid_kernel
   .. automethod:: skimage__restoration___rolling_ball__rolling_ball
   .. automethod:: skimage__restoration__deconvolution__richardson_lucy
   .. automethod:: skimage__restoration__deconvolution__unsupervised_wiener
   .. automethod:: skimage__restoration__deconvolution__wiener
   .. automethod:: skimage__restoration__inpaint__inpaint_biharmonic
   .. automethod:: skimage__restoration__j_invariant__calibrate_denoiser
   .. automethod:: skimage__restoration__j_invariant__denoise_invariant
   .. automethod:: skimage__restoration__non_local_means__denoise_nl_means
   .. automethod:: skimage__restoration__unwrap__unwrap_phase
   .. automethod:: skimage__segmentation___chan_vese__chan_vese
   .. automethod:: skimage__segmentation___clear_border__clear_border
   .. automethod:: skimage__segmentation___expand_labels__expand_labels
   .. automethod:: skimage__segmentation___felzenszwalb__felzenszwalb
   .. automethod:: skimage__segmentation___join__join_segmentations
   .. automethod:: skimage__segmentation___join__relabel_sequential
   .. automethod:: skimage__segmentation___quickshift__quickshift
   .. automethod:: skimage__segmentation___watershed__watershed
   .. automethod:: skimage__segmentation__active_contour_model__active_contour
   .. automethod:: skimage__segmentation__boundaries__find_boundaries
   .. automethod:: skimage__segmentation__boundaries__mark_boundaries
   .. automethod:: skimage__segmentation__morphsnakes__checkerboard_level_set
   .. automethod:: skimage__segmentation__morphsnakes__disk_level_set
   .. automethod:: skimage__segmentation__morphsnakes__inverse_gaussian_gradient
   .. automethod:: skimage__segmentation__morphsnakes__morphological_chan_vese
   .. automethod:: skimage__segmentation__morphsnakes__morphological_geodesic_active_contour
   .. automethod:: skimage__segmentation__random_walker_segmentation__random_walker
   .. automethod:: skimage__segmentation__slic_superpixels__slic
   .. automethod:: skimage__transform___geometric__AffineTransform
   .. automethod:: skimage__transform___geometric__EssentialMatrixTransform
   .. automethod:: skimage__transform___geometric__EuclideanTransform
   .. automethod:: skimage__transform___geometric__FundamentalMatrixTransform
   .. automethod:: skimage__transform___geometric__PiecewiseAffineTransform
   .. automethod:: skimage__transform___geometric__PolynomialTransform
   .. automethod:: skimage__transform___geometric__ProjectiveTransform
   .. automethod:: skimage__transform___geometric__SimilarityTransform
   .. automethod:: skimage__transform___geometric__estimate_transform
   .. automethod:: skimage__transform___geometric__matrix_transform
   .. automethod:: skimage__transform___thin_plate_splines__ThinPlateSplineTransform
   .. automethod:: skimage__transform___warps__downscale_local_mean
   .. automethod:: skimage__transform___warps__rescale
   .. automethod:: skimage__transform___warps__resize
   .. automethod:: skimage__transform___warps__resize_local_mean
   .. automethod:: skimage__transform___warps__rotate
   .. automethod:: skimage__transform___warps__swirl
   .. automethod:: skimage__transform___warps__warp
   .. automethod:: skimage__transform___warps__warp_coords
   .. automethod:: skimage__transform___warps__warp_polar
   .. automethod:: skimage__transform__finite_radon_transform__frt2
   .. automethod:: skimage__transform__finite_radon_transform__ifrt2
   .. automethod:: skimage__transform__hough_transform__hough_circle
   .. automethod:: skimage__transform__hough_transform__hough_circle_peaks
   .. automethod:: skimage__transform__hough_transform__hough_ellipse
   .. automethod:: skimage__transform__hough_transform__hough_line
   .. automethod:: skimage__transform__hough_transform__hough_line_peaks
   .. automethod:: skimage__transform__hough_transform__probabilistic_hough_line
   .. automethod:: skimage__transform__integral__integral_image
   .. automethod:: skimage__transform__integral__integrate
   .. automethod:: skimage__transform__pyramids__pyramid_expand
   .. automethod:: skimage__transform__pyramids__pyramid_gaussian
   .. automethod:: skimage__transform__pyramids__pyramid_laplacian
   .. automethod:: skimage__transform__pyramids__pyramid_reduce
   .. automethod:: skimage__transform__radon_transform__iradon
   .. automethod:: skimage__transform__radon_transform__iradon_sart
   .. automethod:: skimage__transform__radon_transform__order_angles_golden_ratio
   .. automethod:: skimage__transform__radon_transform__radon
   .. automethod:: skimage__util___invert__invert
   .. automethod:: skimage__util___label__label_points
   .. automethod:: skimage__util___map_array__map_array
   .. automethod:: skimage__util___montage__montage
   .. automethod:: skimage__util___regular_grid__regular_grid
   .. automethod:: skimage__util___regular_grid__regular_seeds
   .. automethod:: skimage__util___slice_along_axes__slice_along_axes
   .. automethod:: skimage__util__apply_parallel__apply_parallel
   .. automethod:: skimage__util__arraycrop__crop
   .. automethod:: skimage__util__compare__compare_images
   .. automethod:: skimage__util__dtype__dtype_limits
   .. automethod:: skimage__util__dtype__img_as_bool
   .. automethod:: skimage__util__dtype__img_as_float
   .. automethod:: skimage__util__dtype__img_as_float32
   .. automethod:: skimage__util__dtype__img_as_float64
   .. automethod:: skimage__util__dtype__img_as_int
   .. automethod:: skimage__util__dtype__img_as_ubyte
   .. automethod:: skimage__util__dtype__img_as_uint
   .. automethod:: skimage__util__lookfor__lookfor
   .. automethod:: skimage__util__noise__random_noise
   .. automethod:: skimage__util__shape__view_as_blocks
   .. automethod:: skimage__util__shape__view_as_windows
   .. automethod:: skimage__util__unique__unique_rows
   .. automethod:: slic
   .. automethod:: slice_along_axes
   .. automethod:: sobel
   .. automethod:: sobel_h
   .. automethod:: sobel_v
   .. automethod:: soften_mask
   .. automethod:: sort
   .. automethod:: span
   .. automethod:: spline_filter
   .. automethod:: spline_filter1d
   .. automethod:: square
   .. automethod:: squeeze
   .. automethod:: standard_deviation
   .. automethod:: star
   .. automethod:: std
   .. automethod:: structure_tensor
   .. automethod:: structure_tensor_eigenvalues
   .. automethod:: subdivide_polygon
   .. automethod:: subtract_image
   .. automethod:: subtract_mean
   .. automethod:: subtract_mean_percentile
   .. automethod:: sum
   .. automethod:: sum_bilateral
   .. automethod:: sum_labels
   .. automethod:: sum_percentile
   .. automethod:: swapaxes
   .. automethod:: swirl
   .. automethod:: take
   .. automethod:: thin
   .. automethod:: threshold
   .. automethod:: threshold_isodata
   .. automethod:: threshold_li
   .. automethod:: threshold_local
   .. automethod:: threshold_mean
   .. automethod:: threshold_minimum
   .. automethod:: threshold_minmax
   .. automethod:: threshold_multiotsu
   .. automethod:: threshold_niblack
   .. automethod:: threshold_otsu
   .. automethod:: threshold_percentile
   .. automethod:: threshold_sauvola
   .. automethod:: threshold_triangle
   .. automethod:: threshold_yen
   .. automethod:: to_device
   .. automethod:: tobytes
   .. automethod:: tofile
   .. automethod:: toflex
   .. automethod:: tolist
   .. automethod:: torecords
   .. automethod:: tostring
   .. automethod:: trace
   .. automethod:: translate
   .. automethod:: translate_limits
   .. automethod:: transpose
   .. automethod:: try_all_threshold
   .. automethod:: uniform_filter
   .. automethod:: uniform_filter1d
   .. automethod:: unique_rows
   .. automethod:: unshare_mask
   .. automethod:: unsharp_mask
   .. automethod:: unsupervised_wiener
   .. automethod:: unwrap_phase
   .. automethod:: update
   .. automethod:: use_plugin
   .. automethod:: value_indices
   .. automethod:: values
   .. automethod:: var
   .. automethod:: variance
   .. automethod:: view
   .. automethod:: view_as_blocks
   .. automethod:: view_as_windows
   .. automethod:: warp
   .. automethod:: warp_coords
   .. automethod:: warp_polar
   .. automethod:: watershed
   .. automethod:: watershed_ift
   .. automethod:: white_tophat
   .. automethod:: wiener
   .. automethod:: window
   .. automethod:: windowed_histogram
   .. automethod:: xyz2lab
   .. automethod:: xyz2luv
   .. automethod:: xyz2rgb
   .. automethod:: xyz_tristimulus_values
   .. automethod:: ycbcr2rgb
   .. automethod:: ydbdr2rgb
   .. automethod:: yiq2rgb
   .. automethod:: ypbpr2rgb
   .. automethod:: yuv2rgb
   .. automethod:: zoom
