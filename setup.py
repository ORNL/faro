try:
    from setuptools import setup
except:
    print('Warning: setuptools not installed.  Falling back to distutils.core')
    from distutils.core import setup
import os



setup(name='faro',
      version='1.5.0',
      description='Face Recognition From Oak Ridge.',
      # author='David Bolme',
      # author_email='dbolme@gmail.com',
      # url='https://github.com/bolme/pyvision',
      keywords = ["machine learning", "vision", "image", "face recognition", "deep learning","biometrics"],
         classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        ],
    long_description = "A computer vision library for python.",

      packages=['faro',
                'faro.proto',
                'faro.face_workers',
                'faro.command_line',
                'faro.pyvision',
                'faro.pyvision.face',
                'faro.pyvision.analysis',
                'faro.pyvision.edge',
                'faro.pyvision.optimize',
                'faro.pyvision.other',
                'faro.pyvision.point',
                'faro.pyvision.vector',
                'faro.pyvision.types',
                'faro.pyvision.data',
                'faro.pyvision.gui',
                'faro.pyvision.segment',
                'faro.pyvision.surveillance',
                'faro.pyvision.util',
                'faro.pyvision.beta',
                'faro.pyvision.features',
                'faro.pyvision.ml',
                'faro.pyvision.tools',
                'faro.pyvision.config',
                'faro.pyvision.analysis.FaceAnalysis',
                'faro.pyvision.analysis.classifier',
                'faro.pyvision.analysis.R',
                ],
      package_dir = {'': 'src'},
      install_requires=[
          'opencv-python',
          'Pillow',
          'numpy',
          'scipy',
          'scikit-image',
          'scikit-learn',
          'protobuf',
          'grpcio-tools',
          'sortedcollections',
          'h5py'
      ],
)

# protobuf grpcio grpcio.tools pyvision_toolkit keras_vggface tensorflow keras==2.2.0 dlib
