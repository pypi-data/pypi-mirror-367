SLS_STXMFile
============

.. currentmodule:: Stoner.HDF5

.. autoclass:: SLS_STXMFile
   :show-inheritance:

   .. rubric:: Attributes Summary

   .. autosummary::

      ~SLS_STXMFile.T
      ~SLS_STXMFile.ax
      ~SLS_STXMFile.axes
      ~SLS_STXMFile.basename
      ~SLS_STXMFile.clone
      ~SLS_STXMFile.cmap
      ~SLS_STXMFile.column_headers
      ~SLS_STXMFile.compression
      ~SLS_STXMFile.compression_opts
      ~SLS_STXMFile.data
      ~SLS_STXMFile.dict_records
      ~SLS_STXMFile.dims
      ~SLS_STXMFile.dtype
      ~SLS_STXMFile.fig
      ~SLS_STXMFile.fignum
      ~SLS_STXMFile.filename
      ~SLS_STXMFile.filepath
      ~SLS_STXMFile.header
      ~SLS_STXMFile.labels
      ~SLS_STXMFile.mask
      ~SLS_STXMFile.metadata
      ~SLS_STXMFile.mime_type
      ~SLS_STXMFile.multiple
      ~SLS_STXMFile.no_fmt
      ~SLS_STXMFile.patterns
      ~SLS_STXMFile.positional_fmt
      ~SLS_STXMFile.priority
      ~SLS_STXMFile.records
      ~SLS_STXMFile.setas
      ~SLS_STXMFile.shape
      ~SLS_STXMFile.showfig
      ~SLS_STXMFile.subplots
      ~SLS_STXMFile.template

   .. rubric:: Methods Summary

   .. autosummary::

      ~SLS_STXMFile.SG_Filter
      ~SLS_STXMFile.__call__
      ~SLS_STXMFile.add
      ~SLS_STXMFile.add_column
      ~SLS_STXMFile.annotate_fit
      ~SLS_STXMFile.append
      ~SLS_STXMFile.apply
      ~SLS_STXMFile.asarray
      ~SLS_STXMFile.bin
      ~SLS_STXMFile.clear
      ~SLS_STXMFile.clip
      ~SLS_STXMFile.closest
      ~SLS_STXMFile.colormap_xyz
      ~SLS_STXMFile.column
      ~SLS_STXMFile.columns
      ~SLS_STXMFile.contour_xyz
      ~SLS_STXMFile.count
      ~SLS_STXMFile.curve_fit
      ~SLS_STXMFile.decompose
      ~SLS_STXMFile.del_column
      ~SLS_STXMFile.del_nan
      ~SLS_STXMFile.del_rows
      ~SLS_STXMFile.differential_evolution
      ~SLS_STXMFile.diffsum
      ~SLS_STXMFile.dir
      ~SLS_STXMFile.divide
      ~SLS_STXMFile.extend
      ~SLS_STXMFile.extrapolate
      ~SLS_STXMFile.figure
      ~SLS_STXMFile.filter
      ~SLS_STXMFile.find_col
      ~SLS_STXMFile.find_duplicates
      ~SLS_STXMFile.find_peaks
      ~SLS_STXMFile.format
      ~SLS_STXMFile.get
      ~SLS_STXMFile.get_filename
      ~SLS_STXMFile.griddata
      ~SLS_STXMFile.image_plot
      ~SLS_STXMFile.index
      ~SLS_STXMFile.insert
      ~SLS_STXMFile.insert_rows
      ~SLS_STXMFile.inset
      ~SLS_STXMFile.integrate
      ~SLS_STXMFile.interpolate
      ~SLS_STXMFile.items
      ~SLS_STXMFile.keys
      ~SLS_STXMFile.legend
      ~SLS_STXMFile.lmfit
      ~SLS_STXMFile.load
      ~SLS_STXMFile.make_bins
      ~SLS_STXMFile.max
      ~SLS_STXMFile.mean
      ~SLS_STXMFile.min
      ~SLS_STXMFile.multiply
      ~SLS_STXMFile.normalise
      ~SLS_STXMFile.odr
      ~SLS_STXMFile.outlier_detection
      ~SLS_STXMFile.peaks
      ~SLS_STXMFile.plot
      ~SLS_STXMFile.plot_matrix
      ~SLS_STXMFile.plot_voxels
      ~SLS_STXMFile.plot_xy
      ~SLS_STXMFile.plot_xyuv
      ~SLS_STXMFile.plot_xyuvw
      ~SLS_STXMFile.plot_xyz
      ~SLS_STXMFile.plot_xyzuvw
      ~SLS_STXMFile.polyfit
      ~SLS_STXMFile.pop
      ~SLS_STXMFile.popitem
      ~SLS_STXMFile.quiver_plot
      ~SLS_STXMFile.remove
      ~SLS_STXMFile.remove_duplicates
      ~SLS_STXMFile.rename
      ~SLS_STXMFile.reorder_columns
      ~SLS_STXMFile.reverse
      ~SLS_STXMFile.rolling_window
      ~SLS_STXMFile.rows
      ~SLS_STXMFile.save
      ~SLS_STXMFile.scale
      ~SLS_STXMFile.scan_meta
      ~SLS_STXMFile.search
      ~SLS_STXMFile.search_index
      ~SLS_STXMFile.section
      ~SLS_STXMFile.select
      ~SLS_STXMFile.setdefault
      ~SLS_STXMFile.smooth
      ~SLS_STXMFile.sort
      ~SLS_STXMFile.span
      ~SLS_STXMFile.spline
      ~SLS_STXMFile.split
      ~SLS_STXMFile.std
      ~SLS_STXMFile.stitch
      ~SLS_STXMFile.subplot
      ~SLS_STXMFile.subplot2grid
      ~SLS_STXMFile.subtract
      ~SLS_STXMFile.swap_column
      ~SLS_STXMFile.threshold
      ~SLS_STXMFile.to_pandas
      ~SLS_STXMFile.unique
      ~SLS_STXMFile.update
      ~SLS_STXMFile.values
      ~SLS_STXMFile.x2
      ~SLS_STXMFile.y2

   .. rubric:: Attributes Documentation

   .. autoattribute:: T
   .. autoattribute:: ax
   .. autoattribute:: axes
   .. autoattribute:: basename
   .. autoattribute:: clone
   .. autoattribute:: cmap
   .. autoattribute:: column_headers
   .. autoattribute:: compression
   .. autoattribute:: compression_opts
   .. autoattribute:: data
   .. autoattribute:: dict_records
   .. autoattribute:: dims
   .. autoattribute:: dtype
   .. autoattribute:: fig
   .. autoattribute:: fignum
   .. autoattribute:: filename
   .. autoattribute:: filepath
   .. autoattribute:: header
   .. autoattribute:: labels
   .. autoattribute:: mask
   .. autoattribute:: metadata
   .. autoattribute:: mime_type
   .. autoattribute:: multiple
   .. autoattribute:: no_fmt
   .. autoattribute:: patterns
   .. autoattribute:: positional_fmt
   .. autoattribute:: priority
   .. autoattribute:: records
   .. autoattribute:: setas
   .. autoattribute:: shape
   .. autoattribute:: showfig
   .. autoattribute:: subplots
   .. autoattribute:: template

   .. rubric:: Methods Documentation

   .. automethod:: SG_Filter
   .. automethod:: __call__
   .. automethod:: add
   .. automethod:: add_column
   .. automethod:: annotate_fit
   .. automethod:: append
   .. automethod:: apply
   .. automethod:: asarray
   .. automethod:: bin
   .. automethod:: clear
   .. automethod:: clip
   .. automethod:: closest
   .. automethod:: colormap_xyz
   .. automethod:: column
   .. automethod:: columns
   .. automethod:: contour_xyz
   .. automethod:: count
   .. automethod:: curve_fit
   .. automethod:: decompose
   .. automethod:: del_column
   .. automethod:: del_nan
   .. automethod:: del_rows
   .. automethod:: differential_evolution
   .. automethod:: diffsum
   .. automethod:: dir
   .. automethod:: divide
   .. automethod:: extend
   .. automethod:: extrapolate
   .. automethod:: figure
   .. automethod:: filter
   .. automethod:: find_col
   .. automethod:: find_duplicates
   .. automethod:: find_peaks
   .. automethod:: format
   .. automethod:: get
   .. automethod:: get_filename
   .. automethod:: griddata
   .. automethod:: image_plot
   .. automethod:: index
   .. automethod:: insert
   .. automethod:: insert_rows
   .. automethod:: inset
   .. automethod:: integrate
   .. automethod:: interpolate
   .. automethod:: items
   .. automethod:: keys
   .. automethod:: legend
   .. automethod:: lmfit
   .. automethod:: load
   .. automethod:: make_bins
   .. automethod:: max
   .. automethod:: mean
   .. automethod:: min
   .. automethod:: multiply
   .. automethod:: normalise
   .. automethod:: odr
   .. automethod:: outlier_detection
   .. automethod:: peaks
   .. automethod:: plot
   .. automethod:: plot_matrix
   .. automethod:: plot_voxels
   .. automethod:: plot_xy
   .. automethod:: plot_xyuv
   .. automethod:: plot_xyuvw
   .. automethod:: plot_xyz
   .. automethod:: plot_xyzuvw
   .. automethod:: polyfit
   .. automethod:: pop
   .. automethod:: popitem
   .. automethod:: quiver_plot
   .. automethod:: remove
   .. automethod:: remove_duplicates
   .. automethod:: rename
   .. automethod:: reorder_columns
   .. automethod:: reverse
   .. automethod:: rolling_window
   .. automethod:: rows
   .. automethod:: save
   .. automethod:: scale
   .. automethod:: scan_meta
   .. automethod:: search
   .. automethod:: search_index
   .. automethod:: section
   .. automethod:: select
   .. automethod:: setdefault
   .. automethod:: smooth
   .. automethod:: sort
   .. automethod:: span
   .. automethod:: spline
   .. automethod:: split
   .. automethod:: std
   .. automethod:: stitch
   .. automethod:: subplot
   .. automethod:: subplot2grid
   .. automethod:: subtract
   .. automethod:: swap_column
   .. automethod:: threshold
   .. automethod:: to_pandas
   .. automethod:: unique
   .. automethod:: update
   .. automethod:: values
   .. automethod:: x2
   .. automethod:: y2
