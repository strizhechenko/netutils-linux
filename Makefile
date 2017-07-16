test:
	pytest netutils_linux_*/
	./tests/utils_runnable
	./tests/rss-ladder-test
	./tests/server-info-show
	./tests/link_rate_units.sh

env:
	rm -rf env
	virtualenv env && \
	. env/bin/activate && \
	pip install --upgrade -r requirements.txt && \
	python setup.py install

help:
	@echo "  env         create a development environment using virtualenv"
	@echo "  deps        install dependencies"
	@echo "  clean       remove unwanted stuff"
	@echo "  lint        check style with flake8"
	@echo "  coverage    run tests with code coverage"
	@echo "  test        run tests"

# only for localhost MacOS testing.
test2:
	. env2/bin/activate && \
		./tests/rss-ladder && \
		./tests/server-info-show && \
		./tests/link_rate_units.sh
	pytest netutils_linux_*/

env2:
	rm -rf env2
	virtualenv --python=python2 env2 && \
		. env2/bin/activate && \
		pip install --upgrade -r requirements.txt && \
		python setup.py install

# only for localhost MacOS testing.
test3:
	. env3/bin/activate && \
		./tests/rss-ladder && \
		./tests/server-info-show && \
		./tests/link_rate_units.sh
	pytest netutils_linux_*/

env3:
	rm -rf env3
	virtualenv --python=python3 env3 && \
		. env3/bin/activate && \
		pip install --upgrade -r requirements.txt && \
		python setup.py install

clean:
	rm -fr env
	rm -fr build
	rm -fr dist
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' -exec rm -f {} \;

lint:
	./flake8.sh netutils_linux_monitoring netutils_linux_tuning netutils_linux_hardware
	python setup.py checkdocs

coverage:
	nosetests --with-coverage --cover-package=twitter

build: clean
	python setup.py sdist
	python setup.py bdist_wheel

upload: test lint clean
	python setup.py sdist upload
	# python setup.py bdist_wheel upload

mac_run: env
	. env/bin/activate && \
	network-top --random \
		--softirqs-file=./tests/softirqs/i7/softirqs1 \
		--softnet-stat-file=./tests/softnet_stat/softnet_stat1 \
		--interrupts-file=./tests/interrupts/singlequeue_8cpu/interrupts_short \
		--devices=eth1,eth2,eth3

mac_run_link_rate: env
	. env/bin/activate && \
	link-rate --random \
		--devices=eth1,eth2,eth3

mac_run_irqtop: env
	. env/bin/activate && \
		irqtop --random \
		--interrupts-file=./tests/interrupts/singlequeue_8cpu/interrupts_short

mac_run_softirq_top: env
	. env/bin/activate && \
	softirq-top --random \
		--softirqs-file=./tests/softirqs/i7/softirqs1

mac_run_softnet_stat_top:
	. env/bin/activate && \
	softnet-stat-top --random \
		--softnet-stat-file=./tests/softnet_stat/softnet_stat1
