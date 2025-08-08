from setuptools import setup, find_packages

setup(
    name='aek-img-trainer',
    version='0.2.1',
    description='Image classification trainer using OpenCV and timm',
    author='Alp Emre Karaahmet',
    author_email='alpemre@gmail.com',
    packages=find_packages(),
    install_requires=[
        'torch',
        'opencv-python',
        'numpy',
        'timm',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
)
