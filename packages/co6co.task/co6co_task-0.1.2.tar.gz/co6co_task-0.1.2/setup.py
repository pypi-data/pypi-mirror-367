from setuptools import setup
import co6co.setupUtils as setupUtils
version = setupUtils.get_version(__file__)
packageName, packages = setupUtils.package_name(__file__)
long_description = setupUtils.readme_content(__file__)

requires = [
    "APScheduler>=3.10.4", "SQLAlchemy>=2.0.25", "co6co>=0.0.26", "co6co.sanic_ext>=0.0.9", "co6co.web-db>=0.0.14",
]
setup(
    name=packageName,
    version=version,
    description="任务模块",
    packages=packages,

    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=setupUtils.get_classifiers(),
    include_package_data=True, zip_safe=True,
    # 依赖哪些模块
    install_requires=requires,
    # package_dir= {'utils':'src/log','main_package':'main'},#告诉Distutils哪些目录下的文件被映射到哪个源码
    author='co6co',
    author_email='co6co@qq.com',
    url="http://github.com/co6co",
    data_file={
        ('', "*.txt"),
        ('', "*.md"),
    },
    package_data={
        '': ['*.txt', '*.md'],
        'bandwidth_reporter': ['*.txt']
    }, cmdclass={
        'sdist': setupUtils.CustomSdist
    }
)
