from setuptools import setup, find_packages

setup(
    name='mohamedboualamallah',  # New package name for PyPI
    version='0.1.3',
    author='Mohamed Boualamallah',
    author_email='mohamedboualamallah@icloud.com',
    description='A modular application for audio processing and Finch robot control.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    namespace_packages=["mohamedboualamallah"],  # Enables the namespace package
    install_requires=[
        'sounddevice',
        'numpy',
        'webrtcvad',
        'scipy',
        'gradio-client',
        'google-genai',
        'playsound==1.2.2',
        'birdbrain-python-library',
        'Pillow',
        'pygame'
    ],
    entry_points={
        'console_scripts': [
            'fiji_ai=mohamedboualamallah.fiji_ai.main:main',
            'fruit_ninja=mohamedboualamallah.fruit_ninja.app:main',
        ],
    },
)