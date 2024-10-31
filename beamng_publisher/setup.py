from setuptools import setup
from setuptools_rust import Binding, RustExtension

setup(name='beamng_publisher',
        version='0.1',
        rust_extensions=[
            RustExtension('beamng_publisher', 'Cargo.toml',
                binding=Binding.PyO3)],
            zip_safe=False)
