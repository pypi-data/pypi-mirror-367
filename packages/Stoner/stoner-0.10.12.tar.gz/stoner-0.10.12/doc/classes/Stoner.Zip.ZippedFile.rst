ZippedFile
==========

.. currentmodule:: Stoner.Zip

.. autoclass:: ZippedFile
   :show-inheritance:

   .. rubric:: Attributes Summary

   .. autosummary::

      ~ZippedFile.T
      ~ZippedFile.ax
      ~ZippedFile.axes
      ~ZippedFile.basename
      ~ZippedFile.clone
      ~ZippedFile.cmap
      ~ZippedFile.column_headers
      ~ZippedFile.data
      ~ZippedFile.dict_records
      ~ZippedFile.dims
      ~ZippedFile.dtype
      ~ZippedFile.fig
      ~ZippedFile.fignum
      ~ZippedFile.filename
      ~ZippedFile.filepath
      ~ZippedFile.header
      ~ZippedFile.labels
      ~ZippedFile.mask
      ~ZippedFile.metadata
      ~ZippedFile.mime_type
      ~ZippedFile.multiple
      ~ZippedFile.no_fmt
      ~ZippedFile.patterns
      ~ZippedFile.positional_fmt
      ~ZippedFile.priority
      ~ZippedFile.records
      ~ZippedFile.setas
      ~ZippedFile.shape
      ~ZippedFile.showfig
      ~ZippedFile.subplots
      ~ZippedFile.template

   .. rubric:: Methods Summary

   .. autosummary::

      ~ZippedFile.SG_Filter
      ~ZippedFile.__call__
      ~ZippedFile.add
      ~ZippedFile.add_column
      ~ZippedFile.annotate_fit
      ~ZippedFile.append
      ~ZippedFile.apply
      ~ZippedFile.asarray
      ~ZippedFile.bin
      ~ZippedFile.clear
      ~ZippedFile.clip
      ~ZippedFile.closest
      ~ZippedFile.colormap_xyz
      ~ZippedFile.column
      ~ZippedFile.columns
      ~ZippedFile.contour_xyz
      ~ZippedFile.count
      ~ZippedFile.curve_fit
      ~ZippedFile.decompose
      ~ZippedFile.del_column
      ~ZippedFile.del_nan
      ~ZippedFile.del_rows
      ~ZippedFile.differential_evolution
      ~ZippedFile.diffsum
      ~ZippedFile.dir
      ~ZippedFile.divide
      ~ZippedFile.extend
      ~ZippedFile.extrapolate
      ~ZippedFile.figure
      ~ZippedFile.filter
      ~ZippedFile.find_col
      ~ZippedFile.find_duplicates
      ~ZippedFile.find_peaks
      ~ZippedFile.format
      ~ZippedFile.get
      ~ZippedFile.get_filename
      ~ZippedFile.griddata
      ~ZippedFile.image_plot
      ~ZippedFile.index
      ~ZippedFile.insert
      ~ZippedFile.insert_rows
      ~ZippedFile.inset
      ~ZippedFile.integrate
      ~ZippedFile.interpolate
      ~ZippedFile.items
      ~ZippedFile.keys
      ~ZippedFile.legend
      ~ZippedFile.lmfit
      ~ZippedFile.load
      ~ZippedFile.make_bins
      ~ZippedFile.max
      ~ZippedFile.mean
      ~ZippedFile.min
      ~ZippedFile.multiply
      ~ZippedFile.normalise
      ~ZippedFile.odr
      ~ZippedFile.outlier_detection
      ~ZippedFile.peaks
      ~ZippedFile.plot
      ~ZippedFile.plot_matrix
      ~ZippedFile.plot_voxels
      ~ZippedFile.plot_xy
      ~ZippedFile.plot_xyuv
      ~ZippedFile.plot_xyuvw
      ~ZippedFile.plot_xyz
      ~ZippedFile.plot_xyzuvw
      ~ZippedFile.polyfit
      ~ZippedFile.pop
      ~ZippedFile.popitem
      ~ZippedFile.quiver_plot
      ~ZippedFile.remove
      ~ZippedFile.remove_duplicates
      ~ZippedFile.rename
      ~ZippedFile.reorder_columns
      ~ZippedFile.reverse
      ~ZippedFile.rolling_window
      ~ZippedFile.rows
      ~ZippedFile.save
      ~ZippedFile.scale
      ~ZippedFile.search
      ~ZippedFile.search_index
      ~ZippedFile.section
      ~ZippedFile.select
      ~ZippedFile.setdefault
      ~ZippedFile.smooth
      ~ZippedFile.sort
      ~ZippedFile.span
      ~ZippedFile.spline
      ~ZippedFile.split
      ~ZippedFile.std
      ~ZippedFile.stitch
      ~ZippedFile.subplot
      ~ZippedFile.subplot2grid
      ~ZippedFile.subtract
      ~ZippedFile.swap_column
      ~ZippedFile.threshold
      ~ZippedFile.to_pandas
      ~ZippedFile.unique
      ~ZippedFile.update
      ~ZippedFile.values
      ~ZippedFile.x2
      ~ZippedFile.y2

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
