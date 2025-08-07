from setuptools import setup, find_packages


setup(
	name="calculator_decorator",
	description="calculator operaions",
	version="1.0",
	author="ahmed atef",
	author_email="ahmedatef93legend@gmail.com",
	packages=find_packages(),
    entry_points={
        "console_scripts":[
            "operation_sum = calculator_decorator:sum_numbers",
            "operation_sub = calculator_decorator:sub_numbers",
            "operation_mult = calculator_decorator:mult_numbers",
            "operation_div = calculator_decorator:div_numbers"
		]
	},
	install_requires=[
        # 'numpy>=1.11.1'
    ]
)
