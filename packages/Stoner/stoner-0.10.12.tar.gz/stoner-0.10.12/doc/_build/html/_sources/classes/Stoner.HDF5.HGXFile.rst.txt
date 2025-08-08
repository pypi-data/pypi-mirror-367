HGXFile
=======

.. currentmodule:: Stoner.HDF5

.. autoclass:: HGXFile
   :show-inheritance:

   .. rubric:: Attributes Summary

   .. autosummary::

      ~HGXFile.T
      ~HGXFile.ax
      ~HGXFile.axes
      ~HGXFile.basename
      ~HGXFile.clone
      ~HGXFile.cmap
      ~HGXFile.column_headers
      ~HGXFile.data
      ~HGXFile.dict_records
      ~HGXFile.dims
      ~HGXFile.dtype
      ~HGXFile.fig
      ~HGXFile.fignum
      ~HGXFile.filename
      ~HGXFile.filepath
      ~HGXFile.header
      ~HGXFile.labels
      ~HGXFile.mask
      ~HGXFile.metadata
      ~HGXFile.mime_type
      ~HGXFile.multiple
      ~HGXFile.no_fmt
      ~HGXFile.pattern
      ~HGXFile.positional_fmt
      ~HGXFile.priority
      ~HGXFile.records
      ~HGXFile.setas
      ~HGXFile.shape
      ~HGXFile.showfig
      ~HGXFile.subplots
      ~HGXFile.template

   .. rubric:: Methods Summary

   .. autosummary::

      ~HGXFile.SG_Filter
      ~HGXFile.__call__
      ~HGXFile.add
      ~HGXFile.add_column
      ~HGXFile.annotate_fit
      ~HGXFile.append
      ~HGXFile.apply
      ~HGXFile.asarray
      ~HGXFile.bin
      ~HGXFile.clear
      ~HGXFile.clip
      ~HGXFile.closest
      ~HGXFile.colormap_xyz
      ~HGXFile.column
      ~HGXFile.columns
      ~HGXFile.contour_xyz
      ~HGXFile.count
      ~HGXFile.curve_fit
      ~HGXFile.decompose
      ~HGXFile.del_column
      ~HGXFile.del_nan
      ~HGXFile.del_rows
      ~HGXFile.differential_evolution
      ~HGXFile.diffsum
      ~HGXFile.dir
      ~HGXFile.divide
      ~HGXFile.extend
      ~HGXFile.extrapolate
      ~HGXFile.figure
      ~HGXFile.filter
      ~HGXFile.find_col
      ~HGXFile.find_duplicates
      ~HGXFile.find_peaks
      ~HGXFile.format
      ~HGXFile.get
      ~HGXFile.get_filename
      ~HGXFile.griddata
      ~HGXFile.image_plot
      ~HGXFile.index
      ~HGXFile.insert
      ~HGXFile.insert_rows
      ~HGXFile.inset
      ~HGXFile.integrate
      ~HGXFile.interpolate
      ~HGXFile.items
      ~HGXFile.keys
      ~HGXFile.legend
      ~HGXFile.lmfit
      ~HGXFile.load
      ~HGXFile.main_data
      ~HGXFile.make_bins
      ~HGXFile.max
      ~HGXFile.mean
      ~HGXFile.min
      ~HGXFile.multiply
      ~HGXFile.normalise
      ~HGXFile.odr
      ~HGXFile.outlier_detection
      ~HGXFile.peaks
      ~HGXFile.plot
      ~HGXFile.plot_matrix
      ~HGXFile.plot_voxels
      ~HGXFile.plot_xy
      ~HGXFile.plot_xyuv
      ~HGXFile.plot_xyuvw
      ~HGXFile.plot_xyz
      ~HGXFile.plot_xyzuvw
      ~HGXFile.polyfit
      ~HGXFile.pop
      ~HGXFile.popitem
      ~HGXFile.quiver_plot
      ~HGXFile.remove
      ~HGXFile.remove_duplicates
      ~HGXFile.rename
      ~HGXFile.reorder_columns
      ~HGXFile.reverse
      ~HGXFile.rolling_window
      ~HGXFile.rows
      ~HGXFile.save
      ~HGXFile.scale
      ~HGXFile.scan_group
      ~HGXFile.search
      ~HGXFile.search_index
      ~HGXFile.section
      ~HGXFile.select
      ~HGXFile.setdefault
      ~HGXFile.smooth
      ~HGXFile.sort
      ~HGXFile.span
      ~HGXFile.spline
      ~HGXFile.split
      ~HGXFile.std
      ~HGXFile.stitch
      ~HGXFile.subplot
      ~HGXFile.subplot2grid
      ~HGXFile.subtract
      ~HGXFile.swap_column
      ~HGXFile.threshold
      ~HGXFile.to_pandas
      ~HGXFile.unique
      ~HGXFile.update
      ~HGXFile.values
      ~HGXFile.x2
      ~HGXFile.y2

   .. rubric:: Attributes Documentation

   .. autoattribute:: T
   .. autoattribute:: ax
   .. autoattribute:: axes
   .. autoattribute:: basename
   .. autoattribute:: clone
   .. autoattribute:: cmap
   .. autoattribute:: column_headers
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
   .. autoattribute:: pattern
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
   .. automethod:: main_data
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
   .. automethod:: scan_group
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
