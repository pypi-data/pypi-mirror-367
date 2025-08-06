from silx import resources as _silx_resources  # noqa

# Add processview resources to silx resource management
_silx_resources.register_resource_directory("processview", "processview.resources")
