from distutils.core import setup
import os



setup(name='faro',
      version='0.9.0',
      description='Face Recognition From Oak Ridge.',
      author='David Bolme',
      author_email='dbolme@gmail.com',
      url='https://github.com/bolme/pyvision',
      keywords = ["machine learning", "vision", "image", "face recognition", "deep learning"],
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
                ],
      package_dir = {'': 'src'},
      install_requires=[
          'opencv-python',
          'Pillow',
          'numpy',
          'scipy',
          'scikit-image',
          'scikit-learn',
          'pyvision-toolkit',
          'protobuf',
          'grpcio',
          'grpcio.tools',
          'keras==2.2.0',
          'keras_vggface',
          'dlib',
      ],
)

# protobuf grpcio grpcio.tools pyvision_toolkit keras_vggface tensorflow keras==2.2.0 dlib
