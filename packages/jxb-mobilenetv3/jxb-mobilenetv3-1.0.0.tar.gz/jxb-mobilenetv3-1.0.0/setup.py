from setuptools import setup, find_packages

setup(
    name='jxb-mobilenetv3',
    version='1.0.0',
    packages=find_packages(include=['jxb_mobilenetv3', 'jxb_mobilenetv3.*']),
    package_data={
        'jxb_mobilenetv3.config': ['config.yaml'],  # 把 config.yaml 包含进去
    },
    include_package_data=True, 
    install_requires=[
        "numpy==1.23.5",
        "torch==2.1.0",
        "torchvision==0.16.0",
        "pyyaml==6.0",
        "pillow==10.4.0",
        "tqdm==4.66.5",
        "opencv-python==4.10.0.84",
        "seaborn==0.13.2",
        "matplotlib==3.7.5",
        "scikit-learn==1.3.2"
    ],
    author='Xiaobo Jia',
    author_email='1428340048@qq.com',
    license='MIT',
    description='A MobileNetV3-based classifier',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Starsjxb6/jxb-mobilenetv3',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
