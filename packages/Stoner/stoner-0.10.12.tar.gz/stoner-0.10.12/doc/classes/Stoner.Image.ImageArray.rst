ImageArray
==========

.. currentmodule:: Stoner.Image

.. autoclass:: ImageArray
   :show-inheritance:

   .. rubric:: Attributes Summary

   .. autosummary::

      ~ImageArray.CCW
      ~ImageArray.CW
      ~ImageArray.T
      ~ImageArray.aspect
      ~ImageArray.base
      ~ImageArray.baseclass
      ~ImageArray.centre
      ~ImageArray.clone
      ~ImageArray.ctypes
      ~ImageArray.data
      ~ImageArray.debug
      ~ImageArray.device
      ~ImageArray.draw
      ~ImageArray.dtype
      ~ImageArray.filename
      ~ImageArray.fill_value
      ~ImageArray.flags
      ~ImageArray.flat
      ~ImageArray.flip_h
      ~ImageArray.flip_v
      ~ImageArray.fmts
      ~ImageArray.hardmask
      ~ImageArray.imag
      ~ImageArray.itemset
      ~ImageArray.itemsize
      ~ImageArray.mT
      ~ImageArray.mask
      ~ImageArray.max_box
      ~ImageArray.metadata
      ~ImageArray.nbytes
      ~ImageArray.ndim
      ~ImageArray.newbyteorder
      ~ImageArray.real
      ~ImageArray.recordmask
      ~ImageArray.shape
      ~ImageArray.sharedmask
      ~ImageArray.size
      ~ImageArray.strides
      ~ImageArray.title

   .. rubric:: Methods Summary

   .. autosummary::

      ~ImageArray.AffineTransform
      ~ImageArray.BRIEF
      ~ImageArray.CENSURE
      ~ImageArray.Cascade
      ~ImageArray.CircleModel
      ~ImageArray.EllipseModel
      ~ImageArray.EssentialMatrixTransform
      ~ImageArray.EuclideanTransform
      ~ImageArray.FundamentalMatrixTransform
      ~ImageArray.ImageCollection
      ~ImageArray.LPIFilter2D
      ~ImageArray.LineModelND
      ~ImageArray.MCP
      ~ImageArray.MCP_Connect
      ~ImageArray.MCP_Flexible
      ~ImageArray.MCP_Geometric
      ~ImageArray.MultiImage
      ~ImageArray.ORB
      ~ImageArray.PiecewiseAffineTransform
      ~ImageArray.PolynomialTransform
      ~ImageArray.ProjectiveTransform
      ~ImageArray.RAG
      ~ImageArray.SIFT
      ~ImageArray.SimilarityTransform
      ~ImageArray.Stoner__Image__imagefuncs__adjust_contrast
      ~ImageArray.Stoner__Image__imagefuncs__align
      ~ImageArray.Stoner__Image__imagefuncs__asarray
      ~ImageArray.Stoner__Image__imagefuncs__asfloat
      ~ImageArray.Stoner__Image__imagefuncs__asint
      ~ImageArray.Stoner__Image__imagefuncs__clip_intensity
      ~ImageArray.Stoner__Image__imagefuncs__clip_neg
      ~ImageArray.Stoner__Image__imagefuncs__convert
      ~ImageArray.Stoner__Image__imagefuncs__correct_drift
      ~ImageArray.Stoner__Image__imagefuncs__crop
      ~ImageArray.Stoner__Image__imagefuncs__denoise
      ~ImageArray.Stoner__Image__imagefuncs__do_nothing
      ~ImageArray.Stoner__Image__imagefuncs__dtype_limits
      ~ImageArray.Stoner__Image__imagefuncs__fft
      ~ImageArray.Stoner__Image__imagefuncs__filter_image
      ~ImageArray.Stoner__Image__imagefuncs__gridimage
      ~ImageArray.Stoner__Image__imagefuncs__hist
      ~ImageArray.Stoner__Image__imagefuncs__imshow
      ~ImageArray.Stoner__Image__imagefuncs__level_image
      ~ImageArray.Stoner__Image__imagefuncs__normalise
      ~ImageArray.Stoner__Image__imagefuncs__plot_histogram
      ~ImageArray.Stoner__Image__imagefuncs__profile_line
      ~ImageArray.Stoner__Image__imagefuncs__quantize
      ~ImageArray.Stoner__Image__imagefuncs__radial_coordinates
      ~ImageArray.Stoner__Image__imagefuncs__radial_profile
      ~ImageArray.Stoner__Image__imagefuncs__remove_outliers
      ~ImageArray.Stoner__Image__imagefuncs__rotate
      ~ImageArray.Stoner__Image__imagefuncs__save
      ~ImageArray.Stoner__Image__imagefuncs__save_npy
      ~ImageArray.Stoner__Image__imagefuncs__save_png
      ~ImageArray.Stoner__Image__imagefuncs__save_tiff
      ~ImageArray.Stoner__Image__imagefuncs__sgolay2d
      ~ImageArray.Stoner__Image__imagefuncs__span
      ~ImageArray.Stoner__Image__imagefuncs__subtract_image
      ~ImageArray.Stoner__Image__imagefuncs__threshold_minmax
      ~ImageArray.Stoner__Image__imagefuncs__translate
      ~ImageArray.Stoner__Image__imagefuncs__translate_limits
      ~ImageArray.ThinPlateSplineTransform
      ~ImageArray.active_contour
      ~ImageArray.adjust_contrast
      ~ImageArray.adjust_gamma
      ~ImageArray.adjust_log
      ~ImageArray.adjust_sigmoid
      ~ImageArray.affine_transform
      ~ImageArray.align
      ~ImageArray.all
      ~ImageArray.anom
      ~ImageArray.any
      ~ImageArray.apply_hysteresis_threshold
      ~ImageArray.apply_parallel
      ~ImageArray.approximate_polygon
      ~ImageArray.area_closing
      ~ImageArray.area_opening
      ~ImageArray.argmax
      ~ImageArray.argmin
      ~ImageArray.argpartition
      ~ImageArray.argsort
      ~ImageArray.asarray
      ~ImageArray.asfloat
      ~ImageArray.asint
      ~ImageArray.astype
      ~ImageArray.autolevel
      ~ImageArray.autolevel_percentile
      ~ImageArray.ball
      ~ImageArray.ball_kernel
      ~ImageArray.binary_closing
      ~ImageArray.binary_dilation
      ~ImageArray.binary_erosion
      ~ImageArray.binary_fill_holes
      ~ImageArray.binary_hit_or_miss
      ~ImageArray.binary_opening
      ~ImageArray.binary_propagation
      ~ImageArray.black_tophat
      ~ImageArray.blob_dog
      ~ImageArray.blob_doh
      ~ImageArray.blob_log
      ~ImageArray.block_reduce
      ~ImageArray.blur_effect
      ~ImageArray.butterworth
      ~ImageArray.byteswap
      ~ImageArray.calibrate_denoiser
      ~ImageArray.call_plugin
      ~ImageArray.canny
      ~ImageArray.center_of_mass
      ~ImageArray.central_pixel
      ~ImageArray.centroid
      ~ImageArray.chan_vese
      ~ImageArray.checkerboard_level_set
      ~ImageArray.choose
      ~ImageArray.clear
      ~ImageArray.clear_border
      ~ImageArray.clip
      ~ImageArray.clip_intensity
      ~ImageArray.clip_neg
      ~ImageArray.closing
      ~ImageArray.combine_stains
      ~ImageArray.compare_images
      ~ImageArray.compress
      ~ImageArray.compressed
      ~ImageArray.concatenate_images
      ~ImageArray.conj
      ~ImageArray.conjugate
      ~ImageArray.convert
      ~ImageArray.convert_colorspace
      ~ImageArray.convex_hull_image
      ~ImageArray.convex_hull_object
      ~ImageArray.convolve
      ~ImageArray.convolve1d
      ~ImageArray.copy
      ~ImageArray.corner_fast
      ~ImageArray.corner_foerstner
      ~ImageArray.corner_harris
      ~ImageArray.corner_kitchen_rosenfeld
      ~ImageArray.corner_moravec
      ~ImageArray.corner_orientations
      ~ImageArray.corner_peaks
      ~ImageArray.corner_shi_tomasi
      ~ImageArray.corner_subpix
      ~ImageArray.correct_drift
      ~ImageArray.correlate
      ~ImageArray.correlate1d
      ~ImageArray.correlate_sparse
      ~ImageArray.count
      ~ImageArray.crop
      ~ImageArray.cube
      ~ImageArray.cumprod
      ~ImageArray.cumsum
      ~ImageArray.cumulative_distribution
      ~ImageArray.cut_normalized
      ~ImageArray.cut_threshold
      ~ImageArray.cycle_spin
      ~ImageArray.daisy
      ~ImageArray.deltaE_cie76
      ~ImageArray.deltaE_ciede2000
      ~ImageArray.deltaE_ciede94
      ~ImageArray.deltaE_cmc
      ~ImageArray.denoise
      ~ImageArray.denoise_bilateral
      ~ImageArray.denoise_invariant
      ~ImageArray.denoise_nl_means
      ~ImageArray.denoise_tv_bregman
      ~ImageArray.denoise_tv_chambolle
      ~ImageArray.denoise_wavelet
      ~ImageArray.diagonal
      ~ImageArray.diameter_closing
      ~ImageArray.diameter_opening
      ~ImageArray.diamond
      ~ImageArray.difference_of_gaussians
      ~ImageArray.dilation
      ~ImageArray.disk
      ~ImageArray.disk_level_set
      ~ImageArray.distance_transform_bf
      ~ImageArray.distance_transform_cdt
      ~ImageArray.distance_transform_edt
      ~ImageArray.do_nothing
      ~ImageArray.dot
      ~ImageArray.downscale_local_mean
      ~ImageArray.draw_haar_like_feature
      ~ImageArray.draw_multiblock_lbp
      ~ImageArray.dtype_limits
      ~ImageArray.dump
      ~ImageArray.dumps
      ~ImageArray.ellipse
      ~ImageArray.ellipsoid_kernel
      ~ImageArray.enhance_contrast
      ~ImageArray.enhance_contrast_percentile
      ~ImageArray.entropy
      ~ImageArray.equalize
      ~ImageArray.equalize_adapthist
      ~ImageArray.equalize_hist
      ~ImageArray.erosion
      ~ImageArray.estimate_sigma
      ~ImageArray.estimate_transform
      ~ImageArray.euler_number
      ~ImageArray.expand_labels
      ~ImageArray.extrema
      ~ImageArray.farid
      ~ImageArray.farid_h
      ~ImageArray.farid_v
      ~ImageArray.felzenszwalb
      ~ImageArray.fft
      ~ImageArray.fill
      ~ImageArray.filled
      ~ImageArray.filter_forward
      ~ImageArray.filter_image
      ~ImageArray.filter_inverse
      ~ImageArray.find_available_plugins
      ~ImageArray.find_boundaries
      ~ImageArray.find_contours
      ~ImageArray.find_objects
      ~ImageArray.fisher_vector
      ~ImageArray.flatten
      ~ImageArray.flood
      ~ImageArray.flood_fill
      ~ImageArray.footprint_from_sequence
      ~ImageArray.footprint_rectangle
      ~ImageArray.fourier_ellipsoid
      ~ImageArray.fourier_gaussian
      ~ImageArray.fourier_shift
      ~ImageArray.fourier_uniform
      ~ImageArray.frangi
      ~ImageArray.frt2
      ~ImageArray.gabor
      ~ImageArray.gabor_kernel
      ~ImageArray.gaussian
      ~ImageArray.gaussian_filter
      ~ImageArray.gaussian_filter1d
      ~ImageArray.gaussian_gradient_magnitude
      ~ImageArray.gaussian_laplace
      ~ImageArray.generate_binary_structure
      ~ImageArray.generic_filter
      ~ImageArray.generic_filter1d
      ~ImageArray.generic_gradient_magnitude
      ~ImageArray.generic_laplace
      ~ImageArray.geometric_mean
      ~ImageArray.geometric_transform
      ~ImageArray.get
      ~ImageArray.get_fill_value
      ~ImageArray.get_imag
      ~ImageArray.get_real
      ~ImageArray.getfield
      ~ImageArray.gradient
      ~ImageArray.gradient_percentile
      ~ImageArray.gray2rgb
      ~ImageArray.gray2rgba
      ~ImageArray.graycomatrix
      ~ImageArray.graycoprops
      ~ImageArray.grey_closing
      ~ImageArray.grey_dilation
      ~ImageArray.grey_erosion
      ~ImageArray.grey_opening
      ~ImageArray.grid_points_in_poly
      ~ImageArray.gridimage
      ~ImageArray.h_maxima
      ~ImageArray.h_minima
      ~ImageArray.haar_like_feature
      ~ImageArray.haar_like_feature_coord
      ~ImageArray.harden_mask
      ~ImageArray.hed2rgb
      ~ImageArray.hessian
      ~ImageArray.hessian_matrix
      ~ImageArray.hessian_matrix_det
      ~ImageArray.hessian_matrix_eigvals
      ~ImageArray.hist
      ~ImageArray.histogram
      ~ImageArray.hog
      ~ImageArray.hough_circle
      ~ImageArray.hough_circle_peaks
      ~ImageArray.hough_ellipse
      ~ImageArray.hough_line
      ~ImageArray.hough_line_peaks
      ~ImageArray.hsv2rgb
      ~ImageArray.ids
      ~ImageArray.ifrt2
      ~ImageArray.img_as_bool
      ~ImageArray.img_as_float
      ~ImageArray.img_as_float32
      ~ImageArray.img_as_float64
      ~ImageArray.img_as_int
      ~ImageArray.img_as_ubyte
      ~ImageArray.img_as_uint
      ~ImageArray.imread
      ~ImageArray.imread_collection
      ~ImageArray.imread_collection_wrapper
      ~ImageArray.imsave
      ~ImageArray.imshow
      ~ImageArray.imshow_collection
      ~ImageArray.inertia_tensor
      ~ImageArray.inertia_tensor_eigvals
      ~ImageArray.inpaint_biharmonic
      ~ImageArray.integral_image
      ~ImageArray.integrate
      ~ImageArray.intersection_coeff
      ~ImageArray.inverse_gaussian_gradient
      ~ImageArray.invert
      ~ImageArray.iradon
      ~ImageArray.iradon_sart
      ~ImageArray.is_low_contrast
      ~ImageArray.iscontiguous
      ~ImageArray.isotropic_closing
      ~ImageArray.isotropic_dilation
      ~ImageArray.isotropic_erosion
      ~ImageArray.isotropic_opening
      ~ImageArray.item
      ~ImageArray.items
      ~ImageArray.iterate_structure
      ~ImageArray.join_segmentations
      ~ImageArray.keys
      ~ImageArray.lab2lch
      ~ImageArray.lab2rgb
      ~ImageArray.lab2xyz
      ~ImageArray.label
      ~ImageArray.label2rgb
      ~ImageArray.label_points
      ~ImageArray.labeled_comprehension
      ~ImageArray.laplace
      ~ImageArray.lch2lab
      ~ImageArray.learn_gmm
      ~ImageArray.level_image
      ~ImageArray.load_sift
      ~ImageArray.load_surf
      ~ImageArray.local_binary_pattern
      ~ImageArray.local_maxima
      ~ImageArray.local_minima
      ~ImageArray.lookfor
      ~ImageArray.luv2rgb
      ~ImageArray.luv2xyz
      ~ImageArray.majority
      ~ImageArray.manders_coloc_coeff
      ~ImageArray.manders_overlap_coeff
      ~ImageArray.map_array
      ~ImageArray.map_coordinates
      ~ImageArray.marching_cubes
      ~ImageArray.mark_boundaries
      ~ImageArray.match_descriptors
      ~ImageArray.match_histograms
      ~ImageArray.match_template
      ~ImageArray.matrix_transform
      ~ImageArray.max
      ~ImageArray.max_tree
      ~ImageArray.max_tree_local_maxima
      ~ImageArray.maximum
      ~ImageArray.maximum_filter
      ~ImageArray.maximum_filter1d
      ~ImageArray.maximum_position
      ~ImageArray.mean
      ~ImageArray.mean_bilateral
      ~ImageArray.mean_percentile
      ~ImageArray.medial_axis
      ~ImageArray.median
      ~ImageArray.median_filter
      ~ImageArray.meijering
      ~ImageArray.merge_hierarchical
      ~ImageArray.mesh_surface_area
      ~ImageArray.min
      ~ImageArray.minimum
      ~ImageArray.minimum_filter
      ~ImageArray.minimum_filter1d
      ~ImageArray.minimum_position
      ~ImageArray.mirror_footprint
      ~ImageArray.modal
      ~ImageArray.moments
      ~ImageArray.moments_central
      ~ImageArray.moments_coords
      ~ImageArray.moments_coords_central
      ~ImageArray.moments_hu
      ~ImageArray.moments_normalized
      ~ImageArray.montage
      ~ImageArray.morphological_chan_vese
      ~ImageArray.morphological_geodesic_active_contour
      ~ImageArray.morphological_gradient
      ~ImageArray.morphological_laplace
      ~ImageArray.multiblock_lbp
      ~ImageArray.multiscale_basic_features
      ~ImageArray.noise_filter
      ~ImageArray.nonzero
      ~ImageArray.normalise
      ~ImageArray.octagon
      ~ImageArray.octahedron
      ~ImageArray.opening
      ~ImageArray.order_angles_golden_ratio
      ~ImageArray.otsu
      ~ImageArray.pad_footprint
      ~ImageArray.partition
      ~ImageArray.peak_local_max
      ~ImageArray.pearson_corr_coeff
      ~ImageArray.percentile
      ~ImageArray.percentile_filter
      ~ImageArray.perimeter
      ~ImageArray.perimeter_crofton
      ~ImageArray.pixel_graph
      ~ImageArray.plot_histogram
      ~ImageArray.plot_matched_features
      ~ImageArray.plugin_info
      ~ImageArray.plugin_order
      ~ImageArray.points_in_poly
      ~ImageArray.pop
      ~ImageArray.pop_bilateral
      ~ImageArray.pop_percentile
      ~ImageArray.popitem
      ~ImageArray.prewitt
      ~ImageArray.prewitt_h
      ~ImageArray.prewitt_v
      ~ImageArray.probabilistic_hough_line
      ~ImageArray.prod
      ~ImageArray.product
      ~ImageArray.profile_line
      ~ImageArray.ptp
      ~ImageArray.push
      ~ImageArray.put
      ~ImageArray.pyramid_expand
      ~ImageArray.pyramid_gaussian
      ~ImageArray.pyramid_laplacian
      ~ImageArray.pyramid_reduce
      ~ImageArray.quantize
      ~ImageArray.quickshift
      ~ImageArray.radial_coordinates
      ~ImageArray.radial_profile
      ~ImageArray.radon
      ~ImageArray.rag_boundary
      ~ImageArray.rag_mean_color
      ~ImageArray.random_noise
      ~ImageArray.random_walker
      ~ImageArray.rank_filter
      ~ImageArray.rank_order
      ~ImageArray.ransac
      ~ImageArray.ravel
      ~ImageArray.reconstruction
      ~ImageArray.rectangle
      ~ImageArray.regionprops
      ~ImageArray.regionprops_table
      ~ImageArray.regular_grid
      ~ImageArray.regular_seeds
      ~ImageArray.relabel_sequential
      ~ImageArray.remove_objects_by_distance
      ~ImageArray.remove_outliers
      ~ImageArray.remove_small_holes
      ~ImageArray.remove_small_objects
      ~ImageArray.repeat
      ~ImageArray.rescale
      ~ImageArray.rescale_intensity
      ~ImageArray.reset_plugins
      ~ImageArray.reshape
      ~ImageArray.resize
      ~ImageArray.resize_local_mean
      ~ImageArray.rgb2gray
      ~ImageArray.rgb2hed
      ~ImageArray.rgb2hsv
      ~ImageArray.rgb2lab
      ~ImageArray.rgb2luv
      ~ImageArray.rgb2rgbcie
      ~ImageArray.rgb2xyz
      ~ImageArray.rgb2ycbcr
      ~ImageArray.rgb2ydbdr
      ~ImageArray.rgb2yiq
      ~ImageArray.rgb2ypbpr
      ~ImageArray.rgb2yuv
      ~ImageArray.rgba2rgb
      ~ImageArray.rgbcie2rgb
      ~ImageArray.richardson_lucy
      ~ImageArray.roberts
      ~ImageArray.roberts_neg_diag
      ~ImageArray.roberts_pos_diag
      ~ImageArray.rolling_ball
      ~ImageArray.rotate
      ~ImageArray.round
      ~ImageArray.route_through_array
      ~ImageArray.sato
      ~ImageArray.save
      ~ImageArray.save_npy
      ~ImageArray.save_png
      ~ImageArray.save_tiff
      ~ImageArray.scharr
      ~ImageArray.scharr_h
      ~ImageArray.scharr_v
      ~ImageArray.scipy__ndimage___filters__convolve
      ~ImageArray.scipy__ndimage___filters__convolve1d
      ~ImageArray.scipy__ndimage___filters__correlate
      ~ImageArray.scipy__ndimage___filters__correlate1d
      ~ImageArray.scipy__ndimage___filters__gaussian_filter
      ~ImageArray.scipy__ndimage___filters__gaussian_filter1d
      ~ImageArray.scipy__ndimage___filters__gaussian_gradient_magnitude
      ~ImageArray.scipy__ndimage___filters__gaussian_laplace
      ~ImageArray.scipy__ndimage___filters__generic_filter
      ~ImageArray.scipy__ndimage___filters__generic_filter1d
      ~ImageArray.scipy__ndimage___filters__generic_gradient_magnitude
      ~ImageArray.scipy__ndimage___filters__generic_laplace
      ~ImageArray.scipy__ndimage___filters__laplace
      ~ImageArray.scipy__ndimage___filters__maximum_filter
      ~ImageArray.scipy__ndimage___filters__maximum_filter1d
      ~ImageArray.scipy__ndimage___filters__median_filter
      ~ImageArray.scipy__ndimage___filters__minimum_filter
      ~ImageArray.scipy__ndimage___filters__minimum_filter1d
      ~ImageArray.scipy__ndimage___filters__percentile_filter
      ~ImageArray.scipy__ndimage___filters__prewitt
      ~ImageArray.scipy__ndimage___filters__rank_filter
      ~ImageArray.scipy__ndimage___filters__sobel
      ~ImageArray.scipy__ndimage___filters__uniform_filter
      ~ImageArray.scipy__ndimage___filters__uniform_filter1d
      ~ImageArray.scipy__ndimage___fourier__fourier_ellipsoid
      ~ImageArray.scipy__ndimage___fourier__fourier_gaussian
      ~ImageArray.scipy__ndimage___fourier__fourier_shift
      ~ImageArray.scipy__ndimage___fourier__fourier_uniform
      ~ImageArray.scipy__ndimage___interpolation__affine_transform
      ~ImageArray.scipy__ndimage___interpolation__geometric_transform
      ~ImageArray.scipy__ndimage___interpolation__map_coordinates
      ~ImageArray.scipy__ndimage___interpolation__rotate
      ~ImageArray.scipy__ndimage___interpolation__shift
      ~ImageArray.scipy__ndimage___interpolation__spline_filter
      ~ImageArray.scipy__ndimage___interpolation__spline_filter1d
      ~ImageArray.scipy__ndimage___interpolation__zoom
      ~ImageArray.scipy__ndimage___measurements__center_of_mass
      ~ImageArray.scipy__ndimage___measurements__extrema
      ~ImageArray.scipy__ndimage___measurements__find_objects
      ~ImageArray.scipy__ndimage___measurements__histogram
      ~ImageArray.scipy__ndimage___measurements__label
      ~ImageArray.scipy__ndimage___measurements__labeled_comprehension
      ~ImageArray.scipy__ndimage___measurements__maximum
      ~ImageArray.scipy__ndimage___measurements__maximum_position
      ~ImageArray.scipy__ndimage___measurements__mean
      ~ImageArray.scipy__ndimage___measurements__median
      ~ImageArray.scipy__ndimage___measurements__minimum
      ~ImageArray.scipy__ndimage___measurements__minimum_position
      ~ImageArray.scipy__ndimage___measurements__standard_deviation
      ~ImageArray.scipy__ndimage___measurements__sum
      ~ImageArray.scipy__ndimage___measurements__sum_labels
      ~ImageArray.scipy__ndimage___measurements__value_indices
      ~ImageArray.scipy__ndimage___measurements__variance
      ~ImageArray.scipy__ndimage___measurements__watershed_ift
      ~ImageArray.scipy__ndimage___morphology__binary_closing
      ~ImageArray.scipy__ndimage___morphology__binary_dilation
      ~ImageArray.scipy__ndimage___morphology__binary_erosion
      ~ImageArray.scipy__ndimage___morphology__binary_fill_holes
      ~ImageArray.scipy__ndimage___morphology__binary_hit_or_miss
      ~ImageArray.scipy__ndimage___morphology__binary_opening
      ~ImageArray.scipy__ndimage___morphology__binary_propagation
      ~ImageArray.scipy__ndimage___morphology__black_tophat
      ~ImageArray.scipy__ndimage___morphology__distance_transform_bf
      ~ImageArray.scipy__ndimage___morphology__distance_transform_cdt
      ~ImageArray.scipy__ndimage___morphology__distance_transform_edt
      ~ImageArray.scipy__ndimage___morphology__generate_binary_structure
      ~ImageArray.scipy__ndimage___morphology__grey_closing
      ~ImageArray.scipy__ndimage___morphology__grey_dilation
      ~ImageArray.scipy__ndimage___morphology__grey_erosion
      ~ImageArray.scipy__ndimage___morphology__grey_opening
      ~ImageArray.scipy__ndimage___morphology__iterate_structure
      ~ImageArray.scipy__ndimage___morphology__morphological_gradient
      ~ImageArray.scipy__ndimage___morphology__morphological_laplace
      ~ImageArray.scipy__ndimage___morphology__white_tophat
      ~ImageArray.searchsorted
      ~ImageArray.separate_stains
      ~ImageArray.set_fill_value
      ~ImageArray.setdefault
      ~ImageArray.setfield
      ~ImageArray.setflags
      ~ImageArray.sgolay2d
      ~ImageArray.shannon_entropy
      ~ImageArray.shape_index
      ~ImageArray.shift
      ~ImageArray.shortest_path
      ~ImageArray.show
      ~ImageArray.show_rag
      ~ImageArray.shrink_mask
      ~ImageArray.skeletonize
      ~ImageArray.skimage___shared__filters__gaussian
      ~ImageArray.skimage__color__colorconv__combine_stains
      ~ImageArray.skimage__color__colorconv__convert_colorspace
      ~ImageArray.skimage__color__colorconv__gray2rgb
      ~ImageArray.skimage__color__colorconv__gray2rgba
      ~ImageArray.skimage__color__colorconv__hed2rgb
      ~ImageArray.skimage__color__colorconv__hsv2rgb
      ~ImageArray.skimage__color__colorconv__lab2lch
      ~ImageArray.skimage__color__colorconv__lab2rgb
      ~ImageArray.skimage__color__colorconv__lab2xyz
      ~ImageArray.skimage__color__colorconv__lch2lab
      ~ImageArray.skimage__color__colorconv__luv2rgb
      ~ImageArray.skimage__color__colorconv__luv2xyz
      ~ImageArray.skimage__color__colorconv__rgb2gray
      ~ImageArray.skimage__color__colorconv__rgb2hed
      ~ImageArray.skimage__color__colorconv__rgb2hsv
      ~ImageArray.skimage__color__colorconv__rgb2lab
      ~ImageArray.skimage__color__colorconv__rgb2luv
      ~ImageArray.skimage__color__colorconv__rgb2rgbcie
      ~ImageArray.skimage__color__colorconv__rgb2xyz
      ~ImageArray.skimage__color__colorconv__rgb2ycbcr
      ~ImageArray.skimage__color__colorconv__rgb2ydbdr
      ~ImageArray.skimage__color__colorconv__rgb2yiq
      ~ImageArray.skimage__color__colorconv__rgb2ypbpr
      ~ImageArray.skimage__color__colorconv__rgb2yuv
      ~ImageArray.skimage__color__colorconv__rgba2rgb
      ~ImageArray.skimage__color__colorconv__rgbcie2rgb
      ~ImageArray.skimage__color__colorconv__separate_stains
      ~ImageArray.skimage__color__colorconv__xyz2lab
      ~ImageArray.skimage__color__colorconv__xyz2luv
      ~ImageArray.skimage__color__colorconv__xyz2rgb
      ~ImageArray.skimage__color__colorconv__xyz_tristimulus_values
      ~ImageArray.skimage__color__colorconv__ycbcr2rgb
      ~ImageArray.skimage__color__colorconv__ydbdr2rgb
      ~ImageArray.skimage__color__colorconv__yiq2rgb
      ~ImageArray.skimage__color__colorconv__ypbpr2rgb
      ~ImageArray.skimage__color__colorconv__yuv2rgb
      ~ImageArray.skimage__color__colorlabel__label2rgb
      ~ImageArray.skimage__color__delta_e__deltaE_cie76
      ~ImageArray.skimage__color__delta_e__deltaE_ciede2000
      ~ImageArray.skimage__color__delta_e__deltaE_ciede94
      ~ImageArray.skimage__color__delta_e__deltaE_cmc
      ~ImageArray.skimage__exposure___adapthist__equalize_adapthist
      ~ImageArray.skimage__exposure__exposure__adjust_gamma
      ~ImageArray.skimage__exposure__exposure__adjust_log
      ~ImageArray.skimage__exposure__exposure__adjust_sigmoid
      ~ImageArray.skimage__exposure__exposure__cumulative_distribution
      ~ImageArray.skimage__exposure__exposure__equalize_hist
      ~ImageArray.skimage__exposure__exposure__histogram
      ~ImageArray.skimage__exposure__exposure__is_low_contrast
      ~ImageArray.skimage__exposure__exposure__rescale_intensity
      ~ImageArray.skimage__exposure__histogram_matching__match_histograms
      ~ImageArray.skimage__feature___basic_features__multiscale_basic_features
      ~ImageArray.skimage__feature___canny__canny
      ~ImageArray.skimage__feature___cascade__Cascade
      ~ImageArray.skimage__feature___daisy__daisy
      ~ImageArray.skimage__feature___fisher_vector__fisher_vector
      ~ImageArray.skimage__feature___fisher_vector__learn_gmm
      ~ImageArray.skimage__feature___hog__hog
      ~ImageArray.skimage__feature__blob__blob_dog
      ~ImageArray.skimage__feature__blob__blob_doh
      ~ImageArray.skimage__feature__blob__blob_log
      ~ImageArray.skimage__feature__brief__BRIEF
      ~ImageArray.skimage__feature__censure__CENSURE
      ~ImageArray.skimage__feature__corner__corner_fast
      ~ImageArray.skimage__feature__corner__corner_foerstner
      ~ImageArray.skimage__feature__corner__corner_harris
      ~ImageArray.skimage__feature__corner__corner_kitchen_rosenfeld
      ~ImageArray.skimage__feature__corner__corner_moravec
      ~ImageArray.skimage__feature__corner__corner_orientations
      ~ImageArray.skimage__feature__corner__corner_peaks
      ~ImageArray.skimage__feature__corner__corner_shi_tomasi
      ~ImageArray.skimage__feature__corner__corner_subpix
      ~ImageArray.skimage__feature__corner__hessian_matrix
      ~ImageArray.skimage__feature__corner__hessian_matrix_det
      ~ImageArray.skimage__feature__corner__hessian_matrix_eigvals
      ~ImageArray.skimage__feature__corner__shape_index
      ~ImageArray.skimage__feature__corner__structure_tensor
      ~ImageArray.skimage__feature__corner__structure_tensor_eigenvalues
      ~ImageArray.skimage__feature__haar__draw_haar_like_feature
      ~ImageArray.skimage__feature__haar__haar_like_feature
      ~ImageArray.skimage__feature__haar__haar_like_feature_coord
      ~ImageArray.skimage__feature__match__match_descriptors
      ~ImageArray.skimage__feature__orb__ORB
      ~ImageArray.skimage__feature__peak__peak_local_max
      ~ImageArray.skimage__feature__sift__SIFT
      ~ImageArray.skimage__feature__template__match_template
      ~ImageArray.skimage__feature__texture__draw_multiblock_lbp
      ~ImageArray.skimage__feature__texture__graycomatrix
      ~ImageArray.skimage__feature__texture__graycoprops
      ~ImageArray.skimage__feature__texture__local_binary_pattern
      ~ImageArray.skimage__feature__texture__multiblock_lbp
      ~ImageArray.skimage__feature__util__plot_matched_features
      ~ImageArray.skimage__filters___fft_based__butterworth
      ~ImageArray.skimage__filters___gabor__gabor
      ~ImageArray.skimage__filters___gabor__gabor_kernel
      ~ImageArray.skimage__filters___gaussian__difference_of_gaussians
      ~ImageArray.skimage__filters___median__median
      ~ImageArray.skimage__filters___rank_order__rank_order
      ~ImageArray.skimage__filters___sparse__correlate_sparse
      ~ImageArray.skimage__filters___unsharp_mask__unsharp_mask
      ~ImageArray.skimage__filters___window__window
      ~ImageArray.skimage__filters__edges__farid
      ~ImageArray.skimage__filters__edges__farid_h
      ~ImageArray.skimage__filters__edges__farid_v
      ~ImageArray.skimage__filters__edges__laplace
      ~ImageArray.skimage__filters__edges__prewitt
      ~ImageArray.skimage__filters__edges__prewitt_h
      ~ImageArray.skimage__filters__edges__prewitt_v
      ~ImageArray.skimage__filters__edges__roberts
      ~ImageArray.skimage__filters__edges__roberts_neg_diag
      ~ImageArray.skimage__filters__edges__roberts_pos_diag
      ~ImageArray.skimage__filters__edges__scharr
      ~ImageArray.skimage__filters__edges__scharr_h
      ~ImageArray.skimage__filters__edges__scharr_v
      ~ImageArray.skimage__filters__edges__sobel
      ~ImageArray.skimage__filters__edges__sobel_h
      ~ImageArray.skimage__filters__edges__sobel_v
      ~ImageArray.skimage__filters__lpi_filter__LPIFilter2D
      ~ImageArray.skimage__filters__lpi_filter__filter_forward
      ~ImageArray.skimage__filters__lpi_filter__filter_inverse
      ~ImageArray.skimage__filters__lpi_filter__wiener
      ~ImageArray.skimage__filters__rank___percentile__autolevel_percentile
      ~ImageArray.skimage__filters__rank___percentile__enhance_contrast_percentile
      ~ImageArray.skimage__filters__rank___percentile__gradient_percentile
      ~ImageArray.skimage__filters__rank___percentile__mean_percentile
      ~ImageArray.skimage__filters__rank___percentile__percentile
      ~ImageArray.skimage__filters__rank___percentile__pop_percentile
      ~ImageArray.skimage__filters__rank___percentile__subtract_mean_percentile
      ~ImageArray.skimage__filters__rank___percentile__sum_percentile
      ~ImageArray.skimage__filters__rank___percentile__threshold_percentile
      ~ImageArray.skimage__filters__rank__bilateral__mean_bilateral
      ~ImageArray.skimage__filters__rank__bilateral__pop_bilateral
      ~ImageArray.skimage__filters__rank__bilateral__sum_bilateral
      ~ImageArray.skimage__filters__rank__generic__autolevel
      ~ImageArray.skimage__filters__rank__generic__enhance_contrast
      ~ImageArray.skimage__filters__rank__generic__entropy
      ~ImageArray.skimage__filters__rank__generic__equalize
      ~ImageArray.skimage__filters__rank__generic__geometric_mean
      ~ImageArray.skimage__filters__rank__generic__gradient
      ~ImageArray.skimage__filters__rank__generic__majority
      ~ImageArray.skimage__filters__rank__generic__maximum
      ~ImageArray.skimage__filters__rank__generic__mean
      ~ImageArray.skimage__filters__rank__generic__median
      ~ImageArray.skimage__filters__rank__generic__minimum
      ~ImageArray.skimage__filters__rank__generic__modal
      ~ImageArray.skimage__filters__rank__generic__noise_filter
      ~ImageArray.skimage__filters__rank__generic__otsu
      ~ImageArray.skimage__filters__rank__generic__pop
      ~ImageArray.skimage__filters__rank__generic__subtract_mean
      ~ImageArray.skimage__filters__rank__generic__sum
      ~ImageArray.skimage__filters__rank__generic__threshold
      ~ImageArray.skimage__filters__rank__generic__windowed_histogram
      ~ImageArray.skimage__filters__ridges__frangi
      ~ImageArray.skimage__filters__ridges__hessian
      ~ImageArray.skimage__filters__ridges__meijering
      ~ImageArray.skimage__filters__ridges__sato
      ~ImageArray.skimage__filters__thresholding__apply_hysteresis_threshold
      ~ImageArray.skimage__filters__thresholding__threshold_isodata
      ~ImageArray.skimage__filters__thresholding__threshold_li
      ~ImageArray.skimage__filters__thresholding__threshold_local
      ~ImageArray.skimage__filters__thresholding__threshold_mean
      ~ImageArray.skimage__filters__thresholding__threshold_minimum
      ~ImageArray.skimage__filters__thresholding__threshold_multiotsu
      ~ImageArray.skimage__filters__thresholding__threshold_niblack
      ~ImageArray.skimage__filters__thresholding__threshold_otsu
      ~ImageArray.skimage__filters__thresholding__threshold_sauvola
      ~ImageArray.skimage__filters__thresholding__threshold_triangle
      ~ImageArray.skimage__filters__thresholding__threshold_yen
      ~ImageArray.skimage__filters__thresholding__try_all_threshold
      ~ImageArray.skimage__graph___graph__central_pixel
      ~ImageArray.skimage__graph___graph__pixel_graph
      ~ImageArray.skimage__graph___graph_cut__cut_normalized
      ~ImageArray.skimage__graph___graph_cut__cut_threshold
      ~ImageArray.skimage__graph___graph_merge__merge_hierarchical
      ~ImageArray.skimage__graph___mcp__MCP
      ~ImageArray.skimage__graph___mcp__MCP_Connect
      ~ImageArray.skimage__graph___mcp__MCP_Flexible
      ~ImageArray.skimage__graph___mcp__MCP_Geometric
      ~ImageArray.skimage__graph___rag__RAG
      ~ImageArray.skimage__graph___rag__rag_boundary
      ~ImageArray.skimage__graph___rag__rag_mean_color
      ~ImageArray.skimage__graph___rag__show_rag
      ~ImageArray.skimage__graph__mcp__route_through_array
      ~ImageArray.skimage__graph__spath__shortest_path
      ~ImageArray.skimage__io___image_stack__pop
      ~ImageArray.skimage__io___image_stack__push
      ~ImageArray.skimage__io___io__imread
      ~ImageArray.skimage__io___io__imread_collection
      ~ImageArray.skimage__io___io__imsave
      ~ImageArray.skimage__io___io__imshow
      ~ImageArray.skimage__io___io__imshow_collection
      ~ImageArray.skimage__io___io__show
      ~ImageArray.skimage__io__collection__ImageCollection
      ~ImageArray.skimage__io__collection__MultiImage
      ~ImageArray.skimage__io__collection__concatenate_images
      ~ImageArray.skimage__io__collection__imread_collection_wrapper
      ~ImageArray.skimage__io__manage_plugins__call_plugin
      ~ImageArray.skimage__io__manage_plugins__find_available_plugins
      ~ImageArray.skimage__io__manage_plugins__plugin_info
      ~ImageArray.skimage__io__manage_plugins__plugin_order
      ~ImageArray.skimage__io__manage_plugins__reset_plugins
      ~ImageArray.skimage__io__manage_plugins__use_plugin
      ~ImageArray.skimage__io__sift__load_sift
      ~ImageArray.skimage__io__sift__load_surf
      ~ImageArray.skimage__measure___blur_effect__blur_effect
      ~ImageArray.skimage__measure___colocalization__intersection_coeff
      ~ImageArray.skimage__measure___colocalization__manders_coloc_coeff
      ~ImageArray.skimage__measure___colocalization__manders_overlap_coeff
      ~ImageArray.skimage__measure___colocalization__pearson_corr_coeff
      ~ImageArray.skimage__measure___find_contours__find_contours
      ~ImageArray.skimage__measure___label__label
      ~ImageArray.skimage__measure___marching_cubes_lewiner__marching_cubes
      ~ImageArray.skimage__measure___marching_cubes_lewiner__mesh_surface_area
      ~ImageArray.skimage__measure___moments__centroid
      ~ImageArray.skimage__measure___moments__inertia_tensor
      ~ImageArray.skimage__measure___moments__inertia_tensor_eigvals
      ~ImageArray.skimage__measure___moments__moments
      ~ImageArray.skimage__measure___moments__moments_central
      ~ImageArray.skimage__measure___moments__moments_coords
      ~ImageArray.skimage__measure___moments__moments_coords_central
      ~ImageArray.skimage__measure___moments__moments_hu
      ~ImageArray.skimage__measure___moments__moments_normalized
      ~ImageArray.skimage__measure___polygon__approximate_polygon
      ~ImageArray.skimage__measure___polygon__subdivide_polygon
      ~ImageArray.skimage__measure___regionprops__regionprops
      ~ImageArray.skimage__measure___regionprops__regionprops_table
      ~ImageArray.skimage__measure___regionprops_utils__euler_number
      ~ImageArray.skimage__measure___regionprops_utils__perimeter
      ~ImageArray.skimage__measure___regionprops_utils__perimeter_crofton
      ~ImageArray.skimage__measure__block__block_reduce
      ~ImageArray.skimage__measure__entropy__shannon_entropy
      ~ImageArray.skimage__measure__fit__CircleModel
      ~ImageArray.skimage__measure__fit__EllipseModel
      ~ImageArray.skimage__measure__fit__LineModelND
      ~ImageArray.skimage__measure__fit__ransac
      ~ImageArray.skimage__measure__pnpoly__grid_points_in_poly
      ~ImageArray.skimage__measure__pnpoly__points_in_poly
      ~ImageArray.skimage__measure__profile__profile_line
      ~ImageArray.skimage__morphology___flood_fill__flood
      ~ImageArray.skimage__morphology___flood_fill__flood_fill
      ~ImageArray.skimage__morphology___skeletonize__medial_axis
      ~ImageArray.skimage__morphology___skeletonize__skeletonize
      ~ImageArray.skimage__morphology___skeletonize__thin
      ~ImageArray.skimage__morphology__binary__binary_closing
      ~ImageArray.skimage__morphology__binary__binary_dilation
      ~ImageArray.skimage__morphology__binary__binary_erosion
      ~ImageArray.skimage__morphology__binary__binary_opening
      ~ImageArray.skimage__morphology__convex_hull__convex_hull_image
      ~ImageArray.skimage__morphology__convex_hull__convex_hull_object
      ~ImageArray.skimage__morphology__extrema__h_maxima
      ~ImageArray.skimage__morphology__extrema__h_minima
      ~ImageArray.skimage__morphology__extrema__local_maxima
      ~ImageArray.skimage__morphology__extrema__local_minima
      ~ImageArray.skimage__morphology__footprints__ball
      ~ImageArray.skimage__morphology__footprints__cube
      ~ImageArray.skimage__morphology__footprints__diamond
      ~ImageArray.skimage__morphology__footprints__disk
      ~ImageArray.skimage__morphology__footprints__ellipse
      ~ImageArray.skimage__morphology__footprints__footprint_from_sequence
      ~ImageArray.skimage__morphology__footprints__footprint_rectangle
      ~ImageArray.skimage__morphology__footprints__mirror_footprint
      ~ImageArray.skimage__morphology__footprints__octagon
      ~ImageArray.skimage__morphology__footprints__octahedron
      ~ImageArray.skimage__morphology__footprints__pad_footprint
      ~ImageArray.skimage__morphology__footprints__rectangle
      ~ImageArray.skimage__morphology__footprints__square
      ~ImageArray.skimage__morphology__footprints__star
      ~ImageArray.skimage__morphology__gray__black_tophat
      ~ImageArray.skimage__morphology__gray__closing
      ~ImageArray.skimage__morphology__gray__dilation
      ~ImageArray.skimage__morphology__gray__erosion
      ~ImageArray.skimage__morphology__gray__opening
      ~ImageArray.skimage__morphology__gray__white_tophat
      ~ImageArray.skimage__morphology__grayreconstruct__reconstruction
      ~ImageArray.skimage__morphology__isotropic__isotropic_closing
      ~ImageArray.skimage__morphology__isotropic__isotropic_dilation
      ~ImageArray.skimage__morphology__isotropic__isotropic_erosion
      ~ImageArray.skimage__morphology__isotropic__isotropic_opening
      ~ImageArray.skimage__morphology__max_tree__area_closing
      ~ImageArray.skimage__morphology__max_tree__area_opening
      ~ImageArray.skimage__morphology__max_tree__diameter_closing
      ~ImageArray.skimage__morphology__max_tree__diameter_opening
      ~ImageArray.skimage__morphology__max_tree__max_tree
      ~ImageArray.skimage__morphology__max_tree__max_tree_local_maxima
      ~ImageArray.skimage__morphology__misc__remove_objects_by_distance
      ~ImageArray.skimage__morphology__misc__remove_small_holes
      ~ImageArray.skimage__morphology__misc__remove_small_objects
      ~ImageArray.skimage__restoration___cycle_spin__cycle_spin
      ~ImageArray.skimage__restoration___denoise__denoise_bilateral
      ~ImageArray.skimage__restoration___denoise__denoise_tv_bregman
      ~ImageArray.skimage__restoration___denoise__denoise_tv_chambolle
      ~ImageArray.skimage__restoration___denoise__denoise_wavelet
      ~ImageArray.skimage__restoration___denoise__estimate_sigma
      ~ImageArray.skimage__restoration___rolling_ball__ball_kernel
      ~ImageArray.skimage__restoration___rolling_ball__ellipsoid_kernel
      ~ImageArray.skimage__restoration___rolling_ball__rolling_ball
      ~ImageArray.skimage__restoration__deconvolution__richardson_lucy
      ~ImageArray.skimage__restoration__deconvolution__unsupervised_wiener
      ~ImageArray.skimage__restoration__deconvolution__wiener
      ~ImageArray.skimage__restoration__inpaint__inpaint_biharmonic
      ~ImageArray.skimage__restoration__j_invariant__calibrate_denoiser
      ~ImageArray.skimage__restoration__j_invariant__denoise_invariant
      ~ImageArray.skimage__restoration__non_local_means__denoise_nl_means
      ~ImageArray.skimage__restoration__unwrap__unwrap_phase
      ~ImageArray.skimage__segmentation___chan_vese__chan_vese
      ~ImageArray.skimage__segmentation___clear_border__clear_border
      ~ImageArray.skimage__segmentation___expand_labels__expand_labels
      ~ImageArray.skimage__segmentation___felzenszwalb__felzenszwalb
      ~ImageArray.skimage__segmentation___join__join_segmentations
      ~ImageArray.skimage__segmentation___join__relabel_sequential
      ~ImageArray.skimage__segmentation___quickshift__quickshift
      ~ImageArray.skimage__segmentation___watershed__watershed
      ~ImageArray.skimage__segmentation__active_contour_model__active_contour
      ~ImageArray.skimage__segmentation__boundaries__find_boundaries
      ~ImageArray.skimage__segmentation__boundaries__mark_boundaries
      ~ImageArray.skimage__segmentation__morphsnakes__checkerboard_level_set
      ~ImageArray.skimage__segmentation__morphsnakes__disk_level_set
      ~ImageArray.skimage__segmentation__morphsnakes__inverse_gaussian_gradient
      ~ImageArray.skimage__segmentation__morphsnakes__morphological_chan_vese
      ~ImageArray.skimage__segmentation__morphsnakes__morphological_geodesic_active_contour
      ~ImageArray.skimage__segmentation__random_walker_segmentation__random_walker
      ~ImageArray.skimage__segmentation__slic_superpixels__slic
      ~ImageArray.skimage__transform___geometric__AffineTransform
      ~ImageArray.skimage__transform___geometric__EssentialMatrixTransform
      ~ImageArray.skimage__transform___geometric__EuclideanTransform
      ~ImageArray.skimage__transform___geometric__FundamentalMatrixTransform
      ~ImageArray.skimage__transform___geometric__PiecewiseAffineTransform
      ~ImageArray.skimage__transform___geometric__PolynomialTransform
      ~ImageArray.skimage__transform___geometric__ProjectiveTransform
      ~ImageArray.skimage__transform___geometric__SimilarityTransform
      ~ImageArray.skimage__transform___geometric__estimate_transform
      ~ImageArray.skimage__transform___geometric__matrix_transform
      ~ImageArray.skimage__transform___thin_plate_splines__ThinPlateSplineTransform
      ~ImageArray.skimage__transform___warps__downscale_local_mean
      ~ImageArray.skimage__transform___warps__rescale
      ~ImageArray.skimage__transform___warps__resize
      ~ImageArray.skimage__transform___warps__resize_local_mean
      ~ImageArray.skimage__transform___warps__rotate
      ~ImageArray.skimage__transform___warps__swirl
      ~ImageArray.skimage__transform___warps__warp
      ~ImageArray.skimage__transform___warps__warp_coords
      ~ImageArray.skimage__transform___warps__warp_polar
      ~ImageArray.skimage__transform__finite_radon_transform__frt2
      ~ImageArray.skimage__transform__finite_radon_transform__ifrt2
      ~ImageArray.skimage__transform__hough_transform__hough_circle
      ~ImageArray.skimage__transform__hough_transform__hough_circle_peaks
      ~ImageArray.skimage__transform__hough_transform__hough_ellipse
      ~ImageArray.skimage__transform__hough_transform__hough_line
      ~ImageArray.skimage__transform__hough_transform__hough_line_peaks
      ~ImageArray.skimage__transform__hough_transform__probabilistic_hough_line
      ~ImageArray.skimage__transform__integral__integral_image
      ~ImageArray.skimage__transform__integral__integrate
      ~ImageArray.skimage__transform__pyramids__pyramid_expand
      ~ImageArray.skimage__transform__pyramids__pyramid_gaussian
      ~ImageArray.skimage__transform__pyramids__pyramid_laplacian
      ~ImageArray.skimage__transform__pyramids__pyramid_reduce
      ~ImageArray.skimage__transform__radon_transform__iradon
      ~ImageArray.skimage__transform__radon_transform__iradon_sart
      ~ImageArray.skimage__transform__radon_transform__order_angles_golden_ratio
      ~ImageArray.skimage__transform__radon_transform__radon
      ~ImageArray.skimage__util___invert__invert
      ~ImageArray.skimage__util___label__label_points
      ~ImageArray.skimage__util___map_array__map_array
      ~ImageArray.skimage__util___montage__montage
      ~ImageArray.skimage__util___regular_grid__regular_grid
      ~ImageArray.skimage__util___regular_grid__regular_seeds
      ~ImageArray.skimage__util___slice_along_axes__slice_along_axes
      ~ImageArray.skimage__util__apply_parallel__apply_parallel
      ~ImageArray.skimage__util__arraycrop__crop
      ~ImageArray.skimage__util__compare__compare_images
      ~ImageArray.skimage__util__dtype__dtype_limits
      ~ImageArray.skimage__util__dtype__img_as_bool
      ~ImageArray.skimage__util__dtype__img_as_float
      ~ImageArray.skimage__util__dtype__img_as_float32
      ~ImageArray.skimage__util__dtype__img_as_float64
      ~ImageArray.skimage__util__dtype__img_as_int
      ~ImageArray.skimage__util__dtype__img_as_ubyte
      ~ImageArray.skimage__util__dtype__img_as_uint
      ~ImageArray.skimage__util__lookfor__lookfor
      ~ImageArray.skimage__util__noise__random_noise
      ~ImageArray.skimage__util__shape__view_as_blocks
      ~ImageArray.skimage__util__shape__view_as_windows
      ~ImageArray.skimage__util__unique__unique_rows
      ~ImageArray.slic
      ~ImageArray.slice_along_axes
      ~ImageArray.sobel
      ~ImageArray.sobel_h
      ~ImageArray.sobel_v
      ~ImageArray.soften_mask
      ~ImageArray.sort
      ~ImageArray.span
      ~ImageArray.spline_filter
      ~ImageArray.spline_filter1d
      ~ImageArray.square
      ~ImageArray.squeeze
      ~ImageArray.standard_deviation
      ~ImageArray.star
      ~ImageArray.std
      ~ImageArray.structure_tensor
      ~ImageArray.structure_tensor_eigenvalues
      ~ImageArray.subdivide_polygon
      ~ImageArray.subtract_image
      ~ImageArray.subtract_mean
      ~ImageArray.subtract_mean_percentile
      ~ImageArray.sum
      ~ImageArray.sum_bilateral
      ~ImageArray.sum_labels
      ~ImageArray.sum_percentile
      ~ImageArray.swapaxes
      ~ImageArray.swirl
      ~ImageArray.take
      ~ImageArray.thin
      ~ImageArray.threshold
      ~ImageArray.threshold_isodata
      ~ImageArray.threshold_li
      ~ImageArray.threshold_local
      ~ImageArray.threshold_mean
      ~ImageArray.threshold_minimum
      ~ImageArray.threshold_minmax
      ~ImageArray.threshold_multiotsu
      ~ImageArray.threshold_niblack
      ~ImageArray.threshold_otsu
      ~ImageArray.threshold_percentile
      ~ImageArray.threshold_sauvola
      ~ImageArray.threshold_triangle
      ~ImageArray.threshold_yen
      ~ImageArray.to_device
      ~ImageArray.tobytes
      ~ImageArray.tofile
      ~ImageArray.toflex
      ~ImageArray.tolist
      ~ImageArray.torecords
      ~ImageArray.tostring
      ~ImageArray.trace
      ~ImageArray.translate
      ~ImageArray.translate_limits
      ~ImageArray.transpose
      ~ImageArray.try_all_threshold
      ~ImageArray.uniform_filter
      ~ImageArray.uniform_filter1d
      ~ImageArray.unique_rows
      ~ImageArray.unshare_mask
      ~ImageArray.unsharp_mask
      ~ImageArray.unsupervised_wiener
      ~ImageArray.unwrap_phase
      ~ImageArray.update
      ~ImageArray.use_plugin
      ~ImageArray.value_indices
      ~ImageArray.values
      ~ImageArray.var
      ~ImageArray.variance
      ~ImageArray.view
      ~ImageArray.view_as_blocks
      ~ImageArray.view_as_windows
      ~ImageArray.warp
      ~ImageArray.warp_coords
      ~ImageArray.warp_polar
      ~ImageArray.watershed
      ~ImageArray.watershed_ift
      ~ImageArray.white_tophat
      ~ImageArray.wiener
      ~ImageArray.window
      ~ImageArray.windowed_histogram
      ~ImageArray.xyz2lab
      ~ImageArray.xyz2luv
      ~ImageArray.xyz2rgb
      ~ImageArray.xyz_tristimulus_values
      ~ImageArray.ycbcr2rgb
      ~ImageArray.ydbdr2rgb
      ~ImageArray.yiq2rgb
      ~ImageArray.ypbpr2rgb
      ~ImageArray.yuv2rgb
      ~ImageArray.zoom

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
   .. autoattribute:: itemset
   .. autoattribute:: itemsize
   .. autoattribute:: mT
   .. autoattribute:: mask
   .. autoattribute:: max_box
   .. autoattribute:: metadata
   .. autoattribute:: nbytes
   .. autoattribute:: ndim
   .. autoattribute:: newbyteorder
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
