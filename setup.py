from setuptools import setup

setup(
    name='dashboardapp',
    version='0.1',
    packages=['dashboardapp'],
    description='Dashboard app',
    author='Chris Francis',
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask', 'psycopg2-binary', 'plotly', 'pandas'],
    entry_points={
        'console_scripts': [
            'run-app = dashboardapp.dash_app:run_app',
        ],
    },
)