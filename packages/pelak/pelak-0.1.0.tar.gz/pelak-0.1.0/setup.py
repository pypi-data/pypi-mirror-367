from setuptools import setup, find_packages

setup(
    name='pelak',
    version='0.1.0',
    description='(نسخه آزمايشي) تولید تصویر پلاک استاندارد ایرانی با پشتیبانی از قالب‌های خاص',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='RezaGooner',
    author_email='RezaAsadiProgrammer@Gmail.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    package_data={'pelak': ['data/*.png', 'data/*.ttf']},
    install_requires=[
        'pillow>=10.0.0',
    ],
    python_requires='>=3.7',
    url='https://github.com/RezaGooner/pelak',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
